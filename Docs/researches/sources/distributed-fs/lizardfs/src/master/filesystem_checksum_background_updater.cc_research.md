# sources/distributed-fs/lizardfs/src/master/filesystem_checksum_background_updater.cc

## Purpose
`filesystem_checksum_background_updater.cc` implements the state machine used to recalculate metadata checksums incrementally in the event loop without blocking the master for a full scan.

## Important APIs and control flow
`ChecksumBackgroundUpdater::start()` moves the updater from `kNone` to the first recalculation step and rejects duplicate starts. `end()` compares newly calculated node and xattr checksums with global metadata values, replaces globals on mismatch, resets state, and logs completion. `inProgress`, `getStep`, `incStep`, `getPosition`, and `incPosition` expose the cursor used by `fs_background_checksum_recalculation_a_bit`. `isNodeIncluded` and `isXattrIncluded` decide whether a live mutation must also update the background aggregate by comparing the current step and hash-bucket position. `setSpeedLimit` and `getSpeedLimit` control how much work each event-loop slice performs. `reset()` returns to `kNone`, position zero, and checksum seeds.

## State behavior
The updater stores `step_`, `position_`, `speedLimit_`, and separate aggregate `fsNodesChecksum` and `xattrChecksum`. During node or xattr mutation, callers remove/add the old and new contributions from the background aggregate only if the object has already been scanned by this run. This prevents live mutations from being lost while the recalculation cursor is moving through hash buckets.

## Dependencies and integration points
The class integrates with `filesystem_checksum`, `filesystem_periodic`, global `gMetadata`, xattr hash functions, and logging. It is kicked off by `fs_start_checksum_recalculation` and advanced by the periodic each-loop callback.

## Risks and test signals
The cursor logic is subtle: off-by-one bucket inclusion or step transition mistakes can produce self-healing checksum replacements that hide real mutation-order bugs. Tests should start recalculation, mutate nodes before and after the current bucket, mutate xattrs before and after their hash bucket, and verify the final checksum equals a forced recalculation. Also test duplicate `start()` returns false and `end()` resets all state.
