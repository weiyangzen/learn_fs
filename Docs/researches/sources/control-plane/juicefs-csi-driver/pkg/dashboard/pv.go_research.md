# sources/control-plane/juicefs-csi-driver/pkg/dashboard/pv.go

## Purpose
`pv.go` implements PV, PVC, and StorageClass dashboard endpoints and resource relationship helpers.

## Important APIs, Types, And Functions
It defines `PVCWithMountPod`, `ListPVPodResult`, `ListPVCPodResult`, `ListSCResult`, and its sort methods. Handlers include list/get middleware for PV/PVC/SC, list PVC selector results, unique ID lookup, event endpoints, mount-pod relation endpoints, and PVs of a StorageClass. Helpers include `getPV`, `getPVC`, and `getStorageClass`.

## Control Flow
List handlers delegate to PV/PVC services or list StorageClasses from the cache, filter by driver/name, sort by creation time, and paginate. Middleware fetches and validates resources, rejecting non-JuiceFS PVs/storageclasses. `listPVCWithSelectorHandler` loads either posted config or current global config, lists mount pods, groups them by unique ID, then resolves each configured PVC selector by exact name, storage class, or label selector. Event handlers call `EventService`. Mount-pod relation endpoints list pods matching `LabelSelectorOfMount`.

## State And Persistence
The handlers are mostly read-only. State is derived from cached Kubernetes PVs, PVCs, StorageClasses, Pods, events, and config. No persistent mutation occurs in this file.

## Dependencies And Integration Points
It depends on PV/PVC/Pod/Event services, `config.DriverName`, `config.LoadFromConfigMap`, `config.MountPodPatch`, dashboard utilities, and controller-runtime cache reads.

## Risks
Exact-name PVC selector uses `CoreV1().PersistentVolumeClaims("").Get`, which is unusual for a namespaced resource and may not work as intended. `getPVC` ignores request context by using `context.Background`. StorageClass sorting uses `Total` as the slice length, so `Total` must always match `len(SCs)` before sorting. Unique-ID behavior changes for share-mount mode by sampling the first CSI node pod.

## Test Signals
No direct tests are present except `utils_test.go` exercising `ListSCResult` via reverse sort. Additional tests should cover PVC selector modes, middleware validation, and pagination bounds.
