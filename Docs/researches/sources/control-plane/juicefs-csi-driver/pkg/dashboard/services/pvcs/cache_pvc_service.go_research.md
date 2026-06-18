# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvcs/cache_pvc_service.go

## Purpose
`CachePVCService` provides cached, time-ordered listing and lookup helpers for JuiceFS-bound PVCs.

## Important APIs, Types, And Functions
It defines `CachePVCService`, `ListPVCs`, `ListAllPVCs`, `ListPVCsByStorageClass`, `ListPVCsBasicInfo`, `Reconcile`, and `SetupWithManager`.

## Control Flow
List methods iterate the PVC index, fetch PVCs, apply namespace/name/PV/storageclass filters, and paginate or project basic info. `Reconcile` fetches a PVC, removes missing entries, ignores deleting/unbound PVCs, fetches the bound PV, verifies it is a JuiceFS CSI PV, and adds the PVC to the time index. Setup watches PVC create events for pending/bound PVCs, update events for pending-to-bound transitions, and delete events that remove index entries.

## State And Persistence
State is the in-memory `TimeOrderedIndexes[PersistentVolumeClaim]`. Kubernetes PVC/PV state is read-only.

## Dependencies And Integration Points
It wraps `pvcService`, uses `dashboard/utils.TimeOrderedIndexes`, controller-runtime watches, and `config.DriverName`.

## Risks
DeletionTimestamp handling returns without removing the index, relying on delete events or not-found reconcile to clean up. Update predicate ignores bound PVC updates after initial binding, so storageclass/name changes are not reindexed unless a create/delete path occurs. Cached `ListAllPVCs` ignores its `pvs` argument and returns every indexed PVC, which is fine only if the index is perfectly scoped.

## Test Signals
No direct tests are present. Tests should cover pending-to-bound indexing, deletion cleanup, and cached vs uncached `ListAllPVCs` equivalence.
