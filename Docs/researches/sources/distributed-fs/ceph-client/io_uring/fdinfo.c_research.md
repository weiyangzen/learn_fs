# sources/distributed-fs/ceph-client/io_uring/fdinfo.c

## Purpose
`fdinfo.c` emits diagnostic `/proc/<pid>/fdinfo` output for io_uring file descriptors, including ring indices, queued SQEs/CQEs, SQPOLL metrics, registered files/buffers, poll/cancel state, overflow CQEs, and optional NAPI data.

## Important APIs, Types, And Functions
- `io_uring_show_fdinfo()` is the exported entry called by procfs fdinfo handling.
- `__io_uring_show_fdinfo()` performs the actual `seq_file` emission.
- `napi_show_fdinfo()` and `common_tracking_show_fdinfo()` print busy-poll tracking details when enabled.

## Control Flow
The public function tries `ctx->uring_lock` to avoid ABBA deadlocks with seq locks. The internal printer snapshots SQ/CQ head/tail values, iterates pending SQEs with nospec opcode bounds, iterates CQEs including CQE32 handling, reports SQPOLL thread metrics if applicable, lists registered files and buffers, traverses cancel-table poll lists, prints overflow CQEs under `completion_lock`, and appends NAPI info.

## State And Persistence
No state is mutated except local snapshots. Output reflects possibly racing ring state; the code explicitly tolerates imprecision for debugging.

## Dependencies And Integration Points
It depends on procfs/seq_file, io_uring rings, filetable helpers, SQPOLL metrics, cancel hash table, resource tables, opcode definitions, completion lock, and optional NAPI fields.

## Risks And Edge Cases
The code avoids blocking fdinfo reads behind ring locks by using `mutex_trylock()`, meaning output may be absent under contention. Active rings can race with printed SQ/CQ state. SQE128 and CQE32 handling must avoid wrap/corruption while printing.

## Test Signals
Manual/proc tests should verify fdinfo output for normal rings, SQPOLL, registered files/buffers, CQ overflow, poll lists, SQE128/CQE32, NAPI modes, and lock contention.
