# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_debugfs.c

## Purpose

`drbd_debugfs.c` implements DRBD's debugfs diagnostics. It creates a `/sys/kernel/debug/drbd` tree with version information, resource directories, connection diagnostics, volume diagnostics, minor symlinks, request summaries, metadata/bitmap I/O visibility, activity-log and resync cache dumps, generation IDs, and callback history.

The file is observational. It should not change DRBD replication state, but it must safely traverse live DRBD structures while resources, connections, devices, and peer devices may be removed.

## Important APIs, Types, and Data

- Global dentries: `drbd_debugfs_root`, `drbd_debugfs_version`, `drbd_debugfs_resources`, and `drbd_debugfs_minors`.
- Add/cleanup APIs: `drbd_debugfs_init()`, `drbd_debugfs_cleanup()`, `drbd_debugfs_resource_add/cleanup()`, `drbd_debugfs_connection_add/cleanup()`, `drbd_debugfs_device_add/cleanup()`, and `drbd_debugfs_peer_device_add/cleanup()`.
- `drbd_single_open()` wraps `single_open()` with dentry positivity and kref acquisition to prevent object teardown while a debugfs file is open.
- Show functions include `in_flight_summary_show()`, `callback_history_show()`, `connection_oldest_requests_show()`, device `oldest_requests`, `act_log_extents`, `resync_extents`, `data_gen_id`, `ed_gen_id`, and `drbd_version_show()`.
- Request printing helpers decode `enum drbd_req_state_bits` and peer request flags into tabular seq_file output.

## Control Flow

Module/debugfs setup calls `drbd_debugfs_init()`, which creates root `drbd`, `version`, `resources`, and `minors` entries. Cleanup removes these in reverse-ish dependency order through `drbd_debugfs_remove()`, which nulls dentry pointers after `debugfs_remove()`.

When a resource is added, `drbd_debugfs_resource_add()` creates `/resources/<resource>`, `volumes`, `connections`, and `in_flight_summary`. The summary file prints oldest bitmap I/O, metadata I/O, socket buffer stats, oldest peer requests, application requests waiting for the AL, and transfer-log summary.

Connection add creates a current `peer` directory under the resource connection directory, plus `callback_history` and `oldest_requests`. The callback file prints worker/receiver callback timing history; oldest requests prints the connection's selected request pointers under `req_lock`.

Device add creates a volume directory by vnr, a minor-number symlink under `/minors`, and diagnostic files for oldest requests, AL extents, resync extents, data generation IDs, and exposed data UUID. Device cleanup removes each dentry pointer.

Peer-device add currently creates a vnr directory below the connection directory; cleanup removes it.

Every state-reading file uses seq_file. Many show functions take snapshots under `req_lock`, RCU, or object-specific locks, then format ages relative to `jiffies`. Long transfer-log scans periodically drop and reacquire `req_lock` to avoid holding interrupts disabled for too long.

## State and Persistence Behavior

The debugfs hierarchy mirrors runtime DRBD object state and disappears at cleanup/unmount/module unload. It does not persist data. The diagnostic content is a point-in-time or best-effort snapshot and can be stale immediately after reading.

The file intentionally includes format version markers (`v: 0`) in several outputs. Comments instruct maintainers to bump versions if output format changes.

## Dependencies and Integration Points

- Requires `CONFIG_DEBUG_FS`; otherwise `drbd_debugfs.h` stubs these calls.
- Uses DRBD core resource, connection, device, peer-device, request, peer-request, bitmap I/O, activity-log, resync, UUID, and version structures.
- Uses `seq_file`, debugfs, kref, RCU, spinlocks, jiffies, TCP socket internals, and LRU cache dump helpers.
- Integrates with object lifecycle via krefs and cleanup hooks from DRBD resource/connection/device management.

## Risks and Edge Cases

- Debugfs files are read concurrently with object removal. `drbd_single_open()` mitigates this with parent inode locking, dentry positivity checks, and `kref_get_unless_zero()`.
- Some diagnostic reads are intentionally racy and copy fields without full locking, such as metadata I/O snapshots and callback timing details.
- `in_flight_summary_show()` assumes the first connection and uses TCP internals when a socket exists; future multi-peer behavior may require directory naming and iteration changes.
- Long transfer-log scans drop `req_lock` and use request krefs to avoid holding the lock too long; mistakes in list continuation can skip or duplicate entries under churn.
- Debugfs creation failures are mostly tolerated by storing dentries and continuing, but later code must handle null or error dentries.

## Test Signals

- Build with `CONFIG_DEBUG_FS=y` and confirm expected debugfs tree appears for resources, connections, devices, peer devices, and minors.
- Build with `CONFIG_DEBUG_FS=n` and confirm callers compile against stubs.
- Open debugfs files while concurrently deleting DRBD resources/devices to validate kref lifetime handling.
- Exercise active application I/O, peer I/O, bitmap I/O, metadata I/O, AL waits, and resync; confirm summaries expose plausible entries.
- Format-version regression tests for scripts that consume debugfs outputs.
- Lockdep/KASAN tests for request-list traversal and cleanup races.
