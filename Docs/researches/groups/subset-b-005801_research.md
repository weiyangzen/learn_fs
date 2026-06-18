# subset-b-005801 Research

Grouped source research for XFS statistics, superblock/mount lifecycle, symlink operations, sysctl/sysfs exposure, and tracepoint instantiation. Each section is marker-delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_stats.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_stats.c

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_stats.c` implements XFS runtime statistics formatting, clearing, and legacy procfs compatibility. It owns the global `xfsstats` instance and provides the text output consumed by `/sys/fs/xfs/stats/stats`, per-mount stats kobjects, and `/proc/fs/xfs/stat` symlink compatibility. The source was read as a complete 179-line file for this report.

## Important APIs, Types, and Functions

Important symbols are `struct xstats xfsstats`, `counter_val`, `xfs_stats_format`, `xfs_stats_clearall`, `xfs_init_procfs`, and `xfs_cleanup_procfs`. With quota and procfs enabled, the file also implements `xqm_proc_show` and `xqmstat_proc_show` for legacy quota stats. `xfs_stats_format` emits grouped counters using an internal `xstats_entry` table whose endpoints are derived from `xfsstats_offset(...)`; the high-precision 64-bit counters are emitted separately.

## Control Flow

Stats reads enter through sysfs or procfs and call `xfs_stats_format`. The formatter walks every declared stats group, sums the selected 32-bit counter index across all possible CPUs with `counter_val`, appends a line per group, then separately sums the 64-bit byte/relog counters across CPUs. Stats clearing enters through sysfs `stats_clear` or sysctl `stats_clear`, calls `xfs_stats_clearall`, logs a notice, and zeroes each per-CPU stats object while preserving stateful inode counters.

## State and Persistence Behavior

Statistics are in-memory per-CPU counters. The global `xfsstats.xs_stats` is allocated during module initialization, and each mounted filesystem owns another `mp->m_stats.xs_stats`. Values do not persist across module unload or reboot. `xfs_stats_clearall` intentionally preserves `xs_inodes_active` and `xs_inodes_meta` because they represent current state rather than historical events.

## Dependencies and Integration Points

The implementation depends on XFS platform wrappers, Linux per-CPU iteration, procfs, sysfs, quota configuration, and `xfs_notice`. It integrates with `xfs_sysfs.c` for normal stats exposure, `xfs_sysctl.c` for global clear support, and `xfs_super.c` module init/exit for procfs creation and removal.

## Risks and Edge Cases

The formatting table must match `struct __xfsstats` layout and endpoint order; adding counters without updating endpoints can mislabel or hide stats. The `PATH_MAX` output buffer convention constrains formatting even as counters grow. Clearing loops over possible CPUs and disables preemption around each zeroing operation, but consumers can still observe racing snapshots because these are diagnostic counters, not transactional data.

## Test Signals

Useful signals include building with and without `CONFIG_PROC_FS` and `CONFIG_XFS_QUOTA`, reading `/sys/fs/xfs/stats/stats`, clearing via sysfs and sysctl, verifying active/meta inode counters survive clear, and checking legacy `/proc/fs/xfs/stat`, `xqmstat`, and `xqm` entries when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_stats.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_stats.h

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_stats.h` defines the XFS statistics ABI used by the rest of the filesystem. It lays out every 32-bit and 64-bit counter, provides offset helpers for table-based btree stats, declares formatting/clearing/procfs functions, and defines macros that update both global and per-mount counter sets. The source was read as a complete 230-line file for this report.

## Important APIs, Types, and Functions

Important declarations include `enum __XBTS_*` btree counter offsets, `struct __xfsstats`, `struct xfsstats`, `xfsstats_offset`, `XFS_STATS_CALC_INDEX`, `XFS_STATS_INC`, `XFS_STATS_DEC`, `XFS_STATS_ADD`, `XFS_STATS_INC_OFF`, `XFS_STATS_DEC_OFF`, `XFS_STATS_ADD_OFF`, `xfs_stats_format`, `xfs_stats_clearall`, and `extern struct xstats xfsstats`. Procfs functions are declared when `CONFIG_PROC_FS` is enabled and stubbed otherwise.

## Control Flow

This header has no runtime control flow by itself. Other XFS code invokes the update macros inline at event sites; each macro resolves the current CPU's global stats object and the current mount's stats object, then updates the same field or array offset in both. Formatting and clear entry points are implemented by `xfs_stats.c`.

## State and Persistence Behavior

The file defines the in-memory layout for per-CPU stats. `struct xfsstats` overlays the named `struct __xfsstats` with a 32-bit array for offset-based access up to the quota counter boundary, while 64-bit counters remain named fields. Counters are volatile kernel diagnostics and are not persisted to disk.

## Dependencies and Integration Points

The header depends on `<linux/percpu.h>` and the broader XFS mount/stat types available through including translation units. It is consumed by allocation, btree, inode, buffer, quota, log, zoned, and sysfs code. The btree cursor code uses `XFS_STATS_CALC_INDEX` so cursor instances can carry a base stats index and increment fixed offsets.

## Risks and Edge Cases

The stats structure is an observable diagnostic ABI because userspace tools parse the exported text. Counter order, array bounds, and group endpoints must be changed carefully. `XFS_STATS_DEC_OFF` as written references the offset element without decrementing, so any caller expecting offset decrement behavior would not get it. Update macros assume a valid `mp` and allocated `mp->m_stats.xs_stats`.

## Test Signals

Compile coverage across quota/procfs configurations, static analysis for offset bounds, runtime stats smoke tests that exercise representative update macros, and userspace parser checks for `/sys/fs/xfs/stats/stats` output are the best signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_super.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_super.c

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_super.c` is the XFS VFS superblock and module lifecycle implementation. It parses mount options, opens and configures data/log/realtime devices, initializes per-mount workqueues/counters/stats, fills the Linux superblock, handles remount/freeze/statfs/sync/shutdown callbacks, and registers or unregisters global XFS caches, sysfs, procfs, sysctl, quota, workqueues, and the filesystem type. The source was read as a complete 2,721-line file for this report.

## Important APIs, Types, and Functions

Important public or integration-facing symbols include `xfs_set_inode_alloc`, `xfs_flush_inodes`, `xfs_reinit_percpu_counters`, `xfs_debugfs_mkdir`, `xfs_export_operations`, `xfs_quotactl_operations`, `xfs_discard_wq`, `init_xfs_fs`, and `exit_xfs_fs`. The main static machinery includes `xfs_fs_parameters`, `xfs_fs_parse_param`, `xfs_fs_validate_params`, `xfs_fs_fill_super`, `xfs_fs_get_tree`, `xfs_fs_reconfigure`, `xfs_remount_rw`, `xfs_remount_ro`, `xfs_super_operations`, `xfs_context_ops`, `xfs_fs_type`, cache/workqueue init/destroy helpers, DAX setup, device setup, statfs helpers, freeze/unfreeze helpers, inode lifecycle callbacks, and filesystem context allocation/freeing.

## Control Flow

Module load begins at `init_xfs_fs`: verify on-disk structures, run the directory hash test, initialize directory code, slab caches, global workqueues, MRU cache, procfs, sysctl, debugfs, sysfs kset, global stats, scrub stats, optional debug kobject, quota manager, and finally `register_filesystem`. Mount setup begins with `xfs_init_fs_context`, which allocates a mostly blank `struct xfs_mount`, initializes locks, xarrays, work items, defaults, hooks, and parser operations. Parameters are parsed by `xfs_fs_parse_param`, validated by `xfs_fs_validate_params`, and materialized by `xfs_fs_fill_super`.

During `xfs_fs_fill_super`, the code copies VFS flags into XFS feature state, opens devices, creates debugfs and per-mount workqueues, initializes percpu counters and inodegc state, allocates stats and scrub stats, reads the superblock, validates feature and geometry constraints, configures devices, reads realtime metadata, mounts filestream state, populates the Linux superblock, checks DAX/discard/zoned/reflink constraints, resumes quota flags when appropriate, calls `xfs_mountfs`, and installs the root dentry. Every failure path unwinds only the resources acquired up to that point.

Runtime VFS callbacks route through `xfs_super_operations`: sync forces the log and stops GC before freeze, freeze saves reserve blocks and quiesces the log, unfreeze restores reserves and restarts workers, statfs reports data or realtime free space plus quota adjustments, inode destroy queues reclaim, drop_inode protects recovery inodes, evict_inode tears down page cache/DAX and zoned private state, put_super unmounts and frees per-mount runtime resources, and shutdown forces device-removed shutdown.

Remount uses a fresh parsed mount context. `xfs_fs_reconfigure` validates the requested options, copies error tags, validates atomic write changes, updates inode32/inode64 allocation policy, reruns finish validation, and then dispatches ro-to-rw or rw-to-ro transitions. `xfs_remount_rw` restores reserves, restarts log/blockgc/inodegc/zonegc, and reserves per-AG metadata blocks; `xfs_remount_ro` syncs, stops GC, frees COW/prealloc space, unreserves AG blocks, saves reserve blocks, cleans the log, and marks the mount readonly.

## State and Persistence Behavior

Persistent state is the on-disk XFS superblock, realtime metadata, log, quota state, and feature flags read and modified by lower-level mount code. This file owns orchestration state: `struct xfs_mount`, feature bits, qflags, device targets, workqueue pointers, per-CPU counters, per-CPU stats, inodegc queues, debugfs/sysfs objects, and module-global slab caches/workqueues/ksets. Freeze/remount paths explicitly save and restore reservation pool state. Mount options such as quota flags, DAX mode, inode allocation mode, discard, zoned limits, and atomic write limits affect runtime behavior and sometimes trigger superblock updates through lower layers.

## Dependencies and Integration Points

This file integrates nearly every major XFS subsystem: superblock reading/freeing, log recovery and forcing, inode cache/reclaim, buffer targets, allocation groups, quotas, realtime/zoned allocation, filestreams, scrub stats, health monitoring, parent pointers, deferred ops, reflink, DAX, sysfs/procfs/sysctl/debugfs, VFS fs_context, block device open/flush/invalidate, shrinkers, freeze infrastructure, and module registration. It calls into `xfs_stats.c`/`xfs_sysfs.c` indirectly through stats allocation and module sysfs setup.

## Risks and Edge Cases

Mount and module init are high-risk because the unwind ladder must exactly mirror acquisition order. Device identity checks prevent realtime/log/data aliasing, and `xfs_shutdown_devices` flushes and invalidates bdev page cache to avoid stale metadata reads by userspace tools. Option validation must reject incompatible combinations such as `norecovery` rw mounts, `noalign` with stripe options, invalid log buffer sizes, unsupported quotas, zoned-only options on non-zoned filesystems, unsupported V4/ascii-ci formats, needs-repair filesystems without norecovery, and block sizes outside platform limits. DAX is disabled or rejected depending on device, blocksize, reflink, and partition state. Remount currently ignores many immutable option changes by design, so tests should distinguish accepted-but-ignored options from real state changes.

## Test Signals

Strong signals include kernel builds across `CONFIG_XFS_QUOTA`, `CONFIG_XFS_RT`, `CONFIG_FS_DAX`, `CONFIG_XFS_SUPPORT_V4`, `CONFIG_XFS_SUPPORT_ASCII_CI`, debug, scrub, and repair combinations; fstests mount/remount/freeze/unfreeze/statfs coverage; failure-injection of each mount-stage allocation and device open path; ro/rw remount tests with external log and realtime devices; DAX/discard/zoned/reflink compatibility tests; module load/unload leak checks; and sysfs/procfs/debugfs presence checks after mount and unmount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_super.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_super.h

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_super.h` is the public header for XFS superblock-facing helpers and build-option strings. It centralizes feature strings used in module identification, configuration-dependent quota and ACL stubs, workqueue flag behavior, and declarations needed outside `xfs_super.c`. The source was read as a complete 104-line file for this report.

## Important APIs, Types, and Functions

Important definitions include `XFS_VERSION_STRING`, `XFS_BUILD_OPTIONS`, `XFS_WQFLAGS`, `XFS_M`, `XFS_QUOTA_STRING`, `XFS_ACL_STRING`, `XFS_REALTIME_STRING`, `XFS_SCRUB_STRING`, `XFS_REPAIR_STRING`, and configuration stubs for `xfs_qm_init`, `xfs_qm_exit`, and `set_posix_acl_flag`. Declarations include `xfs_flush_inodes`, `xfs_set_inode_alloc`, `xfs_export_operations`, `xfs_quotactl_operations`, `xfs_reinit_percpu_counters`, `xfs_discard_wq`, and `xfs_debugfs_mkdir`.

## Control Flow

There is no runtime control flow in the header. Compile-time configuration determines which strings, stubs, and flags are visible to callers. `XFS_M(sb)` provides the canonical cast from a Linux `super_block` to the owning `xfs_mount`.

## State and Persistence Behavior

The header owns no storage except external declarations. Its macros influence runtime behavior by enabling POSIX ACL superblock flags, quota manager initialization, and sysfs-visible workqueue flags under debug builds.

## Dependencies and Integration Points

The header depends on Linux exportfs declarations and forward declarations for XFS mount/inode/device types. It is included by files that need superblock helpers, module build strings, quota operation declarations, discard workqueue access, and debugfs helpers.

## Risks and Edge Cases

Build-option strings must remain consistent with actual configuration or module identification becomes misleading. Stubbed quota/ACL helpers must preserve call-site semantics when features are disabled. `XFS_WQFLAGS` changes workqueue observability under debug builds, so debug-only sysfs behavior should not leak into release expectations.

## Test Signals

Compile matrix coverage for quota, ACL, realtime, scrub, repair, warning, fatal assert, and debug options is the main signal. Runtime checks include module description/build-option strings and workqueue sysfs visibility in debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_super.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_symlink.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_symlink.c

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_symlink.c` implements XFS symlink read, create, and inactive cleanup behavior. It handles inline symlink data, remote symlink blocks, quota and parent pointer integration, directory updates, transaction reservation/commit/cancel paths, and corruption detection for invalid symlink lengths or fork data. The source was read as a complete 362-line file for this report.

## Important APIs, Types, and Functions

The externally declared functions are `xfs_readlink`, `xfs_symlink`, and `xfs_inactive_symlink`. The important internal helper is `xfs_inactive_symlink_rmt`, which frees remote symlink blocks and converts the unlinked inode away from symlink mode before truncation. The implementation uses `struct xfs_icreate_args`, `struct xfs_dir_update`, `struct xfs_trans`, `struct xfs_dquot`, parent pointer args, `XFS_SYMLINK_MAXLEN`, `XFS_DINODE_FMT_LOCAL`, and tracepoints `trace_xfs_readlink`, `trace_xfs_symlink`, and `trace_xfs_inactive_symlink`.

## Control Flow

`xfs_readlink` rejects shutdown mounts and zapped data forks, locks the inode shared, validates a nonzero symlink length within `XFS_SYMLINK_MAXLEN`, copies inline data when the data fork is local, or delegates to `xfs_symlink_remote_read` for remote symlink contents. Corrupt cases mark the inode sick and return `-EFSCORRUPTED`.

`xfs_symlink` validates shutdown state and target length, allocates quota records, decides whether the target fits inline or needs remote blocks, starts parent pointer bookkeeping, allocates an inode-create transaction, locks the parent directory, rejects directories with `XFS_DIFLAG_NOSYMLINKS`, allocates and creates the symlink inode, joins the parent to the transaction, attaches dquots, writes the target with `xfs_symlink_write_target`, creates the directory child entry, marks the transaction synchronous for sync/dirsync mounts, commits, releases dquots, unlocks inodes, and returns the created inode. Error paths cancel transactions, finish parent args, release dquots, finish and release partially created inodes, and avoid double-unlocking the parent.

`xfs_inactive_symlink` validates length and returns immediately for inline symlinks because inode freeing removes local fork data. Remote symlinks call `xfs_inactive_symlink_rmt`, which allocates an itruncate transaction, locks and joins the inode, sets disk size to zero, changes VFS mode to regular file to avoid writing a zero-length symlink, logs core changes, truncates remote symlink blocks, commits, frees in-memory extent descriptors, and unlocks.

## State and Persistence Behavior

Symlink target bytes persist either in the inode data fork or in remote filesystem blocks. Creation persists inode metadata, quota attachments, parent pointer metadata when enabled, target data, and the directory entry atomically through XFS transactions. Inactive cleanup persists remote block freeing and inode core changes before memory-only extent descriptor cleanup. Corruption state is recorded in inode health by `xfs_inode_mark_sick`.

## Dependencies and Integration Points

The file depends on XFS inode, bmap, quota, directory, transaction, parent pointer, deferred-op, health, remote symlink, and trace infrastructure. VFS inode operations call into it through `xfs_iops.c`; inactive inode processing calls `xfs_inactive_symlink` from `xfs_inode.c`. It integrates with quota accounting, parent pointers, directory updates, synchronous mount semantics, and log transaction reservation classes.

## Risks and Edge Cases

Target length validation is strict: zero-length symlinks are treated as corruption during read/inactive and too-long targets return `-ENAMETOOLONG` during create. Inline symlink reads require non-null `if_data`; otherwise the inode is marked sick. Remote symlink cleanup assumes extents have been read and that symlink blocks fit the expected one or two extents. Error-path lock ownership changes after `xfs_trans_ijoin` are subtle, and parent pointer/quota resources must be released on every exit.

## Test Signals

Test signals include creating and reading inline and remote symlinks, rejecting too-long targets, enforcing `nosymlinks`, symlink creation under user/group/project quotas, parent-pointer enabled filesystems, sync/dirsync mounts, crash-recovery around symlink creation, corruption tests for bad lengths and missing inline data, and inactive cleanup tests that verify remote blocks are freed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_symlink.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_symlink.h

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_symlink.h` declares the kernel-internal XFS symlink API. It is the small contract used by inode operation code and inactive inode cleanup to create, read, and free symlinks. The source was read as a complete 16-line file for this report.

## Important APIs, Types, and Functions

The header declares `xfs_symlink(struct mnt_idmap *idmap, struct xfs_inode *dp, struct xfs_name *link_name, const char *target_path, umode_t mode, struct xfs_inode **ipp)`, `xfs_readlink(struct xfs_inode *ip, char *link)`, and `xfs_inactive_symlink(struct xfs_inode *ip)`.

## Control Flow

There is no executable flow in the header. Callers use `xfs_symlink` during VFS symlink creation, `xfs_readlink` for readlink/get_link operations, and `xfs_inactive_symlink` during inode inactivation.

## State and Persistence Behavior

The header owns no state. Its declared functions manipulate persistent symlink inode data and directory metadata in `xfs_symlink.c`.

## Dependencies and Integration Points

The declarations rely on XFS inode/name types and Linux idmapped mount types being visible to including translation units. Integration points are VFS inode operations and inode reclaim/inactivation paths.

## Risks and Edge Cases

The API exposes raw XFS inode pointers and caller-provided buffers, so callers must pass locked/lifetime-valid objects according to the implementation contract and enough storage for symlink contents.

## Test Signals

Compile coverage of VFS symlink operation files and inactive inode code is the direct signal; runtime behavior is covered by the `xfs_symlink.c` test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_symlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_sysctl.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_sysctl.c

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_sysctl.c` registers XFS global sysctl tunables under `fs/xfs` and implements special handlers for clearing stats and updating panic behavior. The source was read as a complete 197-line file for this report.

## Important APIs, Types, and Functions

Important symbols include `xfs_table_header`, `xfs_stats_clear_proc_handler`, `xfs_panic_mask_proc_handler`, `xfs_deprecated_dointvec_minmax`, the `xfs_table[]` control table, `xfs_sysctl_register`, and `xfs_sysctl_unregister`. The table exposes `panic_mask`, `error_level`, `xfssyncd_centisecs`, inheritance defaults, `rotorstep`, `filestream_centisecs`, `speculative_prealloc_lifetime`, and procfs-only `stats_clear`.

## Control Flow

Module initialization calls `xfs_sysctl_register`, which registers the static table at `fs/xfs`. Reads and writes are routed through `proc_dointvec_minmax` or custom wrappers. Writing a nonzero `stats_clear` value clears global stats and resets the parameter to zero. Writing `panic_mask` updates the public parameter and, in debug builds, forces corruption-shutdown and log-reservation panic bits. Module exit calls `xfs_sysctl_unregister`.

## State and Persistence Behavior

Sysctl values are in-memory fields of the global `xfs_params` object. They affect subsequent XFS behavior while the module is loaded but are not persisted by this code. `stats_clear` has side effects on global per-CPU stats rather than storing a lasting value.

## Dependencies and Integration Points

The file depends on Linux sysctl/proc handlers, `xfs_params`, `xfs_stats_clearall`, `xfsstats`, and XFS error/panic globals. It is initialized and torn down by `xfs_super.c`. The exposed tunables influence inode flag inheritance, reporting level, panic policy, allocation heuristics, filestream expiry, and block garbage collection intervals elsewhere in XFS.

## Risks and Edge Cases

The table contains procfs-gated handlers, so builds without procfs must still compile through header stubs. Bounds are driven by `xfs_params.*.min/max`; incorrect bounds can admit unsupported runtime values. Debug builds deliberately override `panic_mask`, which can surprise tests that expect exact write/read symmetry.

## Test Signals

Signals include sysctl registration/unregistration smoke tests, read/write validation for every `fs/xfs/*` knob, min/max rejection checks, writing `stats_clear=1` and observing stats reset, and debug-build checks for forced panic bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_sysctl.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_sysctl.h

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_sysctl.h` defines XFS global tunable structures, sysctl IDs, debug/global knobs, and registration stubs. It is the shared contract between sysctl registration, mount/superblock code, and code paths that consume global XFS parameters. The source was read as a complete 100-line file for this report.

## Important APIs, Types, and Functions

Important types are `xfs_sysctl_val_t`, `xfs_param_t`, and `struct xfs_globals`. Important declarations are `extern xfs_param_t xfs_params`, `extern struct xfs_globals xfs_globals`, `xfs_sysctl_register`, and `xfs_sysctl_unregister`. The enum preserves historical sysctl IDs such as `XFS_PANIC_MASK`, `XFS_ERRLEVEL`, `XFS_STATS_CLEAR`, inheritance defaults, and `XFS_FILESTREAM_TIMER`.

## Control Flow

There is no runtime control flow in the header. When `CONFIG_SYSCTL` is disabled, register/unregister collapse to no-op stubs so module init can call them unconditionally.

## State and Persistence Behavior

The header defines the shape of global in-memory tunables. `xfs_params` holds min/current/max triples for user-facing sysctl values. `xfs_globals` holds debug and internal global knobs such as log recovery delay, mount delay, assert behavior, always-COW, bulk-load slack, and debug-only parallel workqueue thread limits.

## Dependencies and Integration Points

The header depends on `<linux/sysctl.h>`. It integrates with `xfs_sysctl.c`, `xfs_super.c`, debug sysfs attributes in `xfs_sysfs.c`, error handling, mount delay simulation, btree bulk loading, and reflink debug behavior.

## Risks and Edge Cases

Because many subsystems read `xfs_params` and `xfs_globals`, changing defaults or ranges can affect mount behavior, error handling, and test-only debug behavior globally. The historical enum values should remain stable for compatibility. Debug-only fields must be guarded consistently with users in `xfs_sysfs.c`.

## Test Signals

Compile coverage with `CONFIG_SYSCTL` on and off plus debug and non-debug builds is essential. Runtime signals include sysctl knob presence, correct default ranges, debug sysfs behavior for `xfs_globals`, and mount-delay/log-recovery-delay injection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_sysctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_sysfs.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_sysfs.c

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_sysfs.c` implements XFS sysfs kobject support and attributes for global debug controls, global and per-mount stats, log state, metadata I/O error retry policy, fail-at-unmount behavior, and zoned filesystem controls. The source was read as a complete 892-line file for this report.

## Important APIs, Types, and Functions

Important types and helpers include `struct xfs_sysfs_attr`, `to_attr`, `xfs_sysfs_object_show`, `xfs_sysfs_object_store`, `xfs_sysfs_ops`, `xfs_mp_ktype`, optional `xfs_dbg_ktype`, `xfs_stats_ktype`, `xfs_log_ktype`, `xfs_error_cfg_ktype`, `xfs_error_ktype`, `struct xfs_error_init`, and `xfs_zoned_ktype`. Important exported functions are `xfs_mount_sysfs_init`, `xfs_mount_sysfs_del`, and `xfs_error_get_cfg`. Attribute handlers cover debug knobs, `stats`, `stats_clear`, log head/tail/grant heads, `max_retries`, `retry_timeout_seconds`, `fail_at_unmount`, `max_open_zones`, `nr_open_zones`, and `zonegc_low_space`.

## Control Flow

Generic sysfs show/store dispatch converts Linux attributes to `struct xfs_sysfs_attr` and calls the attribute-specific function. `xfs_mount_sysfs_init` creates `.../xfs/<dev>/`, then child kobjects for `stats`, `error`, the `fail_at_unmount` file, metadata error policy entries for default/EIO/ENOSPC/ENODEV, and optional `zoned` attributes. `xfs_error_sysfs_init_class` initializes each errno policy kobject and seeds retry defaults. `xfs_mount_sysfs_del` removes zoned, error policy, metadata, error, stats, and mount kobjects in reverse. `xfs_error_get_cfg` maps runtime errno values to the configured retry policy.

## State and Persistence Behavior

Sysfs objects are runtime kernel objects attached to global or per-mount XFS state. Stats attributes read and clear per-CPU stats. Log attributes report live log head/tail/grant atomic state. Error policy attributes mutate `mp->m_error_cfg[class][errno]`, converting `-1` to `XFS_ERR_RETRY_FOREVER` and seconds to jiffies. Zoned attributes expose live open-zone counters and allow `zonegc_low_space` changes that wake zone GC. None of these settings are persisted by this file.

## Dependencies and Integration Points

The file depends on Linux kobject/sysfs APIs, `xfs_sysfs.h`, `xfs_stats_format`, `xfs_stats_clearall`, log internals, mount structures, XFS error policy definitions, realtime/zoned configuration, and zone GC wakeup. It is called from mount/unmount paths in `xfs_mount.c` and global setup in `xfs_super.c` through ktypes.

## Risks and Edge Cases

Attribute validation is critical because these files mutate live filesystem behavior. Retry timeout rejects values less than `-1` or greater than one day; max retries rejects less than `-1`; fail-at-unmount and debug boolean knobs reject invalid values; zoned low-space percentages reject values over 100. The init error path must unwind partially created kobjects, and deletion assumes all kobjects were initialized consistently. Debug-only attributes must match `struct xfs_globals` guards.

## Test Signals

Signals include sysfs tree presence after mount, stats read/clear behavior, log LSN/grant attributes changing under load, metadata error policy read/write validation, fail-at-unmount testing, zoned attribute presence only on zoned RT filesystems, `zonegc_low_space` wakeup behavior, and mount-failure injection to verify kobject unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_sysfs.h -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_sysfs.h

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_sysfs.h` defines the small XFS wrapper API around Linux kobjects. It provides ktype declarations, conversion helpers, init/delete helpers with completion-based release synchronization, and per-mount sysfs init/delete declarations. The source was read as a complete 58-line file for this report.

## Important APIs, Types, and Functions

Important declarations are `xfs_dbg_ktype`, `xfs_log_ktype`, `xfs_stats_ktype`, `xfs_mount_sysfs_init`, and `xfs_mount_sysfs_del`. Important inline helpers are `to_kobj`, `xfs_sysfs_release`, `xfs_sysfs_init`, and `xfs_sysfs_del`.

## Control Flow

`xfs_sysfs_init` selects the parent kobject, initializes the completion, calls `kobject_init_and_add`, and drops the kobject if add fails. `xfs_sysfs_del` removes the kobject, puts the reference, and waits for the release callback to complete. `xfs_sysfs_release` completes the per-object completion when the Linux kobject lifetime actually ends.

## State and Persistence Behavior

The header manages runtime kobject lifetime state embedded in `struct xfs_kobj`. It does not persist anything to disk; the completion only synchronizes teardown with kobject release.

## Dependencies and Integration Points

The header depends on Linux kobject and completion primitives through included XFS platform headers. It integrates with `xfs_sysfs.c`, global stats/debug/log kobjects, and per-mount sysfs setup in mount code.

## Risks and Edge Cases

All embedded `struct xfs_kobj` users must have a valid `complete` field and must not be freed before `xfs_sysfs_del` returns. Failed `kobject_init_and_add` paths rely on `kobject_put` to trigger release. Double deletion or deleting never-added kobjects would break the completion/lifetime contract.

## Test Signals

Build coverage plus mount/unmount leak checks, kobject reference debugging, sysfs removal races, and failure injection around `kobject_init_and_add` are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_trace.c -->
# sources/distributed-fs/ceph-client/fs/xfs/xfs_trace.c

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_trace.c` instantiates the XFS tracepoint definitions. It includes the XFS type and helper headers needed by trace event implementations, defines `CREATE_TRACE_POINTS`, and then includes `xfs_trace.h` last so the tracepoint storage and generated functions are emitted exactly once. The source was read as a complete 65-line file for this report.

## Important APIs, Types, and Functions

The key symbol is the `CREATE_TRACE_POINTS` definition before `#include "xfs_trace.h"`. There are no ordinary functions in this file. The preceding include list supplies types and helpers for trace events covering filesystem operations, btrees, transactions, log recovery, quotas, iomap, reflink, parent pointers, realtime groups, zoned allocation, health, failure notification, and VFS/file paths.

## Control Flow

There is no direct runtime control flow. At compile time, this translation unit turns tracepoint declarations in `xfs_trace.h` into definitions. At runtime, trace calls elsewhere in XFS resolve to the tracepoint objects emitted here.

## State and Persistence Behavior

The file contributes static tracepoint metadata and runtime tracepoint state managed by the Linux tracing subsystem. It does not persist filesystem state and does not own per-mount data.

## Dependencies and Integration Points

The file depends on a broad set of XFS headers because tracepoint format code references many internal structures. It integrates with every `trace_xfs_*` call site, including functions in `xfs_super.c` and `xfs_symlink.c`, and with Linux ftrace/perf tracepoint infrastructure.

## Risks and Edge Cases

Include order is important: `CREATE_TRACE_POINTS` must appear once and `xfs_trace.h` must be included last after helper types are visible. Missing includes can break trace event compilation even if ordinary code compiles. Adding trace events that dereference internal structures requires this file to include the needed helper declarations.

## Test Signals

Build coverage is the primary signal. Runtime signals include enabling representative XFS trace events through tracefs, exercising mount/symlink/log/btree operations, and checking that event formatting does not fault or emit invalid fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_trace.c -->
