# sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/pools.go

## Purpose
`pools.go` summarizes Ceph pool failure domains and reconciles static PDBs for object store RGW and filesystem MDS workloads.

## Important APIs, Types, and Functions
`processPools` lists CephBlockPools, CephFilesystems, and CephObjectStores in a namespace, collects their pool specs, counts top-level pool-bearing resources, and returns the minimum failure domain. `getMinimumFailureDomain` chooses the lowest-ranked CRUSH failure domain based on `topology.CRUSHMapLevelsOrdered`. `reconcileCephObjectStore` creates or deletes RGW PDBs. `reconcileCephFilesystem` creates or deletes MDS PDBs.

## Control Flow, State, and Persistence
Pool processing reads CRs from the API server but persists nothing. RGW PDBs use `minAvailable = gateway instances - 1` and are deleted if that falls below 1. MDS PDBs use `activeCount - 1`, adding one when active-standby is enabled, and delete stale PDBs if below 1. Static PDBs are persisted through `reconcileStaticPDB`.

## Dependencies and Integration Points
The file integrates with Rook Ceph CRDs, topology ordering, Kubernetes PDB APIs, and owner references to the owning object store or filesystem.

## Risks
`processPools` increments `poolCount` by CR count, not actual pool spec count, which is sufficient for deciding whether any pool-bearing CR exists but not for precise pool totals. `reconcileStaticPDB` does not update existing PDB specs, so scale changes above the deletion threshold may leave stale `minAvailable` values.

## Test Signals
Tests cover minimum failure-domain selection and stale/create behavior for RGW and MDS PDBs, including scale-down deletion and active-standby MDS creation.
