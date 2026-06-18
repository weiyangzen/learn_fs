# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos7.c

## Purpose

`clk-exynos7.c` is a Samsung Common Clock Framework provider for the Exynos7 SoC family. It describes the SoC's clock management units as static data tables and registers each CMU from device tree using `CLK_OF_DECLARE()`. The file does not implement clock algorithms itself; it maps PLLs, muxes, dividers, fixed-rate clocks, fixed-factor clocks, and gates onto register offsets and bit fields consumed by the shared Samsung clock core in `drivers/clk/samsung/clk.c`.

The file covers many Exynos7 clock islands: `TOPC`, `TOP0`, `TOP1`, `CCORE`, `PERIC0`, `PERIC1`, `PERIS`, `FSYS0`, `FSYS1`, `MSCL`, and `AUD`. `TOPC` owns the main PLL outputs and top-level derived clocks. `TOP0` and `TOP1` distribute those top clocks into peripheral and file-system domains. Leaf CMUs expose device clocks for RTC, I2C, UART, SPI, timers, chip ID, USB, UFS, MMC, media scaler/JPEG/G2D, and audio peripherals.

## Important APIs, Types, and Tables

The main type is `struct samsung_cmu_info`. Each CMU has one instance describing the arrays to register and the number of clock IDs exported to the CCF:

- `topc_cmu_info` combines PLLs, muxes, dividers, gates, fixed-factor clocks, and a register list.
- `top0_cmu_info` and `top1_cmu_info` define top-level mux/divider/gate distribution domains.
- `ccore_cmu_info`, `peric0_cmu_info`, `peric1_cmu_info`, `peris_cmu_info`, `fsys0_cmu_info`, `fsys1_cmu_info`, `mscl_cmu_info`, and `aud_cmu_info` describe their respective leaf domains.

The file relies on Samsung clock macros from `clk.h`: `PLL()`, `MUX()`, `MUX_F()`, `DIV()`, `GATE()`, `FFACTOR()`, `FRATE()`, and `PNAME()`. These macros create `struct samsung_pll_clock`, `struct samsung_mux_clock`, `struct samsung_div_clock`, `struct samsung_gate_clock`, fixed-factor descriptors, fixed-rate descriptors, and parent-name arrays. Clock IDs come from `<dt-bindings/clock/exynos7-clk.h>`, so exported IDs must stay aligned with the binding.

Registration entry points are small wrappers such as `exynos7_clk_topc_init()`, `exynos7_clk_top0_init()`, and `exynos7_clk_aud_init()`. Each calls `samsung_cmu_register_one(np, &..._cmu_info)`. `CLK_OF_DECLARE()` binds each wrapper to a compatible string like `samsung,exynos7-clock-topc`.

## Control Flow

During early boot, the OF clock initialization path matches clock-provider device-tree nodes against the `CLK_OF_DECLARE()` compatible strings. For each matched node, the corresponding `exynos7_clk_*_init()` function passes the node and static CMU descriptor to `samsung_cmu_register_one()`. The shared Samsung code maps the CMU register region, snapshots or manages the listed `clk_regs`, creates the CCF clock hardware objects, and publishes the provider for consumer drivers.

The runtime control path is then mostly CCF-driven. A consumer asks for a clock by DT phandle/index or by clock name. The CCF invokes the registered mux/divider/gate/PLL operations from the Samsung core, which read or update the register offsets and bit positions declared here. Parent propagation is enabled selectively with flags such as `CLK_SET_RATE_PARENT`; always-on dependencies use `CLK_IS_CRITICAL` or `CLK_IGNORE_UNUSED`.

## State and Persistence Behavior

The file has no heap-owned state, no persistent storage, and no runtime data structures beyond what the shared registration helpers allocate. Its state model is declarative: hardware register state lives in CMU registers, and CCF-visible state is reconstructed at boot from static tables. The `..._clk_regs` arrays identify registers relevant for the CMU, which the Samsung core can use for register save/restore and initialization ordering. Several descriptors are `__initconst`, so the table memory is discarded after boot registration.

Critical clocks are the main persistence signal. For example `aclk_ccore_133`, `aclk_fsys0_200`, and `aclk_fsys1_200` are marked critical where register access or essential bus function depends on them. FSYS1 includes a comment that `aclk_fsys1_200` must remain enabled until proper runtime PM support exists. USB and UFS PHY fixed-rate clocks are modeled as clock inputs rather than discovered dynamically.

## Dependencies and Integration Points

This driver depends on the Linux CCF (`<linux/clk-provider.h>`), the Samsung clock provider helpers (`clk.h`), and Exynos7 clock IDs in the DT binding. It integrates with device tree through compatible strings:

- `samsung,exynos7-clock-topc`
- `samsung,exynos7-clock-top0`
- `samsung,exynos7-clock-top1`
- `samsung,exynos7-clock-ccore`
- `samsung,exynos7-clock-peric0`
- `samsung,exynos7-clock-peric1`
- `samsung,exynos7-clock-peris`
- `samsung,exynos7-clock-fsys0`
- `samsung,exynos7-clock-fsys1`
- `samsung,exynos7-clock-mscl`
- `samsung,exynos7-clock-aud`

Clock-name integration is also important. Parent strings such as `sclk_bus0_pll_a`, `aclk_peric0_66`, `sclk_mmc0`, `phyclk_ufs20_tx0_symbol`, and `fout_aud_pll` must match clocks produced by other tables in this file or by external providers. The ordering implied by device-tree availability matters because leaf CMUs use user mux parents produced by TOP CMUs.

## Risks and Edge Cases

The primary risks are data-table accuracy issues: wrong register offsets, bit shifts, bit widths, parent ordering, or clock IDs can silently produce incorrect clock rates or gate the wrong hardware block. Since many clocks share a register and differ only by bit offset, small mistakes can be difficult to diagnose. A binding mismatch can expose the wrong clock to a consumer or leave a required clock unreachable.

Critical-clock flags are another risk area. Missing `CLK_IS_CRITICAL` on clocks needed for register access, buses, interrupt paths, or early boot can hang the system during unused-clock cleanup. Overusing critical or ignore-unused flags can hide power-management bugs and keep domains unnecessarily active. The FSYS1 comment indicates an acknowledged runtime PM gap.

Parent-name dependencies are fragile because they are string-based within the provider framework. A renamed clock or a mismatched DT-provided external parent can break rate propagation or leave a mux parent unresolved. Fixed-rate PHY clocks may also become inaccurate if board or PHY revisions use different actual rates.

## Test Signals

Useful validation starts with build coverage for `CONFIG_COMMON_CLK_SAMSUNG` and Exynos7 DT bindings. Boot logs should show each CMU provider registered without missing-parent warnings. Device-tree clock consumers for UART, SPI, I2C, MMC, USB, UFS, audio, RTC, WDT, TMU, and MSCL/JPEG/G2D should probe successfully.

Runtime checks include `/sys/kernel/debug/clk/clk_summary` to confirm expected parentage, rates, enable counts, and critical clocks. Peripheral smoke tests should cover serial console stability, MMC timing modes, USB PHY operation, UFS link operation where present, audio I2S/PCM/SPDIF clocks, watchdog and thermal sensor access, and media scaler/JPEG/G2D activity. Suspend/resume testing should focus on CMU register restoration and on the domains whose register lists are enumerated here.
