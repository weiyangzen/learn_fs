# sources/distributed-fs/ceph-client/drivers/clk/nuvoton/clk-ma35d1.c

Purpose: Main platform clock driver for the Nuvoton MA35D1 SoC. It registers a one-cell hardware clock provider with fixed oscillators, PLLs, muxes, dividers, fixed factors, and gates for CPU, system, bus, storage, USB, graphics, timers, UARTs, I2C, SPI, watchdogs, audio, ADC, and other peripherals.

Important APIs, types, and functions: `ma35d1_clocks_probe()` maps the clock controller, parses five `nuvoton,pll-mode` entries with `ma35d1_get_pll_setting()`, allocates `struct clk_hw_onecell_data`, and fills the `hws[]` array up to `CLK_MAX_IDX`. Local helper wrappers register fixed, mux, divider, table divider, pow2 divider, fixed-factor, and gate clocks. The driver registers via `platform_driver_register()` at `postcore_initcall()`.

Control flow: Probe allocates provider storage, maps resource 0, validates PLL modes, registers oscillators and PLLs first, then derived CPU/system/bus clocks, then large groups of peripheral mux/div/gate clocks. It ends by calling `devm_of_clk_add_hw_provider()`.

State and persistence: Clock topology is devm-managed and tied to the platform device. The shared `ma35d1_lock` serializes mux, divider, and gate register accesses. Hardware registers retain rate, parent, and gate state.

Dependencies and integration points: Depends on `dt-bindings/clock/nuvoton,ma35d1-clk.h`, device-tree parent clock names such as `hxt`, register resource mapping, and helper files for PLL and ADC divider registration. Consumers use clock IDs from the binding through the one-cell provider.

Risks: The file is highly table/offset driven, so wrong shifts, widths, parent arrays, or clock IDs produce silent topology bugs. The probe does not check most individual `hws[]` results before publishing the provider. Some parent data entries use `.index = -1` placeholders, so mux widths must not allow invalid selections to leak to consumers. The ADC divider mask argument appears suspicious relative to the helper API.

Test signals: Boot should bind `"nuvoton,ma35d1-clk"` before device consumers probe and publish `CLK_MAX_IDX` clocks. `clk_summary` should show all named gates and parents. DT schema tests should require five valid `nuvoton,pll-mode` strings. Runtime tests should cover representative UART, timer, CAN, SDH, ADC, and PLL rate changes.
