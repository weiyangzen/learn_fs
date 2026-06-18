# subset-b-000416 Research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvs/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/lvs/mod.rs

## Purpose
This module is the LVS backend adapter that connects the concrete SPDK logical-volume implementation to the generic pool, replica, snapshot, and stats traits used by io-engine services. It re-exports the internal LVS/lvol types and hides backend-specific calls behind `PoolOps`, `ReplicaOps`, `SnapshotOps`, `IPoolFactory`, and `IReplicaFactory`.

## Important APIs, Types, And Functions
The public exports are `Lvs`, `Lvol`, `LvsBdev`, iterators, `LvsError`, snapshot descriptors, and snapshot ops. `impl ReplicaOps for Lvol` maps share/unshare, resize, entity-id, destroy, snapshot, and bdev access to lvol methods. `impl SnapshotOps for Lvol` maps snapshot destruction and clone creation. `impl PoolOps for Lvs` handles replica creation, pool destroy/export/grow, and error reset. `PoolLvsFactory` creates/imports/finds/lists pools; `ReplLvsFactory` converts bdevs to replicas and finds/lists replicas, snapshots, and clones.

## Control Flow
Pool creation/import starts at `PoolLvsFactory` and calls `Lvs::create_or_import` or `Lvs::import_from_args`. Replica creation calls `Lvs::create_lvol_with_opts`. Listing paths filter by backend, pool name/uuid, replica name/uuid, or snapshot/source uuid. Snapshot and clone paths first locate the relevant `Lvol`, validate whether it is a snapshot when required, then delegate to snapshot helpers in `lvol_snapshot`.

## State, Persistence, And Dependencies
State is the underlying SPDK LVS metadata and lvol properties. Entity IDs, snapshots, clone relationships, pool UUIDs, and base bdev identity come from the lvol/LVS layer. Stats use SPDK bdev stats from the lvol or the LVS base bdev. Dependencies include `core` bdev/share/snapshot traits, `pool_backend`, `replica_backend`, SPDK bdev stats reset, and the internal LVS submodules.

## Integration Points
This is the LVS implementation selected by `PoolFactory` and `ReplicaFactory`. It integrates with RPC/control-plane operations that create/list/destroy pools and replicas, NVMf sharing via `Lvol::share_nvmf`, snapshot RPC flows through `SnapshotOps`, and pool metrics through `BdevStater`.

## Risks
`ReplLvsFactory::find` returns any lvol by UUID and relies on upper layers to reject snapshots unless requested. Pool disk reporting unwraps crypto base bdevs and returns an empty list if the base bdev is not available. Snapshot lookup paths convert missing lvols into `Invalid` errors while other list paths silently return empty results, so callers need to account for mixed semantics.

## Test Signals
Useful coverage includes creating/importing/exporting/growing/destroying LVS pools, creating and listing replicas with every filter, verifying snapshot and clone list behavior, rejecting non-snapshot lookups through `find_snap`, share/unshare and PTPL paths, stats/reset behavior, encrypted pool disk reporting, and bdev-to-replica conversion for snapshot and non-snapshot lvols.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/lvs/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/persistent_store.rs -->
# sources/control-plane/mayastor/io-engine/src/persistent_store.rs

## Purpose
This file provides the global persistent-store facade used to keep Mayastor state in etcd across restarts. It hides the etcd client behind `PersistentStore`, centralizes endpoint/timeout/retry configuration, and routes all store work onto the primary reactor so store users do not directly couple to the tokio-backed etcd client.

## Important APIs, Types, And Functions
`PersistentStoreBuilder` configures default port, endpoint, timeout, and retry count. `PersistentStore::put`, `txn_create_execute`, `get`, and `delete` are the public async operations. `execute_store_op` submits a closure to `Reactor::spawn_at_primary` and waits for a oneshot result with timeout/retry handling. `connect_to_backing_store`, `reconnect`, `enabled`, `endpoint`, `timeout`, `retries`, and `to_json_byte_vec` support initialization and diagnostics.

## Control Flow
Calling `PersistentStoreBuilder::connect` initializes the `OnceCell` only when an endpoint was provided. Store operations clone the current etcd client under a `parking_lot::Mutex`, spawn the actual `Store` trait call on the primary reactor, and wait with `tokio::time::timeout`. On operation failure or timeout, retries are attempted; when the backing store reports offline, the facade reconnects before retrying.

## State, Persistence, And Dependencies
Process state is held in `PERSISTENT_STORE: OnceCell<Mutex<PersistentStore>>` with endpoint, timeout, retries, and an `Etcd` client. Persistent state lives in etcd as JSON-serialized values. Dependencies include `store::etcd::Etcd`, `Store` traits and errors, `serde_json`, futures oneshots, `snafu`, and the Mayastor reactor abstraction.

## Integration Points
Any subsystem needing durable metadata can call the static `PersistentStore` methods without owning the etcd client. CAS creation uses `txn_create_execute`, which passes explicit new/expected byte values to the store backend. The file is also part of startup configuration because no endpoint means persistence is disabled.

## Risks
All static methods panic if called when persistence was not initialized, except `enabled`. Endpoint parsing treats any colon as an existing port, which is ambiguous for raw IPv6 addresses. Errors during serialization in `to_json_byte_vec` panic. The global mutex protects client replacement but can serialize all operations. Timeout/retry behavior may repeat non-idempotent writes unless higher-level keys are designed idempotently.

## Test Signals
Tests should cover disabled store startup, endpoint default-port insertion, successful put/get/delete, missing key propagation, CAS success and conflict return values, reconnect after an offline client, operation timeout and retry exhaustion, and reactor scheduling from non-primary contexts.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/persistent_store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/pool_backend.rs -->
# sources/control-plane/mayastor/io-engine/src/pool_backend.rs

## Purpose
This file defines the backend-neutral pool contract used by io-engine. It models pool creation arguments, metadata, backend selection, pool operations, error mapping, and the factory that probes enabled backends.

## Important APIs, Types, And Functions
`PoolArgs`, `PoolMetadataArgs`, `ReplicaArgs`, `ListPoolArgs`, and `FindPoolArgs` are request models. `PoolBackend` selects `Lvs` or `Lvm` and can be parsed/serialized. `GenericError` and `Error` convert backend failures to errno and tonic status. `PoolOps` defines create replica, destroy, export, grow, and reset errors. `IPoolFactory` is implemented by concrete backends. `PoolFactory::all_backends`, `backends`, `factories`, `new`, and `find` select and probe backends.

## Control Flow
Callers construct pool or list/find args, then either create a concrete factory or ask `PoolFactory::find` to probe every enabled backend. `PoolFactory::backends` filters all backends through `PoolBackend::enabled`. `find` returns the first backend that yields a pool, preserves the last backend error, and returns `NotFound` if none match and no backend returned a richer error.

## State, Persistence, And Dependencies
This file owns no runtime state. It defines contracts for state held by backend implementations. It depends on core bdev stats traits, encryption keys, logical volume types, `snafu`, `nix::errno`, tonic status conversion, and the concrete LVS/LVM factories.

## Integration Points
RPC layers use these traits to remain backend-neutral. LVS and LVM modules implement the factory and operation traits. Replica creation flows pass `ReplicaArgs` into `PoolOps::create_repl`, while metrics layers use `IPoolProps` and `BdevStater`.

## Risks
Factory probing can mask earlier backend errors if a later backend also errors. Backend enablement is dynamic, so feature or runtime configuration can change visible backends. `FindPoolArgs::uuid_or_name` is a compatibility path that can make name/uuid ambiguity observable.

## Test Signals
Coverage should verify backend filtering, `PoolFactory::find` with uuid/name/name+uuid, error-to-tonic and error-to-errno mapping, `ReplicaArgs` builder flags, encryption argument propagation, and behavior when one backend is disabled or errors.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/pool_backend.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/pool_information.rs -->
# sources/control-plane/mayastor/io-engine/src/pool_information.rs

## Purpose
This file stores lightweight in-memory pool runtime status, currently focused on pool I/O stall state and recent stall-transition timestamps.

## Important APIs, Types, And Functions
`POOL_INFO` is a global `Lazy<RwLock<HashMap<String, RwLock<PoolInfo>>>>`. `PoolInfo` has `io_stalled` and `transition_timestamps`. `PoolInfo::update_transition_timestamp` drops timestamps outside a configured window. `PoolInfo::get`, `pool_info_read`, and `pool_info_write` expose guarded access.

## Control Flow
Callers insert or update pool entries through the write guard, then read individual pool state through mapped read guards. `update_transition_timestamp` is called by consumers after state transitions to keep the rolling window bounded.

## State, Persistence, And Dependencies
All state is process-local and lost on restart. It depends only on `once_cell`, `parking_lot`, `HashMap`, `VecDeque`, and `Instant`.

## Integration Points
Pool health and stall-detection code can use this as shared runtime state without touching backend metadata. The API returns lock guards, so callers can cheaply inspect state while preserving synchronization.

## Risks
There is no automatic entry creation or eviction here; callers must manage map lifecycle. Nested `RwLock`s reduce coarse contention but can create lock-order risks if external code mixes map and entry locks carelessly. Timestamps are monotonic `Instant`s and cannot be serialized.

## Test Signals
Tests should cover insertion/read lookup, missing pool lookup, transition timestamp retention with short and long windows, and concurrent read/write access patterns.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/pool_information.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/prctl.rs -->
# sources/control-plane/mayastor/io-engine/src/prctl.rs

## Purpose
This file wraps Linux `prctl(PR_SET_IO_FLUSHER)` so io-engine threads involved in block I/O can mark themselves as I/O flushers and receive special kernel memory-allocation treatment.

## Important APIs, Types, And Functions
`Prctl::set_io_flusher` calls `libc::prctl(PR_SET_IO_FLUSHER, 1, 0, 0, 0)` and returns `std::io::Result<()>`.

## Control Flow
The function performs one unsafe libc call. A nonzero return is converted to `Error::last_os_error`; zero is success.

## State, Persistence, And Dependencies
The state change is per calling thread/process context in the Linux kernel. Dependencies are `libc` and `std::io`.

## Integration Points
Startup or reactor/thread setup code can call this before participating in block-layer or filesystem I/O paths.

## Risks
`PR_SET_IO_FLUSHER` is Linux-specific and may fail on older kernels, unsupported platforms, or without required privileges/capabilities. The wrapper only enables the flag; it does not expose a clear operation.

## Test Signals
Validation should call the wrapper on supported Linux kernels and assert success or expected `last_os_error` on unsupported environments. Integration tests should ensure failures are logged/handled by the caller rather than silently ignored.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/prctl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/bdev_rebuild.rs -->
# sources/control-plane/mayastor/io-engine/src/rebuild/bdev_rebuild.rs

## Purpose
This file implements the generic bdev-to-bdev rebuild job. It is the base data-copy engine used directly for arbitrary block-device rebuilds and indirectly by snapshot rebuilds.

## Important APIs, Types, And Functions
`BdevRebuildJob` wraps `RebuildJob` and dereferences to it. `BdevRebuildJobBuilder` accepts a range, options, notification callback, and optional `SegmentMap`. `build` creates a `RebuildDescriptor`, allocates a `RebuildTasks` pool, chooses `FullRebuild` or `PartialRebuild`, and returns a frontend job. `BdevRebuildJobBackend<R>` implements `RebuildBackend`.

## Control Flow
The builder opens and validates source/destination through `RebuildDescriptor::new`. Without a bitmap, the backend walks every segment in range. With a bitmap, the descriptor validates map range and `PartialRebuild` schedules only dirty segments. `schedule_task_by_id` takes the next block from the range walker, submits the segment copy to the task pool, and increments active task count.

## State, Persistence, And Dependencies
Runtime state is the descriptor, range walker, task pool, and callback. No durable state is stored. It depends on `SegmentMap`, generic rebuild state/manager/task modules, and the `gen_rebuild_instances!` macro for global in-process job lookup.

## Integration Points
Consumers call `BdevRebuildJob::builder()` and then use inherited `RebuildJob` methods to start/stop/pause/resume/stats. Snapshot rebuild composes this builder. The notification function lets upper layers react to state changes with source/destination URI context.

## Risks
`PartialRebuild::is_partial` currently returns false, so stats for that path may mislabel partial work. Task scheduling mutates `active` outside the task pool method, which requires backend implementations to stay disciplined. Rebuild instances are keyed by destination URI and must run on an SPDK thread.

## Test Signals
Test full and bitmap rebuilds, invalid map range, same source/destination rejection, callback invocation on state changes, job instance store/lookup/remove behavior, and stats for partial-vs-full rebuilds.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/bdev_rebuild.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/rebuild/mod.rs

## Purpose
This is the rebuild module root. It declares the rebuild submodules, re-exports the public job/state/stats/map types, and holds shared constants and helpers.

## Important APIs, Types, And Functions
Public exports include `BdevRebuildJob`, `NexusRebuildJob`, `NexusRebuildJobStarter`, `RebuildJob`, `RebuildJobOptions`, `RebuildVerifyMode`, `RebuildMap`, `RebuildState`, `RebuildStats`, and `SnapshotRebuildJob`. `SEGMENT_TASKS` is the per-job concurrency count and `SEGMENT_SIZE` is derived from `SPDK_BDEV_LARGE_BUF_MAX_SIZE`. `WithinRange` validates nested ranges. `shutdown_snapshot_rebuilds` stops all snapshot rebuilds. `parse_url` maps URL parse errors into `RebuildError`.

## Control Flow
Most logic lives in child modules. The module-level shutdown helper collects forced stop receivers from all snapshot rebuild jobs and awaits them. `parse_url` is a small compatibility wrapper around `url::Url::parse`.

## State, Persistence, And Dependencies
No state is stored here beyond constants. It depends on SPDK constants, URL parsing, and child modules.

## Integration Points
Other io-engine code imports rebuild jobs and state from this module rather than individual submodules. Shutdown paths use `shutdown_snapshot_rebuilds` to drain outstanding snapshot copy work.

## Risks
`SEGMENT_TASKS` and `SEGMENT_SIZE` are global policy knobs; changing them affects memory use, concurrency, and copy granularity across all rebuild variants. `WithinRange` rejects empty ranges and overflow-prone ranges, so callers must use exclusive-end ranges correctly.

## Test Signals
Validate range containment edge cases, URL parse error mapping, snapshot rebuild shutdown behavior with running/stopped jobs, and exported API compatibility for downstream modules.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/nexus_rebuild.rs -->
# sources/control-plane/mayastor/io-engine/src/rebuild/nexus_rebuild.rs

## Purpose
This file implements nexus-aware rebuild jobs. It adds a nexus descriptor and LBA range locking around generic segment copies so frontend I/O cannot race the rebuild on the same logical range.

## Important APIs, Types, And Functions
`NexusRebuildJob` wraps `RebuildJob`. `NexusRebuildJobStarter` lets callers create and optionally store a job before deciding whether to start full or partial-sequential rebuild. `NexusRebuildJob::new_starter` builds descriptors and task pools. `NexusRebuildDescriptor` adds `nexus_name` and a nexus `DescriptorGuard`. `NexusRebuildJobBackendStarter` creates full or partial-seq backends. `NexusRebuildDescriptor::copy_segment` locks and unlocks nexus LBA ranges.

## Control Flow
`new_starter` creates a `RebuildDescriptor`, task pool, nexus descriptor, and frontend manager without immediately scheduling backend work. `store` records the frontend job in the global instance map. `start` consumes the backend starter, picks full or partial sequential mode based on a `RebuildMap`, schedules the backend manager, then starts the frontend job. Each scheduled segment locks the corresponding nexus data-range offset, performs the copy, and unlocks the range.

## State, Persistence, And Dependencies
State includes frontend job state, backend task pool, range walker, nexus bdev descriptor, and optional rebuild map. It is in-memory only. Dependencies include SPDK `LbaRange`, `UntypedBdev`, nexus descriptor range locks, rebuild maps, and the common rebuild manager.

## Integration Points
Nexus child-replacement and resynchronization code use this path so live I/O and rebuild I/O are synchronized. Notifications pass nexus name and destination URI back to the owning nexus.

## Risks
Range locking uses offsets adjusted by `self.range.start`; incorrect ranges can underflow or lock wrong areas. The safety comment notes raw-pointer lifetime constraints in lock/unlock callbacks. Partial rebuild uses `PartialSeqRebuild`, which still schedules every segment and skips clean blocks inside the copier, trading simplicity for task overhead. `stop_for_destroy` or forced failure must wait for active range locks to release.

## Test Signals
Tests should cover full and partial-seq starts, store-before-start behavior, source/destination validation, range-lock failure and unlock failure mapping, frontend I/O exclusion during segment copy, and notify callback arguments.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/nexus_rebuild.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_descriptor.rs -->
# sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_descriptor.rs

## Purpose
This file owns the common data-plane descriptor for rebuild copying. It opens source and destination bdevs, validates range compatibility, allocates DMA buffers, reads source segments, writes destination segments, and optionally verifies copied data.

## Important APIs, Types, And Functions
`RebuildDescriptor::new` opens bdevs from URIs and computes block/range/segment metadata. `validate` checks ranges and block-size compatibility. `validate_map` validates bitmap coverage. `get_segment_size_blks`, `dma_malloc`, `src_io_handle`, `dst_io_handle`, and `adjusted_iov` support task execution. `read_src_segment`, `write_dst_segment`, `verify_segment`, and `verify_failure` implement I/O.

## Control Flow
Construction resolves bdev names from URIs, opens source read-only and destination writable, rejects identical devices, gets nonblocking I/O handles, chooses a full destination range when none is supplied, validates both devices, and records start time. Copy tasks request an adjusted iovec, read the source, skip writes on NVMe unwritten-block status, write destination data, and verify if configured. Compare failures are ignored, converted to rebuild failure, or panic depending on `RebuildVerifyMode`.

## State, Persistence, And Dependencies
The descriptor keeps source/destination descriptors and handles open for the job lifetime. Persistent state is only the destination data written by I/O. Dependencies include `device_open`, bdev URI parsing, SPDK DMA buffers and NVMe statuses, core block-device traits, read options, and rebuild options/errors.

## Integration Points
Every rebuild backend delegates actual copy I/O to this descriptor, either directly or through wrappers like `NexusRebuildDescriptor` and `PartialSeqCopier`. Stats use descriptor block size, range, segment size, and start time.

## Risks
The current validation assumes equal block size and TODOs label/data partition protection. `adjusted_iov` asserts the buffer is large enough, so unexpected segment sizing can panic. Verification rereads the source after writing, which can report false mismatches if the source changes outside nexus range-lock protection. Unwritten source blocks skip destination writes and rely on destination state semantics being acceptable.

## Test Signals
Test invalid URI, missing bdev, same bdev, mismatched block size, out-of-range rebuild ranges, partial final segment sizing, unwritten-block read skip, write errors, verify compare modes, and DMA allocation alignment.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_descriptor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_error.rs -->
# sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_error.rs

## Purpose
This file defines typed errors for rebuild and snapshot rebuild operations using SNAFU. It is the common error vocabulary for job lifecycle, descriptor validation, I/O, task channels, frontend/backend liveness, nexus range locks, URI parsing, and snapshot URI setup.

## Important APIs, Types, And Functions
`RebuildError` includes job existence/lookup, copy buffer allocation, invalid ranges/maps, same bdev, bdev handle/open failures, read/write/verify I/O failures, state operation errors, pending-state conflicts, range lock/unlock failures, invalid URI, dropped frontend/backend, closed task channel, and wrapped `SnapshotRebuildError`. `SnapshotRebuildError` covers missing local bdev, missing remote URI, non-replica bdevs, and URI bdev open failure. `From<SnapshotRebuildError> for RebuildError` wraps snapshot errors.

## Control Flow
Other modules construct these variants through SNAFU contexts or direct errors. The variants carry enough source context for display strings and higher-level conversions through `VerboseError`.

## State, Persistence, And Dependencies
This file stores no state. It depends on `BdevError`, `CoreError`, SPDK descriptor/DMA errors, and `snafu`.

## Integration Points
Rebuild frontend methods, backend manager, descriptor I/O, task scheduling, nexus range locking, and snapshot rebuild builders all return these errors. RPC layers can map them through higher-level error conversion.

## Risks
`RebuildError` derives `Clone`, so embedded source errors must remain cloneable or the type contract changes. Some variants use generic errno-like meanings in display text but do not directly encode retryability. Snapshot errors are flattened under a single rebuild variant, so callers that need exact snapshot failure categories must inspect the source.

## Test Signals
Tests should assert important display strings, SNAFU source preservation, snapshot-to-rebuild conversion, clone compatibility after adding variants, and error mapping in callers that translate to tonic status or errno.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_instances.rs -->
# sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_instances.rs

## Purpose
This file provides the `gen_rebuild_instances!` macro, which gives rebuild job types a static in-process registry keyed by job name.

## Important APIs, Types, And Functions
The macro creates a `RebuildJobInstances` map and methods `count`, `remove`, `store`, `lookup`, and `lookup_src` for the target type. `get_instances` initializes a `OnceCell<Mutex<HashMap<String, Arc<T>>>>` and asserts it runs on an SPDK thread.

## Control Flow
Each rebuild type invokes the macro. `store` rejects duplicate names with `JobAlreadyExists`, wraps the job in `Arc`, and inserts it. Lookup and removal return cloned or removed arcs. `lookup_src` filters values by `src_uri`.

## State, Persistence, And Dependencies
State is process-local static memory per macro invocation/type. It depends on `once_cell`, `parking_lot`, `HashMap`, `Arc`, SPDK thread checks, and the rebuild error type.

## Integration Points
`BdevRebuildJob`, `NexusRebuildJob`, and `SnapshotRebuildJob` use this macro to expose job discovery and lifecycle functions to control-plane code.

## Risks
The registry is per type, so the same key can exist in different rebuild classes. The SPDK-thread assertion will panic if called from an arbitrary async runtime thread. Jobs remain alive until explicitly removed, so failed cleanup leaks registry entries.

## Test Signals
Coverage should verify duplicate rejection, removal of absent jobs, lookup by name and source URI, type isolation, and panic behavior or caller discipline for non-SPDK-thread access.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_instances.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_job.rs -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_job.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_job_backend.rs -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_job_backend.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_map.rs -->
# sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_map.rs

## Purpose
This file wraps a `SegmentMap` with device identity and exposes rebuild-specific dirty/clean segment operations.

## Important APIs, Types, And Functions
`RebuildMap::new` constructs the wrapper. `is_blk_clean` checks whether a logical block does not need transfer. `blk_clean` marks a block clean. `count_dirty_blks` counts remaining dirty blocks. `From<RebuildMap> for BitVec` consumes the segment map into a bit vector.

## Control Flow
Range walkers and partial copy wrappers query the map before copying. Successful partial-sequential copies call `blk_clean` to reduce future remaining work.

## State, Persistence, And Dependencies
State is in-memory `SegmentMap` bits plus `device_name` for diagnostics. Dependencies include `bit_vec` and core `SegmentMap`.

## Integration Points
Nexus partial rebuilds receive a `RebuildMap` from child dirty-bit state. `PartialSeqCopier` locks and mutates the map as segments are copied.

## Risks
Out-of-range map access logs an error and returns dirty/unclean semantics, which avoids data loss but can increase copy work. `blk_clean` assumes the map supports the requested block. Device name is diagnostic only and is not used to validate that the map matches a destination.

## Test Signals
Test clean/dirty queries, out-of-range behavior, dirty count updates after `blk_clean`, conversion to `BitVec`, and use with segment sizes larger than one block.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_map.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_state.rs -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_state.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_stats.rs -->
# sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_stats.rs

## Purpose
This file defines rebuild statistics and history record structures used by running jobs and post-completion reporting.

## Important APIs, Types, And Functions
`RebuildStats` records total/recovered/transferred/remaining blocks, percent progress, blocks per task, block size, total and active tasks, start time, partial flag, and optional end time. `Default` initializes zero counters and current start time. `HistoryRecord` stores child URI, source URI, final stats, final state, and end time, and derefs to `RebuildStats`.

## Control Flow
The backend manager computes `RebuildStats` from task counters and backend descriptors. `RebuildStates::set_final_stats` sets the end time. `RebuildJob::history_record` wraps final stats with URI/state metadata.

## State, Persistence, And Dependencies
These are in-memory data structures. They depend on `chrono` and `RebuildState`.

## Integration Points
RPC/status paths can expose these fields to control-plane clients. History records are lightweight extracts for completed jobs.

## Risks
`progress` is an integer percentage and may lose precision. Defaults use the current timestamp even for placeholder stats, which can be misleading if returned after backend failure. `HistoryRecord` hides `final_stats` from outside the crate except through deref.

## Test Signals
Validate stats calculations in the backend manager, final end-time assignment, default values, history record creation, and partial rebuild `is_partial` propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_stats.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_task.rs -->
# sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_task.rs

## Purpose
This file implements the per-segment copy worker and task pool used by rebuild backends.

## Important APIs, Types, And Functions
`TaskResult` reports task id, block, optional error, and whether data was transferred. `RebuildTask` owns a DMA buffer, completion sender, and last error/result. `RebuildTask::copy_one` performs read, write, and optional verify for one segment. `RebuildTasks` preallocates task buffers, tracks active/total/done/transferred counts, schedules segment rebuild futures, and awaits completions. `RebuildTaskCopier` abstracts direct or wrapped segment copy implementations.

## Control Flow
`RebuildTasks::new` creates an unbuffered MPSC channel and one DMA buffer per task. `schedule_segment_rebuild` sends a future to the current reactor, locks the task, runs the copier, stores a `TaskResult`, and sends it back. `await_one_task` receives a result, decrements active count, and updates counters on success.

## State, Persistence, And Dependencies
State is in-memory task buffers and counters. Persistent impact is destination data written by the descriptor. Dependencies include `DmaBuf`, Mayastor reactors, futures MPSC, `parking_lot::Mutex`, `Arc`, `Rc`, `VerboseError`, and `SEGMENT_SIZE`.

## Integration Points
Bdev and nexus backends schedule work through this pool. `RebuildDescriptor` implements `RebuildTaskCopier` for the direct copy case; nexus and partial wrappers implement it for synchronized or bitmap-filtered copies.

## Risks
The async future holds a `parking_lot::MutexGuard` across await, explicitly allowed in code; this is safe only because each task is uniquely scheduled, but future changes could introduce deadlocks. Active count is managed by callers and `await_one_task`, so missed sends or channel termination can desynchronize manager state. Each task preallocates a large DMA buffer, so concurrency directly affects memory use.

## Test Signals
Tests should cover successful transfer, unwritten-source skip, read/write/verify errors, channel close behavior, counter updates, one-buffer-per-task allocation failures, and reactor scheduling assumptions.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_task.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuilders.rs -->
# sources/control-plane/mayastor/io-engine/src/rebuild/rebuilders.rs

## Purpose
This file implements range-walking strategies for rebuilds: full, bitmap-filtered partial, and partial sequential with clean-segment skipping.

## Important APIs, Types, And Functions
`RangeRebuilder<T>` defines `next`, `peek_next`, `blocks_remaining`, `is_partial`, `desc`, and `copier`. `FullRebuild` steps through the descriptor range by segment size. `PartialRebuild` consumes a `SegmentMap` bit vector and schedules set bits. `PartialSeqRebuild` walks the whole descriptor range while `PartialSeqCopier` skips clean blocks and marks successful blocks clean. `PeekableIterator` provides immutable peek over iterators.

## Control Flow
Backends call `next` to get a block address and `copier` to get the copy implementation for that range. Full rebuild always schedules every segment. Partial rebuild iterates set bits and tracks dirty blocks consumed. Partial sequential rebuild schedules all segment starts but makes the copier no-op for clean segments.

## State, Persistence, And Dependencies
Range-walker state is in-memory iterator position, copied descriptor in `Rc`, and for partial sequential rebuild a mutex-protected `RebuildMap`. Dependencies include `SegmentMap`, `RebuildMap`, `BitVec`, `Rc`, and `parking_lot`.

## Integration Points
Bdev rebuild uses `FullRebuild` or `PartialRebuild`. Nexus rebuild uses `FullRebuild` or `PartialSeqRebuild` because it must coordinate with nexus dirty-map behavior.

## Risks
`PartialRebuild::is_partial` returns false despite being partial, likely affecting stats. In `PartialRebuild::next`, the enumerated bit index is returned as a block address without multiplying by segment size, which must match `SegmentMap` iterator semantics or it will address wrong blocks. Partial sequential mode schedules clean segments and only skips during copy, which can add overhead to mostly-clean maps.

## Test Signals
Coverage should validate block addresses from every walker, remaining-block calculations, `is_partial` values, clean-skip behavior, map mutation after success, no mutation after failure, and `PeekableIterator` correctness.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/rebuilders.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/snapshot_rebuild.rs -->
# sources/control-plane/mayastor/io-engine/src/rebuild/snapshot_rebuild.rs

## Purpose
This file implements snapshot-to-replica rebuild jobs. It composes the generic bdev rebuild engine with URI creation/destruction logic and snapshot/replica metadata.

## Important APIs, Types, And Functions
`SnapshotRebuildJob` wraps a `BdevRebuildJob` plus job UUID, replica UUID, snapshot UUID, and `Uri` wrappers. `Uri` can create/open and later destroy a bdev URI. `SnapshotRebuildJobBuilder` accepts rebuild options, notify callback, bitmap, UUIDs, and explicit replica/snapshot URIs. `build` resolves/creates URIs, builds the inner bdev rebuild, and cleans up on failure. `SnapshotRebuildJob::builder`, `list`, metadata accessors, and `destroy` are public helpers.

## Control Flow
The builder resolves snapshot and replica URIs from explicit URIs or local lvol UUIDs. Explicit URIs are created before use and marked for deletion if creation succeeded. If creating the replica URI fails, the snapshot URI is closed/destroyed. After successful URI setup, the inner bdev rebuild is built from snapshot URI to replica URI. On inner build failure, both URIs are closed. Dropping a `Uri` marked for deletion schedules async destruction on the master reactor.

## State, Persistence, And Dependencies
Runtime state is the inner rebuild job and URI cleanup flags. Persistent effects include data copied into the replica and temporary bdevs created for remote URIs. Dependencies include `device_create`, `device_destroy`, `Bdev`, LVS `Lvol`, generic bdev rebuild, reactors, read options, and rebuild instance macros.

## Integration Points
Snapshot restore/control-plane flows use this job type. `shutdown_snapshot_rebuilds` enumerates and force-stops active snapshot rebuild jobs. The default builder uses `ReadOptions::CurrentUnwrittenFail` to make snapshot reads fail on current unwritten state.

## Risks
The builder has TODOs where lvol snapshot-vs-replica validation comments do not actually return errors. URI destruction is best-effort and async in `Drop`, so cleanup can lag or fail. Explicit URI creation treats `BdevExists` as non-owned and therefore does not delete it, which is correct but depends on accurate ownership assumptions.

## Test Signals
Test explicit and local URI resolution, cleanup when snapshot or replica URI creation fails, inner rebuild build failure cleanup, metadata accessors, instance list/destroy behavior, default read options, and best-effort async cleanup logging.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/rebuild/snapshot_rebuild.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/replica_backend.rs -->
# sources/control-plane/mayastor/io-engine/src/replica_backend.rs

## Purpose
This file defines the backend-neutral replica and snapshot contracts. It lets higher-level code manipulate replicas, snapshots, and clones without depending on LVS or LVM implementation details.

## Important APIs, Types, And Functions
`ReplicaOps` extends `LogicalVolume` and `BdevStater` with share/unshare/update, resize, entity ID, destroy, snapshot creation, snapshot config preparation, PTPL creation, and bdev access. `SnapshotOps` defines snapshot destroy, clone config preparation, clone creation, descriptor lookup, and discarded-state check. `ListReplicaArgs`, `FindReplicaArgs`, `ListSnapshotArgs`, `FindSnapshotArgs`, and `ListCloneArgs` are filter types. `IReplicaFactory` is the backend trait. `ReplicaBdevStats` augments bdev stats with entity and pool metadata. `ReplicaFactory` selects concrete factories and probes replicas.

## Control Flow
Callers use filter structs to locate replicas/snapshots/clones through every enabled backend. `ReplicaFactory::find` returns the first non-snapshot replica unless `allow_snapshots` is set. `bdev_as_replica` asks each backend whether an untyped bdev can be treated as a replica. Default snapshot/clone config helpers construct `SnapshotParams` and `CloneParams` from names/UUIDs.

## State, Persistence, And Dependencies
This file holds no state. It defines abstractions over backend state. Dependencies include core logical volume, share, snapshot, bdev stats types, pool backend errors, and concrete LVS/LVM replica factories.

## Integration Points
RPC services, NVMf custom admin snapshot handling, snapshot/clone workflows, and stats paths use these traits. LVS implements the traits in `lvs/mod.rs`.

## Risks
Factory probing hides backend order in `PoolFactory::backends`. `FindReplicaArgs::allow_snapshots` is a subtle safety switch. Trait objects use `?Send`, consistent with SPDK thread affinity but requiring callers to stay on appropriate reactors.

## Test Signals
Tests should verify replica lookup excludes snapshots by default, `allow_snapshots` behavior, bdev-to-replica conversion, stats metadata construction, snapshot/clone config helpers, and multi-backend probing error behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/replica_backend.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/sleep.rs -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/sleep.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/store/etcd.rs -->
# sources/control-plane/mayastor/io-engine/src/store/etcd.rs

## Purpose
This file implements the generic `Store` trait for etcd using the `etcd-client` crate.

## Important APIs, Types, And Functions
`Etcd(Client)` wraps an etcd client. `Etcd::new` connects to an endpoint. The `Store` implementation provides `put_kv`, `put_kv_cas`, `get_kv`, `delete_kv`, and `online`.

## Control Flow
`put_kv` serializes values to JSON bytes and writes them to etcd. `put_kv_cas` builds an etcd transaction comparing the current value with an expected byte vector; on success it writes the new value, and on compare failure it returns the current stored value if present. `get_kv` reads the first key-value pair and deserializes JSON. `delete_kv` deletes the key. `online` checks etcd status.

## State, Persistence, And Dependencies
Persistent state is etcd key-value data. The wrapper stores a client handle and is cloneable. Dependencies include `etcd_client`, `serde_json`, `async_trait`, SNAFU error contexts, and store trait definitions.

## Integration Points
`PersistentStore` uses this as its backing store. Higher layers pass keys and serializable values through the generic store traits.

## Risks
`put_kv` uses `serde_json::to_string(value).unwrap()` in error context after `to_vec` succeeded; this is probably safe for the same value but still a panic path. CAS compare is byte-for-byte JSON, so semantically equal values with different serialization cannot match. `get_kv` returns only the first KV and treats absence as `MissingEntry`.

## Test Signals
Test connection failure, JSON put/get round trip, missing key, delete, CAS success, CAS conflict returning current bytes, malformed stored JSON deserialization failure, and `online` false when etcd is unavailable.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/store/etcd.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/store/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/store/mod.rs

## Purpose
This module root exposes the persistent-store backend implementation and shared store trait definitions.

## Important APIs, Types, And Functions
It declares `pub mod etcd;` and `pub mod store_defs;`.

## Control Flow
There is no runtime logic. The file controls module visibility for `crate::store::etcd` and `crate::store::store_defs`.

## State, Persistence, And Dependencies
No state is stored here. Persistence behavior lives in `etcd.rs` and `persistent_store.rs`.

## Integration Points
Other modules import store traits and the etcd backend through this module path.

## Risks
Making both modules public exposes low-level backend and trait details crate-wide. Any additional backend must be wired here.

## Test Signals
Compile-level tests/imports are sufficient; functional behavior belongs to child module tests.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/store/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/store/store_defs.rs -->
# sources/control-plane/mayastor/io-engine/src/store/store_defs.rs

## Purpose
This file defines the generic key-value store trait and the error taxonomy used by persistent store backends.

## Important APIs, Types, And Functions
`StoreError` covers connect, put/get/delete/txn/watch, wait-channel cancellation, missing entries, string conversion, serialization/deserialization, and operation timeout. `StoreKey` and `StoreValue` are blanket marker traits for key and serializable value types. `Store` defines async `put_kv`, `put_kv_cas`, `get_kv`, `delete_kv`, and `online`.

## Control Flow
Backend implementations use SNAFU contexts to construct `StoreError` variants. `PersistentStore` receives these errors and wraps wait/timeout behavior around trait calls.

## State, Persistence, And Dependencies
This file stores no state. It depends on `async_trait`, `etcd_client::Error`, `serde_json`, futures oneshot cancellation, and SNAFU.

## Integration Points
`store/etcd.rs` implements this trait. `persistent_store.rs` uses the trait bounds to remain backend-agnostic.

## Risks
Error variants are etcd-client-specific even though the trait is generic, which couples alternate backends to etcd error types or requires broader refactoring. Blanket `StoreKey` accepts any `ToString + Debug`, so poorly designed key string formats are not prevented by the type system.

## Test Signals
Tests should verify error display strings, blanket trait usability with expected key/value types, CAS trait signature behavior, and backend implementations mapping each error context correctly.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/store/store_defs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/config/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/subsys/config/mod.rs

## Purpose
This file implements the Mayastor configuration subsystem. It loads partial YAML config, applies SPDK option groups before use, exports current configuration via JSON-RPC/SPDK config JSON, and persists refreshed config back to disk.

## Important APIs, Types, And Functions
`ConfigSubsystem` builds an SPDK subsystem with init/fini/config callbacks. `EalOpts` and `Config` are serde models. `CONFIG` is the global `OnceCell<Config>`. `Config::get_or_init`, `get`, `read`, `refresh`, `write`, and `apply` are the core API. The subsystem init registers `mayastor_config_export`.

## Control Flow
Startup initializes `CONFIG` from defaults or `Config::read`. `Config::apply` applies NVMe bdev, generic bdev, posix socket, and iobuf options, while NVMf target config is used later during target creation. During SPDK subsystem init, JSON-RPC export is registered and subsystem initialization advances. The export RPC refreshes current settings, then writes back to the original source file if present.

## State, Persistence, And Dependencies
Config state is a process-global immutable `Config`; refreshed exports query live SPDK options. Persistence is YAML on disk at `source`. Dependencies include serde YAML/JSON, SPDK subsystem and JSON callbacks, JSON-RPC registration, and option structs from `opts.rs`.

## Integration Points
`subsys/mod.rs` registers this subsystem before NVMf. NVMf target setup reads `Config::get().nvmf_tgt_conf` and `nexus_opts`. Runtime tooling can call `mayastor_config_export` to save current config.

## Risks
`Config::get` unwraps and will panic if called before initialization. `apply` asserts option setters succeed, turning configuration failures into panics. The source file is overwritten on export without atomic temp-file handling. The config callback serializes to JSON raw output and silently returns on serialization error.

## Test Signals
Test empty and partial YAML reads, unknown-field rejection, source preservation, live refresh after applying options, write failures, export RPC with and without source, and startup ordering that prevents `Config::get` panics.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/config/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/config/opts.rs -->
# sources/control-plane/mayastor/io-engine/src/subsys/config/opts.rs

## Purpose
This file defines serde-friendly copies of SPDK and Mayastor option structures and conversion code to/from SPDK FFI structs. It centralizes environment overrides for NVMf, NVMe, bdev, socket, and iobuf settings.

## Important APIs, Types, And Functions
`GetOpts` defines `get` and optional `set`. `NexusOpts` controls NVMf enablement/discovery and nexus/replica ports. `NvmfTgtConfig`, `NvmfTgtTransport`, and `NvmfTransportOpts` configure the target and transports. `try_from_env` and `time_try_from_env` parse environment overrides, including humantime durations and backward-compatible unit-suffixed names. `NvmeBdevOpts`, `BdevOpts`, `PosixSocketOpts`, and `IoBufOpts` provide defaults, live getters, setters, and FFI conversions.

## Control Flow
Defaults read `MayastorEnvironment` and environment variables. `Config::apply` calls `set` on option groups that support global SPDK setters. `refresh` calls `get` to convert live SPDK options back into serde structs. NVMf target/transport options are converted into SPDK structs when target/transports are created rather than applied globally.

## State, Persistence, And Dependencies
Option values can be persisted as YAML through `Config`. Live state is in SPDK global option structures. Dependencies include SPDK FFI option APIs, `struct_size_init`, serde, humantime, strum, and `MayastorEnvironment`.

## Integration Points
NVMf target and subsystem code uses `NvmfTgtConfig` and transport options. NVMe bdev connection behavior, socket behavior, bdev I/O pool sizing, and iobuf pool sizing are all controlled here.

## Risks
FFI struct layout changes require updates; compile-time field initialization helps catch many but not all semantic changes. Environment parsing falls back to defaults on invalid values, which can hide misconfiguration unless logs are monitored. Some newer SPDK fields are hard-coded to defaults and not exposed. `PosixSocketOpts::get` asserts SPDK success.

## Test Signals
Test env override parsing, humantime and backward-compatible duration names, invalid env fallback logging, FFI round-trip conversions, setter failure handling, YAML unknown-field rejection, RDMA option overrides, and generated default values from `MayastorEnvironment`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/config/opts.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/config/pool.rs -->
# sources/control-plane/mayastor/io-engine/src/subsys/config/pool.rs

## Purpose
This file manages a separate YAML pool configuration used to import/recreate pools at startup and export current pool topology.

## Important APIs, Types, And Functions
`PoolConfig::load`, `export`, `delete`, `capture`, `create_pools`, and `import_pools` are the main API. Internal `Pool` converts to `PoolArgs` and from `LvsBdev`. `ShareType` and `Replica` are serialized models, though replica data is informational/skipped. `create_pool` submits LVS creation/import through `rpc_submit`.

## Control Flow
`load` records the config file path and deserializes YAML or returns default for empty/missing files. `import_pools` asserts it runs on the first core and blocks on `create_pools`, which iterates configured pools and calls `create_pool`. `capture` enumerates current `LvsBdev`s into pool records. `export` serializes the config on a blocking task under a mutex, then signals completion back on the primary reactor.

## State, Persistence, And Dependencies
Persistent state is YAML at the configured path. Process state includes `CONFIG_FILE` and a static mutex used to serialize export writes. Dependencies include LVS pool creation, `LvsBdev` iteration, Mayastor reactors/runtime, gRPC `rpc_submit`, tonic status, and serde YAML.

## Integration Points
Startup pool import and runtime pool export use this module. It converts pool records into `PoolArgs` for the LVS backend; encrypted pools get a generated crypto vbdev name.

## Risks
Missing config files are treated the same as empty files. Export writes are not atomic. `Pool::from(LvsBdev)` currently sets `encrypted: false` with an explicit TODO. Replica entries are skipped on serialization and not recreated. `create_pool` requires at least one disk and always uses `Lvs::create_or_import`.

## Test Signals
Test load of empty/missing/valid/invalid YAML, import failure counting, export serialization and mutex behavior, capture from LVS bdevs, encrypted pool arg conversion, delete behavior, and first-core assertion for import.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/config/pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/subsys/mod.rs

## Purpose
This module root registers Mayastor SPDK subsystems and re-exports subsystem-facing APIs.

## Important APIs, Types, And Functions
It re-exports config types, NVMf types, registration types, and `make_subsystem_serial`. `register_subsystem` adds the config subsystem, NVMf subsystem, an SPDK dependency on `bdev`, the registration subsystem, and the NVMx subsystem. `make_subsystem_serial` generates a deterministic `DCS` serial from a SHA-256 hash truncated to SPDK's 20-character serial limit.

## Control Flow
Startup calls `register_subsystem`, which creates SPDK subsystem structures and registers them with SPDK. The NVMf subsystem is registered with an explicit dependency on `bdev`. Other subsystem modules register themselves through their own registration functions.

## State, Persistence, And Dependencies
State is SPDK's subsystem registry and leaked boxed subsystem/dependency structures handed to SPDK. Dependencies include SPDK subsystem functions, config/NVMf/registration/NVMx modules, `sha2`, and `hex`.

## Integration Points
This is the central startup hook for Mayastor subsystem lifecycle. NVMf sharing depends on NVMf registering after bdev. Control-plane registration and NVMe admin queue management are also wired here.

## Risks
Subsystem names and dependency strings are raw nul-terminated byte strings; typos break SPDK ordering. Boxed subsystem/dependency pointers are intentionally leaked to SPDK. Serial generation truncates hashes, which is acceptable but still theoretically collidable.

## Test Signals
Validate subsystem registration order, dependency presence, deterministic serial generation and length, and that exported types remain available to modules using `crate::subsys::*`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/nvmf/admin_cmd.rs -->
# sources/control-plane/mayastor/io-engine/src/subsys/nvmf/admin_cmd.rs

## Purpose
This file registers and implements a custom NVMe-over-Fabrics admin command for remote snapshot creation.

## Important APIs, Types, And Functions
`NvmeCpl` wraps an NVMe completion and can access status or set `cdw0`. `NvmfReq` wraps an SPDK NVMf request and can complete success or internal-device-error with errno in `cdw0`. `set_snapshot_time` writes current Unix seconds into command dwords 10/11. `decode_snapshot_params` deserializes `NvmeSnapshotMessage` from request data. `nvmf_create_snapshot_hdlr` is the C callback. `create_remote_snapshot` calls `ReplicaOps::create_snapshot`. `setup_create_snapshot_hdlr` registers the opcode handler.

## Control Flow
The handler accepts only subsystems with exactly one namespace. It decodes snapshot parameters, obtains namespace 1 bdev/descriptor/channel, and branches on bdev driver. For published nexuses, it stamps snapshot time and passes the admin command through to the underlying bdev controller. For shared replicas/lvols, it schedules snapshot creation on the master reactor and returns asynchronous request status. Completion is sent after snapshot creation succeeds or fails.

## State, Persistence, And Dependencies
Persistent state is the snapshot metadata/data created by the replica backend. Request state is held in raw SPDK pointers wrapped by `NonNull`. Dependencies include SPDK NVMf request APIs, Mayastor nexus/nvmx snapshot message type, `ReplicaFactory`, reactors, bincode, and errno conversion.

## Integration Points
NVMf subsystem init calls `setup_create_snapshot_hdlr`. Remote hosts can trigger snapshots through the vendor/custom admin opcode. Nexus handling forwards to NVMe passthrough, while replica handling uses local `ReplicaOps`.

## Risks
`decode_snapshot_params` uses `Vec::with_capacity` and copies into the uninitialized buffer pointer, then builds a slice from the raw pointer; this relies on SPDK writing bytes but never sets vector length. The handler returns `-1` for unsupported paths, causing SPDK to handle as unsupported opcode. Raw request wrappers must outlive async snapshot creation. Only single-namespace subsystems are supported.

## Test Signals
Test snapshot message decoding, invalid payload handling, multi-namespace rejection, missing bdev rejection, nexus passthrough with timestamp dwords set, replica async success/failure completion, errno propagation, and custom opcode registration.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/nvmf/admin_cmd.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/nvmf/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/subsys/nvmf/mod.rs

## Purpose
This module root implements SPDK subsystem registration for the Mayastor NVMf target and exposes NVMf subsystem, target, request, and error APIs.

## Important APIs, Types, And Functions
`Nvmf` wraps an SPDK subsystem pointer. `Error` is the NVMf error enum with errno mapping. `NVMF_PGS` stores thread-local poll groups. The module re-exports admin command helpers, `NvmfSubsystem`, `SubType`, and `Target`. `Nvmf::init`, `fini`, and `new` are SPDK lifecycle callbacks/constructors.

## Control Flow
During SPDK init, `Nvmf::init` registers the custom snapshot admin command. If config enables NVMf, it advances the thread-local target state machine; otherwise it calls `spdk_subsystem_init_next`. During fini, it either starts NVMf target shutdown or advances SPDK fini directly when disabled.

## State, Persistence, And Dependencies
State includes the SPDK subsystem pointer, target state in `target::NVMF_TGT`, and thread-local poll groups. No durable state is stored here. Dependencies include config, JSON-RPC error codes, SPDK subsystem callbacks, poll group and transport modules, and `nix::errno`.

## Integration Points
`subsys/mod.rs` registers this subsystem after config and declares a dependency on bdev. Replica/nexus sharing uses `NvmfSubsystem` and `Target`. Error types map to RPC codes and errno values.

## Risks
NVMf startup is controlled by global config; disabled mode must still let SPDK init/fini proceed. Error-to-errno mapping is coarse for some variants. Thread-local poll groups require correct per-reactor initialization by the target module.

## Test Signals
Test enabled and disabled init/fini paths, custom admin handler registration, error errno mapping, poll group creation through target startup, and SPDK subsystem name/dependency consistency.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/nvmf/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/nvmf/poll_groups.rs -->
# sources/control-plane/mayastor/io-engine/src/subsys/nvmf/poll_groups.rs

## Purpose
This file wraps SPDK NVMf poll group creation for a Mayastor reactor thread.

## Important APIs, Types, And Functions
`PollGroup` stores an `Mthread` and a `Pg` wrapper around `*mut spdk_nvmf_poll_group`. `PollGroup::new` calls `spdk_nvmf_poll_group_create`. `group_ptr` returns the raw poll group pointer.

## Control Flow
The target code creates a poll group for an SPDK target pointer and reactor thread, then stores it in thread-local NVMf poll group state.

## State, Persistence, And Dependencies
State is a raw SPDK poll group pointer associated with an `Mthread`. No persistence exists. Dependencies are SPDK NVMf target/poll-group FFI and Mayastor `Mthread`.

## Integration Points
NVMf target connection scheduling uses these poll groups to place qpairs on reactor threads.

## Risks
There is no null check after `spdk_nvmf_poll_group_create`, so allocation failure would store a null pointer. There is no explicit Drop/destructor here; lifecycle likely depends on SPDK target shutdown elsewhere.

## Test Signals
Validate non-null poll group creation, association with the expected thread, pointer access, and cleanup through the target shutdown path.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/nvmf/poll_groups.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/nvmf/subsystem.rs -->
# sources/control-plane/mayastor/io-engine/src/subsys/nvmf/subsystem.rs

## Purpose
This file is the main wrapper around SPDK NVMf subsystems. It creates subsystem NQNs, namespaces, listeners, host access lists, lifecycle transitions, ANA state, event handling, and bdev/nexus/replica integration.

## Important APIs, Types, And Functions
`SubType` maps SPDK discovery/NVMe subsystem types. `NvmfSubsystem` wraps `NonNull<spdk_nvmf_subsystem>` and implements iteration. Constructors include `try_from_with`, `try_from`, `new`, and `new_with_uuid`. Namespace/lifecycle APIs include `add_namespace`, `start`, `stop`, `stop_for_destroy`, `pause`, `resume`, `shutdown_unsafe`, and `destroy_unsafe`. Host APIs include `allow_any`, `allowed_hosts`, `set_allowed_hosts`, `allow_host(s)`, `disallow_host(s)`, and `disconnect_host`. ANA/listener APIs include `set_ana_reporting`, `set_cntlid_range`, `get_ana_state`, `set_ana_state`, `uri_endpoints`, and listener internals. Event handling includes host connect/disconnect/KATO handlers and completion error callbacks for nexus and replicas. `NqnTarget` maps a subsystem namespace bdev to a nexus, lvol replica, or none.

## Control Flow
Sharing a bdev creates a subsystem using `NVME_NQN_PREFIX`, sets serial/model, disables ANA/allow-any by default, and adds namespace 1 with bdev UUID as NGUID and optional PTPL path. `start` adds a TCP listener, optionally RDMA if the target transport exists, then transitions the subsystem to started; on failure it destroys the subsystem. `change_state` wraps SPDK async state-change callbacks in oneshot channels and retries `EBUSY` up to three times with `mayastor_sleep`. Stop-for-destroy stops then removes namespace/destroys. Event callbacks generate host events, update nexus initiator tracking, set completion-error callbacks, and normalize NVMe completion retry-delay/status behavior.

## State, Persistence, And Dependencies
Runtime state is the SPDK subsystem object, namespace, listeners, allowed hosts, event callbacks, and controller callbacks. Persistent state can include PTPL reservation data when a namespace is added with a PTPL path. Dependencies include SPDK NVMf subsystem APIs, Mayastor target/config/transport modules, `Bdev`, `Nexus`, `Lvol`, eventing APIs, ffi helpers, `mayastor_sleep`, and constants for model ID/NQN prefix.

## Integration Points
Replica and nexus share paths call these constructors and lifecycle methods. Host connection events feed eventing and nexus initiator state. Admin command handling depends on namespace/bdev layout. ANA and listener endpoints are exposed to control-plane sharing status. `NVMF_TGT` provides target lookup and RDMA transport checks.

## Risks
Several methods are unsafe because SPDK requires the subsystem to be paused or stopped before namespace removal/destruction. `stop_for_destroy` deliberately avoids SPDK `stop_for_destroy` because it is marked unsafe for current operation queuing, so destruction uses a stop-then-destroy path. `set_allowed_hosts` only disconnects previously registered hosts, not arbitrary connected hosts. ANA reporting is gated by the `NEXUS_NVMF_ANA_ENABLE` environment variable even if callers pass `enable=true`. Listener addition always uses the replica port today. Raw C string conversion rejects embedded NULs.

## Test Signals
Tests should cover NQN and serial generation, duplicate/max-subsystem creation failures, namespace add/remove, start failure cleanup, busy retries in `change_state`, allowed-host add/remove/disconnect behavior, TCP and RDMA listener endpoint reporting, ANA enable/env gating and state changes, event callback effects on nexus initiators, completion error status rewriting, and safe teardown sequencing.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/nvmf/subsystem.rs -->
