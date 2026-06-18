# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvcs/pvc_service.go

## Purpose
This is the uncached PVC service for listing JuiceFS-bound PVCs and exposing PVC basic information.

## Important APIs, Types, And Functions
It defines `pvcService`, asserts it implements `PVCService`, and implements `listPVCs`, `ListPVCs`, `ListAllPVCs`, `ListPVCsByStorageClass`, and `ListPVCsBasicInfo`.

## Control Flow
`ListPVCs` first lists all JuiceFS PVs with claim refs into a PV-name map, then recursively pages PVCs until it has enough PVCs whose `Spec.VolumeName` appears in that map. `ListAllPVCs` lists all PVCs and matches them by namespace/name against claim refs from supplied JuiceFS PVs. StorageClass and basic-info methods list all PVCs and filter/project as needed.

## State And Persistence
The service is stateless and read-only.

## Dependencies And Integration Points
It depends on controller-runtime list operations, corev1 PV/PVC types, and `config.DriverName`. It is used when dashboard manager caching is disabled and by `NewPVCService`.

## Risks
`ListPVCsByStorageClass` does not restrict results to JuiceFS PVs, so selector endpoints may include non-JuiceFS PVCs for a matching storage class. Recursive paging only recurses when at least one matching PVC was found on the current page; if a page has zero matches but a continue token, later matches can be skipped. Uncached and cached list semantics differ.

## Test Signals
No direct tests are present. Tests should target paging gaps, JuiceFS filtering, and storage-class filtering.
