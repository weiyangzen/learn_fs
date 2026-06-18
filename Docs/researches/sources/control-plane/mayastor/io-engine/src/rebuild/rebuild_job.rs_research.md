# sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_job.rs

## Purpose
This file implements the rebuild frontend object. It exposes lifecycle commands and stats to callers while a backend manager performs copy work asynchronously.

## Important APIs, Types, And Functions
`RebuildVerifyMode` selects no verification, failure, or panic on compare mismatch. `RebuildJobOptions` carries verify mode and `ReadOptions`. `RebuildOperation` is the internal operation enum. `RebuildJob` stores source/destination URIs, state lock, frontend/backend channel, notification receiver, and completion listener list. Public methods include `start`, `stop`, `pause`, `resume`, `stats`, `error`, `error_desc`, `state`, `notify_chan`, `src_uri`, `name`, and `dst_uri`.

## Control Flow
`from_backend` creates a backend manager, copies frontend handles, schedules the manager, and returns the frontend. `start` sets pending state to running and registers a completion listener. Stop/pause/resume call the state machine. Internal force paths can override pending operations. When an operation needs backend action, `wake_up` sends `RebuildJobRequest::WakeUp` on the master reactor. Stats are requested from the backend and fall back to final stats if the backend has already exited.

## State, Persistence, And Dependencies
State is in `Arc<RwLock<RebuildStates>>`, plus channels for commands, state notifications, and completion. No persistent state is stored. Dependencies include the backend manager, `Reactors`, `ReadOptions`, oneshot channels, crossbeam receivers, and `VerboseError`.

## Integration Points
Concrete job wrappers deref to `RebuildJob`, so external code controls all rebuild variants through this API. Rebuild history records are derived from final stats and state after completion.

## Risks
Completion listener registration can fail if the backend has gone away. `stats` can return default stats if the backend exits without final stats. Client operations do not override pending state, so callers can see `StatePending`. Force operations intentionally bypass pending state and should be reserved for teardown/error paths.

## Test Signals
Test state command idempotence, completion listener behavior, stats fallback after backend drop, forced stop/fail, notification channel updates, and operations attempted after terminal states.
