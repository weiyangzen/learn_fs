# subset-b-005797 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_inode_item_recover.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_inode_item_recover.c

Purpose: implements log-recovery handling for inode log items. It registers `xlog_inode_item_ops` for `XFS_LI_INODE`, readaheads logged inode buffers during pass 2, verifies logged inode cores and forks, replays them into on-disk dinodes, performs swapext owner repairs, recalculates CRCs, and queues modified buffers for delayed writeback.

Important APIs and functions: `xlog_recover_inode_ra_pass2` issues inode-buffer readahead from the logged inode format. `xlog_recover_inode_commit_pass2` is the main replay routine. `xfs_log_dinode_to_disk`, `xfs_log_dinode_to_disk_ts`, and `xfs_log_dinode_to_disk_iext_counters` translate log-endian/runtime dinode fields into disk dinode fields, including bigtime and 64-bit extent-count formats. `xlog_dinode_verify_extent_counts` rejects inconsistent or unsupported extent counters. `xlog_recover_inode_dbroot` converts logged btree roots for normal data BMBT and metadata btrees. `xfs_recover_inode_owner_change` instantiates a temporary `xfs_inode` directly from the recovered dinode to change BMBT owners without transactions.

Control flow: recovery converts legacy 32-bit inode log formats when necessary, skips replay if the inode buffer was cancelled, reads the inode cluster, verifies disk and log magic, compares disk LSN or v2 flush iteration to decide whether replay is stale, validates mode-specific fork formats and fork offsets, copies the core and optional data/attr fork regions, optionally performs owner-change repair, then validates and CRCs the final dinode before queuing the buffer.

State and persistence: this file mutates persistent inode cluster buffers during log replay. It writes the current recovery LSN into v3 dinodes instead of trusting the logged LSN, updates device numbers and fork payloads, and logs no new transactions because recovery uses the supplied delayed-write buffer list.

Dependencies and integration: it depends on log recovery, inode verifier, buffer, bmap btree, realtime metadata btree, and transaction-private helpers. The owner-change path is tightly coupled to extent swap recovery and CRC-enabled inode owner semantics.

Risks and test signals: corruption checks protect against bad magic, impossible extent counts, unsupported large counts, invalid fork formats, oversized log records, bad fork offsets, and post-replay verifier failures. Tests should include crash replay of inode core/fork updates, v2 flushiter skip behavior, v3 LSN ordering, swapext owner changes, bigtime and nrext64 inodes, cancelled inode buffers, and malformed log records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_inode_item_recover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_ioctl.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_ioctl.c

Purpose: implements the native XFS file ioctl entry point and the helpers behind filesystem geometry, bulk inode reporting, file attributes, extent maps, labels, reserved blocks, growth, shutdown, scrub, handle, exchange-range, health, and media verification operations.

Important APIs and functions: exported helpers include `xfs_file_ioctl`, `xfs_ioc_swapext`, `xfs_fileattr_get`, `xfs_fileattr_set`, `xfs_fsbulkstat_one_fmt`, and `xfs_fsinumbers_fmt`. Bulk request handling is split between legacy `xfs_ioc_fsbulkstat`, v5 `xfs_ioc_bulkstat`, v5 `xfs_ioc_inumbers`, and `xfs_bulk_ireq_setup`/`teardown`. Geometry helpers include `xfs_ioc_fsgeometry`, `xfs_ioc_ag_geometry`, and `xfs_ioc_rtgroup_geometry`. File-attribute mutation is decomposed into validation helpers for xflags, DAX, extent size, CoW extent size, project id, transaction allocation, and commit. `xfs_ioc_getbmap`, label helpers, EOF-block conversion, reserved-block handling, and fs-count reporting serve the corresponding switch cases.

Control flow: `xfs_file_ioctl` traces the call, converts `p` to a user pointer, and dispatches by ioctl number. Read-only or information ioctls copy data out directly; mutating paths check capability, shutdown/read-only state, and use `mnt_want_write_file` around filesystem changes. User ABI handling consistently copies fixed headers in, validates flags/reserved fields, calls XFS internal APIs, and copies output headers/results back.

State and persistence: persistent changes include file xflags/project/extent hints through logged inode transactions, superblock labels with primary and backup superblock writes plus block-device invalidation, reserved block counters, growfs changes, shutdown state, error injection state, blockgc EOF trimming, extent exchange/commit operations, and scrub/health side effects.

Dependencies and integration: this is the ioctl bridge from VFS to XFS subsystems: bulkstat/inumbers, iwalk, fsops/growfs, rtgroups/zoned realtime geometry, quota, bmap, fsmap, scrub, handles, attrs, reflink/exchange range, health monitor, media verification, and fileattr VFS hooks.

Risks and test signals: user pointer handling, flag validation, capability checks, idmapped mount behavior in bulkstat backends, DAX flag cache invalidation, realtime extent hint validation, project quota transitions, label update ordering, and write-mount bracketing are primary risk areas. Tests should cover native ioctl ABI structs, legacy and v5 bulkstat cursors, AG-only bulkstat, metadata-directory filtering, set/get fsxattr validation, label persistence across remount, growfs permission checks, shutdown/error injection gating, and malformed reserved fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_ioctl.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_ioctl.h

Purpose: declares the native ioctl-facing XFS APIs shared by file operations, compat ioctl handling, and bulk inode formatting code.

Important APIs and types: it forward-declares `struct xfs_bstat`, `struct xfs_ibulk`, and `struct xfs_inogrp`. It exposes `xfs_ioc_swapext` for extent swapping, `xfs_fileattr_get` and `xfs_fileattr_set` for VFS fileattr integration, `xfs_file_ioctl` and `xfs_file_compat_ioctl` as ioctl entry points, and the legacy formatter helpers `xfs_fsbulkstat_one_fmt` and `xfs_fsinumbers_fmt`.

Control flow: the header itself has no runtime flow, but it defines the handoff points. VFS file operations call `xfs_file_ioctl`; compat dispatch calls `xfs_file_compat_ioctl`; compat code can reuse native bulkstat formatters when native layout is appropriate, such as x32 ABI handling.

State and persistence behavior: no state is stored here. The declared APIs may mutate filesystem state through swapext, file attribute changes, labels, growfs, and other ioctl operations implemented in `xfs_ioctl.c`.

Dependencies and integration: consumers need XFS and VFS types already visible from surrounding includes. This header links ioctl code to inode operations (`fileattr_get/set`), file operations (`ioctl/compat_ioctl`), and itable formatting.

Risks and test signals: ABI stability depends on keeping prototypes synchronized with implementations and avoiding type drift in formatter callbacks. Build coverage with native and compat ioctl enabled is the main signal; runtime coverage comes from fileattr, swapext, and bulkstat ioctl tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_ioctl32.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_ioctl32.c

Purpose: translates 32-bit and special x32 ioctl ABIs into native XFS operations so compat userspace can use legacy XFS ioctls safely on 64-bit kernels.

Important APIs and functions: `xfs_file_compat_ioctl` is the compat entry point. Alignment-specific helpers under `BROKEN_X86_ALIGNMENT` translate v1 geometry and growfs structs. `xfs_ioctl32_bstime_copyin`, `xfs_ioctl32_bstat_copyin`, `xfs_bstime_store_compat`, and `xfs_fsbulkstat_one_fmt_compat` convert time and bstat layouts. `xfs_compat_ioc_fsbulkstat` handles legacy 32-bit bulkstat/inumbers requests. `xfs_compat_handlereq_copyin`, `xfs_compat_attrlist_by_handle`, and `xfs_compat_attrmulti_by_handle` translate handle and attr-by-handle requests.

Control flow: compat dispatch handles known layout-changing ioctls explicitly, performs pointer conversion with `compat_ptr`, copies compact structs field by field, brackets mutating growfs and swapext paths with `mnt_want_write_file`, and delegates unchanged commands to native `xfs_file_ioctl`. For x32, bulk request pointers are compat-width while output records may use native layout, so the formatter selection is adjusted dynamically.

State and persistence: this file does not implement independent persistent operations; it delegates to native growfs, swapext, handle, attr, bulkstat, and ioctl functions after ABI translation. Persistent effects are therefore the same as native operations.

Dependencies and integration: depends on native ioctl helpers, itable formatters, fsops, attrs, handles, compat user accessors, and architecture layout macros. It must match the compat structs and ioctl numbers in `xfs_ioctl32.h`.

Risks and test signals: field-by-field translations are ABI-sensitive. The `xfs_ioctl32_bstat_copyin` path is especially risky because incorrect source fields corrupt swapext validation. Tests should exercise 32-bit bulkstat, fsinumbers, swapext, handle ioctls, attrlist/attrmulti by handle, x86 packed geometry/growfs, x32 formatter selection, invalid user pointers, overflowed attr op counts, and fallback to native ioctl for unchanged commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_ioctl32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_ioctl32.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_ioctl32.h

Purpose: defines the 32-bit compat XFS ioctl structures and ioctl numbers whose layout differs from native kernel structures.

Important APIs and types: key types include `compat_xfs_bstime_t`, packed `struct compat_xfs_bstat`, `struct compat_xfs_fsop_bulkreq`, `compat_xfs_fsop_handlereq_t`, packed `struct compat_xfs_swapext`, compat attrlist and attrmulti handle request structs, and x86-specific packed geometry/growfs/inogrp structs. It defines compat ioctl numbers such as `XFS_IOC_FSBULKSTAT_32`, `XFS_IOC_FSINUMBERS_32`, handle ioctls, `XFS_IOC_SWAPEXT_32`, and x86 alignment variants.

Control flow: no executable flow exists here; `xfs_ioctl32.c` switches on these constants and copies these layouts to native structs before delegation.

State and persistence behavior: the header stores no state. Its definitions control how compat userspace describes persistent operations such as growfs, swapext, handle open/readlink, and attr mutation.

Dependencies and integration: integrates with Linux compat pointer and time types. `BROKEN_X86_ALIGNMENT` is selected on `CONFIG_X86_64`, forcing packed structures for historical x86 ABI compatibility. The structure definitions must remain synchronized with old userspace expectations and with native conversion code.

Risks and test signals: padding, packing, pointer width, and 32-bit time truncation are the main risks. Build tests should cover `CONFIG_COMPAT`, `CONFIG_X86_64`, and x32. Runtime tests should compare native and 32-bit ioctl outputs for bulkstat/inumbers and validate swapext/handle/attr operations from a 32-bit test binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_ioctl32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_iomap.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_iomap.c

Purpose: implements XFS mappings for the Linux iomap layer. It converts XFS bmbt records to `struct iomap`, allocates blocks for direct and buffered writes, handles delayed allocation, unwritten extent conversion, reflink/CoW, DAX, zoned realtime writes, seek/fiemap/read mappings, xattr mappings, zeroing, and truncate-page operations.

Important APIs and functions: exported operations include `xfs_iomap_write_ops`, `xfs_direct_write_iomap_ops`, `xfs_zoned_direct_write_iomap_ops`, `xfs_atomic_write_cow_iomap_ops`, `xfs_dax_write_iomap_ops`, `xfs_buffered_write_iomap_ops`, `xfs_read_iomap_ops`, `xfs_seek_iomap_ops`, and `xfs_xattr_iomap_ops`. Core helpers include `xfs_iomap_inode_sequence`, `xfs_iomap_valid`, `xfs_bmbt_to_iomap`, `xfs_iomap_write_direct`, `xfs_iomap_write_unwritten`, `xfs_iomap_prealloc_size`, `xfs_bmapi_reserve_delalloc`, `xfs_direct_write_iomap_begin`, `xfs_buffered_write_iomap_begin`, `xfs_zoned_buffered_write_iomap_begin`, and `xfs_atomic_write_cow_iomap_begin`.

Control flow: read/seek/xattr paths lock, read extent maps, optionally trim around shared extents, create iomaps, and unlock. Direct writes decide whether a mapping needs allocation or CoW, reject NOWAIT/overwrite/atomic cases that cannot be satisfied, allocate or convert blocks transactionally, and return source maps for CoW. Buffered writes reserve delalloc in data or CoW forks, merge delayed extents, apply EOF speculative preallocation and low-space/quota throttling, and punch failed new delalloc ranges in `iomap_end`. Zoned paths reserve anonymous writes or CoW delalloc against zone allocation contexts.

State and persistence: persistent state changes occur through bmap transactions for direct allocation and unwritten conversion; buffered writes mostly reserve in-core delayed allocation and quota/block counters until writeback. Sequence cookies from data/attr/CoW forks detect stale iomaps. DAX zeroes blocks before commit where required. Truncate and zero helpers route through iomap or DAX paths while callers hold IO/MMAP locks.

Dependencies and integration: integrates with iomap core, XFS bmap, transactions, quota, reflink, realtime groups, zone allocation, inode forks, page cache dirty-folio scanning, block integrity, DAX, and stats/trace/error-tag systems.

Risks and test signals: the highest risks are stale iomap validation, block-zero corruption detection, CoW/data fork overlap, delalloc accounting rollback, quota throttling, atomic write alignment, DAX unwritten conversion, zoned short writes, and EOF zeroing crash consistency. Test with generic xfstests covering buffered/direct/DAX writes, reflink CoW, zero/unshare, NOWAIT, overwrite-only, atomic writes, ENOSPC/EDQUOT throttling, zoned realtime writes, seek hole/data, fiemap/xattr iomap, and induced stale-map races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_iomap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_iomap.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_iomap.h

Purpose: declares the XFS iomap interface used by file I/O, truncation, zeroing, DAX, reflink, and xattr mapping paths.

Important APIs and types: it forward-declares `struct xfs_inode`, `struct xfs_bmbt_irec`, and `struct xfs_zone_alloc_ctx`. It exposes direct allocation (`xfs_iomap_write_direct`), unwritten conversion (`xfs_iomap_write_unwritten`), EOF alignment (`xfs_iomap_eof_align_last_fsb`), sequence-cookie generation (`xfs_iomap_inode_sequence`), bmbt-to-iomap conversion (`xfs_bmbt_to_iomap`), zero/truncate helpers, and all exported `struct iomap_ops` plus `xfs_iomap_write_ops`.

Control flow: callers select an operation table appropriate to read, seek, buffered write, direct write, DAX write, xattr, zoned direct write, or software atomic CoW write. The inline `xfs_aligned_fsb_count` expands a file-block count to cover an extent-size alignment boundary.

State and persistence behavior: no state is stored in the header. Declared functions can reserve delayed blocks, allocate persistent blocks, convert unwritten extents, and update fork sequence counters indirectly through bmap operations.

Dependencies and integration: includes Linux `iomap.h` and assumes XFS block/offset typedefs are already available. It is a contract between `xfs_iomap.c` and higher-level XFS file, inode, reflink, and truncate code.

Risks and test signals: prototype mismatches can break many I/O modes. Coverage should include all exported operation tables under configs with and without realtime/zoned/DAX/reflink support, plus alignment helper edge cases with zero and non-power-of-two extent hints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_iomap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_iops.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_iops.c

Purpose: implements XFS VFS inode operations, inode initialization, security/ACL setup, namespace operations, getattr/setattr, fiemap, lazy time updates, DAX flag setup, and operation-table assignment.

Important APIs and functions: exported functions include `xfs_inode_init_security`, `xfs_vn_setattr_size`, `xfs_diflags_to_iflags`, `xfs_setup_inode`, `xfs_setup_iops`, and atomic write size reporters. Namespace operations are handled by `xfs_generic_create`, `xfs_vn_create`, `xfs_vn_mknod`, `xfs_vn_mkdir`, `xfs_vn_lookup`, `xfs_vn_ci_lookup`, `xfs_vn_link`, `xfs_vn_unlink`, `xfs_vn_symlink`, `xfs_vn_rename`, and `xfs_vn_tmpfile`. Attribute/stat paths include `xfs_vn_getattr`, `xfs_setattr_nonsize`, `xfs_vn_setattr`, `xfs_vn_update_time`, `xfs_vn_sync_lazytime`, and `xfs_vn_fiemap`.

Control flow: create paths prepare ACLs/security expectations, call XFS create helpers, initialize security xattrs and ACLs, assign iops/fops, instantiate dentries, and clean up on post-create failure. Setattr splits size changes from non-size changes. Size changes break layouts, hold IO/MMAP locks, zero exposed ranges, truncate page cache before transactions, log disk size before freeing blocks, and handle zoned reservations. Non-size changes allocate quotas before transactions, update dquots and inode core, then adjust ACLs after mode changes. Lookup, link, unlink, symlink, rename, and tmpfile operations translate dentries to `xfs_name` and delegate to directory core code.

State and persistence: persistent mutations include inode creation/removal/link counts, directory entries, symlink contents, mode/uid/gid/timestamps, disk size, extent truncation, inode flags, ACL/security xattrs, and logged time updates. `xfs_setup_inode` initializes VFS inode state from XFS state, including page-cache GFP constraints, private metadata inode flags, lock classes, stable writes, and no-xattr/no-acl caches.

Dependencies and integration: bridges VFS inode operations to XFS directory, attr, quota, transaction, bmap, iomap, symlink, file, ACL, security, DAX, and zone allocation subsystems. Operation tables connect regular files, directories, case-insensitive directories, symlinks, and special files to VFS.

Risks and test signals: crash consistency around truncate, zeroing before file extension, ACL/security rollback, idmapped ownership changes, quota chown, DAX enablement, metadata inode privacy, case-insensitive lookup dentries, and tmpfile nlink handling are key risks. Test with xfstests for create/unlink/rename/link/symlink/tmpfile, SELinux/ACL failure rollback, truncate up/down across block boundaries, lazytime sync, statx DIO/atomic reporting, idmapped mounts, reflink/CoW alignment, DAX mount modes, and zoned truncate ENOSPC paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_iops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_iops.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_iops.h

Purpose: declares inode-operation helpers shared outside `xfs_iops.c`, primarily for inode setup, setattr, security initialization, listxattr, and atomic write reporting.

Important APIs and types: it forward-declares `struct xfs_inode` and declares `xfs_vn_listxattr`, `xfs_vn_setattr_size`, `xfs_inode_init_security`, `xfs_setup_inode`, `xfs_setup_iops`, `xfs_diflags_to_iflags`, `xfs_get_atomic_write_min`, `xfs_get_atomic_write_max`, and `xfs_get_atomic_write_max_opt`.

Control flow: this header does not execute code. It defines external call points for VFS-facing and inode-cache code that need to initialize or mutate VFS inode state and query atomic write limits.

State and persistence behavior: no direct state is stored here. Declared functions can initialize VFS inode fields, set persistent inode size, create security xattrs, and report derived device/filesystem limits.

Dependencies and integration: integrates inode cache setup, VFS setattr/listxattr paths, file/stat code, security hooks, and atomic write reporting. It depends on surrounding includes to provide Linux inode, dentry, iattr, idmap, and qstr types.

Risks and test signals: the header is small, so risks are mostly stale declarations and config-dependent type visibility. Build coverage across security, ACL, DAX, and atomic-write configurations plus runtime statx/setattr tests exercise the exported surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_iops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_itable.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_itable.c

Purpose: implements bulk inode stat and inode-number table export. It walks allocated inode records, formats `struct xfs_bulkstat` or `struct xfs_inumbers`, advances request cursors, and delegates userspace formatting to caller-supplied callbacks.

Important APIs and functions: public entry points are `xfs_bulkstat_one`, `xfs_bulkstat`, `xfs_bulkstat_to_bstat`, `xfs_inumbers`, and `xfs_inumbers_to_inogrp`. Internal helpers include `xfs_bulkstat_one_int`, `xfs_bulkstat_iwalk`, `xfs_bulkstat_already_done`, `xfs_inumbers_walk`, and `want_metadir_file`.

Control flow: bulkstat allocates a temporary buffer and empty transaction, then stats either one inode or walks inode btree records through `xfs_iwalk`. `xfs_bulkstat_one_int` igets each inode with untrusted/dontcache flags, reloads incomplete unlinked buckets when needed, skips freed/private/superblock inodes unless metadata-directory output was requested, fills ownership/timestamps/extent/health/block fields, calls the formatter, and advances `startino` unless a runtime error must be replayed to userspace. Inumbers walks inobt records via `xfs_inobt_walk`, formats chunk start/count/free-mask data, and advances by `XFS_INODES_PER_CHUNK`.

State and persistence: normally read-only, but it can reload incomplete unlinked-list state and force shutdown on unrecoverable in-core corruption. It reads inode core/fork state, delayed block counts, health bits, and inobt allocation records. Request state (`startino`, `ocount`, `ubuffer`) is advanced in memory.

Dependencies and integration: depends on iwalk/inobt traversal, inode cache, quota/idmap ownership translation, health reporting, and ioctl formatters. Native and compat ioctls pass formatter callbacks that copy results to userspace ABI layouts.

Risks and test signals: cursor advancement must avoid duplicates or skipped inodes across calls, private metadata leakage must be prevented, idmapped mounts are rejected, formatter `-ECANCELED` must be hidden from userspace, and stale inobt records must not crash the walk. Tests should cover single and bulk modes, buffer-full restarts, AG-limited requests, metadata directory flag behavior, nrext64 flag behavior, idmapped mount rejection, freed inode races, and inumbers chunk masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_itable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_itable.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_itable.h

Purpose: defines the in-memory bulk inode request contract and callback types used by bulkstat and inumbers implementations.

Important APIs and types: `struct xfs_ibulk` stores mount, idmap, user buffer pointer, start inode cursor, requested count, output count, bulk flags, and iwalk flags. Flags include `XFS_IBULK_NREXT64` to request 64-bit extent counts and `XFS_IBULK_METADIR` to expose metadata-directory records. `xfs_ibulk_advance` advances the user buffer and returns `-ECANCELED` when the caller-provided output count is full. Callback typedefs are `bulkstat_one_fmt_pf` and `inumbers_fmt_pf`. Public functions mirror `xfs_itable.c`.

Control flow: callers initialize `xfs_ibulk`, choose formatter callbacks, and call `xfs_bulkstat_one`, `xfs_bulkstat`, or `xfs_inumbers`. Formatters call `xfs_ibulk_advance` after copying one record out.

State and persistence behavior: the header has no persistent state. `xfs_ibulk` is mutable per-request cursor state, and its `startino`/`ocount` fields are the basis for resumable ioctl calls.

Dependencies and integration: used by native ioctl, compat ioctl, and inobt walk code. The callback contract deliberately separates kernel collection from ABI-specific copyout.

Risks and test signals: incorrect advancement sizes corrupt userspace buffers or cursor semantics; missing `-ECANCELED` handling can leak internal stop codes. Tests should verify exact output counts, restart cursors, legacy/native/compat record sizes, nrext64, metadir filtering, and inumbers formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_itable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_iunlink_item.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_iunlink_item.c

Purpose: implements the transaction log item used to update an inode dinode's `di_next_unlinked` pointer during unlinked-list maintenance while preserving correct inode-cluster buffer logging order.

Important APIs and functions: `xfs_iunlink_log_inode` allocates and attaches an `xfs_iunlink_item` to a transaction. Internal item operations include `xfs_iunlink_item_release`, `xfs_iunlink_item_sort`, `xfs_iunlink_log_dinode`, and `xfs_iunlink_item_precommit`. `xfs_iunlink_cache` is the slab cache for these log items.

Control flow: callers request a next-agino update for an inode. The function verifies old and new AG inode values, rejects non-null self-links, allocates a log item, records the inode, per-AG reference, old pointer, and new pointer, joins it to the transaction, marks it dirty, and returns. During transaction precommit, the item maps the inode cluster buffer, skips stale buffers, verifies the on-disk old pointer still matches the expected value, writes the new pointer, recalculates the dinode CRC, logs only the field range, removes itself from the transaction, and releases resources.

State and persistence: this file updates persistent `di_next_unlinked` fields in inode cluster buffers as part of transaction commit. It holds a passive perag reference until release and intentionally avoids relogging stale inode buffers because doing so could clear stale state during inode cluster freeing.

Dependencies and integration: integrates with XFS transaction log items, inode mapping, per-AG lifetime management, dinode verifiers/CRC, tracepoints, and unlinked-list code that tracks `ip->i_next_unlinked`.

Risks and test signals: list corruption risk is managed by old-pointer verification and self-link rejection. Stale-buffer handling is delicate because relogging a stale cluster can resurrect freed metadata. Tests should cover unlink/inactive transactions, unlinked-list recovery, inode cluster freeing, corrupted old pointer detection, null termination, perag lifetime, and transaction precommit ordering across multiple inode clusters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_iunlink_item.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_iunlink_item.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_iunlink_item.h

Purpose: declares the in-memory log item used for transactional unlinked-list pointer updates.

Important APIs and types: `struct xfs_iunlink_item` embeds `struct xfs_log_item` and stores the target inode, held per-AG pointer, new `next_agino`, and expected `old_agino`. It declares the slab cache `xfs_iunlink_cache` and the entry point `xfs_iunlink_log_inode`.

Control flow: no code executes here. Transactions that manipulate unlinked inode lists call `xfs_iunlink_log_inode`, which creates an item whose precommit callback updates the dinode field.

State and persistence behavior: the struct is transient transaction state that drives persistent updates to `di_next_unlinked`. Its old/new AG inode fields are also consistency guards.

Dependencies and integration: depends on transaction, inode, perag, log item, and `xfs_agino_t` definitions supplied by including code. It is consumed by inode unlink/inactivation code and implemented by `xfs_iunlink_item.c`.

Risks and test signals: ABI is internal, but field ordering and lifetime matter for log item operations. Build coverage plus unlink/recovery tests that allocate and free iunlink items validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_iunlink_item.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_iwalk.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_iwalk.c

Purpose: provides generic inode and inode-btree record walkers for XFS. It traverses allocation groups in inode-number order, caches inobt records outside AGI locks, performs inode cluster readahead, supports resumable starts, and optionally parallelizes by AG.

Important APIs and functions: public entry points are `xfs_iwalk`, `xfs_iwalk_threaded`, and `xfs_inobt_walk`. Internal machinery is centered on `struct xfs_iwalk_ag`, `xfs_iwalk_ag_start`, `xfs_iwalk_ag`, `xfs_iwalk_run_callbacks`, `xfs_iwalk_ag_recs`, `xfs_iwalk_args`, `xfs_iwalk_prefetch`, and `xfs_inobt_walk_prefetch`. `xfs_iwalk_ichunk_ra` prefetches inode clusters; `xfs_iwalk_adjust_start` masks inodes before the requested start within the first record.

Control flow: setup computes a prefetch record count, allocates a record cache, and iterates per-AG objects from the start AG. For each AG, it opens the AGI/inobt cursor at or before the requested agino, caches records, skips empty chunks when requested, records forward progress, and when the cache fills, tears down the cursor and AGI buffer before invoking callbacks. After callbacks, it recreates the cursor at the next record. Threaded mode creates one work item per AG with its own empty transaction and perag hold.

State and persistence: the walker is read-oriented and does not itself change persistent metadata. It reads AGI/inobt records, may readahead inode cluster buffers, owns temporary empty transactions for recursive buffer-lock detection, and tracks in-memory cursor state such as `startino`, `lastino`, `nr_recs`, and abort flags.

Dependencies and integration: used by bulkstat/inumbers, scrub-like scans, and other inode iteration users. It depends on perag iteration, inobt btree cursors, transaction buffer handling, parallel work control, inode buffer ops, and corruption health marking.

Risks and test signals: key risks are deadlocks if callbacks run under btree cursor/AGI locks, duplicate or regressive inode records, excessive prefetch memory, start-in-middle masking, abort handling, and threaded perag lifetime. Tests should cover starts at zero and mid-chunk, same-AG walks, sparse/empty chunks, callback `-ECANCELED`, corrupt/non-monotonic inobt records, threaded and polled walks, and prefetch bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_iwalk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_iwalk.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_iwalk.h

Purpose: declares callback contracts and entry points for walking allocated inodes and inode btree records.

Important APIs and types: `xfs_iwalk_fn` is called for each allocated inode number. `xfs_inobt_walk_fn` is called for each in-core inobt record with mount, transaction, AG number, record, and caller data. Entry points are `xfs_iwalk`, `xfs_iwalk_threaded`, and `xfs_inobt_walk`. `XFS_IWALK_SAME_AG` limits traversal to the AG containing `startino`, and `XFS_IWALK_FLAGS_ALL` documents the valid flag mask.

Control flow: no executable logic exists here. The callback return contract is important: `0` continues, negative errors stop, and `-ECANCELED` is a caller-visible intentional stop code not generated by the walker itself.

State and persistence behavior: the header stores no state. Walker implementations read allocation metadata and pass caller data through callbacks; callbacks are responsible for any state mutation.

Dependencies and integration: used by itable/bulkstat, inumbers, scrub, and other scan code. It requires XFS mount, transaction, inode number, AG number, and inobt record types to be visible to includers.

Risks and test signals: misuse of callback return codes or flags can cause incomplete scans or leaked internal stop codes. Tests should compile users of both callback types and exercise same-AG, full-FS, threaded, and early-stop walks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_iwalk.h -->
