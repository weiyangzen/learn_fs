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
