# sources/control-plane/mayastor/io-engine/src/sleep.rs

## Purpose
This file provides an async sleep helper compatible with Mayastor reactor expectations.

## Important APIs, Types, And Functions
`mayastor_sleep(duration: Duration) -> oneshot::Receiver<()>` schedules a tokio sleep and returns a receiver that completes after the delay.

## Control Flow
The helper spawns a tokio task, awaits `tokio::time::sleep`, then sends completion back from the primary reactor using `Reactor::spawn_at_primary`. If the receiver was dropped, it logs an error.

## State, Persistence, And Dependencies
No persistent state is stored. It depends on Mayastor `runtime::spawn`, `Reactor`, futures oneshot channels, and tokio timers.

## Integration Points
NVMf subsystem state changes use this helper for retry delays when SPDK reports a busy subsystem. Any code that needs a reactor-friendly timer can use it.

## Risks
Timer precision is explicitly not exact and includes scheduling delays. Completion involves two runtimes/reactors, so shutdown can cancel or delay delivery. The function logs if no receiver remains, which can be noisy for intentionally abandoned sleeps.

## Test Signals
Tests should verify completion after roughly the requested delay, dropped receiver behavior, primary-reactor completion path, and behavior during runtime shutdown if test infrastructure supports it.
