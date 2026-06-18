# Group Research: OCFS2 namespace, format, locking, tracing, ioctl, and quota headers

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux/fs/ocfs2`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/namei.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/namei.c

Role: Implements OCFS2 VFS namespace operations for lookup, create, mkdir, mknod, link, unlink/rmdir, rename, symlink, and orphan-directory transitions. It installs `ocfs2_dir_iops`, making this file the directory inode operation table for OCFS2.

Key responsibilities:
- `ocfs2_lookup()` validates name length, locks the parent directory, maps name to block number, gets the inode, clears stale `OCFS2_INODE_MAYBE_ORPHANED`, uses `d_splice_alias()`, and attaches OCFS2 dentry locking or a generation marker for negative dentries.
- `ocfs2_get_init_inode()` creates a VFS inode, initializes ownership/mode, sets directory link count to 2, strips SGID as needed, and initializes quota state.
- `ocfs2_mknod()` is the common create path for regular files, directories, device nodes, and named pipes. It reserves inode/data/metadata allocation contexts, computes ACL/security xattr needs, starts a journal transaction, allocates quota, creates the dinode, initializes directory contents if needed, writes ACL/security xattrs, attaches the dentry lock, adds the directory entry, hashes the inode, and instantiates the dentry.
- `__ocfs2_mknod_locked()` formats a new `ocfs2_dinode`: generation, owner, mode, device number, link count, timestamps, signatures, validity flags, inline-data or extent-list initialization, inode population, lock resource creation, and fsync transaction tracking.
- `ocfs2_mknod_locked()` claims a new inode from suballocation and delegates formatting to `__ocfs2_mknod_locked()`.
- `ocfs2_mkdir()` and `ocfs2_create()` are thin wrappers over `ocfs2_mknod()` with `S_IFDIR` or `S_IFREG`.
- `ocfs2_link()` locks source and destination parent directories with `ocfs2_double_lock()`, verifies the old name still refers to the expected inode, locks the target inode, checks link limits, journals link-count and ctime updates, adds the new dirent, attaches dentry locking, and instantiates the hard link.
- `ocfs2_unlink()` covers unlink and rmdir. It locks parent and child, verifies the dirent still targets the expected inode, checks directory emptiness, forces remote dentry invalidation, prepares the orphan dir when the link count will reach zero, deletes the parent entry, updates link counts and parent timestamps, and adds the inode to the orphan dir when needed.
- `ocfs2_rename()` serializes cross-directory directory renames with the cluster rename lock, locks both parents in deadlock-safe order, locks old and possibly new child inodes, validates source and target races, updates or adds target entries, removes the old entry, updates `..` for moved directories, adjusts link counts, optionally orphans overwritten targets, and moves OCFS2 dentry lock state.
- `ocfs2_symlink()` creates fast inline symlinks when the target fits in `ocfs2_fast_symlink_chars()`, otherwise reserves a data cluster, adds extent-backed symlink data via `ocfs2_create_symlink_data()`, initializes xattrs/security, and installs symlink inode operations.
- `ocfs2_create_symlink_data()` writes the symlink target plus NUL into newly allocated data blocks under journal access.
- `ocfs2_check_if_ancestor()` walks `..` links with a capped lookup count to help order nested directory locks and prevent invalid directory renames.
- `ocfs2_double_lock()` orders two directory inode locks by ancestry and block number, using lockdep subclasses for rename vs parent locking.

Orphan handling:
- Orphan names are block numbers formatted as 16 hex characters; direct-IO append orphans add the `dio-` prefix from `namei.h`.
- `ocfs2_lookup_lock_orphan_dir()` gets and exclusively locks the current slot’s orphan directory.
- `ocfs2_prepare_orphan_dir()` and `__ocfs2_prepare_orphan_dir()` compute the orphan name and prepare an insertion slot.
- `ocfs2_orphan_add()` journals orphan-dir and inode changes, inserts the orphan dirent, sets `OCFS2_ORPHANED_FL` or `OCFS2_DIO_ORPHANED_FL`, records the slot, and adjusts orphan directory link count for directories.
- `ocfs2_orphan_del()` removes an orphan dirent and fixes orphan directory link count.
- `ocfs2_prep_new_orphaned_file()` reserves a new inode location before inode creation so the orphan dirent can be named by the future dinode block.
- `ocfs2_create_inode_in_orphan()` creates a new unlinked inode directly in the orphan directory and takes its open lock.
- `ocfs2_add_inode_to_orphan()` handles append-DIO orphaning, including recovery if an inode is already marked `OCFS2_DIO_ORPHANED_FL`.
- `ocfs2_del_inode_from_orphan()` removes an append-DIO orphan, clears DIO orphan flags, and optionally updates inode size.
- `ocfs2_mv_orphaned_inode_to_new()` moves a previously orphaned inode into a visible directory entry, clears orphan state, restores link count, attaches dentry locking, and instantiates the dentry.

Concurrency and integrity:
- Directory operations use OCFS2 inode cluster locks, dentry locks, the global rename lock, and careful lock ordering to handle multi-node races.
- Journal transactions wrap metadata mutations; rollback paths repair link counts, quota allocations, dentry lock state, and newly created inodes.
- Dentry operations are intentionally ordered so cluster lock release happens after dentry insertion/attachment, preventing stale negative or disconnected dentries after remote unlink/create races.
- Quota initialization/allocation/freeing is integrated into create, symlink, link/unlink, and orphan paths.
- Signal blocking is used once transactions become non-restartable.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/namei.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/namei.h

Role: Declares OCFS2 namespace/orphan interfaces shared outside `namei.c`.

Key contents:
- Defines direct-IO orphan name prefix constants: `OCFS2_DIO_ORPHAN_PREFIX` as `"dio-"` and `OCFS2_DIO_ORPHAN_PREFIX_LEN` as `4`.
- Exports `ocfs2_dir_iops`, the directory inode operations table implemented in `namei.c`.
- Declares `ocfs2_get_parent()` for NFS/export parent lookup.
- Declares generic orphan deletion with `ocfs2_orphan_del()`.
- Declares orphan-first inode creation and movement helpers:
  - `ocfs2_create_inode_in_orphan()`
  - `ocfs2_add_inode_to_orphan()`
  - `ocfs2_del_inode_from_orphan()`
  - `ocfs2_mv_orphaned_inode_to_new()`

Design notes:
- The header separates visible VFS namespace operations from cross-file orphan APIs used by file, truncate, append-DIO, and recovery paths.
- The `dio` flag in orphan helpers lets the same orphan directory mechanism distinguish normal unlink orphans from append direct-IO recovery entries.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/namei.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ocfs1_fs_compat.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/ocfs1_fs_compat.h

Role: Defines legacy OCFS1-compatible sector layouts that OCFS2 writes at the start of a volume so OCFS1 tools/drivers can detect the partition and fail cleanly instead of mis-mounting it.

Key contents:
- OCFS1 size constants for volume signature, mount point, volume ID, label, and cluster name.
- OCFS1 version constants: major `2`, minor `0`, signature `"OracleCFS"`.
- `struct ocfs1_vol_disk_hdr`: sector-0 OCFS1 volume header with version, signature, mount point, size/offset fields, cluster sizing, node count, config offsets, and mount/exclusive fields.
- `struct ocfs1_disk_lock`: legacy disk lock format embedded in the volume label sector, with master, lock byte, timestamps, node numbers, node map, and sequence number.
- `struct ocfs1_vol_label`: sector-1 label block containing the disk lock, volume label, volume ID, and cluster name fields.

Design notes:
- These are compatibility disk structures, not active OCFS2 metadata.
- The explicit padding in `ocfs1_disk_lock` preserves the old layout while making alignment visible in C.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ocfs1_fs_compat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ocfs2.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/ocfs2.h

Role: Main in-kernel OCFS2 runtime header. It pulls in on-disk definitions, ioctl ABI, lock IDs, block checking, reservations, and filecheck state, then defines core runtime structures and inline helpers used across the filesystem.

Key contents:
- Metadata cache abstraction:
  - `OCFS2_CACHE_INFO_MAX_ARRAY`
  - `enum ocfs2_caching_info_flags`
  - `struct ocfs2_caching_info`
  - `ocfs2_metadata_cache_get_super()` prototype
- Cluster node maps via `struct ocfs2_node_map`, limited to 256 nodes.
- Cluster lock machinery:
  - AST/unlock action enums
  - lock resource flags such as `OCFS2_LOCK_ATTACHED`, `BUSY`, `BLOCKED`, `NEEDS_REFRESH`, `QUEUED`, `PENDING`
  - `struct ocfs2_lock_res`, including holders, requested/blocking levels, LVB, wait queue, debug list, optional stats, and lockdep map
- Orphan scan state:
  - `enum ocfs2_orphan_reco_type`
  - `enum ocfs2_orphan_scan_state`
  - `struct ocfs2_orphan_scan`
- Volume, allocation, local allocation, mount option, journal trigger, and recovery-state enums.
- `struct ocfs2_super`, the central mounted filesystem state:
  - superblock/root/system inodes
  - slot info and local/global system inode arrays
  - feature flags, mount options, cluster stack identity
  - generation counters, slot/node identity, cluster/block sizing
  - recovery maps/thread, journal pointer, checkpoint waiters
  - local allocation, reservation maps, truncate log, orphan scan, quota recovery
  - DLM connection and lock resources
  - downconvert thread state, blocked lock list, workqueue
  - sysfs/debug/filecheck state
- `OCFS2_SB(sb)` cast helper.

Important inline behavior:
- Feature checks: sparse allocation, unwritten extents, append DIO, inline data, xattrs, metadata ECC, indexed directories, discontiguous block groups, refcount trees, local mount, extended slot map.
- Link-count helpers read/write 32-bit logical link counts split across low/high 16-bit dinode fields.
- Read-only/emergency helpers atomically update and inspect OSB read-only/error flags.
- Cluster stack helpers distinguish userspace stacks, classic `o2cb`, and global heartbeat.
- Signature validation macros check dinodes, extent blocks, group descriptors, xattr blocks, dir trailers, dx roots/leaves, and refcount blocks.
- Unit conversion helpers translate among bytes, sectors, blocks, clusters, pages, and megabytes.
- Bitmap helpers provide little-endian bit operations and unaligned-bit accessors.

Design notes:
- This file is runtime-oriented, while `ocfs2_fs.h` is format-oriented.
- Most small helpers are deliberately inline because OCFS2 code constantly checks feature bits and performs cluster/block conversions.
- `struct ocfs2_super` is the primary cross-subsystem coupling point for allocation, journaling, DLM, recovery, quota, orphan cleanup, and mount policy.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ocfs2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ocfs2_fs.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/ocfs2_fs.h

Role: Defines OCFS2 on-disk ABI: revisions, feature flags, signatures, limits, system inode names, directory formats, dinodes, allocators, extents, xattrs, refcount trees, quota formats, and size calculation helpers. This file is shared with userspace-aware code paths through `#ifdef __KERNEL__` variants.

Key constants and feature flags:
- Revision level `0.90`.
- Superblock location `OCFS2_SUPER_BLOCK_BLKNO == 2`.
- Cluster limits: 4 KiB to 1 MiB; block limits: 512 bytes to 4 KiB.
- Object signatures for superblock, dinode, extent block, group descriptor, xattr block, directory trailer, dx root/leaf, and refcount block.
- Supported compat/incompat/ro-compat masks.
- Incompat features include local mount, sparse alloc, inline data, userspace stack, extended slot map, xattr, metadata ECC, indexed dirs, refcount tree, discontiguous block groups, clusterinfo, and append DIO.
- Special non-supported mount-blocking flags include heartbeat device, resize in progress, and tunefs in progress.
- Dinode flags cover valid, orphaned, system inode roles, local alloc, bitmap, journal, heartbeat, chain allocator, truncate log, quota, and direct-IO orphan state.
- Dynamic dinode features cover inline data, xattr presence, inline xattrs, indexed directories, and refcounted data.
- Extent flags cover unwritten and refcounted extents.
- Limits include filename length 255, slots 255, UUID length 16, volume label 64, stack label 4, cluster name 16, minimum journal size 4 MiB, and minimum inline xattr size 256.

System inode model:
- Enumerates global system inodes: bad blocks, global inode allocator, slot map, heartbeat, global bitmap, user quota, group quota.
- Enumerates per-slot local system inodes: orphan dir, extent allocator, inode allocator, journal, local alloc, truncate log, local user quota, local group quota.
- `ocfs2_system_inodes[]` maps each type to name format, inode flags, and mode.
- Helpers identify global system inode types and format names with or without slot numbers.

Core on-disk structures:
- `struct ocfs2_block_check`: CRC32/ECC trailer embedded in metadata when meta-ECC is enabled.
- `struct ocfs2_extent_rec`, `ocfs2_extent_list`, and `ocfs2_extent_block`: extent B-tree records and blocks.
- `struct ocfs2_chain_rec`, `ocfs2_chain_list`, `ocfs2_group_desc`: chain allocator and group bitmap metadata, including discontiguous block group support.
- `struct ocfs2_truncate_log` and `ocfs2_truncate_rec`: deferred deallocation log records.
- `struct ocfs2_slot_map`, `ocfs2_extended_slot`, `ocfs2_slot_map_extended`: old and extended cluster slot maps.
- `struct ocfs2_cluster_info`: cluster stack label, stack flags, and cluster name.
- `struct ocfs2_super_block`: superblock payload stored inside a dinode, constrained to fit in the minimum block size.
- `struct ocfs2_local_alloc`: per-slot local allocation bitmap.
- `struct ocfs2_inline_data`: inline file/directory data header.
- `struct ocfs2_dinode`: central inode-on-disk format containing identity, owner, size, mode, link counts, flags, timestamps, xattr/refcount pointers, suballocator location, DIO orphan slot, and unioned payload for superblock, local alloc, chain list, extent list, truncate log, inline data, or symlink bytes.
- `struct ocfs2_dir_entry`, `ocfs2_dir_block_trailer`, `ocfs2_dx_entry`, `ocfs2_dx_entry_list`, `ocfs2_dx_root_block`, `ocfs2_dx_leaf`: unindexed and indexed directory formats.
- `struct ocfs2_refcount_rec`, `ocfs2_refcount_list`, `ocfs2_refcount_block`: reflink/reference count tree format.
- Xattr structures: `ocfs2_xattr_entry`, `ocfs2_xattr_header`, `ocfs2_xattr_value_root`, `ocfs2_xattr_tree_root`, `ocfs2_xattr_block`, with helpers for local/external flag and type packing.
- Quota disk structures: global/local magic/version arrays, quota headers, global info and dquot blocks, local quota info/chunks/dquot deltas, quota block trailer, and trailer-location helper.

Sizing helpers:
- Kernel helpers compute fast symlink payload, inline data size with inline xattrs, extent records per dinode/extent block/group desc/dx root/refcount block, chain records per dinode, dx entries per root/leaf, local allocation bitmap size, group bitmap size, truncate records per inode, backup superblock block numbers, xattr records per block, and refcount records per block.
- Non-kernel variants provide similar calculations using blocksize arguments for userspace tooling.
- `ocfs2_set_de_type()` maps inode mode to directory entry file type.
- `ocfs2_gd_is_discontig()` detects group descriptors whose bitmap area is followed by a nonempty extent list.

Design notes:
- Layout comments include fixed offsets, making this header the canonical disk-format reference.
- The superblock is embedded in a dinode payload and explicitly constrained to fit within a 512-byte minimum block payload.
- Directory indexing, xattrs, refcounting, metadata ECC, append DIO, and discontiguous block groups are all represented as feature-gated disk formats here.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ocfs2_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ocfs2_ioctl.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/ocfs2_ioctl.h

Role: Defines OCFS2 userspace ioctl ABI structures and command numbers.

Key contents:
- `struct ocfs2_space_resv`: XFS-compatible space reservation argument layout. `ALLOCSP*` and `FREESP*` commands are declared for completeness but documented as unsupported.
- Space ioctls:
  - `OCFS2_IOC_ALLOCSP`
  - `OCFS2_IOC_FREESP`
  - `OCFS2_IOC_RESVSP`
  - `OCFS2_IOC_UNRESVSP`
  - 64-bit variants for alloc/free/reserve/unreserve
- Online resize input:
  - `struct ocfs2_new_group_input`
  - `OCFS2_IOC_GROUP_EXTEND`
  - `OCFS2_IOC_GROUP_ADD`
  - `OCFS2_IOC_GROUP_ADD64`
- Reflink ABI:
  - `struct reflink_arguments`
  - `OCFS2_IOC_REFLINK`
- Batched info ABI:
  - `struct ocfs2_info`
  - base `struct ocfs2_info_request`
  - typed requests for cluster size, block size, max slots, label, UUID, feature masks, journal size, free inode stats, and free-fragmentation stats
  - `enum ocfs2_info_type`
  - request flags for non-coherent hint, filled response, and per-request error
  - `OCFS2_IOC_INFO`
- Extent movement/defragment ABI:
  - `struct ocfs2_move_extents`
  - flags for auto defrag, partial defrag, and completion
  - `OCFS2_IOC_MOVE_EXT`

Design notes:
- Structures use fixed-width integer types and reserved fields to preserve ABI compatibility.
- The info ioctl is explicitly designed as small request records to preserve backward and forward compatibility.
- This header is pulled into `ocfs2.h`, so kernel code can share exact ioctl ABI definitions with userspace-facing handlers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ocfs2_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ocfs2_lockid.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/ocfs2_lockid.h

Role: Defines the OCFS2 DLM lock-name format and lock type identifiers.

Key contents:
- Lock ID layout:
  - byte 0: lock type character
  - bytes 1-6: reserved pad `"000000"`
  - bytes 7-22: block number as 16 hex characters
  - bytes 23-30: inode generation as 8 hex characters
  - byte 31: NUL
- `OCFS2_LOCK_ID_MAX_LEN` is 32.
- `OCFS2_DENTRY_LOCK_INO_START` marks the inode-number start offset for dentry lock names.
- `enum ocfs2_lock_type` covers metadata, data, super, rename, read/write, dentry, open, flock, quota info, NFS sync, orphan scan, refcount, trimfs, and count.
- `ocfs2_lock_type_char()` maps lock types to single-character DLM name prefixes:
  - meta `M`, data `D`, super `S`, rename `R`, rw `W`, dentry `N`, open `O`, flock `F`, quota `Q`, NFS sync `Y`, orphan scan `P`, refcount `T`, trimfs `I`
- `ocfs2_lock_type_strings[]` maps lock types to human-readable debug strings.
- `ocfs2_lock_type_string()` returns the debug string and asserts valid types under `__KERNEL__`.

Design notes:
- The compact lock name encodes enough object identity for cluster-wide DLM coordination and debugging.
- Read/write uses `W` because `R` is already used by rename.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ocfs2_lockid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ocfs2_lockingver.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/ocfs2_lockingver.h

Role: Defines the OCFS2 cluster locking protocol version.

Key contents:
- `OCFS2_LOCKING_PROTOCOL_MAJOR` is `1`.
- `OCFS2_LOCKING_PROTOCOL_MINOR` is `0`.
- Comment records version `1.0` as the initial locking version from OCFS2 1.4 and points readers to `dlmglue.c` for protocol details.

Design notes:
- This small header centralizes protocol version constants used when validating cluster locking compatibility.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ocfs2_lockingver.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ocfs2_trace.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/ocfs2_trace.h

Role: Defines the OCFS2 ftrace tracepoint catalogue. It sets `TRACE_SYSTEM ocfs2`, declares reusable event classes, instantiates trace events for most OCFS2 subsystems, and ends with `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `<trace/define_trace.h>`.

Reusable event classes:
- Single-value classes for `int`, `unsigned int`, `unsigned long long`, pointer, and string.
- Multi-value numeric classes for common combinations of ints, uints, and 64-bit values.
- Specialized classes for B-tree operations, truncate-log operations, refcount tree records, get-block calls, file operations, xattr lookup, and dentry operations.
- Macros such as `DEFINE_OCFS2_INT_EVENT()` and `DEFINE_OCFS2_ULL_UINT_EVENT()` reduce boilerplate for simple tracepoints.

Subsystem trace coverage:
- `alloc.c`: extent B-tree insertion, split, rotation, truncate commit, extent validation, unwritten extents, trim/discard, and allocation tree changes.
- `truncate_log.c`/deallocation paths: truncate-log append/replay/flush, recovery, cached cluster/block frees, and dealloc runs.
- `localalloc.c`: local allocation sizing, selection, bitmap scanning, sync back to main allocator, and new allocation windows.
- `resize.c`: group extension and group addition.
- `suballoc.c`: group descriptor validation, block group allocation, suballocator reservation/claim/free, chain search, and inode bit tests.
- `refcounttree.c`: refcount block validation, refcount tree creation/purge, record insertion/splitting, refcount increase/decrease, metadata credit calculation, COW cluster replacement, and making clusters writable.
- `aops.c`: `get_block`, symlink block mapping, readpage/bmap, inline write attempts, write begin, and inline write completion.
- `mmap.c`: page fault tracing.
- `file.c`: open/release/sync/read/write/splice, truncate, allocation extension, zeroing, setattr, suid removal, partial-cluster zeroing, range removal, and write preparation.
- `inode.c`: iget lifecycle, inode population, orphan recovery state checks, inode block validation/filecheck repair, delete/wipe decisions, revalidation, and dirty marking.
- `extent_map.c`: virtual block reads.
- `slot_map.c`: slot info refresh, slot buffer mapping, and slot selection.
- `heartbeat.c`: node-down handling.
- `super.c`: remount, fill_super, option parsing, put_super, statfs, dismount, and super initialization.
- `xattr.c`: xattr block validation, allocation extension, xattr set context, bucket/index lookup, bucket movement/splitting/defrag, indexed xattr growth, xattr truncation, reflinked xattrs, and empty xattr block creation.
- `reservations.c`: reservation insertion, free-bit search, window finding, reservation cannibalization, and claimed-bit updates.
- `quota_local.c` and `quota_global.c`: local quota recovery, dquot sync, read/write/acquire/release, quota block validation, and dirty dquot marking.
- `dir.c`: directory block search/validation, indexed directory lookup, entry checks, dx root formatting, directory extension, rebalance, and insert preparation.
- `namei.c`: lookup/create/mkdir/unlink/symlink/move-orphan dentry events, mknod, hard link, unlink no-entry races, double locks, rename, rename denial/target races, symlink data, orphan-name formatting, orphan add/delete.
- `dcache.c`: dentry revalidation, negative dentry generation checks, orphan/delete/nofsdata cases, dentry lock attachment.
- `export.c`: NFS export dentry lookup, stale/generation checks, parent lookup, and file-handle encoding.
- `journal.c`: cache commits, transaction extension, journal access/dirty/init/shutdown, recovery completion, recovery thread/node handling, journal replay, orphan recovery queueing, orphan filldir, orphan recovery, and mount waits.
- `buffer_head_io.c`: synchronous and async block reads/writes.
- `uptodate.c`: metadata cache purge, buffer cache lookup, cache array/tree insertions, expansion, uptodate marking, and cache removal.

Namei-relevant details:
- The dentry event class records directory pointer, dentry pointer, name length/name, parent block number, and an extra value.
- Rename tracepoints capture old/new directories and names plus special target-exists/disagreement/overwrite cases.
- Orphan tracepoints record add begin/end, delete directory/name, and block-number stringification.
- Double-lock tracepoints record the two inode block numbers before and after lock ordering.

Design notes:
- The header is declarative but central to OCFS2 observability; adding/removing function instrumentation often requires updates here.
- Tracepoints avoid heavyweight formatting in hot paths by using ftrace `TP_fast_assign` and `TP_printk`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/ocfs2_trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/quota.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/quota.h

Role: Declares OCFS2 quota in-memory structures, caches, and quota operation APIs for local and global quota handling.

Key contents:
- `OCFS2_MAXQUOTAS` is `2`, covering user and group quota types.
- `struct ocfs2_dquot` embeds the generic VFS `struct dquot` and adds:
  - local quota-file offset and physical block
  - containing quota chunk
  - global use count
  - last globally synced space/inode usage
  - lockless-list node for deferred dquot reference dropping
- `struct ocfs2_recovery_chunk` records a quota chunk number and bitmap for recovery.
- `struct ocfs2_quota_recovery` holds recovery chunk lists per quota type.
- `struct ocfs2_mem_dqinfo` stores quota header/runtime state:
  - quota type, flags, chunk/block counts, sync interval
  - chunk list
  - global quota inode and lock resource
  - buffer heads and holder counts for global/local quota inode/info blocks
  - qtree info, delayed sync work, and optional recovery state
- `OCFS2_DQUOT()` maps a generic `struct dquot` to `struct ocfs2_dquot`.
- `struct ocfs2_quota_chunk` tracks a local quota-file chunk and its header buffer.
- Declares slab caches `ocfs2_dquot_cachep` and `ocfs2_qf_chunk_cachep`.
- Declares global qtree format operations `ocfs2_global_ops`.
- Declares recovery APIs: begin, finish, free quota recovery.
- Declares quota file read/write and global info read/write.
- Declares dquot sync/release wrappers around `__ocfs2_sync_dquot()`.
- Declares global quota-file locking, quota block validation and physical block reads.
- Declares local dquot create/release/write and deferred dquot reference dropping.
- Exports VFS quota operations and quota format type.

Design notes:
- OCFS2 separates global quota accounting from per-node local quota deltas, then synchronizes through cluster locks and delayed work.
- The recovery structures mirror the need to replay or repair per-slot local quota changes after node failure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/quota.h -->