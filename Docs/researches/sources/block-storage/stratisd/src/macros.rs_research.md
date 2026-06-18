# File Research: sources/block-storage/stratisd/src/macros.rs

## Purpose

Defines crate-local helper macros for async testing and blocking task spawning.

## Main Types and Behavior

- `test_async!` builds a current-thread Tokio runtime with a `LocalSet` for tests.
- `spawn_blocking!` wraps `tokio::task::spawn_blocking`, awaits the join, and maps join errors into `StratisError`.

## Integration Points

Used under the engine feature by tests and code that needs a compact blocking-task wrapper.
