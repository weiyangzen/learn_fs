# sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_state.rs

## Purpose
This file defines rebuild lifecycle states and the state machine that validates and stages transitions.

## Important APIs, Types, And Functions
`RebuildState` has `Init`, `Running`, `Stopped`, `Paused`, `Failed`, and `Completed`, with `done` and `running` helpers. `RebuildStates` stores current state, optional pending state, last error, and final stats. It provides `set_pending`, `reconcile`, `exec_op`, `final_stats`, and `set_final_stats`.

## Control Flow
Frontend operations call `exec_op`, which validates the operation against current state and may set a pending state. The backend later calls `reconcile` to make pending current. Terminal states are `Stopped`, `Failed`, and `Completed`. Final stats are stamped with an end time when recorded.

## State, Persistence, And Dependencies
State is in-memory and normally protected by an `RwLock` in `RebuildJob`. It depends on `RebuildError`, `RebuildOperation`, `RebuildStats`, and `chrono`.

## Integration Points
`RebuildJob` uses this to accept/reject client commands. `RebuildJobBackendManager` reconciles pending state and acts on transitions.

## Risks
Some operations while running set pending state but return `Ok(false)`, so the backend must be woken separately or already managing tasks. Pending states can block later client operations unless override is used. Completion from non-running states is rejected, which makes no-work completion depend on first entering running.

## Test Signals
State-machine tests should cover every operation from every state, pending override rules, idempotent start/stop/fail behavior, terminal-state rejection, final stats end-time stamping, and `done`/`running` helpers.
