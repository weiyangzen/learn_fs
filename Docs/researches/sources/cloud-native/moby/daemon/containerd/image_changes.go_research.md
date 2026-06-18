# sources/cloud-native/moby/daemon/containerd/image_changes.go

## Purpose
Computes filesystem changes between a container's writable layer and its parent image snapshot using containerd snapshot mounts.

## Important APIs, Types, And Functions
- `ImageService.Changes(ctx, ctr)` returns `[]archive.Change`.
- Uses container RW layer mount/unmount, snapshotter `Stat` and `View`, `mount.WithReadonlyTempMount`, and `archive.ChangesDirs`.

## Control Flow
The method validates `ctr.RWLayer`, stats the container snapshot to find its parent, creates a temporary read-only parent view snapshot, mounts the container RW layer, mounts the parent view through a temporary read-only mount, diffs the two directories, then removes the parent view and unmounts the RW layer in defers.

## State And Persistence
Creates a temporary snapshot view named from container ID plus random ID and removes it afterward. It temporarily mounts the RW layer and parent view. No image metadata is changed.

## Dependencies And Integration Points
Depends on containerd snapshotter/mount APIs, Moby archive diff utilities, and container layer abstractions. It powers image/container diff APIs for containerd-backed storage.

## Risks And Edge Cases
The code ignores the error returned by `snapshotter.View` before using `imageMounts`, which relies on later mount behavior to fail. Cleanup failures are logged only. A nil RWLayer is considered unexpected and returned as an error.

## Test Signals
No direct tests in this subset. Integration tests should assert added/modified/deleted paths and cleanup after parent-view creation.
