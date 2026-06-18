# Group Research: group_1293_netbsd_src_sources_os_bsd_netbsd_src_sys_ufs_ffs_fs_h_sources_os_bs_9a80b37a8291

Scope checked against `Docs/research_subset_a.md`: subset A includes the complete `sources/os/bsd/netbsd-src` tree. All 10 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/fs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/fs.h

Read completely: 774 lines.

Defines the NetBSD FFS/UFS on-disk superblock, cylinder-group layout, constants, feature flags, and address/size conversion macros.

Core on-disk layout:
- Documents FFS superblock search locations: floppy/front, UFS1 at 8 KiB, UFS2 at 64 KiB, and fallback at 256 KiB, with `SBLOCKSEARCH` deliberately avoiding UFS1 probing at the UFS2 offset.
- Defines boot block and superblock constants (`BBSIZE`, `SBLOCKSIZE`), fragmentation limits (`MAXFRAG`), minimum block size (`MINBSIZE`), mount/volume name lengths, snapshot limits, and layout tuning defaults.
- `struct csum` and `struct csum_total` hold per-cylinder-group and filesystem-wide free-space/directory/inode summaries.
- `struct fs` is the FFS superblock ABI, carrying layout offsets, block/fragment geometry, cylinder group counts, derived masks/shifts, clean state, mount name, volume name, journal/quota/snapshot metadata, cylinder summaries, size fields, flags, inode format, and magic.
- `struct cg` is the modern cylinder group ABI; `struct ocg` preserves old cylinder group layout compatibility.

Feature and compatibility flags:
- Magic values cover UFS1, UFS2, UFS2 extended attributes, swapped-endian variants, and `FS_OKAY`.
- Clean flags distinguish clean and was-clean states.
- Filesystem flags include soft dependencies, WAPBL, quota2, POSIX.1e ACLs, NFSv4 ACLs, TRIM, and compatibility flags from FreeBSD/gjournal.
- `FS_SWAPPED` is the internal endian-swapped marker.

Access and layout macros:
- Cylinder-group accessors abstract old/new cg layouts and swapped-endian fields.
- Address macros map filesystem blocks to disk blocks, cylinder group bases, inode block addresses, inode offsets, block maps, rotational tables, and free-space computations.
- Fast geometry macros implement block/fragment offset, rounding, block-to-fragment conversion, logical block numbers, and direct/indirect block pointer reads for UFS1 vs UFS2.
- `ffs_blksize()` and `ffs_sblksize()` compute real file-block size for fragment-sized final blocks.
- Apple UFS label constants and packed `struct appleufslabel` describe the optional Apple label region.

Risks and notes:
- This is ABI-defining source; changing field order, constants, or macro semantics affects mount, fsck, boot, and cross-BSD compatibility.
- Comments warn that UFS2/FFSv2 superblock placement creates compatibility traps with stale UFS1/UFS2 superblocks.
- Several fields are historical, unused, or compatibility aliases, but remain part of the on-disk structure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/Makefile

Read completely: 7 lines.

Kernel include-install Makefile for LFS public headers.

Behavior:
- Sets `INCSDIR` to `/usr/include/ufs/lfs`.
- Installs `lfs.h`, `lfs_accessors.h`, `lfs_inode.h`, and `lfs_extern.h`.
- Includes `<bsd.kinc.mk>` for NetBSD kernel include installation mechanics.

Risks and notes:
- Any header omitted here will not be installed for consumers expecting public LFS definitions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs.h

Read completely: 1518 lines.

Defines NetBSD LFS public on-disk formats, mount/userland control ABI, in-memory filesystem state, segment structures, and shared constants.

Core layout and constants:
- Defines fixed layout values such as label/superblock padding, reserved inode numbers, root/whiteout inode numbers, summary size defaults, name length, direct/indirect address counts, and directory block sizing.
- Documents LFS directory entry format, including 32-bit vs 64-bit headers, record padding, old directory format compatibility, and d_type/namlen interpretation.
- Defines file type constants matching inode mode high bits and directory entry type codes.
- Uses compile-time assertions to lock structure sizes and alignment.

On-disk metadata:
- Provides 32-bit and 64-bit directory headers/templates.
- Provides `struct lfs32_dinode`, `struct lfs64_dinode`, and `union lfs_dinode`, including direct/indirect block arrays and metadata fields such as times, uid/gid, generation, flags, sizes, block counts, and modrev.
- Defines segment usage structures (`SEGUSE`, `SEGUSE_V1`) and segment flags for active, dirty, superblock-bearing, error, empty, invalid, and reclaim-ready segments.
- Defines segment-summary file info (`FINFO32`, `FINFO64`), inode-info (`IINFO32`, `IINFO64`), ifile entries (`IFILE32`, `IFILE64`, v1), cleaner info, and segment summaries (`SEGSUM_V1`, `SEGSUM32`, `SEGSUM64`).
- Defines 32-bit and 64-bit disk superblocks (`struct dlfs`, `struct dlfs64`) with checkpoint fields, geometry, cleaner metadata, superblock locations, serial/timestamp, mount path, and checksum.

In-memory and kernel-facing state:
- `struct lfs` wraps the disk superblock union and mount-time flags for 64-bit, byte-swapped, and old-directory formats.
- Runtime state tracks current segment writing, ifile vnode, preventative/segment/fragment/ifile locks, writer/dirop counters, dirty inode counts, active superblock selection, cleaner state, reserved blocks, vnode chains, pending segment accounting, device vnode/dev_t, ULFS geometry, quota2 placeholders, and autocleaner state.
- `struct segment` describes a segment under construction, including buffer arrays, summary pointers, inode buffers, file info, bytes remaining, segment number, flags, and I/O counters.

Userland/control ABI:
- Defines `BLOCK_INFO` and compatibility versions for older binaries.
- Defines fcntl/private commands for rewind, invalidation, resize, wrap control, ifile file handle retrieval, segment waits, cleaner info, segment usage, bmapv/markv, reclaim, file stats, file rewrite/scramble, segment rewrite, and autoclean control.
- Provides maximum counts for segment usage, markv blocks, file stats, and rewrite arrays.
- Defines `struct ulfs_args` for mounting.

Risks and notes:
- This file is a dense ABI boundary shared by kernel, tools, and cleaners; field-size changes are high risk.
- The file carries substantial compatibility for LFS v1, 32-bit LFS, 64-bit LFS, older userland ABIs, and old directory formats.
- Multiple comments identify legacy or questionable behavior, including old directory format retention, strict-aliasing concerns around v1 ifile entries, and diagnostic segment-lock assertions that log rather than enforce.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_accessors.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_accessors.h

Read completely: 1569 lines.

Provides inline accessor and utility macros for LFS structures, hiding 32-bit vs 64-bit format differences, optional endian swapping, v1 compatibility, and kernel/userland/standalone build differences.

Build and byte-order model:
- `STRUCT_LFS` lets libsa and cleaner code reuse accessors with alternate LFS-like structures.
- Byte-swap macros are disabled for standalone and kernel builds without `LFS_EI`; otherwise they consult `lfs_dobyteswap`.
- `LFS_LITTLE_ENDIAN_ONDISK()` determines directory old-format interpretation.
- Compiler diagnostics are suppressed around packed-member address type checks used by accessor generators.

Directory and inode accessors:
- Defines directory record sizing (`LFS_DIRECTSIZ`, `LFS_DIRSIZ`, `LFS_MAXDIRENTRYSIZE`) and navigation (`LFS_NEXTDIR`).
- Inline functions get/set directory inode, record length, type, name length, name pointer, and directory-template dotdot fields.
- Handles old 32-bit directory format by returning `LFS_DT_UNKNOWN` and extracting namlen from the byte that overlaps `dh_type` on little-endian media.
- Dinode helpers copy only the active 32-bit or 64-bit structure and generate accessors for mode, nlink, inode number, size, times, flags, blocks, gen, uid/gid, and fake rdev.
- Direct and indirect block accessors preserve sign extension so sentinel values such as `UNWRITTEN` survive 32-bit reads.
- Birthtime is stored only for 64-bit dinodes.

Buffer, ifile, and segment metadata helpers:
- `LFS_LOCK_BUF` and `LFS_UNLOCK_BUF` maintain global locked-buffer count and byte accounting.
- `LFS_SET_UINO` and `LFS_CLR_UINO` maintain unwritten/dirty inode accounting for accessed/cleaning/modified state bits.
- `LFS_SEGENTRY`, `LFS_IENTRY`, `LFS_CLEANERINFO`, and related write macros read and dirty ifile-backed segment usage, inode, and cleaner blocks.
- Generated accessors cover FINFO, IINFO, IFILE, CLEANERINFO, SEGSUM, and superblock fields.
- Free-list head/tail helpers synchronize superblock fields and cleaner info fields for newer formats.
- Superblock accessors handle 64-bit, 32-bit, and 32-bit-only fields such as `ifile`, `segmask`, and `segshift`.

Addressing and free-space helpers:
- Defines block pointer/inode-number sizes, indirect count, inode-per-block/fragment helpers, fragment/block/disk address conversions, block rounding, LFS segment address conversions, and file block sizing.
- `union lfs_blocks` helpers provide format-independent pointer arithmetic over 32-bit or 64-bit block-pointer arrays.
- Free-space estimation macros account for dirty metadata, estimated clean metadata overhead, reserved minimum-free space, and privileged credentials.
- `LFS_NRESERVE` estimates minimum blocks needed to create a new inode.

Risks and notes:
- Many macros perform I/O, lock acquisition, dirty marking, and panics, so they are not simple field accessors.
- Correctness depends on callers holding the expected locks, especially ifile, fragment, segment, and global `lfs_lock` contexts.
- Several comments note file-ordering problems, disabled assertions, and old compatibility paths that should eventually be cleaned up.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_accessors.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_alloc.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_alloc.c

Read completely: 1153 lines.

Implements LFS inode allocation, fixed-number inode allocation, inode freeing, ifile extension, free-list reconstruction, orphan marking/recovery, and DEBUG free-list validation.

Core free-list model:
- Free inode state is stored in ifile entries using `if_daddr == LFS_UNUSED_DADDR` and `if_nextfree` links.
- A runtime bitmap mirrors free inode state for faster checks and diagnostics.
- Cleaner info carries free-list head/tail for newer LFS formats; compatibility macros update the appropriate storage.
- `LFS_ILLEGAL_DADDR` is used under DEBUG to distinguish allocated-but-not-yet-addressed inodes.

Main paths:
- `lfs_extend_ifile()` grows the ifile by one block, reallocates the inode bitmap, initializes new ifile entries, prepends new inodes to the free list, fixes tail when needed, and writes the new ifile block.
- `lfs_valloc()` allocates the free-list head, verifies the entry is free, updates the free-list head, records the generation/version, marks the inode allocated, extends the ifile when the list becomes empty, marks the filesystem modified, and increments file count.
- `lfs_valloc_fixed()` allocates a specific inode/version for roll-forward or recovery use, extending the ifile if necessary and unlinking the target inode from wherever it appears in the free list.
- `lfs_vfree()` waits for pending writes, removes dirop state, finalizes or transfers pending segment-use accounting, clears unwritten inode state, marks the inode deleted/free, clears the ifile disk address, bumps the version, reinserts it on the free list, marks the filesystem modified, and decrements file count.
- `lfs_order_freelist()` scans the full ifile at mount, rebuilds the sorted free list and bitmap, and records orphaned inodes for later reclamation.
- `lfs_orphan()` marks unlinked but still referenced files with the magic orphan nextfree value and may mark the inode dead if only internal references remain.
- `lfs_free_orphans()` vgets and vputs orphaned inodes found during mount so reclaim paths free them.

Debug support:
- `lfs_check_freelist()` verifies that free entries and the linked free list agree, detects loops, count mismatches, bad tail pointers, and in-use inodes on the free list.
- `dump_freelist()` prints free-list head, tail, and sample links for diagnostics.

Risks and notes:
- Corrupt ifile/free-list state commonly leads to `panic()`, not graceful repair.
- Several old ordered-free-list helpers are compiled out, and comments question why list insertion ordering was abandoned.
- Locking relies on preventative lock, fragment lock, vnode interlock, and global `lfs_lock`; many functions assert segment-lock expectations rather than proving them.
- Orphan handling comments acknowledge uncertainty about historical behavior but preserve the recovery mechanism.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_balloc.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_balloc.c

Read completely: 729 lines.

Implements LFS logical block allocation/accounting, fragment extension, indirect-block materialization, and write-pending block tracking for UVM page-backed writes.

Block allocation model:
- Missing blocks are represented as `UNASSIGNED`.
- Blocks accounted to the file but not yet written to disk are represented as `UNWRITTEN`.
- `lfs_balloc()` reserves free fragments before changing inode or indirect block pointers so ENOSPC can be reported before partial allocation.
- Effective block counts (`i_lfs_effnblks`) and superblock free counts are updated for newly accounted data and indirect blocks.

Main allocation behavior:
- Handles writes past EOF by extending a final fragment into a full block when necessary.
- Handles direct final-block fragment allocation or extension when writing within the direct block range.
- Uses `ulfs_bmaparray()` to discover existing mappings and required indirect path entries.
- Creates missing indirect blocks with cleared buffers and `UNWRITTEN` pointers.
- Reads existing indirect blocks if they are not already delayed-write or done.
- Marks direct, single-indirect, or deeper indirect references as `UNWRITTEN` for newly allocated blocks.
- If a caller asks for a buffer, returns an initialized/read buffer as needed; if writing a full block, may avoid an unnecessary read.

Fragment extension:
- `lfs_fragextend()` checks free space and quotas, optionally reads the old fragment buffer, waits for cleaner space if delayed-write accounting would exceed availability, grows the buffer, updates locked-buffer byte accounting, zeros newly added bytes, and updates inode/filesystem block accounting.

Write-pending page tracking:
- Defines an SPLAY tree keyed by logical block number for regular-file blocks dirtied through UVM without buffer headers.
- `lfs_register_block()` records a pending logical block, increases fake availability/page/locked-queue accounting, and waits for cleaner space first.
- `lfs_deregister_block()` removes one pending block unless a cleaner segment write is active.
- `lfs_deregister_all()` clears all pending entries for a vnode.

Risks and notes:
- Comments flag uncertain locking and questionable indirect-block cases, especially around single indirect handling and buffer initialization.
- Several code paths panic on unexpected indirect read failures.
- Correct accounting depends on matching register/deregister calls for page-backed writes and careful preservation of `UNWRITTEN` sentinel sign extension.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_bio.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_bio.c

Read completely: 827 lines.

Implements LFS buffer write interception, resource reservation, cleaner waiting, flush triggering, locked-buffer accounting, and allocation/freeing of LFS-owned I/O buffers.

Global resource accounting:
- Tracks locked-down buffer count/bytes, reserved locked buffer count/bytes, LFS-written pages, per-filesystem page trip threshold, write-in-progress state, and locked-queue waiters.
- Uses `lfs_lock`, `locked_queue_cv`, and `lfs_writing_cv` around these counters.
- Resource thresholds are derived from buffer/page availability via macros in related LFS headers.

Reservation and availability:
- `lfs_reserve()` reserves both estimated disk availability and locked-buffer resources for sensitive vnode-locked operations.
- `lfs_reserveavail()` waits for cleaner progress when available blocks are insufficient, synchronizes cleaner info, wakes the cleaner, and tracks pre-reserved availability.
- `lfs_reservebuf()` forces checkpoint flushes and waits on locked-buffer pressure unless the caller is in a cannot-wait dirop/unlock context.
- `lfs_fits()` estimates whether a requested number of filesystem blocks fits after accounting for summary blocks, dirty inode blocks, segment table, and ifile overhead.
- `lfs_availwait()` wakes and waits for the cleaner until `lfs_fits()` succeeds, with an escape for cleaner/force-checkpoint segment writes.

Write and flush behavior:
- `lfs_bwrite()` is the vnode bwrite entry and delegates to `lfs_bwrite_ext()`.
- `lfs_bwrite_ext()` converts normal buffer writes into delayed locked LFS buffers, marks inodes dirty or cleaner buffers clean, updates availability, reassigns buffers to dirty lists, and suppresses writes on read-only/already-clean filesystems.
- `lfs_flush_fs()` enters the writer, calls `lfs_segwrite()`, clears pending page-daemon flush state, and resets fake availability.
- `lfs_flush()` serializes global flushes, flushes one target filesystem or all mounted LFS filesystems, wakes page waiters, and coordinates with mount busy/unbusy.
- `lfs_needsflush()` and `lfs_needswait()` decide whether resource usage exceeds soft or wait thresholds.
- `lfs_check()` is the pressure gate used before more writes: it may flush dirops, trigger segment writes, wake writerd, and wait for locked-buffer pressure to fall.

Buffer helpers:
- `lfs_newbuf()` allocates an uncached busy I/O buffer, optionally allocates LFS memory, attaches it to a vnode, and sets `lfs_free_aiodone` completion.
- `lfs_freebuf()` detaches the vnode, frees owned memory unless the buffer is fake, and releases the I/O buffer.
- `lfs_wait_pages()` and `lfs_max_pages()` compute dynamic page thresholds from UVM pageable/available memory.

Risks and notes:
- Comments call out missing write-cost accounting, rough reservation estimates, and weak multi-filesystem modeling due to global locked-buffer counters.
- Deadlock avoidance depends on cannot-wait checks for active directory operations and unlock/inactivation paths.
- `lfs_bwrite_ext()` deliberately avoids ordinary asynchronous writes and relies on locked delayed-write buffers so segment writing controls physical placement.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_bio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_cksum.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_cksum.c

Read completely: 117 lines.

Implements LFS checksum helpers shared by kernel and non-kernel builds.

Functions:
- `lfs_cksum_part()` masks the length down to a 16-bit boundary and XORs successive 16-bit words into a running 32-bit sum.
- `cksum()` computes a complete checksum by calling `lfs_cksum_part()` with an initial zero and then `lfs_cksum_fold()`.
- `lfs_sb_cksum()` computes an LFS superblock checksum over the active 32-bit or 64-bit disk superblock variant up to, but not including, the checksum field.

Risks and notes:
- The file explicitly calls the checksum simple and suggests using the TCP/IP checksum instead.
- Input must be short-aligned; the function casts directly to `u_int16_t *`.
- `lfs_cksum_fold()` is currently a macro identity in `lfs_extern.h`, so no additional folding is performed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_cksum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_debug.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_debug.c

Read completely: 331 lines.

Provides DEBUG-only LFS logging, dumping, and consistency-check helpers. With `DEBUG` undefined, the file contributes no runtime code beyond the RCS metadata guard.

Debug facilities:
- Defines a circular `lfs_log` array and `lfs_lognum`.
- `lfs_bwrite_log()` records non-gathered/non-delayed writes before calling `VOP_BWRITE()`.
- `lfs_dumplog()` prints the circular write log with block number, operation, flags, pid, line, and basename.
- `lfs_dump_super()` prints selected superblock geometry, checkpoint, mask/shift, checksum, maxfilesize, and superblock-location fields through accessors.
- `lfs_dump_dinode()` prints inode metadata and direct/indirect block addresses.
- `lfs_check_bpp()` verifies that buffers in a segment buffer array map to contiguous physical disk addresses and reports mismatches.
- `lfs_debug_log()` routes enabled subsystem debug messages to `vlog(LOG_DEBUG, ...)`.

Disabled or weak checks:
- `lfs_check_segsum()` currently returns immediately, so its later segment-summary bounds/overwrite checks are effectively disabled.
- Some diagnostic paths retain DDB hooks and `panic()` calls but are unreachable because of the early return.

Risks and notes:
- This file is diagnostic-only and compiled under `DEBUG`, but its `lfs_bwrite_log()` wrapper changes write logging paths when enabled.
- Debug subsystem enabling is controlled by the `lfs_debug_log_subsys[]` array.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_extern.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_extern.h

Read completely: 349 lines.

Declares the LFS cross-file public/internal API, global variables, pools, sysctl numeric identifiers, and vnode/VFS operation entry points.

Public definitions:
- Defines `IS_LFS_VNODE()` using vnode tag `VT_LFS`.
- Defines LFS sysctl identifiers for write-indirect behavior, clean vnode list placement, stats, max pages, page trip threshold, stats retrieval, roll-forward writes, debug, lazy sync behavior, and roll-forward limit.
- Declares forward types used across LFS without requiring all implementation headers.

Kernel globals:
- Declares condition variables, memory pools, global locked-buffer counters, debug/cleaner settings, global lock, writing condition variable, and roll-forward limits.
- Declares `M_SEGMENT` malloc type.

Function declarations:
- Allocation: inode allocation/free, fixed allocation, free-list ordering, ifile extension, orphan handling, orphan freeing, and DEBUG free-list checking.
- Block allocation/I/O: `lfs_balloc`, block register/deregister helpers, availability wait, bwrite, fits, flush, pressure checks, buffer allocation/free, reservation, and resource thresholds.
- Debug: DEBUG-only write logging, dumps, segment summary/buffer checks, and subsystem logging.
- Inode/segment: update, truncate, ifile lookup, segment-use finalization, segment write/gather/update/invalidate/rewrite, superblock writes, finfo acquisition, and async completion helpers.
- Cleaner/roll-forward/syscalls: clean control, cleaner thread, rewrite file/segments, roll-forward parsing, segment clean/check, bmapv/markv, segwait, and cleaner control.
- VFS/vnode operations: mount operation prototypes, vnode initialization, resize/reset availability, vnode operation entry points, buffered read/write, and vnodeop tables.

Checksum declarations:
- `cksum()`, `lfs_cksum_part()`, `lfs_sb_cksum()`, and identity `lfs_cksum_fold()` are exposed outside `_KERNEL` as well.

Risks and notes:
- This header is the dependency hub for LFS implementation files; declaration drift can break many compilation units.
- Some declarations expose legacy or currently non-operable surfaces, including quota2 placeholders and disabled rewrite prototypes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_extern.h -->