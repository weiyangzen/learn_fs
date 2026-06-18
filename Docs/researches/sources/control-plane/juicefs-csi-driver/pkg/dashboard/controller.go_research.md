# sources/control-plane/juicefs-csi-driver/pkg/dashboard/controller.go

## Purpose
This file starts controller-runtime cache-backed dashboard service reconcilers when dashboard manager mode is enabled.

## Important APIs, Types, And Functions
The only exported behavior is `API.StartManager`. It type-asserts the API services to `CachePodService`, `CachePVService`, `CachePVCService`, `CacheSecretService`, and `CacheJobService`.

## Control Flow
`StartManager` registers each cache service with the supplied manager through its `SetupWithManager` method. If any service is not a cache implementation, it returns an explanatory error. After all watches are installed, it calls `mgr.Start(ctx)`.

## State And Persistence
State is the controller-runtime manager cache and each cache service's in-memory time-ordered indexes. No Kubernetes object is directly mutated by this file; reconcilers may mutate indexes as watches fire.

## Dependencies And Integration Points
It integrates `API.NewAPI` service selection with controller-runtime manager lifecycle. It is the bridge that makes cached list endpoints work.

## Risks
`StartManager` is only valid when `enableManager` produced cache services; otherwise it fails at runtime. Since `mgr.Start` blocks until context cancellation, callers must run it in an appropriate goroutine or lifecycle lane.

## Test Signals
No tests are present. Tests should check failure when services are uncached and successful setup with fake manager/controller registrations.
