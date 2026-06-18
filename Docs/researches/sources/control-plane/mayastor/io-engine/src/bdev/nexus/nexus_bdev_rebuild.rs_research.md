<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_rebuild.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_rebuild.rs

Purpose: manages rebuild jobs for out-of-sync nexus children, including source selection, job creation, lifecycle control, pause/cancel/restart around child operations, completion handling, persistent health updates, and rebuild history.

Important APIs/types/functions: `RebuildPauseGuard`, `start_rebuild`, `find_src_replica`, `create_rebuild_job`, `stop_rebuild`, `pause_rebuild`, `resume_rebuild`, `rebuild_state`, `rebuild_stats`, `rebuild_progress`, `cancel_rebuild_jobs`, `start_rebuild_jobs`, `count_rebuild_jobs`, `on_rebuild_update`, and `notify_rebuild`.

Control flow: `start_rebuild` selects a healthy source, validates the destination is open and out-of-sync with no existing job, creates and stores a `NexusRebuildJobStarter`, emits rebuild-begin, reconfigures nexus channels so the destination becomes a write target, stops any partial-rebuild I/O log to build a `RebuildMap`, and starts the job over the nexus data partition range. Completion callbacks run on a reactor, look up the nexus, inspect final job state, mark successful children synced and persist healthy state, close-fault failed destinations, remove the job, create history, and reconfigure channels again.

State and persistence: active jobs are stored globally by `NexusRebuildJob`, while per-nexus rebuild history is kept in a mutex vector. Successful rebuild completion persists child health with `PersistOp::Update { healthy: true }`. `RebuildPauseGuard` remembers cancelled destination URIs and asserts it was resumed before drop, forcing callers to restart cancelled jobs explicitly.

Dependencies/integration: integrates with `NexusChild` sync state and job lookup, `Nexus::reconfigure`, `PersistOp`, reactor scheduling, `NexusRebuildJob` and rebuild stats/state/error metadata, eventing for rebuild begin/end, and optional `NEXUS_REBUILD_VERIFY` environment modes.

Risks: correct ordering is subtle: destination must receive frontend writes before the rebuild map is frozen, and job removal before reconfigure may allow a new rebuild to start while channels still reflect old state. Source selection prefers local healthy replicas but otherwise just takes the first candidate. Failed persistence after completed copy returns an error even though data copy already happened. `RebuildPauseGuard` will panic on drop if `resume` is skipped.

Test signals: rebuild start without source, wrong destination state, duplicate job, local-source preference, map creation from I/O log, frontend writes during rebuild, successful persist and channel reconfigure, failed/stopped job transitions, rebuild history creation, cancellation when source or destination is removed, and guard panic/resume behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_rebuild.rs -->
