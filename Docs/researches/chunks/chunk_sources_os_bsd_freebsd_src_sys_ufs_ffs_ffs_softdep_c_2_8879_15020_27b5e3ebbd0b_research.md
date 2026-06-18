# Chunk Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_softdep.c lines 8879-15020

## Scope

This chunk covers the middle and later soft-updates implementation for FreeBSD FFS/UFS. It begins inside `softdep_change_directoryentry_offset()` and covers directory add/remove/change dependency cancellation, SUJ journal reference handling, unlinked-inode list maintenance, disk-write initiation/completion rollbacks, inode/cylinder-group sync paths, dependency-pressure cleanup, suspend checks, and DDB debugging helpers.

## APIs and Entry Points

- `softdep_setup_remove()` creates `dirrem` work for directory-entry removal.
- `softdep_setup_directory_change()` combines removal of an old reference with addition of a new reference for rename/change.
- `softdep_change_linkcnt()` records inode link-count deltas.
- `softdep_setup_sbupdate()` tracks SUJ unlinked-inode head updates in superblock writes.
- `softdep_disk_io_initiation()` and `softdep_disk_write_complete()` are the central pre/post write dependency hooks.
- `softdep_load_inodeblock()` and `softdep_update_inodeblock()` preserve effective link counts and transfer inode deps to inode-block buffers.
- `softdep_fsync()`, `softdep_sync_metadata()`, and `softdep_sync_buf()` drain dependencies for sync/fsync.
- `softdep_slowdown()`, `softdep_request_cleanup()`, `softdep_check_suspend()`, and `softdep_get_depcounts()` support cleanup, throttling, and suspend coordination.
- DDB commands expose softdep state for `inodedep`, `worklist`, `mkdir`, `allocdirect`, and `allocindir`.

## Control Flow

Directory removals flow through `newdirrem()`, which allocates `dirrem`, optional SUJ `jremref`s, finds the relevant `pagedep`, and checks for a colliding `diradd`. If the add was never visible on disk, `cancel_diradd()` cancels add-side journal refs, transfers journal work, marks the remove complete, and frees the obsolete add.

Directory changes build on that path. `softdep_setup_directory_change()` allocates a replacement `diradd`, calls `newdirrem()` for the old inode, then attaches the add to the new inode’s dependency lists. SUJ paths bind the latest `jaddref`; non-SUJ paths wait on inode write completion or move directly to pending if already stable. Directory rename/reparenting uses `merge_diradd()`, `cancel_mkdir_dotdot()`, and `cancel_diradd_dotdot()` to keep `.`/`..` ownership coherent.

The disk write path uses rollback-before-write and roll-forward-after-write. Directory pages temporarily hide uncommitted entries; inode blocks hide unwritten allocations and roll back pointers/sizes/link counts; indirect blocks swap to safe copies; cylinder-group bitmaps hide allocations whose journal records are not stable. Completion restores memory, releases only successful dependencies, and reattaches items needing another write.

Sync and cleanup repeatedly force prerequisites forward: journal refs, bitmap writes, inode writes, parent directory writes, dirty vnode flushes, worklist processing, and delayed vnode inactivation.

## State and Data Flow

- `diradd`: new directory references, offsets, target inode, prior `dirrem` for `DIRCHG`, and delayed journal work.
- `dirrem`: removed directory refs, old inode, parent dir inode, journal remove refs, and delayed work.
- `mkdir`: tracks `MKDIR_PARENT` and `MKDIR_BODY` completion for `.` and `..`.
- `inodedep`: link deltas, unlinked-list state, block pointer updates, journal inode refs, `id_bufwait`, `id_inowait`, and bitmap dependency coupling.
- `pagedep`: directory-page add/remove/move dependencies and `NEWBLOCK` state.
- `indirdep`: safe copies, truncation state, and staged `allocindir` lists.
- `bmsafemap`: cylinder-group bitmap deps for inode/block allocation and free work.
- `sbdep`: superblock dependency for SUJ `fs_sujfree` and checksum recomputation.

## Dependencies

This chunk depends on softdep workitem macros/types, journal helpers, dependency lookup helpers, allocation/free helpers, UFS/FFS geometry and bitmap routines, vnode/buffer APIs, mount/device state, AST/callout/sleep primitives, and per-filesystem/global softdep locks.

## Risks and Edge Cases

- Live buffers are temporarily mutated before write; missed roll-forward paths would corrupt cache state.
- Lock dropping around waits, vnode locks, allocation, and I/O requires repeated revalidation.
- Failed writes roll memory forward but do not release dependency ordering.
- SUJ unlinked-inode list ordering is delicate; `fs_sujfree`, `di_freelink`, and `UNLINK*` flags must be written in order.
- Rename/reparenting has subtle `.`/`..` ownership transfers and panic checks.
- UFS1/UFS2 inode rollback logic is duplicated and must stay behaviorally aligned.
- Suspend cleanup includes a forced-unmount workaround for orphaned `indirdep` objects after disk failure.
- Cleanup avoids snapshot/COW and locked-inode recursion paths to prevent deadlock or incoherent snapshots.

## Cross-Chunk References

- Earlier chunks define data structures, flags, workitem macros, counters, lock macros, journal helpers, and constructors.
- Earlier directory-add paths create `diradd`, `mkdir`, `jaddref`, `newdirblk`, `pagedep`, `inodedep`, `newblk`, and `bmsafemap` state completed here.
- Earlier block allocation/truncation code defines `allocdirect`, `allocindir`, `freeblks`, `freework`, `freefrag`, `freedep`, `jblkdep`, and related cancellation/free helpers.
- This range reaches the end of the `SOFTUPDATES` implementation; the final per-file report should merge it with chunk 1 rather than treating it as standalone.