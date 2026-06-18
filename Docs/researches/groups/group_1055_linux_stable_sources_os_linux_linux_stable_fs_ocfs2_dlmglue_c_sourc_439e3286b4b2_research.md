# Group Research: group_1055_linux_stable_sources_os_linux_linux_stable_fs_ocfs2_dlmglue_c_sourc_439e3286b4b2

Scope: `Docs/research_subset_a.md`  
Files read completely: yes

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlmglue.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlmglue.c

Purpose: Implements OCFS2's filesystem-specific interface to the cluster DLM, including lock-resource initialization, lock acquisition/release, lock value block handling, blocked-lock downconversion, and debugfs lock-state reporting.

Read coverage: complete file read, 4468 lines.

Key structures and state:
- `struct ocfs2_lock_res_ops` defines per-lock-type behavior: owner lookup, post-unlock cleanup, downconvert safety checks, LVB population, pre-downconvert worker, and lock-type flags.
- Lock operation tables cover inode RW locks, inode metadata locks, superblock, rename, NFS sync, trim, orphan scan, dentry, open, flock, quota info, and refcount-block locks.
- `struct ocfs2_mask_waiter` waits for specific `l_flags` transitions and optionally records lock timing stats.
- Lock resources track current/requested/blocking DLM levels, holders, pending DLM operations, blocked-list membership, waiters, and debug tracking.
- LVB formats handled here include inode metadata, quota info, orphan scan sequence, and trimfs result data.

Major logic:
- Builds stable OCFS2 lock names and initializes lock resources for inodes, dentries, file-private flock locks, quota info, refcount trees, and global mount locks.
- Implements DLM AST, BAST, and unlock-AST callbacks, translating DLM events into OCFS2 lock-resource state transitions.
- Provides `ocfs2_cluster_lock()` and `ocfs2_cluster_unlock()` as the generic lock acquire/release path with support for convert, attach, noqueue, nonblocking retry, waiters, LVB use, and lockdep.
- Uses `OCFS2_LOCK_PENDING` plus `l_pending_gen` to close the race between marking a lock busy and actually calling into the DLM.
- Refreshes stale inode state from metadata LVBs when trusted, otherwise purges metadata/extent caches and rereads the dinode from disk.
- Handles metadata LVB packing/unpacking for size, clusters, ownership, mode, link count, times, flags, dynamic features, and generation.
- Implements public wrappers for inode metadata locks, inode RW locks, open locks, flock locks, super locks, rename locks, NFS sync locks, trim locks, dentry locks, quota-info locks, orphan-scan locks, and refcount-tree locks.
- Maintains a downconvert kernel thread that processes blocked locks, calls type-specific workers, writes LVBs when safe, cancels conflicting converts, and requeues work when holders or checkpointing prevent downconversion.
- Supplies debugfs `locking_state` and `locking_filter` support with seq_file iteration over tracked lock resources and raw LVB/stat dumps.

Important entry points:
- Initialization and shutdown: `ocfs2_set_locking_protocol()`, `ocfs2_dlm_init()`, `ocfs2_dlm_shutdown()`.
- Lock-resource lifecycle: `ocfs2_lock_res_init_once()`, `ocfs2_inode_lock_res_init()`, `ocfs2_dentry_lock_res_init()`, `ocfs2_file_lock_res_init()`, `ocfs2_qinfo_lock_res_init()`, `ocfs2_refcount_lock_res_init()`, `ocfs2_lock_res_free()`.
- Inode locks: `ocfs2_inode_lock_full_nested()`, `ocfs2_inode_lock_with_folio()`, `ocfs2_inode_lock_atime()`, `ocfs2_inode_unlock()`, tracker variants.
- Other lock wrappers: `ocfs2_rw_lock()`, `ocfs2_try_rw_lock()`, `ocfs2_open_lock()`, `ocfs2_file_lock()`, `ocfs2_super_lock()`, `ocfs2_rename_lock()`, `ocfs2_nfs_sync_lock()`, `ocfs2_trim_fs_lock()`, `ocfs2_dentry_lock()`, `ocfs2_qinfo_lock()`, `ocfs2_refcount_lock()`.
- Cleanup and downconversion: `ocfs2_mark_lockres_freeing()`, `ocfs2_simple_drop_lockres()`, `ocfs2_drop_inode_locks()`, `ocfs2_wake_downconvert_thread()`.

Concurrency and lifetime:
- `l_lock` protects lock-resource state, holder counts, waiter lists, and pending action fields.
- `dc_task_lock` protects the mount's blocked-lock list and downconvert wake sequence.
- The downconvert path may run type-specific filesystem work without `l_lock`, then revalidates blocking state before issuing DLM converts.
- Metadata downconversion is gated by checkpoint completion so dirty metadata is not exposed incorrectly to other nodes.
- Dentry downconversion takes extra dentry-lock references to avoid final-reference teardown while invalidating aliases.
- Flock locks deliberately avoid caching and use signal-aware convert cancellation because userspace can self-deadlock.
- Debug tracking uses a global spinlock and copies lock resources before printing because the owning object may disappear after unlock.

Important dependencies:
- DLM stack glue, heartbeat node-down callbacks, journal checkpointing, metadata cache purge/checkpoint APIs, inode refresh, extent-map truncation, quota read/write helpers, dcache/dentry lock helpers, refcount-tree caching, ACL cache invalidation, and debugfs/seq_file infrastructure.
- Uses DLM LVBs and DLM convert/cancel/drop semantics through `ocfs2_dlm_lock()` and `ocfs2_dlm_unlock()`.

Risk and edge cases:
- Lock state transitions are race-sensitive; `OCFS2_LOCK_PENDING`, `OCFS2_LOCK_BUSY`, `OCFS2_LOCK_UPCONVERT_FINISHING`, and queued/freeing flags must remain synchronized.
- LVB metadata is trusted only when valid, versioned, and generation-matched; stale LVB use would corrupt in-memory inode state.
- Downconvert workers can sleep and can trigger dcache/inode teardown, so queue ownership and post-unlock callbacks are delicate.
- Local mounts and hard-readonly mounts bypass parts of cluster locking; wrapper semantics must preserve expected error behavior such as `-EROFS`.
- `ocfs2_inode_lock_with_folio()` intentionally returns `AOP_TRUNCATED_PAGE` on nonblocking lock conflict to break folio-lock/DLM-lock inversion.
- Lock resource freeing asserts no waiters, holders, busy state, or blocked-list membership; cleanup ordering violations become hard failures.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlmglue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlmglue.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlmglue.h

Purpose: Declares OCFS2 DLM glue data formats, lock flags, locking subclasses, and public lock-management APIs.

Read coverage: complete file read, 207 lines.

Key contents:
- LVB ABI structures for inode metadata, quota info, orphan scan sequence, and trimfs state.
- `struct ocfs2_trim_fs_info` as the CPU-endian trimfs handoff format.
- `struct ocfs2_lock_holder` used by recursive-lock tracking.
- Metadata lock argument flags: recovery wait suppression, noqueue, nonblocking, and get-buffer-only behavior.
- Inode cluster-lock subclasses for normal, parent, rename ordering, and reflink target contexts.
- Public prototypes for DLM lifecycle, lock-resource initialization/freeing, inode/RW/open/dentry/file/quota/refcount/global locks, and downconvert wakeup.
- Convenience macros for common inode-lock variants.

Important invariants:
- LVB versions are explicit ABI checks between mounted nodes.
- Tracker variants distinguish first lock acquisition from recursive compatible lock use and forbid PR-to-EX recursive upgrades.
- `OCFS2_META_LOCK_GETBH` means the caller already has cluster-lock coverage and only wants an up-to-date dinode buffer.

Dependencies:
- Includes `dcache.h` for dentry-lock types and depends on OCFS2 superblock, inode, quota, refcount, folio, and buffer-head declarations from surrounding headers.

Risk notes:
- Any LVB layout or version change affects cluster interoperability.
- Lock flag semantics are tightly coupled to `dlmglue.c`; adding a flag requires auditing wait and downconvert paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlmglue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/export.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/export.c

Purpose: Implements OCFS2 NFS/exportfs support by encoding file handles, resolving handles back to dentries, and locating directory parents.

Read coverage: complete file read, 285 lines.

Key structures and state:
- `struct ocfs2_inode_handle` stores an inode block number and generation.
- File handles encode child block number high/low words plus generation, optionally followed by parent block number high/low words plus generation.

Major logic:
- `ocfs2_get_dentry()` resolves a handle by first checking the inode cache, then taking the NFS sync lock, verifying the inode allocator bit, igetting the inode, and checking generation.
- `ocfs2_get_parent()` takes the NFS sync lock and directory metadata lock, resolves `".."`, validates the parent inode allocator bit, and returns an alias dentry.
- `ocfs2_encode_fh()` emits three 32-bit words for a non-connectable handle and six words when a parent inode is supplied.
- `ocfs2_fh_to_dentry()` and `ocfs2_fh_to_parent()` decode little-endian handle words into `ocfs2_inode_handle` values.
- Exports `ocfs2_export_ops` for VFS exportfs integration.

Concurrency and lifetime:
- The NFS sync lock serializes handle resolution against inode deletion across cluster nodes.
- Directory parent lookup also holds the directory inode lock while reading `".."`.
- Resolved inodes are returned through `d_obtain_alias()`; stale or generation-mismatched handles return `-ESTALE`.

Important dependencies:
- Uses inode lookup/iget, inode allocator bit tests, directory name lookup, dentry aliasing, DLM NFS sync lock wrappers, and exportfs operations.

Risk notes:
- Handle validity depends on both allocator-bit state and generation matching.
- Parent lookup maps several lower-level invalid-inode cases to `-ESTALE` or `-ENOENT` to fit NFS expectations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/export.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/export.h

Purpose: Declares OCFS2's exportfs operation table.

Read coverage: complete file read, 17 lines.

Key contents:
- Includes Linux exportfs declarations.
- Exposes `extern const struct export_operations ocfs2_export_ops`.

Dependencies:
- Implemented by `export.c` and consumed by superblock setup.

Risk notes:
- No internal logic; correctness depends on `export.c` keeping the exported operation table valid.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/export.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/extent_map.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/extent_map.c

Purpose: Provides OCFS2 logical-to-physical cluster/block mapping, a tiny inode-local extent cache, FIEMAP support, SEEK_DATA/SEEK_HOLE support, overwrite checks, xattr extent lookup, and virtual-block reads.

Read coverage: complete file read, 1047 lines.

Key structures and state:
- Uses `struct ocfs2_extent_map` embedded in `ocfs2_inode_info`, capped at `OCFS2_MAX_EXTENT_MAP_ITEMS` entries.
- `struct ocfs2_extent_map_item` records logical cluster start, physical cluster start, cluster count, flags, and LRU list linkage.
- On-disk mappings are read from dinode extent lists or external extent blocks.

Major logic:
- Initializes, looks up, truncates, inserts, merges, and evicts cached extent-map records under `ip_lock`.
- `ocfs2_get_clusters_nocache()` walks the dinode/extent-block tree, returns the matching extent record or computes hole length, and can identify the last extent.
- `ocfs2_get_clusters()` first consults the small cache, then rereads the dinode and caches successful extent records.
- `ocfs2_extent_map_get_blocks()` converts virtual block numbers to physical block numbers and contiguous block counts.
- `ocfs2_xattr_get_clusters()` maps clusters in an xattr extent list and treats holes in xattr storage as corruption.
- `ocfs2_fiemap()` reports inline data/fast symlinks or extent records, including unwritten and shared/refcounted flags.
- `ocfs2_overwrite_io()` verifies a nowait write range is fully allocated and not refcounted.
- `ocfs2_seek_data_hole_offset()` implements SEEK_DATA/SEEK_HOLE semantics, treating unwritten extents as holes.
- `ocfs2_read_virt_blocks()` maps virtual blocks and reads their physical blocks, supporting readahead validation paths.

Important entry points:
- Cache management: `ocfs2_extent_map_init()`, `ocfs2_extent_map_trunc()`, `ocfs2_extent_map_insert_rec()`.
- Mapping: `ocfs2_get_clusters()`, `ocfs2_xattr_get_clusters()`, `ocfs2_extent_map_get_blocks()`, `ocfs2_figure_hole_clusters()`.
- Reporting and policy checks: `ocfs2_fiemap()`, `ocfs2_overwrite_io()`, `ocfs2_seek_data_hole_offset()`.
- I/O helper: `ocfs2_read_virt_blocks()`.

Concurrency and lifetime:
- Cache list state is protected by `ip_lock`.
- Mapping callers are expected to hold `ip_alloc_sem` when allocations must not change during lookup.
- FIEMAP drops and reacquires `ip_alloc_sem` around `fiemap_fill_next_extent()` to avoid page-fault deadlocks.
- Virtual block reads use `down_read_trylock()` on `ip_alloc_sem`; failure returns `-EAGAIN`.

Important dependencies:
- Relies on extent tree traversal helpers from allocation code, inode block reading, metadata cache validation, OCFS2 block/cluster conversion helpers, FIEMAP, buffer-head I/O, and inline-data/fast-symlink helpers.

Risk and edge cases:
- The extent cache is deliberately small and simple; callers must truncate it whenever records are deleted or mappings can overlap stale entries.
- Corrupt extent-list metadata, non-leaf blocks where leaves are expected, invalid `l_next_free_rec`, or zero physical block records produce filesystem errors.
- Hole length can span to `UINT_MAX - v_cluster`, so callers must cap returned ranges to their own request.
- Inline-data files are not valid for normal cluster lookup and return `-ERANGE`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/extent_map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/extent_map.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/extent_map.h

Purpose: Declares the OCFS2 in-memory extent-map structures and block/cluster mapping APIs.

Read coverage: complete file read, 80 lines.

Key contents:
- `struct ocfs2_extent_map_item` stores one cached logical-to-physical extent and flags.
- `struct ocfs2_extent_map` holds a capped LRU-style list of cached mappings.
- `OCFS2_MAX_EXTENT_MAP_ITEMS` limits each inode cache to three entries.
- Declares cluster lookup, xattr lookup, block mapping, FIEMAP, overwrite detection, SEEK_DATA/SEEK_HOLE, virtual block reads, and hole-size helpers.
- Provides inline `ocfs2_read_virt_block()` wrapper for a single virtual block.

Important invariants:
- The cache is a hint, not authoritative; tree mutation paths must invalidate stale ranges.
- `ocfs2_read_virt_block()` rejects a NULL buffer-head pointer before delegating to the multi-block path.

Dependencies:
- Requires OCFS2 extent-record/list types, Linux list heads, inodes, files, buffer heads, and FIEMAP structures.

Risk notes:
- Public mapping APIs encode caller locking assumptions, especially around `ip_alloc_sem`, but the header cannot enforce them.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/extent_map.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/file.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/file.c

Purpose: Implements OCFS2 VFS file and directory operations, file-private lock state, fsync, atime updates, setattr/getattr/permission, file size changes, allocation extension, hole punching, fallocate, read/write iteration, seeking, and reflink remapping.

Read coverage: complete file read, 2893 lines.

Key structures and state:
- Uses `struct ocfs2_file_private` per open file for directory cookies, flock lock resource state, and file pointer backreferences.
- Coordinates VFS inode state with dinode buffer contents, OCFS2 inode private state, quota state, extent trees, refcount trees, page cache, and journal transactions.
- File operation tables provide normal and no-cluster-posix-lock variants for files and directories.

Major logic:
- Open/release paths allocate/free file-private state, initialize flock lock resources, maintain open counts, handle direct-open flags, and initialize quotas for writers.
- `ocfs2_sync_file()` waits on file data, completes the relevant JBD2 transaction, and issues a block-device flush if barriers require it.
- Atime helpers decide when clustered atime updates are needed and journal atime changes without relying on broad inode locks.
- Size update helpers journal dinode size, blocks, ctime, and mtime changes.
- Truncate paths CoW partial refcounted clusters, zero partial clusters, update i_size before allocation removal, drop page cache, remove extents, schedule truncate-log flushing, and attempt refcount-tree removal when empty.
- Extend paths allocate clusters for non-sparse files, zero newly exposed allocated ranges, convert inline data to extents when needed, and update size.
- `ocfs2_setattr()` handles size changes, ownership/mode/time changes, quota transfers, ACL chmod follow-up, recursive cluster-lock tracking, and rw-lock coverage for truncation/extension.
- Fallocate and reservation ioctls allocate unwritten extents or remove byte ranges through common change-file-space logic.
- Hole punching handles inline data, refcount CoW at range edges, partial-cluster zeroing, extent-tree walking from right to left, and page-cache truncation of fully removed clusters.
- Write preparation removes suid/sgid when necessary, checks NOWAIT overwrite eligibility, CoWs refcounted ranges, and upgrades from PR to EX metadata locks only when needed.
- Read/write iterators wrap generic I/O with OCFS2 rw locks, metadata locks, atime refresh, direct-I/O coherency rules, NOWAIT restrictions, and async direct-I/O lock handoff.
- `ocfs2_file_llseek()` supports SEEK_SET/CUR/END/DATA/HOLE with inode locking where size or extent state is needed.
- `ocfs2_remap_file_range()` implements reflink/dedupe remapping with dual-inode locking, allocation semaphores, destination page-cache invalidation, extent-map invalidation, and destination size update.

Important entry points:
- File operations: `ocfs2_file_open()`, `ocfs2_file_release()`, `ocfs2_sync_file()`, `ocfs2_file_read_iter()`, `ocfs2_file_write_iter()`, `ocfs2_file_splice_read()`, `ocfs2_file_llseek()`, `ocfs2_fallocate()`, `ocfs2_remap_file_range()`.
- Inode operations: `ocfs2_setattr()`, `ocfs2_getattr()`, `ocfs2_permission()`.
- Size/allocation helpers: `ocfs2_set_inode_size()`, `ocfs2_simple_size_update()`, `ocfs2_truncate_file()`, `ocfs2_add_inode_data()`, `ocfs2_extend_no_holes()`, `ocfs2_zero_extend()`, `ocfs2_remove_inode_range()`, `ocfs2_change_file_space()`.
- Exported operation tables: `ocfs2_file_iops`, `ocfs2_special_file_iops`, `ocfs2_fops`, `ocfs2_dops`, `ocfs2_fops_no_plocks`, `ocfs2_dops_no_plocks`.

Concurrency and lifetime:
- Uses VFS `inode_lock`, OCFS2 RW DLM locks, metadata DLM locks, and `ip_alloc_sem` in carefully ordered combinations.
- Truncate/setattr waits for direct I/O before taking cluster locks to avoid deadlocks with DIO completion.
- Direct I/O can hand RW-lock release to async completion; buffered async write queuing is BUG-checked because lock coverage would be wrong.
- NOWAIT support is limited to direct I/O and requires trylocks plus overwrite-only mapping checks.
- FIle-private flock resources are dropped and freed on release or directory close.
- Recursive inode-lock tracker paths prevent PR-to-EX upgrades within the same task.

Important dependencies:
- Extent allocation/mutation, truncate log, refcount tree CoW/reflink, inline-data conversion, quota operations, ACL chmod, journaling, ordered data tracking, inode refresh/locking, mmap preparation, ioctl handling, VFS generic I/O helpers, FIEMAP/seek helpers, and block zeroout/flush APIs.

Risk and edge cases:
- Partial-cluster zeroing is subtle because OCFS2 clusters can exceed page size and reflinked cluster edges must be CoWed before zeroing.
- Hole punching walks extent records from right to left and must keep path state, truncate bounds, and delayed deallocation synchronized.
- Write paths must remove suid/sgid before generic write to avoid recursive cluster locking through setattr.
- Size extension with sparse allocation still needs zeroing of already allocated ranges between old and new size.
- Direct-I/O coherency depends on mount options and whether the write is append or unaligned async.
- Operation tables must stay paired between normal and no-plock variants except for POSIX lock hooks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/file.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/file.h

Purpose: Declares OCFS2 file/directory operation tables, per-file private state, and file-size/allocation helper APIs.

Read coverage: complete file read, 74 lines.

Key contents:
- Extern declarations for file and inode operation tables, including no-posix-cluster-lock variants.
- `struct ocfs2_file_private` stores a directory seek cookie, owning `struct file`, mutex, and flock lock resource.
- Prototypes for allocation extension, inode size update, truncation, no-hole extension, zero extension, setattr/getattr/permission, atime handling, file-space reservation/punching, refcount-range checking, and inode-range removal.

Important invariants:
- File-private state owns an OCFS2 lock resource that must be initialized on open and dropped/freed on release.
- Allocation helpers assume higher-level callers have acquired appropriate inode, cluster, journal, and allocation locks.

Dependencies:
- Tied to `file.c`, `dlmglue.c`, allocation contexts, buffer heads, quota/refcount logic, and VFS operation tables.

Risk notes:
- Public helper prototypes expose low-level mutation routines whose correctness depends on caller-side lock and transaction discipline.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/filecheck.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/filecheck.c

Purpose: Implements OCFS2 online file check sysfs support, allowing administrators to queue inode check/fix requests and inspect recent results.

Read coverage: complete file read, 509 lines.

Key structures and state:
- `ocfs2_filecheck_errs[]` maps filecheck-specific status codes to strings.
- `struct ocfs2_filecheck_entry` records inode number, operation type, completion bit, and status.
- `struct ocfs2_filecheck_args` stores parsed sysfs input for check/fix inode numbers or queue-size updates.
- Each mount has `struct ocfs2_filecheck_sysfs_entry` with a kobject and `struct ocfs2_filecheck` queue state.

Major logic:
- Creates a `filecheck` kobject with `check`, `fix`, and `set` attributes under the per-device sysfs area.
- `show` for `set` returns the maximum queue size; `show` for `check` or `fix` prints matching queued entries with inode, done flag, and error string.
- `store` parses a positive integer argument, adjusts queue maximum for `set`, or enqueues a check/fix request for an inode.
- Queue management prevents duplicate pending entries, enforces min/max queue sizes, and evicts oldest completed entries when full.
- `ocfs2_filecheck_handle()` runs the actual check/fix by calling `ocfs2_iget()` with filecheck flags and maps returned statuses to filecheck errors.
- Removal deletes the kobject, waits for release completion, then frees completed queue entries.

Important entry points:
- `ocfs2_filecheck_create_sysfs()`
- `ocfs2_filecheck_remove_sysfs()`

Concurrency and lifetime:
- Queue state is protected by `fc_lock`.
- Sysfs show/store wrappers take a kobject reference around attribute callbacks.
- Kobject release signals a completion so mount teardown can wait before freeing backing state.
- Freeing asserts all entries are done.

Important dependencies:
- Uses OCFS2 inode loading/check flags, OCFS2 superblock device kset, kobject/sysfs infrastructure, spinlocks, and masklog.

Risk and edge cases:
- `ocfs2_filecheck_args_get_long()` copies `count` bytes into a fixed stack buffer after caller enforces `count < 24`; that validation is essential.
- Filecheck work is synchronous in the sysfs store path after enqueueing, so a slow inode check can delay the write.
- Queue resizing refuses to drop pending entries and only erases completed ones.
- Error-string lookup BUGs on out-of-range nonzero filecheck status values.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/filecheck.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/filecheck.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/filecheck.h

Purpose: Defines OCFS2 online file-check status codes, queue structures, operation types, limits, and sysfs lifecycle prototypes.

Read coverage: complete file read, 64 lines.

Key contents:
- Filecheck error codes for success, generic failure, in-progress, readonly, JBD involvement, invalid inode, ECC, block number, valid-flag, generation, and unsupported cases.
- Error range macros used by status mapping.
- `struct ocfs2_filecheck` with entry list, spinlock, maximum size, current size, and completed count.
- Queue size limits: maximum 100 and minimum 10.
- Operation types for check, fix, and set-queue-size.
- `struct ocfs2_filecheck_sysfs_entry` containing kobject, unregister completion, and queue pointer.
- Prototypes for creating and removing sysfs state.

Dependencies:
- Requires Linux list/types and OCFS2 superblock context from users.

Risk notes:
- Error enum numeric values are part of the sysfs-visible behavior and must stay aligned with `filecheck.c` string mapping.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/filecheck.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/heartbeat.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/heartbeat.c

Purpose: Maintains OCFS2 node maps and handles cluster node-down notifications by starting recovery.

Read coverage: complete file read, 101 lines.

Key structures and state:
- Operates on `struct ocfs2_node_map`, using a fixed maximum node count and bitmap storage.
- Initializes and protects mount node maps with `osb->node_map_lock`.
- Currently initializes the recovering-orphan-directories node map.

Major logic:
- `ocfs2_init_node_maps()` initializes the node-map spinlock and the orphan recovery node map.
- `ocfs2_do_node_down()` ignores notifications before cluster connection setup, rejects self-death notifications, and starts `ocfs2_recovery_thread()` for the dead node.
- Node-map helpers set, clear, and test bits under `node_map_lock`.
- Set/clear helpers special-case `-1` and return without action.

Concurrency and lifetime:
- Node-map bitmap operations are protected by `node_map_lock`.
- Node-down recovery depends on `osb->cconn` being established; early notifications are intentionally ignored because slot checking later catches them.

Important dependencies:
- Uses Linux bitmap helpers, OCFS2 recovery thread logic, superblock state, and tracepoints.

Risk notes:
- Test-bit with an out-of-range node logs and BUGs; callers must validate node numbers except for the set/clear `-1` special case.
- Ignoring node-down before `cconn` exists assumes later mount/slot recovery will observe the death.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/heartbeat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/heartbeat.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/heartbeat.h

Purpose: Declares OCFS2 heartbeat/node-map initialization, node-down handling, and bitmap helper APIs.

Read coverage: complete file read, 29 lines.

Key contents:
- `ocfs2_init_node_maps()` for mount-time node-map setup.
- `ocfs2_do_node_down()` callback for cluster node failure.
- Node-map set, clear, and test helpers used to track mounted or in-recovery nodes.

Dependencies:
- Consumed by DLM/cluster connection setup and recovery code.

Risk notes:
- Header exposes low-level node-map mutation helpers; callers are responsible for using the correct `ocfs2_node_map` and node number semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/heartbeat.h -->