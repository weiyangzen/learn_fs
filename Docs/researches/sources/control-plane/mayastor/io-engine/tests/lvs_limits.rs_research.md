# sources/control-plane/mayastor/io-engine/tests/lvs_limits.rs

Purpose: verifies LVS metadata exhaustion is reported as `BsError::OutOfMetadata` while creating many replicas and snapshots.

Important APIs/types/functions: uses `Lvs::create_or_import`, `create_lvol`, `prepare_snap_config`, `create_snapshot`, and matches `LvsError::RepCreate`/`SnapshotCreate` source errors.

Control flow: prepares a 10 GB AIO disk, creates a pool, loops up to 100 replicas and 100 snapshots each, breaks when replica or snapshot creation returns `OutOfMetadata`, and panics on any other error.

State and persistence: LVS metadata on `/tmp/disk0.img`; volume names/UUIDs are deterministic.

Dependencies and integration points: LVS allocator/metadata space accounting, snapshot creation path, AIO bdev.

Risks and edge cases: if disk metadata sizing changes enough to avoid exhaustion within loop bounds, the test may pass without proving the limit. It does not assert that exhaustion definitely occurred, only validates error type when it does.

Test signals: focused guard that metadata-full conditions map to the intended error class.
