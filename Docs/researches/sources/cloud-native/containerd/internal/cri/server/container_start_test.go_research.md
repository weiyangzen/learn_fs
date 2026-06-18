# sources/cloud-native/containerd/internal/cri/server/container_start_test.go

## Purpose
This unit test file validates the container starting state guard used by `StartContainer`.

## Important APIs, Types, and Functions
`TestSetContainerStarting` exercises `setContainerStarting` and `resetContainerStarting` with fake container statuses.

## Control Flow, State, and Persistence
Each test creates an in-memory container status. Only created containers may enter `Starting`; running, exited, unknown, already-starting, or removing containers return an error and leave status unchanged. Successful cases reset the flag afterward.

## Dependencies and Integration Points
It depends on container store status state derivation from timestamps and protects the lifecycle gate that prevents concurrent start/remove races.

## Risks and Test Signals
The strong signal is exact metadata preservation on failed transitions. The test does not exercise task creation, logging, NRI, or checkpoint restore behavior.
