<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_event_test.go -->
# sources/cloud-native/containerd/integration/container_event_test.go

## Purpose
Validates the CRI `GetContainerEvents` streaming API for sandbox and container lifecycle events, including multiple concurrent event subscribers.

## APIs, Types, And Functions
The file defines timeouts, `TestContainerEvents`, `listenToEventChannel`, `drainContainerEventsChan`, and `checkContainerEventResponse`. It uses `runtimeService.GetContainerEvents`, `RunPodSandbox`, `CreateContainer`, `StartContainer`, `StopContainer`, `RemoveContainer`, `StopPodSandbox`, and `RemovePodSandbox`.

## Control Flow And State
The test creates two streaming clients, launches goroutines to receive events into channels, drains stale events from previous tests, then runs a lifecycle: sandbox create/start, container create, container start, container stop/remove, sandbox stop/remove. After each operation it checks both subscribers for the expected event type, the sandbox state when relevant, and the expected list of container states.

## Persistence And Integration Points
State is CRI runtime sandbox/container lifecycle plus streaming gRPC state. The test integrates event publication with status snapshots included in event responses and image availability for the pause container.

## Risks And Test Signals
The helper assumes returned `ContainersStatuses` ordering matches the expected state slice and uses fixed drain/read timeouts, so slow environments can fail. True failures indicate missed events, inconsistent event payload status, broken fan-out to multiple subscribers, or stale events leaking into new subscribers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_event_test.go -->
