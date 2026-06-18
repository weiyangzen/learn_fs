# sources/control-plane/rook/pkg/operator/ceph/object/zonegroup/controller.go

## Purpose

This file implements the `CephObjectZoneGroup` controller for RGW multisite zonegroups. It reconciles a zonegroup CR by waiting for a ready Ceph cluster, requiring a referenced `CephObjectRealm` CR and Ceph realm, creating the RGW zonegroup if missing, marking the first zonegroup as master when needed, and updating status.

## Important APIs, Types, and Functions

- `ReconcileObjectZoneGroup` holds the controller-runtime client, scheme, clusterd context, cluster info, and operator manager context.
- `Add`, `newReconciler`, and `add` register a controller and watch `CephObjectZoneGroup` CRs.
- `Reconcile` wraps `reconcile` with panic recovery and logging.
- `reconcile` fetches the CR, initializes status, waits for cluster readiness, ignores deletion, loads cluster info, validates the CR, reconciles realm prerequisites, creates the Ceph zonegroup, and marks Ready.
- `createCephZoneGroup` checks the current realm period, determines whether this should be the master zonegroup, checks for an existing zonegroup, and runs `radosgw-admin zonegroup create` if needed.
- `reconcileObjectRealm` verifies the Kubernetes `CephObjectRealm` exists.
- `reconcileCephRealm` verifies the Ceph realm exists via `radosgw-admin realm get`.
- `setFailedStatus` and `updateStatus` maintain status phase and observed generation.

## Control Flow

Controller setup watches only zonegroup CRs. Reconcile ignores not-found resources. Unlike zone and pool controllers, this file does not add a finalizer, and deletion simply returns success once cluster readiness allows the code to see the deleted object. If the cluster is absent and the zonegroup is deleting, the function also returns success.

For active resources, the controller loads cluster info, validates name/namespace/realm, sets Reconciling status, and requires both the Kubernetes realm CR and the live Ceph realm. Missing realm CR or live realm produces a 10-second requeue. `createCephZoneGroup` then reads the realm period with `period get`. If `master_zonegroup` is empty, the new zonegroup is created with `--master`. If `zonegroup get` succeeds, no update is performed. If it returns ENOENT, `zonegroup create` runs. Any other command failure is returned.

## State and Persistence Behavior

Kubernetes state is `.status.phase` and `.status.observedGeneration` on the zonegroup CR. No finalizer means the controller does not block deletion or perform Ceph-side deletion. Ceph state includes the RGW zonegroup resource under a realm and possibly the realm's master zonegroup designation.

## Dependencies and Integration Points

The controller integrates with `CephCluster`, `CephObjectRealm`, `object.NewContext`, `object.RunAdminCommandNoMultisite`, `decodeMasterZoneGroup`, `validateZoneGroup`, Rook status reporting, and `k8sutil` status constants. It is a prerequisite for `CephObjectZone`, which reads the zonegroup CR's realm and verifies the live Ceph zonegroup before creating zones.

## Risks and Edge Cases

- No finalizer or deletion cleanup exists for Ceph zonegroups, so deleting the CR does not delete live RGW zonegroup state.
- Existing zonegroups are not updated; reconciliation only creates missing zonegroups.
- If period JSON is malformed or missing `master_zonegroup`, the controller either errors or treats the zonegroup as master.
- Errors wrap `code` even in some branches where `exec.ExitStatus` may not have set a meaningful value.
- Status failures are reported for create errors, but missing realm prerequisites return errors/requeue without a failed status.

## Test Signals

`controller_test.go` covers missing cluster, unready cluster, missing `CephObjectRealm`, and success when Kubernetes and Ceph realm prerequisites exist. `zonegroup.go` helper behavior is not directly tested except through controller success. Deletion and create-on-missing-zonegroup branches are not deeply exercised.
