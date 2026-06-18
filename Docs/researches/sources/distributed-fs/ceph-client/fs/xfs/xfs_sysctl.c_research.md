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
