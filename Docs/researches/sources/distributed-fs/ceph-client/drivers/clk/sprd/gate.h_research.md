# sources/distributed-fs/ceph-client/drivers/clk/sprd/gate.h

## Purpose
Declares Spreadtrum gate clock structures, flags, and macro families for normal, set/clear, PLL set/clear, parent-hw, and firmware-name parents.

## Important APIs, Types, And Functions
`struct sprd_gate` stores enable mask, flags, set/clear offset, optional delay, and common clock data. `SPRD_GATE_NON_AON` marks gates whose register block should be read only when the parent is enabled. Macro families include `SPRD_GATE_CLK`, `SPRD_SC_GATE_CLK`, `SPRD_PLL_SC_GATE_CLK`, and `_HW`/`_FW_NAME` variants.

## Control Flow
Macro expansion chooses one of the exported ops tables and initializes static gate objects. Runtime behavior is provided by `gate.c`.

## State And Persistence
Static metadata persists masks, flags, register offsets, and delay settings. Hardware stores the actual enable state.

## Dependencies And Integration Points
Includes `common.h` and is consumed by SoC clock tables for most domain enable clocks. The flags intentionally share CCF gate flag values and add Spreadtrum-specific bits from bit 3 upward.

## Risks And Edge Cases
The macro matrix is broad; choosing the wrong parent form or ops table can create a clock that registers but cannot safely control hardware. `CLK_GATE_HIWORD_MASK` is reserved by comments but not implemented in `gate.c`, so users must not assume generic gate semantics unless code supports them.

## Test Signals
Compile tests for all macro variants, clock summary parent correctness, and hardware toggling checks for normal gates, set/clear gates, PLL gates, and non-AON gates.
