# sources/cloud-native/containerd/integration/container_without_image_ref_test.go

## Purpose

This test verifies that a running container remains manageable after its original image reference is removed from CRI image storage. It protects lifecycle operations from depending on a still-present tag/reference after container creation.

## Important APIs, Types, And Functions

- `TestContainerLifecycleWithoutImageRef` is the only test.
- `EnsureImageExists` returns the image ID/reference used for deletion.
- `imageService.RemoveImage`, `runtimeService.ContainerStatus`, and `runtimeService.StopContainer` drive the core behavior.

## Control Flow

The test creates a sandbox, ensures BusyBox is available, creates and starts a sleeping container, removes the image using the returned image ID, then asserts the container remains `RUNNING`. It stops the container and checks the state becomes `EXITED`.

## State And Persistence Behavior

The test mutates CRI image metadata by removing the image reference while preserving container/task state. It depends on snapshots and container metadata retaining enough information to operate without that reference.

## Dependencies And Integration Points

It integrates CRI image and runtime services, image ID/reference handling, and container runtime lifecycle operations.

## Risks And Edge Cases

Removing the shared BusyBox image can affect other tests if they run concurrently against the same CRI instance; the integration suite generally serializes or re-pulls images as needed. The test does not verify subsequent container creation from the removed reference.

## Test Signals

Passing confirms status and stop operations work after image reference deletion.
