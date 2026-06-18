# sources/cloud-native/containerd/integration/imagefs_info_test.go

## Purpose

This test verifies CRI `ImageFsInfo` reports a populated filesystem usage record once images and snapshots exist.

## Important APIs, Types, And Functions

- `TestImageFSInfo` is the only test.
- `imageService.ImageFsInfo` retrieves filesystem usage.
- `EnsureImageExists` and `PodSandboxConfigWithCleanup` create data for imagefs accounting.

## Control Flow

The test creates a sandbox to ensure an active snapshot, pulls BusyBox to make image storage non-empty, then polls `ImageFsInfo` until exactly one usage entry exists with nonzero timestamp, nonzero used bytes, and a non-empty mountpoint. It then verifies that the reported mountpoint exists on the host filesystem.

## State And Persistence Behavior

The state observed is image filesystem accounting derived from containerd image/snapshot storage. The test persists no custom data beyond normal pulled image and sandbox state.

## Dependencies And Integration Points

It integrates with CRI image service stats collection, snapshotter filesystem paths, host `os.Stat`, and the shared polling helper.

## Risks And Edge Cases

Stats collection is asynchronous and may lag, so the test polls for up to 30 seconds. Environments with multiple image filesystems would fail because the test expects fewer than two entries.

## Test Signals

Passing confirms CRI reports image filesystem usage with a real mountpoint after image/snapshot activity.
