# sources/distributed-fs/glusterfs/xlators/performance/write-behind/src/write-behind.c

## Purpose
Implements `performance/write-behind`, a client-side write buffering xlator. It can acknowledge non-sync writes before backend completion, aggregate sequential small writes, preserve ordering for overlapping or strict-order dependencies, route barriers such as flush/fsync through the queue, retry failed backend syncs under configured policy, and hide stale `readdirp` stat data while cached writes are outstanding.

## Important APIs, Types, And Functions
`wb_inode_t` owns per-inode queues: `todo`, `liability`, `temptation`, `wip`, `all`, plus write window, transit bytes, generation, file size, invalidation state, and lock. `wb_request_t` wraps a call stub with ordering range, write size, fd/lkowner/pid, generation, refcount, and flags for append, tempted, lied, fulfilled, and go. Core helpers include `wb_enqueue_common()`, `wb_requests_conflict()`, `__wb_pick_winds()`, `__wb_pick_unwinds()`, `wb_fulfill()`, `wb_fulfill_cbk()`, `wb_process_queue()`, and `__wb_collapse_small_writes()`. Fops wrap writes, reads, flush, fsync, stat/fstat, truncate/ftruncate, setattr/fsetattr, lookup, readdirp, link, fallocate, discard, zerofill, and rename.

## Control Flow
Writes create per-inode context as needed. Sync, dsync, and optionally O_DIRECT writes are enqueued as normal tasks; other writes enter `temptation` and may be unwound early when window capacity permits. `wb_process_queue()` repeatedly preprocesses aggregation candidates, picks safe child winds after checking liability and WIP conflicts, unwinds newly lied writes, and sends selected liabilities to backend writev fulfillment. Fulfillment aggregates adjacent writes sharing fd/lkowner/offset within vector and size limits. Backend callbacks mark writes fulfilled, retry or fail on errors, handle short writes by adjusting request offsets/vectors, and reprocess the queue. Flush/fsync/read/stat-like fops enqueue behind dependent cached writes to preserve consistency.

## State And Persistence
State is in-memory per inode and exists until inode forget. Liability generation captures causal dependencies at enqueue time. Window accounting tracks bytes acknowledged but not yet safely fulfilled. File size is updated optimistically on writes/truncates and refreshed from lookup/truncate callbacks. Readdirp invalidation state tracks directories with active readdirp sessions and child inodes whose cached write completion could make returned `d_stat` stale.

## Dependencies And Integration Points
Uses Gluster call stubs, xlator fops, inode contexts, fd refs, iobuf/iobref, iovec helpers, locks, atomics, statedump, option parsing, and default callback helpers. It coordinates with directory metadata consumers by clearing `readdirp` entry inode/stat for regular files with outstanding liabilities or invalidation flags.

## Risks
The queue state machine is complex: refcounts, list membership, and generation checks must stay consistent across early unwind, backend retry, short write, and failure. Flush/fsync semantics are configuration-sensitive, especially `flush-behind` and `resync-failed-syncs-after-fsync`. Aggregation mutates request iovecs and iobrefs; allocation or merge failures must not leak or double-unwind. Append and O_DIRECT handling depend on flags and `strict-O_DIRECT`. The `wb_zerofill()` unwind path falls through to `noqueue` after an ENOMEM unwind, which is a code-shape risk for double handling. Stale `readdirp` stat mitigation relies on active-directory tracking and can miss cases if inode contexts are absent.

## Test Signals
Test buffered writes with early success, overlapping writes, non-overlapping writes with and without strict ordering, append writes, sync/dsync/O_DIRECT writes, flush/fsync barriers, flush-behind, backend write failure and retry policy, short writes, aggregation boundaries, file size after write/truncate/lookup, readdirp while cached writes are outstanding, inode forget with empty queues, and statedump of queue/window state. Fault injection for iobuf/iobref/frame allocation is important.
