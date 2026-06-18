# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvs/pv_service.go

## Purpose
This is the uncached PV service for listing all JuiceFS CSI persistent volumes and looking them up by unique ID.

## Important APIs, Types, And Functions
It defines `pvService` and implements `listPVs`, `ListPVs`, `GetPVByUniqueId`, and `ListAllPVs`.

## Control Flow
`listPVs` lists PV pages with Kubernetes limit/continue, filters to `Spec.CSI.Driver == config.DriverName`, and recursively fetches additional pages until it fills the requested count or exhausts the continue token. `ListPVs` parses page size and continue token. `GetPVByUniqueId` scans all PVs for CSI volume handle equality. `ListAllPVs` lists all PVs and filters to JuiceFS.

## State And Persistence
The service is stateless and read-only.

## Dependencies And Integration Points
It depends on controller-runtime client, Gin query parameters, corev1 PVs, and `config.DriverName`.

## Risks
Like the PVC service, recursive paging only continues when the current page has at least one matching PV; pages with zero JuiceFS PVs and a continue token can stop the scan early. `GetPVByUniqueId` returns an empty PV object instead of nil when not found, which callers must handle carefully.

## Test Signals
No direct tests are present. Tests should cover paging with nonmatching pages and not-found return shape.
