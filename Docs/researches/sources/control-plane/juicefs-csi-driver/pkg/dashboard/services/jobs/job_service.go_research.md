# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/jobs/job_service.go

## Purpose
This is the uncached JobService implementation for listing smooth-upgrade batch Jobs directly through a controller-runtime client.

## Important APIs, Types, And Functions
It defines `jobService` and `ListAllBatchJobs`.

## Control Flow
The method parses `pageSize` with a default of 10, reads a Kubernetes continue token, and optionally handles an exact `name` lookup in the system namespace. Without a name filter, it lists Jobs in the system namespace with labels identifying JuiceFS upgrade jobs and returns the list plus Kubernetes continue token.

## State And Persistence
The service is stateless apart from its client and system namespace. It reads Kubernetes Job state but does not mutate it.

## Dependencies And Integration Points
It is selected by `NewJobService` when manager caching is disabled and is consumed by `batch.go` list endpoints.

## Risks
Name filtering is exact, not substring-based like cached mode, which creates different API behavior between modes. The returned `Total` is not populated in uncached mode. Pagination uses Kubernetes continue tokens rather than page numbers.

## Test Signals
No tests are present. Tests should verify label selectors, exact-name behavior, and empty/not-found behavior.
