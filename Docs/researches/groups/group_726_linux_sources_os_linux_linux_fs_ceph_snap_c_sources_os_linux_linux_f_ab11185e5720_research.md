# Group Research: group_726_linux_sources_os_linux_linux_fs_ceph_snap_c_sources_os_linux_linux_f_ab11185e5720

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A. Each listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/snap.c -->
# File Research: sources/os/linux/linux/fs/ceph/snap.c

CephFS snapshot realm management and cap-snapshot coordination. This file maintains the client-side hierarchy of `ceph_snap_realm` objects, builds per-realm `ceph_snap_context` arrays, handles MDS snapshot notifications, queues inode cap snapshots when contexts change, and manages snapid-to-anonymous-block-device mappings.

Key responsibilities:
- Reference and lifetime management for snap realms via `ceph_get_snap_realm()`, `ceph_put_snap_realm()`, `__destroy_snap_realm()`, and empty-realm cleanup.
- Realm lookup/creation in `mdsc->snap_realms`, keyed by realm inode number.
- Parent/child realm topology updates through `adjust_snap_realm_parent()`.
- Snap context construction in `build_snap_context()`, merging parent snaps newer than `parent_since`, realm-local snaps, and prior-parent snaps, then reverse-sorting snap IDs.
- Downward rebuild traversal in `rebuild_snap_realms()` after realm topology or snap-set changes.
- MDS snap trace decode/apply in `ceph_update_snap_trace()`.
- Creation/finalization/flush queuing of `ceph_cap_snap` records for inodes with dirty caps or dirty/writeback data.
- Snap message handling in `ceph_handle_snap()`, including split-realm migration of inodes and child realms.
- Snapid map allocation, LRU trimming, and cleanup for snapshot device mapping.

Important data/control flow:
- MDS supplies snap traces; the client decodes each encoded `ceph_mds_snap_realm`, updates realm sequence/snaps/parent fields, rebuilds contexts, and queues cap snapshots for dirty realms.
- For a new snapshot, `queue_realm_cap_snaps()` walks all inodes with caps in the affected realm and calls `ceph_queue_cap_snap()`.
- `ceph_queue_cap_snap()` captures inode metadata, xattr blob/version, issued/dirty cap bits, and dirty-page counts under the inode’s previous snap context.
- `__ceph_finish_cap_snap()` records final size/timestamps/version/truncate state and adds the inode to `mdsc->snap_flush_list` once dirty data is gone.
- `flush_snaps()` drains `mdsc->snap_flush_list` by calling `ceph_flush_snaps()`.

Concurrency/lifetime notes:
- Realm topology operations require `mdsc->snap_rwsem`, with write locking for mutation.
- Realm inode lists use `realm->inodes_with_caps_lock`.
- Snap flush queue uses `mdsc->snap_flush_lock`.
- Empty realm destruction uses `snap_empty_lock` around 0-ref transitions to avoid races between re-acquire and deferred cleanup.
- Split handling uses inode `i_ceph_lock` while moving an inode between realms.
- Snapid maps use `snapid_map_lock`, refcounts, rb-tree lookup, and LRU timeout (`CEPH_SNAPID_MAP_TIMEOUT`).

Failure handling:
- Allocation failures during context build clear stale cached contexts and leave rebuild to later.
- Corrupt snap traces fence client I/O via `CEPH_MOUNT_FENCE_IO`, try to blocklist the client, and warn that remount is required.
- `ceph_handle_snap()` closes sessions when `ceph_update_snap_trace()` fails.

Notable observation:
- `ceph_update_snap_trace()` accepts a `deletion` parameter and comments mention avoiding cap-snap queuing on delete, but this file’s visible implementation does not branch on that parameter.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/snap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/strings.c -->
# File Research: sources/os/linux/linux/fs/ceph/strings.c

Small stringification helper file for CephFS debug/log output.

Exports constant string mappings for:
- MDS states: `ceph_mds_state_name()`
- Session operations: `ceph_session_op_name()`
- MDS operations: `ceph_mds_op_name()`
- Capability operations: `ceph_cap_op_name()`
- Lease operations: `ceph_lease_op_name()`
- Snapshot operations: `ceph_snap_op_name()`

Behavior:
- Each helper switches on protocol enum/constant values and returns a stable lowercase string.
- Unknown values return `"???"`.
- Used by trace/debug paths rather than core protocol mutation.

Notable detail:
- `CEPH_MDS_OP_SETLAYOUT` maps to `"setlayou"` in this source, missing the final `t`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/strings.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/subvolume_metrics.c -->
# File Research: sources/os/linux/linux/fs/ceph/subvolume_metrics.c

Implements per-subvolume CephFS I/O metrics tracking. Metrics are stored in an rb-tree keyed by subvolume ID and can be snapshotted, consumed, dumped through debugfs, and recorded from timed read/write operations.

Key structures:
- Internal `ceph_subvol_metric_rb_entry`: rb-node plus read/write operation counts, byte counts, and cumulative latencies.
- Global `ceph_subvol_metric_entry_cachep`: kmem cache for rb entries.
- Public tracker fields are defined in `subvolume_metrics.h`.

Main APIs:
- `ceph_subvolume_metrics_init()`: initializes spinlock, cached rb root, enabled flag, and atomic counters.
- `ceph_subvolume_metrics_destroy()`: clears all entries and disables collection.
- `ceph_subvolume_metrics_enable()`: toggles collection; disabling clears the rb-tree.
- `ceph_subvolume_metrics_record()`: records one read/write sample for a subvolume.
- `ceph_subvolume_metrics_snapshot()`: returns an allocated array of active entries, optionally consuming/resetting tree state.
- `ceph_subvolume_metrics_free_snapshot()`: frees snapshot arrays.
- `ceph_subvolume_metrics_dump()`: prints current entries and average latencies to a seq_file.
- `ceph_subvolume_metrics_record_io()`: wrapper that extracts inode subvolume ID and computes elapsed microseconds.
- `ceph_subvolume_metrics_cache_init()` / `_destroy()`: kmem cache lifecycle.

Concurrency:
- Tree and `nr_entries` are protected by `tracker->lock`.
- Debug/accounting counters use `atomic64_t`.
- `record()` uses a two-pass allocation pattern: check under lock, allocate outside lock, then retry/insert, freeing raced allocations if another thread inserted first.

Filtering:
- Recording skips disabled tracker, subvolume ID 0 (`CEPH_SUBVOLUME_ID_NONE`), zero size, or zero latency.
- `record_io()` increments counters for calls, disabled state, and missing subvolume IDs.
- Negative/zero measured latency is coerced to 1 microsecond before record.

Snapshot behavior:
- Counts active entries first, allocates an array, then copies under lock.
- With `consume=true`, entries are erased and freed after copy.
- Entries with no activity are pruned.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/subvolume_metrics.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/subvolume_metrics.h -->
# File Research: sources/os/linux/linux/fs/ceph/subvolume_metrics.h

Public interface for CephFS per-subvolume metrics.

Defines:
- `struct ceph_subvol_metric_snapshot`: point-in-time counters for a subvolume: ID, read/write ops, read/write bytes, cumulative read/write latency.
- `struct ceph_subvolume_metrics_tracker`: spinlock, cached rb-tree root, entry count, enabled flag, debug counters, and cumulative total read/write counters.

Declared APIs:
- Tracker lifecycle: `ceph_subvolume_metrics_init()`, `_destroy()`, `_enable()`.
- Recording: `ceph_subvolume_metrics_record()` and inode/MDS-aware `ceph_subvolume_metrics_record_io()`.
- Snapshotting: `ceph_subvolume_metrics_snapshot()` and `_free_snapshot()`.
- Debug output: `ceph_subvolume_metrics_dump()`.
- Slab lifecycle: `ceph_subvolume_metrics_cache_init()` and `_destroy()`.

Inline helper:
- `ceph_subvolume_metrics_enabled()` uses `READ_ONCE(tracker->enabled)` for lockless enabled checks.

Role in subsystem:
- Included by Ceph super/client setup and metrics paths.
- Uses forward declarations for `seq_file`, `ceph_mds_client`, and `ceph_inode_info` to avoid broad header coupling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/subvolume_metrics.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/super.c -->
# File Research: sources/os/linux/linux/fs/ceph/super.c

CephFS filesystem registration, mount option parsing, superblock setup, client lifecycle, module cache lifecycle, forced unmount/reconnect, and global module parameters.

Major areas:
- Superblock operations: `ceph_put_super()`, `ceph_statfs()`, `ceph_sync_fs()`, `ceph_umount_begin()`.
- Mount option parsing: `ceph_mount_parameters`, source parsing for old and new syntax, monitor address parsing, and per-option validation.
- Mount option comparison/display: `compare_mount_options()` and `ceph_show_options()`.
- Client lifecycle: `create_fs_client()`, `destroy_fs_client()`, workqueue creation/destruction, global `ceph_fsc_list`.
- Slab/mempool setup: inode, cap, cap-snap, cap-flush, dentry, file, dir-file, MDS request, writeback pagevec pool, and subvolume metrics cache.
- Mount flow: `ceph_get_tree()`, `ceph_set_super()`, `ceph_compare_super()`, `ceph_setup_bdi()`, `ceph_real_mount()`, `open_root_dentry()`.
- Remount/reconfigure: `ceph_reconfigure_fc()`.
- Shutdown coordination: stopping blockers for MDS/OSD paths and `ceph_kill_sb()`.
- Module registration: `init_ceph()`, `exit_ceph()`, `ceph_fs_type`.

Mount parsing:
- Supports old source syntax `<mon>[,<mon>...]:[/path]`.
- Supports new syntax `name@fsid.fsname=/path` plus `mon_addr=`.
- Canonicalizes repeated/trailing slashes in server path.
- Validates size options against page size and Ceph max message limits.
- Handles feature-gated options for fscache, POSIX ACLs, and test dummy encryption.
- Default options include dcache, no copy-from, and async directory ops.

Mount/superblock sharing:
- New fs client is created before `sget_fc()`.
- Existing superblock can be reused only if client/mount options, fsid, sb flags, blocklist state, and mount state are compatible.
- `CEPH_OPT_NOSHARE` disables sharing.

Unmount behavior:
- `ceph_kill_sb()` pre-unmounts MDS client, flushes workqueues, syncs filesystem, waits for dirty folios, advances MDS stopping state, waits for blockers, kills anonymous superblock, cleans debugfs/fscache, then destroys fs client.
- Forced unmount aborts OSD requests, forces MDS unmount, and bumps `filp_gen`.

Module parameters:
- `disable_send_metrics`: custom setter wakes all mounted clients when metrics sending is re-enabled.
- `mount_syntax_v1` and `mount_syntax_v2`: read-only support indicators.
- `enable_unsafe_idmap`: allows idmapped mounts without required MDS feature support.

Dependencies:
- Heavy integration with libceph, MDS client, OSD client, debugfs, fscrypt, fscache, VFS fs_context API, and tracepoints.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/super.h -->
# File Research: sources/os/linux/linux/fs/ceph/super.h

Primary internal CephFS header. It defines mount options, filesystem client state, inode-private state, capability structures, snap realm structures, inline helpers, and cross-file function declarations.

Key definitions:
- Mount option bits including clean recovery, dirstat/rbytes, async readdir, dcache, ino32, fscache, pool permissions, quota statfs behavior, copy-from, async dirops, nopagecache, and sparse read.
- Defaults for block/statfs size, read/write size, readahead, readdir limits, snapdir name, and cap-wanted delays.
- `struct ceph_mount_options`: parsed CephFS mount settings and string options.
- `struct ceph_fs_client`: superblock link, mount options, libceph client, MDS client, workqueues, writeback/congestion state, async unlink conflict table, debugfs dentries, fscache volume, fscrypt dummy policy.
- Capability types: `struct ceph_cap`, `struct ceph_cap_flush`, `struct ceph_cap_snap`.
- Inode support types: directory fragments, xattrs, dentry info, xattr cache info, netfs request data.
- `struct ceph_inode_info`: the central inode-private object containing vino, layout, dir stats, quota state, subvolume ID, frag tree, xattrs, caps, dirty/flushing lists, snap state, truncate/max-size state, cap refs, unsafe ops, work item, and optional fscrypt state.
- Readdir/file private state: `ceph_file_info`, `ceph_dir_file_info`, `ceph_rw_context`, `ceph_readdir_cache_control`.
- `struct ceph_snap_realm`: snapshot realm topology and cached context.

Inline helpers:
- Type conversion/accessors: `ceph_inode()`, `ceph_sb_to_fs_client()`, `ceph_inode_to_client()`, `ceph_vino()`, `ceph_ino()`, `ceph_snap()`.
- User-visible inode number conversion with `ino32`.
- Reserved inode filtering for MDS-private ranges.
- Directory completeness/order counters with memory barriers.
- Capability query wrappers and dirty-cap helper.
- RW context add/remove/find helpers.
- Default congestion calculation based on RAM, capped at 256 MiB.
- Pending cap-snap test.
- Inode shutdown test using inode flag or mount state.
- Quota state checks and update helper.
- Sparse-read extent-count helper for encrypted files.

Declared subsystem API surface:
- Super/mount: `ceph_force_reconnect()`, `ceph_umount_begin()`.
- Snap: realm lookup/refcount/update/handle, cap-snap finish, snapid map lifecycle.
- Inode/trace/readdir/fill/attrs.
- Xattr and security context helpers.
- ACL helpers, with stubs when ACL disabled.
- Capability management.
- File, dir, ioctl, export, lock, debugfs, and quota APIs.
- Stopping blocker APIs for MDS and OSD request paths.

Notable local addition:
- `CEPH_SUBVOLUME_ID_NONE` and `i_subvolume_id` are defined in `ceph_inode_info` for per-subvolume metrics; unknown/unset is represented as 0.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/super.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/util.c -->
# File Research: sources/os/linux/linux/fs/ceph/util.c

Small non-inline Ceph utility helpers.

Functions:
- `ceph_file_layout_is_valid()`: validates stripe unit, stripe count, and object size constraints.
- `ceph_file_layout_from_legacy()`: decodes legacy little-endian layout fields into `ceph_file_layout`, treating all-zero legacy layout as pool `-1`.
- `ceph_file_layout_to_legacy()`: encodes current layout into legacy structure, writing pool 0 for negative pool IDs.
- `ceph_flags_to_mode()`: converts open flags into Ceph file modes, with special handling for `O_DIRECTORY` as pin mode and optional `O_LAZY`.
- `ceph_caps_for_mode()`: maps Ceph file mode bits to required capability bits.

Important behavior:
- Layout validation enforces nonzero stripe unit/object size, 64 KiB alignment, object size multiple of stripe unit, and nonzero stripe count.
- Write mode implies file write/buffer caps plus auth and xattr shared/exclusive caps.
- Lazy mode adds `CEPH_CAP_FILE_LAZYIO`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/xattr.c -->
# File Research: sources/os/linux/linux/fs/ceph/xattr.c

CephFS xattr implementation, including virtual `ceph.*` attributes, cached real xattrs, local dirty xattr mutation under caps, synchronous MDS xattr operations, and security-label initialization.

Major areas:
- Valid xattr prefix filtering for `security.`, `ceph.`, `trusted.`, and `user.`.
- Virtual xattrs for layouts, directory stats, recursive stats, dir pin, quotas, snap birth time, cluster fsid, client ID, caps, auth MDS, and fscrypt auth.
- Per-inode xattr rb-tree management: set/get/remove/copy/destroy.
- Lazy decode of MDS-provided xattr blob into rb-tree.
- Re-encoding dirty xattrs into preallocated Ceph buffers.
- Get/list xattr paths with MDS getattr fallback.
- Set/remove xattr paths with local cap-backed update when possible, otherwise synchronous MDS request.
- Security label helpers and ACL/security context cleanup.

Virtual xattrs:
- Directory-only table includes `ceph.dir.layout`, layout fields, dir stat fields, recursive stat fields, `ceph.dir.pin`, `ceph.quota`, quota fields, `ceph.snap.btime`, and `ceph.caps`.
- File-only table includes `ceph.file.layout`, layout fields, `ceph.snap.btime`, and `ceph.caps`.
- Common table includes `ceph.cluster_fsid`, `ceph.client_id`, `ceph.auth_mds`, and optional `ceph.fscrypt.auth`.
- Flags distinguish read-only, hidden, recursive-stat, and dir-stat attributes.

Real xattr cache:
- `__build_xattrs()` decodes `ci->i_xattrs.blob` into `ci->i_xattrs.index` only when needed and rebuilds if version changes race during allocation.
- `__ceph_build_xattrs_blob()` re-encodes dirty rb-tree entries into `prealloc_blob`, swaps it into `blob`, clears dirty, and bumps version.
- `__set_xattr()` enforces create/replace semantics for local updates, updates size counters, tracks ownership of copied names/values, and marks entries dirty.

Get/list behavior:
- `__ceph_getxattr()` handles virtual `ceph.*` xattrs first; unrecognized `ceph.*` is passed to `ceph_do_getvxattr()`.
- Non-virtual xattrs require `CEPH_CAP_XATTR_SHARED`; otherwise it fetches xattrs from MDS.
- During trace fill (`current->journal_info`), synchronous fetch/set paths return `-EBUSY` to avoid deadlock.
- `ceph_listxattr()` ensures xattr caps, builds rb-tree, and returns/copies null-terminated name list.

Set behavior:
- Snapshot inodes reject mutation with `-EROFS`.
- Read-only virtual xattrs reject with `-EOPNOTSUPP`.
- Unknown `ceph.*` xattrs go synchronously to MDS.
- For ordinary xattrs, local mutation is used only when xattr version exists, XATTR_EXCL cap is issued, and required blob size fits `m_max_xattr_size`.
- Local mutation preallocates cap flush and xattr blob outside critical sections, marks XATTR_EXCL dirty caps, updates ctime, and marks inode dirty.
- Synchronous path builds MDS `SETXATTR` or `RMXATTR` request with optional pagelist payload.

Security integration:
- `ceph_security_xattr_wanted()` detects inode security state.
- `ceph_security_xattr_deadlock()` identifies cases where security xattr fetch would deadlock during inode initialization.
- `ceph_security_init_secctx()` encodes LSM security context into a pagelist for create requests when security labels are enabled.
- `ceph_release_acl_sec_ctx()` releases ACLs, LSM context, fscrypt auth, and pagelist.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/char_dev.c -->
# File Research: sources/os/linux/linux/fs/char_dev.c

Core Linux character device registration and dispatch implementation.

Major responsibilities:
- Maintains registered char device number ranges in `chrdevs[]`, protected by `chrdevs_lock`.
- Allocates static or dynamic major numbers.
- Registers/unregisters char device regions.
- Provides `__register_chrdev()` and `__unregister_chrdev()` convenience APIs that combine region reservation with `struct cdev` lifecycle.
- Maps device numbers to `struct cdev` through global `cdev_map`.
- Handles first open of character special files by replacing default fops with the registered cdev’s fops.
- Exports cdev APIs to modules.

Important functions:
- `find_dynamic_major()`: searches normal and extended dynamic major ranges.
- `__register_chrdev_region()`: validates major/minor range, checks overlap in sorted hash bucket, and inserts region.
- `register_chrdev_region()` / `alloc_chrdev_region()`: public region allocation APIs.
- `__register_chrdev()`: reserves region, allocates cdev, sets owner/ops/name, calls `cdev_add()`.
- `unregister_chrdev_region()` / `__unregister_chrdev()`: remove range and optional cdev.
- `chrdev_open()`: resolves inode `i_rdev` to cdev, pins module/kobject, installs fops, calls driver open.
- `cdev_add()`, `cdev_del()`, `cdev_alloc()`, `cdev_init()`, `cdev_set_parent()`.
- `cdev_device_add()` / `cdev_device_del()`: paired cdev/device registration helpers.
- `chrdev_init()`: initializes `cdev_map` with module autoload probe.

Concurrency/lifetime:
- `chrdevs_lock` protects major/minor range registry and module autoload map initialization.
- `cdev_lock` protects inode-to-cdev links and cdev inode lists.
- `cdev_get()` pins both owner module and kobject.
- `cdev_purge()` clears `i_cdev` links on cdev release.
- Opened cdev fops can remain callable after `cdev_del()`; comments explicitly warn callers.

Exports:
- Region APIs, cdev init/alloc/add/del/parent/device helpers, and legacy register/unregister helpers are exported.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/char_dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/Kconfig -->
# File Research: sources/os/linux/linux/fs/coda/Kconfig

Kconfig entry for the Coda filesystem client.

Defines:
- `CONFIG_CODA_FS`: tristate “Coda file system support (advanced network fs)”.
- Dependency: `INET`.

Help text:
- Describes Coda as a network filesystem similar to NFS.
- Highlights disconnected operation, read/write server replication, authentication/encryption security model, persistent client caches, and write-back caching.
- Clarifies the kernel option enables Linux to act as a Coda client.
- Points to `Documentation/filesystems/coda.rst` and the Coda homepage.
- Module name is `coda`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/Makefile -->
# File Research: sources/os/linux/linux/fs/coda/Makefile

Build rules for the Linux Coda filesystem module.

Behavior:
- Builds `coda.o` when `CONFIG_CODA_FS` is enabled.
- Core object list: `psdev.o`, `cache.o`, `cnode.o`, `inode.o`, `dir.o`, `file.o`, `upcall.o`, `coda_linux.o`, `symlink.o`, `pioctl.o`.
- Adds `sysctl.o` when `CONFIG_SYSCTL` is enabled.
- Contains commented debug `ccflags-y` line for enabling debug macros.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/cache.c -->
# File Research: sources/os/linux/linux/fs/coda/cache.c

Coda kernel minicache helpers for permission caching and dentry/inode invalidation.

Key behavior:
- Maintains a global `permission_epoch` atomic counter.
- `coda_cache_enter()` caches permission mask for current fsuid on an inode; same uid extends mask, different uid replaces mask.
- `coda_cache_clear_inode()` invalidates one inode’s cached permissions by setting stale epoch.
- `coda_cache_clear_all()` invalidates all inode permission caches by incrementing global epoch.
- `coda_cache_check()` validates requested mask, current fsuid, and epoch.
- `coda_flag_inode_children()` finds an alias dentry for a directory, flags child inodes, shrinks child dcache, and drops alias.

Concurrency:
- Per-inode `c_lock` protects cached permission fields.
- Child dentry traversal uses parent d_lock plus RCU read lock.
- Permission cache is intentionally simple: one uid/mask/epoch slot per inode.

Integration:
- Used by Coda permission checks and Venus downcall invalidation paths.
- Flags such as `C_PURGE`, `C_FLUSH`, and `C_VATTR` are consumed by dentry revalidation and inode revalidation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/cnode.c -->
# File Research: sources/os/linux/linux/fs/coda/cnode.c

Coda cnode/inode mapping helpers. This file maps Coda FIDs to Linux inodes, fills inode operations based on Coda vnode attributes, handles special control inode creation, and supports FID replacement.

Key functions:
- `coda_fideq()`: compares `struct CodaFid` objects byte-for-byte.
- `coda_fill_inode()`: applies Coda attributes and assigns inode/file operations for regular files, directories, symlinks, or special inodes.
- `coda_iget()`: obtains or creates an inode via `iget5_locked()` using Coda FID hash/test/set callbacks.
- `coda_cnode_make()`: fetches attributes from Venus, then calls `coda_iget()`.
- `coda_replace_fid()`: replaces an inode’s FID and rehashes it for disconnected-operation collision repair.
- `coda_fid_to_inode()`: looks up an existing inode by FID.
- `coda_ftoc()`: validates and returns Coda file private data.
- `coda_cnode_makectl()`: creates the special `.CONTROL` inode without Venus attributes.

Important behavior:
- `coda_iget()` retries if an existing inode has changed file type, removing it from hash and marking it purged.
- Symlink inodes use `page_get_link`, `coda_setattr`, no-highmem, and `coda_symlink_aops`.
- `coda_replace_fid()` contains a source comment noting locking is probably needed around in-place rehash.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/cnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/coda_cache.h -->
# File Research: sources/os/linux/linux/fs/coda/coda_cache.h

Header for Coda minicache operations.

Declares:
- Permission cache APIs: `coda_cache_enter()`, `coda_cache_clear_inode()`, `coda_cache_clear_all()`, `coda_cache_check()`.
- Child invalidation API: `coda_flag_inode_children()`.

Role:
- Shared by Coda directory/cache/upcall paths that need permission caching or invalidation after Venus downcalls.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/coda_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/coda_fs_i.h -->
# File Research: sources/os/linux/linux/fs/coda/coda_fs_i.h

Coda inode-private and file-private structure definitions.

Defines:
- `struct coda_inode_info`: Coda FID, flags, mmap count, cached permission epoch/fsuid/mask, spinlock, and embedded VFS inode.
- `CODA_MAGIC`: magic value for file private data validation.
- `struct coda_file_info`: magic, host/container file, mmap count, and access-intent support flag.
- Inode flags: `C_VATTR`, `C_FLUSH`, `C_DYING`, `C_PURGE`.

Declared helpers:
- `coda_cnode_make()`
- `coda_iget()`
- `coda_cnode_makectl()`
- `coda_fid_to_inode()`
- `coda_ftoc()`
- `coda_replace_fid()`

Concurrency contract:
- Header comment states `c_lock` protects flags, map count, permission epoch, cached uid, and cached permission mask.
- `vfs_inode` is set only at creation.
- `c_fid` is intended immutable except for the documented replacement special case.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/coda_fs_i.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/coda_int.h -->
# File Research: sources/os/linux/linux/fs/coda/coda_int.h

Internal Coda declarations shared across module files.

Declares:
- Filesystem type: `coda_fs_type`.
- Tunables/globals: `coda_timeout`, `coda_hard`, `coda_fake_statfs`.
- Inode cache lifecycle: `coda_init_inodecache()`, `coda_destroy_inodecache()`.
- Shared fsync: `coda_fsync()`.

Sysctl integration:
- When `CONFIG_SYSCTL` is enabled, declares `coda_sysctl_init()` and `coda_sysctl_clean()`.
- Otherwise provides empty inline stubs.

Role:
- Keeps module-global declarations out of broader public Coda headers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/coda_int.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/coda_linux.c -->
# File Research: sources/os/linux/linux/fs/coda/coda_linux.c

Linux/Coda translation helpers for FIDs, control names, open flags, inode attributes, and Coda vattrs.

Key functions:
- `coda_f2s()`: formats a Coda FID into a static string buffer.
- `coda_iscontrol()`: detects the special `.CONTROL` name.
- `coda_flags_to_cflags()`: maps Linux open flags to Coda open flags.
- `coda_inode_type()`: maps Coda vnode type to Linux inode file type.
- `coda_vattr_to_iattr()`: applies Coda attributes to Linux inode fields.
- `coda_iattr_to_vattr()`: initializes a Coda vattr with sentinel values, then maps Linux `iattr` fields marked valid.

Attribute behavior:
- Coda sentinel `-1` means “not provided / do not modify”.
- Size updates also set `i_blocks` as `(size + 511) >> 9`.
- Time conversion uses helpers between `coda_timespec` and `timespec64`.
- UID/GID conversion uses `init_user_ns`.

Other:
- Global `coda_fake_statfs` is defined here.
- `coda_f2s()` uses a static buffer, so it is not reentrant.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/coda_linux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/coda_linux.h -->
# File Research: sources/os/linux/linux/fs/coda/coda_linux.h

Main Linux-side internal Coda header.

Contains:
- `pr_fmt` setup for module-prefixed logging.
- Includes for kernel memory, wait, VFS, and `coda_fs_i.h`.
- Extern declarations for inode/file/dentry/address-space operations.
- Shared operation declarations: open, release, permission, revalidate, getattr, setattr.
- Helper declarations from `coda_linux.c`: FID formatting, control-name detection, inode/vattr conversion, flag conversion.

Inline helpers:
- `ITOC()`: VFS inode to `struct coda_inode_info`.
- `coda_i2f()`: inode to Coda FID.
- `coda_i2s()`: inode to formatted FID string.
- `coda_flag_inode()`: sets Coda inode flags under `c_lock`, ignoring null inode.

Role:
- Central include for Coda implementation files needing Linux/VFS glue and Coda-private state access.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/coda_linux.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/coda_psdev.h -->
# File Research: sources/os/linux/linux/fs/coda/coda_psdev.h

Coda pseudo-device and Venus upcall interface header.

Defines:
- `CODA_PSDEV_MAJOR` as 67.
- `MAX_CODADEVS` as 5.
- `struct upc_req`: one kernel-to-Venus request with list linkage, data pointer, flags, input/output sizes, opcode, unique ID, and waitqueue.
- Request flags: async, read, write, abort.
- `struct venus_comm`: per-communication-channel sequence, Venus waitqueue, pending/processing lists, in-use flag, superblock pointer, and mutex.
- `coda_vcp()`: superblock to `venus_comm`.

Declares Venus operations:
- Root FID, getattr/setattr, lookup, open/close, mkdir/create/rmdir/remove, readlink, rename, link/symlink, access, pioctl, fsync, statfs, access intent.
- `coda_downcall()` for Venus-to-kernel invalidation/results.
- Global `coda_comms[]`.

Role:
- Defines the internal kernel/userspace protocol surface between Coda VFS code and Venus cache manager.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/coda_psdev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/dir.c -->
# File Research: sources/os/linux/linux/fs/coda/dir.c

Coda directory inode/file/dentry operations. This file forwards namespace operations to Venus, maintains local VFS dentry/inode state, supports fallback Venus directory entry format, and handles Coda invalidation flags.

Directory operations:
- `coda_lookup()`: validates name length, creates `.CONTROL` inode at root, otherwise calls `venus_lookup()` and instantiates result.
- `coda_permission()`: non-RCU permission check with execute bit validation, minicache lookup, Venus access upcall, and cache insert on success.
- `coda_create()`, `coda_mkdir()`, `coda_link()`, `coda_symlink()`: forward creation/link operations to Venus and update local inode/dentry/link/mtime state.
- `coda_unlink()`, `coda_rmdir()`: forward removals to Venus and update local link counts/mtime.
- `coda_rename()`: rejects nonzero flags, calls Venus rename, updates link counts for directory replacement and flags overwritten inode attributes stale.
- `.mknod` is wired to an EIO-returning stub.

Directory read:
- `coda_readdir()` first tries `iterate_dir()` on the host/container file.
- If that returns `-ENOTDIR`, `coda_venus_readdir()` reads Venus-format `struct venus_dirent` records from the container file.
- Fallback parser emits dots, validates short/truncated records, skips `.` and `..`, maps Coda d_type to Linux `DT_*`, and advances by `d_reclen`.

Dentry/inode invalidation:
- `coda_dentry_revalidate()` rejects RCU walk, checks `C_PURGE`/`C_FLUSH`, shrinks child dcache, propagates flush flags, and invalidates unused dentries.
- `coda_dentry_delete()` asks VFS to drop dentries whose inode has `C_PURGE`.
- `coda_revalidate_inode()` refetches attributes when Coda flags indicate stale/purge/flush, warns on type changes, rejects inode-number changes, propagates child flush, and clears flags.

Registered ops:
- `coda_dentry_operations`
- `coda_dir_inode_operations`
- `coda_dir_operations`

Notable behavior:
- `.CONTROL` cannot be created/linked as a normal root entry.
- Directory link count helpers deliberately avoid changing ambiguous low link counts used by Coda/Venus tricks for volume mount points.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/coda/file.c -->
# File Research: sources/os/linux/linux/fs/coda/file.c

Coda regular file operations. This file proxies file I/O to a Venus-provided host/container file while preserving Coda access-intent notifications, mmap mapping redirection, open/release, and fsync behavior.

Main data:
- `struct coda_vm_ops`: wrapper around host VMA ops with refcount, owning Coda file, host ops pointer, and copied vm ops.

Read/write/splice:
- `coda_file_read_iter()` sends Venus read access-intent begin, performs `vfs_iter_read()` on container file, then sends finish intent.
- `coda_file_write_iter()` sends write intent, writes to container file under Coda inode lock, mirrors host size/blocks to Coda inode, updates ctime/mtime, then sends finish intent.
- `coda_file_splice_read()` wraps `vfs_splice_read()` with read access-intent begin/finish.

mmap:
- `coda_file_mmap()` checks host file mmap capability, sends mmap access intent, allocates `coda_vm_ops`, switches Coda file/inode mapping to host mapping, increments inode/file map counts, calls `vfs_mmap()` on host file, then wraps VMA open/close callbacks.
- `coda_vm_open()` increments wrapper refcount and delegates to host open.
- `coda_vm_close()` delegates to host close, restores vm ops on final close, drops Coda file ref, and frees wrapper.
- Prevents new mmap if inode mapping already points at a different host mapping.

Open/release:
- `coda_open()` allocates `coda_file_info`, converts flags, calls `venus_open()` to get container file, propagates append/sync flags, initializes private data and access-intent support.
- `coda_release()` calls `venus_close()`, adjusts mmap counts/mapping, drops host file, frees private data, and returns 0 because VFS ignores release errors.

fsync:
- `coda_fsync()` waits writeback on Coda mapping, locks inode, calls `vfs_fsync()` on host file, then `venus_fsync()` when not datasync.

Registered ops:
- `coda_file_operations`: llseek, read_iter, write_iter, mmap, open, release, fsync, splice_read.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/coda/file.c -->