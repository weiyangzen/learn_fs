# sources/control-plane/rook/pkg/operator/ceph/disruption/clusterdisruption/static_pdb.go

## Purpose
`static_pdb.go` provides small helpers to create static PDBs for non-OSD Ceph workloads such as RGW and MDS.

## Important APIs, Types, and Functions
`createStaticPDB` wraps controller-runtime `Create` and annotates errors with the PDB name. `reconcileStaticPDB` gets an existing PDB by `types.NamespacedName`, creates it if missing, and otherwise leaves it unchanged.

## Control Flow, State, and Persistence
The function persists a new Kubernetes `PodDisruptionBudget` only when one does not already exist. Existing PDB state is treated as accepted and is not updated or reconciled to the desired spec.

## Dependencies and Integration Points
It is called by `reconcileCephObjectStore` and `reconcileCephFilesystem` in `pools.go`, using controller-runtime clients and Kubernetes PDB v1 APIs.

## Risks
Because existing PDBs are not updated, changes to object store instance counts, filesystem active counts, selectors, or owner references can leave stale PDB specs until deletion/recreation logic handles only the low-count stale case.

## Test Signals
There is no direct test file for this helper. Pool tests indirectly verify create-if-missing and stale deletion paths in callers.
