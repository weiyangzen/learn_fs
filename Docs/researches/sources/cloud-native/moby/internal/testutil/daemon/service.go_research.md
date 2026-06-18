# sources/cloud-native/moby/internal/testutil/daemon/service.go

## Purpose
Adds Swarm service/task helper methods on `Daemon` for integration tests.

## Important APIs, Types, And Functions
- `ServiceConstructor func(*swarm.Service)` mutates a service object before create/update.
- `createServiceWithOptions` builds a default replicated busybox service and calls `ServiceCreate`.
- `CreateService`, `GetService`, `GetServiceTasks`, `GetServiceTasksWithFilters`, `UpdateService`, `RemoveService`, `ListServices`, and `GetTask` wrap common service APIs.

## Control Flow
Create builds a `swarm.Service` object with defaults, applies constructors, and submits the spec. Update applies constructors to an existing service and submits with current version. Task helpers filter by service or task ID and assert expected results.

## State And Persistence
Mutates Swarm service/task state in the daemon's cluster. Defaults create one-replica busybox services with command `top`.

## Dependencies And Integration Points
Uses Moby Swarm service/task APIs, daemon clients, client filters, gotest assertions, and service versioning.

## Risks And Edge Cases
Default service values may be inappropriate for specialized tests unless constructors override them. `GetTask` asserts exactly one task for an ID filter. `GetServiceTasksWithFilters` mutates the provided additional filter by adding the service filter.

## Test Signals
Expected signals are successful service IDs, inspectable services, correctly filtered task lists, successful updates/removals, and exact task lookup.
