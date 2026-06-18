# Chunk Research: sources/windows/winbtrfs/src/flushthread.c lines 7489-7950

## Scope

This chunk covers the main write-transaction finalization path for WinBtrfs, starting inside `do_write2()` after its local debug variable declarations and ending with the periodic kernel `flush_thread()` routine. It drains dirty file references, dirty FCBs, dirty subvolumes, dropped roots, chunk updates, tree allocation/splitting, free-space-cache updates, root-tree generation updates, tree writes, superblock writes, post-commit cleanup, rollback handoff, and timer-driven background flushing.

Adjacent context shows that `check_for_orphans()` immediately precedes this range and is part of the same transaction setup. The public entry point in this chunk is `do_write(device_extension* Vcb, PIRP Irp)`, declared in `btrfs_drv.h` and called from other driver paths that need to force metadata out.

## APIs And Entry Points

- `static NTSTATUS do_write2(device_extension* Vcb, PIRP Irp, LIST_ENTRY* rollback)` is the internal ordered commit pipeline. It assumes the caller holds `Vcb->tree_lock` exclusively, matching callees such as `commit_batch_list()` that annotate the same lock requirement.
- `NTSTATUS do_write(device_extension* Vcb, PIRP Irp)` initializes a rollback list, calls `do_write2()`, and either clears rollback records on success or forces the mounted volume readonly and rolls back on failure.
- `static void do_flush(device_extension* Vcb)` is the background flush wrapper. It acquires `Vcb->tree_lock`, calls `do_write()` only when `Vcb->need_write && !Vcb->readonly`, frees cached trees, logs failures, and releases the lock.
- `_Function_class_(KSTART_ROUTINE) void __stdcall flush_thread(void* context)` is the system thread entry point. It references the device object, initializes and arms `Vcb->flush_thread_timer`, waits at `Vcb->options.flush_interval`, exits on unmount/removal, skips work while `Vcb->locked`, signals `flush_thread_finished`, and terminates.

## Control Flow

`do_write2()` starts by initializing a local `batchlist` and checking orphan state for dirty file references. It then exclusively locks `dirty_filerefs_lock`, removes every `file_ref` from `Vcb->dirty_filerefs`, emits its directory/reference changes through `flush_fileref()`, releases each reference with `free_fileref()`, unlocks, and commits the accumulated batch.

Dirty FCB handling is intentionally two-pass while `dirty_fcbs_lock` is held. The first pass flushes and releases deleted FCBs before other files so deleted alternate data streams do not exhaust xattr limits and deleted normal files do not collide with reused inode metadata. After an intermediate batch commit, the second pass flushes non-root-root FCBs, acquiring each FCB `Header.Resource` around `flush_fcb()`, calling `free_fcb()`, and then committing another batch after releasing `dirty_fcbs_lock`.

Subvolume and root cleanup follows. Because the transaction holds `tree_lock` exclusively, the code drains `Vcb->dirty_subvols` without taking `dirty_subvols_lock`, calls `flush_subvol()` for each `root`, then applies `drop_roots()` if any roots are queued. `update_chunks()` writes pending chunk/device metadata into the batch and is followed by another `commit_batch_list()`.

The chunk then forces root metadata participation even for superblock-only changes. If the root tree is absent or not marked for write, it loads item zero from `Vcb->root_root` via `find_item()` and marks `root_root->treeholder.tree->write = true`, with a comment explaining Linux mount compatibility when generations must match. It also forces the extent root into cache via `add_root_item_to_cache(Vcb, BTRFS_ROOT_EXTENT, Irp)`.

If device statistics changed, `do_write2()` iterates `Vcb->devices`, flushes each `dev->stats_changed` device via `flush_changed_dev_stats()`, clears per-device flags, then clears `Vcb->stats_changed`.

The central convergence loop repeats until no free-space-cache allocation changed metadata and `trees_consistent(Vcb)` returns true. Each iteration adds parent pointers, allocates metadata tree extents, performs B-tree splits, updates chunk usage, and then either allocates legacy free-space cache items or updates the free-space-tree/chunk-cache tree when `BTRFS_COMPAT_RO_FLAGS_FREE_SPACE_CACHE` is set. A failure in legacy `allocate_cache()` is downgraded to a warning by setting `no_cache = true`; other loop failures exit through `end`.

Once trees are consistent, `do_write2()` updates the root root, writes dirty trees, checks for fullness with `test_not_full()`, optionally performs a debug-only extent-tree lookup for every tree, sets `superblock.cache_generation`, flushes disk caches unless barriers are disabled, and writes all superblocks. For volume-device children, it propagates the committed generation to every `volume_child` under `pdode->child_lock`.

Successful post-commit cleanup clears space cache state, clears each chunk's `changed` and `space_changed` flags, increments `Vcb->superblock.generation`, clears all in-memory `tree->write` flags, sets `Vcb->need_write = false`, and drains `Vcb->drop_roots`. Dropped roots with no FCBs are freed immediately; roots still referenced by FCBs are marked `dropped`.

`do_write()` wraps this with rollback semantics. Any `do_write2()` failure logs, marks the volume readonly, sends `FSRTL_VOLUME_FORCED_CLOSED` for `Vcb->root_file`, and calls `do_rollback()`; success calls `clear_rollback()`.

## State And Dependencies

Primary state is carried by `device_extension`: `need_write`, `readonly`, `locked`, `removing`, `options.flush_interval`, `superblock.generation`, `superblock.cache_generation`, `superblock.compat_ro_flags`, root pointers (`root_root`, `extent_root`), dirty queues (`dirty_filerefs`, `dirty_fcbs`, `dirty_subvols`), `drop_roots`, `devices`, `chunks`, `trees`, `vde`, and the flush-thread timer/event fields. FCB/file-ref state includes `fcb->deleted`, `fcb->subvol`, `fcb->Header.Resource`, `file_ref->fcb`, and their dirty-list links. Root state includes `root->checked_for_orphans`, `root->fcbs`, `root->dropped`, and `root->nonpaged->load_tree_lock`. Tree state includes `tree->write`, `tree->header.address`, and cached root tree holders.

The commit path depends on earlier functions in this file for transaction assembly and physical metadata work: `flush_fileref()`, `flush_fcb()`, `flush_subvol()`, `drop_roots()`, `update_chunks()`, `add_root_item_to_cache()`, `flush_changed_dev_stats()`, `add_parents()`, `allocate_tree_extents()`, `do_splits()`, `update_chunk_usage()`, `trees_consistent()`, `update_root_root()`, `write_trees()`, `test_not_full()`, `flush_disk_caches()`, `write_superblocks()`, and `clean_space_cache()`. It also depends on `treefuncs.c` helpers `commit_batch_list()`, `clear_batch_list()`, `clear_rollback()`, and `do_rollback()`, plus `free-space.c` helpers `allocate_cache()` and `update_chunk_caches_tree()`.

Windows kernel dependencies include executive resources (`ExAcquireResourceExclusiveLite`, `ExAcquireResourceSharedLite`, `ExReleaseResourceLite`, `ExDeleteResourceLite`), list primitives, pool freeing, object references, timers, events, `KeWaitForSingleObject`, `KeSetTimer`, `KeCancelTimer`, `FsRtlNotifyVolumeEvent`, and `PsTerminateSystemThread`.

## Risks And Edge Cases

- The call at line 7645 assigns `Status = commit_batch_list(...)` but does not immediately test it before root-tree forcing. A failed commit can be overwritten by later successful calls, unlike nearby commit sites that return on failure.
- `check_for_orphans()` inspects `Vcb->dirty_filerefs` just before this chunk without taking `dirty_filerefs_lock`; correctness relies on the surrounding exclusive `tree_lock` and caller discipline.
- Several early failures in `do_write2()` return directly instead of jumping to `end`; rollback is still handled by `do_write()`, but local batch cleanup is inconsistent. One `flush_fcb()` failure calls `clear_batch_list()`, while other paths after batch-producing calls may depend on callee cleanup or rollback.
- `allocate_cache()` failures are intentionally non-fatal and disable cache generation for this transaction. This preserves write progress but may leave the volume without legacy free-space-cache updates.
- `do_flush()` skips writes while `Vcb->locked`; if the timer thread repeatedly finds the volume locked, durability depends on later explicit flushes or a later timer pass.
- `flush_thread()` waits only on the timer. Shutdown/removal must cancel or satisfy the timer/wait path elsewhere, otherwise exit latency can be up to `flush_interval`.
- Dropped roots are physically freed only when their `fcbs` list is empty; otherwise they remain allocated and marked `dropped`, so later lifetime handling must respect that marker.
- The debug flush-time log for FCBs prints `filerefs` in the format string's first slot even though `fcbs` is the relevant counter, suggesting a diagnostics-only typo.

## Cross-Chunk References

- The chunk begins inside `do_write2()`; the function signature and `fcbs` debug variable start just before line 7489.
- `check_for_orphans()` at lines 7454-7479 is adjacent previous context and feeds the first status check in this range. It delegates per-subvolume orphan scanning to `check_for_orphans_root()`, which is earlier in the file.
- Most low-level metadata writers called here are defined earlier in `flushthread.c`, including tree extent allocation, split handling, chunk updates, FCB/file-ref flushing, subvolume flushing, root dropping, disk-cache flushing, and superblock writing.
- The final exported surface from this chunk is referenced across the driver: `do_write()` is used by send, PnP, scrub, balance, fsctl, create/write paths, and shutdown-style flows when `Vcb->need_write` is set. `flush_thread()` is declared in `btrfs_drv.h` and is the periodic background caller.

## Summary

This chunk is the ordered commit and background flush core for WinBtrfs. It turns dirty in-memory filesystem objects into Btrfs tree mutations, drives the metadata-allocation/split/free-space-cache convergence loop, writes trees and superblocks, advances generation state, clears dirty flags, and wraps failures by forcing the volume readonly with rollback. The final timer thread provides periodic durability while respecting mount/removal and volume-lock state.