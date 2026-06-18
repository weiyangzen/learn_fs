# sources/cloud-native/moby/daemon/unpause.go

## Purpose
`unpause.go` resumes a paused container.

## Important APIs, Types, And Functions
`ContainerUnpause` resolves a container and delegates to `containerUnpause`. `containerUnpause` checks paused state, gets the running task, calls `Resume`, updates state/health/events, and checkpoints.

## Control Flow
The container is locked during paused-state validation, task lookup, resume, state mutation, state counter update, health monitor update, event emission, and checkpoint attempt.

## State And Persistence
Updates in-memory paused state, state counters, health monitor behavior, emits an unpause event, and persists the container checkpoint.

## Dependencies And Integration Points
Integrates containerd task resume, container state, daemon health monitor, event logging, and container checkpoint replica.

## Risks
Returning plain formatted errors rather than errdefs for not-paused/resume failures may affect HTTP classification. Holding the container lock while calling `Resume` can block concurrent state operations.

## Test Signals
Container pause/unpause integration tests cover state transitions and event emission.
