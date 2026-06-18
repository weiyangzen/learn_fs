# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_status.c

This file computes high-level pool health/status classifications for `zpool status` and pool import reporting. It maps detailed pool/vdev configuration state into `ZPOOL_STATUS_*` values and optional FMA-style message ids.

Primary responsibilities:
- Inspect active or import-time pool configuration nvlists.
- Detect resilvering, rebuilding, rebuild-needs-scrub, hostid/MMP conflicts, unsupported versions/features, suspended I/O, bad logs, corrupt metadata, missing/faulted devices, failing devices, offline/removed devices, non-native ashift, errata, legacy versions, disabled features, and compatibility mismatches.
- Map selected statuses to stable `ZFS-8000-*` message ids.

Important data:
- `zfs_msgid_table[]` maps early `ZPOOL_STATUS_*` enum values to message ids. Later informational/status values intentionally have no message id.
- `NMSGID` is the table size guard.

Vdev predicate helpers:
- `vdev_missing()` detects `VDEV_STATE_CANT_OPEN` plus `VDEV_AUX_OPEN_FAILED`.
- `vdev_faulted()` detects `VDEV_STATE_FAULTED`.
- `vdev_errors()` detects degraded state or nonzero read/write/checksum errors.
- `vdev_broken()` detects `VDEV_STATE_CANT_OPEN`.
- `vdev_offlined()` detects `VDEV_STATE_OFFLINE`.
- `vdev_removed()` detects `VDEV_STATE_REMOVED`.
- `vdev_non_native_ashift()` detects configured ashift below physical ashift, with optional pool ashift filtering.

Traversal:
- `find_vdev_problem()` recursively walks the vdev tree and optional L2 cache devices, applying a predicate to leaves.
- It can ignore children under replacing vdevs.
- It has dRAID failure-domain awareness: if all members of a dRAID failure group are problematic, it returns `EDOM`; otherwise leaf problems return `ENXIO`.

Status algorithm:
- `check_status()` performs ordered checks from most severe or most actionable to least:
  - active resilvering
  - active rebuild or rebuild completed after last scrub
  - multihost/MMP active/hostid-required/hostid-mismatch cases
  - pool last accessed by another host
  - newer on-disk version
  - unsupported features, read-only vs unreadable
  - bad GUID sum
  - suspended I/O and MMP suspend reason
  - bad log
  - non-replicated missing/faulted/corrupt-label devices
  - corrupt pool metadata
  - persistent data errors
  - replicated missing/faulted/corrupt-label devices, including dRAID fault domains
  - failing devices
  - offline devices
  - removed devices
  - non-native ashift, unless disabled via `ZPOOL_STATUS_NON_NATIVE_ASHIFT_IGNORE`
  - pool errata
  - older but supported pool version
  - feature compatibility and disabled/superfluous feature checks
  - otherwise `ZPOOL_STATUS_OK`

Public entry points:
- `zpool_get_status()` gets pool compatibility and ashift properties from a live `zpool_handle_t`, calls `check_status()`, and returns optional msgid.
- `zpool_import_status()` runs the same status logic for import configs and returns optional msgid.

Important behavior:
- Import checks skip persistent data error and failing-device checks that depend on live pool state.
- Compatibility logic calls `zpool_load_compat()` and compares enabled features against requested compatibility feature sets.
- The `"legacy"` compatibility value suppresses old-version reporting.
- Feature checks skip unsupported-by-module and no-upgrade feature entries.

Dependencies:
- Pool/vdev config nvlist keys from OpenZFS.
- `zfeature_common.h` and `spa_feature_table`.
- `libzutil` and `libzfs_impl.h`.
- System hostid through `get_system_hostid()`.

Research relevance:
- This file is the policy layer that turns raw COW pool topology and scan/device state into user-visible health statuses.
- The ordering in `check_status()` is significant because only one status is returned even when multiple issues are present.
