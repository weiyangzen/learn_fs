# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-gate.c

Purpose: this file implements OWL gate clocks and a helper used by composite clocks.

Important functions: `owl_gate_set()` reads a gate register, computes whether the target bit should be set or cleared based on `CLK_GATE_SET_TO_DISABLE` and the requested enable state, and writes the register back. `owl_gate_enable()`, `owl_gate_disable()`, and `owl_gate_is_enabled()` adapt that helper to `clk_ops`. `owl_gate_clk_is_enabled()` reads the register and inverts the bit interpretation for set-to-disable gates.

Control flow/state: enable state is persisted in hardware gate bits. The code uses full regmap read/modify/write cycles and no local cache.

Dependencies and integration: composite clocks use `owl_gate_set()` and `owl_gate_clk_is_enabled()` directly. Standalone gate clocks are declared by `OWL_GATE` or `OWL_GATE_NO_PARENT`.

Risks and tests: there is no explicit locking in the helper, so multi-field shared registers rely on regmap and framework serialization. Set-to-disable polarity must be correct for each gate. Test signals are gate enable/disable/is_enabled symmetry, clocks marked `CLK_IGNORE_UNUSED`, and checking that unrelated bits survive read/modify/write cycles.
