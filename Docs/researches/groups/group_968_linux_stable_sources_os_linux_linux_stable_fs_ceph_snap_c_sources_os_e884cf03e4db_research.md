# Group Research: Linux stable Ceph snapshot/super/xattr/subvolume metrics, char device, and Coda client files

This group covers CephFS snapshot realm management, mount/superblock setup, shared CephFS state definitions, xattr and virtual-xattr handling, subvolume I/O metrics, Linux character-device registration/open dispatch, and Coda client VFS glue around Venus upcalls.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/snap.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/snap.c

## Purpose
Implements CephFS client-side snapshot realm tracking, snap context construction, cap-snap queuing/flushing, MDS snapshot notification handling, and snapid-to-device mappings for snapped inode presentation.

## Main Interfaces
- Realm references and lookup: `ceph_get_snap_realm()`, `ceph_put_snap_realm()`, `ceph_lookup_snap_realm()`, `ceph_cleanup_global_and_empty_realms()`.
- MDS trace/update handling: `ceph_update_snap_trace()`, `ceph_handle_snap()`.
- Inode realm movement: `ceph_change_snap_realm()`.
- Cap-snap lifecycle: `__ceph_finish_cap_snap()`, internal `ceph_queue_cap_snap()`, `queue_realm_cap_snaps()`, `flush_snaps()`.
- Snap device map: `ceph_get_snapid_map()`, `ceph_put_snapid_map()`, `ceph_trim_snapid_map()`, `ceph_cleanup_snapid_map()`.

## Control Flow
Snapshot state is represented as a hierarchy of `ceph_snap_realm` objects keyed by realm inode number in `mdsc->snap_realms`. MDS snap traces update realm parentage, snap lists, prior-parent snap lists, creation sequence, and realm sequence. When a realm or one of its ancestors changes, `rebuild_snap_realms()` walks downward and `build_snap_context()` composes a reverse-sorted `ceph_snap_context` from parent snaps after `parent_since`, explicit realm snaps, and prior-parent snaps.

When new contexts are built, dirty realms are queued and all inodes with caps in those realms get cap-snap processing. `ceph_queue_cap_snap()` snapshots inode metadata/xattr state when dirty caps, buffered writes, or in-progress writes must be associated with the old snap context. `__ceph_finish_cap_snap()` finalizes size/time/truncate/change metadata once writes and dirty pages are done, then places the inode on `mdsc->snap_flush_list` for `ceph_flush_snaps()`.

`ceph_handle_snap()` decodes MDS snapshot messages. For `CEPH_SNAP_OP_SPLIT`, it moves listed inodes and child realms into a new realm before applying the snap trace. Corrupt snap traces fence I/O, try to blocklist the client, warn, and require remount after MDS-side repair.

## State And Synchronization
Realm topology is protected by `mdsc->snap_rwsem`; zero-reference realms are staged on `mdsc->snap_empty` under `snap_empty_lock` when immediate destruction cannot take the write semaphore. Inodes are attached to realm `inodes_with_caps` lists under per-realm spinlocks and inode `i_ceph_lock`. Cap-snap flushing uses `mdsc->snap_flush_lock`.

The snapid map uses an rb-tree plus LRU list under `snapid_map_lock`, allocates anonymous block devices via `get_anon_bdev()`, and trims unused mappings after `CEPH_SNAPID_MAP_TIMEOUT`.

## Integration Points
Depends on MDS client message decoding, inode/cap code, `ceph_flush_snaps()`, OSD writeback paths, `ceph_monc_blocklist_add()`, and snapshot context APIs from libceph. It is central to write ordering across distributed CephFS snapshots.

## Risks And Review Focus
- Realm reference transitions are subtle because 0-to-1 and 1-to-0 must coordinate with `snap_empty_lock`.
- Snap trace corruption deliberately fences client I/O; decode bounds and error paths are high-impact.
- Cap-snap creation must preserve metadata exactly at the snapshot boundary despite concurrent writes and writeback.
- Split handling races with other MDS notifications and must avoid moving inodes from newer realms.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/snap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/strings.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/strings.c

## Purpose
Provides human-readable names for CephFS MDS states, session operations, MDS operations, capability operations, lease operations, and snapshot operations.

## Main Interfaces
- `ceph_mds_state_name()`
- `ceph_session_op_name()`
- `ceph_mds_op_name()`
- `ceph_cap_op_name()`
- `ceph_lease_op_name()`
- `ceph_snap_op_name()`

## Behavior
Each function switches over protocol constants from Ceph headers and returns a stable string used in debug output, traces, logging, and diagnostics. Unknown values return `"???"`.

## Integration Points
Used by CephFS debugging and message handling code to make protocol-level state transitions readable.

## Risks And Review Focus
- Tables must stay synchronized with Ceph protocol constants.
- These helpers are diagnostic-only, but stale names can mislead debugging of MDS/session/cap behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/strings.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/subvolume_metrics.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/subvolume_metrics.c

## Purpose
Implements per-subvolume CephFS I/O metrics collection, snapshotting, debugfs dumping, and slab-cache lifecycle for metric rb-tree entries.

## Main Interfaces
- Tracker lifecycle: `ceph_subvolume_metrics_init()`, `ceph_subvolume_metrics_destroy()`, `ceph_subvolume_metrics_enable()`.
- Recording: `ceph_subvolume_metrics_record()`, `ceph_subvolume_metrics_record_io()`.
- Snapshot/reporting: `ceph_subvolume_metrics_snapshot()`, `ceph_subvolume_metrics_free_snapshot()`, `ceph_subvolume_metrics_dump()`.
- Cache lifecycle: `ceph_subvolume_metrics_cache_init()`, `ceph_subvolume_metrics_cache_destroy()`.

## Control Flow
Metrics are stored in a cached rb-tree keyed by subvolume ID. Recording skips disabled trackers, unknown subvolume ID `0`, zero-size operations, and zero latency. On a miss, the code drops the spinlock, allocates a new entry from `ceph_subvol_metric_entry_cachep`, then retries under lock to handle concurrent insertion. Read/write operation counts, byte totals, and latency sums are updated per entry, while cumulative tracker totals are atomics.

`snapshot()` first counts active entries under lock, allocates an array, then walks the tree again to copy active entries into `ceph_subvol_metric_snapshot` records. With `consume=true`, copied entries are reset and removed. Entries with no activity are pruned during snapshot walking. `dump()` formats current active entries directly to a `seq_file`.

## State And Synchronization
`tracker->lock` protects the rb-tree and `nr_entries`; `enabled` is read with `READ_ONCE()` and rechecked under lock. Debug counters and cumulative totals use `atomic64_t`.

## Integration Points
`ceph_subvolume_metrics_record_io()` links the tracker to CephFS I/O paths by reading `ci->i_subvolume_id`, measuring elapsed `ktime`, and dispatching read/write activity into `mdsc->subvol_metrics`.

## Risks And Review Focus
- Allocation outside the spinlock is correct but relies on retry/free paths staying balanced.
- Snapshot count and copy are separated, so races are handled by truncating to the allocated count and warning.
- Locking around `seq_printf()` keeps output consistent but can hold the spinlock while formatting many entries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/subvolume_metrics.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/subvolume_metrics.h -->
# File Research: sources/os/linux/linux-stable/fs/ceph/subvolume_metrics.h

## Purpose
Declares the CephFS subvolume metrics data structures and API.

## Main Contents
- `struct ceph_subvol_metric_snapshot`: exported snapshot row containing subvolume ID, read/write ops, byte totals, and latency sums.
- `struct ceph_subvolume_metrics_tracker`: spinlock, cached rb-tree, enable flag, entry count, debug counters, and cumulative read/write totals.
- Function prototypes for lifecycle, enable/disable, record, snapshot, dump, I/O wrapper, and slab-cache lifecycle.
- Inline `ceph_subvolume_metrics_enabled()` using `READ_ONCE()`.

## Integration Points
Included by CephFS MDS/client and debugfs code. The tracker is embedded in `struct ceph_mds_client`, while the implementation records I/O using `struct ceph_inode_info`.

## Risks And Review Focus
- `enabled` is a fast-path lockless read; callers that need tree consistency must still use implementation locking.
- The snapshot structure exposes latency sums, not averages; consumers must divide by operation counts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/subvolume_metrics.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/super.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/super.c

## Purpose
Implements CephFS filesystem registration, mount option parsing, fs-context operations, superblock setup/sharing, root open, unmount/shutdown/reconnect handling, cache initialization, and module parameters.

## Main Interfaces
- Super operations: `ceph_put_super()`, `ceph_statfs()`, `ceph_sync_fs()`, `ceph_umount_begin()`, `ceph_super_ops`.
- Mount parsing: `ceph_parse_mount_param()`, `ceph_parse_source()`, `ceph_parse_mon_addr()`.
- Client lifecycle: `create_fs_client()`, `destroy_fs_client()`.
- Mount lifecycle: `ceph_init_fs_context()`, `ceph_get_tree()`, `ceph_real_mount()`, `ceph_kill_sb()`.
- Recovery/module: `ceph_force_reconnect()`, `init_ceph()`, `exit_ceph()`.

## Control Flow
Mount setup starts with `ceph_init_fs_context()`, which allocates generic Ceph options and CephFS mount options with defaults. `ceph_parse_mount_param()` accepts both libceph parameters and CephFS-specific options such as sizes, readdir limits, snapdir name, namespace, fscache, ACLs, pagecache bypass, sparse read, async dir ops, and dummy encryption.

`ceph_get_tree()` validates source syntax, creates a new `ceph_fs_client`, initializes the MDS client, and uses `sget_fc()` to either share an existing superblock with matching options or install a new one via `ceph_set_super()`. `ceph_real_mount()` opens the cluster session, registers fscache/debugfs as needed, applies dummy encryption, sends a root `GETATTR` request, and installs the root dentry.

Unmount begins with MDS pre-umount and workqueue flush, then forces `sync_filesystem()`, waits for dirty folios and stopping blockers, kills the anonymous superblock, cleans debugfs/fscache, and destroys the fs client. Forced reconnect aborts OSD/MDS requests, invalidates open file generations, resets client address/abort state, and refreshes root attributes.

## State And Synchronization
Global `ceph_fsc_list` is protected by `ceph_fsc_lock` and is used for metrics wakeups when the module parameter changes. Mount operations serialize on `client->mount_mutex`. Stopping blockers use `mdsc->stopping_lock`, `stopping_blockers`, and `stopping_waiter` to prevent teardown while metadata or data I/O is active.

## Integration Points
Connects VFS fs-context and superblock APIs to libceph client creation, monitor map dispatch, MDS map/fsmap handling, MDS request execution, fscache, fscrypt, debugfs, quota statfs, and CephFS inode/dentry/export/xattr operations.

## Risks And Review Focus
- Source parsing supports old and new mount syntaxes; namespace and monitor-address validation must remain exact.
- Superblock sharing depends on complete option comparison and blocklist/shutdown state checks.
- Unmount ordering is sensitive: accepting late MDS messages after flush can resurrect inode refs.
- Reconfigure only updates a limited option subset; new remount-mutability should be deliberate.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/super.h -->
# File Research: sources/os/linux/linux-stable/fs/ceph/super.h

## Purpose
Defines the central CephFS kernel-client data structures, mount option flags, inode/cap/snapshot/xattr state, helper inlines, and cross-file prototypes.

## Main Contents
- Mount definitions: block sizing, default read/write/readdir/readahead limits, snapdir name, mount option flags, and `struct ceph_mount_options`.
- Client state: `struct ceph_fs_client` with superblock, mount options, libceph client, MDS client, mount state, workqueues, fscache/debugfs/fscrypt state, async unlink tracking, and writeback congestion.
- Capability state: `struct ceph_cap`, `struct ceph_cap_flush`, `struct ceph_cap_snap`, cap reference helpers, dirty/flushing state, and prototypes for caps code.
- Inode state: `struct ceph_inode_info` embedding `netfs_inode`, Ceph vino, layout, directory stats, quotas, subvolume ID, fragtree, xattrs, caps, cap snaps, snap realm/map union, truncation/writeback fields, fscrypt data, work bits, and flags.
- Dentry/file state: `struct ceph_dentry_info`, `struct ceph_file_info`, `struct ceph_dir_file_info`, `struct ceph_rw_context`, and readdir cache control.
- Snapshot state: `struct ceph_snap_realm` and snap-related prototypes.
- Prototypes for inode, xattr, ACL, file, dir, ioctl, export, lock, quota, debugfs, and stopping-blocker functions.

## Important Helpers
The header provides conversion helpers between VFS objects and CephFS objects, inode number presentation with `ino32`, reserved inode filtering, directory completeness sequence helpers, quota update helpers, capability-issued wrappers, workqueue scheduling helpers, and `ceph_inode_is_shutdown()`.

## Integration Points
Almost every CephFS implementation file includes this header. It is the shared contract between superblock/mount code, inode metadata, caps, MDS client, xattr, directory, file I/O, quota, fscrypt, fscache, and netfs paths.

## Risks And Review Focus
- Structure fields encode lock ownership assumptions; changing them without matching lock rules can break caps, xattrs, or snapshot flushing.
- `ceph_inode_info` has many cross-subsystem fields, making initialization and eviction consistency important.
- Inline helpers such as directory completeness and mount-state shutdown checks are used on fast paths and must preserve memory-ordering assumptions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/super.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/util.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/util.c

## Purpose
Provides non-inline CephFS utility helpers for file layout conversion/validation and mapping VFS open flags to Ceph file modes/capabilities.

## Main Interfaces
- `ceph_file_layout_is_valid()`
- `ceph_file_layout_from_legacy()`
- `ceph_file_layout_to_legacy()`
- `ceph_flags_to_mode()`
- `ceph_caps_for_mode()`

## Behavior
Layout validation requires nonzero stripe unit/object size, 64 KiB alignment, object size as a multiple of stripe unit, and nonzero stripe count. Legacy conversion maps old wire layout fields to the modern layout and treats an all-zero legacy layout as no pool by setting `pool_id = -1`.

Open flags are translated into Ceph file modes, including directory pin and lazy I/O where supported. File modes are then expanded into required Ceph caps for read, write, buffer, cache, auth, xattr, and lazy I/O access.

## Integration Points
Used by mount/open/layout code and capability acquisition paths to normalize layout metadata and requested access.

## Risks And Review Focus
- Layout validation protects OSD striping assumptions; relaxing alignment/multiplicity checks would affect object mapping.
- Mode-to-cap mapping determines how much authority the client requests from MDS.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/xattr.c

## Purpose
Implements CephFS extended attribute get/list/set handling, cached xattr blob parsing/rebuilding, virtual `ceph.*` xattrs, security-label initialization, and VFS xattr handler registration.

## Main Interfaces
- Generic xattrs: `__ceph_getxattr()`, `__ceph_setxattr()`, `ceph_listxattr()`.
- Blob/cache helpers: `__ceph_build_xattrs_blob()`, `__ceph_destroy_xattrs()`.
- Virtual xattr dispatch: internal `ceph_match_vxattr()` and vxattr callback tables.
- Security helpers: `ceph_security_xattr_wanted()`, `ceph_security_xattr_deadlock()`, `ceph_security_init_secctx()`.
- Context cleanup: `ceph_release_acl_sec_ctx()`.
- VFS handler table: `ceph_xattr_handlers`.

## Control Flow
Regular xattrs are cached as an MDS-provided encoded blob until first use. `__build_xattrs()` decodes that blob into an rb-tree of `ceph_inode_xattr` entries under `i_ceph_lock`, allocating outside the spinlock and retrying if the xattr version changes. `__ceph_getxattr()` fetches `CEPH_CAP_XATTR_SHARED` from the MDS when the cache is missing or unauthorized, then looks up the rb-tree entry. `ceph_listxattr()` similarly ensures xattr caps and copies null-terminated names.

`__ceph_setxattr()` uses a fast local update when the inode has exclusive xattr caps, the xattr blob is known, and the rebuilt blob would not exceed the MDS max xattr size. It preallocates name/value/index storage, cap-flush state, and a buffer for the rebuilt blob, then marks xattr caps dirty. Otherwise it sends synchronous `SETXATTR` or `RMXATTR` requests to the MDS.

Virtual xattrs expose layout, directory stats, recursive stats, quota, snapshot birth time, caps, auth MDS, cluster FSID, client ID, and fscrypt auth. Some are readonly or hidden; some force getattr masks such as `CEPH_STAT_RSTAT` or `CEPH_CAP_FILE_SHARED`.

## State And Synchronization
`ci->i_xattrs` contains the blob, preallocated blob, rb-tree index, dirty flag, counts, sizes, and version numbers, protected by `i_ceph_lock`. Snap interactions may require taking `mdsc->snap_rwsem` before dirtying xattrs so cap-snap boundaries are respected. OSD map pool-name lookups use `osdc->lock`.

## Integration Points
The file integrates with MDS getattr/setxattr requests, caps dirtying/flushing, security modules, POSIX ACL/security creation context pagelists, fscrypt auth xattrs, quota snaprealm validation, and VFS xattr handlers.

## Risks And Review Focus
- Local xattr mutation must recompute blob size after rebuilding because races can replace the blob while the spinlock is dropped.
- Security xattr access during trace filling returns `-EBUSY` to avoid deadlock.
- Virtual xattr existence/read-only flags must match MDS semantics, especially quota and fscrypt fields.
- Synchronous fallback is required when caps or size limits do not permit local mutation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/char_dev.c -->
# File Research: sources/os/linux/linux-stable/fs/char_dev.c

## Purpose
Implements Linux character-device major/minor registration, dynamic major allocation, cdev lifetime management, dev_t-to-cdev lookup, and default character special file open dispatch.

## Main Interfaces
- Region registration: `register_chrdev_region()`, `alloc_chrdev_region()`, `unregister_chrdev_region()`.
- Legacy combined registration: `__register_chrdev()`, `__unregister_chrdev()`.
- cdev lifecycle: `cdev_alloc()`, `cdev_init()`, `cdev_add()`, `cdev_del()`, `cdev_put()`.
- cdev/device helpers: `cdev_set_parent()`, `cdev_device_add()`, `cdev_device_del()`.
- Open dispatch: `def_chr_fops`, internal `chrdev_open()`.
- Initialization/proc: `chrdev_init()`, `chrdev_show()` under procfs.

## Control Flow
Major/minor reservations are tracked in a hash table of `char_device_struct` ranges protected by `chrdevs_lock`. `__register_chrdev_region()` validates major and minor bounds, finds a dynamic major if requested, checks for overlapping reserved ranges, and inserts the new range in sorted order. Multi-major public APIs split large `dev_t` ranges at major boundaries and roll back partial registration on failure.

`cdev_add()` maps a `dev_t` range into `cdev_map` with exact match/lock callbacks and takes a parent kobject reference. Opening a character special file starts at `def_chr_fops.open`; `chrdev_open()` resolves `inode->i_rdev` through `cdev_map`, attaches the resolved cdev to the inode, takes module/kobject refs, replaces the file operations with the device’s real fops, and calls the device open method.

Removal unmaps the cdev range and drops kobject refs. Release handlers purge inode back-pointers from the cdev list before freeing dynamic cdev storage or releasing parent refs.

## State And Synchronization
`chrdevs_lock` protects reservation tables and module autoload map initialization. `cdev_lock` protects inode-to-cdev attachment and cdev inode lists. `cdev_get()` combines `try_module_get()` with `kobject_get_unless_zero()` to prevent opens racing with removal.

## Integration Points
Exports the standard cdev API for drivers and backs VFS open of character device inodes. It also integrates with sysfs device lifetimes through `cdev_device_add()` and `cdev_set_parent()`.

## Risks And Review Focus
- Open/remove races depend on correct module and kobject reference ordering.
- Region overlap checks must remain exact across major boundaries and dynamic major allocation.
- `cdev_device_add()` notes that userspace may open the cdev even if later `device_add()` fails.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/char_dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/coda/Kconfig

## Purpose
Defines the `CODA_FS` kernel configuration option for the Coda network filesystem client.

## Main Contents
- `config CODA_FS`
- Type: `tristate`
- Prompt: `Coda file system support (advanced network fs)`
- Dependency: `INET`
- Help text describing Coda as a network filesystem client with disconnected operation, replication, authentication/encryption model, persistent caches, and write-back caching.

## Integration Points
Controls whether the Coda client is built into the kernel, built as the `coda` module, or omitted.

## Risks And Review Focus
- The Kconfig option only enables kernel client support; userspace Venus/client components remain required.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/coda/Makefile

## Purpose
Defines the object composition for the Linux Coda filesystem module.

## Main Contents
- Builds `coda.o` when `CONFIG_CODA_FS` is enabled.
- Core objects: `psdev.o`, `cache.o`, `cnode.o`, `inode.o`, `dir.o`, `file.o`, `upcall.o`, `coda_linux.o`, `symlink.o`, `pioctl.o`.
- Adds `sysctl.o` when `CONFIG_SYSCTL` is enabled.
- Contains a commented debug `ccflags-y` line.

## Integration Points
Connects Coda source files into one module or built-in object selected by Kconfig.

## Risks And Review Focus
- Object order is conventional for the module; adding features requires including new objects under the right config guards.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/cache.c -->
# File Research: sources/os/linux/linux-stable/fs/coda/cache.c

## Purpose
Implements Coda permission caching and dentry/inode invalidation helpers used after Venus downcalls or cache events.

## Main Interfaces
- Permission cache: `coda_cache_enter()`, `coda_cache_clear_inode()`, `coda_cache_clear_all()`, `coda_cache_check()`.
- Child invalidation: `coda_flag_inode_children()`.

## Control Flow
Permission cache entries are stored per inode in `coda_inode_info` as fsuid, permission mask, and global epoch. `coda_cache_enter()` records or extends permissions for the current fsuid. `coda_cache_check()` hits only when the requested mask is included, fsuid matches, and the inode epoch equals the global `permission_epoch`. `coda_cache_clear_all()` invalidates every cached permission by incrementing the global epoch.

For dentry invalidation, `coda_flag_inode_children()` finds an alias dentry for a directory inode, flags all positive child inodes with the requested Coda flag, shrinks the dcache subtree, and drops the alias.

## State And Synchronization
`permission_epoch` is atomic. Per-inode permission fields and flags are protected by `cii->c_lock`. Child dentry walking uses dentry lock plus RCU read-side protection.

## Integration Points
Used by permission checks in `dir.c`, inode revalidation, and Venus downcall handling to purge or refresh stale kernel-side Coda state.

## Risks And Review Focus
- Permission cache is fsuid-specific; changing credential semantics must preserve this.
- Child flagging intentionally does not handle negative dentries beyond dcache shrinking.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/cnode.c -->
# File Research: sources/os/linux/linux-stable/fs/coda/cnode.c

## Purpose
Implements Coda inode creation, lookup by Coda FID, inode operation selection, FID replacement, and control inode creation.

## Main Interfaces
- Inode creation/lookup: `coda_iget()`, `coda_cnode_make()`, `coda_fid_to_inode()`.
- FID management: `coda_replace_fid()`.
- File private access: `coda_ftoc()`.
- Control inode: `coda_cnode_makectl()`.

## Control Flow
`coda_cnode_make()` asks Venus for attributes with `venus_getattr()` and then calls `coda_iget()`. `coda_iget()` uses `iget5_locked()` with a hash derived from the FID, sets `i_ino`, initializes `coda_inode_info`, and calls `coda_fill_inode()` for new inodes. If an existing inode’s type no longer matches Venus attributes, it removes the inode from the hash, flags it for purge, drops it, and retries.

`coda_fill_inode()` translates Coda attributes to VFS inode attributes and installs file, directory, symlink, or special inode operations. Symlinks use page symlink operations and `coda_symlink_aops`.

`coda_replace_fid()` handles the special disconnected-create case where a local FID is replaced by a globally unique one by removing and reinserting the inode hash with the new FID-derived inode number.

## State And Synchronization
Inode identity is stored in `coda_inode_info.c_fid` and is normally immutable. The FID replacement path notes a lock concern in comments, making it a sensitive area.

## Integration Points
Used by directory lookup/create/mkdir and by downcall paths that need to map a Venus FID back to a VFS inode.

## Risks And Review Focus
- FID collisions and replacement can confuse inode hashing and in-flight upcalls.
- Type changes from Venus force inode purge/retry, which can affect dentries holding old type assumptions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/cnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/coda_cache.h -->
# File Research: sources/os/linux/linux-stable/fs/coda/coda_cache.h

## Purpose
Declares Coda minicache APIs for permission caching and invalidation.

## Main Contents
- Permission cache prototypes:
  - `coda_cache_enter()`
  - `coda_cache_clear_inode()`
  - `coda_cache_clear_all()`
  - `coda_cache_check()`
- Child invalidation prototype:
  - `coda_flag_inode_children()`

## Integration Points
Included by Coda directory, cache, and downcall code that checks permissions or marks cached inode/dentry state stale.

## Risks And Review Focus
- Minimal header; changes should stay aligned with `cache.c` and `dir.c` permission/invalidation callers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/coda_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/coda_fs_i.h -->
# File Research: sources/os/linux/linux-stable/fs/coda/coda_fs_i.h

## Purpose
Defines Coda per-inode and per-file private kernel data structures plus cnode helper prototypes.

## Main Contents
- `struct coda_inode_info`: Coda FID, flags, mmap count, cached permission epoch/fsuid/mask, spinlock, and embedded VFS inode.
- `struct coda_file_info`: magic value, Venus/container file pointer, mmap count, and access-intent support flag.
- Inode flags: `C_VATTR`, `C_FLUSH`, `C_DYING`, `C_PURGE`.
- Prototypes for cnode creation, lookup, control inode creation, FID replacement, and file-private access.

## Integration Points
Included by `coda_linux.h` and implementation files. It is the core state contract for directory, file, cache, inode, and psdev/upcall code.

## Risks And Review Focus
- `c_fid` is documented as immutable except for the special replacement path.
- `c_lock` protects flags, map count, and permission cache fields; callers must follow that boundary.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/coda_fs_i.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/coda_int.h -->
# File Research: sources/os/linux/linux-stable/fs/coda/coda_int.h

## Purpose
Declares internal Coda module globals and lifecycle helpers shared across implementation files.

## Main Contents
- External module/global declarations: `coda_fs_type`, `coda_timeout`, `coda_hard`, `coda_fake_statfs`.
- Inode cache lifecycle: `coda_init_inodecache()`, `coda_destroy_inodecache()`.
- `coda_fsync()` prototype.
- Sysctl lifecycle wrappers: real prototypes under `CONFIG_SYSCTL`, no-op inlines otherwise.

## Integration Points
Used by Coda module initialization, sysctl support, and file/dir operation code.

## Risks And Review Focus
- Header is intentionally small; global behavior changes should remain coordinated with module init and sysctl code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/coda_int.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/coda_linux.c -->
# File Research: sources/os/linux/linux-stable/fs/coda/coda_linux.c

## Purpose
Provides Linux-specific Coda helper conversions for FIDs, open flags, inode types, and attribute translation between Coda/Venus and VFS structures.

## Main Interfaces
- Debug/name helpers: `coda_f2s()`, `coda_iscontrol()`.
- Open flag conversion: `coda_flags_to_cflags()`.
- Attribute conversion: `coda_inode_type()`, `coda_vattr_to_iattr()`, `coda_iattr_to_vattr()`.

## Control Flow
`coda_flags_to_cflags()` maps Linux `O_ACCMODE`, `O_TRUNC`, `O_CREAT`, and `O_EXCL` into Coda open flags sent to Venus. `coda_vattr_to_iattr()` applies Coda attributes to a VFS inode when fields are not set to sentinel `-1`, including mode/type, uid/gid, nlink, size, block count, and timestamps. `coda_iattr_to_vattr()` initializes every Coda attribute field to an ignored sentinel, then fills only fields marked valid by Linux `ia_valid`.

## Integration Points
Used throughout Coda lookup/create/setattr/open code when crossing the kernel/Venus protocol boundary.

## Risks And Review Focus
- Attribute sentinel handling is central to avoiding unintended metadata changes.
- UID/GID conversion uses `init_user_ns`, so idmapped mount semantics are not represented here.
- `coda_f2s()` uses a static buffer and is suitable only for transient debug formatting.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/coda_linux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/coda_linux.h -->
# File Research: sources/os/linux/linux-stable/fs/coda/coda_linux.h

## Purpose
Declares Linux-side Coda VFS operations, common helper APIs, and inline accessors from VFS inodes to Coda private state.

## Main Contents
- Extern operation tables for directories, files, ioctl/control, dentries, address spaces, and symlinks.
- Shared operation prototypes: open, release, permission, inode revalidation, getattr, setattr.
- Helper prototypes from `coda_linux.c`.
- Inline accessors: `ITOC()`, `coda_i2f()`, `coda_i2s()`.
- Inline `coda_flag_inode()` to set Coda inode flags under `c_lock`.

## Integration Points
Included by most Coda implementation files. It bridges VFS operation tables with Coda-specific FID and inode-private data.

## Risks And Review Focus
- `coda_flag_inode()` does not drop inode references or purge immediately; later revalidation/delete paths interpret the flags.
- Header exposes many operation tables, so signature changes must track VFS API changes consistently.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/coda_linux.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/coda_psdev.h -->
# File Research: sources/os/linux/linux-stable/fs/coda/coda_psdev.h

## Purpose
Defines the Coda pseudo-device communication structures and Venus upcall/downcall API declarations.

## Main Contents
- Device constants: `CODA_PSDEV_MAJOR`, `MAX_CODADEVS`.
- `struct upc_req`: queued request data, flags, sizes, opcode, unique ID, and waitqueue.
- Request flags: async, read, write, abort.
- `struct venus_comm`: sequence number, Venus waitqueue, pending/processing lists, in-use flag, superblock pointer, and mutex.
- `coda_vcp()` helper to access `venus_comm` from a superblock.
- Prototypes for all Venus operations used by VFS paths: rootfid, getattr/setattr, lookup, open/close, create/mkdir/remove/rmdir/rename/link/symlink, readlink, access, pioctl, fsync, statfs, access intents, and downcalls.
- Extern `coda_comms[]`.

## Integration Points
Shared by Coda psdev/upcall implementation and VFS operation files. It defines the kernel-to-Venus RPC boundary.

## Risks And Review Focus
- Request size fields note a small maximum; upcall encoding/decoding must enforce bounds.
- Queue ownership and abort semantics depend on `venus_comm` locking and waitqueue discipline in implementation files.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/coda_psdev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/coda/dir.c

## Purpose
Implements Coda directory inode operations, permission checks, dentry revalidation/deletion, directory reading, and inode revalidation.

## Main Interfaces
- VFS directory operations: `coda_lookup()`, `coda_create()`, `coda_mkdir()`, `coda_link()`, `coda_symlink()`, `coda_unlink()`, `coda_rmdir()`, `coda_rename()`.
- Permission/revalidation: `coda_permission()`, `coda_revalidate_inode()`.
- Directory reading: `coda_readdir()`, internal `coda_venus_readdir()`.
- Operation tables: `coda_dentry_operations`, `coda_dir_inode_operations`, `coda_dir_operations`.

## Control Flow
Lookup rejects overlong names, synthesizes the root `.CONTROL` inode locally, or calls `venus_lookup()` and creates a cnode from the returned FID. Entries marked `CODA_NOCACHE` are flagged with `C_VATTR | C_PURGE`.

Permission checks do not support RCU mode, validate execute permission locally, consult the Coda permission cache, and call `venus_access()` on cache miss. Successful access is cached per fsuid/mask.

Create, mkdir, link, symlink, unlink, rmdir, and rename are thin VFS wrappers around Venus upcalls. They update parent mtimes, instantiate or drop dentries, and adjust link counts optimistically where possible. Control object creation at the root is forbidden.

Directory iteration first tries `iterate_dir()` on the Venus-provided container file. If that returns `-ENOTDIR`, it reads Venus-format `venus_dirent` records manually, validates record lengths, skips `.`/`..`, maps Coda d_types to Linux `DT_*`, and emits entries.

Dentry revalidation interprets `C_PURGE` and `C_FLUSH` flags, shrinks child dentries, propagates flush to children, and unhashed stale dentries when their count allows it. Inode revalidation refetches attributes from Venus when flags require it and clears stale flags.

## State And Synchronization
Coda inode flags are protected by `c_lock`. Dentry validity is coordinated through Coda flags plus VFS dentry counts. Directory mtime/link count updates are optimistic unless configured to requery Venus.

## Integration Points
Depends heavily on Venus upcalls declared in `coda_psdev.h`, cnode creation from `cnode.c`, permission cache from `cache.c`, and attribute conversion from `coda_linux.c`.

## Risks And Review Focus
- Venus directory file parsing must reject short or malformed records.
- Rename/link count updates are optimistic and must tolerate Venus-specific volume mount behavior.
- Dentry revalidation returns valid for busy stale dentries, leaving flags for later cleanup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/file.c -->
# File Research: sources/os/linux/linux-stable/fs/coda/file.c

## Purpose
Implements Coda regular-file operations by forwarding I/O and mmap to Venus-provided container files while notifying Venus of access intents and close/fsync events.

## Main Interfaces
- File I/O: `coda_file_read_iter()`, `coda_file_write_iter()`, `coda_file_splice_read()`.
- mmap handling: `coda_file_mmap()`, `coda_vm_open()`, `coda_vm_close()`.
- File lifecycle: `coda_open()`, `coda_release()`, `coda_fsync()`.
- Operation table: `coda_file_operations`.

## Control Flow
`coda_open()` allocates `coda_file_info`, converts Linux flags to Coda flags, calls `venus_open()` to obtain the underlying container file, propagates append/sync flags, and stores the container in `file->private_data`.

Read, write, and splice paths call `venus_access_intent()` before and after forwarding to the container file. Writes serialize on the Coda inode, forward through `vfs_iter_write()`, copy size/block metadata from the host inode, and update Coda inode mtime/ctime.

`coda_file_mmap()` verifies the container can be mmapped, sends a Venus mmap access intent, switches the Coda file and inode mapping to the host mapping under `c_lock`, tracks mapping counts, then invokes `vfs_mmap()` on the host file. It wraps host vm operations so Coda can hold a reference to the original Coda file until the final VMA close.

`coda_release()` sends `venus_close()`, unwinds mmap mapping counts, restores the Coda inode mapping when no mappings remain, drops the container file, and frees private data. `coda_fsync()` writes back the Coda mapping, fsyncs the container file, and sends `venus_fsync()` for full syncs.

## State And Synchronization
`struct coda_file_info` tracks the host file, mmap count, and whether Venus supports access intents. `struct coda_vm_ops` wraps host vm ops with refcounting. `c_lock` protects inode/file mmap counters and mapping substitution.

## Integration Points
Bridges VFS file operations to Venus cache/container files, access-intent upcalls, fsync upcalls, and Coda inode metadata.

## Risks And Review Focus
- Mapping substitution between Coda inode mapping and host inode mapping is delicate and returns `-EBUSY` if the container changes under active mappings.
- Access-intent finish calls run even after failed start operations; Venus-side support flags must tolerate that protocol.
- Release return values are ignored by VFS, so close errors cannot be surfaced through `release()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/coda/file.c -->