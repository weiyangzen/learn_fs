# sources/control-plane/rook/pkg/operator/k8sutil/service.go

## Purpose
`service.go` manages Kubernetes Service create/update operations and multi-cluster ServiceExport lookup/export utilities.

## Important APIs, Types, and Functions
`CreateOrUpdateService()` creates a service or delegates to `UpdateService()` on already-exists. `UpdateService()` preserves immutable `ClusterIP` and uses the existing `ResourceVersion` before update. `ParseServiceType()` maps strings to Kubernetes service types. `IsServiceExported()` checks MCS `ServiceExport` existence. `ExportService()` creates a ServiceExport and resolves its clusterset DNS name. `verifyExportedService()` reports invalid status conditions. `GetExportedServiceIP()` retries DNS lookup.

## Control Flow, State, and Persistence
Service functions persist through client-go core services. MCS functions construct a versioned client from `clusterd.Context.KubeConfig`, create ServiceExports, and perform DNS resolution with 20 retries at five-second intervals.

## Dependencies and Integration Points
It depends on Kubernetes core services, API errors, Rook cluster context, MCS API clients, and `net.LookupIP`. It integrates Rook services with Kubernetes multi-cluster service discovery.

## Risks
`GetExportedServiceIP()` can block for roughly 100 seconds on DNS failure. `ExportService()` relies on DNS name format and only verifies ServiceExport status after DNS resolution fails. Tests cover only `ParseServiceType`; create/update and MCS paths need integration coverage.

## Test Signals
`service_test.go` checks valid and invalid service type strings. Additional signals should cover ClusterIP preservation, resource version propagation, ServiceExport already-exists behavior, invalid status conditions, and DNS retry behavior.
