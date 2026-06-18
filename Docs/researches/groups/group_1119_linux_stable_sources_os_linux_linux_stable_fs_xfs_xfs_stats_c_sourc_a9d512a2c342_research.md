# Group Research: group_1119_linux_stable_sources_os_linux_linux_stable_fs_xfs_xfs_stats_c_sourc_a9d512a2c342

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_stats.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_stats.c

This file implements XFS statistics formatting, clearing, and legacy procfs compatibility.

Key points:
- Defines the global `struct xstats xfsstats`, used for filesystem-wide counters.
- `counter_val` sums a 32-bit counter offset across all possible CPUs from a per-cpu `struct xfsstats`.
- `xfs_stats_format` emits the legacy XFS stats text layout, grouping counters by fixed offset endpoints from `struct __xfsstats`.
- It separately sums 64-bit precision counters: `xs_xstrat_bytes`, `xs_write_bytes`, `xs_read_bytes`, `xs_defer_relog`, and `xs_gc_bytes`.
- Output includes traditional groups such as `extent_alloc`, `abt`, `blk_map`, `bmbt`, `dir`, `trans`, `log`, `rw`, btree v2 groups, quota, zoned, metafile, `xpc`, `defer_relog`, `debug`, and zone GC byte stats.
- `xfs_stats_clearall` zeroes all per-cpu counters but preserves stateful inode counters `xs_inodes_active` and `xs_inodes_meta`.
- With `CONFIG_PROC_FS`, creates legacy `/proc/fs/xfs` entries:
  - `stat` symlink to `/sys/fs/xfs/stats/stats`
  - quota proc views `xqmstat` and `xqm` when `CONFIG_XFS_QUOTA` is enabled.
- `xfs_init_procfs` and `xfs_cleanup_procfs` are module lifecycle helpers called from `xfs_super.c`.

Important dependencies:
- Counter structure and offset macros from `xfs_stats.h`.
- Per-cpu allocation created in module init and per-mount setup.
- Sysfs stats exposure in `xfs_sysfs.c`.
- Global lifecycle in `xfs_super.c`.

Behavioral notes:
- The stats ABI is offset-sensitive because formatting depends on field order in `struct __xfsstats`.
- Clearing is intentionally not a pure reset: active/metafile inode counters are live state, not cumulative events.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_stats.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_stats.h

This header defines XFS runtime statistics layout, btree counter indexing, and counter update macros.

Key points:
- Defines fixed btree statistic offsets `__XBTS_*` with `__XBTS_MAX = 15`.
- Defines `struct __xfsstats`, the canonical ordered counter layout used by stats formatting and offset-based updates.
- Counter groups cover:
  - allocation/free
  - allocation btree and block mapping
  - directory operations
  - transactions
  - inode cache activity
  - log activity
  - AIL pushing
  - reads/writes/xstrat
  - xattrs
  - inode clustering and inode lifecycle
  - buffer cache
  - v2 btree counters for allocation, bmap, inode, rmap, refcount, realtime, and in-memory btrees
  - quota manager counters
  - zoned GC counters
  - metafile inode count
  - 64-bit precision byte/relog counters.
- `xfsstats_offset(f)` converts a field offset to a 32-bit counter index.
- `struct xfsstats` overlays the named struct with a 32-bit array for offset-based updates.
- Declares `xfs_stats_format`, `xfs_stats_clearall`, and global `xfsstats`.
- Provides macros to increment, decrement, and add to both global and per-mount stats:
  - `XFS_STATS_INC`
  - `XFS_STATS_DEC`
  - `XFS_STATS_ADD`
  - `XFS_STATS_INC_OFF`
  - `XFS_STATS_DEC_OFF`
  - `XFS_STATS_ADD_OFF`
- Provides procfs init/cleanup declarations or no-op inline fallbacks depending on `CONFIG_PROC_FS`.

Important dependencies:
- Used by many XFS subsystems for cheap per-cpu accounting.
- `xfs_stats.c` depends on field ordering for text output.
- `xfs_sysfs.c` exposes these counters through sysfs.

Behavioral notes:
- The struct layout is effectively ABI-sensitive for the stats output format.
- `XFS_STATS_DEC_OFF` appears to evaluate the indexed counters without decrementing them; this is notable because the named-field decrement macro does decrement.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_stats.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_super.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_super.c

This is the Linux VFS superblock integration and module lifecycle implementation for XFS. It handles mount option parsing, device setup, mount fill, remount transitions, freeze/thaw, inode/super operations, workqueue and cache initialization, and filesystem registration.

Major responsibilities:
- Defines `xfs_super_operations`, `xfs_fs_type`, module init, and module exit.
- Parses mount options through the modern `fs_context` API.
- Opens and configures data, log, and realtime block devices.
- Allocates per-mount workqueues, per-cpu counters, inode GC state, stats, and scrub stats.
- Reads and validates the on-disk superblock before completing mount.
- Sets VFS superblock properties, root dentry, xattrs, export ops, quota ops, ACL flags, timestamp range, and filesystem limits.
- Implements sync, statfs, freeze, unfreeze, remount read-only/read-write, shrinker callbacks, forced shutdown, and filesystem error reporting.
- Creates and destroys global slab caches, global workqueues, procfs/sysctl/sysfs/debugfs state, quota manager state, and the XFS filesystem registration.

Mount option handling:
- Supports options for log sizing/devices, realtime device, inode32/inode64, allocation size, stripe geometry, group inheritance, sync semantics, discard, DAX, quota modes, filestreams, norecovery, zoned settings, lifetime hints, max atomic write size, and debug errortags.
- Deprecated options `attr2`, `noattr2`, `ikeep`, and `noikeep` are accepted but warn; removal is postponed to September 2030.
- DAX mode is represented as inode/always/never and stored in mount feature flags.
- Quota mount options are tracked with a high-bit sentinel `XFS_QFLAGS_MNTOPTS` so mount-time quota option presence can be distinguished from on-disk resumption.

Mount validation and setup:
- `xfs_fs_validate_params` rejects invalid norecovery read-write mounts, incompatible `noalign` with stripe geometry, quota options without quota support, malformed stripe geometry, invalid logbuf/logbsize values, and invalid allocsize.
- `xfs_finish_flags` validates log buffer constraints, read-only superblock restrictions, group+project quota compatibility, and zoned-only options.
- `xfs_open_devices` opens external log and realtime devices and prevents invalid device aliasing.
- `xfs_setup_devices` configures buffer targets and handles internal realtime device use.
- `xfs_fs_fill_super` performs the full mount sequence: copy VFS flags, validate options, set VFS operation tables, optional debug mount delay, open devices, create debugfs mount dir, initialize workqueues/counters/inodegc/stats/scrub stats, read superblock, validate features, configure devices, mount realtime and filestream state, set VFS block and timestamp properties, validate DAX/discard/zoned/reflink constraints, mount the filesystem, and instantiate the root dentry.

Feature and compatibility checks:
- Warns or rejects deprecated V4 filesystems depending on `CONFIG_XFS_SUPPORT_V4`.
- Warns or rejects ASCII case-insensitive filesystems depending on `CONFIG_XFS_SUPPORT_ASCII_CI`.
- Rejects filesystems marked `needsrepair` unless mounted with `norecovery`.
- Rejects in-progress offline filesystem operations.
- Rejects unsupported block sizes, oversized filesystems, and invalid maximum file offset assumptions.
- Enforces DAX requirements: DAX-capable devices, page-sized blocks, and no incompatible reflink multi-partition combination.
- Zoned filesystems require metadir and are marked experimental.
- Reflink is checked against realtime extent size and zoned realtime incompatibility.

VFS operations:
- `xfs_fs_alloc_inode` is a BUG trap because XFS manages inode allocation through its own cache.
- `xfs_fs_destroy_inode` marks XFS inodes reclaimable and updates inode destroy stats.
- `xfs_fs_drop_inode` protects inodes undergoing log recovery.
- `xfs_fs_evict_inode` handles final page truncation, DAX layout break, and zoned open-zone release.
- `xfs_fs_sync_fs` forces the log on wait syncs and stops inode/block/zone GC during freeze entry.
- `xfs_fs_freeze` saves reserve blocks, quiesces the log under `GFP_NOFS`, and restarts GC workers on failure.
- `xfs_fs_unfreeze` restores reservations, restarts log work, and restarts GC workers for writable mounts.
- `xfs_fs_statfs` reports data or realtime free space depending on inode flags and applies project quota statvfs when appropriate.
- Shrinker callbacks route cached inode counting/reclaim to XFS inode reclaim.
- `xfs_fs_report_error` forwards non-metadata inode I/O errors to health monitoring.

Remount behavior:
- `xfs_fs_reconfigure` parses into a temporary mount struct and applies limited mutable options.
- Supports inode32/inode64 transitions by recomputing per-AG inode allocation policy.
- Validates max atomic write option before applying.
- Read-only to read-write remount rejects read-only log/realtime devices, norecovery mounts, and unknown ro-compat features; then restores reservations, restarts log/blockgc/inodegc/zonegc, and reserves AG metadata blocks.
- Read-write to read-only remount syncs the filesystem, stops block GC, frees speculative/COW staging space, stops inodegc and zonegc, unreserves AG metadata blocks, saves reservation state, cleans the log, and marks the mount readonly.

Global initialization:
- `xfs_init_caches` creates all major XFS slab caches, including buffers, log tickets, btree cursors, deferred item caches, inode/log item caches, intent/done item caches, parent args, and related metadata item caches.
- `xfs_init_workqueues` creates global allocation and discard workqueues.
- `init_xfs_fs` validates on-disk structs, tests directory hash code, prints build options, starts directory support, initializes caches/workqueues/MRU/procfs/sysctl/debugfs/sysfs/global stats/scrub stats/debug kobject/quota, and registers the filesystem.
- `exit_xfs_fs` reverses module setup, unregisters XFS, tears down sysfs/debugfs/procfs/sysctl/caches/workqueues, and frees UUID table state.

Important dependencies:
- Uses nearly every core XFS subsystem: mount, inode cache, log, transactions, allocation, bmap, rmap, refcount, quota, realtime, zoned allocation, filestreams, sysfs, procfs stats, scrub stats, error tags, health monitoring, and parent pointers.
- Exports helpers declared in `xfs_super.h`: `xfs_flush_inodes`, `xfs_set_inode_alloc`, `xfs_reinit_percpu_counters`, `xfs_debugfs_mkdir`, and `xfs_discard_wq`.

Behavioral notes:
- The file is built around carefully ordered allocation and unwind paths; mount failure cleanup mirrors the successful setup sequence.
- Freeze/remount logic coordinates with inodegc, blockgc, zonegc, reservations, and log state to prevent reclaim or inactivation races.
- Option parsing accepts more options than remount can actually mutate; comments explicitly document the compatibility reason for this.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_super.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_super.h

This header exposes XFS superblock-facing helpers, build option strings, and selected globals.

Key points:
- Provides quota init/exit wrappers and `XFS_QUOTA_STRING` depending on `CONFIG_XFS_QUOTA`.
- Provides ACL string and `set_posix_acl_flag` wrapper depending on `CONFIG_XFS_POSIX_ACL`.
- Defines build option string fragments for security attributes, realtime, scrub, repair, verbose warnings, fatal asserts, and debug/no-debug.
- `XFS_VERSION_STRING` is `"SGI XFS"`.
- `XFS_BUILD_OPTIONS` concatenates enabled feature strings for module logging and metadata.
- `XFS_WQFLAGS` adds `WQ_SYSFS` to workqueues in debug builds.
- Forward declares core XFS/VFS types.
- Declares:
  - `xfs_flush_inodes`
  - `xfs_set_inode_alloc`
  - export and quota operation tables
  - `xfs_reinit_percpu_counters`
  - global `xfs_discard_wq`
  - `xfs_debugfs_mkdir`
- Defines `XFS_M(sb)` to recover `struct xfs_mount *` from `sb->s_fs_info`.

Important dependencies:
- Consumed by mount/superblock code and other subsystems needing mount-level helpers.
- Build option strings are used by `xfs_super.c` module init and module metadata.

Behavioral notes:
- This file is mostly compile-time feature plumbing around `CONFIG_XFS_*` options.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_super.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_symlink.c

This file implements XFS symlink read, create, and inactive-time cleanup paths.

Key points:
- `xfs_readlink`:
  - Rejects shutdown filesystems and zapped data forks.
  - Locks the inode shared.
  - Validates symlink length is nonzero and no larger than `XFS_SYMLINK_MAXLEN`.
  - Reads inline symlink data directly from the local data fork.
  - Reads remote symlink data through `xfs_symlink_remote_read`.
  - Marks the inode symlink health sick and returns `-EFSCORRUPTED` on corrupt state.
- `xfs_symlink`:
  - Validates target path length.
  - Allocates quota dquots for the new inode.
  - Computes whether the symlink can fit inline or needs remote blocks, with parent pointer support affecting reservation needs.
  - Starts parent pointer update state.
  - Allocates an inode creation transaction.
  - Locks the parent directory and checks `XFS_DIFLAG_NOSYMLINKS`.
  - Allocates and creates the symlink inode.
  - Joins the parent directory to the transaction after inode allocation because allocation may commit/restart.
  - Attaches dquots, writes the symlink target, updates VFS inode size, creates the directory entry, marks sync if needed, and commits.
  - On error, cancels transaction, finishes/reclaims partially created inode, finishes parent pointer state, releases dquots, and unlocks the parent if needed.
- `xfs_inactive_symlink_rmt`:
  - Handles deletion of remote symlink blocks during inode inactivation.
  - Converts the inode to zero-size regular-file mode before truncation so zero-length symlink state is not written back.
  - Calls `xfs_symlink_remote_truncate`, commits, clears in-memory extent descriptions, and unlocks.
- `xfs_inactive_symlink`:
  - Validates symlink length during inactive cleanup.
  - Does nothing for inline symlinks because `xfs_difree` removes inline fork state.
  - Dispatches remote symlink cleanup to `xfs_inactive_symlink_rmt`.

Important dependencies:
- Directory creation and parent pointer helpers: `xfs_dir_create_child`, `xfs_parent_start`, `xfs_parent_finish`.
- Transaction and inode creation helpers: `xfs_trans_alloc_icreate`, `xfs_dialloc`, `xfs_icreate`.
- Quota helpers: `xfs_icreate_dqalloc`, `xfs_qm_vop_create_dqattach`, `xfs_qm_dqrele`.
- Remote symlink storage helpers from `xfs_symlink_remote`.
- Health reporting through `xfs_inode_mark_sick`.

Behavioral notes:
- The create path carefully handles transaction restarts and lock ownership changes.
- Symlink corruption is treated as inode health damage, not just a failed read.
- Parent pointer support can force block reservation even for otherwise inline-sized symlink targets.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_symlink.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_symlink.h

This header declares kernel-only XFS symlink operations.

Exports:
- `xfs_symlink(struct mnt_idmap *idmap, struct xfs_inode *dp, struct xfs_name *link_name, const char *target_path, umode_t mode, struct xfs_inode **ipp)`
- `xfs_readlink(struct xfs_inode *ip, char *link)`
- `xfs_inactive_symlink(struct xfs_inode *ip)`

Important dependencies:
- Implemented by `xfs_symlink.c`.
- Called from VFS inode operations in `xfs_iops.c` and inactive inode handling in `xfs_inode.c`.

Behavioral notes:
- This header intentionally contains only the small symlink API surface; remote symlink internals are separated elsewhere.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_symlink.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_sysctl.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_sysctl.c

This file registers XFS sysctl tunables under `fs/xfs`.

Key points:
- Maintains a static `ctl_table_header *xfs_table_header`.
- With `CONFIG_PROC_FS`, defines:
  - `xfs_stats_clear_proc_handler`, which clears global XFS stats when `stats_clear` is written nonzero, then resets the knob to zero.
  - `xfs_panic_mask_proc_handler`, which updates `xfs_panic_mask` and forces additional panic tags in debug builds.
- Defines a deprecated sysctl helper that warns on writes, though it is not used by the active table in this file.
- `xfs_table` exposes tunables:
  - `panic_mask`
  - `error_level`
  - `xfssyncd_centisecs`
  - `inherit_sync`
  - `inherit_nodump`
  - `inherit_noatime`
  - `inherit_nosymlinks`
  - `rotorstep`
  - `inherit_nodefrag`
  - `filestream_centisecs`
  - `speculative_prealloc_lifetime`
  - `stats_clear` when procfs is enabled.
- All table entries use min/max bounds from `xfs_params`.
- `xfs_sysctl_register` registers the table at `fs/xfs`.
- `xfs_sysctl_unregister` unregisters it.

Important dependencies:
- Tunable storage and min/max bounds are declared in `xfs_sysctl.h` and defined in `xfs_globals.c`.
- `xfs_stats_clearall` and global `xfsstats` come from stats code.
- Module lifecycle is driven by `xfs_super.c`.

Behavioral notes:
- Sysctl support itself depends on `CONFIG_SYSCTL` through header-level fallback wrappers.
- The stats clear sysctl clears only global stats, not per-mount stats.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_sysctl.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_sysctl.h

This header defines XFS sysctl tunable structures, sysctl IDs, and global debug/tuning state declarations.

Key points:
- `xfs_sysctl_val_t` stores a min/current/max integer triplet.
- `xfs_param_t` groups tunable sysctl values:
  - panic mask
  - error reporting level
  - sync timer
  - stats clear
  - inherited inode flags
  - inode32 rotor step
  - filestream timeout
  - block GC/speculative preallocation lifetime.
- Documents `xfs_error_level` behavior:
  - `0`: no reports
  - `1`: report shutdown-causing corruption
  - `5`: report all known `EFSCORRUPTED` events
  - panic mask bit `0x8` turns reports into panics.
- Defines legacy sysctl numeric IDs for exposed and removed XFS controls.
- Declares global `xfs_params`.
- Defines `struct xfs_globals`, including debug-only knobs:
  - `pwork_threads`
  - `larp`
  and always-present knobs:
  - bulk load slack values
  - log recovery delay
  - mount delay
  - assert BUG behavior
  - always-COW debug behavior.
- Declares global `xfs_globals`.
- Provides `xfs_sysctl_register` and `xfs_sysctl_unregister`, or no-op fallbacks without `CONFIG_SYSCTL`.

Important dependencies:
- Values are defined in `xfs_globals.c`.
- Sysctl table implementation is in `xfs_sysctl.c`.
- Global knobs are surfaced through sysfs in `xfs_sysfs.c` and consumed by mount, recovery, message/assert, pwork, xattr, and scrub code.

Behavioral notes:
- This header separates persistent sysctl-style tunables from debug/global state used through sysfs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_sysctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_sysfs.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_sysfs.c

This file implements XFS sysfs object types and attributes for global stats/debug state, per-mount stats, log state, metadata I/O error retry policy, and zoned filesystem controls.

Core sysfs framework:
- Defines `struct xfs_sysfs_attr`, wrapping `struct attribute` with XFS-specific show/store callbacks.
- Defines generic show/store dispatch through `xfs_sysfs_ops`.
- Defines an empty per-mount kobject type `xfs_mp_ktype`.
- Uses helper macros for read-write, read-only, and write-only attributes.

Debug sysfs attributes:
- Present only under `DEBUG`.
- Exposes:
  - `bug_on_assert`
  - `log_recovery_delay`
  - `mount_delay`
  - `always_cow`
  - `pwork_threads`
  - `larp`
  - `bload_leaf_slack`
  - `bload_node_slack`
- These manipulate `xfs_globals`.
- Numeric delay values are limited to 0-60 seconds.
- `pwork_threads` accepts `-1` through `num_possible_cpus()`.

Stats sysfs attributes:
- Converts a kobject to `struct xstats`.
- `stats` is read-only and emits `xfs_stats_format`.
- `stats_clear` is write-only and accepts only `1`, then calls `xfs_stats_clearall`.
- `xfs_stats_ktype` is used for both global and per-mount stats objects.

Log sysfs attributes:
- Converts a kobject to `struct xlog`.
- Exposes:
  - `log_head_lsn`
  - `log_tail_lsn`
  - `reserve_grant_head_bytes`
  - `write_grant_head_bytes`
- Uses log lock or atomic reads as needed.

Metadata I/O error policy:
- Creates hierarchy shaped like `.../xfs/<dev>/error/<class>/<errno>/`.
- Per-error attributes:
  - `max_retries`
  - `retry_timeout_seconds`
- `-1` means retry forever.
- Retry timeout is capped at one day.
- `fail_at_unmount` is a mount-level error attribute for testing unmount failure behavior.
- Metadata defaults:
  - `default`, `EIO`, and `ENOSPC` retry forever.
  - `ENODEV` has zero retries and timeout because disappearing devices are unrecoverable.
- `xfs_error_get_cfg` maps runtime errors to configured policy entries for `EIO`, `ENOSPC`, `ENODEV`, or default.

Zoned sysfs attributes:
- Present for zoned realtime filesystems when `CONFIG_XFS_RT` is enabled and the mount has zoned support.
- Exposes:
  - `max_open_zones`, excluding GC-reserved open zones from the reported value.
  - `nr_open_zones`
  - `zonegc_low_space`
- Changing `zonegc_low_space` wakes zone GC.

Per-mount sysfs lifecycle:
- `xfs_mount_sysfs_init` creates:
  - `.../xfs/<dev>/`
  - `stats`
  - `error`
  - `error/fail_at_unmount`
  - `error/metadata/*`
  - optional `zoned`
- `xfs_mount_sysfs_del` removes optional zoned state, all error config kobjects, metadata/error dirs, stats, and mount kobject.

Important dependencies:
- Uses `xfs_sysfs.h` for kobject lifecycle helpers.
- Uses stats formatting from `xfs_stats.c`.
- Uses mount/log/error/zoned structures from XFS core headers.
- Per-mount lifecycle is invoked from `xfs_mount.c`; global stats/debug kobjects are initialized in `xfs_super.c`.

Behavioral notes:
- Sysfs deletion waits for release completion through `xfs_sysfs_del`, which prevents freeing containing structures before kobject teardown finishes.
- Error retry policy is mutable at runtime and read by metadata I/O error handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_sysfs.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_sysfs.h

This header declares XFS sysfs kobject types and provides small lifecycle helpers.

Key points:
- Declares exported kobject types:
  - `xfs_dbg_ktype`
  - `xfs_log_ktype`
  - `xfs_stats_ktype`
- `to_kobj` converts a Linux `struct kobject` to containing `struct xfs_kobj`.
- `xfs_sysfs_release` completes the embedded completion when a kobject is released.
- `xfs_sysfs_init` initializes completion state and calls `kobject_init_and_add`, with optional XFS parent kobject.
- On add failure, it drops the kobject reference with `kobject_put`.
- `xfs_sysfs_del` removes and drops the kobject, then waits for release completion.
- Declares per-mount sysfs lifecycle:
  - `xfs_mount_sysfs_init`
  - `xfs_mount_sysfs_del`

Important dependencies:
- Implemented by `xfs_sysfs.c`.
- Requires containers embedding `struct xfs_kobj` to remain valid until release completion.

Behavioral notes:
- The explicit completion wait is important because XFS embeds kobjects inside larger filesystem-owned structures.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_trace.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_trace.c

This file instantiates XFS tracepoints.

Key points:
- Includes a broad set of XFS headers so trace event helpers and structure definitions are available.
- Includes Linux `iomap` and filesystem error headers for tracepoint coverage involving iomap and error reporting.
- Defines `CREATE_TRACE_POINTS` before including `xfs_trace.h`, causing the tracepoint definitions declared in that header to be emitted exactly once.

Important dependencies:
- `xfs_trace.h` contains the actual trace event definitions.
- Many XFS files call tracepoints declared there; this compilation unit provides their storage/implementation.

Behavioral notes:
- This file intentionally contains no runtime logic beyond tracepoint instantiation.
- The comment notes `xfs_trace.h` is included last so helper definitions from prior headers are available to trace event implementations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_trace.c -->