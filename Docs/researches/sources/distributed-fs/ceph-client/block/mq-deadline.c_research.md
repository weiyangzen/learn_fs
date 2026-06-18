<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/mq-deadline.c -->
# sources/distributed-fs/ceph-client/block/mq-deadline.c

## Purpose
`mq-deadline.c` implements the mq-deadline blk-mq scheduler. It adapts the classic deadline algorithm to blk-mq by sorting requests by sector while also enforcing read/write expiration, batching, write-starvation limits, and I/O priority ordering.

## Important APIs, Types, and Functions
- `struct deadline_data` stores global scheduler state: dispatch list, per-priority queues, last direction, batching, starved counter, tunables, and spinlock.
- `struct dd_per_prio` stores per-priority red-black sort lists and FIFO lists for reads and writes plus latest positions and stats.
- Priority mapping maps I/O classes NONE/RT/BE/IDLE to deadline priorities RT/BE/IDLE.
- Core algorithms: `__dd_dispatch_request()`, `dd_dispatch_prio_aged_requests()`, `dd_dispatch_request()`, `dd_insert_request()`, `dd_request_merge()`, `dd_bio_merge()`, and request merge/finish callbacks.
- Tunables: `read_expire`, `write_expire`, `writes_starved`, `front_merges`, `fifo_batch`, and `prio_aging_expire`.

## Control Flow
Initialization allocates `deadline_data`, initializes all per-priority FIFO and RB trees, sets defaults, marks the queue as `QUEUE_FLAG_SQ_SCHED` because scheduling is queue-wide, and sets async depth. Insertion maps request ioprio to a scheduler priority, records the per-prio pointer in `rq->elv.priv[0]`, attempts insert merge, then either appends to the dispatch head list or adds the request to both the sector-sorted RB tree and expiry FIFO list.

Dispatch first drains explicit dispatch-head requests. It then checks priority aging so old lower-priority requests can run despite higher-priority traffic. Otherwise it scans priorities from RT to IDLE and dispatches from the first priority that has work. Within a priority, `__dd_dispatch_request()` continues a batch in the same direction when possible, prefers reads over writes unless writes have been starved too often, switches to FIFO order when deadlines expire or sector order wraps, and rejects requests whose start time is newer than the aging threshold.

Merging can do front merges by RB lookup on `bio_end_sector()` when enabled, repositions RB nodes after front merge, preserves earliest FIFO expiry when two requests merge, and removes merged requests from queue state.

## State and Persistence Behavior
State is runtime scheduler metadata only. Requests live simultaneously in RB trees/FIFO lists or the dispatch list until dispatched. Statistics count inserted, merged, dispatched, and completed requests per priority; they can overflow but are sized for outstanding-request tracking. Sysfs tunables persist only until changed or scheduler teardown.

## Dependencies and Integration Points
The scheduler integrates with blk-mq elevator callbacks, request hashes/RB-tree helpers, bio merge helpers, ioprio encoding, sbitmap depth limiting, tracepoints, and optional blk-mq debugfs. It registers as elevator `mq-deadline` with alias `deadline` and module alias `mq-deadline-iosched`.

## Risks and Edge Cases
The scheduler uses queue-wide state even when dispatch is called for a specific hardware queue, so returned requests may target another hctx. Correct lock coverage around RB/list state is essential. Stats warnings in exit catch missed completions or bypassed paths. Priority aging must prevent starvation without undermining RT priority. Front merges require RB repositioning to preserve sector order.

## Test Signals
Use fio workloads for read-vs-write latency, sequential batching, starvation limits, RT/BE/IDLE priority behavior, priority aging, front merge on/off, scheduler switch/unload under I/O, debugfs queue stats, blk-mq queue-depth updates, and lockdep/KASAN under concurrent merges and dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/mq-deadline.c -->
