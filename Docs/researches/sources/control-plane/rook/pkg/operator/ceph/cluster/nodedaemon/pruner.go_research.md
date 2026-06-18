# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/pruner.go

## Purpose
This file reconciles a CronJob that periodically prunes old Ceph crash reports using the crash collector keyring.

## Important APIs, Types, And Functions
`reconcileCrashPruner(namespace, cephCluster, tolerations)` decides whether to create/update or delete the pruner. `createOrUpdateCephCron(cephCluster, tolerations)` builds the CronJob. `getCrashPruneContainer(cephCluster)` builds the `ceph crash prune` container. The schedule is `0 0 * * *`.

## Control Flow And State
If crash collection is disabled, reconciliation skips pruning. If `DaysToRetain` is zero, it deletes the CronJob if present and ignores not-found. Otherwise it creates or updates an owned CronJob with label `app: rook-ceph-crashcollector-pruner`, cluster label, pod template using crash keyring volumes, inherited tolerations, optional host networking, default service account, and a single container running `ceph -n client.crash crash prune <days>`. The CronJob has `StartingDeadlineSeconds` of 60 to avoid accumulated missed runs counting indefinitely.

## Dependencies And Integration Points
The file depends on Kubernetes batch/v1 CronJobs, Rook controller volume/env helpers, crash collector keyring volumes, CephCluster crash collector spec, owner refs, and controller-runtime `CreateOrUpdate`. It integrates with node reconciliation after node daemon create/delete handling.

## Risks And Test Signals
Risks include stale CronJobs when retention is disabled, missing keyring secret, and prune jobs with incorrect tolerations or host networking. `pruner_test.go` covers CronJob creation and toleration propagation. Deletion and disabled paths are not covered in the shown tests.
