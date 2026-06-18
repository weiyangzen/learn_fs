<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/service.go -->
# sources/cloud-native/moby/api/types/swarm/service.go

## Purpose
Service represents a service.

## Important APIs, Types, And Functions
- Exported types: Service, ServiceSpec, ServiceMode, UpdateState, UpdateStatus, ReplicatedService, GlobalService, ReplicatedJob, GlobalJob, FailureAction, UpdateOrder, UpdateConfig, ServiceStatus, JobStatus, RegistryAuthSource.
- Constants: UpdateStateUpdating, UpdateStatePaused, UpdateStateCompleted, UpdateStateRollbackStarted, UpdateStateRollbackPaused, UpdateStateRollbackCompleted, UpdateFailureActionPause, UpdateFailureActionContinue, UpdateFailureActionRollback, UpdateOrderStopFirst, UpdateOrderStartFirst, RegistryAuthFromSpec, RegistryAuthFromPreviousSpec.
- `Service` fields include ID, Spec, PreviousSpec, Endpoint, UpdateStatus, ServiceStatus, JobStatus.
- `ServiceSpec` fields include TaskTemplate, Mode, UpdateConfig, RollbackConfig, EndpointSpec.
- `ServiceMode` fields include Replicated, Global, ReplicatedJob, GlobalJob.
- `UpdateStatus` fields include State, StartedAt, CompletedAt, Message.
- `ReplicatedService` fields include Replicas.
- Source comments highlight: Service represents a service. ServiceSpec represents the spec of a service. ServiceMode represents the mode of a service.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `time`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Carries timestamp or duration fields that must remain JSON-compatible across daemon/client boundaries.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- Duration and timestamp fields need stable units and timezone/zero-value behavior across API versions.

## Test Signals
- Package-level tests include `network_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/service.go -->
