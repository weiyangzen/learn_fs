<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/socket_unix.go -->
# sources/cloud-native/containerd/pkg/sys/socket_unix.go

## Purpose
Unix local listener helpers with path length, directory ownership, chmod, and stale socket unlink handling.

## Important APIs, Types, And Functions
CreateUnixSocket, GetLocalListener, and mkdirAs.

## Control Flow
CreateUnixSocket checks 104-byte path limit, creates parent dir, unlinks stale socket, and listens. GetLocalListener creates/chowns parent dir, creates socket, chmods and chowns socket.

## State And Persistence
Creates directories and Unix socket filesystem entries.

## Dependencies And Integration Points
Used by daemon service listeners and platform socket setup. Depends on x/sys/unix.

## Risks And Edge Cases
mkdirAs returns existing stat errors directly; ownership changes require privileges. Path length limit is conservative for BSDs.

## Test Signals
No direct tests in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/socket_unix.go -->
