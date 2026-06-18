# sources/distributed-fs/ceph-client/block/bfq-iosched.c lines 7380-7682

## Scope

This chunk covers the tail of `block/bfq-iosched.c`, from BFQ's elevator sysfs show/store helpers through the `struct elevator_type` registration and module init/exit. It includes:

- Generic sysfs parsing/formatting helpers for scheduler tunables.
- Macro-generated show/store methods for BFQ tunables such as FIFO expiry, seek penalty, idling time, max budget, timeout, strict guarantees, and low-latency mode.
- The `bfq_attrs[]` sysfs attribute table exported through the elevator core.
- The `iosched_bfq_mq` elevator descriptor and its blk-mq scheduler callback table.
- BFQ module initialization, including optional blk-cgroup policy registration, slab-cache creation, reference weight-raising durations, and elevator registration.
- BFQ module teardown, including elevator unregister, optional cgroup policy unregister, and slab-cache destruction.

The source path sits under a Ceph-client snapshot tree, but this chunk is Linux block-layer BFQ I/O scheduler code. It is not Ceph filesystem logic.

## Purpose

This chunk is BFQ's public registration and configuration surface. It binds the internal BFQ scheduling implementation to the Linux elevator framework under the scheduler name `bfq`, exposes per-device tunables through elevator sysfs files, allocates the private `bfq_queue` slab cache used by runtime queues, and coordinates global module setup/teardown with optional blk-cgroup integration.

The sysfs methods let userspace tune BFQ policy at runtime for a specific `struct elevator_queue`. The elevator descriptor then wires those runtime settings and the rest of the file's request lifecycle functions into blk-mq: request preparation, dispatch, merge handling, completion, queue initialization, queue teardown, I/O-cq teardown, and depth limiting. Module init registers the scheduler only after all global prerequisites are ready; module exit reverses that registration before freeing global resources.

## Important APIs, Types, And Functions

`bfq_var_show()` formats an unsigned integer as a newline-terminated decimal string for sysfs. `bfq_var_store()` parses decimal input with `kstrtoul()` and stores the result in a caller-provided `unsigned long`. These helpers are intentionally small because all bounds and unit conversions are handled by the generated or hand-written store methods.

`SHOW_FUNCTION()` generates per-attribute show functions that load a field from `struct bfq_data`, optionally convert jiffies to milliseconds or nanoseconds to milliseconds, and call `bfq_var_show()`. The generated functions expose:

- `bfq_fifo_expire_sync_show()` and `bfq_fifo_expire_async_show()` for `bfqd->bfq_fifo_expire[1]` and `[0]`, converting nanoseconds to milliseconds.
- `bfq_back_seek_max_show()` and `bfq_back_seek_penalty_show()` for seek heuristics with no conversion.
- `bfq_slice_idle_show()` for `bfqd->bfq_slice_idle`, converting nanoseconds to milliseconds.
- `bfq_max_budget_show()` for `bfqd->bfq_user_max_budget`.
- `bfq_timeout_sync_show()` for `bfqd->bfq_timeout`, converting jiffies to milliseconds.
- `bfq_strict_guarantees_show()` and `bfq_low_latency_show()` for boolean policy flags.

`USEC_SHOW_FUNCTION()` generates `bfq_slice_idle_us_show()`, exposing the same `bfqd->bfq_slice_idle` idling window in microseconds. This provides finer precision than the millisecond `slice_idle` attribute while sharing the same underlying field.

`STORE_FUNCTION()` generates bounded sysfs store methods for most numeric tunables. It parses unsigned decimal input, clamps it to the supplied min/max range, converts units when needed, writes directly into the chosen `bfq_data` field, and returns the original byte count on success. The generated methods update FIFO expiries in nanoseconds, backward seek thresholds, backward seek penalty, and millisecond `slice_idle`.

`USEC_STORE_FUNCTION()` generates `bfq_slice_idle_us_store()`, which clamps microsecond input to `[0, UINT_MAX]` and stores `bfqd->bfq_slice_idle` in nanoseconds. This and `bfq_slice_idle_store()` are two interfaces to the same state, so the most recent write through either attribute wins.

`bfq_max_budget_store()` handles the `max_budget` attribute specially. A value of zero enables BFQ's automatic max-budget calculation via `bfq_calc_max_budget(bfqd)`, while a nonzero value is clamped to `INT_MAX` and assigned directly to `bfqd->bfq_max_budget`. The original user value, including zero for autotuning mode, is recorded in `bfqd->bfq_user_max_budget`.

`bfq_timeout_sync_store()` parses the `timeout_sync` attribute, clamps it to at least one millisecond and at most `INT_MAX`, converts it to jiffies, and updates `bfqd->bfq_timeout`. If max-budget autotuning is active (`bfq_user_max_budget == 0`), it immediately recomputes `bfq_max_budget` so the time-slice budget remains consistent with the new timeout.

`bfq_strict_guarantees_store()` clamps input to a boolean and stores `bfqd->strict_guarantees`. When enabling strict guarantees, it also raises `bfqd->bfq_slice_idle` to at least 8 ms if the current idling window is shorter. This makes the strict-guarantee mode materially change idling behavior, not just a flag checked later.

`bfq_low_latency_store()` clamps input to a boolean and stores `bfqd->low_latency`. When transitioning from enabled to disabled, it calls `bfq_end_wr(bfqd)` to end existing weight-raising periods for active, idle, and asynchronous BFQ queues. This prevents old low-latency boosts from persisting after userspace disables the feature.

`BFQ_ATTR(name)` creates `struct elv_fs_entry` attributes with mode `0644` and binds each sysfs name to its `bfq_*_show` and `bfq_*_store` functions. `bfq_attrs[]` exports the ten attributes above and terminates with `__ATTR_NULL`.

`iosched_bfq_mq` is the global `struct elevator_type` registered with the block elevator core. Its `.ops` table points to the rest of the BFQ implementation: `bfq_limit_depth`, `bfq_prepare_request`, `bfq_finish_requeue_request`, `bfq_finish_request`, `bfq_exit_icq`, `bfq_insert_requests`, `bfq_dispatch_request`, request ordering helpers, merge hooks, `bfq_has_work`, `bfq_depth_updated`, `bfq_init_queue`, and `bfq_exit_queue`. The descriptor also declares `icq_size = sizeof(struct bfq_io_cq)`, `icq_align = __alignof__(struct bfq_io_cq)`, the sysfs attributes, the elevator name `bfq`, and module ownership.

`bfq_slab_setup()` creates the global `bfq_pool` kmem cache for `struct bfq_queue` using `KMEM_CACHE(bfq_queue, 0)`. `bfq_slab_kill()` destroys it. Runtime queue allocation and freeing elsewhere in the file use this cache through `kmem_cache_alloc_node()` and `kmem_cache_free()`.

`bfq_init()` is the module initializer. With `CONFIG_BFQ_GROUP_IOSCHED`, it first registers `blkcg_policy_bfq` with the blk-cgroup core. It then creates the BFQ queue slab, initializes `ref_wr_duration[0]` and `[1]` for rotational and non-rotational weight-raising duration calculations, and registers `iosched_bfq_mq` through `elv_register()`. On failure it unwinds the slab and optional blkcg policy in reverse order.

`bfq_exit()` is the module exit function. It unregisters the elevator, unregisters the blk-cgroup policy when present, destroys the slab cache, and is bound through `module_exit()`. The module metadata declares `MODULE_ALIAS("bfq-iosched")`, GPL licensing, the author, and the description "MQ Budget Fair Queueing I/O Scheduler".

## Control Flow

Sysfs reads enter through the elevator core using entries in `bfq_attrs[]`. Each show function receives the live `struct elevator_queue`, obtains `struct bfq_data *bfqd` from `e->elevator_data`, reads a scheduler field, performs any outward-facing unit conversion, and writes a decimal value into the supplied buffer. There is no locking in these show paths in this chunk; they are simple reads of per-device scheduler configuration.

Sysfs writes follow a parse, clamp, convert, assign pattern. The generated store functions parse with `kstrtoul()`, reject parse errors by returning the negative error code, clamp values to the attribute-specific range, convert milliseconds or microseconds into internal units where required, and return `count` on success. Hand-written stores add policy coupling: `max_budget` may toggle autotuning, `timeout_sync` may recompute autotuned budget, `strict_guarantees` may lengthen idling, and disabling `low_latency` walks existing queues to clear weight-raising state.

Elevator registration flow is global and staged. `bfq_init()` optionally registers the cgroup policy, then creates the slab cache, then seeds `ref_wr_duration[]`, then registers `iosched_bfq_mq`. Only after `elv_register()` succeeds can block queues select the BFQ scheduler and invoke `bfq_init_queue()`. If slab creation or elevator registration fails, the function unwinds previously registered global resources before returning the error.

Per-request runtime flow is not implemented in this chunk, but the callback table is the dispatch map used by blk-mq. Requests are prepared through `bfq_prepare_request`, associated with a `struct bfq_io_cq`/`struct bfq_queue`, inserted through `bfq_insert_requests`, dispatched through `bfq_dispatch_request`, and completed or requeued through `bfq_finish_request`/`bfq_finish_requeue_request`. Merge-related callbacks keep BFQ's per-queue ordering and FIFO age metadata consistent when the block layer merges requests.

Queue lifecycle flow crosses this chunk through `.init_sched = bfq_init_queue` and `.exit_sched = bfq_exit_queue`. Initialization allocates and populates `struct bfq_data`, initializes the fallback OOM queue, actuator ranges, timers, service trees, root group, accounting flags, WBT state, and queue-depth settings. Teardown cancels the idle timer, deactivates idle queues, checks in-driver request accounting, releases root-group/cgroup resources, disables accounting, restores WBT defaults, and frees `bfq_data`.

Module exit reverses module init at a higher level. `elv_unregister(&iosched_bfq_mq)` first removes BFQ from the elevator registry so new queues cannot select it; normal elevator teardown is then responsible for calling `bfq_exit_queue()` for live users. The optional blkcg policy is unregistered after the elevator is gone, and the queue slab is destroyed last.

## State And Persistence Behavior

There is no on-disk persistence. State in this chunk is kernel-resident and scoped either globally to the module or per block device scheduler instance.

Global state includes `bfq_pool`, the `iosched_bfq_mq` elevator descriptor, and `ref_wr_duration[2]`. The slab cache exists for the module lifetime between `bfq_slab_setup()` and `bfq_slab_kill()`. `ref_wr_duration[0]` and `[1]` are initialized during module load and later used by responsiveness/weight-raising calculations to derive automatic weight-raising durations as peak-rate estimates change.

Per-device persistent state lives in `struct bfq_data`, reached from `elevator_queue->elevator_data`. The sysfs attributes in this chunk mutate fields such as `bfq_fifo_expire[]`, `bfq_back_max`, `bfq_back_penalty`, `bfq_slice_idle`, `bfq_user_max_budget`, `bfq_max_budget`, `bfq_timeout`, `strict_guarantees`, and `low_latency`. These settings affect all subsequent scheduling decisions for that request queue until the scheduler is changed, the block queue is destroyed, or the attributes are written again.

`bfq_user_max_budget` is the key persistence bit for the max-budget mode. Zero means the user wants autotuning, so BFQ recomputes `bfq_max_budget` from peak-rate and timeout information. Nonzero means the explicit user budget persists and suppresses automatic recalculation in paths such as `bfq_timeout_sync_store()` and `update_thr_responsiveness_params()`.

`bfq_slice_idle` is shared by both `slice_idle` and `slice_idle_us`. The millisecond interface and microsecond interface do not maintain separate values; whichever store runs last sets the same nanosecond-backed field.

Low-latency state has both a configuration flag and per-queue effects. `bfqd->low_latency` controls future heuristics, while existing queue boosts are represented by per-queue fields such as `wr_coeff`, `wr_cur_max_time`, `last_wr_start_finish`, and entity priority-change state. `bfq_low_latency_store()` clears those runtime boosts through `bfq_end_wr()` only on a transition from enabled to disabled.

Module metadata and `MODULE_ALIAS("bfq-iosched")` affect kernel module discovery/loading, not BFQ scheduling state.

## Dependencies And Integration Points

This chunk integrates with the Linux elevator framework through `struct elevator_type`, `struct elevator_mq_ops`, `elv_register()`, `elv_unregister()`, `struct elv_fs_entry`, `__ATTR()`, and `__ATTR_NULL`. The registered name `bfq` is the user-visible scheduler name, while the alias preserves module naming compatibility.

It integrates with blk-mq request scheduling through the callback table. The table expects the rest of `bfq-iosched.c` to implement queue depth limiting, request preparation, insertion, dispatch, merge handling, completion/requeue accounting, work detection, and scheduler instance lifecycle. It also uses generic request-ordering helpers `elv_rb_latter_request` and `elv_rb_former_request`.

It integrates with blk-cgroup when `CONFIG_BFQ_GROUP_IOSCHED` is enabled. `bfq_init()` registers `blkcg_policy_bfq`; per-queue initialization later activates the policy through `bfq_create_group_hierarchy()`, and teardown deactivates/unregisters it. The policy and group operations are implemented in `bfq-cgroup.c`, but this chunk owns the global registration sequencing.

It depends on Linux kernel parsing/time/unit helpers: `kstrtoul()`, `sprintf()`, `jiffies_to_msecs()`, `msecs_to_jiffies()`, `div_u64()`, `NSEC_PER_MSEC`, `NSEC_PER_USEC`, and `INT_MAX`/`UINT_MAX`. It also depends on `KMEM_CACHE()` and `kmem_cache_destroy()` for the BFQ queue slab.

The hand-written stores integrate with deeper BFQ policy code. `bfq_max_budget_store()` and `bfq_timeout_sync_store()` call `bfq_calc_max_budget()`, which uses `bfqd->peak_rate` and `bfqd->bfq_timeout`. `bfq_low_latency_store()` calls `bfq_end_wr()`, which locks `bfqd->lock`, iterates active/idle/async queues, ends per-queue weight raising, and marks entities for priority update. `bfq_strict_guarantees_store()` changes the idling window consumed by dispatch/idling logic such as `bfq_better_to_idle()` and the idle-slice timer path.

The queue lifecycle callbacks interact with WBT and block accounting indirectly. `bfq_init_queue()` disables default writeback throttling for the disk and enables block statistics accounting; `bfq_exit_queue()` restores WBT defaults and disables accounting. This chunk's elevator descriptor is the path by which the block layer reaches those lifecycle hooks.

## Risks And Edge Cases

The sysfs store functions update live scheduler fields without taking `bfqd->lock` in this chunk. Many fields are scalar and tolerate relaxed updates, but callers changing idling windows, timeouts, or budgets while I/O is active can observe transitional behavior. Any future change that makes these fields compound or dependent on additional invariants should revisit locking.

`bfq_var_show()` accepts an `unsigned int`, but generated show functions pass a `u64 __data`. Large values are truncated when formatted. Existing bounds and practical tunable ranges keep most values small, but nanosecond-to-millisecond and nanosecond-to-microsecond conversions should remain within unsigned-int range for exposed attributes.

The generated store functions use `unsigned long` input and return `count` even if clamping occurred. This is normal sysfs behavior for tunables, but it means userspace must read the value back to learn the effective value after bounds enforcement.

`slice_idle` and `slice_idle_us` share the same internal field with different input/output precision. Millisecond writes discard sub-millisecond precision that may have been set through `slice_idle_us`, and readback through the millisecond attribute truncates via integer division.

Enabling `strict_guarantees` can silently raise `bfq_slice_idle` to 8 ms. This is a deliberate policy coupling, but it can surprise userspace that expected only a boolean toggle. Disabling strict guarantees does not restore the previous idling value.

Disabling `low_latency` performs immediate per-queue weight-raising cleanup through `bfq_end_wr()`. That function walks active, idle, and async queues under `bfqd->lock`; changes to queue lists, cgroup async queues, or actuator counts must keep that traversal safe. Re-enabling low latency sets only the flag; future requests rebuild weight-raising state naturally.

`bfq_max_budget_store()` makes zero a mode switch rather than a literal zero budget. This must remain consistent with documentation and with code paths that check `bfq_user_max_budget == 0` before recomputing `bfq_max_budget`.

Module init unwind order is correctness-sensitive. If blkcg policy registration succeeds but slab creation or elevator registration fails, `blkcg_policy_unregister()` must run. If elevator registration fails after slab creation, `bfq_slab_kill()` must run before policy unregister. Exit order must keep the slab alive until the elevator is unregistered and live scheduler instances are gone.

The `icq_size` and `icq_align` fields must match `struct bfq_io_cq`. Any change to request-private assumptions such as `RQ_BIC(rq)` and `rq->elv.priv[]` must remain compatible with the elevator core's allocation of BFQ I/O contexts.

## Test Signals

Build coverage should include BFQ built-in and module configurations, with and without `CONFIG_BFQ_GROUP_IOSCHED`. Useful compile targets include block-layer configurations that enable blk-mq schedulers, cgroup I/O scheduling, and module loading/unloading.

Registration smoke tests should verify that the scheduler appears under the block queue scheduler list as `bfq`, can be selected for a test block device, and creates the expected sysfs attributes: `fifo_expire_sync`, `fifo_expire_async`, `back_seek_max`, `back_seek_penalty`, `slice_idle`, `slice_idle_us`, `max_budget`, `timeout_sync`, `strict_guarantees`, and `low_latency`.

Sysfs tests should write valid, invalid, below-minimum, and above-maximum values to each attribute. High-signal checks include parse errors returning failures, clamped readback values, `slice_idle`/`slice_idle_us` reflecting the same underlying state, zero `max_budget` enabling autotuning, `timeout_sync` updating an autotuned max budget, and `strict_guarantees=1` raising `slice_idle` to at least 8 ms.

Runtime scheduling tests should run mixed read/write workloads while changing tunables, watching for lockdep warnings, stalls, request leaks, and obvious scheduling regressions. Toggling `low_latency` during active I/O should not leave persistent weight-raised queues after the disable write.

Cgroup integration tests should load/select BFQ with blkcg enabled, create and remove blkcg hierarchies with active I/O, and then unload the module if modular. These tests exercise the registration order between `blkcg_policy_bfq`, elevator registration, per-queue policy activation, and teardown.

Lifecycle tests should repeatedly switch a block device between BFQ and another scheduler, run I/O during the switch where supported, and unload/reload the module. Kernel logs should remain free of warnings from `bfq_exit_queue()` accounting checks and slab lifetime issues.

Observability checks include validating that sysfs readback uses expected units: FIFO expiries and `slice_idle` in milliseconds, `slice_idle_us` in microseconds, and `timeout_sync` in milliseconds despite being stored internally in jiffies.
