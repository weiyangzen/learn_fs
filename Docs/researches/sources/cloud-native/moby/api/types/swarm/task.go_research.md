<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/task.go -->
# sources/cloud-native/moby/api/types/swarm/task.go

## Purpose
Defines Swarm task specifications, scheduling constraints, resource requirements, status, desired
state, container status, and volume attachments.

## Important APIs, Types, And Functions
- Exported types: TaskState, Task, TaskSpec, Resources, Limit, GenericResource, NamedGenericResource, DiscreteGenericResource, ResourceRequirements, Placement, PlacementPreference, SpreadOver, RestartPolicy, RestartPolicyCondition, TaskStatus, ContainerStatus, PortStatus, VolumeAttachment.
- Constants: TaskStateNew, TaskStateAllocated, TaskStatePending, TaskStateAssigned, TaskStateAccepted, TaskStatePreparing, TaskStateReady, TaskStateStarting, TaskStateRunning, TaskStateComplete, TaskStateShutdown, TaskStateFailed, TaskStateRejected, TaskStateRemove, TaskStateOrphaned, RestartPolicyConditionNone, and others.
- `Task` fields include ID, Spec, ServiceID, Slot, NodeID, Status, DesiredState, NetworksAttachments, GenericResources, JobIteration, Volumes.
- `TaskSpec` fields include ContainerSpec, PluginSpec, NetworkAttachmentSpec, Resources, RestartPolicy, Placement, Networks, LogDriver, ForceUpdate, Runtime.
- `Resources` fields include NanoCPUs, MemoryBytes, GenericResources.
- `Limit` fields include NanoCPUs, MemoryBytes, Pids.
- `GenericResource` fields include NamedResourceSpec, DiscreteResourceSpec.
- Wire JSON fields include MemorySwappiness, SwapBytes.
- Source comments highlight: TaskState represents the state of a task. Task represents a task. TaskSpec represents the spec of a task.
- The constants encode the task state machine visible through service and task APIs.

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
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/task.go -->
