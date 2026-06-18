# Chunk Research: sources/windows/reactos/drivers/filesystems/btrfs/flushthread.c lines 7496-7946

## Scope

This report covers `sources/windows/reactos/drivers/filesystems/btrfs/flushthread.c` lines 7496-7946 for subset A (`Docs/research_subset_a.md`). The chunk begins inside `do_write2()` after its local batch list setup and covers the main Btrfs transaction flush pipeline: orphan pre-checks, dirty fileref and FCB flushing, dirty subvolume/root/drop-root handling, chunk and device-stat updates, tree extent allocation/splitting/cache convergence, tree/superblock writes, post-commit state cleanup, `do_write()` rollback wrapping, `do_flush()` locking, and the periodic kernel `flush_thread()` routine.

The immediately preceding lines define `do_write2()` and `check_for_orphans()`, so this chunk inherits the initialized `batchlist`, `rollback`, `cache_changed`, `no_cache`, and optional debug timing/loop counters from earlier in the same function.

## APIs And Entry Points

- `do_write2(device_extension *Vcb, PIRP Irp, LIST_ENTRY *rollback)` is the internal writeback implementation. In this range it batches and commits dirty metadata, drives tree consistency, writes trees and superblocks, then resets dirty state after success.
- `do_write(device_extension *Vcb, PIRP Irp)` is the public wrapper declared in `btrfs_drv.h`; it creates a rollback list, calls `do_write2()`, forces readonly mode and notifies the filesystem runtime on failure, or clears rollback records on success.
- `do_flush(device_extension *Vcb)` is the timer/manual flush helper. It takes `Vcb->tree_lock` exclusively, writes only when `Vcb->need_write` and not readonly, frees cached trees, logs failures, and releases the lock.
- `flush_thread(void *context)` is the `KSTART_ROUTINE` for the mount's periodic flush thread. It references the `DEVICE_OBJECT`, initializes and arms `Vcb->flush_thread_timer`, waits on it in a loop, skips flushes while the volume is locked, exits on unmount/removal, signals `flush_thread_finished`, and terminates the system thread.

## Control Flow

`do_write2()` first checks orphan state for dirty filerefs, then takes `dirty_filerefs_lock` exclusively and drains `Vcb->dirty_filerefs` by removing each `file_ref`, calling `flush_fileref()`, and releasing it with `free_fileref()`. It commits the resulting `batchlist` immediately via `commit_batch_list()`.

Dirty FCB processing is split into two passes under `dirty_fcbs_lock`. The first pass handles `fcb->deleted` entries before other files, matching the nearby comment about avoiding xattr-limit pressure and inode collisions. Each FCB is locked through `fcb->Header.Resource`, flushed with `flush_fcb(fcb, false, &batchlist, Irp)`, unlocked, then released with `free_fcb()`. The second pass flushes remaining dirty FCBs whose `subvol` is not `Vcb->root_root`.

Dirty subvolumes are drained without taking `dirty_subvols_lock` because the caller is expected to hold `tree_lock` exclusively. Drop roots, chunks, and batched tree edits follow: `drop_roots()` is called if `Vcb->drop_roots` is non-empty, `update_chunks()` may add batched changes and rollback entries, and the batch is committed.

The central convergence loop repeatedly calls `add_parents()`, `allocate_tree_extents()`, `do_splits()`, and `update_chunk_usage()`. It then either allocates legacy free-space cache entries through `allocate_cache()` or updates the free-space cache tree through `update_chunk_caches_tree()`. `allocate_cache()` failure is downgraded to a warning and continues with `no_cache = true`.

After convergence, `update_root_root()` finalizes root-root metadata, `write_trees()` persists dirty tree blocks, and `test_not_full()` validates that the filesystem is not overfull. The final write phase sets `superblock.cache_generation`, optionally flushes disk caches unless `options.no_barrier` is set, and writes all superblocks via `write_superblocks()`.

On success, the code cleans free-space cache state, clears chunk dirty flags, increments `superblock.generation`, clears every tree's `write` flag, marks `Vcb->need_write = false`, and drains `drop_roots`. `do_write()` owns rollback finalization; failure sets `Vcb->readonly = true`, raises `FSRTL_VOLUME_FORCED_CLOSED`, and calls `do_rollback()`.

## State, Dependencies, And Risks

Key state includes `dirty_filerefs`, `dirty_fcbs`, `dirty_subvols`, `drop_roots`, `batchlist`, `rollback`, `Vcb->trees`, `tree->write`, `superblock.generation`, `cache_generation`, `need_write`, `readonly`, `locked`, `removing`, `flush_thread_timer`, and `flush_thread_finished`.

This chunk depends on Windows kernel resource/timer/thread APIs plus Btrfs-local helpers such as `commit_batch_list()`, `flush_fcb()`, `flush_subvol()`, `drop_roots()`, `update_chunks()`, `allocate_tree_extents()`, `write_trees()`, `write_superblocks()`, `do_rollback()`, and `clear_rollback()`.

Major risks are destructive dirty-list removal before full success, inconsistent local `batchlist` cleanup across error paths, the lock invariant that `dirty_subvols` is safe under exclusive `tree_lock`, non-termination or excessive work in the tree-consistency loop, weaker crash ordering when `no_barrier` is enabled, and the coarse failure mode where any `do_write2()` error forces the mount readonly.

## Cross-Chunk References

Earlier `flushthread.c` sections define orphan cleanup, root/superblock writing, free-space cache handling, chunk updates, drop-root logic, and device-stat flushing. `treefuncs.c` defines `commit_batch_list()`, `do_rollback()`, and `clear_rollback()`. `btrfs.c` initializes the dirty queues, mount options, and flush-thread lifecycle. `fsctl.c`, `balance.c`, `scrub.c`, and `pnp.c` interact with `need_write` and explicit `do_write()` calls. This is the final chunk of `flushthread.c`; no later same-file code follows.