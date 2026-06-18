# Group Research: group_1294_netbsd_src_sources_os_bsd_netbsd_src_sys_ufs_lfs_lfs_inode_c_source_542926d1b72b

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/netbsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_inode.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_inode.c

## Purpose

`lfs_inode.c` implements core LFS inode maintenance: inode lookup inside inode blocks, timestamp/update flushing, file truncation and growth, block release, delayed segment-use accounting, indirect-block truncation, and buffer invalidation after truncation.

## Main Responsibilities

- Finds the newest matching dinode in an inode block with `lfs_ifind()`, scanning backward because newer inode copies can supersede older copies in the same block.
- Implements `lfs_update()` for inode time/state updates and synchronous vnode flushes.
- Implements `lfs_truncate()` for file extension, shrink, symlink clearing, page-cache size changes, block-pointer clearing, quota/accounting updates, and dirty-buffer invalidation.
- Frees blocks through `lfs_blkfree()` while batching segment byte decrements by segment.
- Stores postponed truncation deltas in per-inode/per-filesystem rb trees and commits them through `lfs_finalize_ino_seguse()` and `lfs_finalize_fs_seguse()`.
- Recursively truncates direct, single, double, and triple indirect blocks through `lfs_indirtrunc()`.
- Invalidates clean and dirty buffers past a truncation boundary with `lfs_vtruncbuf()` while returning delayed-write space to `lfs_avail`.

## Truncation Flow

`lfs_truncate()` handles device/FIFO/socket no-op truncation, short symbolic links, no-size-change metadata updates, file growth, and file shrink. Growth allocates the last byte, uses page-cache allocation for regular files, reserves log space for non-page-cache paths, updates vnode and dinode sizes, and writes the allocated buffer when needed.

Shrink reserves enough log space for metadata rewrites, zeroes partial tail data when required, sets the VM object size, invalidates buffers/pages beyond the new EOF, clears dead direct and indirect pointers, deregisters logical blocks, and accumulates released logical and real block counts. It updates `i_lfs_effnblks`, dinode block counts, `bfree`, quota usage, `i_lfs_hiblk`, and removes empty files from the paging queue.

## Segment Accounting

Because old blocks are not actually reclaimed until the new metadata reaches the log, block frees are staged as `struct segdelta` records. `lfs_blkfree()` groups contiguous frees from the same segment; `lfs_update_seguse()` inserts or updates rb-tree deltas; `lfs_finalize_seguse()` later subtracts bytes from `SEGUSE::su_nbytes` and writes segment-use entries. This keeps truncation accounting synchronized with eventual inode/ifile writes.

## Concurrency Notes

Most destructive paths assert the segment lock. `lfs_update()` explicitly avoids flushing `VU_DIROP` vnodes during directory operations, waits for in-progress writes on synchronous close/update, and coordinates with `lfs_writer`, `lfs_diropwait`, and `lfs_diropscv`. `lfs_vtruncbuf()` uses the vnode VM object lock and `bufcache_lock`, retries around `bbusy()` races, clears `BO_DELWRI`, unlocks LFS-locked buffers, and wakes `lfs_availsleep`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_inode.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_inode.h

## Purpose

`lfs_inode.h` defines the LFS/ULFS in-memory inode structure used by the kernel and by userland LFS tools running in a faked kernel environment. It also defines inode state flags, lookup-result state, LFS-specific inode extension state, quota constants, debug logging hooks, and helper macros.

## Main Data Structures

`struct ulfs_lookup_results` records directory lookup side effects: free-slot size, useful directory end, lookup hint offset, free-space offset, and found record length. LFS rename code consumes this state between lookup and directory mutation.

`struct inode` combines generic vnode/genfs state, mount/device identity, state flags, quota pointers, NFS modrev, lockf state, cached lookup results, LFS extension pointer, cached dinode fields, directory hash state, and the backing `union lfs_dinode *`.

`struct lfs_inode_ext` holds LFS-only volatile state: on-disk file size, effective block count pending I/O, direct-block fragment sizes, dirop/paging/cleaning list links, LFS private flags, highest logical block, kernel-only block-allocation splay tree, truncation segment-delta rb tree, and cleaner-preserved on-disk link count.

## Important Flags

`i_state` includes generic inode timestamp/write flags (`IN_ACCESS`, `IN_CHANGE`, `IN_UPDATE`, `IN_MODIFY`, `IN_MODIFIED`, `IN_ACCESSED`) and LFS-specific lifecycle flags such as `IN_CLEANING`, `IN_ADIROP`, `IN_PAGING`, `IN_CDIROP`, and `IN_MARKER`. `IN_ALLMOD` groups all states requiring inode writeback.

`lfs_iflags` includes `LFSI_NO_GOP_WRITE`, `LFSI_DELETED`, `LFSI_WRAPBLOCK`, `LFSI_WRAPWAIT`, and `LFSI_BMAP`, controlling page-write behavior, deleted-inode flushing, wrap control, and bmap state.

## Integration Notes

The header deliberately mirrors pieces of UFS inode state while adding LFS log-cleaning and segment-accounting state. Accessor macros such as `i_lfs_effnblks`, `i_lfs_fragsize`, `i_lfs_lbtree`, and `i_lfs_segdhd` hide the extension pointer layout from implementation files.

## Debug Support

Under `DEBUG`, this file defines the circular Ifile write log structure, `LFS_BWRITE_LOG`, `LFS_ENTER_LOG`, and `DLOG_*` debug categories. Without debug, these collapse to direct writes or no-ops, preserving call sites without runtime logging overhead.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_itimes.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_itimes.c

## Purpose

`lfs_itimes.c` implements `lfs_itimes()`, the shared timestamp update helper for LFS inodes. It updates dinode access, modification, and change times, mirrors access time into the Ifile for newer formats, marks inodes/Ifile dirty, updates `i_modrev`, and clears pending timestamp request flags.

## Behavior

`lfs_itimes(ip, acc, mod, cre)` requires one of `IN_ACCESS`, `IN_CHANGE`, `IN_UPDATE`, or `IN_MODIFY`. In kernel builds it obtains `now` with `vfs_timestamp()` when the caller does not provide explicit times.

For `IN_ACCESS`, it updates dinode atime fields. On 64-bit or post-v1 filesystems, it also updates the Ifile entry's atime fields, taking `lfs_fraglock` when the segment lock is not already held, writes the Ifile entry, and marks `LFS_IFDIRTY`. On older formats it marks the inode `IN_ACCESSED`.

For `IN_UPDATE` or `IN_MODIFY`, it updates mtime and increments `i_modrev`. For `IN_CHANGE` or `IN_MODIFY`, it updates ctime. It then marks `IN_MODIFIED` or `IN_ACCESSED` as appropriate under `lfs_lock`.

## Integration Notes

This helper is used by inode writeback and update paths so timestamp propagation is centralized. It supports both kernel and userland LFS tool builds by remapping kernel buffer/vnode/panic names in non-kernel mode.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_itimes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_kclean.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_kclean.c

## Purpose

`lfs_kclean.c` implements the in-kernel LFS cleaner. It selects dirty segments, pre-references live inodes, rewrites live inode/data blocks into the log, checks segment emptiness, runs an autoclean daemon, and exposes control over cleaner policy.

## Main Responsibilities

- Parses partial segments using callbacks shared with roll-forward code.
- Marks live inodes as being cleaned with `lfs_setclean()`.
- Rewrites current live blocks from old segments via `rewrite_block()` and `lfs_bwrite_ext(..., BW_CLEAN)`.
- Rewrites whole segments through `lfs_rewrite_segment()` and batches through `lfs_rewrite_segments()`.
- Checks whether a segment still contains live inode or file blocks with `lfs_checkempty()`.
- Selects candidate segments using greedy free-space benefit or Rosenblum-style cost-benefit age weighting.
- Runs `lfs_cleanerd()` over mounted LFS instances that have autoclean enabled.
- Rewrites whole files for coalescing/testing via `lfs_rewrite_file()`.
- Enables/disables and configures autoclean mode via `lfs_cleanctl()`.

## Segment Rewrite Flow

`lfs_rewrite_segments()` first enters the writer path and cleaner lock to prevent new directory operations and conflicting cleaners. Before taking the segment lock, it walks candidate partial segments and calls `ino_func_setclean()` and `finfo_func_setclean()` to identify live vnodes safely. It then takes `SEGM_CLEAN`, revalidates that candidate segments are dirty and not active, rewrites each live block/inode, flushes the generated segment with `lfs_writeseg()`, records direct-fragment and written-offset counts, and releases locks.

`finfo_func_rewrite()` validates inode number and generation, rejects unavailable or `VU_DIROP` vnodes, marks the vnode cleanable, reads blocks only if their current bmap address still matches the parsed old offset, writes replacement buffers into the current segment, updates metadata, and writes the inode. `ino_func_rewrite()` handles inode blocks not already covered by data-block rewrite.

## Autoclean Policy

`clean()` computes a priority threshold from configured parameters, filesystem pressure, `LFS_MUSTCLEAN`, and available/free block ratios. It scans every segment, skipping active, already-clean, ready, empty, zero-byte, and error segments. The highest-priority dirty segment above threshold is rewritten; repeated failure on the same segment marks it `SEGUSE_ERROR`. Under severe pressure it forces double checkpoints to reclaim ready/empty segments.

`lfs_cleanctl()` installs one of three modes: off, greedy, or cost-benefit. It creates the global `lfs_cleaner` kernel thread on first enabled filesystem and coordinates shutdown status with `lfs_cleanquitcv`.

## Concurrency Notes

The cleaner carefully separates pre-reference work from segment-locked rewrite work to avoid vnode/cleaner deadlocks. It refuses active segments, avoids `VU_DIROP` relocation, uses `LK_NOWAIT` vnode acquisition, and only rewrites inodes found on the clean list when necessary. `lfs_cleanerd()` holds an extra VFS ops reference while running so the LFS module cannot unload underneath the daemon.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_kclean.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_kernel.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_kernel.h

## Purpose

`lfs_kernel.h` provides kernel-only LFS support declarations and compatibility fcntl definitions that do not belong in the on-disk/userland `lfs.h` interface.

## Main Contents

- Declares global `struct lfs_stats lfs_stats`.
- Defines `LFS_SEGLOCK_HELD(fs)` as a wrapper around `lfs_seglock_held(fs)`.
- Defines `struct lfs_cluster`, the async clustered write descriptor used by `lfs_writeseg()` and `lfs_cluster_work()`. It stores copied-buffer size, buffer pointer array, buffer count, flags, owning filesystem, and synchronous segment pointer.
- Defines cluster flags `LFS_CL_MALLOC`, `LFS_CL_SHIFT`, and `LFS_CL_SYNC`.
- Defines `struct lbnentry`, the splay-tree node used to track logical block numbers allocated through `lfs_balloc`.
- Defines legacy/compat LFS fcntl command numbers for old `timeval50`, old `BLOCK_INFO_70`, ifile handle, reclaim, and log-wrap controls.

## Integration Notes

This header is included by the kernel LFS implementation files that need segment-lock checks, clustered write state, private logical-block tracking, or compat fcntl command definitions. Userland tools are expected to use the current public LFS command definitions instead of these compat forms.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_kernel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_pages.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_pages.c

## Purpose

`lfs_pages.c` implements LFS vnode page operations. It wraps `genfs_getpages()`/`genfs_putpages()` with LFS log-write semantics, block-aligned dirty-page handling, pagedaemon deferral, segment-lock integration, and metadata/FINFO updates for gathered page buffers.

## Getpages

`lfs_getpages()` rejects writable mappings of the Ifile with `EPERM`. Writable access to other files marks the inode `IN_MODIFIED` under `lfs_lock`, then delegates to `genfs_getpages()`. The implementation relies on `genfs_getpages()` reading whole filesystem blocks.

## Dirty-Page Normalization

`check_dirty()` scans the page range by filesystem block and ensures block-level consistency: if any page in a block is dirty, all resident pages in that block are marked dirty. For `PGO_FREE`, pages are wired and flagged `PG_DELWRI` so the pagedaemon will not repeatedly process pages that are already queued for LFS writing. Busy pages cause bail-out when the pagedaemon or segment-locked caller could deadlock.

`wait_for_page()` and `write_and_wait()` handle busy pages, including flushing already gathered buffers with `lfs_writeseg()` so pages can complete their journey to disk.

## Putpages Flow

`lfs_putpages()` ignores metadata/Ifiles and non-regular vnodes, handles empty page objects by removing the inode from the LFS paging queue, and expands requested ranges to filesystem-block boundaries. Clean or non-cleaning requests are delegated to `genfs_putpages()`/`genfs_do_putpages()`.

For dirty pages, pagedaemon callers do not write directly. Instead, the inode is put on `lfs_pchainhd`, `IN_PAGING` is set, `lfs_writerd_cv` is broadcast, and `EWOULDBLOCK` is returned.

Non-pagedaemon dirty cleaning acquires or reuses the segment lock, creates an FINFO entry unless the caller already provided one via `PGO_LOCKED`, marks DIROP summaries when necessary, loops through `genfs_do_putpages()` until pages are gathered, gathers indirect blocks for non-locked callers, calls `lfs_updatemeta()`, releases FINFO, writes the segment, and removes the vnode from the paging queue when all pages were written.

## Directory Operation and VM Notes

If a dirty vnode has `VU_DIROP` and the call is not already segment-locked, `lfs_putpages()` flushes pending directory operations through `lfs_flush_fs()` and retries. This avoids writing a newly created file's inode before the directory operation that makes it reachable has completed.

The code uses `LFSI_NO_GOP_WRITE` around clean-page delegation so unexpected dirties return through the LFS path instead of being written by generic GOP logic. There is also a dormant `fstrans` block shaped to avoid mount transaction sleeps in pagedaemon context.

## Concurrency Notes

The function is built around the vnode VM object lock and intentionally drops/reacquires it around filesystem transactions and segment-lock acquisition. It uses `PGO_BUSYFAIL` to prevent deadlocks, translates `EDEADLK`/`EAGAIN` from genfs into retry or flush behavior, and strips `PGO_SYNCIO` before the actual LFS gather because `lfs_segunlock()`/explicit waits perform synchronization.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_pages.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_rename.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_rename.c

## Purpose

`lfs_rename.c` adapts NetBSD's genfs sane/insane rename framework to LFS and ULFS directory formats. It performs permission/possibility checks, directory genealogy analysis, directory-entry mutation, link-count updates, LFS directory-operation bookkeeping, and orphan handling for overwritten targets.

## Main Responsibilities

- Supplies `genfs_rename_ops` callbacks for directory-empty checks, immutable/append checks, sticky/permission checks, remove, lookup, genealogy, lock-directory, and rename.
- Uses `struct ulfs_lookup_results` captured from `relookup()` to mutate directory entries efficiently.
- Recalculates source lookup results when target insertion compacts the same directory block and invalidates the old removal location.
- Reads `..` entries and walks parent directories to detect ancestry relationships.
- Implements actual ULFS-style rename semantics in `ulfs_gro_rename()`.
- Wraps ULFS rename in LFS-specific dirop setup/teardown in `lfs_gro_rename()`.
- Rejects `.` and `..` renames in `lfs_sane_rename()` before delegating to `genfs_sane_rename()`.

## Rename Flow

`ulfs_gro_rename()` first increments the source link count as a crash-recovery safety measure and writes that update through `lfs_update(..., UPDATE_DIROP)`. If the target does not exist, it optionally increments the new parent link count for directory reparenting and creates a new directory entry with `ulfs_direnter()`. If the target exists, it rewrites the target entry to point to the source with `ulfs_dirrewrite()`, adjusts parent link counts for directory replacement, and truncates overwritten directories to zero.

When moving a directory across parents, it rewrites the source directory's `..` entry to point to the new parent. Finally it removes the original source entry with `ulfs_dirremove()`, recalculating `fulr` first if an earlier `ulfs_direnter()` overlapped and compacted the relevant directory block.

## LFS-Specific Bookkeeping

`lfs_gro_rename()` calls `lfs_set_dirop(tdvp, tvp)`, marks source and parent vnodes with `MARK_VNODE`, delegates to `ulfs_gro_rename()`, orphans overwritten targets whose link count reaches zero, unmarks all involved vnodes, calls `lfs_unset_dirop()`, and releases references held for the operation.

## Safety Notes

The code relies heavily on `KASSERT` invariants for locked vnodes, mount equality, vnode distinctness, and type checks. Several comments document inherited UFS/ULFS rename awkwardness around link-count side effects in `ulfs_dirremove()` and `ulfs_dirrewrite()`. Crash consistency is handled through temporary link-count increments and LFS dirop partial-segment marking rather than a traditional journal.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_rename.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_rfw.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_rfw.c

## Purpose

`lfs_rfw.c` implements LFS roll-forward recovery. After an unclean mount, it validates partial segments written after the last checkpoint and reconstructs newer inode generations, inode metadata, and direct data block mappings before forcing a clean checkpoint.

## Main Responsibilities

- Allocates or replaces specific inode generations during recovery with `lfs_rf_valloc()`.
- Updates block metadata and segment accounting for recovered data blocks with `update_meta()`.
- Copies dinode metadata while intentionally excluding block pointers and block counts via `update_inoblk_copy_dinode()`.
- Scans inode blocks to discover highest generation numbers with `update_inogen()`.
- Replays inode blocks with `update_inoblk()`.
- Replays FINFO data-block mappings with `finfo_func_rfw()`.
- Parses and validates partial segments through `lfs_parse_pseg()`.
- Coordinates the four roll-forward phases in `lfs_roll_forward()`.
- Drops pages from recovered vnodes after replay to reset VM state.

## Partial Segment Parser

`lfs_parse_pseg()` skips label/superblock padding, reads the segment summary, validates magic, optional summary checksum, serial/identity or timestamp constraints, and expected serial sequencing. It walks interleaved inode blocks and FINFO-described file blocks, either validating data checksums or invoking supplied inode/FINFO callbacks. It advances to the next partial segment according to the summary's `next` pointer when the current segment lacks room for another partial segment, matching `LFS_PARTIAL_FITS` in `lfs_segment.c`.

The same parser is reused by the cleaner, emptiness checker, and roll-forward code.

## Roll-Forward Phases

`lfs_roll_forward()` skips clean filesystems, disabled recovery, v1 filesystems, and missing process context. For v2+ dirty filesystems:

1. Validates successive partial segments after the checkpoint using checksums and serial numbers, marking covered segments dirty and remembering the last complete non-continuation partial segment.
2. Sets the filesystem write offset to the end of the replay range and chooses a clean next segment so replay does not overwrite data being recovered.
3. Scans inode blocks to record highest inode generations in the Ifile.
4. Replays inode blocks for current generations, updating inode addresses and dinode metadata.
5. Replays FINFO data block mappings, calling `lfs_update_single()` and adding segment bytes for recovered blocks.
6. Writes a synchronous checkpoint and resets availability/accounting from on-disk segment state.

## Recovery Semantics

`lfs_rf_valloc()` can reuse an already-cached matching generation, replace an older cached generation with a newer dinode, or create a new vnode from dinode metadata. Data blocks are not copied during replay; they already exist in the post-checkpoint log, so recovery updates metadata to point at them. Short symlink payloads are copied from dinode direct-block storage.

## Safety Notes

Roll-forward for v1 filesystems is disabled because timestamp-based partial-segment ordering can be fooled by clock rollback. v2+ uses monotonically increasing serial numbers and filesystem identifiers. Incomplete DIROP continuation chains are discarded by replaying only through the last complete non-`SS_CONT` boundary.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_rfw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_segment.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_segment.c

## Purpose

`lfs_segment.c` is the core LFS segment writer. It flushes vnodes, builds partial segments, gathers dirty buffers and pages, updates block and inode metadata, writes segment summaries/inode blocks/data clusters, advances log segments, writes superblocks, and completes asynchronous clustered I/O.

## Main Responsibilities

- Updates Ifile modification time with `lfs_imtime()`.
- Flushes a single vnode synchronously with `lfs_vflush()`.
- Iterates eligible vnodes for regular, dirop, empty, or cleaner writes with `lfs_writevnodes()`.
- Performs whole-filesystem segment writes and checkpoints through `lfs_segwrite()`.
- Writes file data, indirect blocks, and inode records through `lfs_writefile()` and `lfs_writeinode()`.
- Updates inode-address mappings in the Ifile and segment-use byte accounting via `lfs_update_iaddr()`.
- Gathers dirty buffers into FINFO entries with `lfs_gatherblock()` and `lfs_gather()`.
- Assigns new physical addresses and rewrites direct/indirect metadata through `lfs_updatemeta()` and `lfs_update_single()`.
- Starts new partial segments and clean log segments with `lfs_initseg()` and `lfs_newseg()`.
- Writes clustered async disk I/O with `lfs_writeseg()`.
- Writes superblocks and handles superblock/cluster completion workqueue callbacks.
- Maintains FINFO entries with `lfs_acquire_finfo()` and `lfs_release_finfo()`.

## Segment Write Flow

`lfs_segwrite()` decides whether a checkpoint is needed from flags, active segment pressure, explicit checkpoint requests, and clean-segment thresholds. It takes the writer lock before the segment lock when checkpointing, writes regular vnodes, then optionally writes DIROP vnodes under the writer lock, flushes directory-operation state, finalizes filesystem-level segment-use deltas, clears `SEGUSE_ACTIVE` on old segments for checkpoints, repeatedly writes the Ifile until stable, writes pending partial segments, and unlocks.

`lfs_writefile()` creates an FINFO entry, marks DIROP summaries, gathers appropriate data buffers depending on mode, uses `VOP_PUTPAGES(... PGO_LOCKED)` for normal regular files, gathers indirect blocks when required, and releases the FINFO. Cleaner writes gather only fake cleaner buffers; roll-forward drops direct buffers because their contents are already on disk.

`lfs_writeseg()` finalizes segment-use bytes, checks FINFO validity, counts inode blocks, timestamps the segment, marks buffers busy to protect checksums, cleanses `UNWRITTEN` indirect pointers when needed, computes data and summary checksums, updates free/dmeta counters, clusters buffers into `MAXPHYS` writes, submits async I/O, updates stats, and initializes the next partial segment if needed.

## Metadata Updates

`lfs_updatemeta()` sorts gathered buffers by logical block number, records the final fragment length, assigns physical addresses at the current log offset, and calls `lfs_update_single()` for each filesystem block in each gathered buffer. `lfs_update_single()` resolves the old block pointer through `ulfs_bmaparray()`, updates direct, single-indirect, or deeper indirect pointers, adjusts dinode block counts and fragment sizes, subtracts old segment bytes, and marks the Ifile dirty when segment-use entries change.

`lfs_writeinode()` allocates inode blocks in the current segment, updates inode times, copies dinodes, handles Ifile self-write corner cases, marks DIROP completion state, preserves old link count/size when cleaner writes DIROP vnodes, removes `UNWRITTEN` addresses from on-disk dinodes, finalizes per-inode truncation deltas, updates inode summary counts, and records the inode's new address.

## Segment Allocation

`lfs_initseg()` starts a new partial segment, rolling to a new segment when `LFS_PARTIAL_FITS` fails. It skips embedded superblocks and segment-zero label padding, records cleaner partial segment addresses, allocates a summary buffer, initializes `SEGSUM`, FINFO pointers, free-byte counters, and roll-forward flags.

`lfs_newseg()` honors log-wrap stop controls, marks the selected next segment dirty/active, shifts cleanerinfo clean counts to dirty, records last/current segment addresses, scans for the next clean segment while optionally skipping invalidated segments, increments active segment counts, and updates stats.

`lfs_rewind()` can move the write offset to a lower-numbered clean segment before a requested segment, consuming remaining availability in the current segment.

## Async Completion

`lfs_cluster_work()` completes clustered writes on a workqueue. It propagates errors to child buffers, clears `B_GATHERED`, unlocks LFS buffers whose delayed-write state is gone, invalidates ordinary cleaner-created regular-file buffers, restores page-daemon buffer state when needed, calls `biodone()`, marks vnodes modified if dirty buffers remain after output completion, wakes vnode waiters, frees copied cluster memory, releases pools, and decrements filesystem/segment I/O counters.

`lfs_super_work()` frees async superblock buffers, clears `lfs_sbactive`, decrements `lfs_iocount`, and wakes waiters. `lfs_free_aiodone()` frees malloc-backed temporary buffers.

## Concurrency Notes

This file is organized around strict segment-lock ownership. It also coordinates with `lfs_writer`, `lfs_lock`, vnode interlocks, `bufcache_lock`, vnode iterators, workqueues, and `v_numoutput` waits. Special paths avoid reclaim deadlocks, skip vnodes in incompatible vnode states, protect checksum windows by marking buffers busy, and ensure synchronous segment writes wait for outstanding cluster I/O.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_segment.c -->