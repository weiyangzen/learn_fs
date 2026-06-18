# sources/cloud-native/containerd/internal/cri/server/container_remove_test.go

## Purpose
This unit test file validates the container removal state guard.

## Important APIs, Types, and Functions
`TestSetContainerRemoving` exercises `setContainerRemoving` and `resetContainerRemoving` against fake container store statuses.

## Control Flow, State, and Persistence
Each case creates an in-memory container with a synthetic status. Running, starting, and already removing containers should error without metadata changes. Exited containers can enter `Removing` and then reset.

## Dependencies and Integration Points
It depends on `containerstore.NewContainer`, fake statuses, and timestamp-derived CRI state logic. It protects the concurrency gate used by `RemoveContainer`.

## Risks and Test Signals
The signal is exact preservation of status on failed guard transitions. The test does not cover filesystem cleanup, containerd deletion, or NRI interactions.
