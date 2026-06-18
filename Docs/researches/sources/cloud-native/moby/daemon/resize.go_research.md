# sources/cloud-native/moby/daemon/resize.go

## Purpose
Implements resize operations for a container's primary TTY and for exec sessions.

## Important APIs, Types, And Functions
`Daemon.ContainerResize` resolves a container, gets its running task, calls task `Resize`, and logs a resize event. `Daemon.ContainerExecResize` resolves exec config, waits for `ExecConfig.Started`, validates `Process`, and calls process `Resize`.

## Control Flow
Container resize locks only while getting the running task, then resizes with `context.WithoutCancel` so request cancellation does not interrupt runtime resize. Exec resize waits up to ten seconds for exec startup before resizing; if the exec process is nil after startup it returns an invalid-parameter error.

## State And Persistence
No durable state is changed. Runtime terminal dimensions change in containerd/process state, and successful container resize logs an event with height/width attributes.

## Dependencies And Integration Points
Depends on container lookup, running task/process abstractions, exec store, event logging, and API handlers parsing `h` and `w`.

## Risks And Edge Cases
Exec resize has a hardcoded ten-second timeout, making tests slow and behavior inflexible. Context cancellation is intentionally ignored for the actual resize call. Width/height are passed to backend as width then height even though public parameters are height then width.

## Test Signals
`resize_test.go` covers missing exec IDs, successful resize propagation to a mock process, and timeout when exec startup never completes.
