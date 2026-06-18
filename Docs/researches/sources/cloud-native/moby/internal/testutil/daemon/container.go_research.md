# sources/cloud-native/moby/internal/testutil/daemon/container.go

## Purpose
Adds a daemon helper for listing active/running containers in the daemon's isolated environment.

## Important APIs, Types, And Functions
- `(*Daemon).ActiveContainers(ctx, t)` creates a daemon-scoped client, calls `ContainerList` without `All`, and returns container IDs from the response.

## Control Flow
The helper creates a client, defers close, lists containers, asserts no error, then maps summaries to IDs.

## State And Persistence
Read-only helper. It observes currently running containers but does not modify daemon state.

## Dependencies And Integration Points
Uses the `Daemon` client factory, Moby client container API, and gotest assertions. Used by integration tests that need to assert runtime container counts.

## Risks And Edge Cases
Only running containers are returned because `All` is not set. The function ignores the passed context in `ContainerList` and uses `context.Background`, so caller cancellation is not honored.

## Test Signals
Expected signal is a slice of running container IDs with no API error.
