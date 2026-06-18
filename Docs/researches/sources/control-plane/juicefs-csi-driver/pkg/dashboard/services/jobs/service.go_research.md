# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/jobs/service.go

## Purpose
This file defines the JobService interface, list result DTO, and factory for cached vs uncached job services.

## Important APIs, Types, And Functions
It defines `ListJobResult`, `JobService`, and `NewJobService`.

## Control Flow
`NewJobService` creates a base `jobService` with the configured namespace. If `enableManager` is true, it wraps it in `CacheJobService` with a new time-ordered Job index; otherwise it returns the base service.

## State And Persistence
Factory-created state is either a plain client/namespace pair or an additional in-memory index. Persistent Job data remains in Kubernetes.

## Dependencies And Integration Points
It depends on Gin context signatures, batch/v1 Jobs, controller-runtime clients, `config.Namespace`, and dashboard index utilities. The factory is used by `API.NewAPI`.

## Risks
The same interface hides different pagination/filter semantics between cached and uncached implementations. Consumers must not assume `Total` is always populated.

## Test Signals
No tests are present. A small factory test could verify implementation type by `enableManager`.
