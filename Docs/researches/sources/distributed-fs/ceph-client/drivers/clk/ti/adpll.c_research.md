# sources/distributed-fs/ceph-client/drivers/clk/ti/adpll.c

## Purpose

`adpll.c` is a platform driver for TI DM814x ADPLL clocks. It maps an ADPLL register block, registers a DCO clock and its derived internal/output clocks, and exposes the configured outputs through a device-tree onecell provider. It supports both ADPLL-S and ADPLL-LJ layouts.

## Important APIs, Types, And Functions

The file defines register offsets and bit positions for PLLSS lock/unlock, power control, clock control, dividers, fractional divider, bandwidth control, status, M3 divider, and ramp control. `struct ti_adpll_platform_data` describes layout differences: type S has three inputs and four outputs with DCO as an output; type LJ has two inputs and three outputs. `struct ti_adpll_data` owns the device, mapped registers, physical address, spinlock, parent names/clocks, registered clocks, onecell outputs, and embedded DCO `clk_hw`.

Helper constructors register dividers, muxes, gates, fixed factors, and custom clkout clocks. `ti_adpll_prepare()` clears idle bypass and waits for lock; `ti_adpll_unprepare()` sets idle bypass; `ti_adpll_recalc_rate()` computes DCO rate from M/N/fractional fields and type-S multipliers. `ti_adpll_init_children_adpll_s()` and `_lj()` build the topology for each hardware variant. `ti_adpll_probe()` wires all steps together and `ti_adpll_remove()` unregisters resources.

## Control Flow

Probe allocates `ti_adpll_data`, maps resource 0, unlocks the global PLLSS MMR for type S, chooses the register base offset, resolves parent clocks from DT, allocates clock bookkeeping, registers the DCO and internal N2 divider, then registers type-specific children. Type S creates bypass mux, M2 divider, div2 fixed factor, `clkout`, `clkoutx2`, optional HIF mux, and M3 output. Type LJ creates gated DCO output, M2 divider, gated M2 output, bypass mux, and `clkout`. Finally the driver adds an OF clock provider.

Runtime output parent selection reflects hardware bypass status: clkouts use DCO-derived parents when not bypassed and bypass parents when the status bit says bypass. Gates delegate to `clk_gate_ops` with the ADPLL spinlock. Resource cleanup walks registered clocks in reverse order, drops clkdev lookups, and calls stored unregister callbacks.

## State And Persistence Behavior

Hardware registers retain PLL power, bypass, lock, divider, and gate state. The driver stores in-memory clock registration data and clkdev lookups for legacy con_id lookup. Spinlock-protected register access coordinates shared ADPLL control fields. The provider's output array persists until device removal.

## Dependencies And Integration Points

The driver depends on platform devices, OF, CCF, clkdev, MMIO accessors, and DT compatibles `ti,dm814-adpll-s-clock` and `ti,dm814-adpll-lj-clock`. It integrates with parent clocks listed in DT, output names from `clock-output-names`, and legacy clkdev con_id naming derived from the physical address.

## Risks And Edge Cases

Type-S HIF handling registers M3 using `d->clocks[TI_ADPLL_HIF].clk`, but HIF is only initialized when the third parent clock is present; the earlier input validation normally requires it. `ti_adpll_prepare()` ignores the return value from `ti_adpll_wait_lock()` and always returns zero, so lock failures may be visible only through logs and a false prepared state. Rate recalc returns zero in bypass because DCO output is considered low. The driver mixes devm-managed registration with explicit unregister callbacks in its error/remove cleanup path, so cleanup behavior should be checked carefully for double-unregister regressions if refactored.

## Test Signals

Compile with `CONFIG_COMMON_CLK_TI_ADPLL` built-in and module. Probe DT nodes for both ADPLL-S and ADPLL-LJ, verify all `clock-output-names` are present, and inspect onecell outputs. Exercise prepare/unprepare, bypass parent switching, clkout gates, and DCO rate calculation against programmed M/N/fractional registers. Fault-injection or hardware tests should validate lock-timeout logging and behavior when parent clocks are missing.
