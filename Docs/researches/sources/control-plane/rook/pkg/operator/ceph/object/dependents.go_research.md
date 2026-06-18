# sources/control-plane/rook/pkg/operator/ceph/object/dependents.go

## Purpose
`dependents.go` computes deletion-blocking dependents for a CephObjectStore: buckets, CephObjectStoreUsers, and special multisite master-zone peer relationships.

## Important APIs, Types, and Functions
`CephObjectStoreDependents()` returns a `dependents.DependentList`. For multisite stores it first calls `CheckZoneIsMaster()`. Secondary zones skip bucket/user checks because the master is treated as source of truth. Master zones call `getMasterZoneDependents()`; if peer zones exist, deletion is blocked and an explanatory error is returned. Otherwise `getBucketDependents()` checks required pools and lists RGW buckets through Admin Ops, and the function lists `CephObjectStoreUser` CRs whose `Spec.Store` matches. `getMasterZoneDependents()` decodes `radosgw-admin zonegroup get` output and records non-current zones as peer dependents.

## Control Flow, State, and Persistence
The file reads Ceph pools, RGW admin APIs, zonegroup JSON, and Rook CRs. It does not mutate state. Missing pools cause bucket checks to be skipped so partially deleted or external stores can finish deletion.

## Dependencies and Integration Points
It integrates deletion finalizer logic in `controller.go`, Ceph admin command helpers, Admin Ops client, object-store pool discovery, Rook CephObjectStoreUser clientset, and the generic dependents reporting package.

## Risks and Test Signals
Risks include intentionally skipping checks when pools are missing, ignoring users for secondary multisite zones, admin-ops availability determining deletion safety, and peer-zone checks taking precedence over bucket/user details. Tests cover missing pools, buckets, users, secondary zones, master zones with and without peers, and expected dependency classes.
