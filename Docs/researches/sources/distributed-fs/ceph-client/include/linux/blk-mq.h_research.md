# sources/distributed-fs/ceph-client/include/linux/blk-mq.h

## Purpose
`blk-mq.h` declares the multiqueue block request layer. It defines the request object, hardware queue contexts, tag sets, driver callbacks, queue mapping structures, request allocation/completion APIs, requeue/quiesce/freeze helpers, and request data iteration utilities.

## Important APIs, Types, And Functions
Key types include `struct request`, `struct rq_list`, `struct blk_mq_hw_ctx`, `struct blk_mq_queue_map`, `enum hctx_type`, `struct blk_mq_tag_set`, `struct blk_mq_queue_data`, `struct blk_mq_ops`, `struct blk_mq_tags`, `struct req_iterator`, and `struct rq_map_data`. Request flags include `RQF_STARTED`, `RQF_FLUSH_SEQ`, `RQF_MIXED_MERGE`, `RQF_DONTPREP`, scheduler/hash/stat/special-payload/zone-timeout/reserved flags, plus `RQF_NOMERGE_FLAGS`. Request states are `MQ_RQ_IDLE`, `MQ_RQ_IN_FLIGHT`, and `MQ_RQ_COMPLETE`.

Driver callbacks in `blk_mq_ops` include `queue_rq()`, `commit_rqs()`, `queue_rqs()`, budget get/put/token helpers, `timeout()`, `poll()`, `complete()`, hctx/request init and exit hooks, `cleanup_rq()`, `busy()`, `map_queues()`, and optional debugfs display.

Lifecycle APIs include disk/queue allocation (`blk_mq_alloc_disk()`, `blk_mq_alloc_queue()`), tag-set allocation/free, request allocation (`blk_mq_alloc_request()` and hctx-specific variant), request start/end/complete/requeue helpers, queue stop/start/run/delay functions, quiesce/unquiesce, freeze/unfreeze, queue mapping, hardware queue count update, tag iteration, and timeout injection. Data helpers expose request op, direction, ioprio, positions, byte/sector counts, payload bytes, bvec iteration, SG mapping, and clone/execute/map-user/map-kernel operations.

## Control Flow And State
A request flows from allocation from a tag set, through optional scheduler tags, into a hardware context, then to driver `queue_rq()`/`queue_rqs()`, then through completion. State fields track `cmd_flags`, `rq_flags`, tag/internal tag, bio chain, sector and length cursors, timings, physical segment counts, crypto keyslot, deadline, scheduler/private pointers, flush state, and `end_io`. `blk_mq_start_request()` moves a request into flight, completion helpers move it to complete and either batch, direct-complete, remote-complete, or end/free it.

Hardware context state includes dispatch lists, queue state bits, CPU masks, run work, scheduler data, tag sets, wait queues, sysfs/debugfs nodes, CPU hotplug list nodes, and active counts. Tag sets own shared or per-hctx tags, queue maps, locks, SRCU, and update locks. Freeze/quiesce helpers coordinate queue teardown, elevator switching, and resource updates.

## Dependencies And Integration Points
The header includes `linux/blkdev.h`, `linux/sbitmap.h`, lockdep, scatterlist, prefetch, SRCU, write-hint, and rwsem support. It is tightly coupled with `blk_types.h` operations, `blkdev.h` queue/disk state, bio iteration, DMA mapping, I/O schedulers, debugfs, cgroups, zone write plugging, polling, and driver-specific command PDUs placed after `struct request`.

## Risks And Test Signals
Risks include request state races, tag leaks, wrong queue mapping, failing to call budget put on errors, using request fields directly despite cursor comments, mishandling special payloads, batching completions with incompatible handlers, freeze/quiesce deadlocks, and stale queue limits during hctx updates. Tests should cover request allocation/free, queue_rq error returns, batched completion eligibility, timeouts, requeue paths, polling, CPU hotplug queue remapping, shared tag sets, user/kernel request mapping, SG counts, and request clone/unprep behavior.
