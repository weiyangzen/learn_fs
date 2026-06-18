# sources/cloud-native/moby/daemon/delete_test.go

## Purpose
Tests user-facing container removal conflict behavior and duplicate delete protection.

## Important APIs, Types, And Functions
- `newDaemonWithTmpRoot` builds a minimal daemon with temp root and memory store.
- `newContainerWithState` creates a test container with a given state.
- `TestContainerDelete` table-tests paused, restarting, and running container removal without force.
- `TestContainerDoubleDelete` checks `RemovalInProgress` handling.

## Control Flow
Tests add synthetic containers to a minimal daemon and call `ContainerRm` with force disabled or enabled. They assert conflict error typing and exact useful error-message fragments.

## State And Persistence
Creates temporary daemon roots and in-memory containers only. No real layer store or volume state is required because tests stop at pre-cleanup conflict paths.

## Dependencies And Integration Points
Covers `delete.go`, container state transitions, containerd error classification, and backend removal config.

## Risks And Edge Cases
Because cleanup is not fully exercised, layer release, root deletion, volume removal, and event emission still rely on broader integration coverage.

## Test Signals
Failures indicate degraded CLI/API feedback for common `docker rm` mistakes or a race guard regression for duplicate removal.
