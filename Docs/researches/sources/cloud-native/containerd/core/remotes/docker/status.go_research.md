<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/status.go -->
# sources/cloud-native/containerd/core/remotes/docker/status.go

## Purpose
Defines push/fetch operation status tracking interfaces and an in-memory implementation used by Docker pusher uploads.

## Important APIs, Types, And Functions
- `Status` embeds `content.Status` and adds `Committed`, `ErrClosed`, `UploadUUID`, and `PushStatus`.
- `PushStatus` records `MountedFrom` and `Exists`.
- `StatusTracker` exposes `GetStatus` and `SetStatus`.
- `StatusTrackLocker` extends tracker with per-ref `Lock` and `Unlock`.
- `NewInMemoryTracker` returns a mutex-protected `memoryStatusTracker` with a `moby/locker` keyed lock.

## Control Flow
`GetStatus` returns not-found when no status exists. `SetStatus` overwrites the status for a ref. Per-ref locks are separate from the map mutex and are used by `dockerPusher.Writer/push` to serialize decisions for the same ref.

## State And Persistence
The default tracker persists state only in memory for the resolver/pusher lifetime. It tracks in-progress offsets and committed state but does not survive process restart.

## Dependencies And Integration Points
Used by `dockerPusher` to prevent concurrent duplicate uploads, record remote existence/mount outcomes, resume or reject active writer flows, and report content writer status.

## Risks And Edge Cases
The default tracker is process-local; external callers needing durable upload coordination need another implementation. `SetStatus` overwrites full status objects, so callers must preserve fields they care about.

## Test Signals
Covered indirectly by `pusher_test.go`, which inspects tracker status for already-existing and mounted content and validates retry behavior after close/reset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/status.go -->
