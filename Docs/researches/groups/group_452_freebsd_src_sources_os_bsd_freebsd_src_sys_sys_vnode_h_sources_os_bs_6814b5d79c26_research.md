# Group Research: group_452_freebsd_src_sources_os_bsd_freebsd_src_sys_sys_vnode_h_sources_os_bs_6814b5d79c26

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/vnode.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/vnode.h

Core FreeBSD vnode interface and VFS operation contract header. It defines vnode types, vnode lifecycle states, `struct vnode`, vnode attributes, I/O flags, access-mode bits, vnode operation descriptors, VOP helper macros, namecache hooks, vnode reference/locking APIs, range-lock wrappers, VM object helpers, and SMR helpers.

Key content:
- Defines `enum vtype` values for regular files, directories, block/char devices, symlinks, sockets, FIFOs, bad vnodes, and marker vnodes.
- Defines `enum vstate` and `enum vgetstate` for vnode construction/recycle/ref acquisition state.
- `struct vnode` is the central active-file object: operation vector, filesystem-private `v_data`, mount linkage, type-specific union, vfs hash linkage, namecache lists, vnode/interlock locks, buffer object, poll/inotify state, MAC label, advisory/range locks, hold/use counts, flags, write count, and sequence counter state.
- Documents lock ownership for vnode fields and list traversal rules: find under list lock, take interlock, drop list lock, then use `vget()` or doomed checks.
- Defines vnode flags split across interlock-protected `VI_*`/`VIRF_*`, vnode-lock-protected `VV_*`/`V2_*`, and mount-list `VMP_*` state.
- Defines `struct vattr` and operation flags such as `VA_UTIMES_NULL`, `VA_EXCLUSIVE`, and `VA_SYNC`.
- Defines I/O flags used by filesystem VOPs: `IO_SYNC`, `IO_ASYNC`, `IO_DIRECT`, `IO_EXT`, `IO_NORMAL`, `IO_BUFLOCKED`, `IO_RANGELOCKED`, sequence hints, and related bits.
- Defines access-mode bits from classic read/write/execute through NFSv4-style ACL permissions.
- Defines `struct vnodeop_desc`, generic VOP argument layout, VOP descriptor flags, and includes generated `vnode_if.h`.
- Declares broad kernel vnode/VFS APIs: namecache operations, vnode allocation/recycle/reference, `vn_open`, `vn_rdwr`, `vn_copy_file_range`, `vn_start_write`, `vn_truncate_locked`, extattr helpers, path helpers, directory iteration, vfs hash, and default/dead VOPs.
- Provides invariant/debug macros around vnode and VOP locking, stat/readdir/write pre/post hooks, kqueue/inotify notification hooks, and checked writecount/text helpers.
- Provides SMR wrappers for VFS read-side lookup and `vn_load_v_data_smr()`.

Research relevance:
- This is the primary vnode ABI/contract file for FreeBSD filesystems.
- FFS code in this group depends on these contracts for vnode locking, buffer objects, VOP dispatch, write suspension, sequence counters, VM objects, and I/O flag interpretation.
- The header is also the best single map of what a FreeBSD filesystem must implement or can delegate to default VOP helpers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/vnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/wait.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/wait.h

User/kernel wait-status ABI header for `wait`, `waitpid`, `wait3`, `wait4`, `wait6`, and `waitid`.

Key content:
- Defines wait status inspection macros: `WIFSTOPPED`, `WSTOPSIG`, `WIFSIGNALED`, `WTERMSIG`, `WIFEXITED`, `WEXITSTATUS`, `WIFCONTINUED`, and BSD-visible `WCOREDUMP`.
- Defines status construction helpers `W_EXITCODE`, `W_STOPCODE`, and kernel-facing `KW_EXITCODE`, which clamps process return codes to the low 8 bits.
- Defines wait option bits: `WNOHANG`, `WUNTRACED`/`WSTOPPED`, `WCONTINUED`, `WNOWAIT`, `WEXITED`, `WTRAPPED`, and BSD-visible `WLINUXCLONE`.
- Defines `idtype_t` selector values for `waitid()`/`wait6()` style APIs, including process, parent process, process group, session, user/group, all processes, LWP, task, project, pool, jail/zone, contract, CPU, and processor set IDs.
- Defines BSD special pid tokens `WAIT_ANY` and `WAIT_MYPGRP`.
- Exposes userland prototypes for wait-family calls when not compiling the kernel.

Research relevance:
- Not filesystem-specific, but part of the FreeBSD public ABI surface in this group.
- Useful when studying syscall ABI style, process status encoding, and compatibility-visible constants.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/wait.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/watchdog.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/watchdog.h

Public and kernel watchdog control interface.

Key content:
- Defines watchdog device path component `_PATH_WATCHDOG` as `"fido"`.
- Defines ioctl commands for patting the watchdog, setting/getting timeout, getting remaining time, setting/getting pre-timeout, selecting pre-timeout action, selecting software watchdog mode, configuring software timeout action, and generic watchdog control.
- Defines mode/control bits: `WD_ACTIVE`, `WD_PASSIVE`, `WD_LASTVAL`, `WD_INTERVAL`, and `WD_CTRL_DISABLE`/`ENABLE`/`RESET`.
- Defines human-oriented timeout exponent constants from never through 1 ms, 125 ms, 250 ms, 500 ms, 1 sec, and up to 128 sec.
- Defines pre-timeout software actions: panic, enter debugger, log, printf, and mask.
- Kernel section declares watchdog eventhandler callback types, eventhandler lists, kernel pat/control helpers for integer and `sbintime_t` timeouts, and the `wdog_software_attach` hook.

Research relevance:
- Shows FreeBSD’s watchdog ABI as a small ioctl/eventhandler contract.
- Relevant to OS substrate research rather than VFS, but it illustrates how kernel services expose both user-control and eventhandler-backed device/provider interfaces.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/watchdog.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_alloc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_alloc.c

Main FFS allocation, free-space accounting, inode allocation, block reallocation, TRIM aggregation, cylinder-group integrity, and live fsck repair interface.

Key responsibilities:
- `ffs_alloc()` allocates fragments/blocks with quota charging, free-space reserve enforcement, preferred-cylinder selection, softdep cleanup retry, fsfail handling, inode block count updates, and full-filesystem diagnostics.
- `ffs_realloccg()` grows a fragment in place when possible, otherwise allocates a replacement block/fragment, copies/zeros buffer state, frees the old allocation, and switches between space/time optimization.
- `ffs_reallocblks()` plus UFS1/UFS2 variants tries to relocate logical block clusters into contiguous physical extents, updating inode or indirect pointers, coordinating softdep dependencies, then freeing old blocks.
- `ffs_valloc()` allocates a new inode, using `ffs_dirpref()` for directories, `ffs_hashalloc()` for cylinder-group fallback, vnode replacement through `ffs_vgetf()`, generation number initialization, UFS1/UFS2 vnode op selection, and inode birthtime initialization for UFS2.
- `ffs_dirpref()` spreads high-level directories while clustering deeper related directories, using directory depth, average free inode/block counts, existing directory counts, and `fs_contigdirs`.
- `ffs_blkpref_ufs1()` and `ffs_blkpref_ufs2()` compute placement preferences for direct data, indirect metadata, directory blocks, first indirect/data locality, max-blocks-per-cylinder-group sections, and average-free-block cylinder selection.
- `ffs_hashalloc()` implements preferred-cylinder allocation, quadratic rehash, then brute-force cylinder-group search.
- `ffs_fragextend()`, `ffs_alloccg()`, `ffs_alloccgblk()`, `ffs_clusteralloc()`, and `ffs_mapsearch()` operate directly on cylinder-group bitmaps, fragment summaries, block summaries, cluster summaries, and rotors.
- `ffs_nodealloccg()` allocates inodes from cylinder-group inode maps and initializes new UFS2 inode blocks with barrier or synchronous writes before exposing them in the inode map.
- `ffs_blkfree()` and `ffs_blkfree_cg()` free blocks/fragments, handle snapshots/copy-on-write, update block/fragment/cluster summaries, integrate softdep free dependencies, and detect double frees.
- TRIM support (`ffs_blkrelease_start()`, `ffs_blkrelease_finish()`, `trim_lookup()`, `ffs_blkfree_sendtrim()`) consolidates contiguous freed block ranges and delays bitmap reuse until BIO_DELETE completion.
- `ffs_freefile()`, `ffs_vfree()`, and `ffs_checkfreefile()` manage inode bitmap frees and snapshot checks.
- `ffs_getcg()` reads and validates cylinder groups, including CRC/check-hash verification, magic/cg number checks, background-write flags, and timestamp update policy.
- `ffs_checkcgintegrity()` quarantines a corrupt cylinder group by zeroing its summary resources, clearing maxcluster, and marking the filesystem `FS_NEEDSFSCK`.
- `sysctl_ffs_fsck()` exposes controlled live repair commands for fsck: adjust inode ref/block/depth, set size, adjust superblock summaries, free inode/block ranges, set flags, set cwd, rewrite `..`, and unlink duplicate names.

Important patterns:
- UFS mount lock protects global summary mutations; cylinder-group buffers are read/modified around deliberate lock drops.
- Allocation paths commonly retry after `softdep_request_cleanup()` before reporting `ENOSPC`.
- Soft updates are wired into every allocation/free map mutation via setup functions instead of being an afterthought.
- TRIM is conservative: blocks are not returned to free maps until delete I/O completes, preventing reuse-before-delete reordering.
- Integrity failures avoid repeated bad-cylinder use by modifying summary state in memory and forcing fsck.

Research relevance:
- This is the central policy and bitmap implementation for FFS free-space management.
- It explains FFS locality heuristics, fragmentation policy, soft updates integration, quota interaction, snapshots, TRIM behavior, and online fsck repair hooks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_balloc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_balloc.c

FFS logical-block allocation implementation for UFS1 and UFS2. It maps a vnode file offset/logical block to allocated disk storage and returns the corresponding buffer.

Key responsibilities:
- `ffs_balloc_ufs1()` handles UFS1 file data allocation through direct blocks and single/double/triple indirect blocks.
- `ffs_balloc_ufs2()` mirrors that logic for UFS2 and additionally supports external attribute data via `IO_EXT` and `di_extb[]`.
- Both functions extend the previous final fragment to a full block when a later write would skip into a new block.
- Direct-block paths allocate or reallocate fragments/blocks, optionally clear invalid buffer contents (`BA_CLRBUF`), set buffer physical block numbers, update inode block pointers, and establish softdep direct/allocation dependencies.
- Indirect-block paths use `ufs_getlbns()` to walk indirect levels, allocate missing indirect blocks, initialize them, write them synchronously or asynchronously according to flags, and finally allocate the target data block.
- `BA_METAONLY` returns the indirect block buffer rather than allocating/fetching file data, used by truncation and snapshot code.
- Sequential reads through `BA_SEQMASK`/`BA_SEQSHIFT` may use `cluster_read()` when clearing/fetching existing blocks and memory pressure permits.
- Partial allocation failure unwinds allocated blocks: it syncs the vnode to remove dependencies, invalidates transient buffers, clears newly inserted pointers, restores quotas and inode block counts, syncs again, then frees the allocated blocks.
- UFS2 paths use unmapped buffers for metadata where appropriate and avoid WITNESS issues for snapshots via `GB_NOWITNESS`.

Important patterns:
- Every successful metadata pointer insertion sets inode flags such as `IN_CHANGE`, `IN_UPDATE`, and `IN_IBLKDATA`.
- `TDP_INBDFLUSH` is set while walking/allocating indirect blocks to avoid problematic recursive flushing behavior.
- Allocation failures under soft updates can request block cleanup once and retry before surfacing full-filesystem errors.
- UFS1 rejects `IO_EXT`; UFS2 treats external attributes as negative logical block numbers and marks buffers `BX_ALTDATA`.

Research relevance:
- This is the core bridge between VFS writes and FFS allocation policy.
- It shows how FFS builds direct/indirect block trees, integrates soft updates with block pointer publication, and preserves consistency during partial allocation failures.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_extern.h -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_extern.h

Kernel-only external interface for the FreeBSD FFS implementation.

Key content:
- Declares allocation/free APIs: `ffs_alloc`, UFS1/UFS2 `ffs_balloc`, `ffs_blkfree`, block preference helpers, TRIM release key helpers, `ffs_realloccg`, `ffs_reallocblks`, inode allocation/free, `ffs_freefile`, `ffs_checkfreefile`, and cylinder-group helpers.
- Declares superblock and mount operations: superblock hash, search/get/put/update, reload, mount ownership check, old filesystem compatibility helpers, file flush, sync vnode, snapshot mount/unmount/sync/remove, suspension init/uninit, and fsfail cleanup helpers.
- Declares vnode lookup/get APIs: `ffs_vget`, `ffs_vgetf`, `ffs_inotovp`.
- Defines `ffs_vgetf` flags for forced mount-list insertion, replacement, doomed replacement, forced inode dependency, and newly allocated inode handling.
- Defines `ffs_reload` flags for force and unsuspend.
- Defines TRIM keys: `NOTRIM_KEY`, `SINGLETON_KEY`, `FIRST_VALID_KEY`, and `MAXTRIMIO`.
- Exports vnode operation vectors for UFS1/UFS2 regular and FIFO vnode ops.
- Declares the soft updates API surface used throughout FFS allocation, inode updates, sync, rename/link prechecks, block/inode dependency setup, journal handling, buffer dependency movement, cleanup requests, and worklist management.
- Defines softdep cleanup request constants for inode/block flushing with optional wait.
- Defines `ffs_syncvnode()` flags `NO_INO_UPDT` and `DATA_ONLY`.
- Declares `ffs_rdonly()` and snapshot data structures.

Research relevance:
- This is the FFS subsystem contract file tying allocation, vnode ops, mount/superblock handling, snapshots, and soft updates together.
- It is the quickest index of cross-file dependencies for FFS implementation work.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_inode.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_inode.c

FFS inode update and truncation logic.

Key responsibilities:
- `ffs_update()` writes in-core inode state back to the inode block, after `ufs_itimes()` applies access/modify/change timestamps.
- It tracks durable-size/block-pointer changes using `IN_SIZEMOD` and `IN_IBLKDATA`, clearing them only on synchronous inode writes so `fsync()`/`fdatasync()` semantics remain correct.
- Snapshot inode updates avoid deadlock by using `GB_LOCK_NOWAIT`; if the inode buffer is busy, the code temporarily drops the vnode lock, waits, relocks, and revalidates the vnode.
- UFS1 and UFS2 inode writes copy the correct dinode format into the inode block; UFS2 updates dinode check hashes before writing.
- `ffs_truncate()` handles file growth, shrink, full truncation, external attribute truncation, short symlink clearing, directory hash truncation, page/buffer invalidation, quota adjustment, and block freeing.
- Growth path sets VM object size, allocates the last byte via `UFS_BALLOC`, writes the buffer, updates inode size, and writes the inode.
- Shrink path ensures the final block exists when needed, zeros partial-block tail data for non-directories, writes the shortened inode before freeing old blocks, then restores old pointers in memory temporarily to walk and release obsolete storage.
- Soft updates fast path can delegate zero-length truncation to `softdep_setup_freeblocks()` or journal freeblocks; otherwise truncation falls back to synchronous cleanup.
- Extended-attribute data on UFS2 can be truncated separately via `IO_EXT`, including slow synchronous freeing when soft updates cannot cover it.
- `ffs_indirtrunc()` recursively frees indirect-block trees in LIFO order, first zeroing entries and writing the indirect block so crash recovery sees the shortened tree before old blocks are released.
- `ffs_rdonly()` reports filesystem read-only state from the inode’s filesystem.

Important patterns:
- Inode/block pointer updates are persisted before block frees to preserve crash consistency.
- TRIM aggregation is used for freeing runs of direct and indirect blocks.
- `vtruncbuf()` and `vn_pages_remove()` keep buffer cache and VM object state aligned with new file size.
- Invariant checks verify final direct/indirect pointers match the shortened configuration and that full truncation leaves no buffers.

Research relevance:
- This file is central to FFS durability semantics: timestamp writeback, inode persistence, truncation ordering, soft updates interaction, and recursive indirect-block cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_rawread.c -->
# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_rawread.c

Optional FFS raw-read fast path that bypasses the normal buffer cache read path for suitable user reads.

Key responsibilities:
- Defines sysctls `vfs.ffs.allowrawread` and `vfs.ffs.rawreadahead`.
- Initializes a secondary pbuf UMA zone for raw read buffers during VM configuration.
- `ffs_rawread_sync()` ensures raw reads see coherent data by checking dirty mmap pages, pending writes, and dirty buffers; it may start a write section, upgrade the vnode lock, clean vnode pages, wait for buffer output, and call `ffs_syncvnode()`.
- `ffs_rawread_readahead()` builds a physical BIO read directly into mapped user pages using `vmapbuf()`, `ufs_bmaparray()`, and device vnode strategy; holes are filled with zeroes to preserve file semantics.
- `ffs_rawread_main()` drives the raw-read loop with one active pbuf and optional one-buffer readahead, waits for I/O completion, unmaps buffers, advances the `uio`, handles short reads/EOF/errors, and releases pbuf vnode references.
- `ffs_rawread()` decides whether the fast path can be used: raw reads must be enabled, single-iovec, userspace, full-resid read, not in deadlock-treatment mode, and sector-aligned by offset and length.
- Reads extending into a partial final filesystem block use raw I/O only for the full-block portion, leaving the remaining partial EOF handling to the normal buffered path.

Important patterns:
- The fast path prioritizes coherence before bypassing cache: dirty mmap and dirty buffers are flushed first.
- Physical mapping uses filesystem block mapping but avoids populating ordinary file buffers for the data transfer.
- Sparse holes are explicitly zero-filled rather than treated as I/O errors.
- Readahead is opportunistic and falls back cleanly if allocation or mapping setup fails.

Research relevance:
- Shows a FreeBSD FFS direct/raw read optimization distinct from ordinary `IO_DIRECT`.
- Useful for studying cache bypass constraints, vnode write-suspension interaction, dirty-page synchronization, and pbuf-based device I/O into user pages.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_rawread.c -->