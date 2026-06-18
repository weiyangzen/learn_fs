# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra210.c

## Purpose
This file is the Tegra210 SoC CAR clock driver. It registers the Tegra210 oscillator, PLLs, PLL outputs, super clocks, peripheral clocks, EMC/MC clocks, special resets, CPU clock callbacks, syscore suspend/resume handling, and exported PLL hardware-sequencer controls used by XUSB, SATA, UTMIPLL, PLLE, and EMC code. Compared with Tegra20/Tegra30 it carries more hardware policy: PLL default repair, SDM/fractional rate calculation, dynamic ramping, MBIST workarounds, and special reset lines.

## Important APIs, Types, And Functions
Exported functions include `tegra210_plle_hw_sequence_is_enabled()`, `tegra210_plle_hw_sequence_start()`, XUSB/SATA hardware control and sequence helpers, `tegra210_set_sata_pll_seq_sw()`, EMC update helpers, `tegra210_clk_handle_mbist_war()`, and UTMIPLL IDDQ helpers. Core init is `tegra210_clock_init()` declared with `CLK_OF_DECLARE("nvidia,tegra210-car")`.

Important local mechanisms include many `struct tegra_clk_pll_params` definitions for PLLX, PLLC/C2/C3/C4, PLLM/PLLMB, PLLE, PLLRE, PLLP, PLLA/A1, PLLD/D2/DP, and PLLU; post-divider maps; SDM helper macros; `tegra210_pll_fixed_mdiv_cfg()`; `tegra210_pllx_dyn_ramp()`; PLL default setters; `tegra210_periph_clk_init()`; `tegra210_pll_init()`; `tegra210_init_pllu()`; syscore suspend/resume; and special reset assert/deassert hooks for DFLL DVCO and ADSP.

## Control Flow
`tegra210_clock_init()` maps CAR and PMC, maps AHUB/DISPA/VIC physical ranges needed for MBIST workarounds, allocates the shared clock array for seven peripheral banks, reads `SPARE_REG0` to determine the `clk_m` divisor, initializes oscillator and fixed clocks, registers PLLs, registers peripheral clocks, registers audio clocks, forces PLLD as DSIA/DSIB source, stores the init-table callback, initializes gen5 super clocks, installs special reset callbacks, publishes the OF onecell clock/reset provider, registers clkdev aliases, prepares MBIST clock bulk lists, installs CPU CAR ops, and registers syscore suspend/resume.

PLL init first ensures PLLU/UTMIPLL hardware sequencing is configured, then registers PLL families and their fixed/gated/divider outputs. Peripheral init handles SOR semantics, DPAUX, DSI, CSI test pattern, LA, CML, ACLK, SDMMC mux/div clocks, generated peripheral tables, Tegra common peripheral clocks, Tegra210 EMC clock, and MC divider. `tegra210_clock_apply_init_table()` runs later through `tegra_clk_apply_init_table` arch initcall from `clk.c`.

## State And Persistence Behavior
State is a mix of MMIO state, global pointers, PLL parameter objects, spinlocks, and suspend snapshots. MMIO writes configure PLL defaults, lock-detect bits, IDDQ, dividers, clock enable banks, resets, and hardware sequencer state. PM sleep support saves generic CCF clock context, selected bootloader-programmed CAR registers, CPU soft reset registers, and peripheral enable/reset state, then restores oscillator, PLLU/UTMIPLL, clock framework context, and peripheral context on resume.

MBIST workaround state is in `tegra210_pg_mbist_war[]`, which maps powergate IDs to clock bulk arrays and level-2 override handlers. `tegra210_mbist_clk_init()` resolves clock IDs to `clk_bulk_data`; `tegra210_clk_handle_mbist_war()` prepares/enables those clocks, serializes override writes with `lvl2_ovr_lock`, runs a domain-specific handler, and disables the clocks.

## Dependencies And Integration Points
The file is tightly coupled to Tegra common clock code in `clk.h`, common reset provider setup in `clk.c`, PM core syscore hooks, Tegra PMC powergate IDs, dt-bindings for Tegra210 clocks/resets, Linux CCF APIs, and SoC blocks outside CAR such as AHUB, DISPA, and VIC. It exports symbols consumed by USB/XUSB/SATA/EMC and powergate code. It also depends on firmware/bootloader initial clock state because many default setters inspect already-enabled PLLs and only apply safe in-flight defaults.

## Risks
This file has high hardware risk. It directly maps fixed physical addresses for AHUB/DISPA/VIC rather than discovering them from DT. Several flows use `BUG()` or warnings for unexpected oscillator/reference rates. PLL default setters intentionally postpone full programming when firmware left PLLs enabled; wrong assumptions can leave mixed boot/kernel PLL state. `tegra210_wait_for_mask()` can time out but some callers ignore dynamic-ramp errors. The suspend resume sequence temporarily enables all valid peripheral clocks before restoring rates, which is required for glitchless switching but can expose power or peripheral side effects. Special reset IDs are offset behind common reset banks, so `tegra_init_special_resets(2, ...)` must stay synchronized with dt-bindings.

## Test Signals
Strong signals include clean boot without PLL default warnings beyond expected firmware state, successful `of_clk_src_onecell_get()` for all dt-bindings, working XUSB/SATA/UTMI hardware sequencer transitions, EMC rate changes through the separate EMC provider, display SOR/DPAUX operation, audio PLL exact-rate behavior, CPU idle/suspend/resume, ADSP and DFLL reset behavior, powergate MBIST workaround calls for graphics/display/audio/XUSB/SATA domains, and stress tests around PLL rate changes and resume.
