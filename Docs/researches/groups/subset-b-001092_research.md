# Research: subset-b-001092

Grouped research for Linux common clock framework sources under `sources/distributed-fs/ceph-client/drivers/clk/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk.c

## Purpose

`clk.c` is the core implementation of the Linux common clock framework consumer/provider API. It owns the global clock topology, implements public `clk_*`, `clk_hw_*`, and OF provider helpers, coordinates rate and parent changes through provider `struct clk_ops`, and maintains software state for prepare/enable counts, rate bounds, exclusivity, notifiers, runtime PM, debugfs, and orphan clocks. It is the central integration point between clock providers that register `struct clk_hw` objects and consumers that receive opaque `struct clk *` handles.

## Important APIs, Types, And Functions

The private state is centered on `struct clk_core`, which wraps provider-facing `struct clk_hw` with framework-owned state: name, ops, device, OF node, parent map, parent pointer, children, cached rate and requested rate, pending new-rate fields, flags, orphan status, runtime PM status, counts, rate bounds, accuracy, phase, duty cycle, consumers, notifiers, debugfs entry, and kref. `struct clk` is the consumer handle linked back to a `clk_core`; it carries the consumer device, `dev_id`, `con_id`, per-consumer min/max rate constraints, and exclusive-rate count. `struct clk_parent_map` caches parent resolution by direct `clk_hw`, resolved `clk_core`, firmware name, global name, or DT index.

Major exported consumer APIs include `clk_prepare()`, `clk_unprepare()`, `clk_enable()`, `clk_disable()`, `clk_get_rate()`, `clk_round_rate()`, `clk_set_rate()`, `clk_set_rate_exclusive()`, `clk_set_rate_range()`, `clk_set_min_rate()`, `clk_set_max_rate()`, `clk_get_parent()`, `clk_set_parent()`, `clk_set_phase()`, `clk_get_phase()`, `clk_set_duty_cycle()`, `clk_get_scaled_duty_cycle()`, `clk_is_match()`, and notifier registration helpers. Provider-facing helpers include `clk_hw_get_rate()`, `clk_hw_round_rate()`, `clk_hw_get_parent()`, `clk_hw_get_parent_by_index()`, `clk_hw_get_parent_index()`, `clk_hw_set_parent()`, `clk_hw_get_dev()`, `clk_hw_get_of_node()`, `clk_hw_init_rate_request()`, `clk_hw_forward_rate_request()`, `__clk_determine_rate()`, mux determine-rate helpers, registration helpers, and OF provider helpers.

Registration flows through `__clk_register()`, with public wrappers `clk_register()`, `clk_hw_register()`, `of_clk_hw_register()`, `devm_clk_register()`, and `devm_clk_hw_register()`. Teardown uses `clk_unregister()` and `clk_hw_unregister()`, with `clk_nodrv_ops` installed to make late consumers fail predictably after provider unregister.

OF integration is implemented with `struct of_clk_provider`, `of_clk_add_provider()`, `of_clk_add_hw_provider()`, `devm_of_clk_add_hw_provider()`, `of_clk_del_provider()`, `of_parse_clkspec()`, `of_clk_get_hw()`, `of_clk_get()`, `of_clk_get_by_name()`, parent-name helpers, `of_clk_detect_critical()`, and `of_clk_init()`.

## Control Flow

Registration starts by copying immutable init data into a freshly allocated `clk_core`, clearing `hw->init` so providers cannot use it after registration, populating parent maps, allocating the provider's own `hw->clk`, and linking it as a consumer. `__clk_core_init()` validates operation combinations, calls optional provider `.init`, resolves the initial parent with `__clk_init_parent()`, inserts the core into a parent child list, root list, or orphan list, hashes it by name, initializes accuracy/phase/duty/rate, prepares and enables critical clocks, and then attempts to reparent any existing orphans now satisfied by the new provider.

Prepare and enable are split by sleepability. `prepare_lock` is a recursive mutex-like lock used for topology and potentially sleeping provider operations. `enable_lock` is a recursive spinlock used for atomic enable/disable operations. `clk_core_prepare()` recursively prepares parents first, gets runtime PM for the provider, calls `.prepare`, increments `prepare_count`, and applies `CLK_SET_RATE_GATE` protection. `clk_core_enable()` requires the clock to be prepared, recursively enables the parent, calls `.enable`, and increments `enable_count`. Unprepare/disable reverse those paths and warn on critical or imbalanced use.

Rate changes are staged. `clk_set_rate()` takes `prepare_lock`, temporarily relaxes the caller's own exclusive protection if needed, and calls `clk_core_set_rate_nolock()`. The core rounds the requested rate with bounds, refuses protected direct changes, calculates the topmost affected clock with `clk_calc_new_rates()`, sends `PRE_RATE_CHANGE` notifiers through the affected subtree, performs parent/rate changes in `clk_change_rate()`, sends post notifications, and stores `req_rate`. Bounds are aggregated from the provider and all consumer handles, so per-user ranges intersect. `clk_set_rate_range_nolock()` updates a consumer's min/max range, validates the aggregate range, and clamps/reapplies the core requested rate, rolling back if the new range cannot be satisfied.

Parent changes use `clk_core_set_parent_nolock()`. It validates reparenting support and gating/protection constraints, finds the target parent index, runtime-resumes the provider, sends speculative pre-rate notifications, applies hardware parent changes through `__clk_set_parent()`, and recalculates subtree rates and accuracies. `__clk_set_parent_before()` and `__clk_set_parent_after()` migrate prepare/enable state between old and new parents to avoid races and glitches when the child is already prepared.

Orphan handling is continuous. Clocks whose declared parents are not registered enter `clk_orphan_list`; registering a new clock calls `clk_core_reparent_orphans_nolock()`, which tries to resolve orphans and move them into the live tree while preserving counts and recalculating rates.

## State And Persistence Behavior

All state is in memory and tied to kernel object lifetimes. Persistent disk state is not used. Cached state includes current rate, requested rate, accuracy, phase, duty cycle, parent pointer, resolved parent cache entries, prepare/enable/protect counts, notifier count, consumer constraints, runtime PM list membership, debugfs dentries, and OF provider list entries. State is protected by `prepare_lock`, `enable_lock`, `clk_rpm_list_lock`, `clk_debug_lock`, and `of_clk_mutex`. Debugfs exposes read-only summaries and per-clock state by default; write support exists only if `CLOCK_ALLOW_WRITE_DEBUGFS` is manually defined in source.

Runtime PM behavior is provider-device scoped. Registered clocks whose provider devices have runtime PM enabled join `clk_rpm_list`. Operations that may access provider hardware get and put runtime PM around callbacks. The late unused-clock pass calls `clk_pm_runtime_get_all()` before taking `prepare_lock` to avoid deadlocks with runtime PM callbacks that also use clock APIs.

## Dependencies And Integration Points

The file depends on core Linux facilities: `clk.h`, `clk-provider.h`, `clkdev`, device model, OF, runtime PM, debugfs, SRCU notifiers, hlist/list/hash tables, spinlocks/mutexes, modules, tracepoints, and initcalls. Provider drivers integrate by filling `struct clk_init_data`, `struct clk_hw`, and `struct clk_ops`, then registering through `clk_hw_register()` or OF/devm variants. Consumers integrate through clkdev/OF lookup and opaque `struct clk *` handles. Boot-time OF providers integrate through `of_clk_init()` and `CLK_OF_DECLARE` table linkage.

## Risks And Edge Cases

The highest-risk areas are topology mutation under concurrent prepare/enable users, rate propagation across parent chains, stale parent caches when providers unregister, orphan reparenting order, and aggregated rate-range semantics across multiple consumers. Notifier callbacks are explicitly risky because they must not re-enter top-level clock APIs while the framework holds `prepare_lock`. `clk_unregister()` on prepared or protected clocks warns but must still leave remaining consumers with safe no-driver ops. `CLOCK_ALLOW_WRITE_DEBUGFS` is intentionally dangerous because it exposes parent/rate/enable mutation to userspace. Known semantic gaps are documented by KUnit skipped tests: parent changes do not always reevaluate range constraints, and disjoint upstream/downstream ranges are not fully enforced.

## Test Signals

`clk_test.c` exercises most of this file's externally visible behavior: basic get/set/round rate, uncached rate recalc, single and multi-parent muxes, orphan reparenting, range constraints across users and puts, no-reparent determine-rate behavior, notifiers on parent change, `clk_parent_data` resolution through OF/device/direct hw, assigned clock rates from DT overlays, and `clk_hw_get_dev()`/`clk_hw_get_of_node()` accessors. The helper file `clk_kunit_helpers.c` supplies test-managed cleanup for clock gets, registration, providers, and prepare/enable operations. Skipped tests are useful signals of current limitations rather than passing guarantees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk.h -->
# sources/distributed-fs/ceph-client/drivers/clk/clk.h

## Purpose

`clk.h` is a small internal header for the clock framework implementation and adjacent helpers. It exposes framework-private entry points needed by code that cannot use only the public consumer/provider headers, notably OF-to-`clk_hw` lookup, clkdev hardware lookup, creation of a consumer `struct clk` from a provider `struct clk_hw`, and the internal put path.

## Important APIs, Types, And Functions

The header forward-declares `struct clk_hw`, `struct device`, and `struct of_phandle_args`. When both `CONFIG_OF` and `CONFIG_COMMON_CLK` are enabled, it declares `of_clk_get_hw(struct device_node *np, int index, const char *con_id)`. Otherwise it provides an inline stub returning `ERR_PTR(-ENOENT)`, allowing callers to compile without large ifdef blocks.

It declares `clk_find_hw(const char *dev_id, const char *con_id)`, which is implemented outside this file and used by `clk.c` parent resolution as a clkdev fallback. Under `CONFIG_COMMON_CLK`, it declares `clk_hw_create_clk()` and `__clk_put()`. Without common clock support, `clk_hw_create_clk()` is a cast-based inline stub returning the hardware pointer as a `struct clk *`, and `__clk_put()` is a no-op.

## Control Flow

There is no runtime control flow in this header beyond compile-time feature selection. Its role is to let the same callers build whether OF/common-clock support exists. The fallback paths are intentionally simple: OF lookup fails with `-ENOENT`, clock creation degenerates to a cast in non-common-clock builds, and put does nothing.

## State And Persistence Behavior

The header owns no state and persists nothing. It only defines declarations and inline compatibility stubs.

## Dependencies And Integration Points

This file integrates the common clock core with clkdev and OF-aware lookup code. `clk.c` includes it for `clk_hw_create_clk()`, `__clk_put()`, and OF lookup declarations. KUnit tests include it because `clk_hw_get_clk()` and direct provider-to-consumer creation are internal enough that the public headers alone are not sufficient.

## Risks And Edge Cases

The primary risk is configuration skew: callers must handle `ERR_PTR(-ENOENT)` when OF or common clock support is not compiled in. The non-common-clock cast stub is deliberately a compatibility shim, so code must avoid assuming a fully functional `struct clk` object in that configuration. The header relies on other headers to provide `ERR_PTR()` and full structure definitions where needed.

## Test Signals

`clk_test.c` includes this header and directly exercises `clk_hw_create_clk()`-backed behavior through `clk_hw_get_clk()` and KUnit-managed wrappers. Build coverage across `CONFIG_OF` and `CONFIG_COMMON_CLK` combinations is the main signal for the inline stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk_kunit_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk_kunit_helpers.c

## Purpose

`clk_kunit_helpers.c` provides test-managed wrappers for common clock framework operations. It converts manual cleanup requirements such as `clk_put()`, `clk_disable_unprepare()`, `clk_hw_unregister()`, and `of_clk_del_provider()` into KUnit actions that run automatically when a test exits or immediately on setup failure.

## Important APIs, Types, And Functions

`clk_prepare_enable_kunit()` calls `clk_prepare_enable()` and registers a reset action that calls `clk_disable_unprepare()`. `clk_get_kunit()`, `of_clk_get_kunit()`, and `clk_hw_get_clk_kunit()` wrap their respective get functions and funnel successful results through `__clk_get_kunit()`, which registers a `clk_put()` action. `clk_hw_get_clk_prepared_enabled_kunit()` composes managed `clk_hw_get_clk()` with managed prepare/enable.

Provider helpers include `clk_hw_register_kunit()` and `of_clk_hw_register_kunit()`, which register a hardware clock and attach automatic `clk_hw_unregister()`. `of_clk_add_hw_provider_kunit()` registers an OF hardware provider and attaches automatic `of_clk_del_provider()`. Action wrappers are declared with `KUNIT_DEFINE_ACTION_WRAPPER`.

## Control Flow

Each helper follows the same pattern: perform the real clock operation, return the original error if it fails, then call `kunit_add_action_or_reset()`. If the cleanup action cannot be added, KUnit immediately runs the reset action, so partially initialized resources do not leak into later tests. Composition is explicit in `clk_hw_get_clk_prepared_enabled_kunit()`: get the consumer first, then prepare/enable it, returning an error pointer if either stage fails.

## State And Persistence Behavior

The helpers do not own persistent state. They register cleanup callbacks in the KUnit resource/action system. Clock state changes are delegated to the common clock core, and test lifetime determines cleanup ordering. Returned clocks remain valid until the test action runs or the caller manually drops them only if it deliberately bypasses the managed lifetime contract.

## Dependencies And Integration Points

The file depends on public clock consumer/provider APIs, KUnit resources, error-pointer conventions, and OF provider APIs. It is compiled as a GPL module helper for tests and exported with `EXPORT_SYMBOL_GPL()` so KUnit test objects can use the wrappers. `clk_test.c` uses these helpers for provider registration, OF provider registration, managed consumer gets, and managed prepare/enable.

## Risks And Edge Cases

The main risk is cleanup ordering in tests that combine providers, consumers, and OF overlays. Tests should register dependent resources in an order that lets KUnit unwind safely. `clk_hw_get_clk_prepared_enabled_kunit()` returns `ERR_PTR(ret)` if prepare/enable fails after a managed get has already been registered; the get cleanup still runs at test exit because the prior wrapper succeeded. Callers must keep standard `IS_ERR()` handling for all returned clock pointers.

## Test Signals

This file is itself infrastructure for the clock KUnit suites. Its correctness is indirectly exercised by the broad set of tests in `clk_test.c`; failures would normally appear as leaked providers, stale OF providers, unbalanced prepare/enable counts, or use-after-unregister behavior between tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk_kunit_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk_parent_data_test.h -->
# sources/distributed-fs/ceph-client/drivers/clk/clk_parent_data_test.h

## Purpose

`clk_parent_data_test.h` centralizes string constants used by clock parent-data KUnit tests and their DT overlays. It keeps the expected legacy names, firmware names, and generated parent names consistent between C test logic and overlay data.

## Important APIs, Types, And Functions

The file defines four macros: `CLK_PARENT_DATA_1MHZ_NAME`, `CLK_PARENT_DATA_PARENT1`, `CLK_PARENT_DATA_PARENT2`, and `CLK_PARENT_DATA_50MHZ_NAME`. There are no functions or types.

## Control Flow

There is no runtime control flow. The constants are substituted at compile time into test cases that build `struct clk_parent_data` values.

## State And Persistence Behavior

The header has no state and no persistence behavior. It only provides compile-time string literals.

## Dependencies And Integration Points

`clk_test.c` includes this header for the `clk_register_clk_parent_data_of_*`, `clk_register_clk_parent_data_device_*`, and direct-`hw` parent-data parameter tables. The values must align with the KUnit DT overlay data referenced through `kunit_clk_parent_data_test`.

## Risks And Edge Cases

Because this header is the shared contract between test code and overlay contents, changing a string without updating the overlay will produce parent lookup failures rather than compile errors. The include guard prevents duplicate macro definitions.

## Test Signals

The parent-data suites in `clk_test.c` verify these constants by expecting parent lookup through OF index, firmware name, global name, and direct hardware pointer to resolve to the intended clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk_parent_data_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk_test.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk_test.c -->
