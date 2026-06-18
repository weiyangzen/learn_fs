# subset-b-008821 research

Grouped research report for subset `subset-b-008821`. Each section is delimited for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/service.rs -->
# sources/storage-engines/tikv/components/backup/src/service.rs

## Purpose
Implements the gRPC `Backup` service facade for TiKV backup. It translates client RPC streams into internal backup tasks, snapshot-backup stream handling, and legacy pending-admin checks. The file is intentionally thin around scheduling and stream lifecycle; storage scanning and disk snapshot logic live in sibling modules.

## APIs, Types, And Functions
`Service<H: SnapshotBrHandle>` owns a `Scheduler<Task>`, disk snapshot environment, and `abort_last_req` slot. `Service::new` wires those dependencies. The `Backup` trait implementation exposes `check_pending_admin_op`, `backup`, and `prepare_snapshot_backup`. `check_pending_admin_op` calls `SnapshotBrHandle::broadcast_check_pending_admin` and forwards responses to a server stream. `backup` builds a `Task` from `BackupRequest`, schedules it, and streams `BackupResponse` values from an unbounded channel. `prepare_snapshot_backup` creates a `StreamHandleLoop`, aborts any previous stream, and runs the duplex stream on the snapshot async runtime.

## Control Flow
For normal backup, request validation happens in `Task::new`; schedule errors are converted to gRPC status and sent via `sink.fail`. Once scheduled, the response channel is drained into the RPC sink. If stream sending fails, the captured cancellation `AtomicBool` is set so the worker can stop. For snapshot backup, the newest stream replaces the previous one by aborting the stored `AbortHandle`, then `StreamHandleLoop::run` owns request processing until completion or unrecoverable error.

## State And Persistence
No persistent data is written here. Runtime state is the shared scheduler, snapshot environment, and `abort_last_req` mutex. Cancellation is communicated through task-local atomics and future abort handles. The use of an unbounded channel is called out as a TODO and can hold arbitrary responses if a client stops reading.

## Dependencies And Integration Points
Depends on `grpcio`, `kvproto::brpb`, `futures` channels/streams, TiKV worker scheduling, and raftstore snapshot backup handles. It integrates with `crate::Task`, `crate::disk_snap::Env`, and `StreamHandleLoop`. RPC clients observe only protobuf responses and gRPC errors, while internal backup workers observe scheduled `Task`s.

## Risks And Test Signals
Important risks are cancellation timing, unbounded response buffering, and correctness of "last snapshot stream wins" behavior. The included `test_client_stop` starts a real gRPC server and verifies dropped client streams do not panic and do set task cancellation. The compatibility method `check_pending_admin_op` is not deeply tested here because the test handle deliberately panics if invoked.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/service.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/softlimit.rs -->
# sources/storage-engines/tikv/components/backup/src/softlimit.rs

## Purpose
Provides backup-side concurrency throttling. `SoftLimit` is a tokio semaphore wrapper whose capacity can grow or shrink at runtime, and `SoftLimitByCpu` computes a target concurrency from observed per-thread CPU usage.

## APIs, Types, And Functions
`SoftLimit::new`, `guard`, `resize`, and `current_cap` are the production-facing surface. Test-only `shrink` and `grow` exercise explicit permit changes. Internally, `take_tokens` acquires and forgets semaphore permits to reduce capacity, while `grant_tokens` adds permits. `CpuStatistics` abstracts CPU sampling; `ThreadInfoStatistics` implements it. `SoftLimitByCpu::get_quota` calculates available task slots as idle CPUs minus a reserved remainder with a floor of one.

## Control Flow
A caller awaits `guard()` before running work; dropping the permit releases concurrency. `resize` swaps the stored cap first, then either acquires permits to shrink or adds permits to grow. CPU-based callers sample usage, exclude selected thread names, compute quota, and then resize the shared limit.

## State And Persistence
All state is in memory: semaphore permits, an atomic capacity, CPU sampler state, total CPU quota, and `keep_remain`. There is no disk persistence. Shrinking can block until enough in-flight guards are released, which is the intended backpressure mechanism.

## Dependencies And Integration Points
Uses `tokio::sync::Semaphore`, TiKV `ThreadInfoStatistics`, and `SysQuota::cpu_cores_quota`. Backup workers can use it to dynamically avoid saturating the node while leaving CPU headroom for foreground workloads.

## Risks And Test Signals
The main risk is capacity/counter drift if semaphore operations fail or callers forget that shrinking waits for live work. CPU quota is approximate and can be inaccurate when non-TiKV processes share CPUs. Tests cover resizing under live tasks and CPU quota behavior with mocked usage and reserved cores.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/softlimit.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/utils.rs -->
# sources/storage-engines/tikv/components/backup/src/utils.rs

## Purpose
Holds backup utility logic for API-version-aware key/value conversion and runtime construction. The central type, `KeyValueCodec`, normalizes transactional and RawKV backup keys and values across TiKV API versions.

## APIs, Types, And Functions
`BACKUP_V1_TO_V2_TS` is the synthetic causal timestamp used when converting RawKV V1/V1ttl to API V2. `KeyValueCodec` stores whether the operation is RawKV plus current and destination API versions. Its methods validate supported conversions, encode backup ranges, decode response keys, convert encoded raw keys/values to the destination version, validate raw values for deletion/TTL, and detect whether RawKV V2 should use MVCC snapshots. `create_tokio_runtime` creates a multi-thread tokio runtime with export I/O hooks.

## Control Flow
Backup callers construct the codec, call `check_backup_api_version`, encode request ranges, scan data, filter raw values with `is_valid_raw_value`, convert key/value encodings, and decode user-facing response ranges. The conversion paths use `dispatch_api_version!` so version-specific behavior is delegated to the `api_version` crate.

## State And Persistence
The codec is stateless after construction. It does not persist data; it determines how backup entries are represented on disk by downstream writers. Runtime creation sets thread-local file-system I/O type to `Export`, affecting accounting/classification for work executed on that runtime.

## Dependencies And Integration Points
Integrates with `api_version`, `kvproto::kvrpcpb::ApiVersion`, `txn_types::Key/TimeStamp`, file-system I/O classification, and tokio. `writer.rs` uses the codec when writing RawKV SSTs and computing checksums from decoded destination keys/values.

## Risks And Test Signals
Risks center on API-version boundary mistakes: accepting invalid V2 raw ranges, backing up deleted or expired values, or producing incompatible V2 encodings. Tests cover allowed and rejected conversion combinations, backup key encode/decode, V1/V1ttl/V2 key/value conversion, and TTL/delete validity.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/writer.rs -->
# sources/storage-engines/tikv/components/backup/src/writer.rs

## Purpose
Builds in-memory SST files for backup output and uploads them to external storage with encryption, SHA-256, CRC64-XOR, counts, byte totals, column-family metadata, and rate limiting. It supports both transactional MVCC entries and RawKV entries.

## APIs, Types, And Functions
`CfNameWrap` works around lifetime issues for async CF labels. Internal `Writer<W>` wraps an engine `SstWriter` and tracks `total_kvs`, `total_bytes`, and checksum. `BackupWriterBuilder` derives backup file names from store/region/start key and constructs `BackupWriter`. `BackupWriter` owns default and write CF writers for txn backups, with `write`, `save`, `need_split_keys`, and `need_flush_keys`. `BackupRawKvWriter` writes one CF of raw key/value pairs using `KeyValueCodec`.

## Control Flow
Txn `write` iterates `TxnEntry`s, rejects prewrites, writes non-empty default values to default CF, always writes commit metadata to write CF, and updates checksum/counts against the CF that owns the logical value. `save` uploads default CF only when non-empty and write CF when either CF has data, preserving write records even when values live in default. RawKV `write` decodes destination keys/values for checksum accounting while writing encoded bytes to SST. Upload wraps the SST reader in encryption, SHA-256 hashing, and rate limiting before calling external storage.

## State And Persistence
Buffered SST contents are in memory until `save`. Persistent artifacts are `.sst` files in external storage named from backup file base plus CF. Metadata is returned as `brpb::File` with name, size, sha256, crc64xor, kv totals, CF, and cipher IV.

## Dependencies And Integration Points
Uses `engine_traits` SST builders, `ExternalStorage`, encryption readers, `Sha256Reader`, TiKV transaction entries, key prefixing via `keys::data_key`, backup metrics, and `KeyValueCodec`. The files it returns are consumed by backup metadata assembly and restore paths.

## Risks And Test Signals
Risks include checksum mismatches, missing write CF files for default-only values, incorrect raw API decoding, memory pressure from in-memory SSTs, and upload-size assumptions when encryption changes byte layout. Tests ingest produced SSTs into RocksDB to verify empty output, write-only entries, and default+write CF contents.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/writer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/Cargo.toml -->
# sources/storage-engines/tikv/components/batch-system/Cargo.toml

## Purpose
Defines the `batch-system` crate, a reusable TiKV component for batched finite-state-machine polling with mailbox routing, metrics, and optional test/benchmark support.

## APIs, Types, And Functions
The crate exposes a default `test-runner` feature that enables the `derive_more` dependency and test helper module. Main dependencies include `crossbeam`, `dashmap`, `resource_control`, `online_config`, prometheus metrics, TiKV utilities, and kvproto.

## Control Flow
Cargo metadata selects edition 2021 and enables the test runner by default. Test and benchmark targets are registered explicitly: `tests/cases/mod.rs`, `benches/router.rs`, and `benches/batch-system.rs`, all requiring the test runner where needed.

## State And Persistence
No runtime state exists in this manifest. It controls which crate modules and dev-only benchmark/test targets compile.

## Dependencies And Integration Points
The manifest reflects the component's integration points: resource controller scheduling, online config for batch sizing, prometheus for observability, and TiKV utilities for threading and channels.

## Risks And Test Signals
Feature coupling is the main risk: benchmarks and tests rely on `test-runner`; disabling default features changes available modules. The manifest provides explicit bench/test target definitions, which are strong signals that performance and routing behavior are first-class concerns.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/benches/batch-system.rs -->
# sources/storage-engines/tikv/components/batch-system/benches/batch-system.rs

## Purpose
Criterion microbenchmarks for whole-system batch polling under load, imbalance, and fairness scenarios.

## APIs, Types, And Functions
Uses `batch_system::test_runner` to construct simple `Runner` FSMs. `end_hook` sends a completion signal through `Message::Callback`. Benchmarks are `bench_spawn_many`, `bench_imbalance`, and `bench_fairness`, grouped as `fair` and `load`.

## Control Flow
Each benchmark creates a control FSM, system/router, starts worker threads, registers normal FSM mailboxes, sends messages, then waits for callback acknowledgements before each iteration completes. The fairness benchmark additionally runs a background producer against hot FSMs while measuring whether quick tasks on other FSMs still complete.

## State And Persistence
State is transient benchmark state: registered mailboxes, atomic flags/counters, and mpsc completion channels. No persistent output is written except Criterion benchmark data outside this source file's direct concern.

## Dependencies And Integration Points
Exercises `create_system`, `BasicMailbox`, `Router::register`, `Router::send`, and shutdown behavior. It depends on the test runner model rather than production raftstore FSMs, making it a focused performance harness.

## Risks And Test Signals
These benches signal the scheduler's expected properties: high fan-out throughput, spreading hot FSMs, and avoiding starvation. They do not assert correctness but are useful regressions for scheduling algorithm or channel implementation changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/benches/batch-system.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/benches/router.rs -->
# sources/storage-engines/tikv/components/batch-system/benches/router.rs

## Purpose
Criterion microbenchmark for the hot `Router::send` path to a registered normal FSM.

## APIs, Types, And Functions
`bench_send` constructs a test batch system, registers a single `BasicMailbox`, and repeatedly sends `Message::Loop(0)` to address `1`.

## Control Flow
Setup starts the system, registers one normal FSM, then Criterion repeatedly invokes `router.send`. Shutdown occurs after the benchmark closure is registered.

## State And Persistence
Transient system state includes the control FSM, normal mailbox, scheduler channels, and worker threads. No persistent data is written.

## Dependencies And Integration Points
Focuses on router lookup, mailbox send, and FSM notification. Uses the same test runner helper as other benchmarks.

## Risks And Test Signals
Useful for detecting overhead in the most common routing operation. It does not measure end-to-end handler processing or full-channel cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/benches/router.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/batch.rs -->
# sources/storage-engines/tikv/components/batch-system/src/batch.rs

## Purpose
Core implementation of TiKV's generic batch FSM executor. It batches normal FSMs and an optional control FSM, dispatches them to `PollHandler` hooks, reschedules hot or priority-mismatched FSMs, and owns worker thread lifecycle.

## APIs, Types, And Functions
`FsmTypes` unifies normal/control/shutdown messages. `Batch` stores current polling work. `HandleResult` lets handlers continue or stop after a message progress count. `PollHandler` defines lifecycle hooks: `begin`, `handle_control`, `handle_normal`, `light_end`, `end`, and `pause`. `Poller::poll` is the main loop. `HandlerBuilder`, `BatchSystem`, `PoolState`, `BatchRouter`, and `create_system` form the public construction and execution surface.

## Control Flow
Pollers fetch from resource-control channels. If no work exists they call `pause` and block. Each round invokes `begin`, handles control first, handles existing normal FSMs, opportunistically pulls more normals up to batch size, calls `light_end`, schedules skipped FSMs, calls `end`, records metrics, and releases/removes/reschedules FSMs. Hot FSMs are periodically rescheduled to redistribute load, and priority mismatches move FSMs to the proper normal/low-priority queue.

## State And Persistence
State is entirely in memory: batch slots, scheduler channels, worker handles, joinable worker IDs, per-FSM metrics collectors, and optional `PoolStateBuilder`. There is no durable persistence. Ownership of FSMs moves between mailboxes and pollers, and shutdown sends `FsmTypes::Empty` sentinels.

## Dependencies And Integration Points
Uses `resource_control::channel`, TiKV threading utilities, metrics from `metrics.rs`, scheduler types, mailbox ownership, file-system I/O type labeling, failpoints, and online `Config` updates. Higher-level TiKV systems plug in concrete normal/control FSMs and handlers.

## Risks And Test Signals
High-risk areas are ownership release/removal correctness, starvation under hot FSMs, shutdown races, and handler contracts around `StopAt` progress. Tests and benches cover basic execution, priorities, resource-group scheduling, and benchmark fairness/load patterns. Metrics provide production signals for schedule wait, poll duration, rounds, counts, and reschedules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/batch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/config.rs -->
# sources/storage-engines/tikv/components/batch-system/src/config.rs

## Purpose
Defines online-configurable parameters for the batch system worker pool.

## APIs, Types, And Functions
`Config` includes `max_batch_size`, `pool_size`, `reschedule_duration`, and `low_priority_pool_size`. `max_batch_size()` returns the configured size or the test/default fallback of 256. `Default` uses pool size 2, reschedule duration 5s, and one low-priority worker.

## Control Flow
The batch system consumes `Config` during `create_system` and poller construction. `PollHandler::begin` receives an update callback so online config can refresh max batch size between rounds. `reschedule_duration` and low-priority pool size are skipped for online config.

## State And Persistence
The struct is serializable/deserializable and may be persisted in TiKV config files by surrounding systems. Runtime copies are immutable except online config refresh points.

## Dependencies And Integration Points
Uses `online_config::OnlineConfig`, serde, and `ReadableDuration`. Integrated directly by `batch.rs`.

## Risks And Test Signals
The fallback max batch size exists because tests may bypass validation. Misconfigured pool sizes affect throughput and fairness; reschedule duration changes hot-FSM redistribution.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/fsm.rs -->
# sources/storage-engines/tikv/components/batch-system/src/fsm.rs

## Purpose
Defines the finite-state-machine abstraction, scheduler abstraction, priorities, and atomic ownership holder used by mailboxes and pollers.

## APIs, Types, And Functions
`Priority` is `Low` or `Normal`. `FsmScheduler` schedules boxed FSMs, shuts down its resources, and can charge message resource usage. `Fsm` defines message type, metrics label, stopped status, optional mailbox attach/take, and priority. `FsmState<N>` owns an FSM pointer and tracks states `NOTIFIED`, `IDLE`, and `DROP`.

## Control Flow
`FsmState::take_fsm` atomically transitions IDLE to NOTIFIED and extracts the boxed FSM. `notify` takes the FSM, installs the mailbox, and schedules it. `release` returns an FSM to IDLE unless the state was concurrently marked DROP, in which case the FSM is dropped. `clear` marks DROP and drops any idle FSM.

## State And Persistence
State is in-memory and intentionally low-level: an `AtomicUsize` status, an `AtomicPtr`, and shared state count. No persistence exists. The unsafe pointer ownership is guarded by atomic state transitions.

## Dependencies And Integration Points
Integrated by `BasicMailbox`, `Router`, and schedulers. Messages must implement `ResourceMetered` so resource control can be charged before scheduling.

## Risks And Test Signals
The main risk is status/data inconsistency causing double free, leak, or panic. The implementation panics on invalid release states, making bugs visible. Router tests indirectly validate drop counts and mailbox cleanup via `state_cnt`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/fsm.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/lib.rs -->
# sources/storage-engines/tikv/components/batch-system/src/lib.rs

## Purpose
Crate root for the batch-system component. It declares modules and re-exports the public API used by TiKV subsystems and tests.

## APIs, Types, And Functions
Exports `BatchRouter`, `BatchSystem`, `FsmTypes`, `HandleResult`, `HandlerBuilder`, `PollHandler`, `Poller`, `PoolState`, `create_system`, `Config`, `Fsm`, `FsmScheduler`, `Priority`, `BasicMailbox`, `Mailbox`, `FsmType`, and `Router`. The optional `test_runner` module is public only when the feature is enabled.

## Control Flow
No runtime control flow exists in this file. It controls module visibility and public API shape.

## State And Persistence
No state is stored here.

## Dependencies And Integration Points
Acts as the integration boundary for users of the crate, hiding internal module paths while preserving access to core traits and constructors.

## Risks And Test Signals
Changing re-exports is a compatibility risk for all TiKV components using `batch_system::*`. Tests and benches rely on the exported `test_runner` and core types.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/mailbox.rs -->
# sources/storage-engines/tikv/components/batch-system/src/mailbox.rs

## Purpose
Implements message mailboxes that pair a channel with atomic FSM ownership. Mailboxes deliver messages and notify schedulers when an idle FSM should be polled.

## APIs, Types, And Functions
`BasicMailbox<Owner>` stores a `LooseBoundedSender` and `Arc<FsmState<Owner>>`. It exposes `new`, `len`, `is_empty`, `force_send`, and `try_send`; crate-private methods handle connection status, ownership release/take, and close. `Mailbox<Owner, Scheduler>` wraps a basic mailbox with a scheduler for ergonomic `force_send` and `try_send`.

## Control Flow
Both send methods first charge message resource usage through the scheduler, enqueue the message, and then call `FsmState::notify`. `force_send` bypasses channel capacity; `try_send` respects it. Closing the mailbox closes the sender and clears the FSM state.

## State And Persistence
All state is in memory. Cloned mailboxes share the sender and FSM state. The mailbox is responsible for temporarily transferring FSM ownership to a poller and later accepting it back through `release`.

## Dependencies And Integration Points
Uses TiKV loose bounded mpsc channels, crossbeam send errors, `FsmState`, and `FsmScheduler`. Routers store `BasicMailbox` values and return high-level `Mailbox` handles to callers.

## Risks And Test Signals
Resource leaks, duplicate scheduling, or dropped idle FSMs are key risks. Router tests exercise full, disconnected, force-send, close, and drop behavior; batch tests exercise normal message scheduling through mailboxes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/mailbox.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/metrics.rs -->
# sources/storage-engines/tikv/components/batch-system/src/metrics.rs

## Purpose
Defines prometheus metrics for batch-system channels, scheduling, polling, and broadcast operations.

## APIs, Types, And Functions
`FsmType` has static labels `store` and `apply`. Auto-flush local metric vectors cover reschedule count, schedule wait duration, poll duration, poll rounds, and FSM count per poll. Global metrics include `CHANNEL_FULL_COUNTER_VEC`, histogram vectors for FSM timing/counting, and `BROADCAST_NORMAL_DURATION`.

## Control Flow
No direct control flow beyond lazy static registration. Runtime code in router and batch modules increments counters and observes histograms at send, schedule, poll, reschedule, and broadcast points.

## State And Persistence
Prometheus collectors store process-local metric state and export through the wider TiKV metrics subsystem. No source-level persistence exists.

## Dependencies And Integration Points
Uses `prometheus`, `prometheus_static_metric`, and `lazy_static`. `Fsm::FSM_TYPE` selects labels for each concrete FSM.

## Risks And Test Signals
Metric registration names are externally visible and should remain stable. Label cardinality is intentionally fixed by static enums. Runtime tests do not assert metric values, so regressions are mainly caught by compile-time label usage and production observability.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/router.rs -->
# sources/storage-engines/tikv/components/batch-system/src/router.rs

## Purpose
Routes messages to normal FSM mailboxes by address and to the single control FSM. It also owns registration, shutdown, broadcast, and lightweight leak tracing.

## APIs, Types, And Functions
`RouterTrace` reports alive and leaked mailbox counts. `Router<N,C,Ns,Cs>` stores a `DashMap<u64, BasicMailbox<N>>`, a control mailbox, normal/control schedulers, shared state count, and shutdown flag. Important methods include `register`, `send_and_register`, `register_all`, `mailbox`, `control_mailbox`, `try_send`, `send`, `force_send`, `send_control`, `force_send_control`, `broadcast_normal`, `broadcast_shutdown`, `close`, `alive_cnt`, and `trace`.

## Control Flow
Normal sends look up a mailbox, try to enqueue through it, convert full/disconnected/missing cases into either send errors or returned messages, and increment channel-full metrics. `force_send` retries with mailbox `force_send` if bounded send reports full. Shutdown closes all normal mailboxes, clears the map, closes control, and asks both schedulers to shut down. `close` removes one mailbox and shrinks the map when excess capacity grows.

## State And Persistence
Router state is in-memory and shared by clones. Mailbox map entries own normal FSM states. The shutdown flag alters `force_send` handling so disconnected sends after shutdown can be treated as success.

## Dependencies And Integration Points
Integrates `DashMap`, mailbox types, scheduler traits, TiKV `Either`, and batch-system metrics. Higher-level raftstore/apply systems use region IDs or similar addresses as router keys.

## Risks And Test Signals
Risks include stale mailbox handles, capacity-full behavior, replacement closing old mailboxes, and state-count leaks. Tests validate missing sends, force send, full channel handling, close/drop resource release, shutdown, and `RouterTrace` accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/router.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/scheduler.rs -->
# sources/storage-engines/tikv/components/batch-system/src/scheduler.rs

## Purpose
Implements concrete schedulers that enqueue normal and control FSMs into poller channels.

## APIs, Types, And Functions
`NormalScheduler<N,C>` holds normal and low-priority resource-control senders. `ControlScheduler<N,C>` holds the normal-priority sender for control FSMs. Both implement `Clone` and `FsmScheduler`.

## Control Flow
Normal scheduling checks `fsm.get_priority()` and sends `FsmTypes::Normal` with a coarse schedule timestamp to the matching queue. Control scheduling sends `FsmTypes::Control`. Shutdown sends 256 `FsmTypes::Empty` sentinels to wake pollers because explicit channel close is not available. Normal message resource consumption delegates to the resource-control sender; control messages are not charged here.

## State And Persistence
Schedulers only hold channel handles. Schedule timestamps become metric input when `Batch::push` observes wait duration.

## Dependencies And Integration Points
Uses `resource_control::channel::Sender`, crossbeam `SendError`, TiKV time utilities, and `FsmTypes`. Constructed by `create_system` and stored by `Router`.

## Risks And Test Signals
The magic shutdown count assumes it exceeds possible poller count. Failed sends are logged but not retried. Priority routing is covered by `test_priority`, and resource charging is covered by `test_resource_group`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/scheduler.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/test_runner.rs -->
# sources/storage-engines/tikv/components/batch-system/src/test_runner.rs

## Purpose
Provides a simple FSM and handler implementation for batch-system tests and benchmarks.

## APIs, Types, And Functions
`Message` has `Loop`, `Callback`, and `Resource` variants and implements `ResourceMetered`. `Runner` is a test FSM with receiver, mailbox, optional sender, result accumulator, and priority. `HandleMetrics` tracks handler calls. `Handler` consumes up to 16 messages per invocation and implements `PollHandler<Runner, Runner>`. `Builder` constructs handlers with shared metrics and pause counters.

## Control Flow
Tests create `Runner::new` sender/FSM pairs, wrap them in mailboxes, and register them. Handler loops perform synthetic CPU work, execute callbacks, or consume resource messages. `handle_control` and `handle_normal` both process messages and report progress zero so the batch system releases the FSM until new messages arrive.

## State And Persistence
All state is transient. Shared metrics are stored in `Arc<Mutex<HandleMetrics>>`, pause counts in `Arc<AtomicUsize>`, and priority in each runner.

## Dependencies And Integration Points
Integrates with `ResourceController`, TiKV mpsc, batch traits, and optional `derive_more` arithmetic derives. It is feature-gated by the crate's `test-runner` feature.

## Risks And Test Signals
Because tests and benches depend on this helper, changes can mask or create false failures in batch-system validation. Its resource message support is key to testing resource-control ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/src/test_runner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/tests/cases/batch.rs -->
# sources/storage-engines/tikv/components/batch-system/tests/cases/batch.rs

## Purpose
Integration-style tests for batch-system execution, priority routing, and resource-group scheduling.

## APIs, Types, And Functions
Defines `test_batch`, `test_priority`, and `test_resource_group`. Uses `Runner`, `Builder`, `BasicMailbox`, `Router`, `Config`, and `ResourceGroupManager`.

## Control Flow
`test_batch` sends a control callback that registers a normal FSM, then sends a normal callback and verifies handler metrics. `test_priority` registers normal and low-priority runners and asserts they are handled by matching-priority handlers. `test_resource_group` blocks the single poller, queues messages for two resource groups, releases the block, and expects the group with more tokens to run first.

## State And Persistence
State is confined to test channels, resource manager configuration, and running worker threads. No persistence.

## Dependencies And Integration Points
Exercises the public crate API and `kvproto::resource_manager` group settings. It validates integration between resource-control channels and scheduler message charging.

## Risks And Test Signals
These are strong signals for scheduler correctness beyond simple routing. Timing sleeps and blocking channels introduce some test sensitivity, but the assertions cover essential behavior expected by production raftstore/apply users.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/tests/cases/batch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/tests/cases/mod.rs -->
# sources/storage-engines/tikv/components/batch-system/tests/cases/mod.rs

## Purpose
Test module entry point for the batch-system crate.

## APIs, Types, And Functions
Declares `mod batch;` and `mod router;`, making the two test files part of the `tests` target defined in Cargo.toml.

## Control Flow
No runtime logic exists here beyond Rust test discovery through module inclusion.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Connects the Cargo test target to the batch and router test suites. Requires the crate's `test-runner` feature via Cargo target metadata.

## Risks And Test Signals
Removing a module declaration would silently drop an entire suite from the `tests` target. Its existence confirms router and batch behavior are both covered.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/tests/cases/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/tests/cases/router.rs -->
# sources/storage-engines/tikv/components/batch-system/tests/cases/router.rs

## Purpose
Tests router send semantics, capacity behavior, close/shutdown cleanup, and mailbox leak tracing.

## APIs, Types, And Functions
Helper messages include `counter_closure`, `noop`, and an intentionally unreachable callback. Tests are `test_basic` and `test_router_trace`.

## Control Flow
`test_basic` verifies missing mailbox errors, registers a mailbox from a control callback, tests normal and force sends, fills a channel to observe `Full`, unblocks and flushes callbacks, closes the mailbox, and then shuts down the system. `test_router_trace` registers 10 runners, holds mailbox handles, closes router entries, and checks `state_cnt` only drops after handles are released.

## State And Persistence
State is in-memory test routers, mailboxes, channels, and atomic counters. Drop notifications are observed by receiver disconnection.

## Dependencies And Integration Points
Exercises `Router`, `BasicMailbox`, mpsc capacity behavior, `BatchSystem::shutdown`, and `RouterTrace` state accounting.

## Risks And Test Signals
Strongly validates edge cases around disconnected/full sends and resource release. It also documents expected behavior that external mailbox handles can keep FSM state alive after router close.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/batch-system/tests/cases/router.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/causal_ts/Cargo.toml -->
# sources/storage-engines/tikv/components/causal_ts/Cargo.toml

## Purpose
Defines the `causal_ts` crate, which provides causal timestamp provider abstractions and PD-backed TSO caching.

## APIs, Types, And Functions
The package is non-published, edition 2021, with a `testexport` feature. Dependencies include async traits, enum dispatch, PD client, prometheus, parking_lot, tokio sync, TiKV worker/utilities, and transaction timestamps. A Criterion bench target `tso` is defined.

## Control Flow
Cargo feature selection controls test exports and benchmark availability. The manifest keeps `test_pd_client` in dependencies because both `lib.rs` and benches require it.

## State And Persistence
No runtime state in the manifest. It configures compilation and dependency graph.

## Dependencies And Integration Points
Shows core integration with PD, transaction timestamp types, metrics, and test PD clients. This crate is consumed by CDC and other components needing causal timestamps.

## Risks And Test Signals
Keeping test client dependencies in normal dependencies is noted as a TODO and may affect dependency surface. The explicit `tso` benchmark signals performance sensitivity of timestamp cache operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/causal_ts/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/causal_ts/benches/tso.rs -->
# sources/storage-engines/tikv/components/causal_ts/benches/tso.rs

## Purpose
Criterion benchmarks for the cached TSO list and PD-backed batch provider.

## APIs, Types, And Functions
Benchmarks include `bench_batch_tso_list_pop`, `bench_batch_tso_list_push`, `bench_batch_tso_provider_get_ts`, and `bench_batch_tso_provider_flush`. They use `TsoBatchList`, `BatchTsoProvider`, `CausalTsProvider`, `TestPdClient`, and `TimeStamp`.

## Control Flow
List pop benchmarks prefill batches, then repeatedly pop. Push benchmarks repeatedly insert batches. Provider benchmarks construct a provider with background renewal disabled by `Duration::ZERO`, then call `async_get_ts` or `async_flush` through `block_on`.

## State And Persistence
All state is in-memory benchmark state, including fake PD client TSO and cached batch lists.

## Dependencies And Integration Points
Exercises both the low-level cache and the high-level provider API. Uses the same test PD client as unit tests to avoid real PD dependency.

## Risks And Test Signals
Useful for detecting lock/contention overhead in `TsoBatchList` and async-channel overhead in provider renew/flush paths. It does not validate correctness beyond successful execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/causal_ts/benches/tso.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/causal_ts/src/config.rs -->
# sources/storage-engines/tikv/components/causal_ts/src/config.rs

## Purpose
Defines user-facing configuration for `BatchTsoProvider`.

## APIs, Types, And Functions
`Config` contains `renew_interval`, `renew_batch_min_size`, `renew_batch_max_size`, and `alloc_ahead_buffer`. `validate` rejects zero interval, zero min/max batch size, and zero allocation-ahead buffer. `Default` maps to constants from `tso.rs`.

## Control Flow
Configuration is deserialized with kebab-case names and passed into provider construction by surrounding TiKV code. Validation prevents nonsensical production settings; tests can still call lower-level constructors with zero renewal interval to disable background renewal.

## State And Persistence
The struct is serializable and likely persisted in TiKV config. Runtime provider state is derived from it, including cache multiplier and batch size bounds.

## Dependencies And Integration Points
Uses serde derives and `ReadableDuration`. Depends on `crate::tso` constants for defaults.

## Risks And Test Signals
Incorrect validation could permit providers that never renew or request zero TSOs. The code-level defaults encode operational assumptions about PD throughput and desired failure tolerance.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/causal_ts/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/causal_ts/src/errors.rs -->
# sources/storage-engines/tikv/components/causal_ts/src/errors.rs

## Purpose
Defines causal timestamp provider error types and maps them to TiKV error codes.

## APIs, Types, And Functions
`Error` variants are `Pd`, `Tso`, `TsoBatchUsedUp`, `BatchRenew`, and `Other`. `Result<T>` aliases the crate result type. `ErrorCodeExt` maps variants to `error_code::causal_ts` codes or `UNKNOWN`.

## Control Flow
Provider code uses `?` conversions from PD errors and boxed errors. Batch renew failures wrap shared error objects in `Arc` so coalesced request waiters can receive cloned results.

## State And Persistence
Errors carry no persistent state, but their codes become externally visible through TiKV error handling and logging.

## Dependencies And Integration Points
Integrates with `pd_client`, `error_code`, `thiserror`, and the rest of the causal_ts crate.

## Risks And Test Signals
Precise error classification matters for diagnostics. `TsoBatchUsedUp` includes the last batch size, which helps identify under-renew or PD failure conditions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/causal_ts/src/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/causal_ts/src/lib.rs -->
# sources/storage-engines/tikv/components/causal_ts/src/lib.rs

## Purpose
Crate root and public abstraction for causal timestamp providers.

## APIs, Types, And Functions
Exports config, errors, TSO implementation, and metrics. `CausalTsProvider` is an async trait with `async_get_ts` and `async_flush`. `CausalTsProviderImpl` uses `enum_dispatch` to wrap production `BatchTsoProvider<pd_client::RpcClient>`, test provider variants, and `TestProvider`.

## Control Flow
Consumers call the trait methods without knowing the provider implementation. `async_flush` is explicitly for causality-sensitive events such as leader transfer, where cached timestamps must be discarded and a new timestamp returned.

## State And Persistence
The root file has no state. The nested test provider uses an atomic timestamp starting at 100 and increments or jumps by 100 on flush.

## Dependencies And Integration Points
Uses `async_trait`, `enum_dispatch`, `txn_types::TimeStamp`, PD client types, and test PD client under test/testexport. CDC depends on this crate for causal timestamp behavior.

## Risks And Test Signals
Trait semantics are important: providers must return monotonically valid timestamps and flush must enforce causality. The test provider's fixed jump size is part of unit-test expectations and should not be changed casually.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/causal_ts/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/causal_ts/src/metrics.rs -->
# sources/storage-engines/tikv/components/causal_ts/src/metrics.rs

## Purpose
Defines prometheus metrics for timestamp provider cache size, request latency, renew latency, and batch-list counts.

## APIs, Types, And Functions
Global collectors include `TS_PROVIDER_TSO_BATCH_SIZE`, `TS_PROVIDER_GET_TS_DURATION`, `TS_PROVIDER_TSO_BATCH_RENEW_DURATION`, and `TS_PROVIDER_TSO_BATCH_LIST_COUNTING`. Static labels include renew reasons `init`, `background`, `used_up`, `flush`; counting kinds `tso_usage`, `tso_remain`, `new_batch_size`; and result kinds `ok`/`err`. `From<&Result>` converts success/failure to metric labels.

## Control Flow
Provider code observes get-ts and renew durations, reports usage/remain/new batch sizes, and sets total batch size after renew attempts.

## State And Persistence
Metrics live in prometheus collectors and are exported by the process. No durable state is written.

## Dependencies And Integration Points
Uses `prometheus`, `prometheus_static_metric`, and `lazy_static`. `tso.rs` is the primary consumer.

## Risks And Test Signals
Metric names and labels are operational interfaces. Histograms cover very small get-ts latencies and long renew durations, matching cache-fast-path and PD-slow-path expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/causal_ts/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/causal_ts/src/tso.rs -->
# sources/storage-engines/tikv/components/causal_ts/src/tso.rs

## Purpose
Implements a PD-backed causal timestamp provider that caches ranges of TSOs, renews them adaptively, and tolerates short PD failures by allocating ahead.

## APIs, Types, And Functions
`TsoBatch` represents one logical timestamp range for a physical time. `TsoBatchList` is an ordered, lock-protected collection with `pop`, `push`, `flush`, `remain`, `usage`, and `take_and_report_usage`. `BatchTsoProvider<C: PdClient>` owns the PD client, shared batch list, TiKV worker, renewal parameters, interval, and renewal request channel. Public constructors are `new` and `new_opt`; provider methods implement `CausalTsProvider`. `SimpleTsoProvider` is a request-per-call test implementation.

## Control Flow
Initialization spawns a renew worker, performs an initial flush renew, and optionally schedules periodic background renew. `async_get_ts` first pops from cache; if empty, it renews up to three times for `used_up` before returning `TsoBatchUsedUp`. `async_flush` renews with `need_flush`, then returns the first new timestamp. Renew requests are coalesced in `renew_thread`; if any request needs flush, the single PD batch renew flushes old cached TSOs before inserting the new range.

## State And Persistence
State is in memory: ordered timestamp batches, approximate remain/usage counters, atomic allocation offsets, renewal request channel, worker tasks, and metrics. There is no durable timestamp persistence in this file; monotonicity depends on PD-provided TSOs and local rejection of fallback ranges.

## Dependencies And Integration Points
Depends on `pd_client::PdClient::batch_get_tso`, TiKV workers, tokio channels/oneshots, parking_lot `RwLock`, metrics, and `txn_types::TimeStamp`. Higher-level components use the `CausalTsProvider` trait.

## Risks And Test Signals
Critical risks are timestamp fallback, losing causality on flush, stale batches under concurrent readers, counter imprecision, PD renew failure behavior, and large allocation pressure. `RwLock<BTreeMap>` is intentionally chosen so flush synchronization prevents readers from acquiring removed batches. Tests cover batch boundaries, adaptive batch sizing, fallback rejection, capacity eviction, pop-after-ts, simple provider, provider renew/flush/used-up behavior, and failure recovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/causal_ts/src/tso.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/Cargo.toml -->
# sources/storage-engines/tikv/components/cdc/Cargo.toml

## Purpose
Defines the TiKV `cdc` crate and its broad dependency/feature surface for change-data-capture service code.

## APIs, Types, And Functions
Features select test engines, allocator backends, portable/SSE builds, memory profiling, and failpoints. Dependencies include API versioning, causal timestamps, concurrency manager, raftstore, resolved-ts, grpcio, protobuf, online config, PD client, engine traits, and TiKV core crates. Test targets include integration and failpoint suites; benchmark target `cdc_event` measures event sizing.

## Control Flow
Cargo feature selection controls engine backend and test/failpoint compilation. Failpoint tests are isolated in a separate target to avoid interfering with normal tests.

## State And Persistence
The manifest has no runtime state. It controls compile-time composition of CDC service code.

## Dependencies And Integration Points
Shows CDC's integration breadth: storage engines, raftstore events, resolved timestamp tracking, causal timestamp provider, gRPC streaming, and online config.

## Risks And Test Signals
Feature matrix complexity is a risk, especially allocator and engine-test feature interactions. Separate integration/failpoint tests and the event-size benchmark indicate both correctness and stream sizing are important.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/benches/cdc_event.rs -->
# sources/storage-engines/tikv/components/cdc/benches/cdc_event.rs

## Purpose
Benchmarks the optimized `CdcEvent::ResolvedTs::size` approximation against protobuf `compute_size`.

## APIs, Types, And Functions
`bench_cdc_event_size` builds `ResolvedTs` messages with region counts from 1 to 131,072 and compares `protobuf::Message::compute_size` with `CdcEvent::ResolvedTs::size`.

## Control Flow
For each region-count input, the benchmark group registers two benchmark functions: protobuf compute size and CDC's custom size method.

## State And Persistence
Only benchmark-local protobuf messages are created. No persistence.

## Dependencies And Integration Points
Uses `cdc::CdcEvent`, `kvproto::cdcpb::ResolvedTs`, protobuf sizing, and Criterion.

## Risks And Test Signals
The benchmark exists because resolved-ts messages can list many regions and size calculation is on the stream batching path. Unit tests also assert the approximation matches protobuf size for typical region IDs and TSOs.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/benches/cdc_event.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/channel.rs -->
# sources/storage-engines/tikv/components/cdc/src/channel.rs

## Purpose
Implements CDC event channels, memory accounting, batching into gRPC `ChangeDataEvent` responses, barrier handling, and drain cleanup.

## APIs, Types, And Functions
`CdcEvent` variants are `ResolvedTs`, `Event`, and `Barrier`. `CdcEvent::size` computes approximate or protobuf sizes. `EventBatcher` groups events under `CDC_RESP_MAX_BYTES`, keeps resolved-ts messages isolated, and tracks byte statistics. `channel` returns a `Sink`/`Drain` pair. `Sink::unbounded_send` sends observed events and `Sink::send_all` sends scanned events through a bounded channel with shared truncation flag. `Drain::drain` merges scanned and observed streams, frees truncated scanned events, records pending duration, and fires barriers. `Drain::forward` batches drained events into gRPC sink messages with buffered write flags.

## Control Flow
Observed events use an unbounded channel but are constrained by memory quota unless forced. Scanned events pre-allocate total quota, feed the bounded channel, and free quota on send failure. Draining selects between both streams, skips truncated scanned events, and returns `(event, size)`. Forwarding chunks up to 64 CDC events, builds one or more `ChangeDataEvent` responses, frees pending memory just before sending, feeds all responses with buffer hints, flushes the sink, records flush activity, and increments byte metrics.

## State And Persistence
State is in memory: futures channels, `MemoryQuota`, event timestamps, truncation flags, batching buffers, and connection ID. No persistent data is written. `Drop for Drain` closes receivers and synchronously drains remaining events to free memory quota, warning if this takes at least 200 ms.

## Dependencies And Integration Points
Depends on futures streams/sinks, grpcio `WriteFlags`, kvproto CDC protobufs, protobuf sizing, TiKV memory quota utilities, CDC metrics, connection IDs, and watchdog `FlushActivity`. It is the stream transport layer for CDC event-feed RPCs.

## Risks And Test Signals
Key risks are memory quota leaks, oversized response batching, resolved-ts ordering/isolation, barrier semantics, forced error-event sends bypassing quota, and blocking drain drop. Tests cover scanned truncation, barriers, nonblocking batching, congestion, capacity changes, force sends, memory leak scenarios, event batching layout/statistics, and resolved-ts size correctness. Failpoints can force event size or post-flush sleep.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/channel.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/config.rs -->
# sources/storage-engines/tikv/components/cdc/src/config.rs

## Purpose
Provides an online config manager adapter for CDC.

## APIs, Types, And Functions
`CdcConfigManager(pub Scheduler<Task>)` implements `online_config::ConfigManager`. `dispatch` schedules `Task::ChangeConfig(change)` on the CDC worker scheduler. `Deref` exposes the underlying `Scheduler<Task>`.

## Control Flow
When online config changes arrive, the config framework calls `dispatch`; CDC handles the change asynchronously as a worker task rather than applying it in the config callback thread.

## State And Persistence
The manager stores only a scheduler handle. Actual config state and persistence live in the broader TiKV online config system and CDC task handler.

## Dependencies And Integration Points
Uses `online_config::{ConfigChange, ConfigManager}`, TiKV worker `Scheduler`, and crate-level `Task`. It bridges config infrastructure to CDC's internal task loop.

## Risks And Test Signals
Scheduling errors propagate as boxed errors. The main risk is delayed or failed application if the CDC scheduler is stopped or congested. This small adapter has no local tests in the file; coverage likely comes from CDC integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/config.rs -->
