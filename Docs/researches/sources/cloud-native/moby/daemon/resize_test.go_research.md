# sources/cloud-native/moby/daemon/resize_test.go

## Purpose
Tests exec resize behavior for missing exec instances, successful resize calls, and timeout while waiting for exec startup.

## Important APIs, Types, And Functions
`execResizeMockProcess` embeds the containerd process interface and records width/height in its `Resize` method. Tests use `container.NewExecStore`, `Daemon.registerExecCommand`, and `ContainerExecResize`.

## Control Flow
The missing-exec test registers one exec config but resizes a different ID. The success test closes `ec.Started`, attaches a mock process, and asserts recorded dimensions. The timeout test leaves `Started` open and expects the timeout error.

## State And Persistence
All state is in in-memory daemon, container, and exec stores. No runtime process or disk state is used.

## Dependencies And Integration Points
Linux-only test because it imports daemon/containerd process types under the Linux build. It validates the daemon backend used by API exec resize routes.

## Risks And Edge Cases
The timeout test waits for the production ten-second timeout, which is slow for a unit test and noted by a TODO. It does not cover nil process after a closed `Started` channel.

## Test Signals
Failures indicate lookup error text changed, resize argument ordering regressed, or exec-start timeout behavior changed.
