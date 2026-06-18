# Research Report: subset-b-005737

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlmglue.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/dlmglue.c

Purpose: implements the OCFS2-specific layer over the cluster DLM. It creates and names lock resources, negotiates the locking protocol, handles AST/BAST/unlock callbacks, exposes inode/RW/open/flock/super/rename/NFS-sync/trim/orphan/quota/refcount/dentry locks, refreshes inode and quota state from LVBs or disk, and runs the downconvert thread that releases cached locks when other nodes need them.

Important APIs and functions: exported entry points include `ocfs2_dlm_init`, `ocfs2_dlm_shutdown`, `ocfs2_lock_res_init_once`, the lock resource initializers, `ocfs2_create_new_inode_locks`, `ocfs2_drop_inode_locks`, `ocfs2_rw_lock`, `ocfs2_open_lock`, `ocfs2_inode_lock_full_nested`, `ocfs2_inode_lock_with_folio`, `ocfs2_inode_lock_atime`, `ocfs2_inode_lock_tracker`, `ocfs2_super_lock`, `ocfs2_rename_lock`, `ocfs2_nfs_sync_lock`, `ocfs2_trim_fs_lock`, `ocfs2_dentry_lock`, `ocfs2_file_lock`, `ocfs2_qinfo_lock`, and `ocfs2_refcount_lock`. Core internal machinery is `__ocfs2_cluster_lock`, `ocfs2_cluster_unlock`, `ocfs2_locking_ast`, `ocfs2_blocking_ast`, `ocfs2_unlock_ast`, `ocfs2_unblock_lock`, `ocfs2_downconvert_lock`, `ocfs2_prepare_downconvert`, and `ocfs2_downconvert_thread`.

Control flow: mount setup calls `ocfs2_dlm_init`, starts the downconvert kthread, joins the cluster stack with `lproto`, discovers the local node number, and initializes global lock resources. Normal locking goes through `__ocfs2_cluster_lock`: it waits for incompatible `BUSY` or `BLOCKED` states, attaches or converts the DLM lock, waits for AST completion, records holders, and optionally supports noqueue/nonblocking behavior. BASTs mark a lock blocked, enqueue it, and wake the downconvert thread. The downconvert thread checks holders, refresh state, per-lock downconvert callbacks, checkpoint requirements, and LVB updates before converting to PR or NL. Shutdown marks resources freeing, waits for queued work, drops DLM locks, stops the kthread, frees resources, and disconnects from the cluster.

State and persistence behavior: state is mostly in-memory per `ocfs2_lock_res`: lock level, requested level, blocking level, AST action, unlock action, holder counts, flags, pending generation, waiters, blocked-list membership, lock name, and DLM LKS/LVB contents. LVBs persist cluster-visible summaries for metadata (`ocfs2_meta_lvb`), quota info, orphan scan sequence, and trimfs status. Metadata LVBs mirror inode size, clusters, uid/gid, mode, nlink, packed timestamps, attributes, dynamic features, and generation. When LVBs are invalid or stale, the code purges metadata cache and extent map state and rereads disk dinodes or quota blocks. Debug state is reference-counted and exposed under debugfs as `locking_state` and `locking_filter`.

Dependencies and integration points: this file is central to OCFS2 integration with `stackglue`/DLM, the cluster heartbeat callback (`ocfs2_do_node_down`), journal checkpointing, metadata caches, extent maps, dcache alias invalidation, quota, refcount trees, ACL cache invalidation, slot-map refresh, NFS export synchronization, trim ioctl behavior, and VFS open/read/write/setattr/permission paths. It calls into low-level `ocfs2_dlm_lock`/`ocfs2_dlm_unlock`, `ocfs2_cluster_connect`, `ocfs2_cluster_disconnect`, `ocfs2_refresh_inode`, `ocfs2_refresh_slot_info`, and `ocfs2_start_checkpoint`.

Risks: the pending-generation protocol prevents a race between setting `BUSY` and DLM callbacks; regressions can deadlock or drop another operation's pending state. Downconvert callbacks can sleep and may run while dentries, pages, ACLs, or refcount caches are being invalidated, so holder counts and `FREEING`/`QUEUED` flags must be exact. Metadata LVB trust depends on version and inode generation; stale LVB use can corrupt in-memory inode state. `ocfs2_inode_lock_tracker` forbids recursive PR-to-EX upgrades to avoid cross-node deadlock. `ocfs2_file_lock` has a separate cancelable flock path because user-space can signal blocked flock requests. Local mounts and hard-readonly mounts short-circuit many paths, which needs separate coverage.

Test signals: mount/unmount clustered and local OCFS2; lock protocol negotiation across nodes; concurrent EX/PR inode locks; noqueue `-EAGAIN`; folio-lock retry returning `AOP_TRUNCATED_PAGE`; BAST-triggered downconvert under dirty pages; metadata LVB refresh vs disk refresh; inode deletion while waiting for locks; dentry alias deletion under remote rename/unlink; flock cancellation by signal; NFS export stale-handle synchronization; quota info LVB refresh; trimfs LVB propagation; refcount checkpoint gating; debugfs `locking_state`; and lockdep/KASAN coverage for freeing lock resources with waiters or holders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlmglue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlmglue.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/dlmglue.h

Purpose: declares the OCFS2 cluster-locking interface and LVB wire layouts used by `dlmglue.c` and the rest of the filesystem. It is the public contract for metadata, data/RW, open, dentry, flock, quota, refcount, NFS-sync, trim, orphan-scan, and superblock locking helpers.

Important APIs and types: defines `OCFS2_LVB_VERSION`, `struct ocfs2_meta_lvb`, `struct ocfs2_qinfo_lvb`, `struct ocfs2_orphan_scan_lvb`, `struct ocfs2_trim_fs_lvb`, `struct ocfs2_trim_fs_info`, and `struct ocfs2_lock_holder`. It declares all lock lifecycle and acquisition functions, including `ocfs2_dlm_init`, `ocfs2_dlm_shutdown`, `ocfs2_create_new_inode_locks`, `ocfs2_rw_lock`, `ocfs2_open_lock`, `ocfs2_inode_lock_full_nested`, `ocfs2_inode_lock_with_folio`, `ocfs2_inode_lock_tracker`, `ocfs2_super_lock`, `ocfs2_nfs_sync_lock`, `ocfs2_trim_fs_lock`, `ocfs2_file_lock`, `ocfs2_qinfo_lock`, and `ocfs2_refcount_lock`.

Control flow: the header has no active control flow, but its wrappers shape call sites. `ocfs2_inode_lock`, `ocfs2_try_inode_lock`, `ocfs2_inode_lock_full`, and `ocfs2_inode_lock_nested` standardize normal, noqueue, flagged, and lockdep-subclassed metadata locking. `OCFS2_META_LOCK_RECOVERY`, `OCFS2_META_LOCK_NOQUEUE`, `OCFS2_LOCK_NONBLOCK`, and `OCFS2_META_LOCK_GETBH` alter waiting, DLM queueing, folio-lock avoidance, and disk-buffer retrieval.

State and persistence behavior: the LVB structs are DLM lock value block formats shared between nodes. They store inode metadata, quota grace/free counts, orphan scan sequence numbers, and trimfs result metadata in big-endian fields. `ocfs2_lock_holder` is transient stack-associated state used to detect and suppress recursive cluster locking inside one task.

Dependencies and integration points: includes `dcache.h` for dentry-lock data and forwards OCFS2-specific types from inode, quota, refcount, and file layers. Callers across file, inode, dir, quota, refcount, export, xattr, and recovery code rely on these declarations to coordinate cluster coherence before reading or mutating shared disk structures.

Risks: LVB layout changes require matching protocol/version handling in clustered deployments. Misusing `OCFS2_META_LOCK_GETBH` or the tracker API can bypass expected lock acquisition or mask recursive locking bugs. The noqueue/nonblock flags are used to avoid deadlocks with folio locks and nowait I/O, so callers must propagate `-EAGAIN` or `AOP_TRUNCATED_PAGE` correctly.

Test signals: compile coverage for all OCFS2 configs, mixed-node lock protocol tests, metadata LVB version compatibility, noqueue inode-lock users, recursive ACL/setattr and permission paths, trim/orphan LVB read/write, and callers using `ocfs2_inode_lock_with_folio` from address-space operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlmglue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/export.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/export.c

Purpose: implements `export_operations` so OCFS2 can be exported through NFS. It encodes inode and parent file handles, decodes file handles back to dentries, validates stale handles, and obtains parent dentries for reconnectable exports.

Important APIs and functions: defines the on-wire-ish `struct ocfs2_inode_handle` containing block number and generation. Main routines are `ocfs2_get_dentry`, `ocfs2_get_parent`, `ocfs2_encode_fh`, `ocfs2_fh_to_dentry`, `ocfs2_fh_to_parent`, and the exported `ocfs2_export_ops`.

Control flow: handle decode validates a nonzero block number, first checks the inode cache with `ocfs2_ilookup`, and otherwise takes the NFS sync lock in EX mode before testing the inode allocator bit and reading the inode with `ocfs2_iget`. Generation mismatch returns `-ESTALE`. Parent lookup takes the NFS sync lock and a metadata lock on the child directory, resolves `".."`, validates the allocator bit, and obtains the parent alias. Encoding requires three 32-bit words for the target and six when a parent is supplied; insufficient buffers return `FILEID_INVALID` and the required size.

State and persistence behavior: file handles persist only the inode block number and generation, plus optional parent block/generation. The NFS sync DLM lock serializes handle decode against cross-node inode deletion so stale handles cannot race allocator reuse. No persistent state is stored by this file itself.

Dependencies and integration points: integrates VFS exportfs callbacks with OCFS2 inode lookup, allocator bitmap validation, metadata locking, dentry aliasing, tracing, and `ocfs2_nfs_sync_lock` from `dlmglue.c`. It is used when the superblock installs `ocfs2_export_ops`.

Risks: stale-handle detection depends on both allocator-bit validation and generation comparison. Missing the NFS sync lock would race remote inode deletion and reuse. Parent lookup returns `-ENOENT` for failed `".."` lookup but `-ESTALE` for invalid allocator state; NFS clients can observe these as different recovery behaviors. File-handle endianness is explicitly little-endian in the raw fid words.

Test signals: NFS export mount, lookup by file handle after inode eviction, stale handle after unlink/reuse, parent reconnect of disconnected dentries, insufficient file-handle buffer lengths, generation mismatch, invalid block number zero, allocator-bit clear, and multi-node deletion while NFS decode is in progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/export.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/export.h

Purpose: declares the OCFS2 NFS/exportfs operation table.

Important APIs and types: includes `<linux/exportfs.h>` and exposes `extern const struct export_operations ocfs2_export_ops`.

Control flow: none in the header. It provides the symbol that superblock setup can reference to enable NFS export support.

State and persistence behavior: none directly; state is handled by `export.c` through encoded file handles and OCFS2 inode generation/block numbers.

Dependencies and integration points: used by OCFS2 superblock/export setup code and implemented by `export.c`. It connects OCFS2 to the generic Linux exportfs/NFS server infrastructure.

Risks: the header is intentionally narrow. The main compatibility risk is that any change to `ocfs2_export_ops` consumers must keep this declaration synchronized.

Test signals: build coverage with exportfs/NFS server support and mounting an exported OCFS2 volume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/extent_map.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/extent_map.c

Purpose: provides OCFS2 logical-to-physical cluster and block mapping helpers, a tiny per-inode extent cache, fiemap reporting, overwrite detection, SEEK_DATA/SEEK_HOLE support, xattr extent lookup, and virtual block reads through mapped physical blocks.

Important APIs and functions: exported functions are `ocfs2_extent_map_init`, `ocfs2_extent_map_trunc`, `ocfs2_extent_map_insert_rec`, `ocfs2_get_clusters`, `ocfs2_extent_map_get_blocks`, `ocfs2_xattr_get_clusters`, `ocfs2_fiemap`, `ocfs2_overwrite_io`, `ocfs2_seek_data_hole_offset`, `ocfs2_read_virt_blocks`, and `ocfs2_figure_hole_clusters`. Internal helpers include `ocfs2_extent_map_lookup`, `ocfs2_get_clusters_nocache`, `ocfs2_last_eb_is_empty`, `ocfs2_search_for_hole_index`, and `ocfs2_fiemap_inline`.

Control flow: cluster lookup first probes the small extent cache under `ip_lock`; cache miss reads the dinode and descends the extent tree if needed. Holes return physical cluster zero plus a hole length, while real extents are converted to relative physical cluster offsets and inserted into the cache. Fiemap takes the metadata lock and `ip_alloc_sem`, handles inline data and fast symlinks specially, walks extents/hole gaps, and emits unwritten/shared/last flags. SEEK_DATA/SEEK_HOLE uses the same uncached extent walk under locks and treats unwritten extents as holes. Virtual block reads map each block run to physical blocks and call `ocfs2_read_blocks`.

State and persistence behavior: the extent cache is in-memory only, capped at `OCFS2_MAX_EXTENT_MAP_ITEMS` and maintained as an MRU list. It is truncated on allocation changes, inode refresh, remap, and truncate paths. Persistent extent state lives in dinode and extent-block trees; this file validates extent-list depth, counts, nonzero physical block numbers, and leaf-link assumptions before reporting mappings.

Dependencies and integration points: depends on allocation tree search/read helpers, dinode reads, metadata locks from `dlmglue.c`, `ip_alloc_sem`, fiemap VFS helpers, buffer-head I/O, symlink inline-data helpers, and OCFS2 tracing. It feeds read paths, write preparation, hole punching, reflink/CoW checks, fiemap ioctl, lseek, xattr reads, and metadata virtual-block reads.

Risks: the cache accepts overlapping records only in narrow replacement cases and requires callers to call `ocfs2_extent_map_trunc` after deletions. Extent tree corruption is converted to `-EROFS` via `ocfs2_error`, so validation paths are safety-critical. `ocfs2_read_virt_blocks` returns `-EAGAIN` if `ip_alloc_sem` is temporarily unavailable and `-EIO` on unexpected holes; callers must be prepared. Fiemap deliberately drops and reacquires `ip_alloc_sem` around `fiemap_fill_next_extent` to avoid page-fault deadlock.

Test signals: sparse file reads and writes, inline-data and fast-symlink fiemap, unwritten extent fiemap flags, reflink/shared extent flags, SEEK_DATA/SEEK_HOLE over holes/unwritten/data, xattr extent lookup, extent-cache hit/merge/truncate behavior, corrupt extent depth/count/zero-block handling, virtual block readahead, and concurrent allocation changes protected by `ip_alloc_sem`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/extent_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/extent_map.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/extent_map.h

Purpose: declares OCFS2 extent mapping data structures and APIs for translating file offsets to disk blocks, reporting extents, detecting overwrite I/O, and reading mapped metadata/data blocks.

Important APIs and types: defines `struct ocfs2_extent_map_item`, `OCFS2_MAX_EXTENT_MAP_ITEMS`, and `struct ocfs2_extent_map`. Declares `ocfs2_extent_map_init`, `ocfs2_extent_map_trunc`, `ocfs2_extent_map_insert_rec`, `ocfs2_get_clusters`, `ocfs2_extent_map_get_blocks`, `ocfs2_fiemap`, `ocfs2_overwrite_io`, `ocfs2_seek_data_hole_offset`, `ocfs2_xattr_get_clusters`, `ocfs2_read_virt_blocks`, `ocfs2_figure_hole_clusters`, and inline `ocfs2_read_virt_block`.

Control flow: the header's only executable path is `ocfs2_read_virt_block`, which validates that the caller supplied a buffer-head pointer and delegates to `ocfs2_read_virt_blocks` for one block.

State and persistence behavior: the map structs describe an in-memory, per-inode MRU cache of a few logical cluster runs and their physical mappings/flags. Persistent extent state remains on disk in OCFS2 dinode and extent block structures.

Dependencies and integration points: consumers include address-space operations, file write preparation, fiemap/lseek/ioctl code, xattr code, and metadata readers. The API assumes callers hold the proper metadata and allocation locks as documented in `extent_map.c`.

Risks: the small cache size is intentional; callers must not assume full mapping coverage. Misusing the APIs without `ip_alloc_sem` can race allocation changes. `ocfs2_read_virt_block` returns `-EINVAL` for a NULL output pointer and logs directly.

Test signals: compile coverage of all declarations, single-block virtual reads, cache initialization on inode setup, cache truncation after allocation changes, and callers handling holes and unwritten/refcounted extent flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/extent_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/file.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/file.c

Purpose: implements OCFS2 regular-file and directory VFS operations: open/release, fsync, atime, setattr/getattr/permission, extend/truncate, zero extension, allocation reservation and hole punching, direct/buffered read and write iteration, lseek, fallocate, reflink remap, and operation tables with and without cluster POSIX locks.

Important APIs and functions: public helpers include `ocfs2_set_inode_size`, `ocfs2_simple_size_update`, `ocfs2_truncate_file`, `ocfs2_add_inode_data`, `ocfs2_extend_no_holes`, `ocfs2_zero_extend`, `ocfs2_setattr`, `ocfs2_getattr`, `ocfs2_permission`, `ocfs2_should_update_atime`, `ocfs2_update_inode_atime`, `ocfs2_change_file_space`, `ocfs2_check_range_for_refcount`, and `ocfs2_remove_inode_range`. VFS tables are `ocfs2_file_iops`, `ocfs2_special_file_iops`, `ocfs2_fops`, `ocfs2_dops`, `ocfs2_fops_no_plocks`, and `ocfs2_dops_no_plocks`. Major internal paths are `ocfs2_extend_allocation`, `ocfs2_orphan_for_truncate`, `ocfs2_extend_file`, `ocfs2_allocate_unwritten_extents`, `__ocfs2_change_file_space`, `ocfs2_prepare_inode_for_write`, `ocfs2_file_write_iter`, `ocfs2_file_read_iter`, `ocfs2_file_llseek`, and `ocfs2_remap_file_range`.

Control flow: open initializes per-file private state and flock lock resources, increments inode open counts, handles direct-open flags, and initializes quotas for writers. Size changes in `ocfs2_setattr` wait for DIO, take RW and metadata locks, then call truncate or extend paths. Truncate CoWs partial reflink clusters, zeros cluster tails, updates i_size in a journal transaction, truncates page cache, and commits allocation removal. Extension converts inline data if necessary, allocates clusters for non-sparse files, zeroes exposed allocated data, and updates disk inode size. Writes take inode mutex, cluster RW locks, optional metadata lock for full coherency direct I/O, generic write checks, CoW/refcount preparation, suid removal, and then generic write; asynchronous DIO may defer RW unlock to end I/O. Reads update atime through metadata locking and only take RW locks for direct I/O. Fallocate and OCFS2 space ioctls funnel through `__ocfs2_change_file_space` for unwritten allocation or range removal.

State and persistence behavior: persistent updates are journaled through OCFS2 transactions and dinode buffer-head dirtying. The file mutates inode size, block count, ctime/mtime/atime, dinode size/timestamps/mode, allocation trees, truncate logs, quotas, unwritten/refcount extent state, and page cache mappings. Per-open state is `struct ocfs2_file_private`, including a directory seek cookie, mutex, and per-file flock lock resource. It updates fsync transaction ids and handles ordered-data transactions for zeroing/truncate.

Dependencies and integration points: depends on DLM locks from `dlmglue.c`, extent mapping, allocation btrees, journals/JBD2, quotas, refcount/reflink code, inline-data conversion, mmap, ioctl, ACL/xattr/fileattr helpers, Linux generic file read/write/splice/fallocate/remap helpers, direct I/O end handling, buffer-head I/O, and block-device flush/zeroout helpers.

Risks: file size and allocation changes require strict lock ordering among `i_rwsem`, OCFS2 RW lock, metadata lock, `ip_alloc_sem`, DIO wait, quotas, and journal handles. Partial-cluster zeroing is subtle for reflinks, EOF, sparse files, unwritten extents, and non-page-cache zeroout. Nowait paths must return `-EAGAIN` without sleeping and are only supported for direct I/O. Async direct I/O unlock ownership is split with end-I/O state in the kiocb. Error mapping in `ocfs2_setattr` collapses some size-change failures to `-ENOSPC`. Remap must truncate destination page cache and invalidate both extent maps after sharing blocks.

Test signals: open/release counts and direct-open flag clearing; fsync with data barriers; atime behavior under noatime/relatime/NFSD no-mount cases; setattr truncate/extend/chown/chmod and ACL chmod; sparse and non-sparse extension; inline-data conversion; reflink CoW on writes/truncate/hole punch; fallocate keep-size and punch-hole; suid/sgid removal before writes; buffered and direct writes under full/buffered coherency mounts; nowait direct I/O; async DIO unlock completion; SEEK_SET/END/CUR/DATA/HOLE; remap/dedupe on refcount-enabled volumes; and quota transfer/allocation failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/file.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/file.h

Purpose: declares OCFS2 file and inode operation tables plus helper routines used by allocation, truncate, setattr, atime, file-space, and refcount/CoW paths.

Important APIs and types: exposes `ocfs2_fops`, `ocfs2_dops`, lockless variants, `ocfs2_file_iops`, and `ocfs2_special_file_iops`. Defines `struct ocfs2_file_private` with directory seek cookie, backing file pointer, mutex, and file flock lock resource. Declares allocation and size helpers such as `ocfs2_add_inode_data`, `ocfs2_set_inode_size`, `ocfs2_simple_size_update`, `ocfs2_truncate_file`, `ocfs2_extend_no_holes`, `ocfs2_zero_extend`, `ocfs2_change_file_space`, `ocfs2_check_range_for_refcount`, and `ocfs2_remove_inode_range`.

Control flow: no active control flow beyond declarations. The operation table symbols are installed on OCFS2 inodes, and helper declarations allow other modules to participate in file growth, truncation, allocation changes, and VFS attribute handling.

State and persistence behavior: `ocfs2_file_private` is per-open runtime state and owns the file-specific flock lock resource initialized in `file.c` and dropped on release. The declared helpers persist inode size, extents, quota, timestamps, and refcount changes through journaled implementations.

Dependencies and integration points: included by `file.c`, `dlmglue.c`, allocation/refcount code, inode setup, and ioctl paths. It bridges VFS operation registration with OCFS2 internals.

Risks: operation-table variants must remain synchronized except for POSIX lock callbacks. Any layout change to `ocfs2_file_private` must stay compatible with file-lock initialization/freeing and directory llseek cookie use.

Test signals: build coverage, regular and directory open/release, clustered flock paths, localflocks/no-plock mounts choosing lockless operation tables, and external callers of truncate/allocation helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/filecheck.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/filecheck.c

Purpose: implements OCFS2 online file checking through a per-volume sysfs directory. Users can request inode checks, inode fixes, and queue-size changes, then read back recent check/fix results.

Important APIs and functions: public lifecycle functions are `ocfs2_filecheck_create_sysfs` and `ocfs2_filecheck_remove_sysfs`. Internal types include `struct ocfs2_filecheck_entry` and `struct ocfs2_filecheck_args`. Main helpers are `ocfs2_filecheck_attr_show`, `ocfs2_filecheck_attr_store`, `ocfs2_filecheck_adjust_max`, `ocfs2_filecheck_args_parse`, `ocfs2_filecheck_handle`, `ocfs2_filecheck_handle_entry`, and queue erasure/done helpers.

Control flow: mount setup allocates `struct ocfs2_filecheck`, initializes the list/spinlock/default maximum, and creates a `filecheck` kobject with `check`, `fix`, and `set` attributes. Stores parse the attribute name into an operation, parse a positive numeric inode or queue length, reject duplicates among pending entries, enforce the queue maximum, optionally erase the oldest completed entry, enqueue an in-progress entry, then synchronously call `ocfs2_iget` with check or fix flags. Shows render the current max for `set` or a table of inode, done flag, and error string for matching check/fix entries. Removal deletes the kobject, waits for release completion, and frees only completed entries.

State and persistence behavior: queue state is in memory under `fc_lock`: maximum size, current size, completed count, and list of recent entries. File repair/check persistence is delegated to `ocfs2_iget` with `OCFS2_FI_FLAG_FILECHECK_CHK` or `OCFS2_FI_FLAG_FILECHECK_FIX`, which may validate or repair on-disk inode metadata. The sysfs kobject lifetime is guarded with a completion.

Dependencies and integration points: integrates Linux sysfs/kobject operations, OCFS2 superblock device kset, inode loading/check logic, stackglue-visible filecheck errors, and masklog. It is invoked from superblock lifecycle code, not normal file I/O.

Risks: `ocfs2_filecheck_args_get_long` copies `count` bytes into a fixed buffer after the caller enforces `count < 24`; that guard must remain. Queue manipulation assumes callers hold `fc_lock` for duplicate/erase/list updates. `ocfs2_filecheck_sysfs_free` BUGs if removal sees unfinished entries, so teardown must not race an active store. The operation is synchronous despite recording an in-progress entry, so slow inode checks can make sysfs writes block.

Test signals: create/remove sysfs on mount/unmount; write valid and invalid inode numbers to `check` and `fix`; read result tables; duplicate pending request rejection; queue-full `-EAGAIN`; queue-size bounds 10 to 100; shrinking queue with completed entries; read-only/fix failure statuses; invalid inode, block ECC/block number/valid flag/generation errors from inode check; and concurrent sysfs readers/writers during unmount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/filecheck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/filecheck.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/filecheck.h

Purpose: defines the OCFS2 online file-check sysfs API data model, status codes, queue sizing limits, and lifecycle declarations.

Important APIs and types: declares filecheck error constants from `OCFS2_FILECHECK_ERR_SUCCESS` through `OCFS2_FILECHECK_ERR_UNSUPPORTED`, queue limits `OCFS2_FILECHECK_MAXSIZE` and `OCFS2_FILECHECK_MINSIZE`, operation types `OCFS2_FILECHECK_TYPE_CHK`, `OCFS2_FILECHECK_TYPE_FIX`, and `OCFS2_FILECHECK_TYPE_SET`, `struct ocfs2_filecheck`, `struct ocfs2_filecheck_sysfs_entry`, `ocfs2_filecheck_create_sysfs`, and `ocfs2_filecheck_remove_sysfs`.

Control flow: no active control flow. The enums drive `filecheck.c` parsing and status rendering for `check`, `fix`, and `set` sysfs files.

State and persistence behavior: `struct ocfs2_filecheck` holds transient queue/list state protected by a spinlock. `struct ocfs2_filecheck_sysfs_entry` embeds the kobject and completion used to coordinate sysfs lifetime with superblock teardown.

Dependencies and integration points: includes Linux list/types support and is consumed by OCFS2 superblock lifecycle and `filecheck.c`. Error codes are intentionally distinct from normal negative errno so they can describe domain-specific filecheck outcomes.

Risks: error enum ordering must match the string table in `filecheck.c`. Queue limits are part of sysfs behavior and tests may depend on them. Teardown requires all entries to be complete before freeing.

Test signals: compile coverage, enum-to-string mapping, queue max/min behavior, sysfs kobject lifetime, and all defined status codes surfaced through check/fix result output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/filecheck.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/heartbeat.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/heartbeat.c

Purpose: maintains OCFS2 node maps and handles cluster node-down notifications by triggering recovery for failed peers.

Important APIs and functions: public functions are `ocfs2_init_node_maps`, `ocfs2_do_node_down`, `ocfs2_node_map_set_bit`, `ocfs2_node_map_clear_bit`, and `ocfs2_node_map_test_bit`. Internal `ocfs2_node_map_init` initializes a bitmap map to `OCFS2_NODE_MAP_MAX_NODES`.

Control flow: superblock setup initializes `node_map_lock` and the orphan-directory recovery map. The cluster stack calls `ocfs2_do_node_down` with a failed node number; the function rejects self-death with `BUG_ON`, ignores events before a cluster connection exists, and otherwise starts `ocfs2_recovery_thread`. Node-map helpers set, clear, and test bits under the superblock spinlock, with a legacy special case that ignores bit `-1` for set/clear.

State and persistence behavior: node maps are in-memory bitmaps tracking mounted or recovering nodes; no persistent disk state is written here. Recovery triggered by node-down events may later affect journal/orphan cleanup through other modules.

Dependencies and integration points: depends on OCFS2 superblock state, cluster heartbeat callbacks registered by `dlmglue.c`, journal recovery, inode/allocation headers, bitmap operations, and tracing.

Risks: bit bounds are enforced with `BUG_ON`/`BUG`, so invalid node numbers can crash the kernel. Ignoring `-1` in set/clear but not in test reflects legacy caller behavior and should not be broadened silently. Node-down events before `osb->cconn` are intentionally ignored because slot checks after cluster setup catch existing deaths.

Test signals: mount initialization of node maps, node-down callback for remote nodes, rejection of local node number, recovery thread invocation, set/clear/test under concurrent callers, out-of-range node-number assertions in debug testing, and early node-down before cluster connection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/heartbeat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/heartbeat.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/heartbeat.h

Purpose: declares OCFS2 heartbeat/node-map helpers used to initialize node tracking, react to node death, and update/test recovery maps.

Important APIs and types: declares `ocfs2_init_node_maps`, `ocfs2_do_node_down`, `ocfs2_node_map_set_bit`, `ocfs2_node_map_clear_bit`, and `ocfs2_node_map_test_bit` over `struct ocfs2_super` and `struct ocfs2_node_map`.

Control flow: no active control flow; callers use these declarations from superblock and cluster callback setup.

State and persistence behavior: declared helpers mutate in-memory node-map bitmaps under `node_map_lock` and initiate recovery on node-down notifications. There is no direct persistent format in the header.

Dependencies and integration points: consumed by DLM/cluster connection setup, journal recovery, orphan directory recovery, and any code tracking mounted or recovering nodes.

Risks: the API assumes callers pass valid node numbers except for the set/clear `-1` legacy case implemented in `heartbeat.c`. Callers must use the helpers rather than open-coding bitmap access to preserve locking.

Test signals: build coverage, node map initialization at mount, heartbeat callback wiring, and recovery map updates observed during simulated node failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/heartbeat.h -->
