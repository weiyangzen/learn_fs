# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-s10.c

## Purpose
This file is the Stratix10 clock manager platform driver. It describes the Stratix10 clock tree in static tables and registers PLL, peripheral counter, peripheral core, and gate clocks with the Linux common clock framework (CCF). It is bound from Device Tree via `intel,stratix10-clkmgr` and exposes clocks through an `of_clk_hw_onecell_get` provider.

## Important APIs, Types, And Functions
The static topology data uses `struct clk_parent_data`, `struct stratix10_pll_clock`, `struct stratix10_perip_c_clock`, `struct stratix10_perip_cnt_clock`, and `struct stratix10_gate_clock` from `stratix10-clk.h`. The provider-side storage is `struct stratix10_clock_data`, which combines the register base with a flexible `clk_hw_onecell_data` array.

The local registration helpers are `s10_clk_register_pll()`, `s10_clk_register_c_perip()`, `s10_clk_register_cnt_perip()`, and `s10_clk_register_gate()`. Each iterates a static table, calls the matching lower-level registration helper (`s10_register_pll()`, `s10_register_periph()`, `s10_register_cnt_periph()`, or `s10_register_gate()`), logs failures, and stores successful `clk_hw` pointers by dt-binding clock ID. `s10_clkmgr_init()` maps registers, allocates the onecell data, initializes all slots to `ERR_PTR(-ENOENT)`, registers the tables, and installs the OF provider.

## Control Flow
Module initialization uses `core_initcall(s10_clk_init)` to register a platform driver early. Probe delegates directly to `s10_clkmgr_init()`. The init path maps MMIO resource 0, allocates `STRATIX10_NUM_CLKS` hardware slots, fills absent entries with `-ENOENT`, then registers clocks in dependency order: PLLs, core peripheral clocks, counter peripheral clocks, and gates.

The clock topology has explicit parent groups: PLL input muxes from oscillator/internal/free clocks, counter muxes from main/peripheral PLLs and boot sources, free-clock muxes for MPU/NOC/peripherals, and final functional gate clocks for MPU, L4, CoreSight, EMAC, SDMMC, USB, SPI, NAND, GPIO debounce, and PSI references.

## State And Persistence
Runtime state is devm-managed and exists for the lifetime of the platform device. Persistent hardware state is in the clock manager MMIO registers; the driver reads or modifies them indirectly through the lower-level Stratix10 helpers. The provider array intentionally records failed or missing clocks as `ERR_PTR(-ENOENT)` so consumers get deterministic missing-clock behavior.

## Dependencies And Integration Points
The file depends on `dt-bindings/clock/stratix10-clock.h` for clock IDs and on `stratix10-clk.h` for record layouts and registration helper prototypes. It integrates with the platform bus, Device Tree matching, MMIO resource mapping, and CCF onecell lookup. Parent names such as `osc1`, `cb-intosc-hs-div2-clk`, and `f2s-free-clk` must match firmware/Device Tree clock names.

## Risks
Registration helper failures are logged but do not abort initialization, so a partially registered provider can be exposed. Static table ID mismatches with `STRATIX10_NUM_CLKS` or dt-bindings would silently put clocks in wrong onecell slots. Critical clocks are marked selectively; missing a critical flag on boot-required fabric clocks could allow late unused-clock disabling to break the system. Many mux and bypass register offsets are literal constants, so hardware revision drift is risky.

## Test Signals
Useful tests include booting a Stratix10 DT with `intel,stratix10-clkmgr`, verifying `/sys/kernel/debug/clk/clk_summary`, checking that consumers can resolve all binding IDs, and exercising rate/parent changes for MPU, NOC, EMAC, SDMMC, and GPIO debounce clocks. Negative tests should confirm missing optional clocks return `-ENOENT` rather than stale pointers.
