# sources/distributed-fs/ceph-client/drivers/clk/clk_test.c

## Purpose

`clk_test.c` is the KUnit coverage for the common clock framework core. It builds dummy providers, muxes, orphan topologies, OF overlays, platform-device fixtures, notifiers, and assigned-rate scenarios to validate consumer-visible behavior of `clk.c` without real hardware.

## Important APIs, Types, And Functions

The file defines dummy provider contexts and ops: `clk_dummy_context` with recalc/determine/set-rate callbacks, maximizing and minimizing determine-rate variants, single-parent mux callbacks, `clk_multiple_parent_ctx` with mutable current parent, `clk_leaf_mux_ctx` for set-rate-parent forwarding tests, notifier contexts, parent-data test parameter structures, platform-driver device context, assigned-rate contexts, and `clk_hw_get_dev_of_node` fixtures.

Important setup helpers include `clk_test_init_with_ops()`, `clk_multiple_parents_mux_test_init()`, orphan init functions, `clk_single_parent_mux_test_init()`, two-level orphan setup, `clk_leaf_mux_set_rate_parent_test_init()`, `clk_mux_notifier_test_init()`, `clk_mux_no_reparent_test_init()`, parent-data OF/device setup, `kunit_of_platform_driver_dev()`, `clk_assigned_rates_test_init()`, and the dev/of-node accessor setup.

The registered suites are `clk_assigned_rates`, `clk_hw_get_dev_of_node_test_suite`, `clk-leaf-mux-set-rate-parent`, `clk-test`, `clk-multiple-parents-mux-test`, `clk-mux-no-reparent`, `clk-mux-notifier`, `clk-orphan-transparent-multiple-parent-mux-test`, `clk-orphan-transparent-single-parent-test`, `clk-orphan-two-level-root-last-test`, `clk-range-test`, `clk-range-maximize-test`, `clk-range-minimize-test`, `clk_register_clk_parent_data_of`, `clk_register_clk_parent_data_device`, `clk-single-parent-mux-test`, and `clk-uncached-test`.

## Control Flow

Each suite constructs a small clock topology in `.init`, runs one or more assertions, and tears down either with explicit `.exit` callbacks or KUnit-managed actions from `clk_kunit_helpers.c`. Basic rate suites register a single dummy root clock and verify `clk_get_rate()`, `clk_set_rate()`, repeated set, and round/set consistency. The uncached suite uses `CLK_GET_RATE_NOCACHE` and mutates backing state behind the framework to verify recalc behavior.

Mux suites build parent clocks and a child mux. Multi-parent tests verify `clk_get_parent()`, `clk_has_parent()`, range behavior around parent switches, and document a skipped range-on-reparent gap. Orphan suites register children before parents or with missing parents to verify null parent reporting, later `clk_set_parent()`, orphan-to-valid transitions, range preservation, `clk_put()` behavior, and two-level orphan reparenting. Single-parent tests verify parent discovery and range aggregation through parent/child relationships, with skipped tests documenting unimplemented disjoint-range checks.

Range suites use dummy determine-rate callbacks that either echo, maximize, or minimize within requested bounds. They validate invalid ranges, multiple consumer range intersection, clamping during round/set, consistency of round and set, and reevaluation when a consumer drops a range or is put. The leaf mux suite parameterizes calls to `__clk_determine_rate()`, mux determine helpers, and no-reparent determine helper to verify forwarded requests preserve the real upstream mux as `best_parent_hw`.

Notifier tests register a notifier on a mux, switch to a different parent, and wait for `PRE_RATE_CHANGE` and `POST_RATE_CHANGE` with expected old/new rates. No-reparent tests verify `clk_hw_determine_rate_no_reparent()` keeps the current parent for round and set requests. Parent-data tests parameterize OF and device lookup cases for `struct clk_parent_data` fields, including precedence of `hw`, `fw_name`, `index`, and `name`. Assigned-rate tests apply DT overlays and verify provider or consumer `assigned-clock-rates` and `assigned-clock-rates-u64` are applied or skipped. Accessor tests verify `clk_hw_get_dev()` and `clk_hw_get_of_node()` for registrations with a device, a device without OF node, no device, an OF node, or no OF node.

## State And Persistence Behavior

The test state is per-suite and per-test through `test->priv`, KUnit allocations, overlays, provider registrations, and managed cleanup actions. Dummy providers store mutable `rate` and `current_parent` values so assertions can observe framework effects. The file does not persist data outside the kernel test runtime. It intentionally relies on correct cleanup to avoid cross-test contamination in global clock lists and OF provider lists.

## Dependencies And Integration Points

The file depends on the common clock consumer/provider APIs, internal `clk.h`, KUnit clock helpers, KUnit OF overlays, KUnit platform-device helpers, `kunit_clk_assigned_rates.h`, and `clk_parent_data_test.h`. It is tightly coupled to `clk.c` behavior and to overlay data declared through `OF_OVERLAY_DECLARE()` and `of_overlay_apply_kunit()`.

## Risks And Edge Cases

The tests cover many subtle cases but also identify known limitations through `kunit_skip()`: range constraints are not reevaluated after some parent changes, and disjoint parent/child ranges are not fully rejected across the tree. Because the tests use global clock names such as `test-clk` and `parent-0`, cleanup ordering and uniqueness are important. Some tests manually unregister clocks instead of using managed helpers, so a failed setup path could leave state behind if it occurs after partial registration in those paths. Notifier tests depend on a timeout and waitqueue signal; failures can reflect missed notifications or timing issues.

## Test Signals

This file is the direct test signal for `clk.c`, `clk.h`, `clk_kunit_helpers.c`, and `clk_parent_data_test.h`. Passing suites indicate that basic rate APIs, uncached behavior, range clamping/intersection, mux parent selection, no-reparent semantics, orphan recovery, notifier delivery, OF/device parent-data lookup, assigned rates, and device/node accessors match expected behavior. Skipped tests should be tracked as intentional coverage holes rather than successful behavior.
