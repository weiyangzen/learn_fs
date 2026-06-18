# sources/cloud-native/containerd/plugins/server/internal/listen_unix.go

## Purpose
Classifies local listener addresses on non-Windows platforms.

## Important APIs, Types, And Functions
`IsLocalAddress` returns `filepath.IsAbs(path)`.

## Control Flow
Server plugins call this helper to decide between local socket listener creation and TCP listening.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by debug server and shared local endpoint logic on Unix-like systems.

## Risks
Treating all absolute paths as local addresses is appropriate for Unix sockets but relies on callers not passing absolute TCP-like strings.

## Test Signals
No direct tests.
