# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mux.h

## Purpose
This header declares mux descriptors, predivider descriptors, constructor macros, helper prototypes, and notifier state for sunxi-ng mux clocks.

## Important APIs, Types, And Functions
Important types are `ccu_mux_fixed_prediv`, `ccu_mux_var_prediv`, `ccu_mux_internal`, `ccu_mux`, and `ccu_mux_nb`; macros include `_SUNXI_CCU_MUX*`, `SUNXI_CCU_MUX*`, and parent-data/hardware variants.

## Control Flow
No runtime flow is present. It defines data consumed by `ccu_mux.c` and by compound classes embedding `ccu_mux_internal`.

## State And Persistence
State includes bit offsets/widths, optional selector table, fixed/variable predivider arrays, enable bit, and notifier original-parent storage.

## Dependencies And Integration Points
It depends on CCF and `ccu_common`. Integration reaches CPU muxes, bus roots, module clocks, display clocks, and notifier-safe PLL consumers.

## Risks
Selector tables and predivider arrays must match hardware selector values, not logical parent indexes. Wrong values are hard to diagnose because clocks still register.

## Test Signals
Compile, parent selection, and rate determination tests validate it.
