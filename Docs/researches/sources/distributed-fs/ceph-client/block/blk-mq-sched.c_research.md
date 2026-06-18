# sources/distributed-fs/ceph-client/block/blk-mq-sched.c

## Purpose
`blk-mq-sched.c` implements blk-mq scheduler dispatch, merge delegation, scheduler tag allocation, scheduler resource batching, debugfs registration, and scheduler lifecycle attach/detach. It bridges elevator callbacks with blk-mq hardware queues and software queues.

## Important APIs, Types, And Functions
Dispatch APIs include `blk_mq_sched_mark_restart_hctx()`, `__blk_mq_sched_restart()`, and `blk_mq_sched_dispatch_requests()`. Merge APIs are `blk_mq_sched_bio_merge()` and `blk_mq_sched_try_insert_merge()`. Lifecycle/resource APIs include `blk_mq_alloc_sched_tags()`, `blk_mq_alloc_sched_res()`, `blk_mq_alloc_sched_ctx_batch()`, `blk_mq_alloc_sched_res_batch()`, `blk_mq_init_sched()`, `blk_mq_sched_free_rqs()`, and `blk_mq_exit_sched()`.

## Control Flow
Dispatch first drains `hctx->dispatch` for fairness, marks restart when residual requests exist, and only pulls from the scheduler when the dispatch list is empty or made progress. With an elevator, `__blk_mq_do_dispatch_sched()` repeatedly obtains driver budget, asks the scheduler for a request, assigns the budget token, groups cross-hctx requests by hctx if needed, and stops when tags or dispatch capacity are exhausted. Without an elevator, `blk_mq_do_dispatch_ctx()` round-robins software contexts and updates `dispatch_from`. Bio merge first delegates to the scheduler `bio_merge` callback when present, otherwise checks the per-context request list. Scheduler init installs sched tags, calls queue and hctx elevator init callbacks, and unwinds tags on failure.

## State And Persistence
State is runtime queue state: hctx restart bits, `dispatch_from`, scheduler tags, `q->nr_requests`, `q->sched_shared_tags`, `hctx->sched_tags`, `sched_data`, and `q->elevator`. Batch resource changes use an xarray of `elv_change_ctx` entries under `update_nr_hwq_lock`.

## Dependencies And Integration Points
The file integrates with elevator operations, blk-mq dispatch/tag APIs, driver budget callbacks, debugfs registration, writeback throttling defaults, xarray batch updates, and request merge helpers from `blk-merge.c`.

## Risks And Test Signals
Risks include dispatch starvation when residual lists remain, budget leaks on scheduler no-dispatch, cross-hctx scheduler ordering, tag allocation unwind leaks, shared scheduler tag resizing, and elevator switch races. Tests should cover scheduler and no-scheduler queues, busy dispatch lists, SCSI-style budget failures, hctx count changes, shared tags, elevator init_hctx failure unwind, and debugfs register/unregister during scheduler switches.
