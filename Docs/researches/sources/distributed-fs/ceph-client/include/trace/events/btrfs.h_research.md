# sources/distributed-fs/ceph-client/include/trace/events/btrfs.h

## Purpose
`btrfs.h` is the Btrfs filesystem tracepoint schema. It covers transactions, inode lifecycle, extent maps and file extent items, ordered extents and writeback, sync operations, block groups/chunks, delayed refs, COW, allocation and free-space search, space reservation and flushing, workqueues, qgroups, backref prelim refs, extent state bits, tree locking, RAID56, and extent-map shrinker behavior.

## Important APIs, types, and functions
The file defines helpers for root/ref/chunk/group/extent/flush/qgroup enum formatting and fsid-aware macros `TP_STRUCT__entry_btrfs()`, `TP_fast_assign_btrfs()`, and `TP_printk_btrfs()`. Major event classes include `btrfs__inode`, file extent item classes, `btrfs__ordered_extent`, writepage, delayed tree/data/ref-head, chunk, reserved/reserve extent, work/workqueue, qgroup reservation/extent, prelim ref, block group, dump space info, sleep tree lock, locking events, space-info update, and RAID56 bio.

## Control flow
Tracepoints are placed through Btrfs operations: transaction commit, inode create/request/evict, extent lookup and extent item display, ordered extent add/start/finish/remove, writeback hooks, sync file/fs, block group creation/removal/reclaim, delayed ref enqueue/run, chunk alloc/free, COW/search-slot restart, reservation/flush and ticket handling, free extent search and cluster setup, workqueue queue/schedule/done, qgroup accounting and reserve conversions, extent state bit changes, tree lock wait/unlock, RAID56 bio mapping, RAID extent tree changes, and extent-map shrinker scan/removal.

## State and persistence behavior
The header owns no state, but its event payloads are rich snapshots of live Btrfs state: fsid, root ids, inode numbers, generations, extent offsets/lengths/flags/compression, ordered extent refs/bytes left, block group flags/used bytes, delayed ref identity/action/seq, qgroup counters/reservations, space-info counters, tree lock wait timestamps, RAID stripe identity, and shrinker cursor fields.

## Dependencies and integration points
It depends on many Btrfs internal types and helpers, writeback control, mm flag formatting, refcounts, spinlocks, atomic/percpu counters, bio fields, and tracepoint infrastructure. It integrates Btrfs internals with tracingfs/perf/BPF and is used by filesystem developers and xfstests diagnostics.

## Risks and test signals
Risks include high ABI surface area, dereferencing internal objects that may be in teardown, fsid/root formatting assumptions, lock-side effects in qgroup meta free tracing, and expensive counter snapshots if enabled on hot paths. Test signals are Btrfs xfstests and targeted workloads for fsync, delalloc/writeback, ENOSPC/flush tickets, delayed refs, qgroups, block-group reclaim, tree-lock contention, RAID56 I/O, and shrinker pressure, with trace output showing expected root/fsid and counter transitions.
