# sources/distributed-fs/ceph/src/mds/LogSegment.h

## Purpose

`LogSegment.h` defines the in-memory accounting object for one MDS journal segment. It records which metadata objects, client/session state, table transactions, purges, truncates, open files, and distributed operations are tied to a segment so `MDLog` can decide when the segment is safe to expire.

## Important APIs, Types, and Functions

`LogSegment::seq_t` is the segment/event sequence type. The constructor initializes segment id, offset/end positions, event count, and multiple intrusive `elist` containers with the appropriate member offsets from `CDir`, `CInode`, and `CDentry`.

The declared behavior is `try_to_expire(MDSRank*, MDSGatherBuilder&, int op_prio)`, `purge_inodes_finish(interval_set<inodeno_t>&)`, `set_purged_cb`, and `wait_for_expiry`. The inline stream operator prints sequence, offset range, and event count.

The important state fields are dirty/new dirfrags, dirty inodes/dentries, open files, dirty parent inodes, dirty dirfrag scatter categories, truncating and purging inode sets, pending mdstable commits, uncommitted leader/peer/fragment sets, last client tids, touched sessions, inotable/sessionmap/table versions, and expiry waiters.

## Control Flow and Data Flow

`MDLog::_submit_entry` creates or selects the current segment, increments `num_events`, assigns the segment to each `LogEvent`, and lets `LogEvent::update_segment` populate these lists and sets. Later, `MDLog` calls `try_to_expire`; the implementation in `journal.cc` turns each recorded dependency into stores, commits, lock nudges, table saves, waits, or purge callbacks using an `MDSGatherBuilder`.

Dirty dirfrag/dentry/inode lists flow into `CDir::commit` or inode stores. Dirty parent inodes flow into backtrace updates. Dirty dirfrag scatter lists flow into `Locker::scatter_nudge`. Open files may be re-journaled into a newer segment. Table and session versions flow into table save calls. Purging inodes install a callback that completes only after `purge_inodes_finish` subtracts all purged ids.

## State and Persistence Behavior

`LogSegment` is volatile accounting for durable journal content. It does not serialize itself as a standalone structure; rather, journal events update segment accounting as they are submitted or replayed. A segment cannot expire until every dependency represented here is durably stored or otherwise acknowledged. This makes the fields part of the crash-recovery safety mechanism even though they are in-memory.

`offset` and `end` track byte positions in the journal. `seq` is immutable. `purged_cb` and `expiry_waiters` are callback state for asynchronous expiry. Intrusive lists require that tracked cache objects own list hooks and remove/move them correctly.

## Dependencies and Integration Points

The header depends on Ceph intrusive lists, interval sets, context/gather types, fs and MDS types, and concrete cache object headers for member offsets. It integrates with `MDLog`, `LogEvent::update_segment`, `journal.cc` expiry logic, `MDCache`, `Locker`, table clients/servers, session map persistence, inode backtrace storage, purge/truncate machinery, and open file table commit tracking.

## Risks and Edge Cases

Expiry safety depends on complete segment accounting. If an event fails to register a dirty object or table/session version, the journal can trim before the corresponding state is safe. If an object remains on an intrusive list after destruction or migration, expiry can dereference invalid state. `set_purged_cb` asserts only one purge callback, so callers must not install multiple purge waits for the same segment.

Segments with open snap inodes, pending purges, uncommitted peer operations, or dirty scatterlocks can be delayed for reasons that are not obvious from byte offsets alone. Base inodes are stored directly while non-base dirty inodes commit through parent dirs, so tests must cover both paths.

## Test Signals

Integration tests should submit events that dirty each tracked object category and verify segment expiry waits for the expected commits, backtrace stores, table saves, session saves, scatter nudges, truncates, and purges. Replay tests should rebuild equivalent segment accounting from events. Purge tests should verify `purge_inodes_finish` completes `purged_cb` only when the interval set is empty. Log trimming tests should assert segments with pending open file table commits or uncommitted peer requests do not expire early.
