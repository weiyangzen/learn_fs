# Research: sources/distributed-fs/ceph-client/block/bfq-iosched.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000921`: lines 1-7379, `Docs/researches/chunks/subset-b-000921_research.md`
- `subset-b-000922`: lines 7380-7682, `Docs/researches/chunks/subset-b-000922_research.md`

## Chunk Research

### subset-b-000921: lines 1-7379

# sources/distributed-fs/ceph-client/block/bfq-iosched.c lines 1-7379

## Scope And Purpose

This chunk covers almost all executable scheduler logic for the BFQ multi-queue block I/O scheduler, stopping just before the sysfs attribute helpers and module/elevator registration. BFQ is described here as a proportional-share scheduler built around per-process `bfq_queue` objects, sector budgets, B-WF2Q+ scheduling entities, low-latency weight raising, hierarchical cgroup scheduling, queue merging, device idling, request injection, and blk-mq elevator hooks.

The code in this range owns the lifecycle of BFQ queues and their association with `io_context` state, chooses and dispatches requests, updates budgets and peak-rate estimates, decides when to idle or expire the in-service queue, tracks request completion, manages async queues and cgroup/root-group references, initializes per-device `bfq_data`, and creates the `bfq_queue` slab cache. Later lines in the file expose these internals through tunables and register the scheduler; this chunk provides the implementation they operate on.

## Important APIs And Types

`bfq_data`, `bfq_queue`, `bfq_entity`, `bfq_group`, `bfq_io_cq`, `bfq_iocq_bfqq_data`, `bfq_service_tree`, and `bfq_sched_data` are defined in `bfq-iosched.h` and are the core state containers used throughout this chunk. `bfq_data` is the per-request-queue scheduler instance. `bfq_queue` is the leaf queue holding requests for one sync or async flow and one actuator. `bfq_entity` is the B-WF2Q+ schedulable node used for both queues and cgroup groups. `bfq_io_cq` binds a task I/O context to per-actuator sync/async BFQ queues and stores saved state used across merges and splits.

The `BFQ_BFQQ_FNS()` macro generates flag accessors for per-queue state: `just_created`, `busy`, `wait_request`, `non_blocking_wait_rq`, `fifo_expire`, `has_short_ttime`, `sync`, `IO_bound`, `in_large_burst`, `coop`, `split_coop`, and `softrt_update`. These flags drive most control-flow decisions around low-latency treatment, idling, merging, and expiration.

Request and queue association helpers include `bic_to_bfqq()`, `bic_set_bfqq()`, `bic_to_bfqd()`, `icq_to_bic()`, `bfq_bic_lookup()`, `bfq_prepare_request()`, `bfq_init_rq()`, `bfq_get_bfqq_handle_split()`, `bfq_get_queue()`, `bfq_init_bfqq()`, `bfq_exit_icq()`, `bfq_exit_bfqq()`, and `bfq_put_queue()`. Requests store their BFQ private pointers in `rq->elv.priv[0]` and `rq->elv.priv[1]` via `RQ_BIC(rq)` and `RQ_BFQQ(rq)`.

Request ordering and insertion are handled by `bfq_choose_req()`, `bfq_find_next_rq()`, `bfq_check_fifo()`, `bfq_add_request()`, `bfq_remove_request()`, `bfq_insert_request()`, `bfq_insert_requests()`, merge hooks `bfq_bio_merge()`, `bfq_request_merge()`, `bfq_request_merged()`, `bfq_requests_merged()`, and `bfq_allow_bio_merge()`. Requests are tracked in both an rb-tree sorted by sector and a FIFO list with per-sync/async expiration times.

Scheduler selection and dispatch are centered on `bfq_select_queue()`, `bfq_dispatch_rq_from_bfqq()`, `__bfq_dispatch_request()`, `bfq_dispatch_request()`, `bfq_has_work()`, `bfq_schedule_dispatch()`, and `bfq_dispatch_remove()`. Expiration and budget feedback are implemented by `bfq_bfqq_expire()`, `__bfq_bfqq_expire()`, `__bfq_bfqq_recalc_budget()`, `bfq_bfqq_budget_timeout()`, `bfq_may_expire_for_budg_timeout()`, `bfq_set_budget_timeout()`, and `bfq_bfqq_is_slow()`.

Low-latency and throughput heuristics include `bfq_wr_duration()`, `bfq_update_bfqq_wr_on_rq_arrival()`, `bfq_bfqq_softrt_next_start()`, `bfq_update_wr_data()`, `bfq_bfqq_end_wr()`, `bfq_end_wr()`, `bfq_handle_burst()`, `bfq_update_io_intensity()`, `bfq_update_io_thinktime()`, `bfq_update_io_seektime()`, `bfq_update_has_short_ttime()`, `bfq_better_to_idle()`, `idling_boosts_thr_without_issues()`, and `idling_needed_for_service_guarantees()`.

Queue cooperation is handled by the request-position tree and merge helpers: `bfq_pos_tree_add_move()`, `bfq_find_close_cooperator()`, `bfq_setup_cooperator()`, `bfq_setup_merge()`, `bfq_setup_stable_merge()`, `bfq_do_or_sched_stable_merge()`, `bfq_merge_bfqqs()`, `bfq_split_bfqq()`, `bfq_put_cooperator()`, and `bfq_bfqq_save_state()` / `bfq_bfqq_resume_state()`.

Device and blk-mq integration helpers include `bfq_limit_depth()`, `bfq_depth_updated()`, `bfq_update_hw_tag()`, `bfq_update_peak_rate()`, `bfq_update_rate_reset()`, `bfq_calc_max_budget()`, `bfq_init_queue()`, `bfq_exit_queue()`, `bfq_init_root_group()`, `bfq_put_async_queues()`, and `bfq_slab_setup()`.

## Control Flow And Runtime Behavior

Request preparation is intentionally split. `bfq_prepare_request()` only attaches an `io_cq` and clears private pointers because a request can still become queue-less afterward. The real BFQ association happens in `bfq_init_rq()` during insertion or merging, when the request can no longer be transformed outside BFQ. At that point the code checks for I/O priority changes, updates cgroup membership, selects the actuator, obtains or creates a `bfq_queue`, increments allocated/request references up the entity tree, and stores the `bic` and `bfqq` in request-private fields.

Insertion flows through `bfq_insert_request()` under `bfqd->lock`. It first initializes the request, tries blk-mq/elevator merging, handles at-head or pass-through dispatch-list insertion, or calls `__bfq_insert_request()` for normal BFQ queueing. The queueing path may merge cooperating queues before insertion, updates think-time, seek-time, short-think-time, I/O intensity, low-latency state, next-request selection, per-queue FIFO expiration, and possibly idling state. If a request arrives while the queue is in service and waiting, the code may cancel the idle timer or expire the queue for budget timeout.

Dispatch starts at `bfq_dispatch_request()`, locks `bfqd`, calls `__bfq_dispatch_request()`, and updates debug stats after unlocking. `__bfq_dispatch_request()` first drains `bfqd->dispatch`, then refuses dispatch if there is no work, or if `strict_guarantees` requires one request at a time and one is already in the driver. Otherwise it calls `bfq_select_queue()` and dispatches the selected queue's `next_rq`. Dispatch charges service via `bfq_serv_to_charge()`, removes the request from BFQ's rb-tree/FIFO/hash structures, updates peak-rate sampling, increments in-driver counters per actuator, and marks `RQF_STARTED`.

`bfq_select_queue()` is the main decision point. It keeps the current in-service queue if it has budget and requests, expires it on budget timeout or exhaustion, or keeps it empty when device idling is useful. While idling, it can inject work from related async queues, a detected waker queue, a queue woken by the in-service queue, another queue within the in-service queue's adaptive inject limit, or an underused actuator. If no existing queue should continue, the function expires the current queue and obtains the next entity from the service-tree layer through `bfq_set_in_service_queue()`.

Queue expiration updates both fairness and latency state. `bfq_bfqq_expire()` detects slow/seeky queues, may charge elapsed time instead of actual sectors, updates soft real-time next-start windows, resets injection sampling, recalculates the next budget from the expiration reason, and calls `__bfq_bfqq_expire()` to requeue or deactivate the entity. Empty queues can remain busy after preemption when service guarantees require dispatch plugging. Otherwise they are deactivated, and `budget_timeout` is overloaded as the time when the queue became fully idle.

Completion flows through `bfq_finish_request()` or `bfq_finish_requeue_request()`. Started requests update cgroup completion stats, the injection-limit state machine, in-driver counters, hardware-tag detection, per-queue dispatched count, weight trees, last-completion timestamps, waker detection source, soft real-time delayed updates, and possible expiration or idling of the in-service queue. Every finish/requeue drops allocated counters, queue references, and `bic->requests`, then clears request private fields to avoid double handling.

The idle timer path uses `bfq_idle_slice_timer()` and `bfq_idle_slice_timer_body()`. It verifies the sampled queue is still in service, clears `wait_request`, expires the queue for budget timeout or too-idle when appropriate, and schedules dispatch. This timer is central to BFQ's dispatch plugging model: an empty in-service sync queue can deliberately hold service for a short period to wait for its next request.

## State And Persistence Behavior

BFQ state is in-memory scheduler state attached to the block request queue. It persists for the lifetime of the selected elevator instance, not across reboot or scheduler teardown. `bfq_init_queue()` allocates and initializes `bfq_data`, installs it into `eq->elevator_data`, initializes the fallback `oom_bfqq`, root group, idle timer, active/idle/dispatch lists, weight tree, burst list, actuator ranges, queue-depth limits, peak-rate estimates, and low-latency defaults. `bfq_exit_queue()` cancels the timer, deactivates idle queues, checks in-driver counters, tears down cgroup policy or async queues, re-enables writeback throttling defaults, disables blk-stat accounting, and frees `bfq_data`.

Per-request state is transient and reference-counted. Each request can hold a queue reference, and each task association holds a process reference. `bfqq_request_allocated()` and `bfqq_request_freed()` update entity `allocated` counters through ancestors; `bfq_put_queue()` frees a queue only after all process, request, stable-merge, service-tree, and weight-counter references have drained. Freeing a queue also removes it from burst and waker lists and warns if FIFO, rb-tree, or dispatched state is still non-empty.

Per-task `bfq_io_cq` state persists across individual queue merges and splits. `bfq_bfqq_save_state()` records weight raising, think time, short-think-time, I/O-bound, inject-limit, service-time, burst, and soft real-time fields before a queue is merged. `bfq_bfqq_resume_state()` restores that state when a dedicated queue is recreated after split, subject to low-latency settings and elapsed weight-raising windows. Stable merge references are stored in `bfqq_data[actuator].stable_merge_bfqq` and must be released on `bic_set_bfqq()` cancellation or ICQ exit.

Low-latency state is time-windowed. `wr_coeff`, `wr_cur_max_time`, `last_wr_start_finish`, `wr_start_at_switch_to_srt`, `service_from_wr`, and `soft_rt_next_start` determine whether a queue is interactive or soft real-time and how much weight raising it receives. `wr_busy_queues` tracks active weight-raised queues to adjust queue-depth limits and idling/injection decisions. Large-burst state in `bfqd->burst_list`, `burst_size`, `large_burst`, and `last_ins_in_burst` suppresses unnecessary weight raising and idling for many newly created related queues.

Device calibration state is continuously updated. `peak_rate`, `rate_dur_prod`, `budgets_assigned`, `bfq_max_budget`, `last_dispatch`, `first_dispatch`, `last_completion`, `peak_rate_samples`, `sequential_samples`, and `tot_sectors_dispatched` drive automatic budget and weight-raising duration calculations. Hardware queueing state is inferred through `hw_tag`, `max_rq_in_driver`, and `hw_tag_samples`, and affects queue merging/idling decisions through `nonrot_with_queueing`.

Actuator state is maintained per independent access range. `bfq_init_queue()` copies `disk->ia_ranges` when available, otherwise it uses a single full-disk range. `bfq_actuator_index()` maps bio end sector to an actuator. Active queues and in-driver request counters are per actuator, and selection can inject from underused actuators to keep multi-actuator devices busy without losing per-actuator accounting.

## Dependencies And Integration Points

This code integrates tightly with the Linux blk-mq elevator API: `blk_mq_run_hw_queues()`, `blk_mq_sched_try_merge()`, `blk_mq_sched_try_insert_merge()`, request insertion flags, `struct request`, `struct bio`, `struct request_queue`, `struct elevator_queue`, `struct blk_mq_hw_ctx`, queue-depth limiting through `blk_mq_alloc_data`, and request accounting flags such as `RQF_STARTED`.

It depends on generic elevator helpers for sorted request management and merge hashing: `elv_rb_add()`, `elv_rb_del()`, `elv_rb_find()`, `elv_rqhash_add()`, `elv_rqhash_del()`, and `elv_bio_merge_ok()`. It also uses block tracing (`trace_block_rq_insert`), blk-stat accounting, and writeback throttling integration (`wbt_disable_default()`, `wbt_enable_default()`, `QUEUE_FLAG_DISABLE_WBT_DEF`).

Hierarchical scheduling and cgroup integration are compiled through `CONFIG_BFQ_GROUP_IOSCHED` and `CONFIG_BFQ_CGROUP_DEBUG`. The chunk calls into functions provided by other BFQ components, including `bfq_bic_update_cgroup()`, `bfq_bio_bfqg()`, `bfq_create_group_hierarchy()`, `bfqg_and_blkg_put()`, `bfqg_stats_update_*()`, `bfq_init_entity()`, `bfq_get_next_queue()`, `bfq_add_bfqq_busy()`, `bfq_del_bfqq_busy()`, `bfq_deactivate_bfqq()`, `bfq_requeue_bfqq()`, `__bfq_bfqd_reset_in_service()`, `bfq_bfqq_served()`, `bfq_bfqq_charge_time()`, `__bfq_entity_update_weight_prio()`, and group movement helpers.

The code uses Linux kernel infrastructure for timers (`hrtimer`), jiffies/time conversion, rb-trees, hlist/list primitives, slab caches, spinlocks, atomic active references, cgroups, I/O priority helpers, disk independent access ranges, and request queue topology checks such as `blk_queue_rot()`.

The scheduler also integrates with user-visible policy indirectly through ioprio (`ioprio_get` state in `io_context`), cgroup weights, sysfs tunables defined later in the file, blkcg policy activation/deactivation, and queue flags that alter default block-layer behavior.

## Risks And Edge Cases

Reference accounting is a major risk. Queue references come from process ownership, in-flight requests, weight-counter membership, service-tree state, stable merge scheduling, async group ownership, and merge chains. Bugs in `bfq_setup_merge()`, `bfq_merge_bfqqs()`, split handling, request requeue, or ICQ exit can cause use-after-free, leaks, or stale `bic->bfqq` pointers. The code mitigates this with process-reference checks, stable-ref counters, careful `bic_set_bfqq()` cancellation, and WARNs on non-empty queue structures at free time.

Queue merging can improve throughput but can harm fairness or state attribution. The implementation avoids late merges, idle-class merges, mismatched priority/group/actuator merges, seeky queue merges, async merges, OOM queue merging, and nonrotational queueing-device merges. Stable merge state must be cancelled correctly when a non-stable merge redirects to the same target. Shared queues deliberately lose a stable per-process pid and are excluded from some waker logic to avoid false throughput stealing.

Idling and injection trade throughput against guarantees. Incorrect `bfq_better_to_idle()` decisions can either underutilize fast devices or violate per-queue bandwidth/latency. `strict_guarantees` provides stronger ordering only by forcing one request in the device, which may sharply reduce throughput. Injection limit updates depend on total service-time sampling; stale baselines, oscillation, or workload changes can delay convergence.

Low-latency heuristics rely on timing and workload classification. Interactive and soft real-time detection can false-positive on random or CPU/storage-throttled greedy workloads; burst detection can false-positive during application startup; soft real-time windows depend on jiffies granularity and peak-rate estimates; weight raising must be disabled or switched back at the right times. The code includes caps such as `max_service_from_wr`, seeky filters, large-burst suppression, and soft real-time next-start lower bounds to limit these risks.

Concurrency is lock-sensitive. Most scheduler state is protected by `bfqd->lock`, but `bfq_has_work()` intentionally reads `bfqd->queued` locklessly with `READ_ONCE`, accepting harmless extra dispatch attempts. `bfq_bio_merge()` and insertion/dispatch/completion paths take the scheduler lock around state mutations. `bfq_update_dispatch_stats()` and insert stats use `queue_lock` after releasing `bfqd->lock`, relying on request and queue lifetime guarantees. Timer callbacks race with request arrival and dispatch; they recheck `in_service_queue` before expiring.

Multi-actuator support introduces mapping and fairness risks. `bfq_actuator_index()` warns and falls back to actuator 0 if a bio sector is outside configured ranges. Stable merging refuses queues from different actuators to preserve control. Underused-actuator injection can bypass the nominal in-service queue, so it must preserve budget checks and in-driver accounting per actuator.

OOM behavior is intentionally degraded. If a `bfq_queue` allocation fails, requests fall back to `bfqd->oom_bfqq`, which is excluded from merging and has permanent references. This preserves functionality but weakens per-process isolation under memory pressure.

## Test Signals

Scheduler initialization tests should verify that selecting BFQ initializes `bfq_data`, root group, OOM queue, idle timer, async depths, actuator ranges, queue flags, disabled default WBT, blk-stat accounting, and slab allocation; teardown should leave no in-driver requests, cancel timers, release root/async queues, reactivate WBT defaults, and free state.

Request lifecycle tests should cover prepare, insert, merge, dispatch, completion, requeue, and finish paths. Useful assertions include balanced `bfqq->ref`, `bic->requests`, `entity->allocated`, `bfqd->queued`, `bfqq->queued[]`, `bfqq->dispatched`, `tot_rq_in_driver`, `rq_in_driver[]`, FIFO/rb-tree/hash membership, and clearing of `rq->elv.priv[]` after finish/requeue.

Queue selection tests should exercise budget exhaustion, budget timeout, no-more-requests expiration, too-idle timer expiration, CLASS_IDLE preemption, strict-guarantees one-request dispatch, lockless `has_work` false positives, and the case where an empty in-service queue is retained for idling.

Low-latency tests should cover interactive weight raising after long idle, async weight raising after short inter-arrival, large-burst suppression, soft real-time detection and delayed update, `max_service_from_wr` ending, switch-back from soft real-time to interactive weight raising, `wr_busy_queues` balance, and disabling low-latency behavior.

Merging/splitting tests should cover close-cooperator merge, stable early merge on nonrotational queueing devices, delayed stable merge cancellation or execution on rotational/non-queueing devices, merge-chain loop prevention, cgroup/priority/actuator mismatch refusal, seeky split of cooperative queues, saved-state restoration after split, waker preservation across split, and stable-reference cleanup on ICQ exit.

Idling and injection tests should exercise rotational without queueing, nonrotational with hardware queueing, short versus long think time, waker detection after repeated completions, async same-process injection, waker/woken injection, underused actuator injection, adaptive inject-limit increase/decrease, periodic injection reset, and service guarantee preservation when active weights or classes differ.

Cgroup tests should run with and without `CONFIG_BFQ_GROUP_IOSCHED` and `CONFIG_BFQ_CGROUP_DEBUG`. They should verify depth limiting from per-entity allocated counts, group pending request accounting, stats updates for insert/remove/merge/idle/completion, request migration on cgroup changes, root reparenting of async queues during group destruction, and fallback behavior when cgroup support is absent.

Device calibration tests should validate peak-rate updates over sequential and seeky workloads, reset behavior after long idle or slow completion, dynamic max-budget computation, hardware-tag detection thresholds, `nonrot_with_queueing` transitions, and multi-actuator sector-range mapping including out-of-range warning fallback.

### subset-b-000922: lines 7380-7682

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
