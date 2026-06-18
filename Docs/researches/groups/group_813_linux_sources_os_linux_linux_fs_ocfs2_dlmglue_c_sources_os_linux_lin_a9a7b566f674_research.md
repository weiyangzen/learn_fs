# Group Research: group_813_linux_sources_os_linux_linux_fs_ocfs2_dlmglue_c_sources_os_linux_lin_a9a7b566f674

Scope: `Docs/research_subset_a.md`

Files researched:
- `sources/os/linux/linux/fs/ocfs2/dlmglue.c`
- `sources/os/linux/linux/fs/ocfs2/dlmglue.h`
- `sources/os/linux/linux/fs/ocfs2/export.c`
- `sources/os/linux/linux/fs/ocfs2/export.h`
- `sources/os/linux/linux/fs/ocfs2/extent_map.c`
- `sources/os/linux/linux/fs/ocfs2/extent_map.h`
- `sources/os/linux/linux/fs/ocfs2/file.c`
- `sources/os/linux/linux/fs/ocfs2/file.h`
- `sources/os/linux/linux/fs/ocfs2/filecheck.c`
- `sources/os/linux/linux/fs/ocfs2/filecheck.h`
- `sources/os/linux/linux/fs/ocfs2/heartbeat.c`
- `sources/os/linux/linux/fs/ocfs2/heartbeat.h`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlmglue.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlmglue.c

OCFS2 DLM integration layer. This file turns generic cluster-stack DLM callbacks into OCFS2-specific lock resources, lock wrappers, lock value block handling, downconversion, debugfs inspection, and mount/unmount DLM lifecycle.

Major responsibilities:
- Defines per-lock-type operations through `struct ocfs2_lock_res_ops`.
- Initializes lock resources for inode metadata, inode rw/data, open, dentry, flock, quota info, refcount tree, superblock, rename, NFS sync, trim, and orphan-scan locks.
- Builds OCFS2 lock names from lock type, block number, and generation. Dentry locks use a special parent/name layout with embedded inode block number.
- Implements DLM AST, BAST, and unlock AST callbacks through the `ocfs2_locking_protocol`.
- Provides public lock wrappers used throughout OCFS2: inode locks, rw locks, open locks, flock locks, dentry locks, super/rename/NFS/trim/orphan-scan locks, quota info locks, and refcount locks.
- Runs the downconvert kernel thread that responds to other nodes’ blocking ASTs.

Lock state model:
- `struct ocfs2_lock_res` is guarded by `l_lock` and tracked in debug lists.
- Important flags include initialized, attached, busy, blocked, queued, pending, refreshing, upconvert-finishing, local, nocache, and freeing.
- Holder counts distinguish PR and EX holders.
- Mask waiters sleep until selected flag bits reach a goal state; with stats enabled, waits and lock timings are recorded.
- `OCFS2_LOCK_PENDING` plus `l_pending_gen` closes the race between setting `BUSY` and entering `ocfs2_dlm_lock()`, especially when an AST can fire before the DLM call returns.

DLM callback behavior:
- `ocfs2_blocking_ast()` records the requested incompatible level, marks the lock blocked, schedules it on the blocked list, wakes waiters, and wakes the downconvert thread.
- `ocfs2_locking_ast()` handles attach, convert, and downconvert completions, updates granted level, refresh-needed state, pending state, busy state, and waiters.
- `ocfs2_unlock_ast()` handles convert cancellation and final lock drop.
- DLM errors clear busy/upconvert state and wake waiters.

Core cluster lock path:
- `__ocfs2_cluster_lock()` handles attach, upconvert, wait, noqueue, nonblocking AOP retry behavior, holder accounting, LVB flags, and lockdep acquisition.
- `__ocfs2_cluster_unlock()` decrements holders and may wake the downconvert thread if a blocking request can now proceed.
- `ocfs2_lock_create()` attaches a new DLM resource.
- `ocfs2_downconvert_lock()` converts a held lock to the compatible level requested by a remote node.

LVB handling:
- Metadata LVBs cache inode size, clusters, uid/gid, mode, link count, packed atime/mtime/ctime, inode attributes, dynamic features, and generation.
- `ocfs2_inode_lock_update()` refreshes inode state after acquiring a meaningful metadata lock. It trusts the LVB only when valid, version-matched, and generation-matched; otherwise it purges metadata/extent caches and rereads the dinode.
- Deleted inodes invalidate their LVB by setting version 0.
- Quota info LVBs cache quota grace/sync and global-info block accounting.
- Orphan scan and trim locks use small LVBs for sequence/status transfer.

Public lock wrappers:
- `ocfs2_create_new_inode_locks()` creates local/exclusive locks for newly created inodes before other nodes can see them.
- `ocfs2_rw_lock()` / `ocfs2_rw_unlock()` protect cross-node data/rw operations.
- `ocfs2_open_lock()` and `ocfs2_try_open_lock()` coordinate open/exclusive-open style checks.
- `ocfs2_inode_lock_full_nested()` acquires metadata locks, waits for recovery when needed, refreshes inode state, and optionally returns a dinode buffer.
- `ocfs2_inode_lock_with_folio()` is a page/folio-lock inversion escape hatch for address-space operations; on `-EAGAIN` it unlocks the folio and asks VFS to retry.
- `ocfs2_inode_lock_tracker()` prevents recursive cluster-lock upgrades inside one task by tracking stack-local holders.
- `ocfs2_file_lock()` and `ocfs2_file_unlock()` implement flock-specific DLM locking with no caching and signal-driven cancel-convert support.
- Super, rename, NFS sync, trim, dentry, qinfo, orphan scan, and refcount helpers wrap `ocfs2_cluster_lock()` with type-specific refresh/LVB behavior.

Downconversion:
- Blocked locks are queued under `osb->dc_task_lock` and processed by `ocfs2_downconvert_thread()`.
- `ocfs2_unblock_lock()` refuses to downconvert while pending, busy, still held incompatibly, refreshing, or not checkpointed.
- Metadata and refcount locks require their caching info to be fully checkpointed before EX downconversion.
- Data/meta inode downconversion unmaps mappings, writes dirty pages, truncates pages for EX blockers, waits for I/O for PR blockers, increments directory lock generation, and drops cached ACLs.
- Dentry downconversion invalidates local dentries with `d_delete()`, handles final dentry-lock reference drops through post-unlock callbacks, and marks the inode maybe-orphaned.
- Refcount downconversion purges the refcount tree metadata cache.

Lifecycle and cleanup:
- `ocfs2_dlm_init()` starts the downconvert thread, connects to the cluster stack, negotiates locking protocol, discovers the local node number, and initializes OSB lock resources.
- `ocfs2_dlm_shutdown()` drops OSB locks, stops the downconvert thread, frees OSB lock resources, disconnects the cluster, and releases debug state.
- `ocfs2_simple_drop_lockres()` marks a lock resource freeing, waits for blocked-list removal, sets LVB if needed, and calls DLM unlock.
- `ocfs2_drop_inode_locks()` drops open, metadata, and rw locks during inode teardown.

Debug support:
- Tracks live lock resources in `ocfs2_dlm_debug`.
- Exposes debugfs `locking_state` and `locking_filter`.
- Sequence output includes lock name/type state, flags, holders, requested/blocking levels, raw LVB bytes, and optional timing/failure/refresh stats.

Important invariants and risks:
- Many paths depend on exact flag transitions under `l_lock`; missed pending or busy handling can deadlock cluster lock conversion.
- LVB writes are only safe when EX is held and refresh state is clean.
- Downconvert workers may sleep and must recheck lock level/blocking state afterward.
- The dentry downconvert path deliberately does dcache/iput-sensitive work in the downconvert thread and has special freeing logic to avoid self-deadlock.
- Lock tracker forbids PR-to-EX recursive upgrades because two-node upgrade cycles can deadlock.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlmglue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlmglue.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlmglue.h

Public interface for OCFS2 DLM glue.

Defines LVB formats:
- `struct ocfs2_meta_lvb`, version 5: inode size, clusters, ownership, packed timestamps, mode, link count, attributes, dynamic features, and generation.
- `struct ocfs2_qinfo_lvb`, version 1: quota grace periods, sync interval, block count, free block, and free-entry accounting.
- `struct ocfs2_orphan_scan_lvb`, version 1: orphan-scan sequence number.
- `struct ocfs2_trim_fs_lvb`, version 1: trim success, node number, start, length, minimum length, and trimmed byte count.
- `struct ocfs2_trim_fs_info`: in-memory trim result wrapper.

Defines lock helper state:
- `struct ocfs2_lock_holder` tracks task-owned recursive inode lock context.
- Metadata lock flags: recovery/noqueue/nonblock/get-bh.
- Lockdep subclasses for normal, parent, rename, and reflink target inode locks.

Exports:
- DLM mount lifecycle: `ocfs2_dlm_init()`, `ocfs2_dlm_shutdown()`, `ocfs2_set_locking_protocol()`.
- Lock resource initialization/freeing for inode, dentry, file/flock, quota info, and refcount locks.
- Public lock/unlock helpers for rw, open, inode metadata, super, orphan scan, rename, NFS sync, trim, dentry, flock, quota info, and refcount locks.
- Inode lock convenience macros over `ocfs2_inode_lock_full_nested()`.
- Lock-resource teardown helpers and downconvert-thread wakeup.
- DLM debug reference helpers.
- Recursive-lock tracker pair.

Usage expectations:
- Callers must pair lock/unlock at the matching semantic level, not just matching DLM numeric level.
- `ocfs2_inode_lock()` usually means metadata lock; `ocfs2_rw_lock()` is separate data/rw coordination.
- Nonblocking and GETBH variants are specialized and used to avoid page-lock/DLM inversions or to refresh buffers under already-held locks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlmglue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/export.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/export.c

NFS export support for OCFS2. This file implements `struct export_operations` so NFS file handles can be encoded, decoded, and reconnected to dentries safely across a clustered filesystem.

File handle format:
- `struct ocfs2_inode_handle` stores inode block number and generation.
- `ocfs2_encode_fh()` emits a 3-word handle for the inode: high 32 bits of block number, low 32 bits, generation.
- If a parent is supplied, it emits a 6-word connectable handle with parent block number and generation and returns type 2.

Handle decoding:
- `ocfs2_fh_to_dentry()` validates length/type, decodes the target handle, and calls `ocfs2_get_dentry()`.
- `ocfs2_fh_to_parent()` validates type 2 handles, decodes parent fields, and calls `ocfs2_get_dentry()`.

`ocfs2_get_dentry()` behavior:
- Rejects block number zero as stale.
- First checks `ocfs2_ilookup()` for an in-memory inode and validates generation.
- If not cached, takes the NFS sync lock in EX mode to serialize against inode deletion on all nodes.
- Checks the inode allocator bit with `ocfs2_test_inode_bit()` before calling `ocfs2_iget()`.
- Converts invalid inode-bit lookups into `-ESTALE` where appropriate.
- Rejects generation mismatch with `-ESTALE`.
- Returns an alias dentry via `d_obtain_alias()`.

`ocfs2_get_parent()` behavior:
- Takes the NFS sync lock and a PR inode metadata lock on the child directory inode.
- Looks up `".."` with `ocfs2_lookup_ino_from_name()`.
- Verifies the parent inode allocator bit before obtaining an alias for `ocfs2_iget()`.

Export operations:
- `encode_fh`
- `fh_to_dentry`
- `fh_to_parent`
- `get_parent`

Important invariants:
- Generation checks are mandatory to avoid resurrecting stale NFS handles after inode reuse.
- The NFS sync lock serializes export lookup against clustered inode deletion.
- Parent lookup relies on directory metadata locking and allocator-bit validation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/export.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/export.h

Header for OCFS2 NFS export integration.

Exports:
- `extern const struct export_operations ocfs2_export_ops;`

Role:
- Lets the OCFS2 superblock setup install the export operation table implemented in `export.c`.

Dependencies:
- Includes Linux `exportfs.h` for `struct export_operations`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/export.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/extent_map.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/extent_map.c

OCFS2 in-memory extent cache and logical-to-physical mapping implementation. It provides a small inode-local extent map, on-disk extent tree lookup helpers, fiemap support, overwrite detection, SEEK_DATA/SEEK_HOLE handling, xattr extent mapping, and virtual block reads.

Extent cache:
- The cache is intentionally tiny: `OCFS2_MAX_EXTENT_MAP_ITEMS` is 3.
- `ocfs2_extent_map_init()` initializes per-inode list state.
- `ocfs2_extent_map_lookup()` searches the list under `ip_lock`, returns physical cluster/length/flags, and moves hits to the front.
- `ocfs2_extent_map_trunc()` forgets all cached mappings at or beyond a logical cluster and trims overlapping cached records.
- `ocfs2_extent_map_insert_rec()` inserts or merges a disk extent record into the cache. It merges adjacent records with identical flags and overwrites overlapping mappings caused by rare flag-split cases.
- When full, the oldest list entry is reused.

On-disk extent lookup:
- `ocfs2_get_clusters_nocache()` reads the dinode extent list or descends to the leaf extent block with `ocfs2_find_leaf()`.
- It validates leaf depth, `l_next_free_rec <= l_count`, nonzero physical block numbers, and can report whether a found record is the last extent.
- Holes are reported through `hole_len` using `ocfs2_figure_hole_clusters()`.
- `ocfs2_last_eb_is_empty()` handles the special case where the rightmost leaf exists but is empty.
- `ocfs2_xattr_get_clusters()` performs similar mapping for xattr extent lists.

Public mapping:
- `ocfs2_get_clusters()` first consults the small cache, then reads the dinode and walks extents. It returns `p_cluster == 0` for holes and inserts found records into the cache.
- Inline-data files return `-ERANGE` from `ocfs2_get_clusters()`.
- `ocfs2_extent_map_get_blocks()` maps logical file blocks to physical blocks and block counts, preserving holes as physical block zero.
- Callers are expected to hold `ip_alloc_sem` where allocation stability matters.

Fiemap:
- `ocfs2_fiemap()` takes the inode metadata lock and `ip_alloc_sem`.
- Inline-data files and fast symlinks are handled by `ocfs2_fiemap_inline()`, which reports the dinode-resident byte range as inline data.
- Extent-backed files are walked without cache, skipping holes and reporting unwritten and shared/refcounted flags.
- The code releases `ip_alloc_sem` around `fiemap_fill_next_extent()` to avoid page-fault deadlocks.

Overwrite and seek helpers:
- `ocfs2_overwrite_io()` returns success only when a write range is fully backed by allocated, non-refcounted extents; otherwise `-EAGAIN`.
- `ocfs2_seek_data_hole_offset()` implements SEEK_DATA and SEEK_HOLE over extents. Unwritten extents count as holes. Inline-data files have data until EOF and hole at EOF.

Virtual block reads:
- `ocfs2_read_virt_blocks()` maps logical file blocks through the extent map and then calls `ocfs2_read_blocks()`.
- It rejects holes as I/O errors for callers that expect metadata-like allocated virtual blocks.
- Uses trylock on `ip_alloc_sem` and returns `-EAGAIN` if unavailable.

Important invariants and risks:
- Cache invalidation is explicit; deletion paths must call truncate/invalidation before stale physical mappings can be reused.
- Hole length can exceed maximum single extent length, so holes are carried separately from `ocfs2_extent_rec`.
- Extent tree corruption is escalated through `ocfs2_error()` and `-EROFS`.
- The fiemap and read-virt paths carefully avoid lock/page-fault deadlocks by dropping semaphores or using trylocks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/extent_map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/extent_map.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/extent_map.h

Public interface for OCFS2 in-memory extent mapping.

Defines:
- `struct ocfs2_extent_map_item`: cached logical cluster start, physical cluster start, cluster count, flags, and list link.
- `OCFS2_MAX_EXTENT_MAP_ITEMS`: small fixed cache size of 3 entries.
- `struct ocfs2_extent_map`: count plus list head.

Exports:
- Cache lifecycle and mutation: `ocfs2_extent_map_init()`, `ocfs2_extent_map_trunc()`, `ocfs2_extent_map_insert_rec()`.
- File mapping: `ocfs2_get_clusters()`, `ocfs2_extent_map_get_blocks()`.
- Fiemap: `ocfs2_fiemap()`.
- Overwrite and seek helpers: `ocfs2_overwrite_io()`, `ocfs2_seek_data_hole_offset()`.
- Xattr extent mapping: `ocfs2_xattr_get_clusters()`.
- Virtual block read helpers: `ocfs2_read_virt_blocks()` and single-block wrapper `ocfs2_read_virt_block()`.
- Hole sizing helper: `ocfs2_figure_hole_clusters()`.

Contract:
- `ocfs2_read_virt_block()` validates non-NULL output buffer pointer and delegates to the multi-block form.
- Allocation-stable callers should hold the inode allocation semaphore as documented by the implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/extent_map.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/file.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/file.c

OCFS2 file operation implementation. This file owns file open/release state, fsync, atime updates, truncate/extend, setattr/getattr/permission, preallocation and hole punching, buffered/direct read/write locking, llseek, reflink remap, and the exported VFS operation tables.

Open and per-file state:
- `ocfs2_init_file_private()` allocates `struct ocfs2_file_private`, initializes its mutex and per-file flock DLM lock resource, and stores it in `file->private_data`.
- Regular file open initializes quotas for writers, rejects inodes marked deleted, records direct-open state, increments `ip_open_count`, and sets `FMODE_NOWAIT`.
- Release decrements open count, clears direct-open state when the last open closes, and drops the per-file flock lock resource.
- Directories use the same private state for directory cookies and flock support.

Fsync and atime:
- `ocfs2_sync_file()` writes dirty pages, completes the relevant JBD2 transaction, and issues a block-device flush when journal barriers require one.
- `ocfs2_should_update_atime()` implements noatime/nodiratime/relatime and OCFS2 atime quantum policy.
- `ocfs2_update_inode_atime()` updates only atime in a small journal transaction without using the broader dirty-inode helper.

Size updates, truncate, and extend:
- `ocfs2_set_inode_size()` updates VFS inode size, block count, ctime/mtime, and dinode state through `ocfs2_mark_inode_dirty()`.
- `ocfs2_simple_size_update()` wraps that in a transaction.
- `ocfs2_truncate_file()` handles shrink. It holds `ip_alloc_sem`, discards local allocation reservations, handles inline-data truncation, zeroes partial clusters, updates size before allocation removal, truncates page cache, commits extent-tree truncation, schedules truncate-log flush, and tries to remove an empty refcount tree.
- `ocfs2_orphan_for_truncate()` prepares a shrink so recovery can finish later; it CoWs a partial refcounted cluster when needed and zeroes the post-size cluster tail.
- `ocfs2_extend_file()` handles grow. Inline data may remain inline if the new size fits; otherwise inline data is converted to extents. Sparse files zero allocated ranges only; nonsparse files allocate clusters with `ocfs2_extend_no_holes()`.
- `ocfs2_extend_allocation()` locks allocators, reserves quota, starts/restarts journal transactions, adds extent-tree clusters, handles metadata/transaction restarts, and releases unused quota.

Zeroing:
- `ocfs2_zero_extend()` finds allocated, written ranges between old size and new size, CoWs refcounted extents, and zeroes them page by page.
- `ocfs2_write_zero_page()` uses block write helpers without logically exposing stale data and updates i_size temporarily so writeback does not drop dirty EOF pages.
- `ocfs2_zero_partial_clusters()` zeroes unaligned edges for hole punching/truncate, using disk zeroout beyond EOF where page-cache writes are unsuitable.
- Ordered-data files register zeroed ranges with JBD2 when needed.

Setattr/getattr/permission:
- `ocfs2_setattr()` validates attributes, initializes quota when ownership changes, serializes size changes with DIO wait and rw EX lock, uses inode lock tracker, handles truncate/extend, performs quota transfer, updates inode attributes in a transaction, and runs ACL chmod after mode changes.
- Recursive cluster-lock detection is logged because ACL paths can re-enter inode operations.
- `ocfs2_getattr()` revalidates inode state, fills stat data, reports at least one sector for inline-data files, and uses cluster size as preferred block size.
- `ocfs2_permission()` takes a PR metadata lock unless `MAY_NOT_BLOCK` is set.

Preallocation and hole punching:
- `ocfs2_allocate_unwritten_extents()` converts inline data when needed and allocates unwritten extents over holes.
- `ocfs2_remove_inode_range()` handles inline-data punching, CoWs partial refcounted edge clusters, zeroes partial clusters, walks extent leaves from right to left, removes btree ranges, truncates page cache, schedules truncate-log flush, and runs cached deallocations.
- `__ocfs2_change_file_space()` backs OCFS2 reservation ioctls and fallocate. It validates ranges, strips suid/sgid if needed, locks rw/meta/allocation state, allocates unwritten extents or removes ranges, optionally extends i_size, updates timestamps, and honors O_SYNC.
- `ocfs2_fallocate()` supports keep-size and punch-hole modes when unwritten extents are available.

Read/write:
- `ocfs2_prepare_inode_for_write()` obtains metadata locks and `ip_alloc_sem`, checks NOWAIT overwrite feasibility, strips suid/sgid under an EX metadata lock, and CoWs refcounted write ranges.
- `ocfs2_file_write_iter()` rejects buffered NOWAIT, serializes through `inode_lock`, takes the rw lock at EX or PR depending on direct/buffered/full-coherency/append mode, forces metadata EX lock for full-coherency direct I/O, runs generic write checks, prepares extents, converts unaligned async direct I/O to sync completion, and coordinates rw lock release with direct-I/O completion via `iocb->private`.
- `ocfs2_file_read_iter()` takes rw PR for direct I/O, refreshes inode/atime metadata, delegates to generic read, and defers rw unlock to DIO completion when queued.
- `ocfs2_file_splice_read()` refreshes metadata/atime before `filemap_splice_read()`.

Seeking and remap:
- `ocfs2_file_llseek()` handles SEEK_END under inode metadata lock and SEEK_DATA/SEEK_HOLE via extent-map logic.
- Directory llseek uses `generic_llseek_cookie()` with the per-file directory cookie.
- `ocfs2_remap_file_range()` implements reflink/dedupe remap. It requires refcount support, locks both inodes, validates eligibility, locks allocation maps, zaps destination page cache, remaps blocks, clears extent caches, and updates destination size/metadata.

Operation tables:
- `ocfs2_file_iops` and `ocfs2_special_file_iops` install setattr/getattr/permission/xattr/ACL/fileattr hooks.
- `ocfs2_fops` and `ocfs2_dops` include POSIX lock callbacks.
- `ocfs2_fops_no_plocks` and `ocfs2_dops_no_plocks` omit POSIX lock callbacks but keep flock support.

Important invariants and risks:
- Size-changing operations require careful ordering across inode rwsem, rw cluster lock, metadata lock, DIO wait, and `ip_alloc_sem`.
- Partial cluster zeroing is required to avoid stale data exposure on truncate, extend, and hole punch.
- Refcounted extents must be CoWed before partial overwrite or zeroing.
- NOWAIT is only supported where lock acquisition and overwrite checks can avoid blocking.
- DIO completion owns rw-lock release in queued async cases.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/file.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/file.h

Public header for OCFS2 file and inode operation helpers.

Exports operation tables:
- `ocfs2_fops`, `ocfs2_dops`
- `ocfs2_fops_no_plocks`, `ocfs2_dops_no_plocks`
- `ocfs2_file_iops`, `ocfs2_special_file_iops`

Defines:
- `struct ocfs2_file_private`: directory cookie, backing `struct file`, mutex, and per-file flock lock resource.

Declares helpers for:
- Extent allocation into an inode: `ocfs2_add_inode_data()`.
- Size updates: `ocfs2_set_inode_size()`, `ocfs2_simple_size_update()`.
- Truncate/extend: `ocfs2_truncate_file()`, `ocfs2_extend_no_holes()`, `ocfs2_zero_extend()`.
- VFS inode ops: `ocfs2_setattr()`, `ocfs2_getattr()`, `ocfs2_permission()`.
- Atime policy/update: `ocfs2_should_update_atime()`, `ocfs2_update_inode_atime()`.
- Reservation/hole-punch ioctls: `ocfs2_change_file_space()`.
- Refcount and range removal helpers: `ocfs2_check_range_for_refcount()`, `ocfs2_remove_inode_range()`.

Role:
- Shared by address-space, ioctl, inode, and other OCFS2 modules that need file-size/allocation behavior without owning VFS operation tables directly.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/filecheck.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/filecheck.c

Online OCFS2 file-check sysfs implementation. It exposes per-mount sysfs controls that let privileged users request a check or fix of a specific inode and inspect recent results.

Sysfs layout:
- Creates a `filecheck` kobject under the OCFS2 device kset.
- Attributes:
  - `check`: write inode number to run check mode; read result list for check entries.
  - `fix`: write inode number to run fix mode; read result list for fix entries.
  - `set`: write max retained entry count; read current max.

Data model:
- `struct ocfs2_filecheck` owns a spinlock, entry list, maximum entries, current size, and done count.
- `struct ocfs2_filecheck_entry` records inode number, operation type, done bit, and filecheck status.
- Entry retention defaults to `OCFS2_FILECHECK_MINSIZE` and is bounded by `OCFS2_FILECHECK_MAXSIZE`.

Lifecycle:
- `ocfs2_filecheck_create_sysfs()` allocates state, initializes list/lock/counters, initializes the kobject, and adds sysfs files.
- `ocfs2_filecheck_remove_sysfs()` removes the kobject, waits for release completion, then frees only completed entries and the state object.
- `ocfs2_filecheck_release()` completes unregister synchronization.

Input parsing:
- Attribute type is inferred from name: `check`, `fix`, or `set`.
- Writes parse a positive integer from a bounded buffer.
- `set` adjusts maximum queue length only if pending entries still fit.

Queue behavior:
- Duplicate pending inode entries are rejected with `-EEXIST`.
- If the queue is full and no completed entry can be discarded, writes return `-EAGAIN`.
- If full with completed entries present, the oldest completed entry is erased to make room.
- New check/fix entries are inserted as `INPROGRESS`, then handled synchronously.

Check/fix execution:
- `ocfs2_filecheck_handle()` calls `ocfs2_iget()` with either `OCFS2_FI_FLAG_FILECHECK_CHK` or `OCFS2_FI_FLAG_FILECHECK_FIX`.
- Recognized OCFS2 filecheck-specific error codes are preserved; unexpected iget failures collapse to generic `FAILED`.
- Successful iget immediately drops the inode with `iput()`.
- Unsupported operation types report `UNSUPPORTED`.

Output:
- `check` and `fix` reads print a header plus matching entries with inode, done flag, and symbolic error string.
- `set` reads print the current max retained entries.

Important invariants and risks:
- The list is spinlock-protected; sysfs show/store takes a kobject reference around callbacks.
- Teardown asserts all entries are done before freeing.
- The actual validation/fix work is delegated to inode read paths through filecheck flags, so this file is mostly control-plane and result retention.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/filecheck.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/filecheck.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/filecheck.h

Header for OCFS2 online file check.

Defines:
- Filecheck status codes:
  - success
  - failed
  - in progress
  - read-only
  - in journal
  - invalid inode
  - block ECC
  - block number
  - valid-flag
  - generation
  - unsupported
- Error range macros: `OCFS2_FILECHECK_ERR_START` and `OCFS2_FILECHECK_ERR_END`.
- `struct ocfs2_filecheck`: list head, spinlock, max entry count, current entry count, finished entry count.
- Queue bounds: min 10, max 100.
- Operation types: check, fix, and set-max.
- `struct ocfs2_filecheck_sysfs_entry`: sysfs kobject, unregister completion, and pointer to filecheck state.

Exports:
- `ocfs2_filecheck_create_sysfs()`
- `ocfs2_filecheck_remove_sysfs()`

Role:
- Provides the mount-level sysfs state structure embedded in `struct ocfs2_super` and the create/remove hooks called by mount lifecycle code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/filecheck.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/heartbeat.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/heartbeat.c

OCFS2 heartbeat callback and node-map helper implementation. This is a small bridge between cluster heartbeat/node-down notification and OCFS2 recovery bookkeeping.

Node maps:
- `ocfs2_node_map_init()` initializes maps with `OCFS2_NODE_MAP_MAX_NODES` and clears all bits.
- `ocfs2_init_node_maps()` initializes the superblock node-map spinlock and the recovering orphan-directory map.
- `ocfs2_node_map_set_bit()`, `ocfs2_node_map_clear_bit()`, and `ocfs2_node_map_test_bit()` update/test maps under `osb->node_map_lock`.
- Bit `-1` is silently ignored for set/clear as a special legacy case.
- Out-of-range positive bits trigger `BUG_ON()` or explicit error logging and BUG.

Node-down handling:
- `ocfs2_do_node_down()` is the cluster-stack node-down callback registered during DLM connect.
- It asserts the local node is not reported down.
- If the cluster connection is not yet established, it ignores the event because slot scanning after connect will notice recovery needs.
- Otherwise it calls `ocfs2_recovery_thread(osb, node_num)` to start recovery for the dead node.

Dependencies:
- Recovery and journal code receive node-down events.
- Node maps are used to track mounted/recovering node state such as orphan directory recovery.

Important invariants:
- Node map operations require the superblock’s node-map lock.
- Heartbeat callback can arrive before full cluster setup; the file explicitly treats that as safe to ignore.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/heartbeat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/heartbeat.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/heartbeat.h

Header for OCFS2 heartbeat-facing helpers.

Exports:
- `ocfs2_init_node_maps()`
- `ocfs2_do_node_down()`
- `ocfs2_node_map_set_bit()`
- `ocfs2_node_map_clear_bit()`
- `ocfs2_node_map_test_bit()`

Role:
- Lets DLM/cluster setup register node-down handling and lets recovery/orphan code maintain node bitmaps through shared helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/heartbeat.h -->