# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/status.go

## Purpose
Defines upload status tracking abstractions and an in-memory implementation for Docker pusher operations.

## Important APIs, Types, And Functions
`Status`, `StatusTracker`, `StatusTrackLocker`, `NewInMemoryTracker`, and `memoryStatusTracker` methods `GetStatus`, `SetStatus`, `Lock`, and `Unlock`.

## Control Flow
The tracker stores status by ref under a mutex. Missing refs return `errdefs.ErrNotFound`. The locker wraps a `moby/locker` keyed lock so push operations can serialize concurrent attempts for the same ref.

## State And Persistence
All status lives in memory: content status fields, committed flag, close error, and upload UUID. State is lost when the process exits.

## Dependencies And Integration Points
`dockerPusher` relies on this tracker to detect already committed content, active uploads, incomplete closes, offsets, and commit state.

## Risks And Edge Cases
No durable resume exists. Trackers that do not implement `StatusTrackLocker` can race in `dockerPusher.Writer`, as noted in comments. `UploadUUID` is defined but not actively used by current pusher code.

## Test Signals
Pusher tests exercise the default in-memory tracker through normal, retry, reset, and already-exists paths.
