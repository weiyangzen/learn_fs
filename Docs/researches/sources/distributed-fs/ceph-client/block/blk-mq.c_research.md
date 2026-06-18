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
