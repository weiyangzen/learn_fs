# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-composite.c

Purpose: this file implements composite OWL clocks that combine mux, gate, and one rate component. The rate component can be a divider, factor table, fixed factor, or pass-through mux/gate-only clock.

Important functions/APIs: mux callbacks delegate to `owl_mux_helper_get_parent()` and `owl_mux_helper_set_parent()`. Gate callbacks delegate to `owl_gate_set()` and `owl_gate_clk_is_enabled()`. Divider callbacks wrap `divider_determine_rate()`, `owl_divider_helper_recalc_rate()`, and `owl_divider_helper_set_rate()`. Factor callbacks wrap `owl_factor_helper_round_rate()`, `owl_factor_helper_recalc_rate()`, and `owl_factor_helper_set_rate()`. Fixed-factor callbacks invoke the core `clk_fixed_factor_ops` for determine/recalc and return success for set-rate because the rounded rate is already constrained.

Control flow/state: all state lives in CMU registers addressed by the embedded mux/gate/rate descriptors. Calls are synchronous regmap read/modify/write operations and do not persist extra software state.

Integration points: the exported `owl_comp_div_ops`, `owl_comp_fact_ops`, `owl_comp_fix_fact_ops`, and `owl_comp_pass_ops` are wired by macros in `owl-composite.h` and used heavily in S500/S700/S900 descriptor files.

Risks and tests: helper operations are not internally locked, so correctness relies on regmap serialization and clock framework call ordering. Shared registers containing mux, gate, and divider fields are vulnerable to bad masks. Test signals include parent switching, gate toggling, rate rounding/set/recalc, and DT consumers for SD, UART, display, and peripheral clocks.
