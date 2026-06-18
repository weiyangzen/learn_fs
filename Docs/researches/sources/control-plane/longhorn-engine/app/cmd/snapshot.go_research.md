# sources/control-plane/longhorn-engine/app/cmd/snapshot.go

## Purpose
Defines the `snapshot`/`snapshots` CLI group for snapshot create, revert, list, remove, purge, info, clone, clone status, hash, hash cancel, and hash status operations.

## Important APIs, Types, and Functions
- `SnapshotCmd()` and subcommand constructors.
- `createSnapshot()`, `revertSnapshot()`, `rmSnapshot()`, `purgeSnapshot()`, `purgeSnapshotStatus()`.
- `lsSnapshot()` computes common snapshots across RW replicas.
- `infoSnapshot()` uses `sync.GetSnapshotsInfo`.
- `cloneSnapshot()` and `cloneSnapshotStatus()` use controller clients and sync clone helpers.
- `hashSnapshot()`, `cancelHashSnapshot()`, `hashSnapshotStatus()` use `sync.Task`.

## Control Flow
Command constructors bind actions to helper functions. Controller-client operations are used for create/revert/list/info/clone status, while multi-replica asynchronous work such as delete, purge, hash, and restore-style task operations go through `sync.NewTask`. Snapshot listing reads controller replicas, filters to RW replicas, intersects chains across replicas, strips `volume-snap-` and `.img`, and prints IDs newest-first. Clone requires source controller address and snapshot name, builds a second controller client, and delegates to `sync.CloneSnapshot`.

## State and Persistence Behavior
Mutates replica snapshot chains and metadata through controller/sync APIs. Delete marks or removes snapshots depending on chain relationships; purge coalesces removed snapshots. Clone/hashing create long-running state tracked by status maps. Revert requires frontend shutdown at higher levels/tests and changes the active head/parent chain.

## Dependencies and Integration Points
Depends on controller client, `pkg/sync`, `pkg/types`, `pkg/util`, and `go-common-libs/utils.Contains`. Reuses `getChain` from `ls_replica.go`. Extensively exercised by integration helpers and data snapshot-tree tests.

## Risks and Edge Cases
`revertSnapshot` explicitly handles no args and empty arg to avoid panic. `lsSnapshot` only shows snapshots common to all RW replicas; divergent chains or no prepared head can hide snapshots. Clone involves two controller identities and timeouts. Hash status requires snapshot arg and returns JSON. Delete loops over args and returns only the last error while reporting individual failures to stderr.

## Test Signals
`snapshot_test.go` unit-tests revert argument validation. `integration/core/test_cli.py` covers create, default list action, ls, info, rm, rm-empty, purge, purge head-parent limitation, expansion-created snapshots, restart/salvage scenarios. `integration/data/snapshot_tree.py` and `test_backup.py` validate branching snapshot relationships and backup restores from tree nodes.
