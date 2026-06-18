# sources/cloud-native/moby/daemon/restart.go

## Purpose
Implements container restart as a stop-then-start sequence with graceful stop options, manual restart marking, mount optimization, and restart event logging.

## Important APIs, Types, And Functions
`Daemon.ContainerRestart` is the public lookup wrapper. `Daemon.containerRestart` performs restart using `containerStop`, `containerStart`, `Mount`, `Unmount`, container isolation, and backend `ContainerStopOptions`.

## Control Flow
The operation strips cancellation from the context to keep restart atomic after admission. It resolves effective isolation, pre-mounts non-Hyper-V containers to avoid unmount/remount churn, marks running containers as manually restarted, stops them with the provided options, starts the container, and logs an `ActionRestart` event.

## State And Persistence
Mutates container state through stop/start, marks `HasBeenManuallyRestarted`, may mount/unmount the filesystem, and emits an event. The operation delegates actual persistence to stop/start paths.

## Dependencies And Integration Points
Used by API restart route and daemon internals. It integrates with platform isolation, mount management, stop/start lifecycle, event logging, and restart policy semantics.

## Risks And Edge Cases
Request cancellation cannot interrupt the stop/start sequence once begun. Mount optimization is skipped for Hyper-V isolation. If stop succeeds but start fails, the container remains stopped and the error is returned.

## Test Signals
No direct file-local tests are listed; lifecycle integration tests should verify stop options, event emission, manual restart effects, and failure behavior.
