# sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_job_backend.rs

## Purpose
This file implements the generic rebuild backend manager. It owns the async event loop that reconciles frontend state changes, starts/stops segment tasks, computes stats, sends notifications, and completes waiting clients.

## Important APIs, Types, And Functions
`RebuildJobRequest` carries `WakeUp` and `GetStats`. `RebuildFBendChan` is the async channel pair. `RebuildBackend` is the trait implemented by bdev and nexus backends. `RebuildJobManager` builds shared channels/state, while `RebuildJobBackendManager` wraps a concrete backend. Key methods are `schedule`, `run`, `reconcile`, `on_state_change`, `exec_internal_op`, `stats`, `start_all_tasks`, `manage_tasks`, `await_all_tasks`, `reply_stats`, and the `Drop` implementation.

## Control Flow
The scheduled backend loop waits for frontend messages. On wakeup, it reconciles pending state into current state, starts tasks when entering running, waits for active tasks when stopping/pausing/failing/completing, and sends notifications on state changes. `manage_tasks` keeps up to the task-pool concurrency in flight by starting a new segment when one finishes successfully. A task error fails the job and drains active tasks. Drop records final stats, closes and drains command channels, replies to pending stats requests, and notifies completion listeners.

## State, Persistence, And Dependencies
State includes the concrete backend, shared `RebuildStates`, frontend/backend channel, crossbeam notification sender/receiver, completion sender list, and an atomic notification sequence. It is in-memory only. Dependencies include `Reactors`, futures streams, crossbeam channels, atomics, and rebuild task pool/state/stats modules.

## Integration Points
All concrete rebuild variants plug into this manager by implementing `RebuildBackend`. `RebuildJob` frontends only send messages and inspect shared state.

## Risks
Correctness relies on `active` task counts being exact. Channel closure is treated as frontend/backend failure and can fail the job. Stop/pause/fail waits for active tasks without timeout. Stats are computed from task counters and range-walker remaining blocks, so inconsistent `blocks_remaining` implementations can affect progress reporting.

## Test Signals
Coverage should include start-to-completion, task error failure, pause/resume with active tasks, stop while running, stats request while running and after drop, frontend channel closure, notification ordering, and no-work completion.
