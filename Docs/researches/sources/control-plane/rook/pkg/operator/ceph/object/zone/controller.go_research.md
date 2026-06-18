# sources/control-plane/rook/pkg/operator/ceph/object/zone/controller.go

## Purpose

This file implements the `CephObjectZone` controller for RGW multisite zones. It waits for a ready `CephCluster` and a referenced `CephObjectZoneGroup`, validates pool specs, creates RGW zone pools and zone configuration, commits multisite config changes, updates status, and handles zone deletion including dependent object-store checks and optional pool preservation.

## Important APIs, Types, and Functions

- `ReconcileObjectZone` holds the controller-runtime client, scheme, clusterd context, cluster info/spec, operator manager context, and event recorder.
- `Add`, `newReconciler`, and `add` register a controller and watch `CephObjectZone` CRs.
- `Reconcile` wraps `reconcile` with panic recovery and result reporting.
- `reconcile` is the main state machine for finalizer setup, cluster readiness, cluster-info loading, validation, zonegroup lookup, deletion, creation/update, and status updates.
- `createorUpdateCephZone`, `createPoolsAndZone`, and `createZoneIfNotExists` create pools, create the RGW zone if missing, update endpoints when needed, configure shared pools/RADOS namespaces, and commit config.
- `getCephObjectZoneGroup` loads the referenced `CephObjectZoneGroup` CR and returns its realm.
- `reconcileCephZoneGroup` verifies the zonegroup exists in Ceph via `radosgw-admin zonegroup get`.
- `validateZoneCR` checks name, namespace, zonegroup, metadata pool spec, and data pool spec.
- `deleteCephObjectZone`, `deleteZone`, `removeZoneFromZonegroup`, `deleteZonePools`, and `decodePoolPrefixfromZone` implement deletion cleanup.

## Control Flow

Controller setup only watches `CephObjectZone` resources. During reconcile, a missing CR is ignored. Existing CRs receive a finalizer. Newly created resources get empty status. Cluster readiness is required before any Ceph operations. If a deleting zone's cluster is gone, the finalizer is removed without trying Ceph cleanup.

After cluster info loads, pool validation happens before zonegroup lookup. If the zonegroup CR is missing during deletion, the finalizer is removed to avoid blocking simultaneous multisite CR deletion. Otherwise the referenced zonegroup must exist and provides the realm name. Deleting zones call `deleteCephObjectZone`.

For normal reconcile, status is set to Reconciling. The controller verifies the zonegroup exists in Ceph, then builds an object context with realm, zonegroup, and zone. Pool config is validated and, unless shared-pool settings say no pool creation is needed, `object.CreateObjectStorePools` creates the metadata/data pools. The zonegroup config is fetched to determine whether a master zone exists. If the zone already exists, endpoint drift is checked and `object.JoinMultisite` updates custom endpoints when required. If the zone is missing, realm keys are loaded from Kubernetes Secrets and `radosgw-admin zone create` is run, adding `--master` if the zonegroup has no master zone and adding `--endpoints` for custom endpoints. Shared pool/RADOS namespace configuration then runs and RGW config changes are committed.

Deletion first checks whether the zone is present in the zonegroup and whether it is master. If present, `CephObjectZoneDependentStores` lists object stores that reference the zone and blocks deletion if any exist. Non-master zones are removed from their zonegroup and period updates are committed. Pool deletion is skipped when `spec.preservePoolsOnDelete` is true or both pool specs are empty. Otherwise the zone is fetched, its `domain_root` is parsed for the pool prefix, and `object.DeletePools` removes RGW pools. The zone is then deleted and the finalizer removed.

## State and Persistence Behavior

Kubernetes state includes the zone CR finalizer, `.status.phase`, `.status.observedGeneration`, and deletion-blocked conditions indirectly reported through the reporting package. Ceph state includes RGW pools, zone membership in a zonegroup, zone endpoints, shared-pool/RADOS namespace settings, and period commits. Pool deletion derives the RGW pool prefix from the live zone JSON rather than assuming the CR name.

## Dependencies and Integration Points

The controller integrates with `CephCluster`, `CephObjectZoneGroup`, pool validation, Rook object helpers, `radosgw-admin` through `object.RunAdminCommandNoMultisite`, cluster monitor Secrets for realm keys, status reporting, and dependent object-store discovery. Test override variables `createObjectStorePoolsFunc` and `commitConfigChangesFunc` allow unit tests to avoid real Ceph pool creation and commits.

## Risks and Edge Cases

- `decodePoolPrefixfromZone` splits `domain_root` on `.rgw.` and returns `s[0]` without checking the split length. Malformed JSON values could produce misleading prefixes.
- Master zone deletion cannot remove the zone from the zonegroup; the code still proceeds to pool and zone deletion. Master-zone semantics are sensitive and rely on underlying RGW behavior.
- Missing zonegroup during deletion removes the finalizer, which prevents stuck CRs but may leave Ceph-side zone state if the zonegroup CR was deleted before the zone.
- Endpoint updates only happen when the zone already exists and `ShouldUpdateZoneEndpointList` detects changes; other zone fields are not updated.
- Pool deletion is broad by prefix and must be correct to avoid deleting unrelated pools.

## Test Signals

`controller_test.go` covers requeue without a cluster, requeue with an unready cluster, requeue when the zonegroup CR is absent, and successful reconcile with mocked zonegroup/zone `radosgw-admin` outputs. `dependents_test.go` separately covers object-store dependent discovery. Deletion, endpoint update, shared-pool configuration, malformed zone JSON, and dependent-blocked deletion paths are not exercised in the main controller tests.
