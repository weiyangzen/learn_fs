# sources/control-plane/longhorn-engine/integration/data/test_snapshot.py

## Purpose
This module exercises Longhorn snapshot lifecycle semantics: create, list, revert, remove, purge/coalesce, tree branching, backing-file snapshots, expansion across snapshots, mounted filesystem freezing, snapshot pruning, and filesystem trim/unmap behavior.

## Important APIs, types, and functions
- Test entry points: `test_snapshot_revert`, `test_snapshot_rm_basic`, `test_snapshot_revert_with_backing_file`, `test_snapshot_rm_rolling`, `test_snapshot_tree_basic`, expansion tests with/without backing file, `test_snapshot_mounted_filesystem`, `test_snapshot_prune`, `test_snapshot_prune_with_coalesce`, and `test_snapshot_trim_filesystem`.
- Helpers: `snapshot_revert_test`, `volume_expansion_with_snapshots_test`, `snapshot_mounted_filesystem_test`, `filesystem_trim_test`, and `wait_for_snap_size_no_less_than_value`.
- Uses `Snapshot`/`Data` helper objects for writing data, snapshot creation, checksum verification, and refuting data after revert.
- Uses `common.cmd` snapshot commands and controller feature toggles such as `set_unmap_mark_snap_chain_removed`.
- Filesystem-level helpers manage host namespace mount, mkfs, sync, fstrim, checksum, and process log reading.

## Control flow
Snapshot revert tests build ordered snapshots with random data, revert to earlier points, and assert later snapshot data disappears while earlier data remains. Removal/purge tests mark snapshots removed, wait for purge, and verify snapshot-info tree shape and data preservation. Tree tests build a branchy snapshot graph, revert to a node, remove many branches, purge, then verify surviving nodes and rejection when reverting to a removed snapshot.

Expansion tests create snapshots before and after expanding the volume, write into the expanded region, revert to a pre-expansion snapshot, continue writing to expanded space, and purge a snapshot that coalesces with a larger successor.

Mounted filesystem tests create and mount ext4 on the Longhorn block device from the host namespace, take snapshots with the `freeze` flag, inspect engine logs for freeze/unfreeze messages, then revert snapshots and remount to validate file presence/content. Trim tests build branch snapshots with mounted filesystem files, delete files, run `fstrim`, verify only head size shrinks first, enable unmap marking, retrim, and then verify deeper snapshots are marked removed and shrunk while branch data remains restorable.

## State and persistence behavior
The module validates snapshot metadata (`parent`, `children`, `removed`, `usercreated`, `size`), volume-head parentage, branch snapshots, backing-file initial content, device bytes and checksums, engine process logs, mounted filesystem files, snapshot sizes after trim/prune, and feature toggle state for unmap behavior. It uses explicit mount/unmount around frontend shutdown/revert because reverts detach the device.

## Dependencies and integration points
Dependencies include controller/replica fixtures, backing-file fixtures, snapshot tree helpers, host namespace access via `nsenter`, ext4 tooling, `mount`, `umount`, `findmnt`, `fstrim`, engine process logs, and Longhorn snapshot CLI commands. It integrates engine snapshot APIs, frontend lifecycle, filesystem freeze hooks, Linux discard/unmap behavior, and backing-image read paths.

## Risks and edge cases
- Timing-sensitive size checks rely on polling and minimum thresholds because filesystem allocation is not exact.
- Mounted filesystem tests depend on `/host/tmp` bind-mount conventions and privileged host namespace operations.
- Log-count assertions require exactly three freeze and unfreeze log entries; unrelated logging or retries can break the signal.
- Snapshot pruning checks encode exact size deltas such as 4096 bytes and depend on filesystem block size.
- Trim behavior is only run for ext4 because the default test volume size is too small for xfs.
- The module uses exact tree-shape assumptions that will catch legitimate metadata model changes.

## Test signals
Signals include correct snapshot lists/info maps, successful and failed reverts, retained data after purge/coalesce, expected `removed` flags, size reduction after prune/trim, zeroed expanded regions, freeze/unfreeze log counts, filesystem checksum matches after revert, and preserved branch snapshot content after unmap-trim removal.
