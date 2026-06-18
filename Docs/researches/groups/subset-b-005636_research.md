# subset-b-005636 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/snap.c -->
# sources/distributed-fs/ceph-client/fs/ceph/snap.c

## Purpose
`snap.c` implements CephFS client snapshot realm tracking, snap context rebuilding, cap-snap queuing, snap notification handling from MDS sessions, and snap-id-to-anonymous-block-device mapping for snapped inodes. It is the client-side consistency layer that decides which writes belong before or after a snapshot.

## Important APIs, Types, And Functions
Public entry points include `ceph_lookup_snap_realm()`, `ceph_get_snap_realm()`, `ceph_put_snap_realm()`, `ceph_update_snap_trace()`, `ceph_change_snap_realm()`, `ceph_handle_snap()`, `__ceph_finish_cap_snap()`, `ceph_get_snapid_map()`, `ceph_put_snapid_map()`, `ceph_trim_snapid_map()`, and `ceph_cleanup_snapid_map()`. The main state types are `struct ceph_snap_realm`, `struct ceph_cap_snap`, `struct ceph_snap_context`, and `struct ceph_snapid_map`.

## Control Flow
MDS snap messages enter through `ceph_handle_snap()`, which decodes the header, handles split operations by moving inodes and child realms, then calls `ceph_update_snap_trace()` under `mdsc->snap_rwsem`. Snap trace decoding creates or looks up realms, adjusts parents, updates sequence and snap arrays, rebuilds cached contexts from parent to child, then queues cap snaps for dirty realms. `flush_snaps()` later drains `mdsc->snap_flush_list` through `ceph_flush_snaps()`. Snapid maps are looked up in an rb-tree, allocated with `get_anon_bdev()` on misses, and retired through an LRU after timeout.

## State, Persistence, And Dependencies
State is in-memory kernel state protected by `snap_rwsem`, `snap_empty_lock`, per-realm inode locks, `snap_flush_lock`, and `snapid_map_lock`. Nothing is persisted locally; authoritative snapshot state comes from MDS snap traces and is propagated to OSD writes through snap contexts. Dependencies include Ceph MDS client sessions, caps, xattr blob building, OSD snap contexts, rb-trees, lists, atomics, and blocklist support.

## Integration Points
This file integrates with cap management (`ceph_flush_snaps`, dirty caps), inode realm membership, MDS message dispatch, quota/xattr metadata snapshots, mount shutdown cleanup, and snapped inode device presentation.

## Risks
The highest-risk areas are refcount/list transitions for empty realms, memory-allocation failures during context rebuilds, split races across MDSs, corrupted snap traces, and cap-snap sequencing while writes or writeback are active. Corrupted traces deliberately fence IO and try to blocklist the client.

## Test Signals
Exercise snapshot create/delete/split, rename across snap realms, dirty write snapshot boundaries, mmap/page writeback snapshots, MDS failover during snap updates, ENOMEM fault injection, malformed snap traces, unmount cleanup, and snapid-map LRU trimming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/snap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/strings.c -->
# sources/distributed-fs/ceph-client/fs/ceph/strings.c

## Purpose
`strings.c` centralizes human-readable names for CephFS MDS states, session operations, metadata operations, cap operations, lease operations, and snap operations.

## Important APIs, Types, And Functions
It exports string helpers `ceph_mds_state_name()`, `ceph_session_op_name()`, `ceph_mds_op_name()`, `ceph_cap_op_name()`, `ceph_lease_op_name()`, and `ceph_snap_op_name()`. The inputs are protocol enum/int values from Ceph headers.

## Control Flow
Each function is a switch over known protocol constants and returns a stable string literal. Unknown values return `"???"`, which keeps debug paths total even when protocol values are not recognized by the client.

## State, Persistence, And Dependencies
The file has no mutable state and no persistence. It depends on `linux/ceph/types.h` for protocol constants and is used by logging/debugging paths across the client.

## Integration Points
Snapshot handling, MDS session handling, cap handling, and request logging call these helpers to make trace/debug output intelligible without duplicating string tables.

## Risks
The main risk is drift when protocol enums gain new values but this file is not updated, producing `"???"` in diagnostics. There is no runtime safety risk beyond observability loss.

## Test Signals
Compile coverage catches missing constants. Logging or small unit-style assertions can verify every supported enum maps to the expected string and unknown values map to `"???"`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/strings.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/subvolume_metrics.c -->
# sources/distributed-fs/ceph-client/fs/ceph/subvolume_metrics.c

## Purpose
`subvolume_metrics.c` tracks per-subvolume CephFS read/write operation counts, byte counts, and aggregate latency, then exposes snapshots for metric transmission or debugfs dumping.

## Important APIs, Types, And Functions
The private rb-tree node is `struct ceph_subvol_metric_rb_entry`. Public APIs include `ceph_subvolume_metrics_init()`, `destroy()`, `enable()`, `record()`, `snapshot()`, `free_snapshot()`, `dump()`, `record_io()`, and cache init/destroy helpers. The slab cache is `ceph_subvol_metric_entry_cachep`.

## Control Flow
Record paths first reject disabled trackers, unknown subvolume IDs, zero bytes, or zero latency. On a miss, allocation happens outside the spinlock and insertion is retried to handle races. Snapshot first counts active entries, allocates an output array, copies active metrics under lock, and optionally consumes entries by zeroing/removing them. Debug dump formats live rb-tree entries directly.

## State, Persistence, And Dependencies
State lives in `struct ceph_subvolume_metrics_tracker`: a cached rb-tree, entry count, enabled flag, spinlock, and atomic debug counters. It is volatile and reset when disabled or destroyed. Dependencies include rb-tree APIs, slab allocation, `ktime`, `seq_file`, and Ceph inode subvolume IDs.

## Integration Points
`record_io()` is called from data IO paths with a `ceph_mds_client` and `ceph_inode_info`; snapshots are consumed by MDS metric reporting, and dump output appears in debugfs through CephFS debug plumbing. Cache init/destroy is wired through Ceph module cache setup.

## Risks
Potential risks include high-cardinality subvolume IDs growing the rb-tree, allocation failure dropping metrics, snapshot count races causing partial results, and lock hold time during debug `seq_printf()`. Metrics are best-effort and should not affect IO correctness.

## Test Signals
Test disabled/enabled transitions, concurrent records for the same/new IDs, consume and non-consume snapshots, zero/unknown filtering, allocation-failure paths, debugfs formatting, and cache teardown after active entries are cleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/subvolume_metrics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/subvolume_metrics.h -->
# sources/distributed-fs/ceph-client/fs/ceph/subvolume_metrics.h

## Purpose
`subvolume_metrics.h` declares the CephFS per-subvolume metrics interface and the tracker/snapshot data structures used by IO paths, MDS metric reporting, and debugfs.

## Important APIs, Types, And Functions
It defines `struct ceph_subvol_metric_snapshot` with per-subvolume read/write counters and latency sums, and `struct ceph_subvolume_metrics_tracker` with lock, rb-tree, enable flag, and debug/cumulative atomics. It declares init, destroy, enable, record, snapshot, free, dump, record-IO, and slab-cache lifecycle functions plus inline `ceph_subvolume_metrics_enabled()`.

## Control Flow
The header itself has only the inline enabled check via `READ_ONCE()`. Callers initialize a tracker, enable collection when supported, record IO events, periodically snapshot/free arrays, and destroy the tracker during MDS client teardown.

## State, Persistence, And Dependencies
All state is in the tracker embedded elsewhere, not global to the header. It depends on Linux types, rb-tree, spinlock, ktime, atomics, `seq_file`, and forward declarations for Ceph MDS/inode types.

## Integration Points
The tracker is embedded in `struct ceph_mds_client` and used by data IO instrumentation, metric scheduling, and debugfs dumps. Cache lifecycle hooks are called from Ceph module initialization and exit.

## Risks
Callers must respect the lock ownership encoded by the implementation and must not inspect rb-tree internals without the lock. `enabled` is readable locklessly, so implementation paths must recheck it under lock before mutating state.

## Test Signals
Compile coverage across configurations, sparse/lockdep checks, and integration tests that enable/disable metrics and verify snapshot contents are enough to validate the public contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/subvolume_metrics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/super.c -->
# sources/distributed-fs/ceph-client/fs/ceph/super.c

## Purpose
`super.c` implements CephFS filesystem registration, mount option parsing, superblock setup/sharing, client creation/destruction, module cache lifecycle, statfs/sync behavior, forced unmount/reconnect, remount handling, and module parameters.

## Important APIs, Types, And Functions
Key functions include `ceph_init_fs_context()`, `ceph_parse_mount_param()`, `ceph_get_tree()`, `ceph_set_super()`, `ceph_compare_super()`, `ceph_real_mount()`, `ceph_kill_sb()`, `ceph_umount_begin()`, `ceph_force_reconnect()`, `init_ceph()`, and `exit_ceph()`. It defines super operations, fs context operations, `ceph_fs_type`, global kmem caches, and the `disable_send_metrics`/mount syntax/idmap module parameters.

## Control Flow
Mount starts with fs-context allocation and option parsing, including old and new source syntaxes. `ceph_get_tree()` creates a `ceph_fs_client`, initializes the MDS client, finds or creates a shared superblock, sets up BDI parameters, opens a cluster session, registers fscache/debugfs, and opens the root dentry. Unmount pre-flushes MDS state, syncs filesystems, waits for dirty folios and stopping blockers, kills the anon super, unregisters fscache/debugfs, and destroys the client.

## State, Persistence, And Dependencies
The file owns process-wide CephFS cache objects and a list of clients used to wake metric reporting when module parameters change. Per-mount state lives in `struct ceph_fs_client` and `struct ceph_mount_options`. Persistent storage is remote Ceph cluster state; local state is kernel memory and superblock structures.

## Integration Points
It ties VFS fs_context/super_operations, libceph monitor/osd clients, MDS client, fscache, fscrypt, debugfs, quota statfs, xattrs, export ops, and workqueues together. `extra_mon_dispatch()` routes MDSMAP/FSMAP messages to the MDS client.

## Risks
Risks include option compatibility between old/new mount syntax, superblock sharing with subtly different options, teardown ordering around dirty folios and MDS blockers, mount failure cleanup, blocklisted-client recovery, and module parameter changes racing with live clients.

## Test Signals
Test old/new mount sources, remountable options, no-MDS cluster behavior, shared versus `noshare` mounts, fscache/fscrypt configs, statfs with quotas and noquotadf, forced unmount, blocklist clean recovery, module load/unload, and fault injection in cache/client setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/super.h -->
# sources/distributed-fs/ceph-client/fs/ceph/super.h

## Purpose
`super.h` is the central CephFS client contract header. It defines mount options, per-mount client state, inode/cap/xattr/snap data structures, inline helpers, constants, and cross-file function declarations.

## Important APIs, Types, And Functions
Major types include `struct ceph_mount_options`, `struct ceph_fs_client`, `struct ceph_cap`, `struct ceph_cap_flush`, `struct ceph_cap_snap`, `struct ceph_inode_xattr`, `struct ceph_inode_xattrs_info`, `struct ceph_inode_info`, `struct ceph_file_info`, `struct ceph_dir_file_info`, `struct ceph_rw_context`, and `struct ceph_snap_realm`. Inline helpers cover option tests, inode/client conversions, vino presentation, inode lookup, cap checks, dir completeness, workqueue scheduling, quota updates, and shutdown checks.

## Control Flow
The header establishes how implementation files coordinate: superblock code constructs `ceph_fs_client`; inode/file/dir/xattr/cap/snap code mutates fields in `ceph_inode_info`; snap code uses `ceph_snap_realm`; and workqueue helpers schedule asynchronous inode actions by setting work bits.

## State, Persistence, And Dependencies
All declarations describe in-kernel state. Persistent authoritative state remains on MDS/OSD servers. Dependencies span VFS, netfs, fscache, fscrypt, libceph, exportfs, mempools, atomics, waitqueues, rb-trees, and Ceph protocol headers.

## Integration Points
This header is included by most CephFS client source files and is the glue for VFS operations, MDS requests, OSD data IO, snapshots, quotas, caps, ACL/security labels, fscrypt, debugfs, and export support.

## Risks
Because it is shared, field lifetime and lock rules are critical. `i_ceph_lock`, session mutexes, snap semaphores, and dirty/flushing lists must be used consistently. Structure changes can silently affect slab sizes, cache initialization, on-stack assumptions, or cross-file invariants.

## Test Signals
Build all CephFS config combinations, run sparse/lockdep/KCSAN, exercise mount/open/read/write/xattr/snapshot/quota/readdir paths, and use fault injection around cap flushes, snap contexts, and workqueue shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/super.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/util.c -->
# sources/distributed-fs/ceph-client/fs/ceph/util.c

## Purpose
`util.c` provides non-inline CephFS helper functions for file layout validation/conversion and mapping Linux open flags or Ceph file modes to required capability bits.

## Important APIs, Types, And Functions
It implements `ceph_file_layout_is_valid()`, `ceph_file_layout_from_legacy()`, `ceph_file_layout_to_legacy()`, `ceph_flags_to_mode()`, and `ceph_caps_for_mode()`. The relevant data structures are `struct ceph_file_layout` and `struct ceph_file_layout_legacy`.

## Control Flow
Layout validation checks nonzero stripe unit/object size, minimum stripe-unit alignment, object-size multiple of stripe unit, and nonzero stripe count. Legacy conversion translates little-endian fields and treats all-zero legacy layout as no pool (`pool_id = -1`). Flag/mode conversion maps VFS access modes to `CEPH_FILE_MODE_*` and then to cap masks.

## State, Persistence, And Dependencies
There is no mutable state. The helpers depend on Linux open flag constants and Ceph protocol/layout definitions.

## Integration Points
Mount, inode fill, layout xattrs, file open, and cap acquisition paths use these helpers to validate layouts and request the correct MDS capabilities for read, write, lazy IO, or directory pins.

## Risks
Incorrect cap mapping can over-request or under-request MDS caps, affecting cache coherency or write permissions. Layout validation must stay aligned with MDS/OSD layout constraints and legacy encoding semantics.

## Test Signals
Test valid and invalid stripe layouts, all-zero legacy layouts, endian conversion, read/write/read-write/directory/lazy open flag mappings, and cap masks consumed by open/write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/xattr.c -->
# sources/distributed-fs/ceph-client/fs/ceph/xattr.c

## Purpose
`xattr.c` implements CephFS extended attribute handling, including virtual `ceph.*` attributes, cached xattr rb-tree construction from MDS blobs, local dirty updates under xattr caps, synchronous MDS xattr updates, xattr listing, and security-label initialization support.

## Important APIs, Types, And Functions
Important functions include `__ceph_getxattr()`, `ceph_listxattr()`, `__ceph_setxattr()`, `ceph_sync_setxattr()`, `__ceph_build_xattrs_blob()`, `__ceph_destroy_xattrs()`, `ceph_security_xattr_wanted()`, `ceph_security_xattr_deadlock()`, `ceph_security_init_secctx()`, and `ceph_release_acl_sec_ctx()`. Virtual xattrs are described by `struct ceph_vxattr` tables for directories, files, and common attributes.

## Control Flow
Getxattr first checks for virtual `ceph.*` names and refreshes stats/caps as needed, otherwise it ensures shared xattr caps or fetches xattrs from the MDS, builds the rb-tree from the encoded blob, and copies the value. Setxattr rejects snapshots, handles read-only virtual attributes, chooses synchronous MDS updates for `ceph.*`, missing caps, or oversized blobs, and otherwise preallocates memory/blob/cap flush state, updates the rb-tree, marks xattr caps dirty, and later encodes a blob for cap flush.

## State, Persistence, And Dependencies
Per-inode xattr state is `ci->i_xattrs`: encoded blob, preallocated blob, rb-tree, dirty flag, counts, sizes, and versions protected by `i_ceph_lock`. Persistent xattr state is authoritative on the MDS; local dirty state is flushed through caps.

## Integration Points
The file integrates with MDS getattr/setxattr requests, cap dirty tracking, snap cap snapshots, layout/pool metadata, quota realm checks, fscrypt auth, POSIX ACL/security label creation, LSM hooks, and VFS xattr handlers.

## Risks
Risks include lock dropping during xattr tree builds, stale blob/version races, max-xattr-size transitions, security xattr deadlocks while filling traces, memory ownership for blob/name/value allocations, and read-only virtual attribute semantics.

## Test Signals
Test virtual xattrs, user/trusted/security xattrs, listxattr sizing, local dirty update versus sync fallback, max size overflow, concurrent cap grants while building xattrs, quota xattr realm validation, fscrypt/security-label configs, and snapshot read-only behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/char_dev.c -->
# sources/distributed-fs/ceph-client/fs/char_dev.c

## Purpose
`char_dev.c` implements Linux character-device number registration, dynamic major allocation, `struct cdev` lifetime, char-device open dispatch, and helper APIs for binding cdevs to devices.

## Important APIs, Types, And Functions
External APIs include `register_chrdev_region()`, `alloc_chrdev_region()`, `unregister_chrdev_region()`, `__register_chrdev()`, `__unregister_chrdev()`, `cdev_alloc()`, `cdev_init()`, `cdev_add()`, `cdev_del()`, `cdev_set_parent()`, `cdev_device_add()`, `cdev_device_del()`, `cdev_put()`, and `chrdev_init()`. Internal state uses `struct char_device_struct`, the `chrdevs` hash, `cdev_map`, and `cdev_lock`.

## Control Flow
Registration reserves major/minor ranges in `chrdevs`; dynamic allocation scans legacy and extended dynamic ranges. `__register_chrdev()` additionally allocates a `cdev`, installs fops, and adds it to `cdev_map`. Opening a char special inode uses `def_chr_fops.open`, resolves the cdev through `kobj_lookup()`, pins its module/kobject, replaces file operations, and calls the driver open method. Deletion unmaps future opens while existing open files keep callable fops.

## State, Persistence, And Dependencies
State is kernel-global and volatile: reserved ranges, kobject map entries, cdev kobjects, inode `i_cdev` links, and module references. It depends on VFS, kobjects, module refcounts, mutex/spinlock locking, device core helpers, and procfs display hooks.

## Integration Points
Every char driver registration path uses these APIs. `cdev_device_add()` bridges cdev lifetime with `struct device`, while `base_probe()` supports module autoload aliases for char majors.

## Risks
Risks include overlapping range detection, major exhaustion, lifetime after `cdev_del()`, module refcount failure during open, parent kobject references, and callers assuming failed `cdev_device_add()` means userspace never opened the cdev.

## Test Signals
Test fixed/dynamic registration, multi-major ranges, overlap failures and unwind, open while deleting, module autoload, cdev-device parent lifetime, proc `/proc/devices` output, and KASAN/KCSAN around inode cdev links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/char_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/Kconfig -->
# sources/distributed-fs/ceph-client/fs/coda/Kconfig

## Purpose
`Kconfig` exposes the Coda filesystem client as `CONFIG_CODA_FS`, an advanced network filesystem option with disconnected operation, replication, authentication/security, persistent caches, and write-back caching.

## Important APIs, Types, And Functions
This is build configuration rather than C code. It defines a tristate symbol `CODA_FS` depending on `INET`, with help text documenting that the kernel component is only the Coda client and requires user-level Venus/server software.

## Control Flow
Kconfig selection determines whether the Coda client is built in, built as module `coda`, or omitted. The dependency prevents selection without networking support.

## State, Persistence, And Dependencies
It has no runtime state. Its main dependency is `INET`; runtime persistence is handled by user-space Coda/Venus caches, not this file.

## Integration Points
The symbol controls `fs/coda/Makefile`, module compilation, and availability of the Coda VFS and psdev interfaces.

## Risks
Misconfiguration can produce a kernel without Coda support or build the client without required user-space components. The help text points users to documentation and the Coda project.

## Test Signals
Validate `CONFIG_CODA_FS=y`, `m`, and unset builds, ensure `depends on INET` is respected, and confirm the module name and object list match Makefile behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/Makefile -->
# sources/distributed-fs/ceph-client/fs/coda/Makefile

## Purpose
The Coda `Makefile` declares how the kernel builds the Coda filesystem client module/object set.

## Important APIs, Types, And Functions
It builds `coda.o` when `CONFIG_CODA_FS` is enabled. Core objects are `psdev.o`, `cache.o`, `cnode.o`, `inode.o`, `dir.o`, `file.o`, `upcall.o`, `coda_linux.o`, `symlink.o`, and `pioctl.o`; `sysctl.o` is included when `CONFIG_SYSCTL` is enabled.

## Control Flow
Kbuild combines the listed objects into the built-in filesystem or loadable `coda` module depending on the tristate configuration. Optional debug `ccflags-y` are left commented out.

## State, Persistence, And Dependencies
There is no runtime state. Dependencies are Kbuild variables and the configuration symbols `CONFIG_CODA_FS` and `CONFIG_SYSCTL`.

## Integration Points
This file links the VFS operations, Venus upcall/downcall device, cache, inode, directory, file, symlink, pioctl, and sysctl pieces into one filesystem implementation.

## Risks
Missing an object breaks link-time symbols or runtime feature coverage. Optional sysctl compilation must stay aligned with declarations in `coda_int.h`.

## Test Signals
Build Coda as built-in and module with/without `CONFIG_SYSCTL`, run modpost/link checks, and verify exported module metadata comes from the compiled object set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/cache.c -->
# sources/distributed-fs/ceph-client/fs/coda/cache.c

## Purpose
`cache.c` implements Coda's small in-kernel permission cache and dentry/inode invalidation helpers used when Venus downcalls indicate cached state is stale.

## Important APIs, Types, And Functions
Public functions are `coda_cache_enter()`, `coda_cache_clear_inode()`, `coda_cache_clear_all()`, `coda_cache_check()`, and `coda_flag_inode_children()`. Global state is `permission_epoch`; per-inode state lives in `struct coda_inode_info` fields protected by `c_lock`.

## Control Flow
Permission checks store the current fsuid, granted mask, and epoch. Later checks hit only if the same fsuid has all requested mask bits and the epoch still matches. Clearing one inode sets a stale epoch; clearing all increments the global epoch. Child invalidation finds an alias dentry for a directory, flags child inodes, shrinks child dentries, and drops the alias.

## State, Persistence, And Dependencies
State is volatile kernel cache only. It depends on current credentials, dentry aliases, RCU dentry traversal, spinlocks, and VFS dcache shrinking.

## Integration Points
`dir.c` permission and revalidation use this cache; Venus downcalls and Coda invalidation paths use child flagging to propagate `C_PURGE`, `C_FLUSH`, or `C_VATTR` effects.

## Risks
Permission caching is fsuid-specific and mask-based; stale invalidation depends on epoch updates and child flag propagation. Dentry traversal must avoid unsafe negative dentry handling and respect locking/RCU rules.

## Test Signals
Test repeated permission hits/misses by uid/mask, global and per-inode invalidation, downcall purge/flush propagation, directory child dentry shrinking, and lockdep/RCU validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/cnode.c -->
# sources/distributed-fs/ceph-client/fs/coda/cnode.c

## Purpose
`cnode.c` maps Coda file identifiers to VFS inodes, fills inode operations based on Venus attributes, handles special control inode creation, and supports fid replacement for disconnected-create collision repair.

## Important APIs, Types, And Functions
Important functions are `coda_iget()`, `coda_cnode_make()`, `coda_replace_fid()`, `coda_fid_to_inode()`, `coda_ftoc()`, and `coda_cnode_makectl()`. Internal helpers include `coda_fideq()`, `coda_fill_inode()`, `coda_test_inode()`, and `coda_set_inode()`.

## Control Flow
`coda_cnode_make()` asks Venus for attributes, then calls `coda_iget()` using `iget5_locked()` keyed by `coda_f2i(fid)`. New inodes get `i_ino`, cnode state, and mode-specific inode/file operations. Existing inodes with changed type are removed from the hash, flagged for purge, dropped, and retried. The control inode is created locally without Venus attributes.

## State, Persistence, And Dependencies
Per-inode Coda state is `struct coda_inode_info`, especially immutable `c_fid`, flags, mapcount, and permission cache fields. Persistent identity belongs to Venus/Coda servers. Dependencies include VFS inode hash APIs, page symlink ops, Coda attribute conversion, and Venus getattr.

## Integration Points
Directory lookup/create paths call into this file to materialize inodes. File operations use `coda_ftoc()` to validate private data. Pioctl/control operations use the synthetic control inode.

## Risks
`coda_replace_fid()` explicitly notes missing locking around rehashing. Fid hash collisions, type changes, disconnected local fid replacement, and stale inode flags are core risk areas.

## Test Signals
Test lookup/create for regular files, directories, symlinks, special files, type-change replacement, fid-to-inode lookup, control inode lookup, disconnected fid replacement, and inode hash race detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/cnode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/coda_cache.h -->
# sources/distributed-fs/ceph-client/fs/coda/coda_cache.h

## Purpose
`coda_cache.h` declares Coda permission-cache and invalidation helper functions shared between directory, downcall, and attribute paths.

## Important APIs, Types, And Functions
It declares `coda_cache_enter()`, `coda_cache_clear_inode()`, `coda_cache_clear_all()`, `coda_cache_check()`, and `coda_flag_inode_children()`.

## Control Flow
The header has no executable flow. Callers use the cache APIs around Venus access checks and use child flagging when a directory subtree needs purge, flush, or attribute invalidation.

## State, Persistence, And Dependencies
State is implemented in `cache.c`; this header only exposes the contract. It depends on VFS `struct inode` and `struct super_block` declarations through included users.

## Integration Points
`dir.c` uses the permission cache in `coda_permission()` and invalidation helpers in dentry/inode revalidation. Venus downcall code uses these declarations to invalidate kernel cache state.

## Risks
The API does not encode locking in types, so callers must rely on implementation semantics. Misuse can leave stale permissions or dentries visible.

## Test Signals
Build coverage and permission/invalidation integration tests validate that declarations remain aligned with `cache.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/coda_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/coda_fs_i.h -->
# sources/distributed-fs/ceph-client/fs/coda/coda_fs_i.h

## Purpose
`coda_fs_i.h` defines Coda per-inode and per-file private structures and declares inode/fid helper functions.

## Important APIs, Types, And Functions
It defines `struct coda_inode_info` with fid, flags, mmap count, permission-cache fields, lock, and embedded VFS inode. It defines `struct coda_file_info` with magic, container file, mmap count, and access-intent support. It declares `coda_cnode_make()`, `coda_iget()`, `coda_cnode_makectl()`, `coda_fid_to_inode()`, `coda_ftoc()`, and `coda_replace_fid()`.

## Control Flow
The header is declarative. Runtime code allocates Coda inodes from the inode cache, uses `c_fid` as identity, stores container-file state in `file->private_data`, and tracks flags such as `C_VATTR`, `C_FLUSH`, `C_DYING`, and `C_PURGE`.

## State, Persistence, And Dependencies
State is volatile kernel-side representation of Venus/server identities and open files. It depends on Linux inode/list/spinlock types and UAPI Coda fid/attribute definitions.

## Integration Points
`cnode.c`, `file.c`, `dir.c`, inode cache code, and psdev/upcall paths all rely on these structures to bridge VFS objects to Coda identities and Venus-opened container files.

## Risks
The comment says `c_fid` should be immutable, with only special replacement support elsewhere. Lock coverage for `c_flags`, `c_mapcount`, and permission fields must be preserved to avoid stale cache or mmap mapping races.

## Test Signals
Compile layout users, exercise file open/release/mmap, permission caching, invalidation flags, fid lookup/replacement, and KASAN checks for `coda_file_info` lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/coda_fs_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/coda_int.h -->
# sources/distributed-fs/ceph-client/fs/coda/coda_int.h

## Purpose
`coda_int.h` provides internal Coda module declarations for filesystem registration, tunables, inode-cache lifecycle, fsync, and optional sysctl hooks.

## Important APIs, Types, And Functions
It declares `coda_fs_type`, `coda_timeout`, `coda_hard`, `coda_fake_statfs`, `coda_init_inodecache()`, `coda_destroy_inodecache()`, and `coda_fsync()`. It declares `coda_sysctl_init()`/`clean()` when `CONFIG_SYSCTL` is set and provides no-op inline stubs otherwise.

## Control Flow
There is no runtime flow in the header. It lets module init/exit and VFS operation files share internal symbols without exposing them outside Coda.

## State, Persistence, And Dependencies
The declared tunables influence Coda runtime behavior but are owned by other files. There is no persistence in this header.

## Integration Points
`psdev.c`/module init uses inode-cache and sysctl declarations; `dir.c` references `coda_fsync()` for directory file operations; sysctl compilation is isolated behind config guards.

## Risks
Optional sysctl stubs must match the real signatures. Global tunables need coherent definitions in exactly one object to avoid link or behavior drift.

## Test Signals
Build with and without `CONFIG_SYSCTL`, load/unload Coda, and verify sysctl registration plus directory/file fsync linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/coda_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/coda_linux.c -->
# sources/distributed-fs/ceph-client/fs/coda/coda_linux.c

## Purpose
`coda_linux.c` provides Linux-specific helper conversions for Coda: fid formatting, control-name recognition, open-flag translation, time conversion, inode type mapping, and VFS/Coda attribute translation.

## Important APIs, Types, And Functions
Public functions are `coda_f2s()`, `coda_iscontrol()`, `coda_flags_to_cflags()`, `coda_inode_type()`, `coda_vattr_to_iattr()`, and `coda_iattr_to_vattr()`. It also defines global `coda_fake_statfs`.

## Control Flow
Open flags are converted into Coda `C_O_*` flags. Venus `coda_vattr` values are copied into Linux inode fields only when not set to sentinel `-1`; Linux `iattr` valid bits are converted back into Coda attributes with unspecified fields initialized to sentinel values.

## State, Persistence, And Dependencies
The only global is the fake statfs flag. All conversion state is on-stack or in caller-provided inode/attribute structures. Dependencies include Linux credentials/user namespace conversions, VFS inode timestamps, and Coda UAPI attributes.

## Integration Points
`cnode.c` uses attribute-to-inode conversion during inode fill; setattr paths use inode-to-Coda conversion before Venus upcalls; file open/release maps Linux flags to Venus flags; directory lookup recognizes `.CONTROL`.

## Risks
`coda_f2s()` uses a static buffer and is not reentrant. UID/GID conversion assumes `init_user_ns`. Sentinel handling must stay aligned with Venus protocol expectations, especially for timestamps and sizes.

## Test Signals
Test all open flag combinations, `.CONTROL` matching, vattr sentinel handling, uid/gid/mode/size/time translation, static fid formatting in logs, and setattr round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/coda_linux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/coda_linux.h -->
# sources/distributed-fs/ceph-client/fs/coda/coda_linux.h

## Purpose
`coda_linux.h` is the main Linux-kernel-facing Coda header, declaring operation tables, shared VFS operation functions, helper conversions, cnode accessors, and inode flagging.

## Important APIs, Types, And Functions
It declares Coda inode, dentry, address-space, file, directory, and ioctl operations; shared functions such as `coda_open()`, `coda_release()`, `coda_permission()`, `coda_revalidate_inode()`, `coda_getattr()`, and `coda_setattr()`; helper functions from `coda_linux.c`; and inline accessors `ITOC()`, `coda_i2f()`, `coda_i2s()`, and `coda_flag_inode()`.

## Control Flow
The only executable logic is inline object conversion and flag setting. `coda_flag_inode()` locks the cnode and ORs an invalidation flag without dropping the inode.

## State, Persistence, And Dependencies
State is in `struct coda_inode_info` embedded in VFS inodes. The header depends on VFS, memory, wait, and Coda inode private definitions.

## Integration Points
Nearly every Coda source file includes this header to wire VFS methods to Coda/Venus helpers and to access per-inode fid/flag state.

## Risks
Inline accessors assume the inode really belongs to Coda. Misusing `coda_i2s()` inherits the static-buffer caveat of `coda_f2s()`. Flagging does not perform cache eviction by itself; revalidation paths must consume the flags.

## Test Signals
Build coverage, lockdep around `coda_flag_inode()`, and broad VFS operation tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/coda_linux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/coda_psdev.h -->
# sources/distributed-fs/ceph-client/fs/coda/coda_psdev.h

## Purpose
`coda_psdev.h` defines the kernel-to-Venus pseudo-device communication structures and declares all Venus upcall/downcall helpers used by the Coda VFS client.

## Important APIs, Types, And Functions
It defines `CODA_PSDEV_MAJOR`, `MAX_CODADEVS`, `struct upc_req`, request flags, and `struct venus_comm`. It declares `coda_vcp()`, all `venus_*` operations for rootfid/getattr/setattr/lookup/open/close/create/remove/rename/link/symlink/access/pioctl/fsync/statfs/access_intent, and `coda_downcall()`.

## Control Flow
The header itself only provides `coda_vcp()` to get `struct venus_comm` from `sb->s_fs_info`. Runtime upcall flow is implemented in psdev/upcall sources: VFS operations allocate requests, queue them to Venus, wait for userspace replies, and process downcalls.

## State, Persistence, And Dependencies
`venus_comm` tracks sequence numbers, waitqueue, pending and processing request lists, in-use state, associated superblock, and mutex. Request state is per-upcall in `struct upc_req`. Persistent Coda cache state lives in userspace Venus, not this header.

## Integration Points
All Coda VFS operation files call `venus_*` helpers. The psdev character device exposes queues to the Venus userspace cache manager.

## Risks
Queue lifetime, request abort handling, userspace daemon death, and size limits on upcall messages are key risks. `MAX_CODADEVS` fixes the number of concurrent device channels.

## Test Signals
Test Venus startup/shutdown, concurrent upcalls, interrupted waits, downcall invalidations, daemon death, mount per-device isolation, and every declared Venus operation through VFS workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/coda_psdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/dir.c -->
# sources/distributed-fs/ceph-client/fs/coda/dir.c

## Purpose
`dir.c` implements Coda directory VFS operations, permission checks, lookup/create/remove/rename/link/symlink/mkdir/rmdir operations, directory reading, and dentry/inode revalidation.

## Important APIs, Types, And Functions
Key functions include `coda_lookup()`, `coda_permission()`, `coda_create()`, `coda_mkdir()`, `coda_link()`, `coda_symlink()`, `coda_unlink()`, `coda_rmdir()`, `coda_rename()`, `coda_readdir()`, `coda_dentry_revalidate()`, `coda_dentry_delete()`, and `coda_revalidate_inode()`. It exports `coda_dentry_operations`, `coda_dir_inode_operations`, and `coda_dir_operations`.

## Control Flow
Directory mutations call corresponding Venus operations, then update local dentries, link counts, and directory mtime. Lookup handles the root `.CONTROL` pseudo-entry specially, otherwise asks Venus and materializes an inode. Permission checks use the kernel permission cache before `venus_access()`. Readdir first delegates to the container file's `iterate_dir()`; if that reports `-ENOTDIR`, it parses Venus directory records manually. Revalidation consumes Coda flags and refetches attributes from Venus.

## State, Persistence, And Dependencies
Directory state is split between local VFS dentries/inodes and authoritative Venus/server state. Coda invalidation flags (`C_VATTR`, `C_PURGE`, `C_FLUSH`) drive cache refresh. Dependencies include Venus upcalls, cnode creation, permission cache, dcache shrink/revalidation, and VFS link-count helpers.

## Integration Points
This is the main bridge from VFS directory operations to the Venus cache manager. It shares open/release/fsync with `file.c`, cnode materialization with `cnode.c`, and invalidation with `cache.c`.

## Risks
Risks include stale dentries after downcalls, manual Venus dirent parsing, link-count heuristics for volume mount points, unsupported rename flags, `.CONTROL` protection, and revalidation returning success for busy purged dentries until references drop.

## Test Signals
Test lookup, negative lookup, `.CONTROL`, create/mkdir/link/symlink/unlink/rmdir/rename, permission-cache hits and misses, readdir via host directory and Venus records, downcall purge/flush behavior, and RCU lookup fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/file.c -->
# sources/distributed-fs/ceph-client/fs/coda/file.c

## Purpose
`file.c` implements Coda regular-file operations by forwarding IO to a Venus-provided container file while notifying Venus of access intents, managing mmap redirection, and syncing local/container state.

## Important APIs, Types, And Functions
Important functions are `coda_file_read_iter()`, `coda_file_write_iter()`, `coda_file_splice_read()`, `coda_file_mmap()`, `coda_open()`, `coda_release()`, and `coda_fsync()`. `struct coda_vm_ops` wraps host vm operations with Coda lifetime tracking. The exported table is `coda_file_operations`.

## Control Flow
Open asks Venus for a container file and stores it in `struct coda_file_info`. Reads, writes, splice reads, and mmap send access-intent begin/finish upcalls when supported, then call VFS helpers on the container file. Writes update Coda inode size, blocks, mtime, and ctime from the host inode. Mmap swaps the VMA file to the host file, redirects open/close vm operations, and tracks cnode/file map counts. Release calls `venus_close()`, unwinds mmap mapping state, fputs the container, and frees private data. Fsync flushes local mapping, fsyncs the host file, then asks Venus to fsync for full-data sync.

## State, Persistence, And Dependencies
Open-file state is in `struct coda_file_info`; mmap state is split between inode/file map counts and allocated `struct coda_vm_ops`. Persistent file data is handled by the container file and Venus cache/server. Dependencies include VFS iter/splice/mmap/fsync helpers, Venus open/close/access_intent/fsync, and cnode locks.

## Integration Points
Directory operations reuse open/release/fsync for directories. Cnode state tracks mapping redirection, while psdev/upcall code implements the Venus side of file operations.

## Risks
Risks include access-intent begin/finish imbalance, mmap lifetime/refcount errors, mapping mismatch when Venus changes container files, write metadata drift, and ignored errors from `release()`.

## Test Signals
Test read/write/splice/mmap/fsync/open/release, unsupported access-intent fallback, mmap then release, concurrent mmaps with container changes, write size updates, daemon failures, and lock/refcount validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/coda/file.c -->
