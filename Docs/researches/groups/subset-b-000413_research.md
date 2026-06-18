# Research: subset-b-000413

This grouped report covers the requested io-engine core, eventing, fault-injection, and controller gRPC files. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/device_events.rs -->
# sources/control-plane/mayastor/io-engine/src/core/device_events.rs

## Purpose
Defines the in-process device event listener model used by block-device implementations and nexus children. It lets device owners publish removal, resize, media, and NVMe admin-queue failure events without hard-coupling to the nexus logic that reacts to them.

## Important APIs, Types, and Functions
- `DeviceEventType` enumerates operational events: `DeviceRemoved`, `LoopbackRemoved`, `DeviceResized`, `MediaManagement`, `AdminCommandCompletionFailed`, `AdminQNoticeCtrlFailed`, and `AdminQBroken`.
- `DeviceEventListener` is the consumer trait with `handle_device_event(evt, dev_name)` and optional `get_listener_name`.
- `DeviceEventSink` wraps a listener in an `Arc` and exposes a weak reference to the dispatcher.
- `DeviceEventDispatcher` stores `Weak<SinkInner>` listeners, supports `add_listener`, `dispatch_event`, `count`, and internal `purge`.

## Control Flow and State
Callers create a `DeviceEventSink` from a listener and retain a clone as the lifetime anchor. `DeviceEventDispatcher::add_listener` stores only a weak reference, then purges stale entries. `dispatch_event` upgrades live weak references into temporary `Arc`s while holding the listener-list mutex, drops the mutex before invoking callbacks, and purges again afterwards.

State is entirely memory resident. There is no persistence; listener retention is intentionally driven by `Arc` ownership outside the dispatcher.

## Dependencies and Integration Points
Uses `parking_lot::Mutex` and `Arc`/`Weak`. Integrated from `core/mod.rs`, bdev/device event dispatch, NVMe controller notifications, and nexus child handling. Nexus implements `DeviceEventListener` in `nexus_bdev_children.rs`.

## Risks and Test Signals
The sink uses `transmute` to convert a borrowed trait object to `'static`, relying on the caller retaining the actual listener for as long as its `DeviceEventSink` exists. Misuse can create dangling references. The dispatcher avoids callback-under-lock deadlocks, which is a key concurrency property to preserve. Tests should exercise listener drop/purge behavior, multiple listeners, and dispatch during callbacks that mutate registration state.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/device_events.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/device_monitor.rs -->
# sources/control-plane/mayastor/io-engine/src/core/device_monitor.rs

## Purpose
Provides a lightweight asynchronous monitor loop for deferred device-management commands. Its current command closes or retires a failed child from a nexus on the primary reactor rather than directly from the device event callback path.

## Important APIs, Types, and Functions
- `DeviceCommand::RetireDevice { nexus_name, child_device }` is the only queued command.
- `DEV_CMD_QUEUE` is a global `WorkQueue<DeviceCommand>`.
- `device_cmd_queue()` exposes the queue to device-event handlers.
- `device_monitor_loop()` polls the queue every 10 ms and schedules work on the primary SPDK thread with `Reactor::spawn_at_primary`.

## Control Flow and State
Producers enqueue `RetireDevice` commands, for example when a nexus child receives device removal or admin-queue failure events. The monitor loop ticks forever. For each command it looks up the nexus by name, calls `close_child(child_device).await`, logs verbose errors, and awaits the oneshot returned by `spawn_at_primary`.

State is volatile queue state only. Commands are not persisted, deduplicated, or retried after process restart.

## Dependencies and Integration Points
Depends on `WorkQueue`, `Reactor`, `nexus_lookup`, and `VerboseError`. It bridges event paths into reactor-affine nexus mutation, avoiding direct manipulation from arbitrary async contexts.

## Risks and Test Signals
The loop consumes one command per tick and has no backpressure beyond the unbounded `SegQueue`; a storm of device events can build latency. Failed scheduling logs and drops the command. Tests should verify retire commands are scheduled on primary, nexus lookup absence is harmless, close errors are logged, and queue ordering/throughput remain acceptable under bursts.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/device_monitor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/diagnostics.rs -->
# sources/control-plane/mayastor/io-engine/src/core/diagnostics.rs

## Purpose
Implements reactor/process diagnostics, primarily stack dumping when reactor freeze detection decides a reactor has stopped responding.

## Important APIs, Types, and Functions
- `diagnose_reactor(&Reactor)` logs core, TID, and state, then spawns stack collection.
- `process_diagnostics_cli(&MayastorCliArgs)` handles the hidden `--diagnose-stack` CLI path and returns a trace result.
- `collect_process_stack(pid)` uses `rstack::TraceOptions` to print per-thread frames to stdout.
- `dump_self_stack()` re-executes the current io-engine binary with `--diagnose-stack <pid>` and logs stdout.

## Control Flow and State
Freeze detection calls `diagnose_reactor`; this logs the frozen reactor and launches a Tokio task. The task runs a separate process so stack collection can be isolated from the hung runtime path. When invoked in CLI diagnostic mode, the process traces the requested PID and prints thread names plus symbolized frames.

No persistent state is stored. Diagnostic output goes to logs or stdout depending on mode.

## Dependencies and Integration Points
Depends on `async_process`, `rstack`, `MayastorCliArgs`, and `Reactor`. It is called from `reactor_monitor_loop` in `reactor.rs` and from CLI bootstrap before normal environment startup.

## Risks and Test Signals
`String::from_utf8(output.stdout).unwrap()` can panic on invalid output, though diagnostic command output is expected UTF-8. Stack tracing may need privileges and symbols. Tests should cover CLI routing, invalid PID errors, and that freeze diagnostics do not block the monitor loop.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/diagnostics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/env.rs -->
# sources/control-plane/mayastor/io-engine/src/core/env.rs

## Purpose
Owns io-engine process configuration and lifecycle. It parses CLI/environment options, initializes logging, DPDK/EAL, SPDK subsystems, memory pools, reactors, persistent store, gRPC, registration, tracing, and graceful shutdown.

## Important APIs, Types, and Functions
- `MayastorCliArgs` is the clap command surface for gRPC, registration, EAL, memory, pool config, persistent store, events, reactor freeze detection, feature flags, coredump, tracing, and NVMe limits.
- `MayastorEnvironment` is the runtime environment snapshot and global/default store.
- `MayastorEnvironment::new`, `init`, `start`, and `fini` implement process lifecycle.
- `mayastor_env_stop`, `do_shutdown`, `mayastor_signal_handler`, and `signal_trampoline` coordinate graceful shutdown.
- Parsers include `parse_mb`, `parse_ps_timeout`, `parse_crdt`, `parse_grpc_ip`, and feature compatibility parser `delay_compat`.
- Feature access is provided through `MayastorFeatures::get`.

## Control Flow and State
`new` converts CLI args into environment fields and installs the global default. `init` initializes SPDK logging, optionally prints ASAN metadata, loads YAML config, prepares PTPL paths and pool config, initializes EAL, creates I/O context mempools, installs signals, sets feature globals, initializes reactors, launches remote cores, enters the primary SPDK thread, starts tracing, and calls `spdk_subsystem_init` until the RPC server is ready. `start` builds a current-thread Tokio runtime, optionally connects the persistent store, enters master interrupt mode, schedules the user future, and joins gRPC, registration, and reactor futures. Shutdown first stops gRPC/registration, drains nexuses and snapshot rebuilds, exports LVS/LVM pools, finishes RPC and SPDK subsystems, emits stop events, then stops reactors.

Global state includes `GLOBAL_RC`, `SIG_RECEIVED`, `MAYASTOR_FEATURES`, and `MAYASTOR_DEFAULT_ENV`. Persistent effects include PTPL directory creation, persistent-store connection, imported pools, SPDK trace shared memory, and event messages.

## Dependencies and Integration Points
This file is the central integration point for `spdk_rs`, DPDK/EAL, `logger`, `grpc`, `subsys`, `persistent_store`, `nexus`, `lvs`, optional `lvm`, `eventing`, `nic`, `reactor`, and memory-pool initialization. The main binary constructs `MayastorCliArgs` and starts this environment.

## Risks and Test Signals
Startup order is critical: EAL before SPDK subsystems, reactors before cross-core setup, primary thread context before bdev registration, interrupt-mode setup before reactor polling. Several paths panic on unrecoverable init failures. Network selection for NVMf target depends on interface parsing and IPv4/IPv6 preference. Tests should cover CLI defaults, deprecated gRPC endpoint handling, CRDT bounds, persistent-store option propagation, signal idempotence, shutdown ordering, YAML overrides, feature env flags, and target interface detection.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/env.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/fault_injection/bdev_io_injection.rs -->
# sources/control-plane/mayastor/io-engine/src/core/fault_injection/bdev_io_injection.rs

## Purpose
Implements low-level SPDK bdev function-table patching for `FaultDomain::BdevIo` injections. This lets tests force NVMe completion statuses before the original bdev `submit_request` handler runs.

## Important APIs, Types, and Functions
- `BdevInfo` records the replacement fn table, original fn table, and associated `Injection`.
- `get_bdevs()` returns the global hash map of patched bdevs.
- `inject_submit_request(chan, io_ptr)` is the replacement SPDK submit callback.
- `add_bdev_io_injection(inj)` validates and installs the patched fn table.

## Control Flow and State
Adding an injection validates submission stage and NVMe-status method, looks up the target `UntypedBdev`, rejects duplicate injection for that bdev, clones the original `spdk_bdev_fn_table`, replaces `submit_request` with `inject_submit_request`, writes the new function table pointer into the bdev, and stores metadata keyed by replacement table pointer. On submit, the callback reconstructs `BdevIo`, builds an `InjectIoCtx`, asks the injection whether it applies, completes the I/O with an NVMe status if so, or forwards to the original `submit_request`.

State is global and process-local. The code does not restore original fn tables on removal in this file.

## Dependencies and Integration Points
Feature gated under `fault-injection`. Called by `injection_api::Injections::add` when the domain is `BdevIo`. Depends on SPDK raw structs and `spdk_bdev_io_complete_nvme_status`.

## Risks and Test Signals
This is highly unsafe: it mutates SPDK bdev internals and leaks replacement function tables. Removal from the main injection list does not undo the bdev hook. Multiple injections per bdev are rejected. Tests should verify validation errors, forwarding to original callback, exact NVMe completion status, duplicate rejection, and behavior after injection removal.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/fault_injection/bdev_io_injection.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/fault_injection/fault_method.rs -->
# sources/control-plane/mayastor/io-engine/src/core/fault_injection/fault_method.rs

## Purpose
Defines the concrete effect of a fault injection: return a synthetic I/O status or corrupt buffers.

## Important APIs, Types, and Functions
- `FaultMethod::Status(IoCompletionStatus)` returns an error or status to the caller.
- `FaultMethod::Data` overwrites I/O buffers with deterministic pseudo-random bytes and returns success.
- `FaultMethod::DATA_TRANSFER_ERROR` is a shorthand NVMe data transfer error.
- `inject(state, ctx)` applies the method to an active injection.
- `parse(s)` parses URI method strings such as `status-nvme-sct-sc`, `status-lvol-nospace`, `status-submit-read`, `status-submit-write`, and `status-admin`.

## Control Flow and State
The injection dispatcher calls `FaultMethod::inject` after an `Injection` has matched domain, operation, stage, device, range, time, and retry constraints. Status methods return a copied `IoCompletionStatus`. Data methods call `ctx.iovs_mut()` and replace every byte of every initialized I/O vector using the injection state's seeded RNG.

No independent persistence exists. Data corruption advances the `InjectionState` RNG.

## Dependencies and Integration Points
Depends on `IoCompletionStatus`, `IoSubmissionFailure`, `LvolFailure`, `NvmeStatus`, regex parsing, and `InjectIoCtx`. Used by URI parser and injection runtime.

## Risks and Test Signals
`FaultMethod::Data` mutates raw I/O buffers through context pointers, so context validity and lifetime are critical. Parsing supports only selected lvol/submission/admin names plus NVMe code pairs. Tests should cover display/parse round trips, unsupported strings, deterministic data corruption, and success status after data injection.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/fault_injection/fault_method.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/fault_injection/inject_io_ctx.rs -->
# sources/control-plane/mayastor/io-engine/src/core/fault_injection/inject_io_ctx.rs

## Purpose
Carries I/O metadata from hot I/O paths into the fault-injection matcher. It abstracts over block-device references and plain device names while exposing operation, block range, and mutable I/O vectors.

## Important APIs, Types, and Functions
- `InjectIoDevice` can be `None`, `BlockDevice(*mut dyn BlockDevice)`, or `DeviceName(*const str)`.
- `InjectIoCtx::new(domain)` creates an invalid placeholder context.
- `InjectIoCtx::with_iovs(domain, dev, io_type, offset, num_blocks, iovs)` builds a full context.
- Match helpers include `is_valid`, `domain_ok`, `device_name_ok`, `io_type_ok`, and `block_range_ok`.
- `iovs_mut()` returns mutable I/O vectors for data corruption injection.

## Control Flow and State
I/O paths create a context at submission or completion time and pass it to `inject_submission_error` or `inject_completion_error`. The injection logic filters contexts by domain, target device, read/write operation, and overlapping block range. Data injection requests mutable I/O vectors only after all matching logic succeeds.

State is borrowed raw pointer state. Nothing is owned or persisted by the context.

## Dependencies and Integration Points
Uses `spdk_rs::IoType`, `spdk_rs::IoVec`, and `core::BlockDevice`. Created from nexus child and block-device paths, plus bdev I/O fn-table injection.

## Risks and Test Signals
The enum stores raw trait-object and string pointers. The caller must guarantee the referenced device/string and I/O vectors outlive injection evaluation. `iovs_mut` permits mutation through `&self`, guarded only by pointer checks. Tests should exercise range overlap edges, read/write matching, device-name matching through both variants, and null/empty/uninitialized iov handling.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/fault_injection/inject_io_ctx.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/fault_injection/injection.rs -->
# sources/control-plane/mayastor/io-engine/src/core/fault_injection/injection.rs

## Purpose
Defines a complete fault-injection rule and its URI representation. It matches I/O context attributes and time/retry constraints, then delegates to `FaultMethod`.

## Important APIs, Types, and Functions
- `Injection` fields include `domain`, `device_name`, `io_operation`, `io_stage`, `method`, `time_range`, `block_range`, `retries`, and internal `InjectionState`.
- `InjectionBuilder` adds `with_offset`, `with_method_nvme_error`, validation, and `build_uri`.
- `Injection::from_uri`, `uri`, and `as_uri` convert to/from `inject://device?...` syntax.
- `is_active()` enforces retry count and begin/end duration.
- `inject(stage, ctx)` performs all matching and applies the method.

## Control Flow and State
Parsing validates an `inject://` URI, derives the target device from host, port, and path, then applies query parameters (`domain`, `op`, `stage`, `method`, `begin_at`, `end_at`, `offset`, `num_blk`, `retries`). `num_blk` is converted into an exclusive end by adding the offset. At runtime `inject` first checks domain, stage, op, device, and block overlap. On first match it starts the state clock and records the first hit. If active, it invokes the selected method.

Injection state is in a `RefCell`, so cloned injections carry cloned state. There is no disk persistence.

## Dependencies and Integration Points
Depends on `url`, `derive_builder`, `NvmeStatus`, `IoCompletionStatus`, and the fault-injection module enums. Used by test gRPC and injection API.

## Risks and Test Signals
`begin_at` timing starts only after the first matching I/O, not at injection creation. Retry counting increments before active-window checking, so delayed injections still consume hits. URI construction formats `begin_at` with debug formatting for milliseconds, which should be checked for round-trip compatibility. Tests should cover bad URI schemes, invalid params, duration ordering, range matching, retries, and parser aliases.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/fault_injection/injection.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/fault_injection/injection_api.rs -->
# sources/control-plane/mayastor/io-engine/src/core/fault_injection/injection_api.rs

## Purpose
Provides the global public API for registering, removing, listing, and applying fault injections in I/O paths.

## Important APIs, Types, and Functions
- `add_fault_injection(inj)` enables injections globally and inserts the injection.
- `remove_fault_injection(uri)` removes matching URI entries from the in-memory list.
- `list_fault_injections()` returns cloned injections.
- `injections_enabled()` is the fast hot-path atomic check.
- `inject_submission_error(ctx)` maps injected submission faults into `CoreError`.
- `inject_completion_error(ctx, status)` replaces successful completions with injected status when configured.

## Control Flow and State
`INJECTIONS_ENABLED` starts false and is set when the first injection is added. `Injections` is a lazily initialized `parking_lot::Mutex<Vec<Injection>>`. Adding a `BdevIo` injection also installs the bdev-level hook. Submission injection returns `Ok(())` if disabled, invalid, unmatched, or method yields success; otherwise it maps to a generic bdev I/O error for the operation. Completion injection only runs for successful original completions and returns either the injected status or success.

State is global and volatile. Removing all injections does not reset the enabled atomic.

## Dependencies and Integration Points
Feature gated under `fault-injection`. Called from bdev device and nexus I/O paths, and managed by test gRPC endpoints.

## Risks and Test Signals
Global enable remains true after removals, so hot paths still take the mutex after the first add. The first matching injection wins. Bdev-level hooks installed by `add_bdev_io_injection` are not undone here. Tests should cover disabled fast path, removal semantics, list clone behavior, first-match ordering, completion only on success, and concurrency around the mutex.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/fault_injection/injection_api.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/fault_injection/injection_state.rs -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/fault_injection/injection_state.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/fault_injection/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/core/fault_injection/mod.rs

## Purpose
Defines and re-exports the feature-gated fault-injection subsystem. It supplies common enums, errors, and public API shims used by test endpoints and hot I/O paths.

## Important APIs, Types, and Functions
- Re-exports `FaultMethod`, `InjectIoCtx`, `InjectIoDevice`, `Injection`, `InjectionBuilder`, `InjectionState`, and API functions.
- `FaultDomain` selects `NexusChild`, `BlockDevice`, or `BdevIo`.
- `FaultIoOperation` selects read, write, or both.
- `FaultIoStage` selects submission or completion.
- `FaultInjectionError` reports disabled injections, URI/parameter errors, missing devices, invalid injection combinations, and bad durations.

## Control Flow and State
This module has no runtime flow beyond type definitions and feature gating. The module tree compiles only with `fault-injection`, so any unconditional imports outside matching cfg must be guarded by build configuration.

## Dependencies and Integration Points
Depends on `snafu`, `url::ParseError`, and standard display/debug traits. The public API is re-exported through `core/mod.rs` as `pub mod fault_injection`, and consumers include bdev/nexus I/O code and test gRPC.

## Risks and Test Signals
Because the module is feature gated, CI needs coverage for builds with and without `fault-injection`. Error variants are part of user-visible test API behavior, so URI validation should remain stable. Tests should cover display strings for domains/stages/ops and Snafu messages consumed by gRPC conversion.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/fault_injection/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/handle.rs -->
# sources/control-plane/mayastor/io-engine/src/core/handle.rs

## Purpose
Wraps an SPDK bdev descriptor and I/O channel into an async Rust handle for internal reads, writes, resets, write-zeroes, snapshots, and NVMe admin commands.

## Important APIs, Types, and Functions
- `BdevHandle<T: BdevOps>` owns an `IoChannelGuard` and shared `DescriptorGuard`.
- `open`, `open_with_bdev`, `close`, `get_bdev`, `io_tuple`, and `dma_malloc` provide setup helpers.
- `write_at`, `read_at`, `reset`, `write_zeroes_at`, `create_snapshot`, `nvme_identify_ctrlr`, `nvme_admin_custom`, and `nvme_admin` submit SPDK operations and await oneshots.
- `io_completion_cb` frees SPDK I/O and sends `NvmeStatus`.

## Control Flow and State
Opening obtains a descriptor, optionally claims the bdev, and allocates an I/O channel on the current core. Each async operation creates a oneshot, submits an SPDK bdev command with `cb_arg(sender)`, maps immediate errno into dispatch `CoreError`, and maps completion status into success or a specific `CoreError`. Drop order is important: channel is declared before descriptor so it is dropped first.

State is the live SPDK descriptor/channel. No persistent state is written except device effects from I/O/admin commands.

## Dependencies and Integration Points
Depends on `spdk_rs`, `Bdev`, `DescriptorGuard`, `DmaBuf`, `CoreError`, `SnapshotParams`, and `subsys::set_snapshot_time`. Used by replica wiping, bdev LVS helpers, and test/admin paths.

## Risks and Test Signals
All operations are reactor/thread-affine through the channel. The completion callback expects sender delivery to succeed and panics otherwise. `create_snapshot` only sends an NVMe admin command and ignores the provided params in this wrapper. Tests should cover dispatch errno mapping, completion status mapping, unallocated-block read behavior, channel allocation failure, and NVMe admin buffer sizing.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/handle.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/io_device.rs -->
# sources/control-plane/mayastor/io-engine/src/core/io_device.rs

## Purpose
Provides a safer Rust wrapper around SPDK I/O device registration and channel traversal.

## Important APIs, Types, and Functions
- `IoDevice(NonNull<c_void>)` represents a registered SPDK I/O device.
- `IoDevice::new<C>` registers a device pointer with create/destroy callbacks and per-channel context size.
- `traverse_io_channels` wraps `spdk_for_each_channel` with Rust closures for per-channel and completion callbacks.
- `Drop` unregisters the device with `spdk_io_device_unregister`.

## Control Flow and State
Construction registers the supplied device pointer and channel context type size with SPDK. Channel traversal boxes a context containing caller closures and caller state, passes it into SPDK, invokes `channel_cb` for each channel after deriving typed channel context with `ctx_getter`, continues iteration with the returned status, then reconstructs the box in the done callback and invokes `done_cb`.

State is SPDK registration plus the raw device pointer. There is no persistence.

## Dependencies and Integration Points
Depends on SPDK channel iteration APIs, `IntoCString`, and raw C callback conventions. Used by modules that expose SPDK channel data across all cores.

## Risks and Test Signals
The type is marked `Send`/`Sync` with a TODO question, so thread-safety relies on SPDK lifetime and caller discipline. Closure contexts are leaked if SPDK never invokes the done callback. Tests should validate registration/unregistration ordering, traversal completion on empty and multi-channel devices, error propagation status, and no double-unregister.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/io_device.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/io_driver.rs -->
# sources/control-plane/mayastor/io-engine/src/core/io_driver.rs

## Purpose
Implements a test/support I/O workload driver that creates or opens a bdev and continuously submits random read or write I/O at a configured queue depth.

## Important APIs, Types, and Functions
- `IoType::{Read, Write}` selects workload direction.
- `Builder` configures URI, queue depth, I/O size, existing bdev, and core.
- `Job` owns the descriptor, I/O channel, queue, counters, RNG, drain/reset flags, and thread.
- `JobQueue` starts/stops jobs, stops all jobs, and signals reset across jobs.

## Control Flow and State
`Builder::build` creates or opens the bdev, computes block and I/O geometry, allocates one `DmaBuf` per queue entry, and returns a `Job`. `Job::start` creates an SPDK thread on the selected core, allocates a channel, boxes the job, and starts each queued `Io`. Each completion frees SPDK I/O, updates inflight/completion counters, sends the drain oneshot if all I/O has drained, otherwise submits another random offset unless draining. Reset requests cause the next I/O to submit a reset first.

State is all in-memory and tied to the created SPDK thread/channel. Created bdevs persist according to their backend until deleted elsewhere.

## Dependencies and Integration Points
Depends on `bdev_create`, `UntypedBdev`, `UntypedDescriptorGuard`, SPDK bdev I/O calls, `DmaBuf`, `Thread`, and `Cores`. Intended for tests and diagnostics rather than production data path.

## Risks and Test Signals
Several calculations can divide by zero if invalid `io_size` or block size reaches the builder. The random offset expression appears to use `rng % io_size` multiplied by `io_blocks`, which may not span the full device as expected. Completion sends the drain signal when inflight reaches zero; double stop panics. Tests should cover build validation, stop/drain, reset injection, core affinity assertion, and qd/io-size edge cases.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/io_driver.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/lock.rs -->
# sources/control-plane/mayastor/io-engine/src/core/lock.rs

## Purpose
Provides an async resource lock manager for serializing global, subsystem, and per-resource operations such as nexus, pool, and replica mutations.

## Important APIs, Types, and Functions
- `ProtectedSubsystems` defines common IDs: `NEXUS`, `POOL`, and `REPLICA`.
- `ResourceLockManagerConfig::with_subsystem` declares subsystem lock shards.
- `ResourceLockManager::initialize`, `get_instance`, `lock`, and `get_subsystem` manage global access.
- `ResourceSubsystem::lock` and `lock_resource` acquire subsystem-level or hashed object-level locks.
- `ResourceLockGuard` releases on drop.

## Control Flow and State
Startup initializes a singleton `ResourceLockManager` from config. Each subsystem owns a vector of async mutexes for hashed object locks plus one subsystem-wide mutex. `acquire_lock` supports optional timeout, immediate try-lock, or indefinite wait, then increments `num_acquires` and returns a guard.

State is process-local lock state and simple acquisition counters. There is no persistence.

## Dependencies and Integration Points
Uses `futures::lock::Mutex`, `tokio::time::timeout`, and `OnceCell`. The main binary initializes it; gRPC v0/v1 pool, replica, nexus, stats, and snapshot handlers use it to serialize control-plane operations.

## Risks and Test Signals
Resource locks are hash-sharded, so different resource IDs can collide and serialize unexpectedly. `get_instance` and unknown subsystem lookup panic. `try_lock` is ignored when a timeout is supplied. Tests should cover initialization, duplicate subsystem panic, timeout behavior, try-lock behavior, hash-lock mutual exclusion, and integration with gRPC operations that must not deadlock.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/lock.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/logical_volume.rs -->
# sources/control-plane/mayastor/io-engine/src/core/logical_volume.rs

## Purpose
Defines the backend-neutral logical volume interface used by replicas, LVM volumes, and event/reporting code.

## Important APIs, Types, and Functions
- `LogicalVolume` trait exposes identity, pool identity, entity ID, provisioning/read-only flags, size/accounting, backend type, snapshot/clone role, parent snapshot, share protocol/URI, allowed hosts, and encryption.
- `LvolSpaceUsage` carries capacity, allocated bytes, cluster size/counts, snapshot allocation, and optional clone-derived snapshot allocation.

## Control Flow and State
This file declares contracts only. Implementors supply state from backend-specific volume metadata. Consumers can treat LVS and LVM-style volumes uniformly for listing, event metadata, and share state.

There is no state or persistence in this file, but fields map directly to persisted backend metadata and runtime share configuration.

## Dependencies and Integration Points
Depends on `Protocol` and `PoolBackend`. Implemented by LVS `Lvol` and LVM volume types, and consumed by eventing, replica APIs, and gRPC response builders.

## Risks and Test Signals
The trait returns many owned `String` values, so repeated reporting can allocate heavily. Semantics such as `allocated`, `committed`, and snapshot allocation must be consistent across backends. Tests should compare LVS and LVM implementations for identical API semantics, especially snapshot/clone flags and share metadata.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/logical_volume.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/mempool.rs -->
# sources/control-plane/mayastor/io-engine/src/core/mempool.rs

## Purpose
Wraps SPDK/DPDK mempools for allocation-free hot-path object reuse with drop-time accounting.

## Important APIs, Types, and Functions
- `MemoryPool<T>` stores the raw `spdk_mempool`, name, capacity, and element type marker.
- `MemoryPool::create(name, size)` creates a pool sized for `T`.
- `get(val)` obtains an element and writes `val` into the slot.
- `put(ptr)` returns a slot to the pool.
- `Drop` asserts all elements have been returned and frees the SPDK pool.

## Control Flow and State
Creation calls `spdk_mempool_create` with `size_of::<T>()` and SPDK default cache sizing. `get` calls `spdk_mempool_get`, writes the provided object into raw memory, and returns a typed pointer. `put` returns the pointer without running `drop` for `T`. On pool drop, `spdk_mempool_count` must equal capacity or the process panics.

State is the SPDK pool and outstanding borrowed elements. No persistence exists.

## Dependencies and Integration Points
Depends on `spdk_rs::libspdk` mempool functions and `IntoCString`. Used by bdev and NVMe I/O context pool initialization from `env.rs`.

## Risks and Test Signals
`put` does not drop values, which is only safe for pool element types designed for this lifecycle. Drop-time assert catches leaks but can panic during shutdown. Tests should cover exhausted pools, returned counts, capacity accounting, and element types with destructor-sensitive behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/mempool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/core/mod.rs

## Purpose
Acts as the main public facade for core SPDK/io-engine abstractions and shared error/status types.

## Important APIs, Types, and Functions
- Re-exports bdev, block device, descriptor, device event, environment, reactor, lock, share, snapshot, and runtime APIs.
- `VerboseError` formats an error chain.
- `CoreError` is the central Snafu error enum for bdev open, I/O dispatch/completion, sharing, reactor config, DMA, statistics, PTPL, snapshot, wipe, and crypto errors.
- `ToErrno` maps `CoreError` to POSIX errno values for API boundaries.
- `IoCompletionStatus`, `LvolFailure`, and `IoSubmissionFailure` normalize completion domains.
- `PAUSING` and `PAUSED` are global pause counters.
- `MayastorFeatures` and `MayastorBugFixes` expose feature/bugfix capability state.

## Control Flow and State
This file mostly defines contracts. `ToErrno` is used when control-plane or C-facing layers need errno-like errors. `IoCompletionStatus::from(NvmeStatus)` maps no-space/capacity-exceeded into `LvolError::NoSpace`; all other NVMe status values remain protocol-specific.

State is limited to exported atomics and feature structs initialized elsewhere.

## Dependencies and Integration Points
Every core consumer imports through this facade. It links `NvmfError`, SPDK status types, snapshot traits, share traits, and module visibility decisions.

## Risks and Test Signals
`CoreError` variants are user-visible through gRPC status mapping and logs, so changes have broad compatibility impact. Errno mappings must stay consistent with callers. Tests should verify error-to-errno mapping, no-space status conversion, re-export availability under feature flags, and error-chain formatting.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/nic.rs -->
# sources/control-plane/mayastor/io-engine/src/core/nic.rs

## Purpose
Discovers and filters network interfaces for NVMf target address selection, with helpers for IP, subnet, MAC, and IPv4/IPv6 preference handling.

## Important APIs, Types, and Functions
- `SIpAddr` wraps IPv4 or IPv6 plus optional scope ID and converts from socket addresses.
- `InetConfig<T>` stores address/netmask pairs.
- `MacAddr` parses and formats six-byte MAC addresses.
- `Interface` stores name, IPv4/IPv6 configs, and MAC, with matching and sorting helpers.
- `find_all_nics()` enumerates system interfaces via `nix::ifaddrs`.
- `parse_ip` and `parse_ip_subnet` parse address and CIDR filters.

## Control Flow and State
`find_all_nics` iterates `getifaddrs`, creates an `Interface` for each address record, fills IPv4, IPv6, MAC, and netmask fields when present, skips scoped IPv6 addresses, and returns entries that have at least one IP address. `Interface` methods filter by exact IP, subnet, or preference order. IPv6 sorting prefers unique local, then link local, then non-unspecified, then non-multicast addresses.

No state is retained; discovery is live system state.

## Dependencies and Integration Points
Used by `MayastorEnvironment::detect_nvmf_tgt_iface_ip` to resolve `--tgt-iface` values. Depends on `nix::ifaddrs` and standard network types.

## Risks and Test Signals
`getifaddrs().unwrap()` can panic if interface enumeration fails. Multiple `getifaddrs` records for the same interface are not merged, so name/MAC filters may return partial records depending on ordering. IPv6 scope IDs are skipped. Tests should cover MAC parsing, subnet masks including `/0`, v4/v6 preference, exact matching, and multi-address interface behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/nic.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/partition.rs -->
# sources/control-plane/mayastor/io-engine/src/core/partition.rs

## Purpose
Calculates fixed partition layout offsets for reserving GPT and io-engine metadata space before the user data partition.

## Important APIs, Types, and Functions
- `GPT_TABLE_SIZE`, `METADATA_RESERVATION_OFFSET`, `METADATA_RESERVATION_SIZE`, and `DATA_PARTITION_OFFSET` define layout constants.
- `calc_data_partition(req_size, num_blocks, block_size)` returns `(data_start, data_end, req_blocks)` in blocks.
- `bytes_to_alinged_blocks(size, block_size)` rounds byte sizes up to block counts.

## Control Flow and State
`calc_data_partition` computes GPT table blocks, metadata start, last usable block before backup GPT, metadata blocks, and data start. If the device cannot fit metadata reservation before the usable end, it returns `None`. It then rounds requested size to blocks and caps the data end at the last usable block.

There is no state or persistence here; the returned offsets are consumed by bdev/pool layout code.

## Dependencies and Integration Points
Used by nexus/bdev layout paths that create or expose data partitions while reserving metadata space.

## Risks and Test Signals
The function assumes `num_blocks` is large enough for `gpt_blocks + 2`; otherwise unsigned subtraction can underflow in debug builds and wrap in release if not optimized with checks. `block_size` must be nonzero. The helper name contains a typo (`alinged`). Tests should cover tiny devices, non-divisible block sizes, exact metadata fit, oversized requested data, and zero block-size rejection by callers.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/partition.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/reactor.rs -->
# sources/control-plane/mayastor/io-engine/src/core/reactor.rs

## Purpose
Implements the io-engine reactor runtime: one reactor per SPDK lcore, SPDK thread scheduling, Rust future dispatch, poll/interrupt-mode loops, shutdown, and freeze monitoring.

## Important APIs, Types, and Functions
- `ReactorState` includes `Init`, `Running`, `Shutdown`, `Delayed`, and `Interrupt`.
- `Reactors::init`, `launch_master`, `launch_remote`, `current`, `master`, `iter`, and SPDK thread scheduling callbacks manage global reactor setup.
- `Reactor::send_future`, `spawn_local`, `block_on`, `spawn_at`, and `spawn_at_primary` bridge futures to reactor/SPDK threads.
- `poll_reactor`, `poll_once`, `poll_times`, `add_incoming`, `destroy_exited`, `enter_interrupt_mode`, and `leave_interrupt_mode` drive execution.
- `Future for &'static Reactor` lets Tokio poll the master reactor.
- `reactor_monitor_loop` schedules heartbeat futures and emits freeze/unfreeze events.

## Control Flow and State
Initialization configures SPDK thread library, optionally enables global interrupt mode, creates reactors for all cores, and creates an init SPDK thread. SPDK thread creation is routed through `Reactors::do_op`, which schedules new threads onto reactors matching CPU masks and wakes sleeping reactors. Each reactor drains cross-core futures, runs local async tasks, polls SPDK threads, accepts incoming SPDK threads, and destroys exited ones. In interrupt mode, per-thread fd groups are nested under a reactor fd group and an eventfd wakes the reactor for Rust futures. Shutdown changes state, exits interrupt mode, waits/destroys threads, and joins remote cores.

State includes per-reactor thread queues, incoming queues, future channels, fd groups, wakeup fd, reactor state, and TID. It is process-local only.

## Dependencies and Integration Points
Depends on SPDK thread/fd group APIs, `async_task`, `crossbeam`, `Cores`, `events_api`, diagnostics, and configuration env helpers. It underpins gRPC management, bdev operations, device monitor, and environment startup/shutdown.

## Risks and Test Signals
Reactor context is safety-critical: many SPDK APIs require the correct current SPDK thread. Interrupt mode has partial-nesting rollback paths that must prevent silent poller loss. `send_future` writes to eventfd without checking short/error writes. Freeze detection schedules heartbeats and can mark a reactor frozen if futures are queued behind long work. Tests should cover cross-core `spawn_at`, interrupt-mode enter/exit with incoming threads, shutdown with remaining threads, freeze/unfreeze events, and developer delay mode.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/reactor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/runtime.rs -->
# sources/control-plane/mayastor/io-engine/src/core/runtime.rs

## Purpose
Provides a small global Tokio multi-threaded runtime helper for background tasks that do not need to run on SPDK reactors.

## Important APIs, Types, and Functions
- `spawn(f)` submits a `Send + 'static` future and detaches it.
- `spawn_await(f)` submits and awaits completion.
- `block_on(f)` runs a future to completion on the global runtime.
- `spawn_blocking(f)` delegates blocking work to Tokio.
- `Runtime` wraps `tokio::runtime::Runtime`.

## Control Flow and State
`RUNTIME` is lazily created with `Builder::new_multi_thread().enable_all()`. Helper functions call through to that singleton. The runtime exists for process lifetime and is separate from the current-thread runtime used in `MayastorEnvironment::start`.

State is the Tokio runtime and its task queues. No persistence exists.

## Dependencies and Integration Points
Used by io-engine modules that need generic Tokio execution. Coexists with SPDK reactor-local future execution, so callers must choose the correct runtime based on SPDK thread affinity.

## Risks and Test Signals
Tasks spawned here must be `Send` and must not directly use SPDK APIs requiring current SPDK thread context. `spawn_await` awaits a join handle and ignores panics only through unwrap semantics? It awaits with `let _ =`, so panic results are dropped. Tests should cover runtime initialization, spawn completion, blocking task execution, and absence of reactor-affine calls in runtime tasks.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/runtime.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/segment_map.rs -->
# sources/control-plane/mayastor/io-engine/src/core/segment_map.rs

## Purpose
Represents dirty/clean rebuild segments over a block device. It maps logical block ranges to fixed-size segment bits for rebuild tracking.

## Important APIs, Types, and Functions
- `SegmentMap<B: BitBlock = u32>` stores a `BitVec`, number of segments, device block count, block length, and segment size.
- `new(num_blocks, block_len, segment_size)` creates a zeroed bitmap.
- `set(lbn, lbn_cnt, value)` marks the segment range containing a block range.
- `get(lbn)` reads the bit for a block.
- `merge`, `count_dirty_blks`, `segment_size_blks`, and `size_blks` support rebuild consumers.
- `From<SegmentMap> for BitVec` exposes the underlying bitmap.

## Control Flow and State
The constructor computes segment count by ceiling-dividing total bytes by segment size. `set` maps the first and last logical blocks to segment indices and sets all bits in that inclusive segment range. Dirty block count multiplies set segment count by segment-size blocks.

State is in-memory bitmap state. Persistence, if needed, must be handled by consumers.

## Dependencies and Integration Points
Depends on `bit_vec`. Used by rebuild logic to track what replica segments need transfer.

## Risks and Test Signals
`set` asserts `num_blocks != 0` but does not validate `lbn_cnt > 0`, `segment_size > 0`, or block range bounds. Dirty block count may over-count at the tail because it multiplies full segments. Tests should cover tail segments, merge semantics, zero/invalid inputs, and conversion to `BitVec`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/segment_map.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/share.rs -->
# sources/control-plane/mayastor/io-engine/src/core/share.rs

## Purpose
Defines protocol-neutral share/unshare/update properties and the async `Share` trait for exposing bdev-backed volumes over NVMe-oF.

## Important APIs, Types, and Functions
- `Protocol::{Off, Nvmf}` maps from gRPC integer values and displays protocol names.
- `ShareProps::Nvmf`, `NvmfShareProps`, `UnshareProps`, `PtplProps`, and `UpdateProps` carry share configuration.
- `NvmfShareProps` supports controller ID range, ANA, allowed hosts, and PTPL path.
- `Share` trait defines `share_nvmf`, `create_ptpl`, `update_properties`, `unshare`, `shared`, `share_uri`, `allowed_hosts`, and bdev URI accessors.

## Control Flow and State
This file is mainly contracts and property conversion. `Protocol::try_from` validates user-supplied gRPC enum values. `From<Option<_>>` defaults missing props. Conversions from share props to update props preserve allowed hosts. Implementors perform actual target creation, PTPL file creation, property updates, and unsharing.

State lives in implementors and NVMe-oF subsystems, not in this file. PTPL props refer to a persistent JSON reservation path.

## Dependencies and Integration Points
Uses `async_trait` and `LvsError`. Implemented by logical volume/bdev share layers and consumed by replica and nexus gRPC handlers.

## Risks and Test Signals
`ShareProps::allowed_hosts(self)` consumes the enum, which is appropriate for conversion but can surprise callers. Only NVMe-oF is currently represented; previous iSCSI enum value is rejected. Tests should cover protocol validation, default props, allowed-host conversions, PTPL path propagation, and implementor behavior around persistent unshare.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/share.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/snapshot.rs -->
# sources/control-plane/mayastor/io-engine/src/core/snapshot.rs

## Purpose
Defines snapshot and clone parameter models, snapshot listing descriptors, LVS extended attribute names, and descriptor access traits shared by replica backends.

## Important APIs, Types, and Functions
- `SnapshotParams` stores entity, parent, transaction, name, UUID, create time, and discarded flag.
- `CloneParams` stores clone name/UUID, source UUID, and creation time.
- `SnapshotInfo` and `SnapshotDescriptor` bundle backend snapshot object plus generic metadata.
- `PropXattrs`, `SnapshotXattrs`, and `CloneXattrs` map logical properties to LVS xattr C strings.
- `ISnapshotDescriptor` abstracts snapshot parameter getters/setters and is implemented for `SnapshotParams`.
- Re-exports `LvolSnapshotOps`.

## Control Flow and State
`prepare` constructors validate required string inputs and add `chrono::Utc::now()` timestamps. Backend code stores and retrieves fields via xattrs. Snapshot descriptors combine a boxed `SnapshotOps` implementation with collected metadata for list responses. `discarded_snapshot` models deferred delete when clones still reference a snapshot.

State in this file is data only. Persistence occurs when backends write the named xattrs to LVS/LVM metadata.

## Dependencies and Integration Points
Used by replica backend traits, LVS snapshot implementation, LVM module, NVMf admin snapshot command decoding, and eventing. Depends on `serde`, `chrono`, `strum`, and backend traits.

## Risks and Test Signals
Several getters clone strings, and validation is limited to non-empty fields. `BrokenEntityId` documents an xattr representation mismatch. Tests should cover xattr names, prepare validation, discarded snapshot propagation, clone metadata round trips, and backend compatibility for snapshot UUID and entity ID fields.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/thread.rs -->
# sources/control-plane/mayastor/io-engine/src/core/thread.rs

## Purpose
Provides the `Mthread` type alias for `spdk_rs::Thread`, preserving the older core naming convention used across io-engine.

## Important APIs, Types, and Functions
- `pub type Mthread = spdk_rs::Thread`.

## Control Flow and State
No behavior is implemented here. All methods and state are provided by `spdk_rs::Thread`.

## Dependencies and Integration Points
Re-exported by `core/mod.rs` and used by environment startup/shutdown signal handling to access primary SPDK thread context.

## Risks and Test Signals
The alias can obscure the underlying type for readers, but it avoids broad churn. Tests are covered by `spdk_rs::Thread` integration and callers such as `env.rs`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/thread.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/wiper.rs -->
# sources/control-plane/mayastor/io-engine/src/core/wiper.rs

## Purpose
Implements bdev wiping and streamed wipe progress reporting for replica cleanup/test APIs. It supports no-op, write-zeroes, and CRC32C checksum modes.

## Important APIs, Types, and Functions
- `Error` maps wipe validation, I/O, abort, unsupported method, and notification failures.
- `Wiper` owns an `UntypedBdevHandle` and `WipeMethod`.
- `StreamedWiper<S: NotifyStream>` wipes in chunks and notifies clients.
- `NotifyStream` abstracts progress streaming and close detection.
- `WipeMethod::{None, WriteZeroes, Unmap, WritePattern, CkSum}` and `CkSumMethod::Crc32`.
- `WipeStats`, `FinalWipeStats`, and `WipeIterator` track progress, bandwidth logging, and chunk iteration.

## Control Flow and State
`Wiper::new` validates method support. `wipe` either does nothing, submits `write_zeroes_at`, reads and updates CRC, or returns unimplemented for unmap/pattern. `StreamedWiper::new` validates chunk size against bdev size and block length, constructs stats, and enforces max chunk count. `wipe` sends initial stats, iterates chunks, splits large chunks into 8 MiB operations, checks aborts, updates stats, finalizes CRC by XOR on the last chunk, and returns final timing.

State is in-memory progress and mutable checksum. Device contents are modified by write-zeroes.

## Dependencies and Integration Points
Used by replica gRPC and test gRPC. Depends on `UntypedBdevHandle`, SPDK CRC constants/functions, `byte_unit`, `uuid`, and `CoreError`.

## Risks and Test Signals
The iterator skips 33 backup GPT blocks at the end, which affects exact wipe size. `dma_malloc(size).unwrap()` can panic during checksum mode. Unsupported methods are represented but rejected. Tests should cover chunk alignment, zero-size devices, max chunk limits, abort on closed streams, CRC finalization, large-chunk splitting, and conversion between `Error` and `CoreError`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/wiper.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/work_queue.rs -->
# sources/control-plane/mayastor/io-engine/src/core/work_queue.rs

## Purpose
Defines a simple thread-safe FIFO-like work queue abstraction over `crossbeam::queue::SegQueue`.

## Important APIs, Types, and Functions
- `WorkQueue<T: Send + Debug + Display>` stores an incoming `SegQueue<T>`.
- `new`, `enqueue`, `len`, `is_empty`, and `take` expose queue operations.

## Control Flow and State
Producers call `enqueue`, which logs and pushes onto the lock-free queue. Consumers call `take`, which pops one item if available. Length and emptiness are snapshots of the concurrent queue.

State is in-memory queued work only. No persistence or retry metadata exists.

## Dependencies and Integration Points
Used by `device_monitor.rs` for device commands. Could be reused by other core monitor loops.

## Risks and Test Signals
`SegQueue` is unbounded, so producers can outpace consumers. `len` under concurrency is only advisory. Tests should cover enqueue/take order expectations, empty behavior, and concurrent producers/consumers.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/core/work_queue.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/coredump.rs -->
# sources/control-plane/mayastor/io-engine/src/coredump.rs

## Purpose
Enables Linux core dumps for the io-engine process by raising `RLIMIT_CORE`.

## Important APIs, Types, and Functions
- `DEFAULT_CORE_LIMIT` is 5 GiB, matching SPDK app default behavior.
- `enable(limit)` calls `setrlimit(RLIMIT_CORE, ...)` and returns `nix::Error` on failure.

## Control Flow and State
The caller chooses a limit, constructs a libc `rlimit` with current and max equal to that limit, and applies it through `setrlimit`. The effect is process resource-limit state.

## Dependencies and Integration Points
Used by CLI/startup coredump option handling. Depends on `libc` and `nix`.

## Risks and Test Signals
Raising `rlim_max` may require privileges or be capped by the parent environment. Tests should cover success under permissive limits, failure propagation, and CLI default/debug-build behavior around the enable option.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/coredump.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/delay.rs -->
# sources/control-plane/mayastor/io-engine/src/delay.rs

## Purpose
Registers an SPDK poller that sleeps periodically to reduce CPU usage in non-performance contexts such as unit tests.

## Important APIs, Types, and Functions
- `register()` registers a poller that calls `sleep` every 1000 us and records the poller pointer in thread-local state.
- `unregister()` unregisters the saved poller if present.
- `sleep` sleeps the current thread for 1 ms and returns success.

## Control Flow and State
Each thread has a `DELAY_POLLER` `RefCell<Option<*mut spdk_poller>>`. Registering warns, calls `spdk_poller_register`, and panics on double registration for that thread. Unregistering takes the pointer and passes it to `spdk_poller_unregister`.

State is thread-local SPDK poller registration. There is no persistence.

## Dependencies and Integration Points
Depends on SPDK poller APIs. Related to developer delay mode in reactor/environment options, though reactor-level delay is also implemented directly in `reactor.rs`.

## Risks and Test Signals
Register does not check for null poller return. Double registration panics. The sleep blocks the reactor thread and intentionally degrades responsiveness. Tests should cover register/unregister lifecycle, double register panic, and no warning about leaked pollers at shutdown.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/delay.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/clone_events.rs -->
# sources/control-plane/mayastor/io-engine/src/eventing/clone_events.rs

## Purpose
Adds event generation for clone lifecycle operations represented by `CloneParams`.

## Important APIs, Types, and Functions
- Implements `Event` for `CloneParams`.
- Builds `EventSource` with node name, source UUID, and clone creation time.

## Control Flow and State
When a clone action occurs, callers invoke `CloneParams::event(action)`. The event category is `Clone`, the target is the clone UUID or empty string, and metadata includes clone source information derived from the current global/default environment node name.

No state is persisted by this file; generated messages are handed to the eventing transport elsewhere.

## Dependencies and Integration Points
Depends on `events_api::event`, `CloneParams`, and `MayastorEnvironment`. Used by clone creation/deletion paths that emit events.

## Risks and Test Signals
Missing optional fields become empty strings, so event consumers must tolerate incomplete metadata. Tests should assert category/action/target mapping and metadata values for complete and partial `CloneParams`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/clone_events.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/host_events.rs -->
# sources/control-plane/mayastor/io-engine/src/eventing/host_events.rs

## Purpose
Builds metadata and event messages for host initiator events against NVMe-oF subsystems, nexus targets, and replica targets.

## Important APIs, Types, and Functions
- `HostTargetMeta` adds target details to existing event metadata.
- Implementations for `Nexus` and `Lvol` tag target type and UUID.
- `EventMetaGen for NvmfSubsystem` adds subsystem NQN metadata.
- `EventWithMeta for NvmfController` adds host initiator NQN and produces `HostInitiator` events.

## Control Flow and State
Target code starts with metadata from a subsystem or target, then host controller event creation adds initiator host NQN and emits a message with empty target field and host initiator category. Nexus and Lvol target metadata helpers mutate existing `EventMeta` only when a source is present.

No state is stored.

## Dependencies and Integration Points
Depends on `events_api`, `Nexus`, `LogicalVolume`, `Lvol`, `NvmfSubsystem`, `NvmfController`, and `MayastorEnvironment`. Used by NVMe-oF connect/disconnect and host event paths.

## Risks and Test Signals
Metadata enrichment silently does nothing if `meta.source` is absent. Replica target data uses `Lvol::uuid`, while nexus uses `Nexus::uuid`. Tests should cover source-present/source-absent metadata, target type strings, and host NQN population.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/host_events.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/io_engine_events.rs -->
# sources/control-plane/mayastor/io-engine/src/eventing/io_engine_events.rs

## Purpose
Creates io-engine and reactor event messages, including shutdown duration metadata and reactor freeze/unfreeze details.

## Important APIs, Types, and Functions
- `io_engine_stop_event_meta(total_time)` produces duration metadata.
- Implements `Event` and `EventWithMeta` for `MayastorEnvironment`.
- Implements `Event` for `Reactor`.

## Control Flow and State
Environment events use category `IoEngineCategory`, action from caller, target as environment name, and node metadata. Stop events can include elapsed shutdown duration. Reactor events use the reactor TID as target and include core number plus current reactor state in metadata.

No persistent state is stored; messages are generated for the event bus.

## Dependencies and Integration Points
Used by environment startup/shutdown and reactor freeze monitor. Depends on `events_api`, `MayastorEnvironment`, and `Reactor`.

## Risks and Test Signals
Reactor target is `tid().to_string()`, which is `0` before the reactor records its TID. Tests should verify shutdown duration metadata, environment target naming, and reactor core/state metadata for each state.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/io_engine_events.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/eventing/mod.rs

## Purpose
Declares the eventing module tree and the small traits used by io-engine domain objects to generate event messages and metadata.

## Important APIs, Types, and Functions
- Module declarations for clone, host, io-engine, nexus child, nexus, pool, replica, and snapshot events.
- `Event` trait creates a plain `EventMessage`.
- `EventWithMeta` creates an `EventMessage` using supplied metadata.
- `EventMetaGen` creates reusable `EventMeta`.

## Control Flow and State
There is no runtime flow here. Implementations in sibling modules attach these traits to domain types such as `Nexus`, `Lvol`, `SnapshotParams`, `CloneParams`, `NvmfSubsystem`, and `Reactor`.

No state or persistence exists in this file.

## Dependencies and Integration Points
Depends on `events_api::event::{EventAction, EventMessage, EventMeta}`. This is the compile-time hub used by environment and storage components before messages are passed to the event transport.

## Risks and Test Signals
Trait visibility is mixed: `Event` is public within the crate API surface, while metadata helpers are crate-private. Tests should cover that all event modules remain compiled and that changes to events-api types propagate through trait signatures.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/nexus_child_events.rs -->
# sources/control-plane/mayastor/io-engine/src/eventing/nexus_child_events.rs

## Purpose
Generates nexus child add/remove event messages from gRPC request types.

## Important APIs, Types, and Functions
- Implements `Event` for `AddChildNexusRequest`.
- Implements `Event` for `RemoveChildNexusRequest`.
- Both use `with_nexus_child_data(&self.uri)` metadata.

## Control Flow and State
When an add or remove child request is accepted, callers can emit an event with the request object. The event category is `Nexus`, target is the nexus UUID from the request, and metadata identifies the child URI and node name.

No state is persisted here.

## Dependencies and Integration Points
Depends on `io_engine_api::v1::nexus` request types, `events_api`, and `MayastorEnvironment`. Integrated into nexus gRPC request handling.

## Risks and Test Signals
Events are based on request data rather than post-operation object state, so they may include the requested URI even if later normalization occurs elsewhere. Tests should assert add/remove parity, target UUID, and URI metadata.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/nexus_child_events.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/nexus_events.rs -->
# sources/control-plane/mayastor/io-engine/src/eventing/nexus_events.rs

## Purpose
Creates nexus, nexus child, rebuild, pause, state-change, and error event metadata/messages.

## Important APIs, Types, and Functions
- `EventMetaGen for NexusRebuildJob` maps rebuild states to `RebuildStatus` and includes source/destination URI plus error text.
- `EventMetaGen for NexusChild` includes child URI.
- `state_change_event_meta(previous, next)` records nexus state transitions.
- `subsystem_pause_event_meta(status, total_time, error)` records pause status, duration, and optional error.
- Implements `Event` and `EventWithMeta` for `nexus::Nexus`.
- `EventMetaGen for Error` converts nexus errors into event metadata.

## Control Flow and State
Rebuild jobs and nexus operations generate metadata at transition points. Nexus events use category `Nexus`, target as nexus UUID, and either default node metadata or supplied metadata. Pause metadata starts with node and pause status, then optionally adds elapsed duration and error detail.

No state is stored; it reflects caller-provided object state at generation time.

## Dependencies and Integration Points
Depends on nexus types, rebuild state, `VerboseError`, `events_api`, and `MayastorEnvironment`. Called from rebuild and nexus control/data paths.

## Risks and Test Signals
Unknown rebuild states fall back to `RebuildStatus::Unknown`. Error metadata for rebuild uses verbose error chains, while nexus error metadata uses `to_string`, so detail level differs. Tests should cover each rebuild state, pause metadata combinations, state transitions, and category/target correctness.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/nexus_events.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/pool_events.rs -->
# sources/control-plane/mayastor/io-engine/src/eventing/pool_events.rs

## Purpose
Generates pool event messages from `Lvs` pool objects.

## Important APIs, Types, and Functions
- Implements `Event` for `Lvs`.
- Event category is `Pool`; target is `Lvs::name()`.

## Control Flow and State
Pool lifecycle code calls `Lvs::event(action)` to build a message with current global/default node name and no extra pool metadata beyond target.

No state is stored.

## Dependencies and Integration Points
Depends on `events_api`, `MayastorEnvironment`, and `lvs::Lvs`. Used by pool create/import/destroy related event paths.

## Risks and Test Signals
The event target is pool name, not UUID, so consumers needing stable identity must correlate elsewhere. Tests should assert category, action, target, and node metadata.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/pool_events.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/replica_events.rs -->
# sources/control-plane/mayastor/io-engine/src/eventing/replica_events.rs

## Purpose
Creates replica and replica-child state event messages.

## Important APIs, Types, and Functions
- Implements `Event` for `Lvol`, producing `Replica` category messages.
- `state_change_event_meta(previous, next)` records `ChildState` transitions.
- Implements `EventWithMeta` for `NexusChild`, using the child UUID as target.

## Control Flow and State
Replica events derive pool name, pool UUID, and replica name from the `Lvol` and use the logical volume UUID as target. Nexus child state events use supplied metadata and target the child UUID or an empty string.

No state is stored.

## Dependencies and Integration Points
Depends on `events_api`, `LogicalVolume`, LVS lvol traits, `ChildState`, `NexusChild`, and `MayastorEnvironment`. Used by replica lifecycle and nexus child state transitions.

## Risks and Test Signals
`NexusChild::get_uuid()` may be absent, leading to empty target. Tests should cover replica metadata values, child state transition metadata, and missing UUID behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/replica_events.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/snapshot_events.rs -->
# sources/control-plane/mayastor/io-engine/src/eventing/snapshot_events.rs

## Purpose
Generates snapshot event messages from `SnapshotParams`.

## Important APIs, Types, and Functions
- Implements `Event` for `SnapshotParams`.
- Metadata includes parent ID, create time, and entity ID through `with_snapshot_data`.
- Target is the snapshot UUID or an empty string.

## Control Flow and State
Snapshot lifecycle code calls `SnapshotParams::event(action)` after preparing or loading snapshot parameters. Optional fields default to empty strings in the event message.

No state is stored here.

## Dependencies and Integration Points
Depends on `events_api`, `ISnapshotDescriptor`, `MayastorEnvironment`, and `SnapshotParams`. Used by snapshot create/delete/reporting paths.

## Risks and Test Signals
Missing optional metadata is silently represented as empty strings. Tests should assert target UUID, category, action, and metadata for complete and incomplete snapshot params.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/eventing/snapshot_events.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/controller_grpc.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/controller_grpc.rs

## Purpose
Provides gRPC-facing helper functions for listing NVMe controllers and fetching per-controller I/O statistics.

## Important APIs, Types, and Functions
- `NvmeControllerInfo` includes controller name, state, namespace size, and block size.
- `NvmeController::to_info()` converts controller runtime state into response data.
- `controller_stats(controller_name)` asynchronously obtains `BlockDeviceIoStats`.
- `list_controllers()` returns info for all names in `NVME_CONTROLLERS`.

## Control Flow and State
`controller_stats` looks up a controller by name, creates a oneshot, locks the controller, calls its callback-style `get_io_stats`, and awaits the result. If submission fails, it logs and returns the `CoreError`. If the controller name is absent, it returns `CoreError::BdevNotFound`. `list_controllers` iterates the controller registry names, re-lookups each controller, locks it, and converts it to info. Namespace absence yields zero size and block size.

State lives in `NVME_CONTROLLERS`; this file only reads it and bridges callback results to async.

## Dependencies and Integration Points
Used by gRPC v0/v1 host/controller services and io-engine client controller stats commands. Depends on `NvmeController`, `NvmeControllerState`, `NVME_CONTROLLERS`, `BlockDeviceIoStats`, `CoreError`, and callback helpers.

## Risks and Test Signals
Registry entries can disappear between name listing and lookup, so `filter_map` intentionally skips missing controllers. The stats oneshot expects a callback response; if callback is never invoked, callers await forever. Tests should cover missing controller error, namespace-less controller info, stats success/failure, and concurrent registry mutation during list.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/controller_grpc.rs -->
