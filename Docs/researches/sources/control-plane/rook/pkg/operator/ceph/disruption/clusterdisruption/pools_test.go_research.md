# sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/pools_test.go

## Purpose
This test file verifies failure-domain selection and static PDB behavior for RGW object stores and CephFS MDS workloads.

## Important APIs, Types, and Functions
`TestGetMinimumFailureDomain` validates `getMinimumFailureDomain`. `TestReconcileCephObjectStorePDB` covers stale PDB deletion and PDB creation for gateway instances. `TestReconcileCephFilesystemPDB` covers stale MDS PDB deletion and active-standby creation.

## Control Flow, State, and Persistence
Tests build fake controller-runtime clients with optional pre-existing PDBs, call the reconcile helper, then fetch PDBs to assert creation or deletion. State exists only in the fake API client.

## Dependencies and Integration Points
The tests use the Rook scheme, Kubernetes PDB v1 scheme, controllerconfig context with `context.TODO()`, and fake controller-runtime clients.

## Risks
Existing PDB update behavior is not tested; this is important because `reconcileStaticPDB` leaves existing specs unchanged. `processPools` itself is not tested for list aggregation across block pools, filesystems, and object stores.

## Test Signals
Signals include host/zone/region ordering, defaulting to host for unknown domains, stale PDB deletion when instance counts cannot tolerate disruption, RGW PDB creation for two instances, and MDS PDB creation with one active plus standby.
