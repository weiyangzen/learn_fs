# subset-b-008261 RustFS heal subsystem research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/channel.rs -->
# sources/object-store/rustfs/crates/heal/src/heal/channel.rs

## Purpose

`channel.rs` adapts the common RustFS heal channel protocol into local `HealManager` operations. It receives start, query, and cancel commands from `rustfs_common::heal_channel`, converts user/admin-facing request shapes into internal `HealRequest` values, submits them to the manager, and publishes both oneshot replies and broadcast `HealChannelResponse` messages. It is the boundary between admin/API command handling and the internal queue/scheduler/task model.

## Important APIs, types, and functions

- `HealChannelProcessor` owns an `Arc<HealManager>`, an unbounded response sender, and an unbounded local response receiver used to observe locally published responses.
- `HealTaskStatusPayload` is the JSON payload for query responses, carrying a MinIO-style `summary` string plus `HealResultItem` details.
- `new` creates the processor and local response channel.
- `start` runs a `tokio::select!` loop over inbound `HealChannelReceiver` commands and local responses. It exits when the command receiver closes.
- `process_command` dispatches `HealChannelCommand::Start`, `Query`, and `Cancel`.
- `process_start_request` converts a channel request, submits it with `HealManager::submit_heal_request`, returns `HealAdmissionResult`, and broadcasts an admission response.
- `process_query_request` calls `HealManager::get_task_report_for_path` and maps internal statuses to the external summaries `running`, `finished`, or `stopped`.
- `process_cancel_request` cancels either by explicit client token or, if token is empty, by heal path.
- `convert_to_heal_request` maps channel fields into `HealType`, `HealPriority`, and `HealOptions`.
- `publish_response` sends to the local unbounded channel and calls `publish_heal_response`.
- `get_response_sender` exposes a clone of the local response sender.

## Control flow

The main loop receives a command, logs it, and lets command-specific handlers send the oneshot response. Start requests are converted before manager submission. Conversion failures produce an immediate error oneshot plus a failed broadcast. Successful manager admission sends `Ok(admission)` to the caller and publishes a response whose `data` contains an ASCII `admission=...,reason=...` string; queue-full or dropped admissions are treated as unsuccessful broadcast responses even though manager submission itself returned `Ok`.

Query requests are path-token bound. Active or queued tasks produce `running`, completed tasks produce `finished`, cancelled/timeout/failed tasks produce `stopped` with an error/detail string, and a missing task is treated as `finished` with no result items. A mismatched token for a path that still has a task is reported as `invalid heal client token`.

Cancel requests use token precedence when the token is non-empty. Empty-token cancellation cancels all queued or active tasks matching the path and treats a missing path as already stopped, which gives idempotent cancel behavior for path-level admin calls.

## State and persistence behavior

This file has no durable state. Its persistent effects come through `HealManager` and through the global heal-channel response publisher. The local response channel is in-memory, unbounded, and only used by this processor instance to observe responses. Query response result items are drawn from active task state or the manager's short-lived completed-task cache.

## Dependencies and integration points

The file depends on `HealManager`, `HealTaskReport`, internal `task` types, and `utils::normalize_set_disk_id`. It integrates with `rustfs_common::heal_channel` for command/request/response/admission/scan-mode types and global response publication. It serializes query payloads with `serde_json`, returns object-level result items from `rustfs_madmin::heal_commands`, and uses structured `tracing` fields for heal-channel observability.

## Risks and edge cases

- `force_start` deliberately affects admission only. The comment warns against interpreting it as `remove_corrupted=true`, because admin clients may pass force start with remove false.
- Disk requests become `HealType::ErasureSet` with an empty bucket list; callers or later storage logic must populate buckets for actual erasure-set healing.
- Query treats `TaskNotFound` as finished. This is useful for client polling after completion but can hide lost status once completed-task retention expires.
- Local response delivery failure is logged but does not block global broadcast.
- Unbounded local response buffering can grow if responses are produced faster than the processor drains them.
- Query JSON serialization failure is propagated as `Serialization`.

## Test signals

The test module uses a `MockStorage` and covers conversion behavior, start admission paths, query reporting for missing/queued/wrong-token/empty-path cases, cancel by token, cancel by path, idempotent unknown-path cancel, and unknown-token cancel errors. Additional useful tests would cover broadcast failure behavior, invalid disk-id conversion, and `force_start` preserving non-destructive options.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/channel.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/erasure_healer.rs -->
# sources/object-store/rustfs/crates/heal/src/heal/erasure_healer.rs

## Purpose

`erasure_healer.rs` implements resume-aware erasure-set healing. It scans configured buckets, pages through objects, checks or heals each object using the `HealStorageAPI`, records progress/checkpoints to disk-backed resume managers, and cleans up resume state after successful completion. It is the worker-side implementation for `HealType::ErasureSet` tasks.

## Important APIs, types, and functions

- `ErasureSetHealer` holds the storage API, shared `HealProgress`, cancellation token, resume/checkpoint disk, and `HealOpts`.
- `page_parallel_enabled`, `heal_page_object_concurrency`, `effective_heal_page_object_concurrency`, and `effective_heal_page_object_concurrency_for_scan_mode` read configuration and force deep scans to serial object processing.
- `heal_erasure_set` is the public entry point. It creates or resumes a task id, initializes resume/checkpoint managers, runs healing, and cleans durable resume files on success.
- `get_or_create_task_id` scans disk resume state for a matching `set_disk_id`, otherwise creates `{set_disk_id}_{uuid}`.
- `initialize_resume_state` loads existing resume/checkpoint files or creates new `ResumeManager` and `CheckpointManager` instances.
- `execute_heal_with_resume` initializes in-memory progress from resume state, continues from checkpoint bucket/object indexes, updates resume counters, handles cancellation, and marks completion.
- `heal_bucket_with_resume` pages object listings, skips already processed/skipped checkpoint entries, runs per-page object heal futures with a semaphore, updates checkpoint object sets and positions, and records success/failure/skip counters.
- `initialize_progress` maps persisted resume counters into `HealProgress`.
- Dead-code helpers `heal_buckets_concurrently`, `heal_single_bucket`, `heal_objects_concurrently`, and `process_results` show an older non-resume concurrent implementation retained for reference/tests.

## Control flow

Healing starts by selecting a resumable task for the same set disk id when possible. If no state exists, a new resume state and checkpoint are written to the disk's meta bucket. `execute_heal_with_resume` clones the saved resume state and checkpoint, initializes counters from it, and iterates buckets from `current_bucket_index`, skipping buckets already marked complete.

For each bucket, `heal_bucket_with_resume` verifies the bucket exists, then repeatedly calls `list_objects_for_heal_page`. For each page it records a `global_obj_idx`, skips objects before `current_object_index`, and also skips objects already recorded as processed or skipped in the checkpoint. Each remaining object is healed in a future guarded by a page semaphore. Deep scans call `heal_object` directly and treat not-found errors as a non-failing skip/ok. Normal scans first call `object_exists`, then heal existing objects. `TransientSkip` is counted separately and checkpointed as skipped.

When futures complete, successes and missing-as-ok objects are added to processed checkpoint state; transient skips are added to skipped; other failures are added to failed. The processed counter is incremented for every completed future. The checkpoint position is written after each page and periodically inside large pages. Cancellation returns `TaskCancelled` and resets the page concurrency gauge to zero.

After each bucket, resume progress is saved and successful bucket completion updates `completed_buckets`. Bucket-level errors are logged and do not stop later buckets. At the end the resume state is marked completed, and the top-level `heal_erasure_set` removes resume/checkpoint files only when the overall result is `Ok`.

## State and persistence behavior

Durable state is delegated to `ResumeManager` and `CheckpointManager`, which write JSON under the RustFS meta bucket on the selected `DiskStore`. Resume state stores task counters, current bucket/object, completed/pending buckets, set id, retry metadata, and completion. Checkpoint state stores bucket/object indexes plus processed/failed/skipped object name lists.

In-memory progress is a best-effort view backed by `Arc<RwLock<HealProgress>>`; it is initialized from resume state but not updated for every object in this file except through resume counters. Metrics include `rustfs_heal_page_concurrency_current` with a set label.

## Dependencies and integration points

The implementation depends on `HealStorageAPI` for bucket lookup, paged listing, existence checks, and object healing. It depends on `resume.rs` for persistent state and on `progress.rs` for user-visible progress. Configuration comes from `rustfs_config` and `rustfs_utils`; scan mode and options come from `rustfs_common::heal_channel::HealOpts`. It uses `tokio_util::CancellationToken`, `tokio::Semaphore`, `FuturesUnordered`, `join_all`, metrics gauges, and structured `tracing`.

## Risks and edge cases

- Checkpoint object sets store object names without bucket qualification. Since checkpoints are per erasure-set task and processing is bucket-indexed, duplicate object names across buckets may cause unwanted skips if a later bucket contains the same object name.
- `checkpoint` is captured before iterating a page, so processed/skipped membership used for that page does not include updates made while the page is running.
- Periodic checkpoint updates inside a page use `page_resume_index`, not the completed object's global index. A crash mid-page may redo page work, which is safe but less precise.
- `ResumeState.total_objects` is never populated by this healer, so resume progress percentage based on total objects remains zero unless another component updates it.
- Non-deep scans skip missing objects as successful, while deep scans infer missing by string matching error messages containing `File not found` or `not found`.
- Bucket-level errors do not fail the overall task unless they surface outside the per-bucket `match`, so a task can complete with failed objects or failed buckets recorded only in counters/logs.
- Resume files are not cleaned on cancellation or failure, which is required for resume but may leave stale state until explicit expiration cleanup.

## Test signals

The file has focused tests for environment-driven page concurrency and the deep-scan serial override. Broader integration tests should exercise resume after crash/cancel, duplicate object names across buckets, transient skip behavior, checkpoint precision, bucket-list pagination without continuation token, normal versus deep scan missing-object handling, and gauge reset on early errors.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/erasure_healer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/event.rs -->
# sources/object-store/rustfs/crates/heal/src/heal/event.rs

## Purpose

`event.rs` defines heal-domain events and converts them into `HealRequest` values. It also provides a small bounded in-memory event handler for storing, filtering, and clearing recent events. This file is a classification and request-construction layer rather than an async scheduler.

## Important APIs, types, and functions

- `CorruptionType` classifies data, metadata, partial, and complete corruption.
- `Severity` is ordered from `Low` through `Critical` and maps to heal priority.
- `HealEvent` variants cover object corruption, missing object, metadata corruption, disk status changes, EC decode failure, checksum mismatch, bucket metadata corruption, and MRF metadata corruption.
- `HealEvent::to_heal_request` maps events into `HealType::{Object, Metadata, ErasureSet, ECDecode, Bucket, MRF}` with default options and severity-derived or fixed priority.
- `severity_to_priority` maps low/medium/high/critical to low/normal/high/urgent.
- `description` builds human-readable event strings.
- `severity` returns effective severity for each event kind.
- `timestamp` returns `SystemTime::now()` when called.
- `HealEventHandler` stores up to `max_events` events in a `Vec`, evicting the oldest when full.
- Handler methods include `add_event`, `get_events`, `clear_events`, `event_count`, `filter_by_severity`, and `filter_by_type`.

## Control flow

`to_heal_request` pattern matches the event. Object-corruption requests preserve version id and derive priority from explicit severity. Object-missing, checksum, bucket metadata, MRF metadata, and metadata-corruption events use high priority. EC decode failures use urgent priority. Disk status changes derive a set disk id from the endpoint pool/set indexes and create an erasure-set request with an empty bucket list; invalid endpoint indexes return `InvalidHealType`.

The event handler is synchronous. Adding to a full handler removes `events[0]`, then pushes the new event. Filtering by severity uses the enum's ordering. Filtering by type matches fixed string names.

## State and persistence behavior

There is no durable persistence. `HealEventHandler` is an in-memory bounded vector with O(n) oldest removal and O(n) filters. `timestamp` does not read a stored event timestamp; it returns the current time on each call, so event time is not preserved in `HealEvent`.

## Dependencies and integration points

This file uses internal `HealOptions`, `HealPriority`, `HealRequest`, and `HealType`, the crate `Error`/`Result`, and `rustfs_ecstore::disk::endpoint::Endpoint` for disk events. Disk event conversion uses `crate::heal::utils::format_set_disk_id_from_i32`, so it must stay consistent with manager/channel erasure-set key normalization.

## Risks and edge cases

- Disk-status events produce erasure-set requests with empty bucket vectors. Callers must populate bucket lists or storage execution will have nothing to scan.
- Event timestamps are not intrinsic to events, so callers cannot reconstruct detection time from an event instance.
- `filter_by_type` depends on exact string literals and has no enum-safe selector API.
- `add_event` removes from the front of a `Vec`, which is acceptable for the default 1000 events but is O(n).
- Event details such as missing/available shard/location vectors influence descriptions but not request options.

## Test signals

Tests cover event-to-request mapping for object, missing object, metadata, EC decode, checksum, bucket metadata, and MRF events; severity-to-priority mapping; descriptions; severity calculation; handler construction/defaults; bounded eviction; clear/get; and filtering by severity/type. Additional coverage should include disk-status conversion success/failure and the empty-bucket handoff requirement.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/event.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/manager.rs -->
# sources/object-store/rustfs/crates/heal/src/heal/manager.rs

## Purpose

`manager.rs` is the central heal scheduler and admission controller. It owns the priority queue, active task map, completed-task status cache, global heal configuration/state/statistics, background queue scheduler, and automatic disk scanner for unformatted local disks. It turns `HealRequest` submissions into `HealTask::execute` calls while enforcing queue capacity, deduplication, priority ordering, optional displacement, and per-erasure-set bulkheads.

## Important APIs, types, and functions

- `PriorityHealQueue` wraps a `BinaryHeap<PriorityQueueItem>`, FIFO sequence number, and dedup-key reference counts.
- `PriorityQueueItem` orders higher `HealPriority` first and lower sequence first within equal priority.
- `QueuePushOutcome` distinguishes accepted versus merged duplicate pushes.
- `CompletedHealStatus` stores recent completed task type/status/result items plus completion time.
- `HealTaskReport` is the public report used by channel queries.
- `HealConfig` reads environment-backed defaults for auto heal, intervals, concurrency, queue size, low-priority merge/drop policy, event-driven scheduler, set bulkhead, and page parallel flags.
- `HealState` stores manager runtime flags and cumulative counters.
- `HealManager` owns config, state, active tasks, queue, completed cache, storage, cancellation token, statistics, and scheduler notify handle.
- Public methods include `new`, `start`, `stop`, `submit_heal_request`, status/report/progress getters, `cancel_task`, `cancel_tasks_for_path`, statistics/count getters, and queue length.
- Background methods include `start_scheduler`, `start_auto_disk_scanner`, and static `process_heal_queue`.
- Helpers include `heal_type_matches_path`, metric publishers, per-set scheduling helpers, completed-status pruning, and active-running metric updates.

## Control flow

Submission first reads config and locks the queue. Non-forced duplicate dedup keys are merged, except low-priority duplicates can be policy-dropped when low-priority merge is disabled. If the queue is full and the request is not forced, higher-priority requests can displace one lower-priority queued request; otherwise low priority may be dropped or the request is reported full. Accepted requests are pushed into the heap, queue length metrics are updated, and the scheduler is notified when event-driven scheduling is enabled.

`start` marks the manager running, spawns the scheduler, and spawns the auto disk scanner. `stop` cancels the manager cancellation token, cancels all active tasks, clears active/completed state, resets metrics, and marks the manager stopped. The same cancellation token is used by background loops, so a stopped manager instance is not reusable without constructing a new token.

The scheduler loop wakes on cancellation, notify, or interval. `process_heal_queue` checks global active capacity, locks the queue, optionally skips erasure-set requests whose set already hit `max_concurrent_per_set`, converts selected requests into `Arc<HealTask>`, inserts them into `active_heals`, and spawns each task. When a task finishes, the spawned future removes it from active state, inserts a pruned completed-status entry, updates success/failure/running statistics, updates running metrics, and notifies the scheduler again.

The auto disk scanner periodically inspects `GLOBAL_LOCAL_DISK_MAP`; unformatted disks become candidates. It lists buckets through storage, formats endpoint pool/set into a set disk id, skips duplicate queued/active erasure-set heals, and enqueues normal-priority erasure-set requests directly into the queue.

Status paths check active tasks first, queued request ids second, and recent completed statuses third. Path-bound variants require the task's heal type to match the supplied path; if another task exists for the path, an unknown token returns `InvalidClientToken`. Completed statuses are retained for `KEEP_HEAL_TASK_STATUS_DURATION` of ten minutes.

Cancellation by task id cancels active tasks or removes queued requests. Cancellation by path cancels all matching active tasks and queued requests and errors only if no match exists; channel-level path cancel converts unknown path to success.

## State and persistence behavior

Manager state is in memory. Active tasks and the queue are protected by `tokio::Mutex`; config/state/statistics use `RwLock`. Completed statuses are in-memory and pruned after ten minutes. Queue dedup state is maintained as reference counts so forced duplicates reserve the key until all queued copies are popped or removed.

Persistent healing effects are delegated to `HealTask` and storage implementations, and erasure-set resume persistence is handled outside this file. The auto scanner derives candidates from the global local disk map and storage bucket listing, but does not persist its own cursor. Metrics are pushed through crate-level setters plus `metrics::counter` and `metrics::gauge`.

## Dependencies and integration points

The manager integrates with `HealStorageAPI`, `HealTask`, `HealRequest`, `HealType`, `HealOptions`, `HealPriority`, and `HealTaskStatus`. It depends on `rustfs_common::heal_channel` for admission result/drop reason, `rustfs_ecstore` disk APIs and `GLOBAL_LOCAL_DISK_MAP` for auto scanning, `rustfs_config`/`rustfs_utils` for configuration, `tokio` primitives for async scheduling, and `metrics`/`tracing` for observability. Channel queries and cancels rely on `get_task_report_for_path`, `get_task_status_for_path`, and path matching semantics here.

## Risks and edge cases

- `stop` cancels the manager-level token used by scheduler and scanner. There is no token reset on `start`, so restarting the same manager may immediately stop background loops.
- The scheduler holds `active_heals_guard` while locking the queue and while spawning tasks. Other paths generally avoid reverse lock order, and the auto scanner comment explicitly uses queue-first then active to avoid deadlock.
- Forced requests bypass duplicate and full-queue admission, so queue length can exceed configured capacity.
- Completed statuses are in-memory only and expire after ten minutes; clients polling late will see not found, which the channel may translate to finished.
- Auto scanner pushes directly into `PriorityHealQueue` rather than calling `submit_heal_request`, so it shares queue dedup but bypasses full-queue admission policy and queue-pressure logging.
- Per-set bulkhead only applies to `HealType::ErasureSet`; object requests with pool/set options use labels for metrics but are always schedulable.
- Low-priority duplicate policy can drop a duplicate request even though an equivalent queued request exists; clients must interpret `Dropped(PolicyDropped)`.
- Displacement removes a lower-priority request without sending that displaced request's client a direct failure response unless the client later polls and sees task not found.

## Test signals

Tests cover queue priority ordering, FIFO within priority, dedup key generation, erasure-set contains checks, priority statistics, empty state, bulkhead skip behavior, per-set scheduling limits, duplicate merge, queued pending status, path-token rejection, inactive path behavior, completed status/report reads, queued cancellation by id/path, full-queue low-priority drop, high-priority displacement, and forced admission behavior. Further useful tests would cover manager stop/start reuse, auto scanner full-queue behavior, event-driven wakeups, completed-status pruning timing, and task completion metric labels.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/mod.rs -->
# sources/object-store/rustfs/crates/heal/src/heal/mod.rs

## Purpose

`mod.rs` is the module declaration and public re-export surface for the heal subsystem. It wires the submodules into the crate and exposes the primary manager, erasure healer, resume, and task types to callers.

## Important APIs, types, and functions

Declared modules are `channel`, `erasure_healer`, `event`, `manager`, `progress`, `resume`, `storage`, `task`, and `utils`. Public re-exports include:

- `ErasureSetHealer`
- `HealManager`
- `CheckpointManager`, `ResumeCheckpoint`, `ResumeManager`, `ResumeState`, `ResumeUtils`
- `HealOptions`, `HealPriority`, `HealRequest`, `HealTask`, `HealType`

## Control flow

There is no runtime control flow. The file defines compile-time module topology and which symbols downstream modules can import from `crate::heal`.

## State and persistence behavior

No state or persistence is defined here. Re-exported resume types are the durable state interface, and re-exported task/manager/healer types own runtime behavior elsewhere.

## Dependencies and integration points

The file is the integration point for internal callers that use `crate::heal::{HealManager, HealRequest, ...}` instead of reaching into individual submodules. Adding or removing module declarations changes what code is compiled; adding or removing re-exports changes the public crate-facing API.

## Risks and edge cases

- The module exposes resume internals as public re-exports, so external code can couple to checkpoint/state representation.
- `channel`, `event`, `progress`, `storage`, and `utils` are declared public modules but not all their common types are re-exported here; callers may use mixed import styles.
- Changes here have broad compile impact even though the file is small.

## Test signals

There are no direct tests for this file. Compile tests and downstream imports are the signal: if a module declaration or re-export is wrong, the crate fails to compile. API compatibility checks should watch re-export changes.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/progress.rs -->
# sources/object-store/rustfs/crates/heal/src/heal/progress.rs

## Purpose

`progress.rs` defines lightweight serializable progress and aggregate statistics models for heal tasks. It is an in-memory/status-reporting layer used by tasks and manager code, separate from durable resume/checkpoint persistence.

## Important APIs, types, and functions

- `HealProgress` stores scanned/healed/failed object counts, processed bytes, current object, progress percentage, start time, last update time, and estimated completion time.
- `HealProgress::new` initializes start and last update timestamps.
- `update_progress` sets counters and bytes, updates last-update time, and computes `progress_percentage`.
- `set_current_object` updates current object and timestamp.
- `is_completed` checks either percentage >= 100 or healed+failed >= scanned when scanned is positive.
- `get_success_rate` computes healed / (healed + failed).
- `HealStatistics` stores total/successful/failed/running tasks, total healed objects/bytes, and last update time.
- `HealStatistics::new`/`Default` initialize zero counters.
- Statistics mutators update completion counts, running counts, healed object/byte totals, and timestamps.
- `HealStatistics::get_success_rate` computes successful tasks / completed tasks.

## Control flow

All methods are synchronous data updates. `update_progress` replaces the counters rather than incrementing them. Its percentage denominator is `scanned + healed + failed`, so it behaves more like a ratio of healed to all reported counters than a conventional processed/scanned percentage. Completion can still be detected when `objects_healed + objects_failed >= objects_scanned`.

## State and persistence behavior

Both structs derive `Serialize` and `Deserialize`, but this file does not persist them. Timestamps are `SystemTime`. `estimated_completion_time` is present but not computed by this implementation. Consumers wrap these structs in locks or embed them in task state.

## Dependencies and integration points

The file depends only on `serde` and `std::time::SystemTime`. `HealManager` owns `HealStatistics`, `HealTask` and `ErasureSetHealer` use `HealProgress`, and channel/status APIs can return progress through manager methods.

## Risks and edge cases

- The progress percentage formula can be surprising: with `scanned=10`, `healed=8`, and `failed=2`, percentage is 40 rather than 100, because scanned is included in the denominator along with outcomes.
- `is_completed` may report complete even when `progress_percentage` is below 100 if healed+failed reaches scanned.
- No rate or ETA calculation is implemented despite the ETA field.
- `update_progress` can move counters backward if the caller supplies smaller values.
- Statistics do not decrement `running_tasks` automatically; callers must set the count correctly.

## Test signals

Tests cover initialization, progress updates including zero and all-healed cases, current-object timestamp updates, completion checks by percentage and processed counts, progress success rate, statistics defaults, completion updates, running count updates, healed object accumulation, and statistics success rate. Additional useful tests would document the progress-percentage semantics explicitly for UI/API consumers.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/progress.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/resume.rs -->
# sources/object-store/rustfs/crates/heal/src/heal/resume.rs

## Purpose

`resume.rs` implements disk-backed resume and checkpoint state for heal tasks, especially erasure-set healing. It serializes JSON files into the RustFS meta bucket on a `DiskStore`, provides managers for updating state safely behind async locks, and offers utilities to discover and clean resumable tasks.

## Important APIs, types, and functions

- Constants define file suffixes: `ahm_resume_state.json`, `ahm_progress.json`, and `ahm_checkpoint.json`.
- `path_to_str` validates UTF-8 paths before disk API calls.
- `ResumeState` stores task identity/type, set disk id, timestamps, completion flag, object counters, current bucket/object, completed/pending buckets, error string, retry count, and max retries.
- `ResumeState` methods update progress, current item, bucket completion, completion flag, error, retry count, retry eligibility, progress percentage, and success rate.
- `ResumeManager` owns a `DiskStore` and `Arc<RwLock<ResumeState>>`.
- `ResumeManager::new`, `load_from_disk`, `has_resume_state`, `get_state`, update methods, `cleanup`, `save_state`, and `read_state_file` are the state file API.
- `ResumeCheckpoint` stores task id, checkpoint timestamp, current bucket/object indexes, processed objects, failed objects, and skipped objects.
- `CheckpointManager` mirrors `ResumeManager` for checkpoint creation/loading/existence, position/object-list updates, cleanup, save, and read.
- `ResumeUtils` generates UUID task ids, checks resumability, lists resume files, and cleans expired states.

## Control flow

Creating a `ResumeManager` builds a fresh `ResumeState`, then attempts to save it. Initial save failures are logged as warnings but do not fail construction. Subsequent update methods modify the in-memory state under a write lock, drop the lock, then serialize and write the whole JSON state file. Loading reads the state file and deserializes it.

`save_state` writes `{task_id}_ahm_resume_state.json` under `BUCKET_META_PREFIX` in `RUSTFS_META_BUCKET`. If the disk reports `UnformattedDisk`, the save is skipped and returns success, allowing healing of unformatted disks to proceed without resume persistence on that disk. Other write errors are converted to `TaskExecutionFailed`.

`CheckpointManager` follows the same pattern but writes `{task_id}_ahm_checkpoint.json`. Unlike resume state save, checkpoint save does not special-case unformatted disks. Processed/failed/skipped object additions deduplicate by linear `Vec::contains`.

Cleanup deletes state, progress, and checkpoint files for `ResumeManager`, and checkpoint file for `CheckpointManager`, ignoring delete errors. `ResumeUtils::get_resumable_tasks` lists `BUCKET_META_PREFIX`, filters entries ending in `_ahm_resume_state.json`, strips the suffix, and returns non-empty task ids. Expired cleanup loads each task and removes states whose `last_update` age exceeds a caller-supplied hour threshold.

## State and persistence behavior

Persistence is JSON written through `DiskStore::write_all` into the metadata bucket. State writes are whole-file replacements. Resume and checkpoint managers keep an in-memory copy under `RwLock` and persist after each mutation. `RESUME_PROGRESS_FILE` is only cleaned here; this file does not create or update a separate progress JSON file.

Timestamps are Unix seconds. `ResumeState::new` initializes `pending_buckets` from the caller and leaves `total_objects` at zero. `completed_buckets` and checkpoint object lists can grow for the lifetime of a task and are stored as arrays in JSON.

## Dependencies and integration points

This file integrates with `rustfs_ecstore::disk::{DiskAPI, DiskStore, RUSTFS_META_BUCKET, BUCKET_META_PREFIX}` and `DiskError`, uses crate `Error`/`Result`, serializes through `serde_json`, and uses `uuid` for task ids. `ErasureSetHealer` uses `ResumeManager`, `CheckpointManager`, and `ResumeUtils` to resume work for a set disk id. Tests use local disk construction and temp directories.

## Risks and edge cases

- Initial save failures are warnings, so callers can believe resume is enabled even if the first state/checkpoint was not persisted.
- Resume state save ignores `UnformattedDisk`, but checkpoint save does not; new checkpoint creation logs initial failure and continues, while later checkpoint updates can fail the heal.
- Whole-file JSON writes after every object-list update can become expensive for large buckets because processed/failed/skipped vectors grow without compaction.
- Object names in checkpoint lists are not bucket-qualified.
- `cleanup_expired_states` computes `current_time - state.last_update` directly; if a corrupt/future timestamp appears, unsigned subtraction can panic in debug or underflow semantics depending on build behavior.
- `ResumeUtils::get_resumable_tasks` depends on `list_dir` returning names in a format compatible with suffix stripping; callers should verify whether returned entries include the prefix.
- `RESUME_PROGRESS_FILE` is deleted but not otherwise managed, suggesting either planned functionality or compatibility with older code.

## Test signals

Tests cover resume state creation, progress math, bucket completion bookkeeping, UUID generation, and integration listing of resumable task files while ignoring checkpoint/progress/empty-id files. Additional tests should cover load/save round trips, unformatted-disk save behavior, checkpoint updates and cleanup, expired cleanup with future timestamps, and large checkpoint performance.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/resume.rs -->
