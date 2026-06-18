# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvs/cache_pv_service.go

## Purpose
`CachePVService` provides cached, time-ordered listing and lookup for JuiceFS PersistentVolumes.

## Important APIs, Types, And Functions
It defines `CachePVService`, `ListPVs`, `GetPVByUniqueId`, `ListAllPVs`, `Reconcile`, and `SetupWithManager`.

## Control Flow
`ListPVs` parses current/page size/order and name/PVC/SC filters, iterates the PV index, fetches PVs, filters them, and slices the page. `GetPVByUniqueId` scans indexed PVs for matching CSI volume handle. `Reconcile` fetches PVs, removes missing/deleting objects, indexes current PVs by creation time, and logs claim-ref PVC fetch failures. Setup watches JuiceFS CSI PV create and delete events; update events are ignored.

## State And Persistence
State is the in-memory `TimeOrderedIndexes[PersistentVolume]`. Kubernetes PV state is read-only here.

## Dependencies And Integration Points
It wraps `pvService`, uses controller-runtime watches, `config.DriverName`, dashboard index utilities, and is registered by `API.StartManager`.

## Risks
Ignoring update events means claimRef, storageclass, or volume-handle changes are not reflected until delete/recreate or another reconcile. `GetPVByUniqueId` assumes every indexed PV has non-nil `Spec.CSI`, relying on watch filtering. `Reconcile` fetches the claim PVC but does not use it, so errors only log and return nil.

## Test Signals
No direct tests are present. Tests should verify create/delete indexing, update omission behavior, and filtering/pagination.
