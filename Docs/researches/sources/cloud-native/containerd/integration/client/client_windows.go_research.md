# sources/cloud-native/containerd/integration/client/client_windows.go

## Purpose
This Windows file defines the default integration-test named pipe address.

## Important APIs, Types, and Functions
`defaultAddress` is `\\.\pipe\containerd-containerd-test`.

## Control Flow
No executable flow.

## State and Persistence
No persisted state; the address selects the Windows named pipe endpoint.

## Dependencies and Integration Points
Used by shared client integration flags and setup on Windows.

## Risks
The address must match the daemon under test; named pipe availability is platform-specific.

## Test Signals
Build/configuration signal for Windows integration tests.
