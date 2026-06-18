# sources/distributed-fs/ceph-client/drivers/md/dm-snap.c

## Purpose
Implements Device Mapper `snapshot`, `snapshot-origin`, and `snapshot-merge` targets. It maintains exception mappings, coordinates copy-on-write through dm-kcopyd, tracks origin writes for all snapshots sharing an origin, performs exception handover during reload, and merges COW data back to the origin.

## Important APIs, Types, And Functions
`struct dm_snapshot` contains origin/COW devices, validity and overflow flags, active state, pending and completed exception tables, locks, tracked chunks, exception store, kcopyd client, merge state, and queued bios. `struct dm_snap_pending_exception` represents an in-flight exception with waiting origin/snapshot bios, sequence number, copy status, optional full-bio shortcut, and RB-tree linkage. Important functions include `snapshot_ctr()`, `snapshot_map()`, `snapshot_merge_map()`, `snapshot_resume()`, `snapshot_merge_resume()`, `do_origin()`, `__origin_write()`, `pending_complete()`, `start_copy()`, `copy_callback()`, and `snapshot_merge_next_chunks()`.

## Control Flow
Snapshot construction opens devices, creates the exception store, initializes hash tables, mempools, kcopyd, and origin registration, then loads metadata unless this target will receive handover. Snapshot reads map to COW if a completed exception exists or to origin otherwise. Snapshot writes allocate or reuse a pending exception, remap to COW, queue behind copy-out, and complete once metadata commit installs the completed exception. Origin writes call `do_origin()` so every active non-merging snapshot creates needed exceptions before the origin write proceeds.

Snapshot-merge maps like a snapshot but copies exception runs back to origin. It asks the persistent store for reverse consecutive runs, reallocates overlapping chunks for other snapshots, waits for pending IO and tracked reads, copies COW to origin, flushes, commits metadata removal, removes in-memory exceptions, and repeats.

## State And Persistence
Runtime state includes global origin hashes, DM-origin registrations, caches, mempools, exception tables, sequence counters, tracked reads, and merge flags. Persistence is delegated to the selected exception store. Handover swaps stores and exception tables between old and new targets sharing a COW device.

## Dependencies And Integration Points
Depends on DM target registration, `dm-exception-store`, dm-kcopyd, block bio remapping/splitting, per-bio data, table events, and suspend/resume target callbacks. It exports `dm_snap_origin()` and `dm_snap_cow()` for store implementations.

## Risks
Concurrency is the main risk: pending exceptions must commit in sequence, tracked reads must drain before overwrite, origin writes must protect all snapshots, and handover must only occur with the source suspended. Merge failure must stop safely and leave normal IO behavior intact.

## Test Signals
Test persistent and transient snapshots, origin-write COW, snapshot writes/reads, COW overflow, discard features, suspend/resume handover, concurrent IO under kcopyd load, multiple snapshots per origin, and snapshot-merge success/failure. Debug builds should show no leaked tracked chunks or pending exceptions.
