# subset-b-005739 Research

Grouped research report for the requested OCFS2 namei, layout, locking, ioctl, trace, and quota headers. Each file section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/namei.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/namei.c

Purpose: implements OCFS2 namespace operations for directories: lookup, create, mknod, mkdir, hard link, unlink/rmdir, rename, symlink, and helpers for moving inodes into and out of per-slot orphan directories. This is the VFS-facing path that turns directory changes into cluster-locked, journaled OCFS2 metadata updates.

Important APIs and functions: `ocfs2_dir_iops` exports the directory inode operations. `ocfs2_lookup()` resolves a name under a cluster inode lock and attaches OCFS2 dentry lock state. `ocfs2_mknod()`, `ocfs2_create()`, and `ocfs2_mkdir()` allocate and initialize dinodes, ACLs, security xattrs, directory entries, and quota state. `ocfs2_link()` increments on-disk link counts and adds another dirent. `ocfs2_unlink()` removes a dirent, updates link counts, and adds final-link victims to the orphan dir. `ocfs2_rename()` serializes cross-directory directory moves with the rename lock, handles overwrite-orphaning, updates `..`, and moves dentry lock ownership. Symlink support is split between fast inline symlinks in `ocfs2_dinode.id2.i_symlink` and extent-backed symlinks written by `ocfs2_create_symlink_data()`. Exported orphan helpers include `ocfs2_orphan_del()`, `ocfs2_create_inode_in_orphan()`, `ocfs2_add_inode_to_orphan()`, `ocfs2_del_inode_from_orphan()`, and `ocfs2_mv_orphaned_inode_to_new()`.

Control flow: namespace operations first initialize quotas, acquire parent and child cluster locks in a stable order, verify names and live link counts, reserve allocation contexts, then start a JBD2 transaction sized by OCFS2 credit helpers. Once metadata mutation begins, signals are blocked in create/link/symlink paths to avoid restart after partially journaled changes. The code journals dinode buffers before changing link counts, flags, timestamps, extent-list headers, and directory blocks. Insert paths prepare a directory lookup/insert result before allocating. Delete paths delete the parent entry before decrementing the victim and possibly append an orphan-dir entry. Rename adds or updates the target entry first, then removes the source entry, because directory indexing may change the lookup shape during insertion.

State and persistence: persistent state is stored in OCFS2 dinodes, directory entries, extent lists, inline-data regions, per-slot orphan directories, and quota files. In-memory state includes VFS inode link counts/timestamps, `OCFS2_I(inode)` flags such as `OCFS2_INODE_MAYBE_ORPHANED` and `OCFS2_INODE_SKIP_ORPHAN_DIR`, dentry lock objects, allocation contexts, and buffer-head cache state. Orphan persistence is explicit: normal unlinks set `OCFS2_ORPHANED_FL` and `i_orphaned_slot`; append-DIO orphaning uses `OCFS2_DIO_ORPHANED_FL`, `i_dio_orphaned_slot`, and a `dio-` prefixed orphan name. Transactions are committed before cluster locks are dropped.

Dependencies and integration: this file depends on the OCFS2 allocator, directory, DLM glue, inode, journal, symlink, xattr, ACL, quota, and dcache layers. It integrates with VFS `struct inode_operations`, Linux quota operations, POSIX ACL/security xattr initialization, JBD2 transactions, per-slot system inodes, metadata-cache uptodate tracking, and tracepoints from `ocfs2_trace.h`.

Risks: lock ordering is high risk because link and rename may lock two directories plus children; `ocfs2_double_lock()` combines inode-number ordering with ancestor checks to prevent deadlocks. Rename has complex crash-consistency exposure between target insert/update and old-entry delete, with explicit `ocfs2_error()` if the old entry cannot be removed after the new entry is visible. Orphan handling is critical for crash recovery and append-DIO cleanup. Link-count rollback on failed create/mkdir/symlink and dentry-lock cleanup after failed `ocfs2_add_entry()` are easy regression points. Cross-node races are handled by rechecking on-disk inode numbers and forcing remote dentry deletion; missing those checks can create stale dentries or unlink the wrong inode.

Test signals: useful coverage includes multi-node lookup/unlink races, create failure injection after inode allocation and after dentry lock attach, mkdir link-limit checks with indexed and non-indexed dirs, hard link races against remote unlink, rename over files and empty directories, cross-directory directory rename updating `..`, symlink tests on both fast and extent-backed thresholds, append-DIO orphan add/delete recovery, fsck/orphan-dir recovery after crash, quota accounting rollback, security/ACL initialization failures, tracepoint visibility, and lockdep or DLM deadlock testing under concurrent renames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/namei.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/namei.h

Purpose: declares the OCFS2 namespace and orphan-management interface used outside `namei.c`.

Important APIs and types: the header exports `ocfs2_dir_iops` for directory inode operations, `ocfs2_get_parent()` for NFS/export dentry parent lookup, and orphan helpers for deleting, creating, adding, removing, and moving orphaned inodes. It also defines `OCFS2_DIO_ORPHAN_PREFIX` and its length, which establish the persistent `dio-` orphan-name convention for direct-I/O orphan entries.

Control flow: callers use the exported orphan helpers when an inode must survive temporarily without a normal directory name, especially append direct I/O and delayed creation paths. The API contract passes locked inodes, journal handles, dinode buffers, and flags indicating direct-I/O orphan naming.

State and persistence: this header has no storage, but its prototypes expose persistent orphan state changes in `OCFS2_ORPHANED_FL`, `OCFS2_DIO_ORPHANED_FL`, orphan slot fields, and per-slot orphan directory entries.

Dependencies and integration: consumers depend on `struct ocfs2_super`, `handle_t`, `struct inode`, `struct dentry`, and `struct buffer_head` from the OCFS2 and kernel journaling layers. The interface ties namespace code to file-write, truncate, recovery, and export paths.

Risks: prototype drift would break lock/journal ownership assumptions in callers. The DIO orphan prefix is part of an on-disk naming convention; changing it would break cleanup of existing direct-I/O orphan entries.

Test signals: build coverage across OCFS2 files, append-DIO orphan recovery, NFS export parent lookup, orphan create/move/delete paths, and crash-recovery tests that inspect orphan directory names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/namei.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ocfs1_fs_compat.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/ocfs1_fs_compat.h

Purpose: defines OCFS1-compatible sector-0 and sector-1 volume structures that OCFS2 writes so older OCFS1 tooling recognizes the device and fails cleanly rather than mis-mounting it.

Important APIs and types: constants define OCFS1 signature, version, label, UUID, mount-point, and cluster-name lengths. `struct ocfs1_vol_disk_hdr` describes the sector-0 OCFS1 volume header. `struct ocfs1_disk_lock` mirrors the old disk lock shape with explicit padding. `struct ocfs1_vol_label` describes the sector-1 label containing disk-lock, label, volume ID, and cluster-name fields.

Control flow: this header contains no executable flow; formatting and compatibility code include it when laying out the first sectors of a new OCFS2 volume.

State and persistence: all structures are on-disk compatibility records. They are not the active OCFS2 superblock; OCFS2's real superblock starts at `OCFS2_SUPER_BLOCK_BLKNO` from `ocfs2_fs.h`.

Dependencies and integration: depends on fixed-width kernel integer types and is coupled to mkfs/tunefs behavior and any mount detection code that validates the OCFS1 signature.

Risks: field size, alignment, or signature changes can break the protective compatibility mechanism and confuse old tools. Because these structures live in fixed sectors, packing and padding assumptions are ABI-sensitive.

Test signals: mkfs image inspection of sectors 0 and 1, old OCFS1 mount rejection behavior, endian/layout checks, and compatibility tests that verify OCFS2 superblock discovery still starts at block 2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ocfs1_fs_compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2.h

Purpose: defines central in-kernel OCFS2 state, lock-resource state, mount flags, metadata-cache contracts, feature helpers, link-count helpers, block/cluster conversion helpers, and endian-safe bitmap helpers.

Important APIs and types: `struct ocfs2_super` is the mounted filesystem state, holding root/system inodes, slot information, feature bits, cluster identity, journal/recovery state, local allocation state, DLM lock resources, orphan scanning state, quota drop work, truncate-log state, directory hash seeds, refcount-tree cache, workqueue, sysfs/debugfs state, and filecheck state. `struct ocfs2_lock_res` is the DLM lock resource wrapper with holders, requested/blocking levels, lock name, callbacks, flags, LVB, waitqueue, and optional stats. `struct ocfs2_caching_info` tracks metadata buffer cache state and transaction numbers. Helper APIs include `OCFS2_SB()`, feature predicates such as `ocfs2_supports_inline_data()` and `ocfs2_supports_indexed_dirs()`, link-count accessors, readonly-state helpers, cluster-stack helpers, signature validators, block/cluster/page conversion helpers, and OCFS2 little-endian bitmap wrappers.

Control flow: this header primarily provides inline decisions used throughout the filesystem. Runtime code checks feature bits in `ocfs2_super` before choosing inline data, indexed directories, append-DIO, xattrs, metadata ECC, discontiguous block groups, and refcount-tree behavior. Readonly helpers serialize flag access through `osb_lock`. Conversion helpers translate between filesystem clusters, blocks, bytes, sectors, and page indexes.

State and persistence: most state here is in-memory mount state derived from on-disk superblock and system files. Persistent behavior is influenced by cached feature fields, link-count encoding from `ocfs2_dinode`, and block/cluster geometry. Lock-resource flags and metadata-cache transaction fields are runtime-only but guard cluster coherence and journal ordering.

Dependencies and integration: included by most OCFS2 implementation files. It depends on Linux locking, workqueue, rb-tree, kref, JBD2, stack glue, on-disk definitions from `ocfs2_fs.h`, lock IDs, ioctls, block checking, reservations, and filecheck support. `namei.c` uses its feature, link-count, readonly, geometry, and `OCFS2_SB()` helpers directly.

Risks: incorrect feature predicates can make the filesystem interpret on-disk data using the wrong format. `ocfs2_lock_res` flag transitions are concurrency-sensitive and affect DLM downconversion. Geometry helpers must avoid overflow and rounding errors because allocation, truncation, symlink sizing, and quota accounting depend on exact block/cluster conversion. Link-count helpers split and merge high link counts for indexed directories; mistakes can corrupt nlink persistence.

Test signals: Kconfig build matrix, mount option parsing, local versus clustered mount tests, DLM lock stress, metadata-cache invalidation tests, inline-data and indexed-dir feature tests, high-link-count directory tests, readonly/error-state transitions, block/cluster conversion unit coverage, and big-endian/little-endian bitmap validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_fs.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_fs.h

Purpose: defines the OCFS2 on-disk format: superblock location, feature bits, object signatures, system inode names, dinodes, extents, directories, indexed directories, allocators, refcount trees, xattrs, quotas, and size-calculation helpers shared by kernel and userspace.

Important APIs and types: major structures include `ocfs2_super_block`, `ocfs2_dinode`, `ocfs2_extent_rec/list/block`, `ocfs2_chain_list`, `ocfs2_group_desc`, `ocfs2_dir_entry`, `ocfs2_dir_block_trailer`, `ocfs2_dx_root_block`, `ocfs2_dx_leaf`, `ocfs2_refcount_block`, xattr header/block/value-root/tree-root structures, global and local quota records, and quota block trailers. Constants define compatibility, incompatibility, and ro-compat feature masks, inode flags such as `OCFS2_ORPHANED_FL` and `OCFS2_DIO_ORPHANED_FL`, dynamic inode flags such as `OCFS2_INLINE_DATA_FL` and `OCFS2_INDEXED_DIR_FL`, system inode indexes, directory-entry sizing, link-count limits, cluster/block limits, and backup superblock positions. Inline helpers calculate per-block record capacity, system inode names, directory file type, quota trailers, fast symlink space, inline data space, group bitmap size, and discontiguous group detection.

Control flow: implementation code uses the constants and helpers to parse disk blocks and decide how many records fit in a block for the active block size and feature set. System inode names are generated from a global table, with global files unformatted and slot-local files formatted with the slot number. On-disk unions in `ocfs2_dinode` select superblock, local-alloc bitmap, chain allocator, extent list, truncate log, inline data, or symlink payload according to inode type and flags.

State and persistence: this file is the durable OCFS2 ABI. Feature bits gate mount compatibility; flags persist inode validity, orphan state, system-file identity, append-DIO orphaning, inline data/xattr/index/refcount state, and journal recovery state. Directory entries persist names and target inode block numbers. Indexed-directory and xattr structures persist secondary trees. Quota structures persist global usage, local deltas, recovery chunks, and metadata checksums.

Dependencies and integration: included from kernel OCFS2 code and userspace tools. It depends on `linux/magic.h`, fixed-width endian types, Linux file attribute flags, and object layout assumptions from mkfs, fsck, tunefs, mount, and the kernel. `namei.c` directly relies on filename limits, link limits, orphan flags, dynamic inode flags, fast symlink sizing, directory-entry layout, system inode IDs, and link-count encoding.

Risks: any layout change is ABI-sensitive. Feature-bit mistakes can allow unsafe mounts or reject valid volumes. Record-capacity helpers must match exact struct offsets or metadata blocks will be overrun. The userspace `ocfs2_group_bitmap_size()` branch appears to reference `sb->s_blocksize` despite taking `blocksize`; userspace compile coverage should catch this contract if that branch is built. Orphan and DIO orphan flags must remain consistent with recovery code. Indexed directory link limits and high-link-count encoding must remain in sync with VFS nlink behavior.

Test signals: on-disk layout tests with `pahole`/static assertions or fsck fixtures, mkfs/mount/fsck round trips for each feature bit, endian tests, backup superblock discovery, inline data and fast symlink boundary tests, indexed-directory creation/search/delete, xattr bucket/tree tests, refcount/reflink tests, discontiguous group allocation, quota recovery, and crash recovery of `OCFS2_ORPHANED_FL` and `OCFS2_DIO_ORPHANED_FL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_ioctl.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_ioctl.h

Purpose: defines OCFS2 user-space ioctl ABI structures and command numbers for space reservation, online resize group management, reflink, filesystem information queries, and extent movement/defragmentation.

Important APIs and types: `struct ocfs2_space_resv` mirrors XFS-style reservation arguments used by `OCFS2_IOC_RESVSP*` and `OCFS2_IOC_UNRESVSP*`; unsupported ALLOCSP/FREESP numbers are still reserved for completeness. `struct ocfs2_new_group_input` passes group descriptor data for online resize. `struct reflink_arguments` carries old path, new path, and preserve flag user pointers/values. The `ocfs2_info` family defines a multiplexed request array with per-request headers and typed outputs for cluster size, block size, slot count, label, UUID, features, journal size, free inode stats, and free-fragment stats. `struct ocfs2_move_extents` defines defrag/move input/output fields and operation flags.

Control flow: ioctl handlers copy these structures to or from user space, validate request magic/code/size, then dispatch to reservation, resize, reflink, info, or move-extents code. `OCFS2_INFO_FL_NON_COHERENT` is an input hint that allows the kernel to decide whether cluster locking can be skipped; `FILLED` and `ERROR` are kernel-populated result flags.

State and persistence: the header has no runtime storage, but commands can persistently reserve/unreserve extents, add allocation groups, create reflinks, and move extents. Info requests expose mounted filesystem state and on-disk feature/geometry fields.

Dependencies and integration: included by `ocfs2.h` and ioctl implementation code, and must stay ABI-compatible with user-space tools. It depends on ioctl encoding macros, fixed-width types, and constants such as `OCFS2_VOL_UUID_LEN`, `OCFS2_MAX_VOL_LABEL_LEN`, `OCFS2_MAX_SLOTS`.

Risks: structure packing, field size, command number, or semantic changes break user-space ABI. Pointer-sized path fields in `reflink_arguments` are encoded as `__u64`, so compat handling must be correct. Info request size/magic validation is important for forward/backward compatibility. Move-extents flags can fragment or relocate data incorrectly if validation is weak.

Test signals: ioctl ABI compile tests, 32-bit compat tests, reservation and unreservation xfstests, online resize group-add/extend tests, reflink preserve-mode tests, `OCFS2_IOC_INFO` with mixed known/unknown request codes and non-coherent hints, defragmentation/move-extents tests, and strace/ABI checks for command numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_lockid.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_lockid.h

Purpose: defines OCFS2 distributed lock identifier format, lock type enumeration, type-to-character mapping, and human-readable lock type names.

Important APIs and types: lock IDs are fixed at `OCFS2_LOCK_ID_MAX_LEN` bytes and encode a type character, six pad characters, a 16-character hex block number, an 8-character generation, and a NUL terminator. `enum ocfs2_lock_type` lists meta, data, super, rename, rw, dentry, open, flock, quota info, NFS sync, orphan scan, refcount, and trim locks. `ocfs2_lock_type_char()` maps enum values to stable single-character lock name prefixes. `ocfs2_lock_type_string()` maps enum values to display strings through `ocfs2_lock_type_strings`.

Control flow: DLM glue and debug code use the enum to construct lock names and print diagnostics. The inline mapping returns NUL for unknown character mappings, while the string accessor asserts under `__KERNEL__` if the type is out of range.

State and persistence: this header has no shared runtime state, but the lock-name format is part of cluster interoperability. Every node must construct identical names for the same resource.

Dependencies and integration: included by `ocfs2.h` and DLM-related implementation files. It integrates with `struct ocfs2_lock_res` and the cluster lock manager. The dentry lock inode field starts at `OCFS2_DENTRY_LOCK_INO_START`, which is a parsing convention for dentry lock IDs.

Risks: changing type characters, string length, padding, or block/generation offsets breaks cross-node lock compatibility. Adding lock types requires keeping enum values, character mapping, strings, and any lock statistics/debug consumers in sync.

Test signals: multi-node lock acquisition across all lock types, lock-name formatting/parsing tests, DLM debug output checks, invalid enum assertions in debug builds, dentry-lock coherence tests, and rolling-upgrade compatibility where older and newer nodes agree on lock IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_lockid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_lockingver.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_lockingver.h

Purpose: declares the OCFS2 cluster locking protocol version used by locking negotiation.

Important APIs and types: `OCFS2_LOCKING_PROTOCOL_MAJOR` and `OCFS2_LOCKING_PROTOCOL_MINOR` are currently `1` and `0`, documented as the initial protocol from OCFS2 1.4.

Control flow: this header has no code; DLM glue and mount/cluster negotiation code include the version constants to advertise or verify locking compatibility.

State and persistence: no storage is defined here. The constants are runtime protocol ABI rather than filesystem metadata.

Dependencies and integration: integrates with `dlmglue.c` and cluster stack compatibility checks. It is intentionally small so every participant compiles against the same version constants.

Risks: bumping the version without matching negotiation behavior can split clusters or allow incompatible nodes to coordinate incorrectly. Failing to bump it when lock semantics change can cause subtle cross-version corruption.

Test signals: mixed-version cluster mount tests, lock negotiation failure tests, DLM protocol logging, and rolling-upgrade scenarios that verify expected accept/reject behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_lockingver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_trace.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_trace.h

Purpose: defines the OCFS2 ftrace tracepoint surface for metadata, allocation, refcount, file I/O, inode, superblock, xattr, reservation, quota, directory, namespace, dentry, export, journal, recovery, buffer I/O, and metadata-cache operations.

Important APIs and types: the file declares reusable `DECLARE_EVENT_CLASS` templates for common argument shapes such as int, unsigned int, `u64`, pointer, string, pairs/triples, btree operations, truncate-log operations, get-block operations, file operations, and refcount-tree operations. It then instantiates many `DEFINE_OCFS2_*_EVENT` and `TRACE_EVENT` entries, including namei-relevant events such as `ocfs2_lookup_ret`, `ocfs2_mknod`, `ocfs2_link`, `ocfs2_unlink_noent`, `ocfs2_double_lock`, `ocfs2_rename`, `ocfs2_rename_not_permitted`, `ocfs2_rename_target_exists`, `ocfs2_rename_disagree`, `ocfs2_rename_over_existing`, `ocfs2_create_symlink_data`, `ocfs2_symlink_begin`, `ocfs2_blkno_stringify`, `ocfs2_orphan_add_begin/end`, and `ocfs2_orphan_del`.

Control flow: when included with tracing enabled, each tracepoint records typed fields through `TP_STRUCT__entry`, assigns values in `TP_fast_assign`, and formats them through `TP_printk`. The header uses the standard tracepoint multi-read pattern and includes `trace/define_trace.h` outside the include guard so one C file can instantiate tracepoint definitions.

State and persistence: tracepoints do not persist filesystem state. They expose transient runtime state such as block numbers, clusters, inode numbers, names, return codes, allocation decisions, and lock flow to ftrace/perf consumers.

Dependencies and integration: depends on Linux tracepoint infrastructure and is included throughout OCFS2 implementation files. It is the main observability integration for debugging cluster races, allocation failures, journal recovery, quota sync, dentry invalidation, and namespace operations.

Risks: tracepoint field or name changes can break user scripts and diagnostics. String handling must avoid reading unstable memory after events. High-frequency tracepoints in allocation, I/O, and metadata-cache paths can add overhead when enabled. Format mistakes can hide the values needed to debug corruption or deadlocks.

Test signals: kernel build with tracing enabled and disabled, `trace-cmd`/ftrace smoke tests for representative events, namespace operation traces from create/unlink/rename, allocation and recovery trace coverage during stress tests, and checks that event formats remain parseable by existing tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/quota.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/quota.h

Purpose: declares OCFS2 quota in-memory structures and the internal quota API for global/local quota files, quota recovery, dquot synchronization, and quota block validation.

Important APIs and types: `struct ocfs2_dquot` embeds the generic VFS `struct dquot` and tracks local quota-file offset, physical block, quota chunk, global reference count, last globally synced space/inode usage, and deferred-drop list membership. `struct ocfs2_mem_dqinfo` describes one quota type, including flags, local chunk/block counts, global quota inode and lock, cached quota inode buffers, local info buffers, qtree info, delayed sync work, and recovery info. `struct ocfs2_quota_recovery` and `struct ocfs2_recovery_chunk` track chunks and bitmaps that need recovery. Exported APIs cover quota recovery begin/finish/free, quota read/write, global info read/write, dquot sync/release, global quota locking, quota block validation and physical reads, local dquot create/release/write, deferred dquot reference dropping, and VFS quota operation/format registrations.

Control flow: quota users initialize and modify generic dquots, then OCFS2 syncs local quota deltas to global quota files under `dqi_gqlock`. Recovery code records quota chunks needing repair for a slot and completes them when quotas are enabled or recovery finishes. Delayed work periodically syncs dquots according to `dqi_syncms`, and deferred drop work releases dquot references outside sensitive paths.

State and persistence: runtime state lives in `ocfs2_dquot`, `ocfs2_mem_dqinfo`, cache objects, locks, delayed work, and recovery lists. Persistent state lives in global and local quota files whose on-disk structures are defined in `ocfs2_fs.h`, including local chunks, local dquot delta records, global qtree records, and quota trailers with block checks.

Dependencies and integration: depends on Linux quota and qtree APIs, slab caches, lists, lock resources, OCFS2 superblock state, and the VFS dquot layer. Namespace code in `namei.c` calls quota initialization and inode/space allocation or rollback during create, symlink, and link-related updates.

Risks: quota synchronization is cluster-sensitive because local deltas and global usage must remain consistent across node crashes. Lock ordering around global quota files can deadlock if mixed with inode or journal locks incorrectly. Recovery bitmaps must match local quota chunks exactly or leak/duplicate usage. Deferred dquot drops must not race with quota shutdown.

Test signals: user and group quota enable/disable tests, multi-node quota allocation and release stress, crash recovery with dirty local quota files, delayed sync behavior, dquot cache lifetime tests, quota block checksum validation, ENOSPC/EDQUOT rollback in create/symlink paths, and VFS quota operation conformance tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/quota.h -->
