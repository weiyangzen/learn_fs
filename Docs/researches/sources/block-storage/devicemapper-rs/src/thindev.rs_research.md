# File Research: sources/block-storage/devicemapper-rs/src/thindev.rs

## Purpose
Implements high-level `dm-thin` device wrapper, status parsing, snapshot creation, table changes, and destruction of thin IDs from a thin pool.

## Key Types
`ThinTargetParams`, `ThinDevTargetTable`, `ThinDev`, `ThinDevWorkingStatus`, and `ThinStatus`.

## Behavior
Target params parse `thin <pool> <thin_id> [external_origin]`. `ThinDev::new` sends `create_thin` to the pool, rejects pre-existing names, creates a one-line thin table, and activates it. `setup` validates or creates a device for an already-known thin ID. `snapshot` suspends source, sends `create_snap`, resumes source, and creates a new thin device with the snapshot ID. `destroy` removes the DM device and sends `delete <thin_id>` to the pool.

## Status
`ThinStatus` handles `Error`, `Fail`, or working status with mapped sector count and optional highest mapped sector; zero mapped sectors means no highest sector.

## Tests/Notes
Loopback/XFS tests cover zero-size failure, setup without prior pool ID failure, basic idempotency, udev symlinks, snapshots, filesystem writes increasing pool usage, snapshot copy-on-write usage, and destroy semantics.
