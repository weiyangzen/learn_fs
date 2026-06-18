# sources/distributed-fs/ceph-client/drivers/clk/st/clk-flexgen.c

## Purpose
This file implements ST flexgen clocks, which combine a parent crossbar mux, pre-divider gate, pre-divider, final divider gate, final divider, and optional asynchronous-mode control into one Linux clock. It supports generic DT-provided output names and several STiH-specific static output lists with critical clock annotations.

## Important APIs, Types, And Functions
`struct flexgen` embeds `clk_mux`, two `clk_gate`s, and two `clk_divider`s. `flexgen_ops` implements enable, disable, is_enabled, parent switching, rate determination, rate recalculation, and rate setting. `clk_register_flexgen()` wires one logical flexgen output to register offsets derived from the output index. `st_of_flexgen_setup()` is the OF entry point registered by `CLK_OF_DECLARE(flexgen, "st,flexgen", ...)`.

## Control Flow
The OF setup maps the parent node registers, gathers parent names, chooses compatible-specific `struct clkgen_data`, allocates `clk_onecell_data`, and registers each non-empty output. Enable turns on both pre and final gates. Disable only turns off the final gate. Rate setting computes a best divider, optionally clears the sync/control bit, then places the division either in the final divider for `div <= 64` or in the pre-divider for larger divisors to avoid duty-cycle problems.

## State And Persistence
Runtime state is held in hardware registers for mux selection, gates, dividers, and sync. The allocated `flexgen`, lock, parent-name array, and onecell data persist after early clock registration. Some outputs are marked `CLK_IS_CRITICAL` because they keep memory, bus interconnect, or CPU paths alive.

## Dependencies And Integration Points
The code depends on the common clock framework primitive ops (`clk_mux_ops`, `clk_gate_ops`, `clk_divider_ops`), OF address mapping, `clock-output-names`, and ST compatible strings such as `st,flexgen-stih410-c0`, `st,flexgen-stih418-d2`, and `st,flexgen-video`. Consumers get clocks through the onecell provider.

## Risks
Index-derived offsets mean output order must match hardware layout exactly. Empty static names skip unused channels, so array position remains semantically important. Error paths do not fully unregister previously registered clocks, which is typical for early clock setup but makes partial failures hard to recover. The control-mode path clears the sync bit but does not restore it in the local function.

## Test Signals
Expected tests include boot-time provider registration, clock summary checks for parent/rate propagation, rate-setting tests above and below divider 64, critical-clock retention, and functional tests of display/audio/peripheral blocks that consume flexgen outputs.
