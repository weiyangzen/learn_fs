# Chunk Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_softdep.c lines 1-8878

## Scope

This chunk covers the opening 8,878 lines of FreeBSD FFS soft updates and soft updates journaling support. It includes the non-`SOFTUPDATES` stubs, active softdep feature registration, dependency allocation/accounting, per-mount initialization and teardown, worklist and journal queue infrastructure, journal segment writing/completion, allocation bitmap dependencies, direct and indirect block allocation dependencies, block/inode deallocation setup, truncation machinery, and the beginning of directory-entry addition handling. The chunk ends in the signature and comments for `softdep_change_directoryentry_offset()`, whose implementation continues in the next chunk.

## APIs and Entry Points

- Non-`SOFTUPDATES` build stubs export the same public softdep API surface, mostly panicking on impossible calls and returning no-op status for selected hooks such as `softdep_mount()`, `softdep_initialize()`, `softdep_fsync()`, `softdep_flushworklist()`, cleanup requests, journal lookup, and dependency counts.
- Active exported entry points in this chunk include `softdep_initialize()`, `softdep_uninitialize()`, `softdep_mount()`, `softdep_unmount()`, `softdep_flushfiles()`, `softdep_flushworklist()`, `softdep_prealloc()`, `softdep_prerename()`, `softdep_prelink()`, `softdep_journal_lookup()`, allocation/deallocation setup functions, and `softdep_setup_directory_add()`.
- Internal BIO hooks are declared here and installed through `bioops`: `softdep_disk_io_initiation()`, `softdep_disk_write_complete()`, `softdep_deallocate_dependencies()`, and `softdep_count_dependencies()`.
- The per-filesystem flush thread entry point is `softdep_flush()`.
- SUJ journal APIs include `journal_mount()`, `journal_space()`, `journal_suspend()`, `softdep_process_journal()`, `jwait()`, and record writers for refs, blocks, truncation, and fsync.
- Directory-add setup begins with `setup_newdir()` and `softdep_setup_directory_add()`; `softdep_change_directoryentry_offset()` starts at the chunk boundary.

## Control Flow

Initialization installs global softdep BIO hooks, initializes global lists/callouts, sets `max_softdeps`, and registers AST cleanup. Mount setup allocates `mount_softdeps`, initializes hashes and dependency lists, enables `MNT_SOFTDEP`, optionally mounts SUJ, starts `softdepflush`, and may recompute cylinder group summaries. Unmount stops the flusher, tears down journal state, removes mount state, asserts dependency drainage, and frees hashes/locks.

The background loop calls `softdep_process_worklist()`, which first processes journal records and then dispatches pending `D_DIRREM`, `D_FREEBLKS`, `D_FREEFRAG`, and `D_FREEFILE` work. `process_removes()` and `process_truncates()` provide vnode-local pressure paths when locked vnodes block normal reclaim.

SUJ reserves space before allocations and link-count changes. `softdep_prealloc()`, `softdep_prerename()`, and `softdep_prelink()` may flush vnode work, drop locks, and return `ERELOOKUP`. Low journal space can trigger sync, speedup, and filesystem suspension until `journal_unsuspend()` sees enough space.

Journal work is packed into `jseg` buffers by `softdep_process_journal()`, written with segment headers, and optionally followed by a BIO flush barrier. Completion is ordered through `handle_written_jseg()`, `softdep_synchronize_completed()`, `complete_jsegs()`, and `free_jsegs()`.

Allocation setup flows from bitmap update to `bmsafemap` plus `inodedep/newblk`, then pointer update converts `newblk` into `allocdirect` or `allocindir`. Truncation builds `freeblks/freework` graphs, cancels obsolete allocations, writes safe inode/indirect state, and later frees blocks.

Directory-add setup links `diradd` into parent `pagedep`, target `inodedep` or `jaddref`, and for mkdir adds `mkdir/newdirblk` dependencies so `.` and `..` become stable before the parent entry.

## State and Data Flow

- Global state: dependency counters, `softdepmounts`, `max_softdeps`, callout, cleanup flags, and `debug.softdep` sysctls.
- Per-mount state: rw lock, pending work/journal lists, dependency hashes, dirty CG list, unlinked/mkdir lists, and SUJ `jblocks`.
- `worklist` is the common embedded header carrying type, state, mount, and list linkage.
- Main dependency types visible: `pagedep`, `inodedep`, `bmsafemap`, `newblk`, `allocdirect`, `indirdep`, `allocindir`, `freefrag`, `freeblks`, `freework`, `freefile`, `diradd`, `mkdir`, `newdirblk`, SUJ journal records, `jseg`, `jsegdep`, and `freedep`.
- Key flags include `ATTACHED`, `DEPCOMPLETE`, `COMPLETE`, `ALLCOMPLETE`, `INPROGRESS`, `IOSTARTED`, `ONWORKLIST`, `ONDEPLIST`, `GOINGAWAY`, `UNDONE`, `NEWBLOCK`, `MKDIR_BODY`, `MKDIR_PARENT`, `EXTDATA`, `UNLINKED`, `DELAYEDFREE`, and `UFS1FMT`.

## Dependencies

This code depends on FreeBSD vnode/mount locking, buf/bio, GEOM I/O, kthreads, callouts, sysctls, ASTs, VM pager truncation, UFS/FFS inode and block helpers, quotas, snapshots, and FFS allocation/free/update paths.

Many helpers are declared but defined later, including I/O initiation/completion handlers, pagedep cleanup, inode block rollback/rollforward, bmsafemap write handling, cleanup scheduling, exported sync/request helpers, and remaining directory remove/change logic.

## Risks and Edge Cases

- Correctness depends on strict lock ordering across vnode, buffer, softdep, mount, UFS, and global locks.
- Journal-space accounting is delicate; underestimation can force waiting, sync, or suspension.
- Worklist ordering is required to avoid inode/block identity reuse before old dependencies are gone.
- Journal segment reclamation must wait for ordered write completion and optional cache flush.
- Bitmap safety depends on `bmsafemap` ordering for both allocations and frees.
- Truncation is high risk: it mutates inode pointers, indirect buffers, page cache, quotas, journal records, and dirty-buffer dependencies.
- UFS1/UFS2 indirect pointer handling is manual and format-sensitive.
- No final per-file report was created.

## Cross-Chunk References

- Active behavior continues beyond this chunk; later chunks define many prototypes listed near lines 699-931.
- `softdep_change_directoryentry_offset()` begins at line 8875 and continues in the next chunk.
- `softdep_setup_directory_add()` depends on later `diradd_lookup()`, `diradd_inode_written()`, `merge_diradd()`, and completion/free helpers.
- Truncation/free paths call later `cancel_indirdep()`, `free_indirdep()`, `handle_jwork()`, `handle_workitem_freefile()`, and `handle_workitem_remove()`.
- Journal completion hands off to later bmsafemap, inode, and buffer completion/rollback helpers.