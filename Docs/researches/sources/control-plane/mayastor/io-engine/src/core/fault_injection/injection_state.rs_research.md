# sources/control-plane/mayastor/io-engine/src/core/fault_injection/injection_state.rs

## Purpose
Tracks mutable per-injection runtime state: activation time, hit count, and deterministic RNG state used by data corruption.

## Important APIs, Types, and Functions
- `InjectionState { started, hits, rng }`.
- `Default` seeds `StdRng` with all-zero bytes for repeatability.
- `tick()` starts the injection on first matching I/O and increments hits thereafter.
- `now()` returns elapsed time since start or `Duration::MAX` if not started.

## Control Flow and State
`Injection::inject` calls `tick` after static match checks. On first tick, `started` is set to `Instant::now()` and hits becomes 1. Later ticks increment hits. `is_active` uses `hits` and `now()` to decide if time and retry gates permit injection. Data injection consumes `rng`.

State is in-memory only and is cloned with `Injection`.

## Dependencies and Integration Points
Uses `rand::rngs::StdRng`, `SeedableRng`, `Instant`, and `Duration`. Owned through a `RefCell` in `Injection`.

## Risks and Test Signals
`now()` returns `Duration::MAX` before start; callers must call `tick` first for meaningful timing. Retry and time behavior depend on match attempts rather than successful injections. Tests should assert first tick return value, hit increments, deterministic RNG, and active-window interactions.
