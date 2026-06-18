<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/kyber-iosched.c -->
# sources/distributed-fs/ceph-client/block/kyber-iosched.c

## Purpose
`kyber-iosched.c` implements the Kyber blk-mq I/O scheduler. Kyber controls latency by classifying requests into scheduling domains, limiting each domain with device-wide tokens, batching dispatch per hardware queue, and dynamically resizing token depths from latency histograms.

## Important APIs, Types, and Functions
- Domain constants: `KYBER_READ`, `KYBER_WRITE`, `KYBER_DISCARD`, `KYBER_OTHER`.
- Queue state: `struct kyber_queue_data` stores domain token `sbitmap_queue`s, per-cpu latency histograms, timer, latency targets, and p99 state.
- Hardware context state: `struct kyber_hctx_data` stores per-domain flushed request lists, current domain, batching counter, per-software-context queues, busy bitmaps, and wait entries.
- Elevator callbacks: init/exit, hctx init/exit, depth limiting, bio merge, request prepare/insert/finish/requeue/completed, dispatch, has-work, depth-updated.
- Tunables: sysfs `read_lat_nsec` and `write_lat_nsec`; debugfs token/list/wait/current-domain/batching views.

## Control Flow
Initialization enables block stats, clears single-queue scheduling, computes async depth as 75% of queue requests, allocates per-domain token pools and per-cpu latency buckets, and initializes per-hctx queues and wait entries. Inserts classify each request by operation, append it to the matching per-context domain list, and set a busy bit so dispatch can flush it later.

Dispatch holds the hctx scheduler lock. It continues the current domain batch until the batch size is consumed or the domain cannot supply a request/token. It then rotates domains and attempts dispatch. `kyber_dispatch_cur_domain()` either dispatches from already flushed domain lists or obtains a token and flushes busy per-context queues. If no token is available, it registers a wait entry in the token sbitmap so token release reruns the hardware queue.

Completion records total and device I/O latency for read/write/discard requests in per-cpu histograms and schedules a timer. The timer aggregates histograms, computes p90 I/O congestion and p99 total latency, and resizes domain token depths: congested devices throttle domains with good latency and ease throttling for domains with bad latency.

## State and Persistence Behavior
Kyber state is runtime-only: token depths, wait queues, current batching domain, per-context pending lists, latency histograms, target latency sysfs values, and trace/debugfs observations. It does not persist policy across reboot. Request `elv.priv[0]` stores the allocated domain token index until finish/requeue clears it.

## Dependencies and Integration Points
The scheduler integrates with blk-mq elevator registration, request queues, `sbitmap_queue`, blk statistics, block tracepoints, Kyber tracepoints, debugfs, and request ioprio indirectly through operation classification. It is registered as elevator `kyber` via module init.

## Risks and Edge Cases
Correct token release is critical; leaks throttle domains permanently. Wait-queue insertion/removal has races with token wakeups and is carefully protected. Per-context list flushing trades merge opportunities against dispatch latency. Only read/write latency targets are exposed even though discard has an internal default. Latency feedback depends on sample windows and may overreact or underreact on sparse workloads.

## Test Signals
Run fio latency tests across read/write/discard mixes, token-depth resizing tracepoint checks, scheduler switch/load/unload tests, blk-mq debugfs inspection, NOWAIT/sync-vs-async queue-depth checks, merge tests, CPU hotplug/per-cpu bucket aggregation, and lockdep under high parallel dispatch/completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/kyber-iosched.c -->
