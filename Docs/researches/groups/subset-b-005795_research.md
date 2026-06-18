# subset-b-005795 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_exchrange.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_exchrange.c

## Purpose
`xfs_exchrange.c` implements XFS range exchange and commit-range ioctls. It validates two regular files, flushes and invalidates the affected pagecache, reserves quota, and swaps the underlying extent mappings through `xfs_exchmaps`, with optional freshness checks for staged commit workflows.

## Important APIs, types, and functions
Public entry points are `xfs_ioc_exchange_range`, `xfs_ioc_start_commit`, `xfs_ioc_commit_range`, `xfs_exchrange_ilock`, `xfs_exchrange_iunlock`, and `xfs_exchrange_estimate`. `struct xfs_exchrange` carries the two files, offsets, length, public flags, and the sampled file2 identity/ctime/mtime/generation used by `__XFS_EXCHANGE_RANGE_CHECK_FRESH2`. Core helpers include `xfs_exchange_range`, `xfs_exchrange_contents`, `xfs_exchrange_prep`, `xfs_exchange_range_checks`, `xfs_exchrange_check_rtalign`, `xfs_exchrange_mappings`, `xfs_exchrange_reserve_quota`, and `xfs_exchange_range_finish`.

## Control flow
The ioctl wrappers copy arguments, reject nonzero padding or unsupported flags, resolve `file1_fd`, and call `xfs_exchange_range` with `file2` as the ioctl target. `xfs_exchange_range` rejects cross-mount, non-regular, directory, append-only, and insufficiently opened files; runs `remap_verify_area`; sets private cmtime update flags; wraps the operation in `file_start_write`/`file_end_write`; and sends fsnotify modify events after success. `xfs_exchrange_contents` verifies the filesystem feature and shutdown state, takes IO/MMAP locks on both inodes, prepares both files, exchanges mappings, and removes write-sensitive file privileges. Preparation checks EOF/range/alignment rules, handles realtime allocation-unit divisibility, waits for DIO, writes dirty cache ranges, attaches dquots, flushes/unmaps cached mappings, and cancels speculative CoW ranges. The mapping phase estimates reservation needs, starts a transaction, locks and joins both inodes, verifies forks, reserves quota with one blockgc retry on `EDQUOT`/`ENOSPC`, performs dry-run exit or updates timestamps, calls `xfs_exchange_mappings`, optionally marks the transaction synchronous, commits, and swaps incore sizes for `TO_EOF`.

## State and persistence
The durable state change is the logged extent-map exchange, inode timestamp updates, optional on-disk size exchange, and quota accounting adjustments. Runtime state includes paired IO/MMAP/ILOCK ordering, transaction reservations, quota retry bookkeeping, and temporary private flag bits. `START_COMMIT` persists nothing; it copies an opaque freshness blob to userspace containing mount fsid, file2 inode/generation, and ctime/mtime. `COMMIT_RANGE` revalidates that blob under metadata locking and fails with `-EBUSY` if file2 changed or the fsid differs.

## Dependencies and integration points
The file bridges VFS file semantics, XFS inode locking, quota, reflink/CoW cleanup, exchange-map deferred work, realtime allocation geometry, log transactions, pagecache writeback, fsnotify, and ioctl dispatch in `xfs_ioctl.c`. Scrub repair code and `xfs_exchmaps_item.c` reuse the lock and estimate helpers. `xfs_exchrange.h` exposes the ioctl and helper contracts.

## Risks and test signals
Risks cluster around atomicity and locking: same-file overlap detection, realtime allocation units that are not powers of two, partial EOF-block exchanges, stale freshness blobs, dry-run side effects, quota retry correctness, and incore size swapping after commit. Test signals include exchange within one file, cross-file exchange, `TO_EOF`, `DSYNC`, `DRY_RUN`, immutable/swap/append files, files with CoW fork preallocations, realtime files with unusual extent sizes, quota exhaustion followed by blockgc, concurrent writes between start and commit, crash recovery of the logged exchange, and fsnotify/timestamp behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_exchrange.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_exchrange.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_exchrange.h

## Purpose
`xfs_exchrange.h` declares the internal representation and entry points for XFS file range exchange and commit-range support.

## Important APIs, types, and functions
The header defines private flag bits `__XFS_EXCHANGE_RANGE_UPD_CMTIME1`, `__XFS_EXCHANGE_RANGE_UPD_CMTIME2`, and `__XFS_EXCHANGE_RANGE_CHECK_FRESH2`, grouped in `XFS_EXCHANGE_RANGE_PRIV_FLAGS`. `struct xfs_exchrange` stores both `struct file` pointers, byte offsets, length, user-visible flags, and file2 freshness fields. It declares the three ioctl handlers, the inode lock/unlock helpers used by exchange-map code, and `xfs_exchrange_estimate`.

## Control flow
Callers build `struct xfs_exchrange` from ioctl arguments or scrub repair state and pass it to the implementation in `xfs_exchrange.c`. The private flags are set internally after VFS checks or commit-range freshness setup; they must not overlap public `XFS_EXCHANGE_RANGE_*` flags.

## State and persistence
The header owns no storage. Its private flags control transaction-time timestamp updates and freshness validation, which affect on-disk inode metadata only when the implementation commits an exchange.

## Dependencies and integration points
It depends on XFS transaction and inode types through forward declarations and is included by exchange-range implementation, exchange-map intent recovery, and scrub temporary-file repair code.

## Risks and test signals
The key risk is flag-space collision with user ABI flags, guarded by build-time checks in the implementation. Test signals are compile coverage of ioctl handlers, scrub repair exchange-map paths, and any future flag additions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_exchrange.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_export.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_export.c

## Purpose
`xfs_export.c` supplies XFS exportfs operations for NFS and pNFS. It encodes stable file handles, decodes file handles back to dentries or parents, looks up `..`, and forces inode metadata to the log for NFS commit semantics.

## Important APIs, types, and functions
The externally referenced object is `xfs_export_operations`. Helper `xfs_fileid_length` validates supported 32-bit and 64-bit inode filehandle layouts. `xfs_fs_encode_fh` emits either generic `struct fid` or packed `struct xfs_fid64` handles. `xfs_nfs_get_inode` resolves an inode number/generation pair. `xfs_fs_fh_to_dentry`, `xfs_fs_fh_to_parent`, `xfs_fs_get_parent`, and `xfs_fs_nfs_commit_metadata` implement exportfs callbacks.

## Control flow
Encoding chooses parent-bearing fileid types only when a parent inode is supplied, and adds `XFS_FILEID_TYPE_64FLAG` when the filesystem can expose 64-bit inode numbers. Decode checks that the supplied filehandle length is sufficient, extracts inode/generation fields, calls `xfs_nfs_get_inode`, and wraps the result with `d_obtain_alias`. `xfs_nfs_get_inode` uses `XFS_IGET_UNTRUSTED`, translates invalid/stale/corrupt inode references to `-ESTALE`, reloads incomplete unlinked state if necessary, rejects generation mismatches and private inodes, and returns a VFS inode.

## State and persistence
Filehandles persist outside the kernel as inode/generation identities plus optional parent identity. The code itself keeps no private state. `commit_metadata` persists pending inode metadata by forcing the inode log item.

## Dependencies and integration points
It integrates with Linux exportfs, NFS filehandle ABI, XFS inode cache, directory lookup, pNFS block export callbacks under `CONFIG_EXPORTFS_BLOCK_OPS`, and the handle ioctl code that reuses `xfs_nfs_get_inode`.

## Risks and test signals
Risks include stale handles after inode reuse, NFSv2 handle-size limits with 64-bit inodes and subtree checks, generation zero being valid rather than wildcard, unlinked-list reload failures forcing shutdown, and private inode exposure. Test signals include encode/decode with and without parent handles, 32-bit and 64-bit inode filesystems, stale generation lookup, invalid inode numbers, exported subdirectories with `fsid`, pNFS block callbacks, and metadata commit after NFS writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_export.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_export.h

## Purpose
`xfs_export.h` documents and declares the XFS NFS filehandle ABI, especially the 64-bit inode extension.

## Important APIs, types, and functions
It defines packed `struct xfs_fid64` with inode, generation, parent inode, and parent generation fields, plus `XFS_FILEID_TYPE_64FLAG` to tag 64-bit inode handles. It declares `xfs_nfs_get_inode`.

## Control flow
The header has no executable flow. `xfs_export.c` uses the layout and flag while encoding/decoding filehandles; handle ioctl code also uses the 64-bit fileid type to decode XFS handles through exportfs.

## State and persistence
The packed layout is wire-visible persistent ABI. The comment explains operational constraints for NFS exports of filesystems that may contain 64-bit inode numbers.

## Dependencies and integration points
It depends on VFS `struct inode`/`struct super_block` concepts and is included by XFS export and handle code.

## Risks and test signals
Risks are ABI incompatibility if the flag or struct layout changes and NFS deployments that export subdirectories on 64-bit inode filesystems without a suitable `fsid`. Test signals include compile-time layout use, NFS handle round trips, and compatibility with old clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_extent_busy.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_extent_busy.c

## Purpose
`xfs_extent_busy.c` tracks blocks that have been freed logically but whose freeing transactions are not yet durable or whose discard is in progress. This prevents immediate unsafe reallocation and coordinates allocation retries, log forcing, discard completion, and unmount waits.

## Important APIs, types, and functions
The private `struct xfs_extent_busy_tree` holds a spinlock, rb-tree, generation counter, and waitqueue per allocation group or realtime group. Public functions insert normal and discard busy extents, search for overlap, trim allocation candidates, reuse or clear busy ranges, flush/wait for busy extents, sort busy lists, test emptiness, and allocate the tree. The per-entry type and flags are declared in `xfs_extent_busy.h`.

## Control flow
Freeing code inserts a busy extent into the group rb-tree and a transaction/CIL list. Allocators call `xfs_extent_busy_search` or `xfs_extent_busy_trim` to detect overlap; trim returns a usable subrange and the current generation if busy extents forced a reduction. If an allocator decides to reuse a busy metadata extent, `xfs_extent_busy_reuse` walks overlaps and either shrinks/removes entries at the ends, delays for discard, or forces the log when splitting would be necessary. CIL checkpoint completion calls `xfs_extent_busy_clear`, which removes committed entries from rb-trees or marks them `DISCARDED` when discard must finish first. `xfs_extent_busy_flush` log-forces and then waits for the generation to change unless the current transaction holds unresolved busy extents, in which case it may return early or `-EAGAIN` to avoid deadlock.

## State and persistence
Busy extents are runtime state, keyed by group and block number, with held group references. They mirror transaction durability: once the freeing transaction is committed and optional discard handling completes, entries are removed, the generation counter increments, and waiters wake. No busy-tree state persists on disk; recovery reconstructs allocation safety from the log and metadata.

## Dependencies and integration points
It is used by `libxfs/xfs_alloc.c` allocation/freeing paths, `xfs_log_cil.c` checkpoint completion, scrub repair code, AG/rtgroup lifetime, tracepoints, and discard scheduling. Zoned realtime groups bypass busy tracking through the macro in the header because zone reset ordering supplies the needed safety.

## Risks and test signals
Risks include rb-tree/list consistency when entries are zero-length invalidated but still present on immutable transaction lists, deadlocks when a transaction waits on its own busy frees, reuse during discard, generation wakeups that do not guarantee emptiness, and allocation fragmentation from trim choices. Test signals include low-space allocation requiring log force, busy exact and partial overlap searches, discard and skip-discard paths, AGFL/userdata reuse behavior, fatal-signal interruption expectations, unmount waiting across AGs and rtgroups, and zoned realtime configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_extent_busy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_extent_busy.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_extent_busy.h

## Purpose
`xfs_extent_busy.h` defines the busy extent data structures and allocator-facing API used to protect recently freed blocks from unsafe reuse.

## Important APIs, types, and functions
`struct xfs_extent_busy` is the rb-tree/list node for a busy range, with group pointer, AG-relative block, length, and flags `XFS_EXTENT_BUSY_DISCARDED` and `XFS_EXTENT_BUSY_SKIP_DISCARD`. `struct xfs_busy_extents` groups related extents through discard completion. The header declares insertion, clearing, search, reuse, trim, flush, wait, list-empty, tree allocation, and list sort helpers.

## Control flow
Transactions append busy entries through `xfs_extent_busy_insert`; CIL or discard completion clears lists; allocation code probes, trims, flushes, or reuses ranges before handing blocks back out. `xfs_extent_busy_sort` groups list entries by group and block to let clear operations process them efficiently.

## State and persistence
The declared objects represent in-memory transaction and discard state only. The `owner` field of `struct xfs_busy_extents` defines who is freed after endio-style processing.

## Dependencies and integration points
It forward-declares XFS mount, group, and transaction types and uses Linux rbtrees, lists, work structs, and list sorting. `xfs_group_has_extent_busy` encodes the integration rule that zoned realtime groups do not need normal busy extent tracking.

## Risks and test signals
Risks include incorrect group type decisions, caller misuse of busy lists after transaction attachment, and missed discard-skip semantics. Test signals are allocation/freeing tests on data AGs, non-zoned rtgroups, zoned rtgroups, discard-enabled mounts, and low-space retry paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_extent_busy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_extfree_item.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_extfree_item.c

## Purpose
`xfs_extfree_item.c` implements extent-free intent/done log items and deferred operation types for freeing data, AGFL, and realtime extents. It guarantees that extent frees either complete or are replayed after crash recovery.

## Important APIs, types, and functions
It defines `xfs_efi_cache`, `xfs_efd_cache`, EFI/EFD item ops, log-space helpers, and defer op types `xfs_extent_free_defer_type`, `xfs_agfl_free_defer_type`, and `xfs_rtextent_free_defer_type`. Core routines allocate/format/release EFI and EFD log items, copy recovered 32/64/native log formats, add extents to intents/dones, finish normal and AGFL frees, process realtime frees, recover EFI work, relog intents, and consume recovered EFDs.

## Control flow
`xfs_extent_free_defer_add` computes and holds the destination group from the encoded startblock, selects the correct defer op, traces, and queues the item. Defer processing logs an EFI containing all extents, creates an EFD linked to the EFI, and processes each item. Normal frees call `__xfs_free_extent`, AGFL frees read AGF and call `xfs_free_ag_extent`, and realtime frees lock the rtgroup and call zoned or bitmap free helpers. Each successful or cancelled item is copied into the EFD and released. If a free returns `-EAGAIN`, the code copies the entire EFI into the EFD so the current intent is cancelled safely while a new intent is logged. Recovery reconstructs in-core EFIs from log records, validates each extent, queues deferred work, allocates a recovery transaction, finishes intents, and captures follow-on defer work.

## State and persistence
EFI items are persistent redo intents with two references: one for AIL insertion and one held until EFD completion. EFD items are persistent completion records that release matching EFI intents during recovery. Runtime state includes atomic next-extent slots, EFI reference counts, held group-intent references, defer pending lists, and optional rtgroup lock state. Recovered bad extents are treated as log corruption.

## Dependencies and integration points
The file connects the deferred-operation framework, transaction/log item machinery, AIL, log recovery, allocation btrees, reverse mapping owner info, busy extent insertion through lower free routines, realtime bitmap/rmap/refcount code, zoned allocator, and trace/error reporting. Transaction reservation code uses the exported log-space helpers.

## Risks and test signals
Risks include EFI/EFD reference imbalance, incomplete EFD cancellation during transaction roll, cross-architecture log format conversion, invalid recovered extent validation, mixing realtime and non-realtime intents, AGFL accounting differences, and CONFIG_XFS_RT disabled handling of realtime log items. Test signals include crash recovery between EFI and EFD, large extent counts beyond fast caches, `-EAGAIN` transaction roll, AGFL single-block frees, realtime bitmap and zoned frees, corrupt log item lengths, and relogging to push the log tail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_extfree_item.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_extfree_item.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_extfree_item.h

## Purpose
`xfs_extfree_item.h` declares the in-kernel EFI/EFD log item structures and APIs for deferred extent freeing.

## Important APIs, types, and functions
It defines `XFS_EFI_MAX_FAST_EXTENTS`, `struct xfs_efi_log_item`, `xfs_efi_log_item_sizeof`, `struct xfs_efd_log_item`, `xfs_efd_log_item_sizeof`, `XFS_EFD_MAX_FAST_EXTENTS`, cache externs, `xfs_extent_free_defer_add`, `xfs_efi_log_space`, and `xfs_efd_log_space`.

## Control flow
Allocation code creates `struct xfs_extent_free_item` objects and passes them to `xfs_extent_free_defer_add`; transaction and recovery code use the log item size helpers to allocate variable-length EFI/EFD objects and reserve log space.

## State and persistence
The structures contain the logged EFI/EFD format payloads, in-core log items, EFI reference state, and EFD backpointer to the EFI. Their embedded format records are what reach the journal.

## Dependencies and integration points
It depends on XFS log format definitions, transaction/defer infrastructure, and slab caches initialized elsewhere in XFS.

## Risks and test signals
Risks include variable-size allocation mistakes, fast-cache thresholds diverging from implementation, and misuse of EFI reference ownership documented in the header. Test signals include log-space reservation checks, large batch frees, recovery replay, and transaction cancellation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_extfree_item.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_file.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_file.c

## Purpose
`xfs_file.c` is the VFS file operation layer for XFS regular files and directories. It implements reads, writes, DAX faults, fsync, fallocate, reflink remap, directory reads, open/release heuristics, mmap setup, and file operation tables.

## Important APIs, types, and functions
Exported objects are `xfs_file_operations` and `xfs_dir_file_operations`; exported helper `xfs_is_falloc_aligned` checks allocation-unit alignment. Important flows are `xfs_file_read_iter`, `xfs_file_write_iter`, `xfs_file_fsync`, `xfs_file_fallocate`, `xfs_file_remap_range`, `xfs_file_open`, `xfs_file_release`, `xfs_file_llseek`, and `xfs_file_mmap_prepare`. Internal helpers separate buffered, DIO, DAX, zoned, unaligned, and atomic write paths, EOF zeroing, direct-I/O completion, mmap write faults, and fallocate modes.

## Control flow
Reads reject shutdown mounts, update stats, and dispatch to DAX, direct, buffered, or splice paths under `XFS_IOLOCK_SHARED`. Writes validate atomic constraints, choose DAX/direct/buffered/zoned paths, and use `xfs_file_write_checks` for generic limits, layout breakage, privilege removal needs, and post-EOF zeroing. Direct I/O enforces device-sector alignment, routes unaligned writes through overwrite-only/exclusive retry logic, routes zoned writes through space reservation and zone allocation, and routes atomic writes through hardware atomic or CoW fallback. DIO completion updates stats, completes CoW or unwritten conversion, and serializes EOF updates. Buffered writes retry once after quota/space cleanup. Fallocate takes IO/MMAP exclusive locks, drains DIO, calls file modification checks, and dispatches punch, collapse, insert, zero, unshare, or allocate-range helpers. Reflink remap uses reflink prep/remap/update helpers and syncs if either file requires it. Mmap faults use DAX or iomap page-mkwrite under MMAPLOCK and pagefault freeze protection.

## State and persistence
Persistent effects include file data writes, extent conversion, CoW completion, inode size updates, timestamp/security privilege changes, fallocate extent edits, reflink sharing, and log/device flushes for sync operations. Runtime state includes IO/MMAP lock modes, `XFS_ITRUNCATED` and `XFS_EOFBLOCKS_RELEASED`, zoned allocation contexts, DIO completion flags, i_size serialization with `i_flags_lock`, and stats counters. Release may flush delayed blocks after truncation and opportunistically free post-EOF preallocations.

## Dependencies and integration points
The file integrates VFS `file_operations`, iomap buffered/direct/DAX APIs, XFS iomap ops, reflink, CoW, zoned allocator, block device flushes, writeback, file leases, fadvise, directory readdir, ioctl handlers, pNFS, transparent hugepage unmapped-area helper, and trace/stats/error tags.

## Risks and test signals
Risks include IOLOCK demotion/upgrade races, unaligned direct-I/O zeroing corruption, EOF moving backward under AIO completion, DAX synchronous fault handling, zoned reservation accounting, atomic write fallback correctness, buffered write retry behavior under ENOSPC/EDQUOT, post-EOF preallocation heuristics, and fsync ordering across data/log/realtime devices. Test signals include NOWAIT read/write, DAX read/write/faults, direct unaligned writes to reflink files, atomic writes over one and multiple extents, zoned buffered and direct writes, fallocate all modes, collapse/insert alignment failures, remap partial results, fsync with separate log/rt devices, last-close EOF block cleanup, SEEK_DATA/SEEK_HOLE, and mmap write faults during remap/truncate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_file.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_file.h

## Purpose
`xfs_file.h` exposes XFS regular-file and directory VFS operation tables and a shared fallocate alignment helper.

## Important APIs, types, and functions
It declares `xfs_file_operations`, `xfs_dir_file_operations`, and `xfs_is_falloc_aligned`.

## Control flow
Mount/inode setup code uses the operation tables for regular files and directories. Fallocate and exchange-range related code can call the alignment helper before extent-moving operations.

## State and persistence
The header has no state. The declared operation tables drive all persistent file data and metadata changes implemented in `xfs_file.c`.

## Dependencies and integration points
It depends on VFS `struct file_operations` and XFS inode types and is included by file-operation implementation and inode setup paths.

## Risks and test signals
Risk is minimal; changes here alter the public internal contract for VFS integration. Test signals are build coverage and mount-time assignment of file and directory operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_filestream.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_filestream.c

## Purpose
`xfs_filestream.c` implements directory-to-allocation-group associations for filestream allocation. It tries to keep files created under the same directory in a chosen AG to improve streaming layout while avoiding AGs preferred for metadata unless space is tight.

## Important APIs, types, and functions
The main public functions are `xfs_filestream_select_ag`, `xfs_filestream_deassociate`, `xfs_filestream_mount`, and `xfs_filestream_unmount`. Private `struct xfs_fstrm_item` stores an MRU-cache element and referenced `struct xfs_perag`. Key helpers are `xfs_filestream_pick_ag`, `xfs_filestream_get_parent`, `xfs_filestream_lookup_association`, and `xfs_filestream_create_association`.

## Control flow
Allocation calls `xfs_filestream_select_ag`, which resolves the parent inode from a dentry alias, looks for an MRU association keyed by parent inode, and reuses it if the AG has enough longest free extent or the transaction is in low-space mode. If lookup fails or is unsuitable, creation removes an old association, chooses a start AG from the old AG or inode32 rotor, adjusts adjacent allocation hints, scans AGs for an unused and sufficiently free candidate, and inserts a new MRU entry. The picker tracks a fallback AG with the most free blocks, performs a second pass for skipped AGF locks, then a low-space pass, and finally may share the fullest AG if no unassociated AG is available.

## State and persistence
All filestream associations are runtime MRU-cache state under `mp->m_filestream`. Each association holds a perag active reference and increments `pagf_fstrms`; expiry or deletion decrements and releases the AG. No on-disk metadata records the association.

## Dependencies and integration points
It integrates with XFS bmap allocation arguments, perag reference counting, AG reservation/free-space queries, MRU cache infrastructure, inode32 AG rotor tuning, directory parent lookup through dentries, tracepoints, and the mount/unmount lifecycle.

## Risks and test signals
Risks include stale or missing parent aliases, AG reference leaks, contention around `pagf_fstrms`, overuse of metadata-preferred AGs, poor fallback behavior under low space, and MRU expiry races. Test signals include creating many files in one directory, deleting/renaming directories, inode32 rotor behavior, AGF lock contention returning `-EAGAIN`, low-space transactions, metadata-preferred AG filtering, mount/unmount cache teardown, and filestream deassociation during inode inactivation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_filestream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_filestream.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_filestream.h

## Purpose
`xfs_filestream.h` declares the filestream allocation API and the predicate for deciding if an inode should use filestream placement.

## Important APIs, types, and functions
It declares mount/unmount lifecycle functions, `xfs_filestream_deassociate`, `xfs_filestream_select_ag`, and inline `xfs_inode_is_filestream`, which checks the mount-wide feature or the inode `XFS_DIFLAG_FILESTREAM` bit.

## Control flow
Allocation code calls `xfs_inode_is_filestream` to decide whether to route through `xfs_filestream_select_ag`; inode teardown can call `xfs_filestream_deassociate`; mount setup/teardown initializes and destroys the MRU cache.

## State and persistence
The header has no state. It exposes the runtime association machinery implemented in `xfs_filestream.c`; the inode flag used by the predicate is persistent inode metadata.

## Dependencies and integration points
It forward-declares XFS mount, inode, bmalloc, and allocation argument types and is included by allocation and inode lifecycle code.

## Risks and test signals
Risks are incorrect predicate behavior when mount-wide and inode-level filestream settings interact. Test signals include mount option behavior, inherited inode flags, and allocation path selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_filestream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_fsmap.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_fsmap.c

## Purpose
`xfs_fsmap.c` implements `GETFSMAP` for XFS. It translates user fsmap keys into data/log/realtime device queries, enumerates reverse mappings or free-space records, fabricates gaps, reports sharing, and copies results back to userspace.

## Important APIs, types, and functions
The public entry point is `xfs_ioc_getfsmap`. Internal types are `struct xfs_getfsmap_info` for query state and `struct xfs_getfsmap_dev` for per-device handlers. Important helpers convert fsmap units/owners, validate keys/devices, format results, check shared extents, query data-device rmapbt or bnobt, query external log, query realtime bitmap or realtime rmapbt under `CONFIG_XFS_RT`, and run the top-level `xfs_getfsmap` device loop.

## Control flow
The ioctl copies and validates the header/reserved fields, allocates an internal buffer up to 128 KiB with page fallback, converts the two keys to internal basic-block units, and loops until the user buffer fills or the query finishes. `xfs_getfsmap` validates flags/devices/key ordering, enables rmap ownership only when rmapbt exists and the caller has `CAP_SYS_ADMIN`, installs data/log/rt handlers, sorts by device id, and calls handlers inside empty transactions for recursive buffer-lock protection. Data handlers convert low/high physical keys to AG-local rmap keys and iterate perags. Rmapbt handlers enumerate ownership; bnobt fallback enumerates free extents and reports unknown gaps. Realtime handlers perform analogous rtbitmap or rtrmapbt scans and handle zoned internal-rt synthetic regions. `xfs_getfsmap_helper` filters continuation records, emits gap records, converts owners/flags, checks refcount btrees for shared file data, and stops with `-ECANCELED` when the internal buffer is full.

## State and persistence
The code is read-only with respect to filesystem metadata. Runtime state tracks continuation low keys, next expected disk address, end address, current group, AGF buffer, and output counters. It does not persist state; userspace resumes by feeding the last returned record as the next low key.

## Dependencies and integration points
It integrates Linux `fsmap` ioctl ABI, XFS rmap/refcount/free-space btrees, realtime bitmap/rmap/refcount btrees, perag and rtgroup iterators, transaction buffer recursion, device encoding, capability checks, tracepoints, and ioctl dispatch.

## Risks and test signals
Risks include off-by-one continuation semantics, unit conversion between bytes/basic blocks/fsblocks/rtblocks, owner mapping of special owners, unprivileged fallback leaking too little or too much, synthetic gap correctness, shared-flag false positives/negatives, device ordering with internal realtime volumes, and memory buffer refill loops. Test signals include count-only mode, small user buffers forcing `-ECANCELED` refill, low key with nonzero length, CAP_SYS_ADMIN versus unprivileged output, filesystems with and without rmapbt/reflink/realtime/external log/zoned rt, invalid reserved fields, malformed owner/flag keys, and fatal signal interruption during long scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_fsmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_fsmap.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_fsmap.h

## Purpose
`xfs_fsmap.h` defines XFS-internal fsmap structures and declares the GETFSMAP ioctl handler.

## Important APIs, types, and functions
`struct xfs_fsmap` mirrors userspace `struct fsmap` in internal basic-block units. `struct xfs_fsmap_head` stores input flags, output flags, counts, and low/high keys. `struct xfs_fsmap_irec` represents an internal reverse-mapping record with disk address, length, owner, owner offset, rmap flags, and original rmapbt key. The header declares `xfs_ioc_getfsmap`.

## Control flow
The implementation converts userspace keys into these internal forms, scans device metadata, and converts the records back before copying results to userspace.

## State and persistence
The structures are temporary query state only and do not persist. They reflect durable reverse-map/free-space metadata read by `xfs_fsmap.c`.

## Dependencies and integration points
It depends on XFS block address types and Linux fsmap ABI types. It is used by ioctl and trace code.

## Risks and test signals
Risks are type-width and unit mismatches, especially physical/offset/length conversions. Test signals include compile coverage and GETFSMAP ABI round trips for large devices and high inode owner ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_fsmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_fsops.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_fsops.c

## Purpose
`xfs_fsops.c` implements filesystem-level operations: data/log growfs entry points, reserved block pool resizing, user-triggered shutdown, forced shutdown reporting, and per-AG/realtime metadata reservation setup and teardown.

## Important APIs, types, and functions
Public functions are `xfs_growfs_data`, `xfs_growfs_log`, `xfs_reserve_blocks`, `xfs_fs_goingdown`, `xfs_do_force_shutdown`, `xfs_fs_reserve_ag_blocks`, and `xfs_fs_unreserve_ag_blocks`. Internal helpers initialize new AG headers, perform data grow/shrink transaction work, reject unsupported log grow/move requests, and update `imaxpct`.

## Control flow
Data grow requires `CAP_SYS_ADMIN`, takes `m_growlock`, rejects internal-rt data size changes, optionally updates `imaxpct`, then grows or experimentally shrinks data blocks. Grow validates block count and device reachability, checks realtime geometry, computes AG deltas, initializes new perag structures, allocates a grow transaction, writes new AG headers non-transactionally before logging sb changes, extends or shrinks the last AG, updates superblock counters transactionally, commits synchronously, updates mount-side derived limits, reserves AG metadata blocks, recomputes rt btree maxlevels, updates secondary superblocks, and bumps mount generation. Log grow is permission/lock protected but returns `-ENOSYS` for actual movement/resizing. `xfs_reserve_blocks` changes per-counter reserve totals under `m_sb_lock`, moving unused reserves back or partially filling from free counters. Shutdown ioctls map user flags to log/device shutdown variants; `xfs_do_force_shutdown` atomically marks shutdown, shuts down the log, reports alerts, fserror, and healthmon events.

## State and persistence
Growfs persists superblock AG count, data block count, free block count, imaxpct, new AG headers, and secondary superblocks. Runtime state includes perag arrays, max inode count, low-space thresholds, allocation set-aside, mount generation, reserve pool counters, shutdown flags, and metadata reserve pools. Forced shutdown prevents further persistent writes after the first successful state transition.

## Dependencies and integration points
This file integrates ioctl dispatch, superblock validation/logging, AG header initialization, perag lifecycle, grow/shrink helpers, transaction reservations, allocation reservations, realtime geometry and btree sizing, block-device freeze/thaw, log shutdown, fserror, health monitor, and admin capability checks.

## Risks and test signals
Risks include partial grow after non-transactional header writes, unsupported shrink edge cases, secondary superblock update failures after live size change, reserve counter TOCTOU near ENOSPC, shutdown races, and metadata reservation failures forcing shutdown. Test signals include grow by extending last AG and adding new AGs, no-op grow, invalid block counts, internal realtime rejection, imaxpct-only updates, reserve increase/decrease under concurrent allocation, goingdown flag variants, repeated forced shutdown calls, AG reservation ENOSPC versus hard errors, and recovery after crash during growfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_fsops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_fsops.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_fsops.h

## Purpose
`xfs_fsops.h` declares the filesystem-level operation API used by ioctl and mount lifecycle code.

## Important APIs, types, and functions
It declares data/log growfs, reserve-block adjustment, filesystem going-down, AG metadata reserve initialization, and AG metadata reserve teardown functions.

## Control flow
Ioctl code calls growfs, reserve, and going-down functions; mount/remount paths call reservation helpers after geometry changes or during teardown.

## State and persistence
The header owns no state. Declared functions mutate durable superblock geometry and runtime reservation/shutdown state in `xfs_fsops.c`.

## Dependencies and integration points
It depends on `struct xfs_mount`, growfs ioctl structures, and `enum xfs_free_counter`.

## Risks and test signals
Risks are API signature drift with ioctl callers and mount code. Test signals are build coverage and ioctl exercises for growfs/reserve/goingdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_fsops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_globals.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_globals.c

## Purpose
`xfs_globals.c` defines global tunable defaults and miscellaneous global XFS behavior switches.

## Important APIs, types, and functions
It defines `xfs_params`, whose fields provide min/default/max values for panic mask, error level, sync daemon timer, stats clearing, inherited inode flags, rotor step, filestream timer, and blockgc timer. It also defines `xfs_globals`, with defaults for log recovery delay, mount delay, assert behavior, debug-only parallel work and logged-attribute replay switches, and btree bulk-load slack.

## Control flow
There are no functions. Sysctl and mount/runtime code read these global structures to clamp tunables and initialize behavior.

## State and persistence
The values are runtime globals. They do not persist on disk, though they influence persistent operations such as inherited inode flags, log recovery timing, and repair/btree build behavior.

## Dependencies and integration points
It includes XFS platform and error definitions and is consumed by sysctl setup, mount code, blockgc, filestream, error reporting, assertions, and debug paths.

## Risks and test signals
Risks include invalid min/default/max ranges, changing defaults in ways that affect performance or error handling, and debug-only fields diverging from users. Test signals include sysctl registration, mount under DEBUG and non-DEBUG builds, assert-fatal builds, and tunable boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_globals.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_handle.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_handle.c

## Purpose
`xfs_handle.c` implements XFS handle ioctls, privileged open/readlink-by-handle, legacy attribute list/multi operations by handle, and parent-pointer enumeration ioctls.

## Important APIs, types, and functions
Public functions include `xfs_find_handle`, `xfs_handle_to_dentry`, `xfs_open_by_handle`, `xfs_readlink_by_handle`, `xfs_ioc_attr_list`, `xfs_attrlist_by_handle`, `xfs_ioc_attrmulti_one`, `xfs_attrmulti_by_handle`, `xfs_ioc_getparents`, and `xfs_ioc_getparents_by_handle`. Helpers initialize filesystem/file handles, decode kernel/user handles to dentries or inodes, format attr list entries, map attr flags, perform attr get/set/remove, and format parent pointer records.

## Control flow
`xfs_find_handle` resolves either an fd or path, verifies an XFS regular file/directory/symlink, initializes an fs or file handle, and copies it to userspace. Handle decode requires a directory file as the authority and validates handle length before using exportfs or `xfs_nfs_get_inode`. `xfs_open_by_handle` requires `CAP_SYS_ADMIN`, restricts target types, applies append/immutable/directory-write checks, opens a new fd, and marks regular-file opens `O_NOATIME`/`FMODE_NOCMTIME`. `xfs_readlink_by_handle` similarly requires privilege and symlink target. Attribute list/multi paths copy legacy request arrays, decode the handle, allocate bounded buffers, filter namespaces, and perform attr get/set/remove with write-mount accounting. Parent enumeration requires parent-pointer feature and privilege, lists `XFS_ATTR_PARENT` records through the attr cursor, formats variable-length records with parent handles and names, expands the final record to fill the buffer, and copies records/request state back.

## State and persistence
Handles persist outside the kernel as fsid plus inode/generation. Attribute set/remove operations persist xattrs and may invalidate ACL cache for root namespace changes. Parent pointer reads are read-only, but corrupt parent attr decode marks the inode sick. Runtime state includes copied request buffers, attr cursors, per-call kernel output buffers, held dentries/inodes, and mount write references.

## Dependencies and integration points
It integrates with XFS export/NFS inode lookup, Linux path/fd/open helpers, xattr and parent-pointer subsystems, ACL cache, health marking, ioctl dispatch, privilege checks, usercopy, and VFS readlink/open semantics.

## Risks and test signals
Risks include exposing handle operations without proper privilege, stale handle generation, non-directory authority files, user buffer overflow/short-buffer handling, attr namespace flag conflicts, immutable/append enforcement, parent pointer corruption loops, and cursor continuation correctness. Test signals include all handle-generating ioctls, open/readlink by stale and valid handles, regular/dir/symlink and rejected special files, attrlist cursor continuation, attrmulti mixed success/error array reporting, root/secure/user namespace filters, parent list small-buffer `-EMSGSIZE`, root-directory parent flag, getparents by handle without exportfs dentry connection, and corruption marking on malformed parent attrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_handle.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_handle.h

## Purpose
`xfs_handle.h` declares the handle, by-handle attribute, and parent-pointer ioctl helpers implemented in `xfs_handle.c`.

## Important APIs, types, and functions
It declares attrlist/attrmulti by handle, path/fd-to-handle conversion, open/readlink by handle, single attrmulti operation, attr list on an inode, user handle-to-dentry decode, and getparents ioctl handlers.

## Control flow
`xfs_ioctl.c` dispatches legacy XFS handle and parent-pointer ioctls to these functions. Other XFS code can decode handles to dentries through the declared helper.

## State and persistence
The header owns no state. The declared functions work with persistent fsids, inode generation handles, xattrs, and parent pointer attributes.

## Dependencies and integration points
It depends on XFS ioctl ABI structures, VFS file/inode/dentry types, and user pointer annotations.

## Risks and test signals
Risks are ABI signature changes that break ioctl dispatch or compat paths. Test signals are build coverage and ioctl coverage for all declared operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_handle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_health.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_health.c

## Purpose
`xfs_health.c` tracks runtime health state for filesystem-wide, per-group, per-rtgroup, and per-inode metadata. It records sick/corrupt/healthy transitions, reports errors to fsnotify/fserror and health monitors, maps internal sick masks to ioctl-visible masks, and warns at unmount about unfixed corruption.

## Important APIs, types, and functions
Public functions mark and measure fs, AG, rtgroup, group, inode, bmap, btree, dir/attr, and da-state sickness; fill health fields in geometry and bulkstat outputs; and translate masks for health monitor events. Internal tables map `XFS_SICK_*` bits to `XFS_FSOP_GEOM_*`, `XFS_AG_GEOM_*`, `XFS_RTGROUP_GEOM_*`, and `XFS_BS_SICK_*` ABI bits.

## Control flow
Mark-sick functions assert valid masks, take the relevant spinlock, OR sick bits, optionally set checked bits for corrupt/fsck-observed state, report metadata errors, and emit healthmon events with old and changed masks. Mark-healthy functions clear requested sick bits, clear secondary bits when no primary bits remain, set checked bits, and report healthy events. Measure functions sample sick/checked masks under locks. Unmount scans all perags and rtgroups plus fs-level masks, warns if unfixed corruption remains, and special-cases sick summary counters so repair guidance does not conflict with deliberate dirty-log recovery. Geometry/bulkstat helpers sample health state and translate internal masks to ioctl fields.

## State and persistence
Health state is in-memory in `mp->m_fs_sick/m_fs_checked`, `xg->xg_sick/xg_checked`, and `ip->i_sick/i_checked`. It does not directly persist as a standalone structure, but it reflects detected persistent metadata problems and influences unmount logging and user-visible health queries. Sick inodes are kept out of `I_DONTCACHE` so reports are not lost prematurely.

## Dependencies and integration points
It integrates with scrub and repair health updates, btree/dir/attr corruption detection, fserror/fsnotify reporting, health monitor event delivery, bulkstat and geometry ioctls, AG/rtgroup iterators, inode lifecycle, quota and realtime health masks, and tracepoints.

## Risks and test signals
Risks include lost health reports from inode reclaim, incorrect primary/secondary clearing, mismatched internal-to-ABI mask translation, reporting metadata inodes to file-level fserror incorrectly, health monitor event masks missing bits, and unmount behavior around sick counters. Test signals include marking sick/corrupt/healthy for fs/group/inode, scrub clearing health, btree sick marking for bmap and non-ephemeral btrees, dir/attr sick marking, bulkstat and geometry sick/checked outputs, rtgroup health reporting, unmount warning paths, shutdown suppression, and health monitor event verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_health.c -->
