# sources/control-plane/longhorn-engine/integration/data/snapshot_tree.py

## Purpose
Builds and verifies a branching snapshot tree used by data and backup tests to validate snapshot relationships and data restoration across branches.

## Important APIs, Types, and Functions
- `snapshot_tree_build()` creates a fixed branching topology with snapshots `0a` through `3c`.
- `snapshot_tree_create_node()` writes data and creates a snapshot.
- `snapshot_tree_verify()`, `snapshot_tree_verify_relationship()`, `snapshot_tree_verify_data()`, `snapshot_tree_verify_node()`.
- `snapshot_tree_verify_backup_node()` restores a backup and checks data for a named node.

## Control Flow
The builder writes data and snapshots along one branch, reverts to earlier snapshots to create side branches, then verifies relationships and data. Strict verification checks exact node count, head parent/children, and snapshot ls output. Data verification repeatedly reverts to each snapshot and checks block contents.

## State and Persistence Behavior
Mutates volume block data, creates snapshots, reverts frontend state, and in backup verification resets volumes and restores backups. It relies on persisted snapshot metadata and data contents.

## Dependencies and Integration Points
Uses `common.cmd` CLI wrappers and `common.core` data/restore/reset helpers. Consumed by `integration/data/test_backup.py`.

## Risks and Edge Cases
Strict relationship assertions encode exact pruning/list behavior. Repeated reverts require frontend shutdown/start by helper. Data offset/length must remain within page and volume constraints.

## Test Signals
Provides high-value signal for branchy snapshot lineage, snapshot listing after reverts, and backup restore correctness for non-linear snapshot histories.
