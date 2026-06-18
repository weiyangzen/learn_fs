# sources/cloud-native/containerd/plugins/services/tasks/service.go

## Purpose
`service.go` exposes the local task service over gRPC.

## Important APIs, Types, And Functions
The gRPC plugin ID is `tasks`. `service` stores an `api.TasksClient`, embeds `api.UnimplementedTasksServer`, registers with `api.RegisterTasksServer`, and forwards all task RPCs to `local`.

## Control Flow
Initialization resolves `services.TasksService`. Every RPC is a direct pass-through, preserving the local service's error handling and response shape.

## State And Persistence
This wrapper stores only a local client reference. Runtime, metadata, content, and checkpoint state are handled by `local.go`.

## Dependencies And Integration Points
It connects the service plugin to the gRPC task API and plugin registry.

## Risks
No additional validation is performed at the gRPC layer. The type assertion depends on the service plugin implementing `api.TasksClient`.

## Test Signals
No direct tests are present. RPC registration and task integration tests are the likely signal.
