# Group Research: group_1057_linux_stable_sources_os_linux_linux_stable_fs_ocfs2_namei_c_sources_afc16270c739

Scope: `Docs/research_subset_a.md`; source tree `sources/os/linux/linux-stable` is included in subset A.

Read coverage: complete read of all listed files, 8,936 total source lines.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/namei.c

Purpose: implements OCFS2 namespace-changing VFS inode operations: lookup, create, mknod, mkdir, link, unlink/rmdir, rename, symlink creation, dentry-lock attachment, and the orphan-directory workflows used for normal unlink, rename-overwrite, direct-I/O append recovery, and creating orphan-staged inodes.

Read coverage: complete file read, 2,945 lines.

Key responsibilities:
- Provides `ocfs2_dir_iops`, wiring OCFS2 directory inodes to VFS create/lookup/link/unlink/rmdir/symlink/mkdir/mknod/rename plus attribute, ACL, xattr, fiemap, and fileattr handlers.
- Creates new dinodes with `ocfs2_mknod_locked()` / `__ocfs2_mknod_locked()`, populating on-disk fields, extent-list or inline-data layout, generation, suballocator location, ownership, timestamps, link count, device id, cluster lock resources, and fsync transaction tracking.
- Performs VFS lookups under parent inode cluster locks, resolves names to block numbers, loads inodes with `ocfs2_iget()`, clears stale maybe-orphan state, and attaches OCFS2 dentry lock state or negative-dentry generation state.
- Implements hard link creation with ordered double-directory locking, source-name revalidation, destination-space preparation, inode link-count journaling, directory insertion, and dentry-lock attach.
- Implements unlink/rmdir by locking parent and child, verifying on-disk directory entry identity, forcing remote dentry invalidation, optionally preparing an orphan-dir entry when the removed inode becomes unlinkable, deleting the parent entry, adjusting link counts and times, and adding normal orphans.
- Implements rename with cluster-wide rename locking for cross-directory directory moves, ancestor checks to avoid directory cycles, ordered parent and child locking, target race checks, target orphaning when overwritten, `..` updates, old-entry deletion, link-count/time updates, and dentry-lock move notification.
- Implements fast and allocated symlink creation, including security xattr setup, quota accounting, cluster reservation for slow symlinks, symlink-data block journaling, and inline symlink storage in the dinode.
- Implements orphan helpers for normal unlink orphans and DIO append orphans, including deterministic orphan names based on inode block numbers and the `dio-` prefix.

Important entry points:
- VFS operations: `ocfs2_lookup()`, `ocfs2_mknod()`, `ocfs2_mkdir()`, `ocfs2_create()`, `ocfs2_link()`, `ocfs2_unlink()`, `ocfs2_rename()`, `ocfs2_symlink()`.
- Creation internals: `ocfs2_get_init_inode()`, `ocfs2_mknod_locked()`, `__ocfs2_mknod_locked()`, `ocfs2_create_symlink_data()`.
- Lock ordering helpers: `ocfs2_double_lock()`, `ocfs2_double_unlock()`, `ocfs2_check_if_ancestor()`, `ocfs2_remote_dentry_delete()`.
- Orphan APIs exported through `namei.h`: `ocfs2_orphan_del()`, `ocfs2_create_inode_in_orphan()`, `ocfs2_add_inode_to_orphan()`, `ocfs2_del_inode_from_orphan()`, `ocfs2_mv_orphaned_inode_to_new()`.

Concurrency and ordering:
- Directory mutations take OCFS2 inode cluster locks and VFS inode mutexes in explicit parent/child/orphan-dir orders; `ocfs2_double_lock()` orders by ancestry and block number to avoid cross-node deadlocks.
- Cross-directory directory renames use the filesystem rename lock to serialize hierarchy moves across cluster nodes.
- Dentry cluster locks are attached before directory entry exposure so remote unlink/downconvert notifications cannot leave stale dentries behind.
- `ocfs2_remote_dentry_delete()` briefly takes an exclusive dentry lock to force other nodes to drop cached aliases before unlink or rename modifies names.
- Orphan-dir helpers return orphan directory inodes locked when callers need to combine orphan entry changes with an outer transaction.
- Signals are blocked after transactions begin in create/link/symlink paths once restart is no longer safe.

Journaling, quota, and allocation:
- Namespace operations reserve inode, metadata, cluster, security xattr, ACL, and directory-insert resources before starting journal transactions.
- New directory creation accounts for inline-data support, indexed-directory metadata, parent link count, and new directory initialization through `ocfs2_fill_new_dir()`.
- Symlink creation distinguishes fast symlinks stored in `ocfs2_dinode.id2.i_symlink` from slow symlinks backed by allocated clusters and `ocfs2_aops`.
- Quota initialization and `dquot_alloc_inode()` / `dquot_free_inode()` / `dquot_alloc_space_nodirty()` cleanup are paired with inode and cluster allocation.

Dependencies:
- Uses OCFS2 directory lookup/insert/delete/update helpers, dcache/dentry locks, DLM glue, inode loading/population, journaling, suballocators, local/global quota hooks, xattr/security/ACL initialization, extent maps, file truncation, and system-file lookup.
- Relies on VFS inode/dentry operations, idmapped mount prototypes, quota core, buffer heads, JBD2 handles, and Linux timestamp/link-count helpers.

Risk and edge cases:
- Many operations revalidate on-disk directory entries after VFS lookup because another cluster node can remove or replace names while local code waits for locks.
- Failed create/symlink after dentry-lock attachment must explicitly tear down `d_fsdata`; otherwise dentry lock resources leak.
- Unlink and rename-overwrite must add last-link files to the orphan dir before commit so crash recovery can finish deletion.
- Rename reports filesystem errors if the new entry is added but old-entry deletion then fails outside an aborted journal.
- Directory ancestry checks are bounded by `MAX_LOOKUP_TIMES`; hitting the bound logs a notice and treats the move as not proven ancestral.
- DIO orphan helpers must recover an existing `OCFS2_DIO_ORPHANED_FL` state before adding a new DIO orphan entry.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/namei.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/namei.h

Purpose: declares OCFS2 namespace/orphan entry points exported from `namei.c` to other OCFS2 modules.

Read coverage: complete file read, 38 lines.

Key contents:
- Defines DIO orphan entry naming constants: `OCFS2_DIO_ORPHAN_PREFIX` as `"dio-"` and `OCFS2_DIO_ORPHAN_PREFIX_LEN` as 4.
- Exposes `ocfs2_dir_iops`, the directory inode operation table implemented in `namei.c`.
- Declares `ocfs2_get_parent()` for export/NFS parent lookup integration.
- Declares normal and DIO orphan manipulation helpers: `ocfs2_orphan_del()`, `ocfs2_create_inode_in_orphan()`, `ocfs2_add_inode_to_orphan()`, `ocfs2_del_inode_from_orphan()`, and `ocfs2_mv_orphaned_inode_to_new()`.

Dependencies:
- Uses OCFS2 superblock, inode, dentry, buffer-head, JBD2 handle, and directory-orphan semantics defined in surrounding OCFS2 headers.

Risk and edge cases:
- Callers must respect lock ownership implied by the prototypes: several orphan helpers expect already locked inode/dinode buffers or return locked orphan directories through the implementation contract.
- The `dio-` prefix is part of on-disk orphan directory naming; changing it would break recovery of existing DIO orphan entries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/namei.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ocfs1_fs_compat.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/ocfs1_fs_compat.h

Purpose: defines the OCFS1-compatible volume header and label structures that OCFS2 writes into the first two sectors so old OCFS1 code detects the partition and fails cleanly instead of mis-mounting it.

Read coverage: complete file read, 94 lines.

Key structures and constants:
- Defines OCFS1 string limits for volume signature, mount point, volume id, label, and cluster name.
- Defines OCFS1 compatibility version `2.0` and signature `"OracleCFS"`.
- `struct ocfs1_vol_disk_hdr` models the OCFS1 sector-0 volume header, including version, signature, mount point, serial/device size, bitmap/public/vote/root offsets, data/root sizes, cluster/node counts, node config offsets, protection bits, and exclusive mount field.
- `struct ocfs1_disk_lock` models the OCFS1 disk lock embedded in the volume label, with explicit padding for historical alignment.
- `struct ocfs1_vol_label` models the sector-1 volume label with disk lock, label, volume id, and cluster name fields.

Dependencies:
- Uses fixed-width Linux integer types only; this header is a disk-layout compatibility contract, not active OCFS2 runtime logic.

Risk and edge cases:
- Structure offsets are annotated and effectively ABI-sensitive. Padding or field-size changes would alter the compatibility sectors.
- These headers are intentionally valid enough for OCFS1 recognition but describe an unmountable OCFS1 volume.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ocfs1_fs_compat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ocfs2.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/ocfs2.h

Purpose: central in-kernel OCFS2 private header defining metadata-cache state, node maps, DLM lock-resource state, mount/recovery/local-allocation enums, the `ocfs2_super` in-memory superblock, feature/read-only helpers, signature validators, cluster/block/page conversion helpers, and endian-safe bitmap helpers.

Read coverage: complete file read, 993 lines.

Key structures:
- `struct ocfs2_caching_info` tracks metadata buffer uptodate/cache membership with a small inline array that expands to an rb-tree, plus transaction ids protected by `trans_inc_lock`.
- `struct ocfs2_node_map` stores up to 256 cluster node bits.
- `struct ocfs2_lock_res` is the generic OCFS2 cluster lock resource: lock name, type, levels, holder counts, blocked/masked waiter lists, AST/unlock actions, DLM LKSB, waitqueue, debug list, optional stats, and lockdep map.
- `struct ocfs2_orphan_scan` stores the cluster-wide orphan scan lock resource and delayed work state.
- `struct ocfs2_super` is the main per-mount state object, holding VFS superblock pointers, root/system inodes, slot info, feature bits, mount options, generation counters, recovery maps/threads, journal, local allocation state and reservations, quota recovery, ECC/allocation stats, cluster stack connection, super/rename/NFS/trim lock resources, downconvert-thread state, truncate-log state, orphan recovery/wipe tracking, indexed-dir hash state, refcount-tree cache, workqueue, sysfs state, and filecheck state.

Feature and state helpers:
- `ocfs2_should_order_data()` enables ordered data for regular files unless writeback data mode is mounted.
- `ocfs2_sparse_alloc()`, `ocfs2_writes_unwritten_extents()`, `ocfs2_supports_append_dio()`, `ocfs2_supports_inline_data()`, `ocfs2_supports_xattr()`, `ocfs2_meta_ecc()`, `ocfs2_supports_indexed_dirs()`, `ocfs2_supports_discontig_bg()`, and `ocfs2_refcount_tree()` test feature bits copied from the superblock.
- `ocfs2_link_max()`, `ocfs2_read_links_count()`, `ocfs2_set_links_count()`, and `ocfs2_add_links_count()` handle OCFS2's normal and indexed-directory link count formats.
- `ocfs2_set_osb_flag()`, `ocfs2_set_ro_flag()`, `ocfs2_is_hard_readonly()`, `ocfs2_is_soft_readonly()`, `ocfs2_is_readonly()`, and `ocfs2_emergency_state()` coordinate soft/hard read-only mount state under `osb_lock`.
- Cluster-stack helpers identify local mounts, userspace stack, o2cb stack, and o2cb global heartbeat.

Geometry helpers:
- Converts between clusters, blocks, bytes, sectors, megabytes, and page indexes using mounted block size and cluster size.
- `ino_from_blkno()` maps a disk block number into a VFS inode number by truncating to `unsigned long`.
- Provides unaligned little-endian bitmap helpers used where OCFS2 bitmaps may not be naturally word-aligned.

Dependencies:
- Includes stack glue, on-disk format definitions, lock-id definitions, ioctl UAPI definitions, blockcheck stats, reservations, and filecheck state.
- Used throughout OCFS2 by allocation, journal, inode, dcache, DLM glue, quota, refcount, recovery, and superblock code.

Risk and edge cases:
- `struct ocfs2_super` fields have varied locking rules; comments identify critical protection for generation/flags/steal slots, local alloc bits, local alloc state, truncate-log cluster counts, and downconvert lists.
- The lock-resource flags drive asynchronous DLM state transitions; changing flag semantics can break downconvert and upconvert races.
- Feature helpers operate on in-memory feature copies; callers that depend on current disk state must ensure mount/superblock state is initialized and stable.
- `ino_from_blkno()` can truncate block numbers on 32-bit systems unless `OCFS2_MOUNT_INODE64` and VFS/export handling account for it.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ocfs2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_fs.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_fs.h

Purpose: defines OCFS2's on-disk ABI: revision numbers, feature flags, object signatures, inode/superblock/extent/directory/allocator/refcount/xattr/quota structures, system inode names, layout-capacity helpers, and directory/type utilities shared by kernel and userspace.

Read coverage: complete file read, 1,616 lines.

Format constants and features:
- Defines OCFS2 revision `0.90`, superblock block number 2, cluster/block size limits, object signatures for superblock/dinode/extent/group/xattr/dir trailer/dx root/dx leaf/refcount block, and supported compat/incompat/ro-compat masks.
- Incompat features include local mount, sparse allocation, inline data, extended slot map, userspace stack, xattrs, indexed dirs, metadata ECC, refcount tree, discontiguous block groups, clusterinfo, and append DIO. Heartbeat-only and resize/tunefs-in-progress bits are intentionally not mount-supported in the same way.
- Defines dinode flags such as valid, orphaned, system, superblock, local alloc, bitmap, journal, heartbeat, chain, dealloc, quota, and DIO orphaned.
- Defines dynamic inode features for inline data, xattrs, indexed dirs, and refcount-tree attachment.
- Maps user-visible inode attributes to Linux `FS_*` flags and defines extent flags for unwritten and refcounted extents.

System files and names:
- Enumerates global and slot-local system inode types: bad block, global inode alloc, slot map, heartbeat, global bitmap, global quotas, orphan dir, extent alloc, inode alloc, journal, local alloc, truncate log, and local quota files.
- `ocfs2_system_inodes[]` defines each system inode name template, required dinode flags, and file mode.
- `ocfs2_system_inode_is_global()` and `ocfs2_sprintf_system_inode_name()` distinguish single-copy system inodes from per-slot inodes.

Major on-disk structures:
- `struct ocfs2_block_check` stores metadata CRC/ECC trailers.
- `struct ocfs2_extent_rec`, `ocfs2_extent_list`, `ocfs2_extent_block` define extent trees.
- `struct ocfs2_chain_rec`, `ocfs2_chain_list`, and `ocfs2_group_desc` define allocation chains and bitmap groups, including discontiguous block-group support.
- `struct ocfs2_slot_map`, `ocfs2_extended_slot`, and `ocfs2_slot_map_extended` define old and extended slot maps.
- `struct ocfs2_cluster_info` stores cluster stack label, flags, and cluster name.
- `struct ocfs2_super_block` is embedded in a dinode and stores revision, state, features, root/system dir blocks, block/cluster geometry, slot count, label, UUID, cluster info, xattr inline size, and indexed-dir hash seeds.
- `struct ocfs2_dinode` is the central inode block, with ownership, size, mode, link count high/low, flags, timestamps, block number, generation, orphan slots, xattr/refcount/dx pointers, checksum, and a union for superblock/local alloc/chain list/extent list/truncate log/inline data/symlink payload.
- Directory structures include packed `ocfs2_dir_entry`, `ocfs2_dir_block_trailer`, `ocfs2_dx_entry`, `ocfs2_dx_entry_list`, `ocfs2_dx_root_block`, and `ocfs2_dx_leaf`.
- Refcount structures include `ocfs2_refcount_rec`, `ocfs2_refcount_list`, and `ocfs2_refcount_block`.
- Xattr structures include `ocfs2_xattr_entry`, `ocfs2_xattr_header`, value/tree roots, and xattr blocks.
- Quota disk structures define global/local quota magic/version arrays, headers, global quota info/records, local quota info/chunks/records, and quota block trailers.

Layout helpers:
- Kernel helpers calculate fast symlink capacity, inline-data capacity with inline xattrs, extent records per dinode/extent block/group descriptor/dx root/refcount block, chain records per inode, dx entries per leaf/root, local alloc bitmap size, group bitmap size, truncate-log capacity, backup superblock locations, xattr records per block, and low 32 bits of refcount record positions.
- Userspace-compatible helper variants are provided outside `__KERNEL__` for several blocksize-based calculations.
- `ocfs2_xattr_set_local()`, `ocfs2_xattr_is_local()`, `ocfs2_xattr_set_type()`, and `ocfs2_xattr_get_type()` manipulate xattr entry type/local bits.
- `ocfs2_set_de_type()` maps inode modes to directory entry file types, and `ocfs2_gd_is_discontig()` identifies discontiguous group descriptors from layout/counter fields.

Dependencies:
- Exposes disk structures to the kernel and userspace OCFS2 tooling; depends on Linux magic numbers, fixed-width little-endian types, and flexible array/count annotations.

Risk and edge cases:
- This header is ABI-sensitive. Field order, sizes, signatures, feature bits, and helper calculations must remain compatible with existing disks and userspace tools.
- Superblock data must fit inside the smallest 512-byte block as embedded in `ocfs2_dinode.id2`; comments explicitly reserve space for that constraint.
- Discontiguous group detection depends on `bg_size` positioning `bg_list` exactly after the filler bitmap and on `l_next_free_rec` being meaningful only in that case.
- Refcount records use 64-bit physical cluster positions while some tree indexing uses low 32 bits; callers must preserve the split/index assumptions.
- The non-kernel `ocfs2_group_bitmap_size()` helper references `sb->s_blocksize` even though its parameter is `blocksize`, which is notable for userspace consumers of this header.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_ioctl.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_ioctl.h

Purpose: defines OCFS2 ioctl UAPI structures, command numbers, request codes, and flags for space reservation, online resize/group add, reflink, filesystem information queries, and extent movement.

Read coverage: complete file read, 224 lines.

Key UAPI groups:
- `struct ocfs2_space_resv` and `OCFS2_IOC_*SP*` commands mirror XFS-style space reservation/free allocation ioctl layouts; comments state `ALLOCSP*` and `FREESP*` are listed for completeness but unsupported.
- `struct ocfs2_new_group_input` with `OCFS2_IOC_GROUP_EXTEND`, `OCFS2_IOC_GROUP_ADD`, and `OCFS2_IOC_GROUP_ADD64` supports online resize/group descriptor additions.
- `struct reflink_arguments` and `OCFS2_IOC_REFLINK` pass old path, new path, and preserve flag for legacy OCFS2 reflink operations.
- `struct ocfs2_info` plus `struct ocfs2_info_request` and typed payloads implement batched `OCFS2_IOC_INFO` requests for cluster size, block size, max slots, label, UUID, feature bits, journal size, free inode stats, and free fragmentation stats.
- `struct ocfs2_move_extents` and `OCFS2_IOC_MOVE_EXT` define manual/automatic extent movement and defragmentation requests.

Constants and flags:
- `OCFS2_INFO_MAX_REQUEST` caps batched info requests at 50.
- `OCFS2_INFO_MAGIC` identifies valid info request objects.
- `OCFS2_INFO_FL_NON_COHERENT` asks the kernel to avoid cluster-coherent locking if possible; `OCFS2_INFO_FL_FILLED` and `OCFS2_INFO_FL_ERROR` are kernel-returned status flags.
- Move-extents flags include automatic defrag, partial defrag, and completion indication.

Dependencies:
- References `OCFS2_VOL_UUID_LEN`, `OCFS2_MAX_VOL_LABEL_LEN`, and `OCFS2_MAX_SLOTS` from OCFS2 disk format definitions.
- Consumed by OCFS2 ioctl dispatch in `ioctl.c` and by userspace tools issuing these ioctls.

Risk and edge cases:
- Pointer fields are encoded as `__u64` for userspace ABI stability and compat handling.
- Packed label/UUID info structures avoid unintended padding changes.
- Request `ir_size` and `ir_code` validation in the implementation depends on these exact structure sizes and enum values.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_lockid.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_lockid.h

Purpose: defines OCFS2 cluster lock-id layout, lock type enum values, single-character lock type tags, and human-readable lock type names.

Read coverage: complete file read, 117 lines.

Key contents:
- Documents lock id strings as 32 bytes: one type byte, six reserved pad characters, 16 hex block-number characters, 8 hex generation characters, and NUL terminator.
- Defines `OCFS2_LOCK_ID_MAX_LEN`, `OCFS2_LOCK_ID_PAD`, and `OCFS2_DENTRY_LOCK_INO_START`.
- Enumerates lock types for metadata, data, super, rename, read/write, dentry, open, flock, quota info, NFS sync, orphan scan, refcount, and trim-fs locks.
- `ocfs2_lock_type_char()` maps lock types to DLM name prefixes such as `M`, `D`, `S`, `R`, `W`, `N`, `O`, `F`, `Q`, `Y`, `P`, `T`, and `I`.
- `ocfs2_lock_type_strings[]` and `ocfs2_lock_type_string()` provide debug-readable lock type names.

Dependencies:
- Used by DLM glue and debug paths that construct, parse, and report OCFS2 lock resources.

Risk and edge cases:
- Lock type chars and positions are protocol-visible through DLM lock names; changes can break compatibility between nodes.
- `ocfs2_lock_type_string()` only guards enum range with `BUG_ON()` under `__KERNEL__`; non-kernel consumers must pass valid enum values.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_lockid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_lockingver.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_lockingver.h

Purpose: defines the OCFS2 cluster locking protocol version.

Read coverage: complete file read, 22 lines.

Key contents:
- Declares locking protocol major version `1` and minor version `0`.
- Comments identify this as the initial OCFS2 1.4 locking version and point readers to `dlmglue.c` for protocol details.

Dependencies:
- Used by cluster stack/DLM compatibility checks so nodes agree on the lock protocol before sharing a volume.

Risk and edge cases:
- Version values are cluster-compatibility gates; changing them requires corresponding protocol negotiation and compatibility handling in DLM glue.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_lockingver.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_trace.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_trace.h

Purpose: declares the OCFS2 ftrace tracepoint surface for allocation, local allocation, resize, suballocation, refcount/COW, address-space operations, mmap, file operations, inode lifecycle, extent maps, slot maps, heartbeat, superblock operations, xattrs, reservations, quotas, directory operations, namespace operations, dcache, export/NFS file handles, journaling/recovery, buffer-head I/O, and metadata-cache tracking.

Read coverage: complete file read, 2,764 lines.

Tracepoint infrastructure:
- Sets `TRACE_SYSTEM` to `ocfs2` and includes `<linux/tracepoint.h>`.
- Defines reusable event classes for common payload shapes: int, uint, ull, pointer, string, pairs/triples/quads of integers and block numbers, btree operations, truncate-log operations, refcount records, get-block events, file operations, xattr lookup events, and dentry operations.
- Ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE ocfs2_trace`, and `<trace/define_trace.h>` outside the include guard as required by Linux tracepoint headers.

Subsystem coverage:
- Allocation and truncate-log events cover btree rotations/splits/inserts/removals, extent writes/truncates, trim/discard, cached deallocation, local allocation windowing, resize group add/extend, suballocator group allocation/search/claim/free, and group descriptor validation.
- Refcount events cover refcount block validation, tree creation/purge, record insert/split/increase/decrease, metadata credit calculation, COW duplication, refcount flag changes, cluster replacement, and writable-cluster conversion.
- AOP/file/mmap events cover block mapping, inline writes, write begin/end, page faults, file open/release/read/write/splice/fsync, truncation, allocation extension, zeroing, setattr, SUID removal, partial cluster zeroing, inode write preparation, and read/splice return values.
- Inode events cover iget, actor matching, inode population/read/validation/filecheck repair, orphan recovery state checks, delete/wipe queries, cleanup, clear, revalidation, and dirty marking.
- Super/recovery events cover remount, fill_super, option parsing, put_super, statfs, dismount, super initialization, journal commit/access/dirty/init/shutdown, recovery slots, recovery thread, journal replay, dead node marking, orphan scan/recovery, and mount waits.
- Directory/name/dcache/export events cover directory block validation/search, indexed directory searches/rebalances, lookup/create/mkdir/unlink/symlink/mknod/link/rename, orphan add/delete, dentry revalidation/attach, NFS dentry lookup, parent lookup, and file handle encoding.
- Xattr, reservation, quota, extent-map, slot-map, heartbeat, buffer I/O, and uptodate-cache events expose their module-specific state transitions and parameters.

Dependencies:
- Tracepoint users in OCFS2 C files call the generated `trace_ocfs2_*` functions; event declarations must match call-site argument types.
- Uses Linux tracepoint macros, string assignment helpers, device major/minor extraction, and pointer/integer formatting.

Risk and edge cases:
- Tracepoint ABI is externally observable through ftrace/perf tooling; renaming events or changing field order/types can break diagnostics.
- Several tracepoints copy names with `__string()` / `__assign_str()` and print with explicit lengths; call sites must pass valid pointers for traced names.
- Pointer values and block numbers are intentionally exposed for debugging but can be sensitive in production traces.
- Event-class macro reuse reduces boilerplate but means signature changes affect many events at once.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/quota.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/quota.h

Purpose: declares OCFS2 quota in-memory structures, quota recovery structures, global/local quota helpers, quota I/O APIs, dquot lifecycle hooks, and exported VFS quota operations/format objects.

Read coverage: complete file read, 123 lines.

Key structures:
- `struct ocfs2_dquot` embeds a generic VFS `struct dquot` and adds local quota file offset, physical quota block, owning chunk, global use count, last globally synced space/inode usage, and a lockless-list node for deferred reference dropping.
- `struct ocfs2_recovery_chunk` records one local quota chunk requiring crashed-node recovery, with chunk number and bitmap of entries to replay.
- `struct ocfs2_quota_recovery` stores per-quota-type recovery chunk lists.
- `struct ocfs2_mem_dqinfo` stores per-quota-type runtime state: flags, chunk/block counts, chunk list, global quota inode, qinfo lock resource, cached global/local info buffers, qtree state, delayed sync work, and optional recovery information.
- `struct ocfs2_quota_chunk` tracks a local quota chunk number and header buffer.

Declared APIs:
- Recovery: `ocfs2_begin_quota_recovery()`, `ocfs2_finish_quota_recovery()`, `ocfs2_free_quota_recovery()`.
- Physical and logical quota I/O: `ocfs2_quota_read()`, `ocfs2_quota_write()`, `ocfs2_read_quota_phys_block()`, `ocfs2_validate_quota_block()`.
- Global quota state: `ocfs2_global_read_info()`, `ocfs2_global_write_info()`, `__ocfs2_sync_dquot()`, `ocfs2_sync_dquot()`, `ocfs2_global_release_dquot()`, `ocfs2_lock_global_qf()`, `ocfs2_unlock_global_qf()`.
- Local dquot lifecycle: `ocfs2_create_local_dquot()`, `ocfs2_local_release_dquot()`, `ocfs2_local_write_dquot()`, `ocfs2_drop_dquot_refs()`.
- Exports slab caches, qtree operations, `ocfs2_quota_operations`, and `ocfs2_quota_format`.

Dependencies:
- Includes Linux quota/qtree/list/slab types and OCFS2 core state.
- Implemented mainly by `quota_global.c` and `quota_local.c`, with recovery coordination from journal/recovery paths.

Risk and edge cases:
- Quota state spans local per-node files and global qtree records; callers must respect lock ordering and sync/recovery ownership from the implementation.
- Deferred dquot reference dropping exists because some contexts, such as downconvert paths, cannot safely perform final quota release work inline.
- `OCFS2_MAXQUOTAS` fixes support to user and group quotas.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/quota.h -->