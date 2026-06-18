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
