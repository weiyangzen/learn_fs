# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/pruner_test.go

## Purpose
This file tests crash pruner CronJob creation.

## Important APIs, Types, And Functions
`TestCreateOrUpdateCephCron` calls `r.createOrUpdateCephCron(cephCluster, tolerations)` and then fetches the `rook-ceph-crashcollector-pruner` CronJob from a fake controller-runtime client.

## Control Flow And State
The test creates a CephCluster with placement tolerations, a fake scheme/client with batch/v1 registered, and a `ReconcileNode`. It verifies the operation result is `created` and that the CronJob pod template carries the expected tolerations.

## Dependencies And Integration Points
The test depends on Kubernetes batch/v1 CronJob types, Rook fake clients, controller-runtime fake client, and node-daemon pruner code. It validates the object creation path, not the higher-level `reconcileCrashPruner()` decision logic.

## Risks And Test Signals
The test covers a narrow but important scheduling property: prune jobs inherit tolerations. It does not assert schedule, command args, owner refs, keyring volumes, delete-on-zero-retention behavior, or crash collector disabled behavior.
