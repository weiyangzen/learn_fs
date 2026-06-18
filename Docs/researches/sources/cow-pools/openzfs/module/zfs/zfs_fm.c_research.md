# File Research: sources/cow-pools/openzfs/module/zfs/zfs_fm.c

## Summary
Implements ZFS fault-management ereport and resource-event generation, duplicate suppression, rate limiting, checksum-error annotation, and ereport lifecycle management.

## Main Responsibilities
- Builds ZFS FMA ereports for pool, vdev, I/O, data, device, and checksum events.
- Selects ENA values to correlate related load or logical I/O failures.
- Suppresses duplicate recent IO/data/checksum ereports.
- Rate-limits delay, deadman, and checksum events.
- Annotates checksum ereports with changed byte ranges and bit counts.
- Posts resource events for remove, autoreplace, state change, snapshots, and zvol events.
- Initializes and tears down recent-event tracking.

## Key APIs
- `zfs_ereport_post()`
- `zfs_ereport_start_checksum()`
- `zfs_ereport_finish_checksum()`
- `zfs_ereport_free_checksum()`
- `zfs_ereport_post_checksum()`
- `zfs_event_create()`
- `zfs_post_remove()`, `zfs_post_autoreplace()`, `zfs_post_state_change()`
- `zfs_ereport_init()`, `zfs_ereport_taskq_fini()`, `zfs_ereport_fini()`
- `zfs_ereport_clear()`, `zfs_ereport_is_valid()`

## Important Behavior
`zfs_ereport_start()` constructs the class, detector FMRI, common pool payload, failmode, vdev payload, parent/spare info, ZIO details, logical bookmark fields, and tuning thresholds inherited from vdev properties.

Duplicate detection stores recent event keys in both an AVL tree and a time-ordered list. Duplicates refresh their timestamp and return `EALREADY`; old entries are purged by a delayed task.

Checksum annotation compares good and bad ABD buffers, summarizes changed ranges, counts set/cleared bits, optionally embeds exact bitmasks for small corruptions, and can drop events when buffers are identical.

## State and Synchronization
Ereport construction serializes through `spa_errlist_lock`. Duplicate tracking uses `recent_events_lock`, `recent_events_tree`, `recent_events_list`, and a delayed cleaner task. Checksum reports can be attached to a logical ZIO and finished later.

## Risks
Duplicate suppression and rate limiting intentionally drop events, so diagnostics depend on retention knobs and vdev rate-limit state. Checksum annotation borrows full buffers and can allocate per-report state. Event validity filters out recovery, tryimport, inaccessible vdevs, DTL checksum reads, and bogus delay events.
