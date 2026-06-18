# Group Research: group_877_linux_sources_os_linux_linux_fs_xfs_xfs_stats_c_sources_os_linux_lin_3d607ad3aab7

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`.

This grouped report covers XFS statistics, sysctl/sysfs exposure, superblock and module lifecycle, tracepoint instantiation, and symlink operations. Every source file listed in the work item was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_stats.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_stats.c

## Purpose

`xfs_stats.c` implements global and per-mount XFS statistics formatting, clearing, and legacy procfs compatibility endpoints. It is the implementation behind `/sys/fs/xfs/stats/stats`, per-mount stats sysfs files, and the older `/proc/fs/xfs/*` quota/stat paths when procfs is enabled.

## Main Interfaces

- `struct xstats xfsstats`: global XFS statistics object, with its per-CPU counter storage allocated during module init in `xfs_super.c`.
- `xfs_stats_format(struct xfsstats __percpu *stats, char *buf)`: emits the text statistics format expected by sysfs/procfs readers.
- `xfs_stats_clearall(struct xfsstats __percpu *stats)`: clears per-CPU statistics while preserving stateful inode counters.
- `xfs_init_procfs()` / `xfs_cleanup_procfs()`: create and remove `/proc/fs/xfs` compatibility entries under `CONFIG_PROC_FS`.
- `xqm_proc_show()` and `xqmstat_proc_show()`: legacy quota stat show callbacks under `CONFIG_XFS_QUOTA`.

## Implementation Notes

- `counter_val` sums a 32-bit counter index across all possible CPUs by treating each per-CPU `struct xfsstats` as a `uint32_t` array.
- `xfs_stats_format` uses a static table of stat group names and endpoint offsets. It prints grouped counters in the historic order: extent allocation, allocation btrees, block map, directories, transactions, inode grabs, log, AIL pushes, I/O, attributes, inode clustering, vnode-era counters, buffer cache, newer btree families, quota, zoned GC, and metafile counters.
- High precision counters are summed separately as 64-bit values: `xs_xstrat_bytes`, `xs_write_bytes`, `xs_read_bytes`, `xs_defer_relog`, and `xs_gc_bytes`.
- The `debug` line reports whether the kernel was built with `DEBUG`.
- `xfs_stats_clearall` preserves `xs_inodes_active` and `xs_inodes_meta`, because they represent current state rather than monotonic event counts.
- Procfs initialization creates `/proc/fs/xfs/stat` as a symlink to `/sys/fs/xfs/stats/stats`, then conditionally creates quota compatibility files.

## Dependencies and Callers

- Consumes layout definitions and macros from `xfs_stats.h`.
- Called by `xfs_sysfs.c` for sysfs stats reads and clears.
- Called by `xfs_sysctl.c` when the `stats_clear` sysctl is written.
- Global stats allocation, sysfs registration, and cleanup are orchestrated by `init_xfs_fs` and `exit_xfs_fs` in `xfs_super.c`.

## Research Notes

- The stats ABI is layout sensitive: group boundaries depend on field ordering in `struct __xfsstats`.
- Buffer length is bounded with `PATH_MAX - len`; callers must provide a buffer large enough for sysfs/procfs style output.
- Clearing is per-CPU and uses `preempt_disable` around each per-CPU update, but does not globally synchronize readers; readers can observe in-progress clears.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_stats.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_stats.h

## Purpose

`xfs_stats.h` defines the in-memory XFS statistics layout, btree stat offsets, per-CPU update macros, and procfs initialization stubs. It is the central contract between XFS subsystems that increment counters and the reporting code that formats them.

## Main Interfaces

- `enum __XBTS_*`: fixed offsets for per-btree operation counters such as lookup, compare, insert record, split, join, alloc, free, and moves.
- `struct __xfsstats`: concrete counter layout for all exported XFS statistics.
- `struct xfsstats`: union of structured fields and a 32-bit array used for offset-based counter access.
- `xfsstats_offset(f)` and `XFS_STATS_CALC_INDEX(member)`: convert field names to 32-bit counter indexes.
- `XFS_STATS_INC`, `XFS_STATS_DEC`, `XFS_STATS_ADD`: update named fields in both global and per-mount stats.
- `XFS_STATS_INC_OFF`, `XFS_STATS_DEC_OFF`, `XFS_STATS_ADD_OFF`: update counters by precomputed offset.
- `xfs_stats_format`, `xfs_stats_clearall`, `xfs_init_procfs`, `xfs_cleanup_procfs`: declarations or no-op stubs depending on config.

## Counter Families

- Allocation counters: extents and blocks allocated/freed.
- Btree counters: legacy allocation/bmap counters and version 2 arrays for `abtb`, `abtc`, `bmbt`, `ibt`, `fibt`, `rmap`, `refcnt`, memory btrees, realtime rmap/refcount, and rcbag.
- Mapping, directory, transaction, inode lookup/reclaim, log, AIL push, read/write, attribute, inode cluster, and buffer counters.
- Quota manager counters for dquot reclaim/cache activity.
- Zoned GC counters and metafile inode counters.
- 64-bit precision counters for byte totals and deferred operation relogging.

## Implementation Notes

- The 32-bit array in `struct xfsstats` ends at `xs_qm_dquot`, so offset-based access is intended for the fixed-width 32-bit counter region. The 64-bit counters are handled separately by format/clear code.
- Update macros use `current_cpu()` and directly access per-CPU storage for both `xfsstats.xs_stats` and `mp->m_stats.xs_stats`.
- The btree stat comments explicitly require appending new btree stat types to preserve output ordering and cursor index assumptions.
- `XFS_STATS_DEC_OFF` appears to evaluate the selected counter slots without decrementing them. Research consumers should verify whether the macro is unused, intentionally inert, or a bug candidate in this kernel snapshot.

## Dependencies and Callers

- Included by XFS code that needs to update counters, and by `xfs_stats.c` for formatting.
- The procfs declarations are active only with `CONFIG_PROC_FS`; otherwise the init and cleanup functions compile to no-ops.

## Research Notes

- This header is ABI-sensitive because user-visible stat output depends directly on structure field order.
- Any extension to counters must coordinate `struct __xfsstats`, `xfs_stats_format` grouping, and any users that compute `XFS_STATS_CALC_INDEX`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_stats.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_super.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_super.c

## Purpose

`xfs_super.c` is the Linux VFS integration and module lifecycle implementation for XFS. It handles mount option parsing, filesystem context setup, block device opening, per-mount workqueue and counter initialization, superblock validation, VFS super operations, remount transitions, cache creation/destruction, global sysfs/procfs/debugfs setup, and module registration.

## Top-Level State

- `xfs_super_operations`: VFS superblock callbacks for inode lifecycle, sync, freeze, statfs, unmount, shrinker, shutdown, stats, and error reporting.
- `xfs_debugfs`: top-level debugfs directory for XFS.
- `xfs_kset`: top-level sysfs kset under `/sys/fs/xfs`.
- `xfs_dbg_kobj`: debug-only global sysfs object.
- `xfs_fs_type`: Linux `file_system_type` registered as `"xfs"`.
- `xfs_discard_wq`, `xfs_alloc_wq`: global workqueues initialized at module load.

## Mount Option Parsing

- Defines table-driven fs parameters in `xfs_fs_parameters`.
- Supports core options such as `logbufs`, `logbsize`, `logdev`, `rtdev`, `wsync`, `noalign`, `swalloc`, `sunit`, `swidth`, `nouuid`, `inode32`, `inode64`, `largeio`, `filestreams`, quota options, `discard`, DAX options, zoned options, lifetime controls, max atomic write size, and debug errortags.
- Deprecates `attr2`, `noattr2`, `ikeep`, and `noikeep`, with loud warnings and deprecation postponed to September 2030.
- `suffix_kstrtoint` and `suffix_kstrtoull` parse K/M/G suffixes for size options.
- `xfs_fs_parse_param` writes parsed state into the temporary `struct xfs_mount` stored in `fs_context->s_fs_info`. It sets feature bits, quota flags, names for external devices, DAX mode, max open zones, and atomic write limits.
- `xfs_fs_validate_params` rejects incompatible combinations such as `norecovery` without read-only, `noalign` with stripe settings, quota options without quota support, invalid stripe settings, invalid log buffer counts/sizes, and invalid allocation size.

## Device Setup

- `xfs_blkdev_get` opens external log or realtime devices using the superblock open mode.
- `xfs_open_devices` opens external log/realtime devices, rejects identical realtime and data/log devices, and allocates buffer targets for data, log, and realtime devices.
- `xfs_setup_devices` configures buffer targets after the on-disk superblock is read, including log sector size, internal realtime handling, and external realtime size.
- `xfs_shutdown_devices` flushes and invalidates data, log, and realtime block devices during teardown to avoid stale page-cache metadata after unmount.

## Workqueues, Counters, and Inode GC

- `xfs_init_mount_workqueues` creates per-mount workqueues for buffer I/O, unwritten extent conversion, inode reclaim, speculative block GC, inode GC, and sync work.
- `xfs_destroy_mount_workqueues` tears them down in reverse.
- `xfs_flush_inodes_worker` and `xfs_flush_inodes` perform synchronous inode flushing via the sync workqueue.
- `xfs_init_percpu_counters`, `xfs_reinit_percpu_counters`, and `xfs_destroy_percpu_counters` manage free block, inode, delalloc block, and realtime extent counters.
- `xfs_inodegc_init_percpu` allocates and initializes per-CPU inode GC queues and delayed work items.
- `xfs_inodegc_free_percpu` releases inode GC storage.

## VFS Super Operations

- `xfs_fs_alloc_inode` intentionally BUGs because XFS uses its own inode allocation path.
- `xfs_fs_destroy_inode` marks XFS inodes reclaimable and increments destroy counters.
- `xfs_fs_drop_inode` keeps recovery-owned unlinked inodes alive until log recovery handles them.
- `xfs_fs_evict_inode` breaks final DAX layout, truncates inode pages, clears the VFS inode, and releases zoned realtime open-zone references for regular files.
- `xfs_fs_sync_fs` forces the log on synchronous sync, and stops inode/block/zone GC during the pagefault stage of filesystem freeze.
- `xfs_fs_freeze` saves reserve blocks and quiesces the log in a nofs allocation context.
- `xfs_fs_unfreeze` restores reservations, restarts log work, and restarts background GC for read-write mounts.
- `xfs_fs_statfs` reports data or realtime space depending on inode flags, accounts for reserved blocks, reports inode capacity/free counts, and applies project quota limits when relevant.
- `xfs_fs_shutdown` forces shutdown with `SHUTDOWN_DEVICE_REMOVED`.
- `xfs_fs_show_stats` emits zoned stats for zoned realtime filesystems.
- `xfs_fs_report_error` forwards non-metadata inode I/O errors to health monitoring.

## Mount Fill and Validation

- `xfs_fs_fill_super` is the central mount routine used by `get_tree_bdev`.
- It copies VFS flags into XFS mount state, validates parsed options, sets VFS xattr/export/quota/super operations, handles debug mount delay, opens devices, creates debugfs directory, initializes workqueues/counters/inodegc/stats/scrub stats, reads the superblock, finishes flags, and configures devices.
- It rejects unsupported or unsafe states: unsupported V4 filesystems, deprecated ASCII case-insensitive filesystems when support is disabled, `needsrepair` without `norecovery`, in-progress offline operations, block sizes unsupported by page cache or folios, filesystems too large for platform limits, and file offset limits exceeding XFS extent map capacity.
- It initializes realtime superblock state and filestream mount state before configuring VFS superblock fields.
- It sets VFS metadata such as magic, block size, max file size, max links, timestamp range, cgroup writeback, HSM flag, POSIX ACL flag, and inode versioning for v5 superblocks.
- It validates DAX support, disables unsupported discard, enforces zoned realtime requirements, rejects reflink with incompatible realtime extent sizes or zoned realtime devices, and enables debug-only always-COW mode when configured.
- It resumes quota accounting/enforcement from on-disk state if no quota mount options were provided.
- It calls `xfs_mountfs`, obtains the root inode, and installs `sb->s_root`.
- Error paths unwind in staged reverse order: filestream, realtime sb, core sb, scrub stats, stats, inodegc, counters, workqueues, and devices.

## Remount and Filesystem Context

- `xfs_remount_rw` rejects read-write transition when external log/realtime devices are read-only, `norecovery` is set, or unknown ro-compatible features exist. It then clears readonly, writes pending superblock changes, restores reservations, restarts log/blockgc/inodegc/zonegc, and reserves AG metadata blocks.
- `xfs_remount_ro` syncs the filesystem, stops blockgc, frees COW/speculative preallocation state, stops inodegc and zonegc, frees AG metadata reservations, saves reserve blocks, cleans the log, and marks the mount readonly.
- `xfs_fs_reconfigure` applies supported remount changes, validates parameters, copies errortags, updates max atomic write size, handles inode32/inode64 transitions, re-runs finish flag validation, and performs readonly/read-write transitions.
- `xfs_init_fs_context` allocates and initializes a fresh `struct xfs_mount`, including locks, xarrays, work structs, kset linkage, finobt reservation behavior, default log/allocsize values, and directory update hooks.
- `xfs_fs_free` frees an untransferred mount during fs_context cleanup.
- `xfs_kill_sb` delegates to `kill_block_super` and then frees the XFS mount.

## Cache and Module Lifecycle

- `xfs_init_caches` creates slab caches for buffers, log tickets, btree cursors, deferred items, directory/attr state, iforks, transactions, log item types, inodes, inode log items, intent/done item families, unlink items, exchange mapping items, and parent pointer args. Error paths unwind each cache in reverse dependency order.
- `xfs_destroy_caches` waits for delayed RCU frees via `rcu_barrier` and destroys all caches.
- `xfs_init_workqueues` creates global allocation and discard workqueues.
- `xfs_destroy_workqueues` destroys global workqueues.
- `init_xfs_fs` verifies on-disk structure sizes, runs dahash tests, prints build options, starts directory support, initializes caches/workqueues/MRU/procfs/sysctl/debugfs/sysfs/global stats/scrub stats/debug sysfs/quota, and registers the filesystem.
- `exit_xfs_fs` unregisters and tears down quota, filesystem registration, debug sysfs, scrub stats, stats sysfs, global stats storage, kset, debugfs, sysctl, procfs, MRU cache, workqueues, caches, and UUID table.

## Dependencies and Callers

- This file depends on nearly every major XFS subsystem: mount, inode, btree, allocation, log, quota, filestreams, realtime, reflink, zoned allocation, health monitoring, scrub stats, and VFS fs_context APIs.
- Exports or defines functions used externally through `xfs_super.h`, including `xfs_flush_inodes`, `xfs_set_inode_alloc`, `xfs_reinit_percpu_counters`, `xfs_debugfs_mkdir`, and `xfs_discard_wq`.
- Coordinates with `xfs_sysfs.c` for per-mount and global sysfs objects, `xfs_stats.c` for global/per-mount stats storage, and `xfs_sysctl.c` for sysctl registration.

## Research Notes

- This file is the highest-risk integration point in the group. Small changes can affect mount compatibility, recovery safety, block-device lifetime, remount semantics, freeze/thaw behavior, or module unload cleanup.
- Mount validation is deliberately staged: option-only validation occurs before devices and superblock read, while feature compatibility checks occur after the on-disk superblock and realtime metadata are available.
- Teardown is heavily order-dependent because background workers, log state, inode reclaim, buffer targets, sysfs/debugfs objects, and per-CPU allocations all depend on mount lifetime.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_super.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_super.h

## Purpose

`xfs_super.h` declares superblock-facing XFS interfaces and centralizes build option strings for module metadata and boot messages.

## Main Interfaces

- Feature string macros: `XFS_QUOTA_STRING`, `XFS_ACL_STRING`, `XFS_SECURITY_STRING`, `XFS_REALTIME_STRING`, `XFS_SCRUB_STRING`, `XFS_REPAIR_STRING`, `XFS_WARN_STRING`, `XFS_ASSERT_FATAL_STRING`, `XFS_DBG_STRING`, `XFS_VERSION_STRING`, and `XFS_BUILD_OPTIONS`.
- `XFS_WQFLAGS(wqflags)`: adds `WQ_SYSFS` to workqueue flags under `DEBUG`.
- Forward declarations for `struct xfs_inode`, `struct xfs_mount`, `struct xfs_buftarg`, and `struct block_device`.
- Function declarations: `xfs_flush_inodes`, `xfs_set_inode_alloc`, `xfs_reinit_percpu_counters`, and `xfs_debugfs_mkdir`.
- External operations: `xfs_export_operations` and `xfs_quotactl_operations`.
- Global workqueue declaration: `xfs_discard_wq`.
- `XFS_M(sb)`: converts a VFS superblock to `struct xfs_mount *`.

## Configuration Behavior

- Quota and ACL declarations compile to real functions/flags only when the corresponding config options are enabled; otherwise they compile to no-op helpers and empty strings.
- Realtime, scrub, repair, warning, fatal assert, and debug strings reflect build-time configuration.
- `set_posix_acl_flag` mutates `sb->s_flags` only when POSIX ACL support is enabled.

## Dependencies and Callers

- Consumed by `xfs_super.c` and other XFS files that need mount/superblock helpers.
- Build option strings are used for module description and init-time printk output.

## Research Notes

- This header is small but central for build-configuration reporting and VFS mount access.
- `XFS_BUILD_OPTIONS` must keep debug string last because it lacks a trailing comma fragment.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_super.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_symlink.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_symlink.c

## Purpose

`xfs_symlink.c` implements XFS symlink read, create, and inactive-time cleanup. It handles both inline symlink targets stored in the inode data fork and remote symlink targets stored in filesystem blocks.

## Main Interfaces

- `xfs_readlink(struct xfs_inode *ip, char *link)`: reads a symlink target into the caller-provided buffer.
- `xfs_symlink(struct mnt_idmap *idmap, struct xfs_inode *dp, struct xfs_name *link_name, const char *target_path, umode_t mode, struct xfs_inode **ipp)`: creates a symlink inode and directory entry transactionally.
- `xfs_inactive_symlink(struct xfs_inode *ip)`: frees remote symlink blocks during inode inactivation.
- `xfs_inactive_symlink_rmt(struct xfs_inode *ip)`: helper for remote symlink truncation.

## Read Path

- `xfs_readlink` traces the operation, rejects shutdown mounts and zapped data forks, then locks the inode shared.
- It validates `i_disk_size` against zero, negative values, and `XFS_SYMLINK_MAXLEN`.
- Inline symlinks require non-null `ip->i_df.if_data`; missing data is treated as corruption and marks the inode sick.
- Remote symlinks are read through `xfs_symlink_remote_read`.
- Corruption paths unlock, mark `XFS_SICK_INO_SYMLINK`, and return `-EFSCORRUPTED`.

## Create Path

- `xfs_symlink` initializes inode creation args with the idmap, parent inode, and symlink mode.
- It rejects shutdown mounts and targets whose string length is `>= XFS_SYMLINK_MAXLEN`.
- It allocates quota records with `xfs_icreate_dqalloc`.
- It decides whether the target can fit inline. If parent pointers are enabled or the target exceeds inline capacity, it reserves remote symlink blocks.
- It starts parent pointer context, allocates an inode creation transaction, and locks the parent directory with parent locking semantics.
- It rejects creation under directories with `XFS_DIFLAG_NOSYMLINKS`.
- It allocates and creates the symlink inode, joins the parent directory to the transaction, attaches dquots, writes the target through `xfs_symlink_write_target`, updates VFS inode size, and creates the directory entry with `xfs_dir_create_child`.
- Synchronous or dirsync mounts force the transaction to disk before returning.
- Successful completion commits the transaction, releases dquots, returns the new inode locked state correctly unwound, unlocks parent and child, finishes parent pointer state, and returns the new inode through `ipp`.

## Inactive Cleanup

- `xfs_inactive_symlink` validates symlink length under exclusive inode lock.
- Inline symlinks require no explicit cleanup because inode deletion frees local fork state.
- Remote symlinks call `xfs_inactive_symlink_rmt`.
- `xfs_inactive_symlink_rmt` asserts remote extents are already readable and limited to one or two extents, starts an itruncate transaction, changes the inode size to zero and type to regular file to avoid writing zero-length symlinks to disk, truncates remote symlink blocks, commits, and drops in-memory extent descriptions.

## Error Handling

- Transaction errors cancel the transaction and then finish inode setup/release carefully to avoid recursive transactions and deadlocks from `xfs_inactive`.
- Quotas and parent pointer context are released on all relevant error paths.
- Parent directory unlock on errors is guarded by `unlock_dp_on_error` because after `xfs_trans_ijoin`, transaction cancel owns unlock behavior.

## Dependencies and Callers

- Uses inode, bmap, quota, transaction, directory, parent pointer, deferred operation, health, and remote symlink helpers.
- Declared by `xfs_symlink.h` and used by XFS VFS inode operation code.

## Research Notes

- Parent pointer support changes symlink space reservation even for targets that otherwise fit inline.
- The cleanup path intentionally converts a soon-to-be-deleted symlink to a regular file after size zeroing so verifiers do not encounter a zero-length symlink on disk.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_symlink.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_symlink.h

## Purpose

`xfs_symlink.h` declares the kernel-only XFS symlink operations implemented in `xfs_symlink.c`.

## Main Interfaces

- `xfs_symlink`: create a symlink under a parent XFS directory.
- `xfs_readlink`: read an XFS symlink target.
- `xfs_inactive_symlink`: clean up symlink storage during inode inactivation.

## Dependencies and Callers

- Depends on declarations of `struct mnt_idmap`, `struct xfs_inode`, and `struct xfs_name` from included XFS/VFS headers in callers.
- Included by symlink implementation and XFS inode operation code.

## Research Notes

- This header intentionally contains only prototypes and include guards; behavior is entirely in `xfs_symlink.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_symlink.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_sysctl.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_sysctl.c

## Purpose

`xfs_sysctl.c` registers XFS tunables under the kernel sysctl tree `fs/xfs`. It exposes error behavior, inode flag inheritance defaults, legacy timers, allocation behavior, filestream timeout, speculative preallocation cleanup lifetime, and stats clearing.

## Main Interfaces

- `xfs_sysctl_register()`: registers `xfs_table` at `fs/xfs`.
- `xfs_sysctl_unregister()`: unregisters the table.
- `xfs_stats_clear_proc_handler`: write handler for `stats_clear` when procfs support is enabled.
- `xfs_panic_mask_proc_handler`: write handler for `panic_mask`, adding mandatory debug panic bits in debug builds.
- `xfs_deprecated_dointvec_minmax`: helper that warns on writes to deprecated sysctl options. It is defined in this file but not used by the current table.

## Tunables

- `panic_mask`: controls panic behavior for selected XFS error tags.
- `error_level`: controls how much corruption/error detail XFS reports.
- `xfssyncd_centisecs`: legacy sync daemon timer parameter.
- `inherit_sync`, `inherit_nodump`, `inherit_noatime`, `inherit_nosymlinks`, `inherit_nodefrag`: default inheritance behavior for inode flags.
- `rotorstep`: inode32 allocation group rotation control.
- `filestream_centisecs`: filestream directory-to-AG association timeout.
- `speculative_prealloc_lifetime`: blockgc/speculative preallocation lifetime.
- `stats_clear`: procfs-enabled write-only behavior to clear global stats.

## Implementation Notes

- Most entries use `proc_dointvec_minmax` with min/max values from `xfs_params`.
- `stats_clear` calls `xfs_stats_clearall(xfsstats.xs_stats)` when written with a nonzero value, then resets the stored sysctl value to zero.
- `panic_mask` mirrors the sysctl value to the global `xfs_panic_mask`; debug builds force corruption-shutdown and log-reservation panic bits.
- The table is static const and registration stores its header in `xfs_table_header`.

## Dependencies and Callers

- Includes `xfs_platform.h` and `xfs_error.h`.
- Uses `xfs_params`, `xfs_panic_mask`, `xfs_stats_clear`, and global `xfsstats`.
- Called by `init_xfs_fs` and `exit_xfs_fs` in `xfs_super.c`.

## Research Notes

- Sysctl support is optional at the header level; this implementation is compiled when the build includes the relevant source.
- The sysctl ABI overlaps conceptually with sysfs stats clearing, but sysctl clearing targets global stats only.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_sysctl.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_sysctl.h

## Purpose

`xfs_sysctl.h` defines the storage structures, sysctl IDs, globals, and conditional registration interface for XFS tunables.

## Main Interfaces

- `xfs_sysctl_val_t`: min/current/max triple for integer sysctl values.
- `xfs_param_t`: grouped XFS tunables backing the sysctl table.
- Sysctl ID enum: legacy numeric IDs for XFS sysctl options, with gaps for removed or disabled tunables.
- `struct xfs_globals`: global debug and runtime knobs not represented as `xfs_param_t`.
- `xfs_params`: external instance of `xfs_param_t`.
- `xfs_globals`: external instance of `struct xfs_globals`.
- `xfs_sysctl_register` / `xfs_sysctl_unregister`: real declarations under `CONFIG_SYSCTL`, no-op macros otherwise.

## Tunable Coverage

- Error reporting and panic behavior.
- Sync and blockgc timers.
- Stats clearing.
- Inheritance of sync, nodump, noatime, nosymlinks, and nodefrag inode flags.
- inode32 rotor step.
- Filestream timeout.
- Debug-only parallel workqueue threads and logged attribute recovery persistence.
- Bulk load slack controls, log recovery delay, mount delay, fatal assert behavior, and always-COW testing.

## Implementation Notes

- Comments describe `error_level` values and the interaction with `xfs_panic_mask`.
- Some enum IDs are preserved as comments for removed historical sysctls, which helps maintain ABI/context for old numeric identifiers.
- Debug-only fields in `struct xfs_globals` are protected by `#ifdef DEBUG`; non-debug fields remain available for production builds.

## Dependencies and Callers

- Included by code that defines or uses global tunables, including `xfs_sysctl.c`, `xfs_sysfs.c`, and `xfs_super.c`.
- `xfs_sysfs.c` exposes many `xfs_globals` fields under debug sysfs.

## Research Notes

- This file separates tunables backed by sysctl min/val/max triples from broader globals exposed through debug sysfs or used internally.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_sysctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_sysfs.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_sysfs.c

## Purpose

`xfs_sysfs.c` implements XFS sysfs objects and attributes for global stats, per-mount stats, log state, metadata I/O error handling policy, debug knobs, and zoned realtime status.

## Generic Sysfs Layer

- `struct xfs_sysfs_attr` wraps `struct attribute` with XFS-specific show/store callbacks.
- `XFS_SYSFS_ATTR_RW`, `XFS_SYSFS_ATTR_RO`, and `XFS_SYSFS_ATTR_WO` define typed attributes.
- `xfs_sysfs_object_show` and `xfs_sysfs_object_store` dispatch generic sysfs operations to the XFS attribute callbacks.
- `xfs_sysfs_ops` is reused by the kobject types in this file.
- `xfs_mp_ktype` defines the per-mount root object type. It currently has no default mount-root attributes.

## Debug Sysfs Attributes

Compiled under `DEBUG`:

- `bug_on_assert`: toggles `xfs_globals.bug_on_assert`.
- `log_recovery_delay`: integer delay from 0 to 60 seconds.
- `mount_delay`: integer mount delay from 0 to 60 seconds.
- `always_cow`: bool forcing COW behavior for reflink debug testing.
- `pwork_threads`: parallel workqueue thread override from -1 to `num_possible_cpus()`.
- `larp`: logged attribute recovery persistence testing knob.
- `bload_leaf_slack` and `bload_node_slack`: btree bulk load slack controls.
- `xfs_dbg_ktype`: global debug kobject type for these attributes.

## Stats Sysfs Attributes

- `to_xstats` maps the stats kobject to `struct xstats`.
- `stats_show` calls `xfs_stats_format`.
- `stats_clear_store` accepts only value `1` and clears the associated stats object with `xfs_stats_clearall`.
- `xfs_stats_ktype` provides `stats` and `stats_clear` attributes for global and per-mount stats directories.

## Log Sysfs Attributes

- `to_xlog` maps the kobject to `struct xlog`.
- `log_head_lsn` reads current cycle/block under `l_icloglock`.
- `log_tail_lsn` cracks the atomic tail LSN.
- `reserve_grant_head_bytes` and `write_grant_head_bytes` expose grant head byte counters.
- `xfs_log_ktype` groups these log attributes.

## Metadata Error Policy Sysfs

- Directory shape is `.../xfs/<dev>/error/<class>/<errno>/<error_attrs>`.
- `to_error_cfg` maps errno-level kobjects to `struct xfs_error_cfg`.
- `err_to_mp` maps the error root kobject to the mount.
- `max_retries` exposes retry count, mapping `XFS_ERR_RETRY_FOREVER` to `-1`.
- `retry_timeout_seconds` exposes retry timeout in seconds, also using `-1` for forever.
- `fail_at_unmount` is a mount-level error test/control attribute under the error directory.
- `xfs_error_meta_init` sets default metadata error policies: default, `EIO`, and `ENOSPC` retry forever, while `ENODEV` has zero retries and zero timeout.
- `xfs_error_sysfs_init_class` initializes the class directory and one kobject per errno policy, with unwind on partial failure.
- `xfs_error_get_cfg` maps runtime errno values to the default, EIO, ENOSPC, or ENODEV configuration.

## Zoned Sysfs Attributes

- Active when `CONFIG_XFS_RT` is enabled and the mount has zoned realtime support.
- `max_open_zones` reports open zones available for user data, subtracting `XFS_OPEN_GC_ZONES`.
- `nr_open_zones` reports the current open-zone count from zone info.
- `zonegc_low_space` is read/write, accepts 0 to 100, and wakes zone GC when changed.
- `xfs_zoned_ktype` groups zoned attributes.

## Mount Sysfs Lifecycle

- `xfs_mount_sysfs_init` names the superblock sysfs entry, creates the mount root, stats directory, error directory, `fail_at_unmount` file, metadata error class entries, and optional zoned directory.
- On failure it unwinds created objects in reverse order.
- `xfs_mount_sysfs_del` removes optional zoned sysfs, all error cfg kobjects, metadata error class, error root, stats dir, and mount root.

## Dependencies and Callers

- Depends on `xfs_sysfs.h`, log internals, mount state, and zoned allocation headers.
- Called by mount/log/global stats setup code elsewhere in XFS, especially `xfs_super.c`.
- Uses `xfs_stats_format` and `xfs_stats_clearall` from `xfs_stats.c`.

## Research Notes

- Kobject lifetime is completion-based through helpers in `xfs_sysfs.h`; deletion waits for release completion.
- Error policy sysfs is per mount, while stats sysfs exists both globally and per mount.
- Debug sysfs attributes directly mutate global variables and are intentionally available only in debug builds.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_sysfs.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_sysfs.h

## Purpose

`xfs_sysfs.h` declares XFS sysfs kobject types and provides small helpers for kobject initialization, deletion, release completion, and mount sysfs lifecycle.

## Main Interfaces

- External kobject types: `xfs_dbg_ktype`, `xfs_log_ktype`, and `xfs_stats_ktype`.
- `to_kobj(struct kobject *kobject)`: maps a generic kobject to `struct xfs_kobj`.
- `xfs_sysfs_release`: completes the embedded completion when a kobject is released.
- `xfs_sysfs_init`: initializes completion and calls `kobject_init_and_add` with an optional parent `xfs_kobj`.
- `xfs_sysfs_del`: deletes, puts, and waits for release completion.
- `xfs_mount_sysfs_init` / `xfs_mount_sysfs_del`: per-mount sysfs lifecycle declarations.

## Implementation Notes

- `xfs_sysfs_init` calls `kobject_put` on initialization failure, matching kobject lifetime rules.
- `xfs_sysfs_del` waits synchronously for release completion, which protects embedded kobjects inside longer-lived XFS structs.
- Parent linkage is based on `struct xfs_kobj`, but the helper accepts a null parent for top-level sysfs objects under the kset configured by callers.

## Dependencies and Callers

- Used by `xfs_sysfs.c` for all kobject types.
- Used by `xfs_super.c` to create global stats/debug sysfs objects and by mount code to manage per-mount sysfs state.

## Research Notes

- This header encodes the expected XFS sysfs lifetime pattern: embedded kobject plus completion, with synchronous teardown.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_trace.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_trace.c

## Purpose

`xfs_trace.c` instantiates XFS tracepoints. It includes the XFS headers needed by trace event definitions, then defines `CREATE_TRACE_POINTS` before including `xfs_trace.h`.

## Main Interfaces

- No callable functions are defined here.
- The key action is `#define CREATE_TRACE_POINTS` followed by `#include "xfs_trace.h"`, which causes tracepoint storage and event implementations to be generated once.

## Included Subsystems

The file includes headers for filesystem format, mount state, allocation, bmap, attributes, transactions, log internals, buffer items, quota and dquot items, log recovery, filestreams, fsmap, staged btrees, inode cache, unlinked inode items, AG state, error handling, iomap, in-memory buffers/btrees, exchange mappings/ranges, parent pointers, reverse mapping, refcount, metafiles, metadir, realtime groups, zoned allocation, health monitoring, failure notification, file operations, and generic filesystem error events.

## Dependencies and Callers

- Trace macros throughout XFS call events declared in `xfs_trace.h`; this file provides the single compilation unit that materializes them.
- The comment notes that `xfs_trace.h` is included last so helper definitions from prior headers are available to trace event implementations.

## Research Notes

- Changes to trace event definitions generally occur in `xfs_trace.h`, but this file must include any headers required by those definitions.
- Because this file creates tracepoints, duplicate `CREATE_TRACE_POINTS` definitions elsewhere would conflict.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_trace.c -->