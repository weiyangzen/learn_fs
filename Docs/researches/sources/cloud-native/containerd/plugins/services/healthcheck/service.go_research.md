# sources/cloud-native/containerd/plugins/services/healthcheck/service.go

## Purpose
Registers the standard gRPC health checking service.

## Important APIs, Types, And Functions
`service` wraps `*health.Server`. `newService` constructs it. `Register` registers `grpc_health_v1.HealthServer`.

## Control Flow
Plugin init returns a new health service without dependencies. The gRPC server later registers it.

## State And Persistence
Health status state is in-memory inside `health.Server`.

## Dependencies And Integration Points
Depends on gRPC health package and plugin registry. Exposed by the main gRPC server.

## Risks
No service statuses are configured here; default behavior depends on `health.Server`.

## Test Signals
No direct tests.
