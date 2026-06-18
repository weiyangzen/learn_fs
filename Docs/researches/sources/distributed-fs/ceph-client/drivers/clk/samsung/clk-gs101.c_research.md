# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-gs101.c

## Purpose

`clk-gs101.c` is the Common Clock Framework provider description for the Google GS101 SoC clock-management units using the Samsung/Exynos arm64 clock helper layer. It does not implement a new clock algorithm; instead it enumerates register offsets, parent-name arrays, PLLs, muxes, dividers, fixed-rate/fixed-factor clocks, gate clocks, and per-domain `struct samsung_cmu_info` blocks. Those descriptions let the shared Samsung clock code register CCF clocks, expose device-tree clock IDs from `dt-bindings/clock/google,gs101.h`, initialize automatic/manual clock gating, and save/restore CMU and sysreg clock state across suspend.

The covered CMU domains are:

- `CMU_TOP`: shared PLLs and top-level derived clocks feeding CPU, bus, display/camera, HSI, MISC, PERIC, TPU, and other subsystem CMUs.
- `CMU_APM`: always-on/APM clocks, fixed alive PLL-derived rates, mailbox/PMU/RTC/watchdog/USI gates, and boost-option clocks.
- `CMU_DPU`: display-processing bus, PPMU, SSMT, SYSMMU, DPUF, and sysreg clocks.
- `CMU_HSI0`: USB/DisplayPort high-speed I/O clocks, including a USB PLL rate table and temporary fixed-rate external placeholders.
- `CMU_HSI2`: PCIe, embedded UFS, MMC-card, GPIO, and HSI2 bus gates.
- `CMU_MISC`: GIC, MCT, watchdog, TMU, DMA, SSS/crypto, OTP, PUF, RTIC, SYSMMU, and miscellaneous bus clocks.
- `CMU_PERIC0` and `CMU_PERIC1`: peripheral/I3C/USI/UART clock trees and gates for the two peripheral controller islands.

## Important APIs, Types, and Tables

- `struct samsung_cmu_info`: the central per-CMU descriptor. Each instance points at the arrays of PLL/mux/div/gate/fixed clocks, the number of clock IDs, the register save list, optional sysreg save list, optional parent `clk_name`, and GS101 auto-gating metadata.
- `PLL`, `MUX`, `nMUX`, `DIV`, `DIV_F`, `FFACTOR`, `FRATE`, and `GATE`: Samsung clock-description macros from `clk.h`. They expand to table entries consumed by the shared registration functions.
- `PNAME(...)`: static parent-name arrays. Most muxes are pure name-based CCF parent links, so string spelling must match clocks registered in this file, fixed clocks, or external DT-provided clocks.
- `CLKS_NR_TOP`, `CLKS_NR_APM`, `CLKS_NR_DPU`, `CLKS_NR_HSI0`, `CLKS_NR_HSI2`, `CLKS_NR_MISC`, `CLKS_NR_PERIC0`, `CLKS_NR_PERIC1`: onecell clock table sizes. Each is defined as the last binding ID for that domain plus one.
- `top_pll_clks`, `hsi0_pll_clks`, and `hsi0_usb_pll_rates`: GS101 uses five TOP shared PLLs and a USB PLL in HSI0. The HSI0 USB PLL rate table has a 24.576 MHz output from a 19.2 MHz input.
- `*_clk_regs`: register-offset lists used by Samsung sleep/syscore code and by the arm64 initialization helper. They include PLL, mux, divider, gate, QCH/PCH, queue, option, and other CMU registers relevant to each domain.
- `dcrg_memclk_sysreg` and `dcrg_sysreg`: sysreg-side save lists for automatic clock gating. `dcrg_memclk_sysreg` includes dynamic root clock gating (`0x104`) and memclk (`0x108`); `dcrg_sysreg` includes only dynamic root clock gating.
- `GS101_GATE_DBG_OFFSET`, `GS101_DRCG_EN_OFFSET`, `GS101_MEMCLK_OFFSET`: GS101-specific offsets used by auto-gate registration and sysreg DRCG/memclk handling.
- `CLK_OF_DECLARE(...)`: early registration hooks for TOP and MISC.
- `gs101_cmu_probe`, `gs101_cmu_of_match`, `gs101_cmu_driver`, and `gs101_cmu_init`: platform-driver path for non-early domains.

## Control Flow

Boot-time registration is split deliberately:

1. `gs101_cmu_top_init()` is registered with `CLK_OF_DECLARE("google,gs101-cmu-top")` and calls `exynos_arm64_register_cmu(NULL, np, &top_cmu_info)`. TOP is registered early because later domains use TOP outputs as parent clocks.
2. `gs101_cmu_misc_init()` is also registered with `CLK_OF_DECLARE("google,gs101-cmu-misc")`. The comment notes that MISC is needed early for the MCT timer.
3. `core_initcall(gs101_cmu_init)` registers `gs101_cmu_driver`.
4. Platform devices with compatibles `google,gs101-cmu-apm`, `-dpu`, `-hsi0`, `-hsi2`, `-peric0`, or `-peric1` match `gs101_cmu_of_match`. `gs101_cmu_probe()` retrieves the matched `samsung_cmu_info` via `of_device_get_match_data()` and passes it to `exynos_arm64_register_cmu(dev, dev->of_node, info)`.
5. `exynos_arm64_register_cmu()` attempts to enable the CMU's parent bus clock if `.clk_name = "bus"` is set, initializes hardware control bits, and calls `samsung_cmu_register_one()`.
6. `samsung_cmu_register_one()` maps the CMU registers, allocates a Samsung provider sized by `.nr_clk_ids`, registers the described clocks, adds a DT clock provider, initializes sleep register caching, and enables sysreg DRCG if available.

Within a domain, CCF registration order is fixed by the shared helper: PLLs, muxes, dividers, gates, fixed-rate clocks, fixed-factor clocks, then CPU clocks. The GS101 tables are written to make parent strings resolvable under that order or by existing external clock providers.

## State and Persistence Behavior

This file's state is static descriptor data plus hardware state in MMIO registers. The descriptors are marked `__initconst` and are only needed during initialization. Runtime state lives in the common clock framework objects and in the CMU/sysreg hardware.

Persistence across suspend/resume is driven by the `*_clk_regs` and `sysreg_clk_regs` arrays. `samsung_cmu_register_one()` registers CMU register save/restore data through `samsung_clk_extended_sleep_init()` for non-PM CMUs. For sysreg DRCG/memclk registers, `samsung_en_dyn_root_clk_gating()` writes DRCG enable bits and, if a memclk offset is provided, clears the memclk enable bit mask; it also registers sysreg save data when the CMU is not handled by a PM-aware path.

Automatic clock gating is enabled per CMU by `.auto_clock_gate = true`. The shared arm64 helper checks `samsung_is_auto_capable(np)`, which requires the DT resource size to be `0x10000`; otherwise it falls back toward manual gate initialization. If auto mode is enabled and an `.option_offset` exists, the helper writes the CMU option register to enable global automatic gating, power management, layer-2 control, mem power gating, and debug behavior. Gate clocks are then registered against the gate debug register region (`gate register offset + 0x4000`) with no-op enable/disable operations and an `is_enabled` readback based on automatic clock-gate state. If auto mode is not available, gate registers in the `0x2000..0x2fff` range are forced into manual mode by setting bit 20 and clearing HWACG bit 28.

Several gates use `CLK_IS_CRITICAL` because disabling them was observed or expected to hang the system. Others use `CLK_IGNORE_UNUSED` with comments indicating missing consumer drivers. PERIC USI divider/gate entries often use `CLK_SET_RATE_PARENT` so serial/I3C-related consumers can propagate rate changes up through the peripheral user mux.

## Dependencies and Integration Points

- Linux CCF headers: `linux/clk-provider.h` supplies core registration types and flags.
- Platform/OF infrastructure: `linux/of.h`, `linux/mod_devicetable.h`, and `linux/platform_device.h` support DT matching, early OF declarations, and the platform driver.
- Samsung clock core: `clk.h`, `clk-exynos-arm64.h`, and `clk-pll.h` define the descriptor macros, `struct samsung_cmu_info`, PLL types, and `exynos_arm64_register_cmu()`.
- DT binding IDs: `dt-bindings/clock/google,gs101.h` must remain synchronized with every table ID and `CLKS_NR_*` size.
- Device tree nodes must provide the relevant `compatible`, MMIO `reg`, optional parent clocks named `"bus"` for non-root CMUs, optional `samsung,sysreg` phandle for DRCG/memclk, and external parent clocks such as `oscclk`, `pad_clk_apm`, `tcxo_hsi1_hsi0`, `usb20phy_phy_clock`, and `ioclk_clk_hsi0_alt`.
- Downstream device drivers consume these clocks by phandle ID and clock name; display, USB/DP, PCIe, UFS, MMC, I3C, USI/UART, GIC, timer, watchdog, thermal, DMA, and crypto blocks depend on the correctness of these tables.

## Risks and Edge Cases

- Table/register mismatches are the primary risk. A wrong register offset, shift, width, parent string, or gate bit can produce silent bad rates, failed probes, hangs during unused-clock cleanup, or broken suspend/resume.
- Binding drift is dangerous. `CLKS_NR_*` depends on the last clock ID in `google,gs101.h`; adding IDs without updating these sizes can drop clocks from the onecell provider.
- Early registration order matters. TOP must precede child CMUs, and MISC must precede timer use. Moving these from `CLK_OF_DECLARE` to normal platform probing can break early boot.
- Automatic gating depends on DT resource size. Older or incorrect DTs with non-`0x10000` CMU resources disable auto mode and change gate behavior.
- Several comments identify incomplete integration: HSI0 has fixed-rate placeholders "until we implement APMGSA", and multiple HSI/PERIC infrastructure gates are kept with `CLK_IGNORE_UNUSED` because consumers are missing. Those are deliberate workarounds but can hide missing drivers.
- Critical clocks in APM, HSI2, PERIC0, and PERIC1 are system-liveness dependencies. Removing `CLK_IS_CRITICAL` or changing their parents should be validated on real hardware.
- Some table entries look easy to mis-copy because of generated-style naming. Examples worth audit when modifying this file include duplicated or nearby PERIC register-list entries, long PCIe HSI2 gate names, and gates whose clock ID/name appears similar to a neighboring register macro.
- Parent-name strings are not type-checked. A typo such as `dout_*` vs `gout_*` may only surface as a missing parent, unexpected rate, or deferred/failed consumer probe.

## Test Signals

- Build coverage: compile the GS101/Samsung clock driver with the GS101 DT binding header and run kernel clock driver build checks; warnings about undefined IDs or missing symbols indicate binding/table drift.
- Boot log signals: absence of `failed to register clock`, `could not enable bus clock`, `incorrect res size for automatic clocks`, and `Unable to get CMU sysreg` messages for expected sysreg-backed CMUs.
- DT validation: GS101 CMU nodes should have the expected compatibles, `reg` resources sized for auto-gating, `"bus"` parent clocks where `.clk_name` is set, and `samsung,sysreg` phandles for domains using DRCG.
- Runtime CCF inspection: `/sys/kernel/debug/clk/clk_summary` should show the registered GS101 clock names, sane parentage from TOP into child domains, expected rates for PLL/divider outputs, and consumers on critical high-speed/peripheral clocks.
- Functional hardware probes: DPU/display, USB/DP on HSI0, UFS/MMC/PCIe on HSI2, MCT/GIC/watchdog/TMU/MISC peripherals, and USI/I3C/UART devices under PERIC0/PERIC1 should probe and run at expected bus/peripheral rates.
- Power-management validation: suspend/resume cycles should preserve CMU and sysreg DRCG/memclk state, with no loss of display, storage, serial, timer, or interrupt functionality after resume.
- Unused-clock cleanup validation: booting with clock debug enabled should not hang when unused clocks are disabled, which specifically exercises `CLK_IS_CRITICAL` and `CLK_IGNORE_UNUSED` choices.
