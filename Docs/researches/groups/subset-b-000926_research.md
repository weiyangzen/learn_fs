# Research: subset-b-000926 block multiqueue, PM, QoS, limits, stats, and sysfs

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq.c -->
# sources/distributed-fs/ceph-client/block/blk-mq.c

## Purpose

`blk-mq.c` is the core Linux block multiqueue implementation. It turns bios and prepared passthrough requests into `struct request` objects, maps software CPU queues to hardware dispatch queues, manages request/tag allocation, dispatch, completion, requeue, timeout handling, CPU hotplug migration, queue freeze/quiesce, queue/tag-set lifetime, queue resizing, and polling. In this source tree it is used as the central request path that Ceph/RBD-style block clients and other request-based drivers depend on through the generic blk-mq APIs rather than directly on transport details.

## Important APIs, Types, And Functions

The file exports queue coordination APIs such as `blk_freeze_queue_start()`, `blk_mq_freeze_queue_wait()`, `blk_mq_freeze_queue_nomemsave()`, `blk_mq_unfreeze_queue_nomemrestore()`, `blk_mq_quiesce_queue()`, `blk_mq_unquiesce_queue()`, `blk_mq_quiesce_tagset()`, and `blk_mq_unquiesce_tagset()`. Request allocation and execution are exposed through `blk_mq_alloc_request()`, `blk_mq_alloc_request_hctx()`, `blk_execute_rq_nowait()`, `blk_execute_rq()`, `blk_insert_cloned_request()`, and clone helpers under `CONFIG_BLK_MQ_STACKING`. Submission enters through `blk_mq_submit_bio()`.

Request lifecycle functions include `blk_rq_init()`, `blk_mq_start_request()`, `blk_update_request()`, `blk_mq_end_request()`, `__blk_mq_end_request()`, `blk_mq_end_request_batch()`, `blk_mq_complete_request_remote()`, `blk_mq_complete_request()`, `blk_mq_free_request()`, and `blk_mq_put_rq_ref()`. Dispatch is centered on `blk_mq_dispatch_rq_list()`, `blk_mq_run_hw_queue()`, `blk_mq_run_hw_queues()`, `blk_mq_delay_run_hw_queue()`, `blk_mq_flush_plug_list()`, `blk_mq_try_issue_directly()`, and the scheduler-facing insert helpers.

Queue/tag-set lifetime APIs include `blk_mq_alloc_queue()`, `blk_mq_init_allocated_queue()`, `blk_mq_destroy_queue()`, `blk_mq_exit_queue()`, `blk_mq_release()`, `blk_mq_alloc_tag_set()`, `blk_mq_alloc_sq_tag_set()`, `blk_mq_free_tag_set()`, `blk_mq_update_nr_requests()`, and `blk_mq_update_nr_hw_queues()`. Polling is provided by `blk_mq_poll()` and `blk_rq_poll()`.

## Control Flow

Normal bio submission starts in `blk_mq_submit_bio()`: it tries to reuse a plug-cached request, enters the queue if needed, validates logical-block alignment and poll support, splits the bio to queue limits, prepares integrity metadata, records issue timing, attempts plug/scheduler merge, optionally zone-write-plugs the bio, allocates or reuses a request, tracks QoS, converts the bio to request fields, obtains an inline-crypto keyslot, handles flush sequencing, and then either adds the request to the current plug, inserts it into scheduler/software queues, or issues it directly to the driver.

Dispatch drains plug lists by grouping requests by queue, hctx, ctx, and passthrough status. Without a scheduler and with a driver `queue_rqs()` hook, a same-queue list may be submitted in batch. Otherwise requests are inserted into scheduler queues, per-CPU software queues, or hctx dispatch lists. `blk_mq_run_hw_queue()` checks stopped/quiesced state, dispatch work, CPU affinity, and blocking transport constraints before calling scheduler dispatch under RCU/SRCU. `blk_mq_dispatch_rq_list()` prepares budgets and driver tags, calls `queue_rq()`, handles `BLK_STS_RESOURCE` and `BLK_STS_DEV_RESOURCE` by requeueing to `hctx->dispatch`, commits partial batches, and schedules reruns or delayed reruns to avoid stalls.

Completion begins when a driver calls `blk_mq_complete_request()` or a polled path completes through `poll()`. Completion may be redirected by IPI/softirq to honor `rq_affinity`. `blk_update_request()` completes full or partial bio ranges, updates integrity and crypto keyslot state, accounts bytes, advances bio iterators, handles zone append constraints, and recalculates segments for partial requests. `__blk_mq_end_request()` records stats, finishes scheduler state, invokes `end_io` if present, and frees the request. Batched completion reduces tag and queue-reference churn by collecting same-hctx tags before returning them.

Freeze and quiesce are distinct. Freeze kills the queue usage percpu ref and waits for users to drain, blocking new entries. Quiesce increments `quiesce_depth`, sets `QUEUE_FLAG_QUIESCED`, waits for RCU/SRCU dispatch sections to finish, and prevents new driver dispatch while allowing completions. Runtime PM, sysfs reconfiguration, scheduler switching, and hardware queue resizing all rely on these boundaries.

## State And Persistence Behavior

The main persistent state is in memory: `request_queue`, per-CPU `blk_mq_ctx`, per-hardware-queue `blk_mq_hw_ctx`, tag bitmaps, request pools, dispatch lists, plug lists, timeout/requeue work items, and tag-set maps. There is no disk persistence. State is synchronized through percpu refs, spinlocks, mutexes, RCU/SRCU, CPU-hotplug callbacks, sbitmap queues, wait queues, delayed work, timers, and request reference counts. Request state transitions use `MQ_RQ_IDLE`, `MQ_RQ_IN_FLIGHT`, and `MQ_RQ_COMPLETE`; tags use `BLK_MQ_NO_TAG` and reserved-vs-normal tag ranges.

Queue resizing and tag-set updates temporarily switch schedulers away, freeze all queues on the tag set, allocate/replace hctx and tag maps, remap software queues, restore schedulers, then re-register sysfs/debugfs hctx objects. Request pools are allocated in pages sized for `struct request` plus driver-private command payload and released after SRCU-safe cleanup.

## Dependencies And Integration Points

This file integrates with schedulers (`blk-mq-sched.h`, elevator ops), tags (`blk_mq_get_tag()`, `blk_mq_put_tag()`), flush machinery, integrity (`blk-integrity`), inline crypto, zones, writeback throttling/QoS (`rq_qos_*`), cgroups, partition stats, debugfs/sysfs helpers, CPU hotplug, softirq, kblockd, and driver-provided `blk_mq_ops` (`queue_rq`, `queue_rqs`, `commit_rqs`, `poll`, `timeout`, `init_hctx`, `exit_hctx`, `init_request`, `exit_request`, budget callbacks, and queue mapping). Driver behavior is constrained by return values from `queue_rq()` and by correct calls to `blk_mq_start_request()` and request completion.

## Risks And Edge Cases

The highest-risk areas are concurrency boundaries: missing queue freeze/quiesce can race with limits, scheduler, or hctx-map changes; incorrect tag accounting can leak queue references or starve shared-tag users; and wrong memory ordering around stopped queues or dispatch wait queues can lose wakeups. CPU hotplug must migrate pending software-queue requests and mark hctxs inactive only when no online CPU maps to them. Timeout handling deliberately avoids `blk_queue_enter()` to prevent freeze-time deadlocks. Partial completions must not corrupt zone append ordering or crypto keyslot lifetime. Plug recursion and request-cache use are subtle because sleeping QoS throttles can flush plugs and invalidate assumptions. Queue resizing must restore schedulers and sysfs/debugfs registration even on fallback paths.

## Test Signals

Useful signals include blktests coverage for blk-mq queueing, timeout, scheduler switching, hotplug, polling, flush, zone append, and queue-depth changes; lockdep and KCSAN for freeze/quiesce and hotplug races; fault injection through `should_fail_request()`; tracepoints (`block_rq_issue`, `block_rq_complete`, `block_unplug`, `block_rq_requeue`, `block_rq_error`); sysfs-driven `nr_requests` and `io_timeout` changes under I/O; runtime PM suspend/resume with in-flight requests; and stress tests with shared tag sets, cgroup/QoS throttling, polled I/O, and stacked request cloning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq.h -->
# sources/distributed-fs/ceph-client/block/blk-mq.h

## Purpose

`blk-mq.h` is the internal header for the block multiqueue core. It defines software queue state, allocation parameters, tag helpers, queue mapping helpers, dispatch lock wrappers, and internal prototypes shared between `blk-mq.c`, scheduler code, sysfs, debugfs, and tag-management files.

## Important APIs, Types, And Functions

`struct blk_mq_ctxs` owns the per-CPU software queue allocation and kobject. `struct blk_mq_ctx` is the CPU-facing queue with a lock, per-hctx-type request lists, CPU id, mapping indices, hctx pointers, parent queue, and kobject. `struct blk_mq_alloc_data` carries queue, flags, operation flags, shallow depth, cached request batch data, and selected ctx/hctx across request allocation.

The header declares submission, polling, queue exit, request-depth update, wakeup, dispatch, busy-ctx flushing, ctx dequeue, request reference release, request-map allocation/free, sysfs registration, plug flushing, work cancellation, and queue release helpers. Inline mapping helpers include `blk_mq_get_hctx_type()`, `blk_mq_map_queue_type()`, and `blk_mq_map_queue()`. Tag helpers include `blk_mq_tags_from_data()`, `blk_mq_tag_is_reserved()`, `blk_mq_is_shared_tags()`, `blk_mq_get_driver_tag()`, and `blk_mq_put_driver_tag()`.

## Control Flow

Operation flags drive hctx selection: polled I/O uses `HCTX_TYPE_POLL`, reads may use `HCTX_TYPE_READ`, and all else defaults to `HCTX_TYPE_DEFAULT`. Allocation paths fill `blk_mq_alloc_data`, map the current CPU ctx to an hctx, choose scheduler tags or driver tags, and use `blk_mq_tags_from_data()` for the active tag pool. Dispatch paths use `blk_mq_hctx_stopped()` and `blk_mq_hw_queue_mapped()` to decide whether work can run. Driver-budget helpers dispatch into optional `blk_mq_ops` callbacks while returning benign defaults when a driver has no budget implementation.

Shared-tag fairness is handled by active-request counters and `hctx_may_queue()`: if tags are shared and active queues/users are known, the helper derives a per-user depth floor and prevents one hctx or queue from consuming too many tags. The `__blk_mq_run_dispatch_ops()` macro wraps dispatch work in SRCU for blocking tag sets and RCU for nonblocking sets.

## State And Persistence Behavior

All state is transient kernel memory. The header establishes cacheline-aligned ctx structures, active request counters, pending software queue bits, stopped state checks with memory barriers, and dispatch budget tokens carried on requests. The stopped-queue helper contains a memory barrier paired with `blk_mq_start_stopped_hw_queue()` to avoid lost dispatch visibility.

## Dependencies And Integration Points

It depends on public blk-mq definitions from `<linux/blk-mq.h>` and local `blk-stat.h`, plus types from request queues, gendisks, hctxs, tags, schedulers, and debugfs. It is an internal integration layer: external drivers see public blk-mq APIs, while core block files include this header to share non-public helpers.

## Risks And Edge Cases

The key risk is misuse of inline helpers outside their invariants. `blk_mq_get_ctx()` assumes per-CPU ctx lifetime is persistent and does not require preemption stability. `blk_mq_put_driver_tag()` only releases a driver tag when both driver and scheduler tag state indicate one is held. `hctx_may_queue()` can affect fairness and forward progress for shared tags; incorrect flags would over-throttle or starve queues. The dispatch macro must match blocking-vs-nonblocking tag-set behavior, because drivers with blocking `queue_rq()` need SRCU sleepability.

## Test Signals

Compile coverage with different `CONFIG_BLK_MQ`, scheduler, polling, and debugfs options is important because many users are inline. Runtime signals include no lost dispatch when stopping/starting queues, fair tag allocation under shared tag sets, correct poll hctx mapping, and successful sysfs/debugfs hctx registration paths using the declared helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-pm.c -->
# sources/distributed-fs/ceph-client/block/blk-pm.c

## Purpose

`blk-pm.c` implements request-based runtime power-management support for block queues. It lets drivers bind a queue to a `struct device`, coordinate runtime suspend with queue usage references, and restore queue access on resume. It is only useful for request-based drivers, not bio-only drivers.

## Important APIs, Types, And Functions

`blk_pm_runtime_init()` stores `q->dev`, marks the queue runtime-PM state active, sets autosuspend delay to `-1`, and enables autosuspend semantics. `blk_pre_runtime_suspend()` transitions the queue to suspending, sets PM-only mode, freezes the queue usage counter, switches it to atomic mode, and allows suspend only if the usage counter reaches zero. `blk_post_runtime_suspend()` finalizes `RPM_SUSPENDED` on success or restores active state and clears PM-only mode on failure. `blk_pre_runtime_resume()` marks `RPM_RESUMING`. `blk_post_runtime_resume()` marks active, updates last busy time, requests autosuspend, and clears PM-only mode if the old state was not active.

## Control Flow

A driver initializes runtime PM after queue allocation but before normal I/O can race with runtime PM. During runtime suspend, the driver calls `blk_pre_runtime_suspend()` near the start of its suspend callback. That function blocks new non-PM queue entrants by setting PM-only, then freezes queue entry and synchronously switches `q_usage_counter` to atomic mode so new entrants observe the PM-only state. If the counter is zero, suspend can proceed; otherwise it restores active state, marks the device busy, clears PM-only, and returns `-EBUSY`. After the device-level suspend callback, the driver calls `blk_post_runtime_suspend()` with the callback result. Runtime resume uses the pre/post pair to mark the transient state and then reopen normal queue entry.

## State And Persistence Behavior

The file updates in-memory queue fields: `q->dev`, `q->rpm_status`, PM-only queue state, and the queue usage percpu ref mode. It also updates runtime-PM state in the device core through `pm_runtime_*()` calls. There is no durable persistence. Locking is through `q->queue_lock`, freeze/unfreeze functions, and percpu ref synchronization.

## Dependencies And Integration Points

It includes `<linux/pm_runtime.h>`, `<linux/blk-pm.h>`, block queue definitions, and `blk-mq.h`. It integrates with `blk_queue_enter()` PM behavior, queue freeze/unfreeze, runtime-PM autosuspend, and the driver runtime suspend/resume callbacks. `blk-pm.h` provides inline fast-path helpers used by request allocation/free paths.

## Risks And Edge Cases

The suspend path is sensitive to ordering. PM-only must be set before checking for in-flight non-PM users, and the q_usage_counter must switch to atomic mode so later entrants observe the state. A failed suspend must clear PM-only or normal I/O can remain blocked. `q->dev == NULL` is treated as no-op support. Drivers must call the post hooks consistently; otherwise `rpm_status` and PM-only state can remain stale. Runtime resume always clears PM-only for non-active old states even if hardware resume failed, because error handling still needs device communication.

## Test Signals

Relevant tests include runtime suspend while I/O is idle, suspend rejection with active I/O, PM requests allowed while PM-only is set, resume after successful and failed suspend, lockdep for queue_lock/freeze ordering, and driver tests that ensure no I/O is admitted after `blk_pre_runtime_suspend()` succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-pm.h -->
# sources/distributed-fs/ceph-client/block/blk-pm.h

## Purpose

`blk-pm.h` provides small inline helpers for the block runtime-PM fast path. It keeps PM checks cheap in blk-mq paths while compiling to no-ops when `CONFIG_PM` is disabled.

## Important APIs, Types, And Functions

With `CONFIG_PM`, `blk_pm_resume_queue(pm, q)` decides whether queue entry may proceed or should request runtime resume. If the queue has no runtime-PM device or is not PM-only, it returns `1`. If the caller is a PM request and the queue is not suspended, it returns `1`. Otherwise it calls `pm_request_resume(q->dev)` and returns `0` to indicate that the current queue-enter attempt should not proceed. `blk_pm_mark_last_busy(rq)` marks the device busy after non-PM request completion. Without `CONFIG_PM`, both helpers compile to simple allow/no-op implementations.

## Control Flow

Queue entry code can call `blk_pm_resume_queue()` after detecting PM-only state. A non-PM request against a suspended queue triggers an async resume request rather than entering the queue. A PM-marked request is allowed when the queue is already resuming or active, which avoids blocking the PM machinery itself. Request free/completion paths call `blk_pm_mark_last_busy()` so autosuspend timing is based on normal I/O activity.

## State And Persistence Behavior

The helper reads `q->dev`, queue PM-only state, request `RQF_PM`, and `q->rpm_status`; it updates runtime-PM last-busy state through the device core. No persistent state is stored in this header.

## Dependencies And Integration Points

It depends on `<linux/pm_runtime.h>` and block queue/request fields defined elsewhere. It is coupled to `blk-pm.c` state transitions and blk-mq request free paths.

## Risks And Edge Cases

The return convention is easy to misuse: `1` means request allowed or nothing to do, while `0` means resume was requested and queue entry should be retried later. Marking last busy must skip `RQF_PM` requests; otherwise PM-internal traffic can keep devices awake indefinitely. Non-PM builds must retain identical call-site behavior through no-op helpers.

## Test Signals

Compile with and without `CONFIG_PM`, runtime-PM suspend/resume queue-entry tests, and autosuspend timing after normal I/O completions are the primary checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-rq-qos.c -->
# sources/distributed-fs/ceph-client/block/blk-rq-qos.c

## Purpose

`blk-rq-qos.c` implements the generic request-queue QoS framework used by writeback throttling, latency control, and cost models. It provides a linked chain of QoS policies, dispatches lifecycle callbacks to each policy, manages wait queues for throttling, scales queue depth, and safely adds/removes policies under queue freeze.

## Important APIs, Types, And Functions

Callback fanout functions include `__rq_qos_cleanup()`, `__rq_qos_done()`, `__rq_qos_issue()`, `__rq_qos_requeue()`, `__rq_qos_throttle()`, `__rq_qos_track()`, `__rq_qos_merge()`, `__rq_qos_done_bio()`, and `__rq_qos_queue_depth_changed()`. `rq_wait_inc_below()` atomically reserves an inflight slot below a limit. `rq_qos_wait()` is the common throttling wait primitive. Queue-depth scaling is handled by `rq_depth_calc_max_depth()`, `rq_depth_scale_up()`, and `rq_depth_scale_down()`. Policy lifetime is managed by `rq_qos_add()`, `rq_qos_del()`, and `rq_qos_exit()`.

## Control Flow

The block hot path uses inline wrappers from `blk-rq-qos.h`, which call these fanout functions only if QoS is enabled and the queue has a policy chain. Each fanout walks `rqos->next` and calls the corresponding operation when present. Throttling policies call `rq_qos_wait()`: it first tries to acquire an inflight token without sleeping if no waiters are present, otherwise installs an exclusive wait entry with a custom wake function that atomically claims a token before waking the task. The first waiter rechecks acquisition to guarantee progress when no inflight process exists.

Adding a policy requires `q->rq_qos_mutex` and freezes the blk-mq queue so no I/O is in flight while inserting at the head of the chain and setting `QUEUE_FLAG_QOS_ENABLED`. Duplicate IDs return `-EBUSY`. Deletion similarly freezes, unlinks the policy, clears the queue flag if the chain is empty, and unfreezes. `rq_qos_exit()` drains all policies under the mutex and invokes each policy's `exit()`.

## State And Persistence Behavior

QoS state is in memory on `request_queue::rq_qos`, `struct rq_qos`, `struct rq_wait`, and `struct rq_depth`. Wait state uses an atomic inflight counter plus wait queue. Queue depth scaling maintains `scale_step`, `scaled_max`, current queue depth, default depth, and derived max depth. No state is persisted across queue destruction.

## Dependencies And Integration Points

It depends on blk-mq queue freeze/unfreeze, request/bio lifecycle hooks, wait queues, atomics, and the policy implementations referenced by `enum rq_qos_id` (`RQ_QOS_WBT`, `RQ_QOS_LATENCY`, `RQ_QOS_COST`). It integrates with `blk_mq_submit_bio()`, request issue/completion/requeue paths, sysfs WBT settings, and queue-depth changes from `blk-settings.c`.

## Risks And Edge Cases

`rq_qos_wait()` has subtle wakeup ownership rules: the wake function claims the token, removes the wait entry, and relies on memory-ordering semantics of `finish_wait()` and `list_del_init_careful()` to avoid use-after-free or double-token ownership. Cleanup callbacks must undo an extra local token if a race grants two. Queue freeze during add/delete is required because policy lists are traversed in hot paths. Depth scaling must avoid underflow/overflow of `scale_step` and handle queue-depth-one devices specially.

## Test Signals

Signals include WBT/latency throttling tests under concurrent bios, wakeup fairness with many waiters, add/delete policy operations under I/O, queue-depth change notifications, lockdep for `rq_qos_mutex` plus freeze, and stress tests that verify no inflight counter leaks after interrupted races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-rq-qos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-rq-qos.h -->
# sources/distributed-fs/ceph-client/block/blk-rq-qos.h

## Purpose

`blk-rq-qos.h` declares the block request QoS framework data structures, operation table, identifiers, and fast-path wrappers. It lets policy modules plug into bio/request throttle, track, merge, issue, requeue, completion, cleanup, queue-depth-change, exit, and debugfs behavior.

## Important APIs, Types, And Functions

`enum rq_qos_id` identifies WBT, latency, and cost policies. `struct rq_wait` contains the wait queue and inflight counter used by throttlers. `struct rq_qos` is a linked-list node with ops, owning disk, id, next pointer, and optional debugfs directory. `struct rq_qos_ops` is the callback contract. `struct rq_depth` tracks adaptive depth state. Lookup helpers include `rq_qos_id()`, `wbt_rq_qos()`, and `iolat_rq_qos()`. Fast-path wrappers include `rq_qos_throttle()`, `rq_qos_track()`, `rq_qos_merge()`, `rq_qos_issue()`, `rq_qos_requeue()`, `rq_qos_done()`, `rq_qos_done_bio()`, `rq_qos_cleanup()`, and `rq_qos_queue_depth_changed()`.

## Control Flow

Callers check queue flags through the inline wrappers rather than walking policies directly. `rq_qos_throttle()` marks `BIO_QOS_THROTTLED` before invoking policy throttles, and `rq_qos_merge()` marks `BIO_QOS_MERGED`; `rq_qos_done_bio()` uses those flags to decide whether bio completion may need policy cleanup. It then revalidates that the current queue still has QoS enabled because bios can traverse stacked devices where lower and upper queues differ. Request completion skips passthrough requests for normal QoS done callbacks.

## State And Persistence Behavior

This header defines the in-memory policy chain and per-policy state hooks but does not persist anything. Bio flags are transient markers that link throttle/merge decisions to completion cleanup. Queue flag `QUEUE_FLAG_QOS_ENABLED` is the coarse fast-path gate.

## Dependencies And Integration Points

It includes kernel, block, atomic, wait queue, blk-mq, and debugfs interfaces. It is consumed by blk-mq submission/completion, WBT, latency/cost policies, sysfs, and queue-depth update code.

## Risks And Edge Cases

The main risk is stale bio flags across stacked devices; the header explicitly guards against calling into absent QoS chains on completion. Policy ordering is linked-list order, with new policies inserted by the implementation. Missing fast-path flag updates would either bypass QoS or call into an empty chain. Passthrough request filtering avoids applying filesystem I/O QoS semantics to admin commands.

## Test Signals

Compile coverage with and without debugfs/QoS policies, stacked-device tests where only one layer enables QoS, WBT sysfs changes, passthrough completions, and bio merge/throttle cleanup tests are the best indicators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-rq-qos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-settings.c -->
# sources/distributed-fs/ceph-client/block/blk-settings.c

## Purpose

`blk-settings.c` validates, defaults, commits, and stacks block queue limits. It defines the rules that turn driver-provided limits into coherent `queue_limits`, applies them to request queues and backing-dev readahead, handles atomic write constraints, zoned-device constraints, integrity metadata constraints, discard/write-zeroes caps, and reports alignment for block devices and partitions.

## Important APIs, Types, And Functions

Public APIs include `blk_queue_rq_timeout()`, `blk_set_stacking_limits()`, `blk_validate_limits()`, `blk_set_default_limits()`, `queue_limits_commit_update()`, `queue_limits_commit_update_frozen()`, `queue_limits_set()`, `blk_stack_limits()`, `queue_limits_stack_bdev()`, `queue_limits_stack_integrity()`, `blk_set_queue_depth()`, `bdev_alignment_offset()`, and `bdev_discard_alignment()`. Internal validators cover zoned limits, integrity limits, atomic write boundaries, atomic write update calculations, discard alignment, logical/physical block alignment, and stacked-device atomic-write compatibility.

## Control Flow

Drivers initialize or update a `queue_limits` structure, then call `queue_limits_set()` or the start/commit update API. `blk_validate_limits()` fills defaults, rejects impossible configurations, rounds sizes to logical block sectors, derives `max_sectors` from hardware, device, user, and optimal I/O caps, validates segment and DMA constraints, normalizes discard values, clears unsupported FUA without write cache, derives atomic-write limits, validates integrity metadata, and finally validates zoned settings. `queue_limits_commit_update()` requires `q->limits_lock`, validates the candidate, rejects unsupported integrity plus inline encryption, copies it into `q->limits`, updates BDI readahead, and unlocks. The frozen variant wraps the commit in blk-mq freeze/unfreeze.

Stacking drivers call `blk_set_stacking_limits()` to set permissive initial values, then repeatedly call `blk_stack_limits()` or `queue_limits_stack_bdev()` for component devices. Stacking intersects inherited features and sizes, reconciles alignment offsets with LCM/GCD calculations, propagates misalignment flags, combines discard and zone limits, and narrows atomic-write support to configurations aligned across all components.

## State And Persistence Behavior

The file mutates in-memory `queue_limits`, `request_queue::rq_timeout`, `request_queue::queue_depth`, and BDI `ra_pages/io_pages`. Queue-limit updates are serialized by `limits_lock`; frozen commits additionally block I/O while limits change. No persistent storage is written.

## Dependencies And Integration Points

It depends on block core types, backing-dev info, DMA/page constants, integrity/T10 PI/CRC64 metadata, zoned block support, atomic write helpers, and rq-qos queue-depth notification. Sysfs store callbacks in `blk-sysfs.c` use the update/commit APIs. Stacking drivers such as device mapper and MD depend on the stacking functions to produce safe upper-device limits.

## Risks And Edge Cases

Invalid limits can cause data corruption or bio splitting failures, so validation is defensive. Risks include integer shifts between sectors and bytes, non-power-of-two block sizes, atomic-write boundaries incompatible with chunk sizes, integrity interval mismatches, zoned limits without zoned support, discard granularity zeroing when discard is unsupported, and alignment offsets for partitions. Frozen commits are necessary when live I/O could observe changed limits mid-submission. BDI readahead is only increased, not decreased, to preserve user tuning.

## Test Signals

Useful tests include sysfs writes to max sectors/discard/write-cache/iostats, driver initialization with incomplete limits, stacked DM/MD devices with mismatched block sizes and discard granularity, integrity metadata profiles, zoned devices with zone append caps, atomic write positive/negative configurations, inline encryption plus integrity rejection, and lockdep around `limits_lock` and queue freeze.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-settings.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-stat.c -->
# sources/distributed-fs/ceph-client/block/blk-stat.c

## Purpose

`blk-stat.c` implements block request latency statistics callbacks. It lets consumers register bucketed callbacks that collect per-CPU request completion latency samples during a timer window, then aggregate them and invoke a policy callback. It also provides generic queue-level accounting enable/disable independent of callbacks.

## Important APIs, Types, And Functions

`struct blk_queue_stats` owns the callback list, lock, and accounting reference count. Request-stat helpers are `blk_rq_stat_init()`, `blk_rq_stat_add()`, and `blk_rq_stat_sum()`. `blk_stat_add()` records a completed request into active callbacks. `blk_stat_alloc_callback()`, `blk_stat_add_callback()`, `blk_stat_remove_callback()`, and `blk_stat_free_callback()` manage callback lifetime. `blk_stat_enable_accounting()` and `blk_stat_disable_accounting()` toggle the `QUEUE_FLAG_STATS` fast-path gate for users that only need request time/size accounting. `blk_alloc_queue_stats()` and `blk_free_queue_stats()` manage queue stats allocation.

## Control Flow

A consumer allocates a callback with a timer function, bucket function, bucket count, and private data, then adds it to a queue. Adding initializes all per-CPU buckets, links the callback via RCU, and sets `QUEUE_FLAG_STATS`. During request completion, blk-mq calls `blk_stat_add()` when the request has stats enabled; it computes latency from `rq->io_start_time_ns`, enters RCU, pins the current CPU, walks active callbacks, maps the request to a bucket, and accumulates the latency sample in the per-CPU bucket. When the callback timer fires, `blk_stat_timer_fn()` initializes aggregate buckets, sums all online CPU buckets into the aggregate, resets per-CPU buckets, and calls the consumer's timer function.

Removal unlinks the callback under the stats lock, clears `QUEUE_FLAG_STATS` if there are no callbacks and no accounting users, and synchronously deletes the timer. Freeing is RCU-delayed so readers that saw the callback list entry complete safely.

## State And Persistence Behavior

All stats are in memory. Samples are held in per-CPU `blk_rq_stat` arrays until the timer aggregates and resets them. Aggregate buckets store min, max, mean, sample count, and batch sum. The queue flag is reference-like: callbacks and explicit accounting users can keep it set. There is no durable persistence.

## Dependencies And Integration Points

It depends on RCU lists, per-CPU allocation, timers, blk-mq completion timestamps, and queue flags. Consumers include latency-control and writeback-throttling style policies that need rolling latency windows.

## Risks And Edge Cases

Mean aggregation deliberately ignores overflow by returning early if sample count wraps. Only online CPUs are summed at timer fire, so CPU hotplug behavior depends on per-CPU buffers being initialized across possible CPUs and active samples on offline CPUs not being expected for future windows. Callback removal must delete the timer before freeing. `blk_stat_add()` assumes `q->stats` exists and callbacks remain RCU-valid. Accounting enable/disable must remain balanced or stats overhead may stay enabled or be disabled too early.

## Test Signals

Tests should cover callback add/remove/free under I/O, timer aggregation across CPUs, bucket functions returning `-1`, concurrent accounting enable/disable, no callback leaks at queue teardown, and consumers seeing sane min/max/mean under synthetic latency distributions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-stat.h -->
# sources/distributed-fs/ceph-client/block/blk-stat.h

## Purpose

`blk-stat.h` declares the block latency statistics callback interface and inline activation helpers. It is the contract between blk-mq completion accounting and consumers that need bucketed latency windows.

## Important APIs, Types, And Functions

`struct blk_stat_callback` contains an RCU list node, timer, per-CPU bucket array, bucket function, bucket count, aggregate bucket array, timer callback, private data, and RCU head. Public functions allocate/free queue stats, add latency samples, enable/disable accounting, allocate/add/remove/free callbacks, and manipulate `struct blk_rq_stat`. Inline helpers are `blk_stat_is_active()`, `blk_stat_activate_nsecs()`, `blk_stat_activate_msecs()`, and `blk_stat_deactivate()`.

## Control Flow

Consumers allocate a callback, add it to a request queue, then activate it for a time window with nanosecond or millisecond helpers. While the timer is pending, completion accounting calls the bucket function for each eligible request and records latency in the current CPU's bucket. Timer expiry aggregates samples and invokes the consumer callback. Deactivation synchronously deletes the timer.

## State And Persistence Behavior

The header defines transient in-memory callback state only. Timer pending state is the active/inactive indicator. Per-CPU and aggregate arrays are owned by the implementation and freed after RCU grace.

## Dependencies And Integration Points

It includes block device definitions, ktime/jiffies conversion, RCU, and timers. It is included by `blk-mq.h`, `blk-stat.c`, and block policies that consume latency statistics.

## Risks And Edge Cases

Consumers must remove a callback before freeing it and must not add one callback to multiple queues. Timer activation uses jiffies conversion, so very small windows round according to kernel timer behavior. Bucket functions must validate request types and return `-1` for ignored requests to avoid corrupting unrelated buckets.

## Test Signals

Compile coverage, callback lifecycle tests, activation/deactivation timing, RCU-safe removal under concurrent completion, and bucket-count bounds checks in consumers are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-sysfs.c -->
# sources/distributed-fs/ceph-client/block/blk-sysfs.c

## Purpose

`blk-sysfs.c` exposes request queue attributes under each disk's `queue/` sysfs directory and coordinates queue registration/unregistration with sysfs, debugfs, scheduler, crypto, independent access ranges, and writeback throttling. It is the user-visible control and inspection surface for many `queue_limits` and blk-mq runtime knobs.

## Important APIs, Types, And Functions

`struct queue_sysfs_entry` describes an attribute and either direct show/store callbacks or limit-aware show/store callbacks. Attribute callbacks cover `nr_requests`, `async_depth`, `read_ahead_kb`, max sectors/segments/discard/write-zeroes/zone append/atomic write sizes, block sizes, zone state, nomerges, rq affinity, polling, I/O timeout, write cache, rotational, iostats, stable writes, add_random, DAX/FUA display, passthrough stats, and WBT latency when enabled. The main kobject hooks are `queue_attr_show()`, `queue_attr_store()`, `queue_attr_visible()`, `blk_mq_queue_attr_visible()`, `blk_queue_ktype`, `blk_register_queue()`, and `blk_unregister_queue()`.

## Control Flow

Show callbacks either read queue fields directly or, for limit attributes, run under `q->limits_lock`. Limit store callbacks use `queue_limits_start_update()`, mutate the candidate limits, then call `queue_limits_commit_update_frozen()` so validation and copying happen while the queue is frozen. Direct stores use their own synchronization: `nr_requests` uses the tag-set `update_nr_hwq_lock`, freezes the queue, and updates scheduler or hardware tags; `async_depth` freezes and locks the elevator; `zoned_qd1_writes` freezes and quiesces; `rq_affinity` updates atomic flags; `io_timeout` stores jiffies; WBT latency uses `disk->rqos_state_mutex`.

Queue registration creates `queue` kobject under the disk device, registers blk-mq sysfs hctxs, creates debugfs directories, registers blk-mq debugfs, sets default zoned QD1 writes for rotational zoned mq devices, registers independent access ranges and crypto sysfs, sets the default elevator, marks the queue registered, enables default WBT, sends uevents, and switches `q_usage_counter` to percpu mode after init. Unregistration clears the registered flag, removes mq sysfs hctxs and crypto sysfs before mutable queue data disappears, unregisters access ranges, sends remove uevent, deletes the kobject, removes the elevator, and tears down debugfs.

## State And Persistence Behavior

Sysfs writes mutate in-memory queue limits, queue flags, request depth, async scheduler depth, read-ahead pages, timeout, WBT latency, and debugfs/sysfs registration state. Changes persist only for the lifetime of the queue unless a driver/userspace reapplies them. Registration state is tracked by `QUEUE_FLAG_REGISTERED` and `QUEUE_FLAG_INIT_DONE`.

## Dependencies And Integration Points

The file integrates with queue limits from `blk-settings.c`, blk-mq sysfs/debugfs helpers, elevator switching, WBT/rq-qos, blk-cgroup throttling headers, blktrace shutdown, crypto sysfs, independent access ranges, kobjects, and uevents. It is the bridge between userspace controls and the lower block core.

## Risks And Edge Cases

Lock ordering is critical. `queue_requests_store()` uses `down_write_trylock()` to avoid kernfs active-reference deadlocks during disk deletion. Limit stores must cancel updates on parse failure and commit frozen to avoid live I/O seeing inconsistent limits. Visibility callbacks hide zoned-only and mq-only attributes when unsupported. `queue_poll_store()` accepts but ignores writes for supported queues and rejects unsupported polling. Registration error paths must unwind debugfs, hctx sysfs, independent access ranges, crypto sysfs, and kobjects in the right order. Unregister must remove sysfs before queue internals can be modified or destroyed.

## Test Signals

Signals include sysfs read/write tests for every mutable attribute, invalid input parsing, queue deletion racing with sysfs writes, mq vs bio queue visibility, zoned attribute visibility, WBT latency updates, debugfs cleanup, scheduler default setup/removal, uevent ordering, and lockdep while changing `nr_requests`, limits, and zoned QD1 writes under active I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-sysfs.c -->
