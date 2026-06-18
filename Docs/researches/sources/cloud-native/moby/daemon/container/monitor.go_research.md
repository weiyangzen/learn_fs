<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/monitor.go -->
# sources/cloud-native/moby/daemon/container/monitor.go

## Purpose
Resets runtime container IO/logging state after a container exits so it can be restarted.

## Important APIs, Types, And Functions
`loggerCloseTimeout` and `Container.Reset`.

## Control Flow
`Reset` closes streams, recreates stdin pipes when needed, waits up to ten seconds for the log copier to finish, closes the log driver, logs warnings/errors, and clears runtime logger fields.

## State And Persistence Behavior
Mutates runtime stream/log fields only. No direct disk persistence, though closing log drivers flushes their files/backends.

## Dependencies And Integration Points
Integrates stream config and logger copier/driver lifecycle. Called from container runtime/monitor paths and `InitializeStdio` error handling.

## Risks And Test Signals
Risks include truncated logs on timeout and callers needing to hold the container lock as documented. Container lifecycle/logging tests provide downstream signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/monitor.go -->
