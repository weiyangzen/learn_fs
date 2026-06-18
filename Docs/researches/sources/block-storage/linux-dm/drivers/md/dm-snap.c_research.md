# File Research: sources/block-storage/linux-dm/drivers/md/dm-snap.c

## Purpose
Implements the device-mapper snapshot family: `snapshot`, `snapshot-origin`, and `snapshot-merge`. It manages copy-on-write exception tables, origin-to-snapshot registration, snapshot metadata loading/commit through exception stores, snapshot merge-back into the origin, and COW-triggering for origin writes.

## Main Objects
- `struct dm_snapshot`: per snapshot/merge target state, including origin/COW devices, exception tables, exception store, pending exception mempool, merge state, tracked read chunks, and queued merge-overlap bios.
- `struct dm_exception_table`: hash table for completed or pending exceptions.
- `struct dm_snap_pending_exception`: in-flight COW work, queued origin/snapshot bios, kcopyd sequencing, and full-chunk write fast path.
- `struct origin`: global origin-device entry with ordered list of snapshots.
- `struct dm_origin`: per `snapshot-origin` target context.

## Public/Exported Surface
- Exports `dm_snap_origin()` and `dm_snap_cow()` for access to snapshot devices.
- Registers three target types:
  - `snapshot`
  - `snapshot-origin`
  - `snapshot-merge`
- Module parameters:
  - `snapshot_cow_threshold`
  - kcopyd throttle parameter via `DECLARE_DM_KCOPYD_THROTTLE_WITH_MODULE_PARM`.

## Control Flow
- `dm_snapshot_init()` initializes exception-store infrastructure, origin hash tables, slab caches, and registers all three targets.
- `snapshot_ctr()` parses `<origin_dev> <COW-dev> <p|po|n> <chunk-size> [features]`, opens devices, creates the exception store, allocates exception hash tables, creates the kcopyd client and pending exception mempool, registers the snapshot under its origin, and reads metadata unless exception-table handover will happen later.
- `snapshot_resume()` performs exception handover for same-COW table reloads, suspending/resuming the origin mapped device if needed, then marks the snapshot active.
- `snapshot_map()` handles normal snapshot I/O:
  - flushes go to COW,
  - invalid or overflowed snapshots reject writes,
  - reads without an exception go to origin and are tracked,
  - reads/writes with completed exceptions remap to COW,
  - writes create or join pending exceptions, dispatching kcopyd or full-bio copy paths.
- `origin_map()` remaps origin I/O linearly, but writes call `do_origin()` so all active snapshots get required exceptions before the origin write proceeds.
- `snapshot_merge_map()` combines snapshot and origin semantics: reads use exceptions when present, writes may queue if they overlap actively merging chunks, and otherwise origin writes create exceptions in other snapshots.
- `snapshot_merge_next_chunks()` repeatedly asks the exception store for merge ranges, ensures other snapshots have exceptions for the origin extent, waits for conflicting tracked I/O, copies COW data back to origin, flushes, commits the merge, and removes merged exceptions.
- `snapshot_dtr()` stops merge if needed, unregisters the snapshot, waits for pending exceptions, destroys exception tables, mempool, exception store, bio, and devices.

## Data Structures and Algorithms
- Origin devices are hashed globally in `_origins`, with snapshots sorted by descending chunk size.
- Completed exceptions support coalescing consecutive chunks using `DM_CHUNK_CONSECUTIVE_BITS`.
- Pending exceptions are keyed separately and do not coalesce.
- Completion order is serialized by `exception_sequence` and an RB tree of out-of-order completions.
- Read tracking uses `dm_per_bio_data()` and a small chunk hash so merge and COW completion can wait for conflicting reads before overwriting origin/COW state.
- Snapshot reload handover swaps completed exception tables and exception stores between old and new targets sharing the same COW device.

## Dependencies
- Core DM target APIs from `dm.h` and `device-mapper.h`.
- Exception-store interface from `dm-exception-store.h`.
- kcopyd for chunk copy, zero, and callback sequencing.
- Bio remapping/submission, mempools, slab caches, hlist bitlocks, rwsems, spinlocks, wait queues, RB trees.

## Notable Behaviors
- `discard_zeroes_cow` allows discards to zero completed COW chunks rather than issue discard.
- `discard_passdown_origin` depends on `discard_zeroes_cow` and can pass discard to origin without triggering snapshot exceptions.
- Persistent overflow can either invalidate the snapshot or set `snapshot_overflowed` when userspace supports overflow reporting.
- Merge failure leaves the target usable as a normal snapshot/origin path where possible, but reports `"Merge failed"`.

## Risk and Test Focus
- Race-sensitive paths: pending exception allocation/insertion, completion table insertion, read tracking, and merge overlap queuing.
- Error paths should be tested for exception-store failures, COW full/overflow, kcopyd read/write errors, and merge commit failures.
- Snapshot reload and exception handover are delicate because metadata may only be loaded into one table at a time.
- `snapshot_dtr()` busy-waits on pending exceptions; pending-count leaks or callback loss would hang teardown.
