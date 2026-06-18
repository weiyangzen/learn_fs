# sources/cloud-native/moby/daemon/stop.go

## Purpose
`stop.go` implements graceful container stop with timeout and force-kill fallback.

## Important APIs, Types, And Functions
`ContainerStop` resolves a container and checks running state. `containerStop` chooses stop signal/timeout from container defaults or request options, sends the signal, waits for not-running, and calls `Kill` on timeout.

## Control Flow
`ContainerStop` returns not-modified if already stopped and wraps stop failures as system errors. `containerStop` uses `context.WithoutCancel` so client cancellation does not abort stopping. It parses custom signals, builds a timeout context unless timeout is negative, waits for exit, logs signal errors, returns early for infinite wait interruption, and force-kills if the container missed the timeout. On success it logs a stop event and locks the container to wait for exit handler checkpointing.

## State And Persistence
Backend state changes include process signal/kill, container state transition by the monitor/exit handler, stop event emission, and state checkpoint synchronization.

## Dependencies And Integration Points
Integrates container state wait conditions, daemon kill functions, API stop options, signal parsing, events, logging, and errdefs.

## Risks
Negative timeout means no force kill; interrupted waits can return signal errors. The function intentionally outlives request cancellation. Waiting for the exit handler through a lock is subtle but ensures status persistence before returning.

## Test Signals
Container stop integration tests cover signal handling, timeout behavior, already-stopped responses, and kill fallback.
