# sources/cloud-native/moby/daemon/start_notlinux.go

## Purpose
`start_notlinux.go` provides the non-Linux stub for post-task creation initialization.

## Important APIs, Types, And Functions
`initializeCreatedTask` accepts the same signature as the Linux version and returns nil.

## Control Flow
No runtime work is performed on non-Linux platforms.

## State And Persistence
No state is changed.

## Dependencies And Integration Points
Keeps common `containerStart` code portable across platforms.

## Risks
Platform-specific setup required by future non-Linux runtimes must be added here or in more specific build-tag files.

## Test Signals
Compilation and non-Linux lifecycle tests validate the stub.
