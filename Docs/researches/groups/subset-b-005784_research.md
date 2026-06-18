# Research: subset-b-005784

Grouped research for XFS libxfs inode, metadata-directory, parent-pointer, quota, and log-format files. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_iext_tree.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_iext_tree.c

Purpose: Implements the in-core extent tree used by `struct xfs_ifork` when inode data, attr, or CoW forks are represented as decoded `xfs_bmbt_irec` records. It stores compact 16-byte records in a small B-tree with linked leaves, optimized for fast cursor walking and sequential append.

Important APIs and types: private `struct xfs_iext_rec`, `struct xfs_iext_node`, and `struct xfs_iext_leaf`; exported operations include `xfs_iext_count`, cursor movement (`xfs_iext_first`, `xfs_iext_last`, `xfs_iext_next`, `xfs_iext_prev`), lookup (`xfs_iext_lookup_extent`, `xfs_iext_lookup_extent_before`, `xfs_iext_get_extent`), mutation (`xfs_iext_insert_raw`, `xfs_iext_insert`, `xfs_iext_remove`, `xfs_iext_update_extent`), and destruction (`xfs_iext_destroy`).

Control flow: extent records are packed/unpacked by `xfs_iext_set` and `xfs_iext_get`. Inserts allocate a root for the first extent, grow the root allocation while height is one, split full leaves, and propagate new separator keys upward with `xfs_iext_insert_node`. Removals shift records out of a leaf, update parent keys when the first record changes, merge underfull leaves or inner nodes when possible, and shrink the root when only one child remains. Lookup descends by file offset to a leaf, then searches records and may advance to the next leaf for hole lookups.

State and persistence: this is purely in-memory state derived from on-disk bmbt records. `if_bytes`, `if_height`, and `if_data` describe the tree. `if_seq` is incremented with `WRITE_ONCE` before mutations so writeback/COW users can detect fork changes. Persistence occurs elsewhere when fork extents are flushed back to disk.

Dependencies and integration: relies on XFS bmap record limits from `xfs_format.h`, inode fork state from `xfs_inode.h`, allocation via kernel memory APIs, and tracepoints. It is consumed heavily by inode fork formatting/flushing and bmap code.

Risks and test signals: high risk areas are separator-key maintenance, leaf merge cursor repair, empty-record detection via `hi == 0`, and overflow assumptions in packed bit fields. Useful tests include bmap fuzzing with many insert/remove/update sequences, sequential append and middle insertion workloads, debug assertions, fsstress with reflink/COW, and mount/recovery after extent-heavy operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_iext_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_buf.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_buf.c

Purpose: Verifies inode buffers and converts inode cores between on-disk `struct xfs_dinode` and in-core `struct xfs_inode` state. It centralizes dinode integrity checks, timestamp conversion, CRC calculation, extent count encoding, and inode hint validation.

Important APIs: buffer verifier ops `xfs_inode_buf_ops` and `xfs_inode_buf_ra_ops`; `xfs_imap_to_bp`; timestamp helpers `xfs_inode_from_disk_ts` and the private disk encoder; conversion functions `xfs_inode_from_disk` and `xfs_inode_to_disk`; verifiers `xfs_dinode_verify`, `xfs_dinode_verify_metadir`, `xfs_inode_validate_extsize`, `xfs_inode_validate_cowextsize`; CRC writer `xfs_dinode_calc_crc`.

Control flow: read verification scans every inode in a buffer, checking magic, version, and unlinked-list agino. Readahead failures mark the buffer not done instead of producing normal corruption reports. `xfs_inode_from_disk` verifies the dinode, copies permanent VFS/XFS fields, handles v1 inode compatibility, decodes timestamps including bigtime, formats data and attr forks, initializes CoW forks for reflink, and adjusts metadata-inode stats. `xfs_inode_to_disk` writes the reverse representation, selecting v2/v3 fields and large extent counters. `xfs_dinode_verify` performs layered checks: v3 CRC/UUID/ino, mode/size, fork counts, fork offsets and formats, feature-dependent flags, metadata inode constraints, hint alignment, bigtime, reflink/realtime compatibility, and nblocks consistency.

State and persistence: this file is a persistence boundary. It reads and writes dinode core fields, inode buffer CRCs, LSNs, fork counters, timestamps, metadata type, quota/project ids, and unlinked-list pointers. It marks sick AG/inode metadata on verifier failures.

Dependencies and integration: calls fork materialization from `xfs_inode_fork.c`, health marking, transaction buffer reads, directory and metadata feature predicates, and Linux VFS inode helpers.

Risks and test signals: ABI and compatibility risks are high: incorrect endian conversion, v3 CRC range, large extent counters, bigtime ranges, metadir restrictions, and extent hint validation can reject valid filesystems or admit corruption. Signals include xfs/122-style ondisk layout tests, fuzzed inode images, mount tests across feature combinations, realtime/reflink/bigtime/metadir matrices, and log recovery over inode buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_buf.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_buf.h

Purpose: Declares inode-buffer location and conversion/verifier interfaces shared by libxfs users. It is the public contract for mapping inode numbers to buffers and translating `xfs_dinode` cores.

Important APIs and types: `struct xfs_imap` records inode chunk block, length, and byte offset; declarations cover `xfs_imap_to_bp`, `xfs_dinode_calc_crc`, `xfs_inode_to_disk`, `xfs_inode_from_disk`, `xfs_dinode_verify`, `xfs_dinode_verify_metadir`, `xfs_inode_validate_extsize`, `xfs_inode_validate_cowextsize`, `xfs_inode_from_disk_ts`, `xfs_inode_encode_bigtime`, and `xfs_dinode_good_version`.

Control flow: the header itself has minimal logic. `xfs_inode_encode_bigtime` maps Unix seconds into the XFS bigtime epoch and adds nanoseconds. `xfs_dinode_good_version` defines the feature-dependent acceptable dinode versions: v3 only for v3 inode filesystems, otherwise v1/v2.

State and persistence: exposes structures and functions that operate on persistent dinode buffers and bigtime timestamp encoding. `xfs_imap` is transient in-core mapping metadata but points to persistent inode chunks.

Dependencies and integration: included by inode read/write, recovery, icache, and repair paths needing verifier or conversion functions. It depends on mount feature predicates, timestamp constants, and core XFS type definitions.

Risks and test signals: the header is small but ABI-sensitive because callers rely on exact conversion semantics. Tests should cover bigtime encode/decode round trips, v1/v2/v3 version acceptance, and inode buffer mapping callers that pass `xfs_imap` into transaction reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_buf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_fork.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_fork.c

Purpose: Materializes and flushes inode forks. It converts local, extent, btree, device, and metadata-btree fork formats between on-disk dinode storage and in-core `struct xfs_ifork`, manages fork memory, verifies local fork contents, and enforces extent-count capacity.

Important APIs: `xfs_init_local_fork`, `xfs_iformat_data_fork`, `xfs_iformat_attr_fork`, `xfs_ifork_init_attr`, `xfs_ifork_zap_attr`, `xfs_broot_alloc`, `xfs_broot_realloc`, `xfs_idata_realloc`, `xfs_idestroy_fork`, `xfs_iextents_copy`, `xfs_iflush_fork`, `xfs_iext_state_to_fork`, `xfs_ifork_init_cow`, `xfs_ifork_verify_local_data`, `xfs_ifork_verify_local_attr`, `xfs_iext_count_extend`, and `xfs_ifork_is_realtime`.

Control flow: local forks are copied from the dinode, with symlink data overallocated for null termination. Extent forks validate every disk bmbt record and insert decoded records into the in-core extent tree. Btree forks validate root shape and copy the root into an in-core btree block while leaving extents lazily unread. Data fork formatting dispatches by inode mode and fork format, including special metadata btrees for realtime rmap/refcount. Attr formatting mirrors this for attr fork formats. Flush dispatches by current fork format and log flags, copying local bytes, encoding extents, converting btree roots, writing device numbers, or delegating metadata btree flush.

State and persistence: owns `if_format`, `if_nextents`, `if_needextents`, `if_bytes`, `if_data`, `if_broot`, and CoW fork allocation. Persistence is through `xfs_iflush_fork`, which writes fork payloads into dinodes according to inode log item fields.

Dependencies and integration: integrates with bmap btree conversion, attr/dir/symlink verifiers, realtime metadata btrees, tracepoints, inode log items, and the in-core extent tree.

Risks and test signals: risks include trusting fork size/counts, lazy extent state ordering, btree root resizing, attr fork cleanup after errors, and large extent counter upgrades. Tests should exercise local directory/symlink validation, attr fork conversions, btree-to-extents transitions, CoW fork init, delayed allocation filtering in `xfs_iextents_copy`, and debug lock assertions during flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_fork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_fork.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_fork.h

Purpose: Defines `struct xfs_ifork` and the public fork/extent-tree APIs used throughout XFS inode and bmap code.

Important APIs and types: `struct xfs_ifork` stores fork bytes, btree root, extent tree sequence, tree height, data pointer, extent count, root size, format, and lazy-read flag. Macros estimate worst-case extent count growth for common operations. Inline helpers expose max extents, fork format, fork extent counts, disk fork extent counters, cursor peeking, iteration via `for_each_xfs_iext`, and `xfs_need_iread_extents`.

Control flow: the header provides selection and iteration primitives. `xfs_iext_next_extent` and `xfs_iext_prev_extent` move a cursor then decode the pointed extent; peek helpers copy the cursor first. `xfs_need_iread_extents` uses acquire semantics paired with release stores during fork formatting to ensure readers see valid format state when lazy btree extents must be loaded.

State and persistence: the state is in-core but mirrors persistent fork format and extent counts. Disk extent-count helpers understand the large extent counter feature and choose the correct dinode fields.

Dependencies and integration: included by inode conversion, bmap, attr, recovery, and flush code. It declares functions implemented by `xfs_inode_fork.c` and `xfs_iext_tree.c`.

Risks and test signals: errors in max extent limits or disk counter selection affect ENOSPC/EFBIG behavior and verifier decisions. Test signals include feature matrices for large extent counters, attr/data/CoW fork iteration, lazy btree extent read races, and build coverage for all consumers of fork constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_fork.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_util.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_util.c

Purpose: Provides inode utility operations: user-visible flag translation, inheritance during inode creation, inode initialization, link-count changes, and maintenance of the per-AG unlinked inode lists.

Important APIs: `xfs_flags2diflags`, `xfs_flags2diflags2`, `xfs_ip2xflags`, `xfs_get_initial_prid`, `xfs_inode_init`, `xfs_iunlink`, `xfs_iunlink_remove`, `xfs_droplink`, `xfs_bumplink`, and `xfs_inode_uninit`. Private helpers manage flag inheritance and unlinked-list bucket/backref updates.

Control flow: flag conversion maps FS_XFLAG bits to XFS dinode flags with mode-specific filtering and preserves internal bits such as PREALLOC, REFLINK, BIGTIME, and NREXT64. `xfs_inode_init` sets link counts, ownership, project inheritance, timestamps, fork format, inherited flags, optional attr fork creation for xattrs/parent pointers, and logs the inode. Unlinked insertion reads the AGI, validates the target bucket, updates the next inode backref, logs this inode's `di_next_unlinked`, and points the bucket at the new inode. Removal clears this inode's pointer, updates the next inode's backref, then either patches the previous inode or bucket head.

State and persistence: mutates dinode flags, timestamps, project ids, fork formats, link counts, attr fork presence, superblock attr feature bit, AGI unlinked buckets, and inode `di_next_unlinked`. In-core `i_prev_unlinked` provides a back pointer for efficient removal but on-disk remains singly linked.

Dependencies and integration: depends on transaction logging, AGI buffer access, inode allocation/free, bmap and fork helpers, health marking, quota/project inheritance, parent pointer feature checks, and VFS inode helpers.

Risks and test signals: unlinked-list corruption is high impact because it affects crash recovery and inode freeing. Risk areas include AGI lock ordering, stale inode-cache lookups, ENOLINK reloads, link count pinning, and inherited hint validation. Tests include O_TMPFILE, unlink under crash/recovery, high-AG-count workloads, project inheritance, parent-pointer inode creation, and corrupt AGI bucket fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_util.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_util.h

Purpose: Declares inode utility interfaces and creation/time-change metadata shared by XFS inode creation, linking, and deletion code.

Important APIs and types: `struct xfs_icreate_args` packages idmap, parent inode, device number, mode, and creation flags. Flags include tmpfile, initialize xattrs, and unlinkable. Time-change flags drive `xfs_trans_ichgtime`. Declared operations include flag conversion, initial project id selection, inode initialization/uninitialization, unlinked-list insertion/removal, and link count changes.

Control flow: the header contains no complex implementation but defines call contracts. Passing `idmap == NULL` creates detached or root-like metadata files with root ownership. `pip == NULL` means tree root creation. Creation flags influence whether an inode starts unlinked and whether an attr fork must be present.

State and persistence: consumers mutate persistent inode core fields, timestamps, link counts, fork offsets, and AGI unlinked structures through the declared functions.

Dependencies and integration: used by inode allocation, metadir creation, quota inode creation, VFS create/link/unlink paths, and transaction logging. `struct xfs_icluster` is forward-declared for inode free batching.

Risks and test signals: API misuse can create incorrectly owned detached metadata files or miss parent-pointer attr fork initialization. Tests should cover idmapped creates, tmpfiles, quota/metadir callers with `idmap == NULL`, and all link count transitions through zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_inode_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_log_format.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_log_format.h

Purpose: Defines the on-disk log ABI for XFS. It covers physical log record headers, operation headers, transaction headers, log item type codes, and every serialized log item structure interpreted by recovery.

Important APIs and types: physical constants and helpers such as `xlog_assign_lsn`, `xlog_get_cycle`, `CYCLE_LSN`, and record-size macros; `struct xlog_op_header`, `struct xlog_rec_header`, `struct xfs_trans_header`; item type constants `XFS_LI_*`; inode log formats and `XFS_ILOG_*` flags; buffer log format and buffer type encodings; intent/done structures for EFI/EFD, RUI/RUD, CUI/CUD, BUI/BUD, XMI/XMD, ATTRI/ATTRD, quotaoff, dquot, and icreate.

Control flow: this header does not execute recovery but encodes how recovery parses records. Variable-length intent structures place arrays immediately after a fixed 16-byte header and provide size helpers. Buffer item flags encode dirty bitmap chunks and buffer type in upper bits. Inode log flags distinguish core, local data, extents, btree roots, device numbers, fork owner updates, and in-memory-only timestamp/version triggers.

State and persistence: all structures are persistent journal state. Some are host-endian historical formats, so the header preserves 32-bit and 64-bit structure variants and architecture-dependent checksum compatibility. Quota flags are shared with superblock/mount state.

Dependencies and integration: consumed by log item formatters, transaction code, recovery, ondisk layout checks, inode flush, buffer replay, deferred operation recovery, and quota code.

Risks and test signals: this is ABI-critical. Changing sizes, offsets, endian assumptions, item ids, or flag masks can make logs unrecoverable. Tests include xfs/122 layout assertions, dirty-log recovery across architectures, intent/done replay matrices for data and realtime operations, inode log replay with all fork formats, and quota flag compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_log_format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_log_recover.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_log_recover.h

Purpose: Declares the internal recovery item dispatch interface and core recovery data structures.

Important APIs and types: `enum xlog_recover_reorder` selects replay ordering queues; `struct xlog_recover_item_ops` defines per-log-item callbacks for reorder, readahead, pass1, and pass2; `struct xlog_recover_item` stores recovered item regions; `struct xlog_recover` tracks partial transactions by transaction id. Extern ops cover icreate, buffers, inodes, dquots, quotaoff, bmap/rmap/refcount/extent intents and done items, attr intents, mapping exchange, and realtime variants.

Control flow: recovery reads log operations into `xlog_recover_item` structures, associates each with item ops, optionally reorders them, performs pass1 bookkeeping, then pass2 replay. Intent items reconstruct in-core intent items and insert them into the AIL; done items find corresponding intents and release them. `xlog_recover_resv` adapts normal transaction reservations for intent replay by forcing logcount to one.

State and persistence: recovery consumes persistent log regions and creates transient transaction/item queues. It also manages the buffer cancel table and recovered intent lifecycle so replay does not redo canceled buffers or completed deferred operations.

Dependencies and integration: depends on log item type codes from `xfs_log_format.h`, transaction reservations, buffer cache readahead/cancel logic, inode lookup helpers, AIL intent handling, and deferred operation types.

Risks and test signals: replay ordering and intent lifetime are correctness-critical. Tests should cover canceled buffer replay, inode-buffer ordering, partial continued transactions, recovered intents with tight log grant space, and failures during pass2 cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_log_recover.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_log_rlimit.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_log_rlimit.c

Purpose: Computes the maximum transaction reservation and minimum legal log size for a filesystem feature set. It preserves historical compatibility where older kernels expected overestimated log sizes, while allowing corrected computations for newer feature combinations.

Important APIs: `xfs_log_get_max_trans_res` and `xfs_log_calc_minimum_size`. Private helpers include `xfs_want_minlogsize_fixes`, `xfs_log_calc_max_attrsetm_res`, and `xfs_log_calc_trans_resv_for_minlogblocks`.

Control flow: feature gating checks the ondisk superblock and enables corrected minimum-log computations only for v5 filesystems with parent pointers. Attribute set maximum reservation computes the largest local attr value reservation, with a parent-pointer-era fix for a unit conversion issue. The alternate transaction reservation table either uses modern calculations or temporarily restores legacy rmap/reflink assumptions, old rmap maxlevels, and older log counts/reservation formulas. `xfs_log_get_max_trans_res` scans the reservation table for the largest total reservation, comparing attrsetm separately. `xfs_log_calc_minimum_size` converts the max reservation to log blocks, accounts for log stripe unit padding, multiplies by `XFS_MIN_LOG_FACTOR`, and returns filesystem blocks.

State and persistence: no persistent writes. It reads superblock features and mount geometry; temporarily mutates `m_rmap_maxlevels` during legacy calculation and restores it before return.

Dependencies and integration: used by mkfs/mount-style validation to reject undersized logs. Depends on transaction reservation calculators, bmap/da space formulas, log unit reservation helpers, superblock feature predicates, and tracepoints.

Risks and test signals: risks include silently reducing minimum log size for filesystems that older kernels should mount, incorrect temporary mount state restoration, and log stripe unit rounding errors. Tests should compare minlog outputs across rmap/reflink/parent feature combinations, small AG geometries, large attr cases, and stripe-unit configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_log_rlimit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_metadir.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_metadir.c

Purpose: Implements the metadata directory tree abstraction for metadata inodes stored in a hidden internal namespace. It provides lookup, create, link in userspace builds, commit/cancel, and mkdir helpers.

Important APIs: `xfs_metadir_load`, `xfs_metadir_start_create`, `xfs_metadir_create`, userspace-only `xfs_metadir_start_link` and `xfs_metadir_link`, `xfs_metadir_commit`, `xfs_metadir_cancel`, and `xfs_metadir_mkdir`. Private helpers set `xfs_name`, perform directory lookup with type validation, and tear down update state.

Control flow: load converts a path component to `xfs_name`, locks the parent directory, looks up the inode, validates inode number/type, then calls `xfs_trans_metafile_iget`. Create starts by allocating parent-pointer context and a create transaction, then locks the parent. `xfs_metadir_create` verifies nonexistence, allocates an inode, initializes it, marks it as a metadata file, joins the parent after possible transaction rolling, and creates the directory entry with parent pointer arguments. Commit commits the transaction and releases locks/context; cancel aborts and releases. `xfs_metadir_mkdir` wraps start/create/commit and handles partially created inode cleanup.

State and persistence: mutates the metadata directory tree, creates metadata inode cores, directory entries, parent pointer attrs, and inode flags. Update state tracks held locks, transaction, parent args, and created inode.

Dependencies and integration: depends on directory code, inode allocation/init, transaction reservations, parent pointers, metadata inode flags, health marking, and shutdown checks. It deliberately excludes legacy quota/realtime bitmap/summary inode management from this abstraction.

Risks and test signals: risks include lock/transaction cleanup on partial create, exposing metadata inodes without required flags, directory type mismatches, and parent-pointer consistency. Tests should cover missing/existing path components, shutdown behavior, metadir mkdir failure injection, quota exclusion, parent-pointer enabled/disabled filesystems, and repair of sick metadir state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_metadir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_metadir.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_metadir.h

Purpose: Declares the metadata directory tree update interface and `struct xfs_metadir_update`, the state object used to create or link internal metadata files.

Important APIs and types: `struct xfs_metadir_update` carries parent directory, path component, parent-pointer context, child inode, transaction, metadata file type, and lock-state bits. Declared operations cover load, start/create, start/link, commit/cancel, and mkdir.

Control flow: callers fill an update structure, call a start function to allocate resources and lock inodes, call create/link, then must call commit or cancel. The API intentionally separates resource acquisition from mutation so callers can finish setup of returned metadata inodes.

State and persistence: the structure tracks transient transaction and lock state around persistent metadir mutations. `metafile_type` becomes persistent inode metadata through `xfs_metafile_set_iflag`.

Dependencies and integration: consumed by quota/metafile/realtime metadata creation and repair paths. It depends on parent pointer declarations and metadata file type enums from core XFS format headers.

Risks and test signals: misuse can leak locks or transactions, especially because create can return an inode even on error. Tests should assert every start path is paired with commit/cancel and exercise cleanup of partially initialized metadata inodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_metadir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_metafile.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_metafile.c

Purpose: Manages metadata inode identity and space reservations for metadata btree files, especially realtime rmap/refcount btrees under the metadir feature.

Important APIs: `xfs_metafile_type_str`, `xfs_metafile_set_iflag`, `xfs_metafile_clear_iflag`, `xfs_metafile_resv_critical`, `xfs_metafile_resv_alloc_space`, `xfs_metafile_resv_free_space`, `xfs_metafile_resv_free`, and `xfs_metafile_resv_init`.

Control flow: metadata flag setup strips permissions, forces root uid/gid, applies mandatory metadata file or directory flags, clears DAX, sets `XFS_DIFLAG2_METADATA`, records metatype, logs the inode, and moves stats from active to metadata. Reservation initialization frees old reservation state, walks realtime groups to compute used and target reserve for rtrmap/rtrefcount btrees, caps reservation to a quarter of data blocks, hides unused reserved space from fdblocks, and records used/available/target counts. Allocation first consumes reservation availability and updates reserved fdblocks, then falls back to free blocks or transaction reservation for overrun. Freeing decrements inode blocks, refills hidden reservation to target, and returns excess to global fdblocks.

State and persistence: mutates inode core metadata flags and `i_nblocks`, mount reservation counters under `m_metafile_resv_lock`, in-core and on-disk fdblocks, and delayed allocation accounting.

Dependencies and integration: depends on realtime group iteration, rtrmap/rtrefcount reserve calculators, transaction superblock accounting, allocation args, error injection, and feature predicates.

Risks and test signals: space-accounting bugs can hide or leak blocks and cause metadata btree ENOSPC. Tests should cover mount/unmount reservation init/free, growfs or realtime feature changes, reservation critical thresholds, overrun paths, transaction rollback, and stats transitions for metadata inodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_metafile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_metafile.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_metafile.h

Purpose: Declares metadata inode flagging and reservation interfaces.

Important APIs and types: mandatory flag masks `XFS_METAFILE_DIFLAGS` and `XFS_METADIR_DIFLAGS`; type string lookup; metadata flag set/clear; reservation critical/allocation/free/init APIs; external iget hooks `xfs_trans_metafile_iget` and `xfs_metafile_iget`.

Control flow: callers use set/clear helpers within transactions to change inode identity and reservation helpers from allocation/freeing paths. The external iget hooks are implementation-specific for kernel/userspace.

State and persistence: flag helpers persist inode metadata status and metatype. Reservation helpers manage mount-wide reserved/used/available counters and superblock free-space accounting through implementation in `xfs_metafile.c`.

Dependencies and integration: used by metadir create/load, inode verifier metadata checks, realtime metadata btree allocation, quota metadata inode loading, and repair tools.

Risks and test signals: mandatory flag masks must match verifier expectations. Tests should pair metadata flag creation with `xfs_dinode_verify_metadir`, and reservation tests should verify fdblocks/delalloc invariants before and after allocation and unmount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_metafile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ondisk.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ondisk.h

Purpose: Provides compile-time assertions that XFS on-disk and UABI structures have exact expected sizes, offsets, and constant values. It is a guardrail against accidental ABI/layout drift.

Important APIs: assertion macros `XFS_CHECK_STRUCT_SIZE`, `XFS_CHECK_OFFSET`, `XFS_CHECK_VALUE`, `XFS_CHECK_SB_OFFSET`, and the init-time function `xfs_check_ondisk_structs`.

Control flow: `xfs_check_ondisk_structs` runs a sequence of `static_assert` checks covering file structures, btrees, dir/attr layouts, realtime metadata, log item formats, parent pointer ioctls, v5/v4 shared header offsets, timestamp/quota time range values, superblock offsets, and ioctl UABI structures. It also documents intentionally omitted architecture-sensitive structures.

State and persistence: no runtime mutable state. Its entire purpose is to protect persistent on-disk and userspace ABI formats at build time.

Dependencies and integration: includes all relevant structure definitions indirectly through format headers. It must be updated whenever a deliberate on-disk or UABI layout change is made.

Risks and test signals: missing or stale assertions can allow silent ABI regressions; incorrect assertions can break valid builds on some architectures. Test signals are compile coverage across 32-bit/64-bit architectures, xfs/122 ondisk layout tests, and CI builds after changing any format header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ondisk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_parent.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_parent.c

Purpose: Implements parent pointer xattr validation, hashing, transactional updates for create/remove/rename, extraction from attrs, lookup, and repair set/unset helpers.

Important APIs: `xfs_parent_namecheck`, `xfs_parent_valuecheck`, `xfs_parent_hashval`, `xfs_parent_hashattr`, `xfs_parent_addname`, `xfs_parent_removename`, `xfs_parent_replacename`, `xfs_parent_from_attr`, `xfs_parent_lookup`, `xfs_parent_set`, and `xfs_parent_unset`. It also defines `xfs_parent_args_cache`.

Control flow: name validation rejects incomplete attrs and delegates filename component validation. Value validation requires the parent feature, exact `struct xfs_parent_rec` size, local value storage, and valid parent directory inode. Hashing combines the directory name hash with parent inode bits to distinguish hardlink parents. Update helpers ensure the child attr fork exists and extents are read, initialize `xfs_da_args` with `XFS_ATTR_PARENT` and logged operation flags, fill parent records from directory inode generation, and call attr set/remove/replace. Repair helpers sanity-check inputs and invoke immediate attr updates without an existing transaction.

State and persistence: parent pointers are stored as local extended attributes in the child attr fork. The value records parent inode and generation; names are directory entry names. Transactional helpers keep parent pointers consistent with directory mutations.

Dependencies and integration: integrates with attr, dir hash/name validation, deferred attr items, transaction space, inode health marking, parent-pointer feature checks, and repair code.

Risks and test signals: missing attr forks on parent-enabled filesystems are corruption; ENOSPC during parent pointer creation risks namespace inconsistency; hardlink hash collisions and rename replacement correctness matter. Tests should cover create/unlink/rename/hardlink with parent pointers, attr scrub/repair, invalid parent attrs, noattr-fork corruption, and logged attr recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_parent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_parent.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_parent.h

Purpose: Declares the parent pointer interface and small helpers for encoding parent records and allocating update context.

Important APIs and types: validators, hash functions, `xfs_parent_rec_init`, `xfs_inode_to_parent_rec`, `struct xfs_parent_args`, `xfs_parent_start`, `xfs_parent_finish`, transactional add/remove/replace, attr extraction, lookup, repair set, and repair unset.

Control flow: `xfs_parent_start` allocates a zeroed parent args object only when the filesystem has parent pointers; otherwise it returns a null context and success. `xfs_parent_finish` frees the context if present. Inline record helpers encode inode and generation in big-endian on-disk form.

State and persistence: `struct xfs_parent_args` is transient state that carries old/new parent records and a prepared `xfs_da_args` for logged attr operations. Parent records themselves persist inside child xattrs.

Dependencies and integration: used by directory create/remove/rename code, metadir operations, attr recovery, scrub/repair, and parent-pointer validators.

Risks and test signals: callers must honor null contexts on filesystems without parent pointers and must not reuse stale `xfs_da_args`. Tests should cover feature-disabled no-op start/finish, allocation failure, record endian encoding, and rename replacement carrying both old and new records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_parent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_quota_defs.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_quota_defs.h

Purpose: Defines quota-related shared types, flags, reservation constants, dquot verification hooks, timestamp helpers, and metadir quota inode helpers.

Important APIs and types: `xfs_qcnt_t`, `xfs_dqtype_t`, `XFS_DQUOT_LOGRES`, quota state predicates (`XFS_IS_QUOTA_ON`, user/group/project accounting and enforcement checks), `XFS_QMOPT_*` reservation/modification flags, transaction dquot aliases, `xfs_dqinode_path`, `xfs_dqinode_metafile_type`, dquot verify/repair prototypes, dquot timestamp conversion, sick-mask lookup, and quota inode load/create/link/mkdir APIs.

Control flow: inline helpers map quota type to metadir path strings and metadata file types, asserting on invalid types. Macros separate persistent mount/superblock quota accounting flags from nonpersistent internal operation flags.

State and persistence: quota accounting flags persist in mount/superblock state via values defined in `xfs_log_format.h`; dquot records and quota inode metadata are persistent. `XFS_DQUOT_LOGRES` sizes transaction reservation for worst-case dquot logging.

Dependencies and integration: shared between kernel and userspace libxfs. Integrates with transaction quota modification, metadir quota inode management, dquot buffer verification, and health/scrub code.

Risks and test signals: quota type mapping must stay aligned with metadata inode types; reservation underestimates can deadlock or fail quota updates; persistent and nonpersistent flag spaces must not be confused. Tests should cover user/group/project quota enablement, quotaoff logging, chmod/rename worst-case dquot modifications, metadir quota inode load/create/link, and dquot verifier fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_quota_defs.h -->
