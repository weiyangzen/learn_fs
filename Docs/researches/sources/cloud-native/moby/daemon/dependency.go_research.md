# sources/cloud-native/moby/daemon/dependency.go

## Purpose
Exposes a small adapter for dependency-aware exec/start logic by binding a named dependency store into the daemon's container store.

## Important APIs, Types, And Functions
- `SetContainerDependencyStore(name string, store exec.DependencyGetter) error` delegates to `daemon.containers.SetDependencyStore`.

## Control Flow
The function performs no validation itself; it forwards the name and store to the underlying container memory store.

## State And Persistence
Mutates in-memory container store dependency tracking. No on-disk persistence is performed here.

## Dependencies And Integration Points
Integrates the daemon package with `daemon/cluster/executor/container` dependency getter interfaces and container store dependency support.

## Risks And Edge Cases
Errors are entirely determined by the store implementation. A nil or incorrectly named store could affect dependent-container ordering if not rejected downstream.

## Test Signals
No direct tests in this subset; integration signals are dependency-aware start/restart behavior and store-level tests.
