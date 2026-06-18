# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk.h

## Purpose

`clk.h` is the private interface for the NVIDIA Tegra clock-controller implementation. It centralizes register offsets, valid enable masks, private clock data structures, flag definitions, helper prototypes, and SoC-specific initialization entry points used by the many Tegra clock source files. The header is not a standalone driver; it is the shared contract between Tegra clock implementations for PLLs, fractional dividers, peripheral clocks, super clocks, SDMMC mux/dividers, EMC clocks, reset handling, and device-tree provider setup.

## Important APIs, Types, And Functions

The top of the file defines the common CAR register offsets for clock enable banks `L/H/U/V/W/X/Y`, set/clear aliases, reset-device banks, and Tegra210 valid-bit masks. `struct tegra_clk_sync_source`, `struct tegra_clk_frac_div`, `struct tegra_clk_pll_freq_table`, `struct pdiv_map`, `struct div_nmp`, `struct tegra_clk_pll_params`, `struct tegra_clk_pll`, and `struct tegra_clk_pll_out` describe the PLL and divider plumbing. The PLL params structure is the largest contract: it carries base/misc register offsets, masks and shifts for M/N/P, lock bits, SDM data, fixed-rate tables, p-div mappings, step registers, output masks, and per-PLL operation callbacks.

Peripheral clock interfaces are represented by `struct tegra_clk_periph_regs`, `struct tegra_clk_periph_gate`, `struct tegra_clk_periph_fixed`, `struct tegra_clk_periph`, `struct tegra_periph_init_data`, `TEGRA_CLK_PERIPH()`, `TEGRA_INIT_DATA_TABLE()`, and `TEGRA_INIT_DATA()`. CPU and system muxing is represented by `struct tegra_clk_super_mux` and the `tegra_clk_register_super_*()` family. The late file-level APIs expose `tegra_clk_init()`, `tegra_lookup_dt_id()`, `tegra_add_of_provider()`, `tegra_register_devclks()`, per-SoC init hooks, EMC registration hooks, suspend/resume hooks, and low-level helpers such as `tegra_pll_wait_for_lock()`, `tegra_pll_p_div_to_hw()`, and `div_frac_get()`.

## Control Flow

Consumers include SoC-specific Tegra clock files. Their normal flow is to map the CAR base, call `tegra_clk_init()` to allocate the clock array, register fixed/oscillator/PLL/peripheral/super/audio/EMC clocks through the prototypes here, populate duplicate device clock lookups, initialize default rates and parents from `struct tegra_clk_init_table`, and add a device-tree clock provider through `tegra_add_of_provider()`. Runtime control is then delegated to CCF operations implemented in the corresponding `.c` files, using the register offsets and masks encoded by these structures.

## State And Persistence Behavior

The header describes hardware state rather than owning it. Persistent state lives in CAR registers: enable bits, reset bits, PLL programming, peripheral mux/divider fields, PLL output gates, and suspend/resume shadow state maintained by implementation files. Several structures contain pointers to shared locks, reg bases, and clock arrays, so a bad initializer can couple unrelated clocks to the wrong register bank. The valid enable masks prevent writes to reserved bits for Tegra210 banks.

## Dependencies And Integration Points

This file depends on Linux CCF types, Tegra device-tree clock IDs from `<dt-bindings/clock/tegra*.h>`, reset-controller integration, EMC support, and SoC-specific Tegra clock implementation files. `CONFIG_ARCH_TEGRA_124_SOC` gates the Tegra124 EMC registration path and supplies stubs otherwise. Device-tree integration depends on onecell clock provider arrays and stable DT clock IDs.

## Risks And Edge Cases

Register bank offsets and bit masks are hardware-sensitive. An incorrect bank, reset bit, or PLL field can disable a live peripheral or program a PLL outside its safe range. PLL flags such as `TEGRA_PLL_USE_LOCK`, `TEGRA_PLL_BYPASS`, `TEGRA_PLLM`, `TEGRA_PLLU`, and `TEGRA_MDIV_NEW` select different algorithms in implementation files, so table-driven additions must match the exact PLL generation. The periph macros hide many positional parameters; initializer ordering mistakes are easy to compile but hard to diagnose at boot. EMC function stubs return safe defaults when Tegra124 support is absent, which can mask missing config until a board expects dynamic EMC handling.

## Test Signals

Build Tegra clock drivers across representative SoC configs, including with and without `CONFIG_ARCH_TEGRA_124_SOC`. Boot tests should inspect `/sys/kernel/debug/clk/clk_summary`, verify DT clock IDs resolve, exercise peripheral gates and resets, test CPU/super-clock rate transitions, and run suspend/resume to confirm CAR state restoration. PLL-focused tests should validate lock polling and output frequencies against hardware documentation.
