# sources/distributed-fs/ceph-client/drivers/clk/socfpga/stratix10-clk.h

## Purpose
This header defines the hardware description records and registration API used by Stratix10-family, Agilex, N5X, and Agilex5 clock providers. It standardizes how SoC-specific topology tables describe PLLs, peripheral counters, gates, mux parents, divider fields, bypass controls, and onecell provider storage.

## Important APIs, Types, And Functions
`struct stratix10_clock_data` stores the MMIO base plus a trailing `clk_hw_onecell_data`. The clock record structs are `stratix10_pll_clock`, `stratix10_perip_c_clock`, `n5x_perip_c_clock`, `stratix10_perip_cnt_clock`, `stratix10_gate_clock`, `agilex5_pll_clock`, `agilex5_perip_cnt_clock`, and `agilex5_gate_clock`.

The prototypes expose registration helpers: `s10_register_pll()`, `agilex_register_pll()`, `n5x_register_pll()`, `agilex5_register_pll()`, `s10_register_periph()`, `n5x_register_periph()`, `s10_register_cnt_periph()`, `agilex5_register_cnt_periph()`, `s10_register_gate()`, `agilex_register_gate()`, and `agilex5_register_gate()`.

## Control Flow
There is no executable code. SoC drivers populate const arrays of these structures, then call the matching helper to allocate or register `clk_hw` implementations. The helpers interpret offsets, shifts, parent data, and flags according to the clock class.

## State And Persistence
The record structs are static topology descriptions. Runtime state is in registered `clk_hw` objects and in hardware registers addressed relative to the provider base. The onecell array stores exported clock handles by dt-binding ID.

## Dependencies And Integration Points
This header integrates SoC-specific clock-table files with shared implementation code in the SoCFPGA clock subsystem. It depends on CCF types, firmware-node parent data, and dt-binding IDs in individual providers.

## Risks
Many structs are similar but not interchangeable; using the wrong registration helper for a table silently misinterprets fields. `parent_name`, `parent_names`, `parent_data`, and `parent_hws` variants must match the helper and kernel CCF registration API. Array IDs must remain synchronized with DT bindings and the allocated onecell size.

## Test Signals
Compile coverage across Stratix10, Agilex, N5X, and Agilex5 configurations is important. Runtime validation should inspect `clk_summary`, parent names, divider rates, and gate states for each SoC family after boot.
