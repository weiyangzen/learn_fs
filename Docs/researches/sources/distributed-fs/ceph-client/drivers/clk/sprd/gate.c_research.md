# sources/distributed-fs/ceph-client/drivers/clk/sprd/gate.c

## Purpose
Implements Spreadtrum gate clocks, including normal read-modify-write gates, set/clear-register gates, and PLL gates that delay after prepare.

## Important APIs, Types, And Functions
Exports `sprd_gate_ops`, `sprd_sc_gate_ops`, and `sprd_pll_sc_gate_ops`. Core helpers are `clk_gate_toggle`, `clk_sc_gate_toggle`, and `sprd_gate_is_enabled`. PLL prepare uses `sprd_pll_sc_gate_prepare` with `udelay`.

## Control Flow
Enable/disable callbacks compute whether setting a bit means enable or disable, then either update the base register or write the mask to a set/clear companion register. `is_enabled` optionally checks the parent first for `SPRD_GATE_NON_AON`, reads the base register, applies `CLK_GATE_SET_TO_DISABLE`, and returns bit state.

## State And Persistence
Gate state persists in hardware enable registers. Set/clear gates write transient command registers but read state from the base register. The only in-memory state is each gate's mask, flags, set/clear offset, and delay.

## Dependencies And Integration Points
Depends on CCF gate semantics, regmap, delay APIs, and parent-clock state checks. SoC files use gate macros for PMU, AHB/APB, AON, multimedia, and PLL enable controls.

## Risks And Edge Cases
Normal gates do read-modify-write without a local lock and ignore regmap errors. Set/clear offset must match hardware layout exactly. `SPRD_GATE_NON_AON` prevents reads while parent power is off, but incorrect parent modeling can still cause unsafe reads. PLL gates need correct settle delays.

## Test Signals
Enable/disable tests should confirm base/set/clear register writes and `is_enabled` behavior. Boot should avoid unused critical gates being shut off incorrectly. PLL consumers should work after prepare delays.
