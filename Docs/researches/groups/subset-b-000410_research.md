# subset-b-000410 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev.rs

Purpose: defines the core `Nexus` block device: a mirrored, SPDK-backed virtual bdev that fronts one or more child block devices and can be shared over NBD or NVMe-oF. It owns nexus identity, requested size, child list, state machine, NVMe reservation parameters, event sink, persistent nexus info, rebuild history, and the I/O pause subsystem.

Important APIs/types/functions: `Nexus`, `NexusTarget`, `NexusOperation`, `NexusStatus`, `NexusState`, `NvmeAnaState`, `NvmeReservation`, `NexusNvmeParams`, `nexus_create`, `nexus_create_v2`, and `nexus_create_internal`. Core methods include `new`, `setup_nexus_bdev`, `register_instance`, `destroy_ext`, `resize`, `pause`, `resume`, `shutdown`, `status`, `check_nexus_operation`, `reconfigure`, ANA getters/setters, and the `BdevOps`/`IoDevice` implementations.

Control flow: creation validates NVMe controller and reservation parameters, checks for duplicate name/UUID, constructs an SPDK bdev under `NexusModule`, adds child devices, computes geometry from children, registers an I/O device and bdev, opens children, acquires reservations, persists creation, and moves from `Init` to `Open`. I/O entry goes through `BdevOps::submit_request`, wraps SPDK `BdevIo` as `NexusBio`, and delegates to the I/O module. Destruction unshares, cancels rebuild jobs, closes children, persists shutdown, removes PTPL data when not SIGTERM, and unregisters the bdev. Shutdown pauses I/O, cancels rebuilds, closes children, persists shutdown, and records state transition events.

State and persistence: `NexusState` is mutex-protected while fast flags such as `shutdown_requested` use atomics. `req_size`, `data_ent_offset`, bdev block length/count, and required alignment are derived from child geometry. `nexus_info` is updated through `persist(PersistOp::Create/Shutdown/...)`; creation is persisted before exposing the open nexus through listing semantics. Eventing records init, delete, state changes, subsystem pause/resume, and reconfiguring transitions. Rebuild history is in-memory per nexus.

Dependencies/integration: integrates with SPDK bdev module APIs from `spdk_rs`, Mayastor `Bdev`, `Share`, `Reactors`, `NvmfSubsystem`, partition geometry helpers, persistent nexus info, PTPL operations, child management, rebuild logic, eventing metadata, and the nexus I/O subsystem. The `BdevStater` implementation delegates statistics to the underlying bdev wrapper.

Risks: much of the object uses pinned self references and explicit unsafe lifetime extension (`unpin_mut`, `pinned_mut`, `unsafe_from_untyped_bdev`), so aliasing mistakes would be severe. `nexus_create_internal` returns `Ok(())` for an already existing matching nexus without validating child topology. `destruct` uses `Reactor::block_on` on outstanding children as a last-resort cleanup path. Pause/resume must run on the master/first core; callers outside that contract can panic. Failed persistence during create/add paths must leave no leaked open child or registered bdev.

Test signals: create with matching/mixed block sizes, too-small children, duplicate UUID/name, invalid NVMe reservation/controller ranges, persistence create/shutdown failures, resize success and rollback, unshare/destroy ordering, shutdown idempotency and concurrent shutdown rejection, ANA state for NVMf and non-NVMf shares, and SPDK bdev I/O type support across child capabilities.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_children.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_children.rs

Purpose: implements parent-side operations for adding, opening, removing, faulting, onlining, retiring, detaching, and resetting nexus children. It is the dynamic reconfiguration layer that keeps the child vector, SPDK I/O channels, persistent child health, and rebuild jobs consistent.

Important APIs/types/functions: `new_child`, `add_child`, `remove_child`, `fault_child`, `online_child`, `try_open_children`, `close_children`, `min_num_blocks`, child lookup helpers, `DeviceEventListener` for `Nexus`, `retire_child_device`, `detach_device`, `disconnect_all_detached_devices`, `set_nexus_io_mode`, `try_self_shutdown`, and `reset_all_children`.

Control flow: initial creation uses `new_child` only in `Init`, creating a device from a URI and pushing a `NexusChild`. Runtime add validates nexus operation state, creates the device, checks block size/count against the nexus, opens it as out-of-sync, acquires reservations, registers event listening, persists `AddChild`, and optionally starts rebuild. Removal protects against deleting the only child or last healthy child, pauses rebuild jobs and frontend I/O, persists `RemoveChild`, detaches channel handles, closes the child, removes it from the vector, then resumes I/O and rebuilds. Faulting stops related rebuilds, marks the child faulted, starts an optional I/O log, schedules retirement, and resumes rebuilds.

State and persistence: child membership is in the `children` vector; channel state is changed by traversing all `NexusChannel` instances. Retire persistence uses `PersistOp::UpdateCond` and deliberately does not persist loss of the last healthy replica, so control plane can reconstruct from the latest data holder. Device retire is two-phase: detach handles from I/O paths, then disconnect/drop after pause. Reset state transitions use `Reconfiguring` and then `Open`.

Dependencies/integration: relies on `device_create`, `device_destroy`, `device_lookup`, `device_cmd_queue`, `NexusChild`, `NexusChannel`, `NexusIoSubsystem`, rebuild pause guards, persistent nexus ops, `Reactors::master`, `NvmfSubsystem::reset_controller`, and SPDK channel traversal. Device events drive hot-remove, loopback removal, NVMe admin failure, and controller failure handling.

Risks: many routines depend on strict ordering: persist before disconnecting a failed child, pause before final handle drop, and resume rebuilds through `RebuildPauseGuard`. `remove_child` returns `Ok(())` if pause fails after logging, which can hide a failed remove from callers. Unsafe mutable child access is used by `online_child` to operate on child and nexus in one scope. If device events arrive during close/destroy, the remove-channel handshake must avoid leaving descriptors around.

Test signals: add/remove/fault/online with healthy, out-of-sync, faulted, and destroying children; last-child and last-healthy-child rejection; persistence failure rollback for add/remove/retire; hot remove while open vs intentional destroy; controller failure during pause; reset of only NVMe children; I/O channel detach/disconnect races; rebuild cancellation and restart around remove/fault.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_children.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_error.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_error.rs

Purpose: centralizes nexus operation errors and maps them to gRPC `tonic::Status` and Unix errno values. It gives higher layers stable failure categories for create, share, child, rebuild, snapshot, resize, and persistence operations.

Important APIs/types/functions: `Error` with SNAFU contexts under `nexus_err`, `impl From<NvmfError> for Error`, `impl From<Error> for tonic::Status`, and `impl ToErrno for Error`.

Control flow: nexus and child modules construct typed variants with contextual fields. Conversion to `tonic::Status` first computes errno, then selects a gRPC status class such as `invalid_argument`, `failed_precondition`, `not_found`, `already_exists`, `out_of_range`, `data_loss`, or `internal`, and stores errno in response metadata. `ToErrno` delegates to nested `CoreError`, `BdevError`, `ChildError`, or direct `Errno` where available, and uses fixed errno for semantic nexus failures.

State and persistence: this file has no mutable state or persistence, but it influences persistent workflows by classifying `SaveStateFailed` as `data_loss` and `ENODATA`, and by deciding whether retrying callers see precondition, not-found, or internal failures.

Dependencies/integration: depends on `ChildError`, `NbdError`, `BdevError`, `CoreError`, `RebuildError`, `StoreError`, `NvmfError`, SNAFU, tonic, and Mayastor's `ToErrno`/`VerboseError`. All nexus RPC surfaces use these conversions directly or indirectly.

Risks: mappings are policy, so incorrect status classes can change control-plane retry behavior. Some errors with potentially recoverable causes map to `internal`, while `CreateRebuild` maps to `already_exists` regardless of underlying rebuild error. `FailedCreateSnapshot` maps to `internal` even for user/topology validation failures. The errno metadata insertion assumes conversion to metadata value from `i32` remains accepted.

Test signals: unit-test each major variant's gRPC code and errno, nested errno propagation for share/open/close/update errors, metadata presence, snapshot validation mapping, reservation and geometry invalid-argument cases, and backwards compatibility for clients expecting specific status codes.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_error.rs -->

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

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_snapshot.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_snapshot.rs

Purpose: coordinates crash-consistent snapshot requests across nexus replicas. It validates requested replica topology, pauses frontend I/O, schedules per-replica snapshot commands, gathers status per replica, and resumes I/O.

Important APIs/types/functions: `NexusReplicaSnapshotDescriptor`, `NexusReplicaSnapshotStatus`, `NexusSnapshotStatus`, `ReplicaSnapshotExecutor`, `SnapshotExecutorReplicaCtx`, `ReplicaSnapshotExecutor::new`, `take_snapshot`, `Nexus::check_nexus_state`, `do_nexus_snapshot`, and `create_snapshot`.

Control flow: public `create_snapshot` requires a snapshot name, verifies nexus operations are allowed, requires non-empty children and `NexusState::Open`, pauses the I/O subsystem, builds a `ReplicaSnapshotExecutor`, runs per-replica snapshots in parallel through `join_all`, resumes I/O, and returns per-replica errno statuses plus skipped replica UUIDs. Each snapshot task is spawned on the primary reactor, relooks up the nexus and child by replica UUID, gets a nonblocking I/O handle, and calls `handle.create_snapshot`.

State and persistence: this file does not persist snapshot state itself; it sends snapshot parameters to child block device handles. It records a parsed snapshot timestamp in the returned status. The frontend pause freezes new I/O while snapshots are issued so participating healthy replicas see a consistent point.

Dependencies/integration: depends on child UUID extraction, `NexusChild` health, `SnapshotParams`, `ISnapshotDescriptor`, reactor scheduling, `CoreError::to_errno`, `nexus_lookup`, and the nexus pause/resume implementation. It assumes child devices implement `create_snapshot` on their I/O handles.

Risks: topology validation requires the replica descriptor count to equal nexus child count, even if some are skipped. `create_time` parsing uses `unwrap_or_default`, so invalid timestamps silently become default. Resume errors are logged but the snapshot result is still returned, potentially leaving initiators unable to access the nexus. Per-replica failures are encoded as status integers rather than failing the whole snapshot after dispatch.

Test signals: missing snapshot name, non-open or empty nexus, descriptor count mismatch, duplicate replica UUID, unknown replica UUID, skipped replica handling, unhealthy participating replica rejection, child handle failure mapped to errno, partial replica failures in result vector, pause failure aborting operation, and resume failure logging.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_bdev_snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_channel.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_channel.rs

Purpose: defines per-core nexus I/O channel state: child handles used as readers and writers, detached handles awaiting disconnection, partial-rebuild I/O log channels, read round-robin cursor, frozen I/O queue, and channel-level I/O mode.

Important APIs/types/functions: `NexusChannel`, `IoMode`, `DrEvent`, `new`, `destroy`, `for_each_writer`, `for_each_io_log`, `select_reader`, `detach_device`, `disconnect_detached_devices`, `reconnect_all`, `connect_children`, `reconnect_io_logs`, `fault_device`, `set_io_mode`, `is_frozen`, `resubmit_frozen`, `abort_frozen`, and `freeze_io_submission`.

Control flow: channel creation decides whether the current SPDK thread should host normal frontend I/O handles or act as an auxiliary channel, initializes I/O log channels, then connects healthy children. `connect_children` opens two handles for each healthy child, one writer and one reader, and adds rebuilding out-of-sync children as write-only if at least one reader exists. Dynamic reconfiguration clears/rebuilds handle vectors and refreshes I/O logs. Faulting a device delegates to nexus retire logic, then reconnects logs.

State and persistence: state is per-core and non-persistent. Detached handles remain alive until `disconnect_detached_devices` drops them, allowing two-phase retire. Frozen `NexusBio` objects are queued in memory while `IoMode::Freeze` is active and resubmitted or failed later. `previous_reader` is an `UnsafeCell<usize>` because reader selection mutates through `&self` in the I/O path.

Dependencies/integration: depends on `BlockDeviceHandle`, `NexusChild` state predicates, `Nexus::io_log_channels`, SPDK thread identity, runtime flags `ENABLE_IO_ALL_THRD_NX_CHAN` and `ENABLE_NEXUS_CHANNEL_DEBUG`, and `NexusBio` for frozen I/O resubmission.

Risks: reader/writer handles are duplicated by calling `get_io_handle` twice per healthy child; failure of either faults the child. If no readers exist, rebuilding children are not added as write-only. The read cursor uses unsafe interior mutability and must remain single-threaded per SPDK channel. Frozen I/Os consume memory until resume or abort. Detach/disconnect ordering is critical to avoid I/O races and dangling handles.

Test signals: channel creation on primary vs I/O threads, healthy child reader/writer connection, rebuilding child write-only behavior, read round-robin selection, detach then disconnect with predicates, reconnect after child state changes, freeze/resubmit/abort semantics, debug dump safety with missing device names, and fault path reconnecting I/O logs.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_channel.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_child.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_child.rs

Purpose: defines the `NexusChild` object and its lifecycle, health, sync, reservation, close/unplug, rebuild, and I/O-log behavior. It wraps a child URI, block device, descriptor, state atomics, event listener attachment, and rebuild metadata for one replica under a nexus.

Important APIs/types/functions: `ChildError`, `FaultReason`, `ChildState`, `ChildStateClient`, `ChildSyncState`, `ChildDestroyState`, `NexusChild`, `open`, `online`, `close`, `unplug`, `hot_removed`, `reservation_acquire`, `reservation_acquire_argkey`, `reservation_preempt_holder`, `resv_check_holder`, `get_io_handle`, `get_io_handle_nonblock`, `start_io_log`, `stop_io_log`, `io_log_channel`, `rebuild_job`, and `get_rebuild_progress`.

Control flow: `open` rejects destroying or permanently faulted children, validates parent size against child size, opens the block device for write access, stores a descriptor, sets state `Open`, and records sync state. `online` recreates the underlying block device for recoverable closed/faulted children, then opens it out-of-sync for rebuild. `close` transitions destroy state, unclaims the descriptor, destroys the device, waits for removal/unplug notification when needed, and clears destroy state. `unplug` responds to device removal by dropping device/descriptor only for intentional destroy, closing open state, reconfiguring the parent unless the child already faulted for I/O error, and notifying `close`.

State and persistence: child state, sync state, and destroy state are `AtomicCell`s; fault timestamp is mutex-protected. Persistent-store enabled mode requires child URI UUIDs and panics if missing. NVMe reservation behavior depends on environment and `NexusNvmeParams`; PTPL behavior uses the global environment. I/O logs are optional per child and converted into rebuild maps when stopped.

Dependencies/integration: depends on Mayastor block-device traits, device create/destroy/lookup, SNAFU/CoreError errno mapping, URL parsing for replica UUIDs, persistent store availability, rebuild job registry, SPDK NVMe reservation structures/actions, DMA buffers, eventing, and `nexus_lookup_mut` for unplug reconfiguration.

Risks: `Url::parse(uri).expect` in UUID extraction can panic on invalid child URI. Persistent-store UUID enforcement also panics. Reservation report parsing uses `align_to` and assumes returned buffer layout is compatible. Close waits on a bounded channel with retry sleeps; unusual event ordering can leave descriptors longer than intended. State transitions mix atomic stores and event generation without a single global lock.

Test signals: state/client-state transitions, recoverable vs permanent faults, open too-small child, device open failure, online recreation failure, close idempotency, hot remove vs intentional destroy, unplug descriptor dropping, UUID extraction and invalid URIs, NVMe reservation unsupported path, reservation holder/preempt cases, PTPL flag behavior, I/O log lifecycle, and rebuild progress lookup.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_child.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io.rs

Purpose: implements the fast-path nexus I/O submission and completion logic. It translates a parent SPDK bdev I/O into one child read or fan-out write-like operations, handles retries and resubmission, faults failed children, logs writes for partial rebuild, and completes the parent I/O.

Important APIs/types/functions: `NioCtx`, `NexusBio`, `NexusBio::new`, `submit_request`, `child_completion`, `complete`, `readv`, `do_readv`, `submit_all`, `submit_write`, `submit_unmap`, `submit_write_zeroes`, `submit_reset`, `submit_flush`, `resubmit`, `fail`, `fail_nvme_status`, `completion_error`, `fault_device`, `log_io`, and fault-injection helpers under feature flags.

Control flow: `submit_request` freezes the I/O if the channel is frozen, otherwise dispatches by `IoType`. Reads select one reader and retry other readers if submission fails. Writes, unmaps, write-zeroes, resets, and flushes submit to every writer and log write-like ranges to active I/O logs. Each child completion updates `in_flight`, success/failure counters, and on last completion either completes success, resubmits when some children succeeded, or fails the parent if all failed.

State and persistence: per-I/O state lives in SPDK driver context `NioCtx` and is sized by the nexus module. Nexus-wide `last_error` records the final child error when all children fail and affects parent failure status. No disk persistence occurs, but completion errors can schedule child retirement, which later updates persistent nexus info. Effective offsets add the nexus data partition offset before child submission.

Dependencies/integration: uses `NexusChannel` for reader/writer/log selection, block-device handle APIs, SPDK NVMe completion status helpers, Mayastor `IoCompletionStatus`, `IoStatus`, `CoreError`, `NvmeStatus`, `LvolFailure`, and optional `fault-injection`/`nexus-io-tracing` features.

Risks: submission errors fault devices broadly, with TODOs noting ENOMEM and ENXIO should be distinguished. Parent I/O resubmission after partial child failure can repeat writes on children that already succeeded, so child idempotence and upper-layer semantics matter. Reservation conflict triggers self-shutdown rather than child retire. Invalid opcode is ignored for retire. Frozen I/O stores cloned `NexusBio` until resume/abort.

Test signals: read selection and retry exhaustion, write fan-out partial submission failure, all-completion success/fail/resubmit paths, ENOSPC mapping to capacity exceeded, reservation conflict self-shutdown, invalid opcode no-retire behavior, write logging when I/O log exists, frozen submission and abort, data partition offset correctness, and fault-injection submission/completion paths.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io_log.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io_log.rs

Purpose: provides per-core write-range logging for partial rebuild. When a synced child faults, the nexus can track write/unmap/write-zero ranges that occur while the child is absent and later rebuild only modified segments.

Important APIs/types/functions: `IOLogChannelInner`, `IOLogChannel`, `IOLog`, `IOLog::new`, `current_channel`, `IOLogChannelInner::log_io`, `take_segments`, and `IOLog::finalize`.

Control flow: `IOLog::new` creates one `IOLogChannel` per SPDK core, each with its own `SegmentMap`. Active nexus channels hold the current core's `IOLogChannel` and call `log_io` for write-like operations. `finalize` consumes all channel segment maps, merges them, and returns a `RebuildMap` for the target device.

State and persistence: log state is in-memory only. Each channel owns an `UnsafeCell<Option<SegmentMap>>`; `take_segments` consumes it so later access panics. The merged `RebuildMap` becomes input to rebuild logic, not a persisted artifact here.

Dependencies/integration: depends on core `SegmentMap`, rebuild `RebuildMap` and `SEGMENT_SIZE`, SPDK core enumeration/current core, parking-lot mutex, and nexus channel write logging. It is started/stopped from `NexusChild`.

Risks: `log_io` asserts the caller is on the channel's core, so cross-core misuse panics. The `UnsafeCell` design is lockless but relies on SPDK single-thread-per-channel discipline. Debug formatting unwraps the first channel and assumes at least one core. Access after `finalize` panics. Segment size and block-length conversions must match rebuild expectations.

Test signals: per-core channel creation, write/write-zero/unmap marking, read/flush/reset not marking, merge of multiple core maps, access-after-finalize panic expectations, current-core lookup, empty/invalid device creation assertions, and rebuild map ranges matching logged LBNs.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io_log.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io_subsystem.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io_subsystem.rs

Purpose: serializes pause and resume operations for the frontend nexus subsystem, mainly NVMe-oF, while supporting nested/concurrent pause requests and a frozen state for faulted nexus behavior.

Important APIs/types/functions: `NexusPauseState`, `NexusIoSubsystem`, `new`, `pause_state`, `suspend`, and `resume`.

Control flow: `suspend` must run on the first core, transitions `Unpaused -> Pausing`, increments the pause counter from zero, pauses the NVMf subsystem if shared, stores `Paused`, and wakes one waiter. If already `Paused` or `Frozen`, it increments the pause counter. If another transition is active, it queues a oneshot waiter and retries. `resume` decrements the pause counter; only the final resume either leaves state `Frozen` when requested/frozen or resumes the NVMf subsystem and stores `Unpaused`.

State and persistence: pause state is an `AtomicCell<NexusPauseState>`, pause count is `AtomicU32`, and waiters are in-memory oneshot senders. There is no persistent state. `Frozen` intentionally keeps the subsystem paused even after the pause count reaches zero.

Dependencies/integration: owns a mutable reference to the nexus `Bdev`, checks share protocol through `Share`, looks up `NvmfSubsystem` by name, uses core identity assertions, and is called by nexus shutdown, snapshot, child retire, remove, and resume flows.

Risks: wrong-core calls panic. Unexpected pause/resume errors can panic except for selected `EPERM`/`ECANCELED` cases. Waiter ordering wakes only one waiter per transition, so correctness relies on each resumed waiter retrying and waking the next. Frozen state blocks later nexus operations through `check_nexus_operation`.

Test signals: nested pause/resume counts, concurrent pause while unpausing, concurrent resume while pausing, freeze-on-fault behavior, NVMf shared vs unshared nexus, tolerated subsystem pause/resume errors, wrong-core assertions, waiter wake chaining, and operation rejection while frozen.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io_subsystem.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_iter.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_iter.rs

Purpose: provides iterators and lookup helpers over all registered nexus bdevs in the SPDK `NexusModule`.

Important APIs/types/functions: `nexus_iter`, `nexus_iter_mut`, `nexus_lookup`, `nexus_lookup_mut`, `nexus_lookup_name_uuid`, `nexus_lookup_uuid_mut`, `nexus_lookup_nqn`, `nexus_lookup_nqn_mut`, `NexusIter`, and `NexusIterMut`.

Control flow: immutable and mutable iterators wrap `BdevModuleIter<Nexus>`. Lookup helpers create a fresh iterator and find by nexus name, UUID, name-or-UUID, or a name parsed from NQN text. Mutable iteration returns pinned mutable nexus references from bdev data.

State and persistence: no state is stored here. The live SPDK bdev module registry is the source of truth. NQN lookup parses the substring after the first colon as a nexus name.

Dependencies/integration: depends on `NexusModule::current`, `spdk_rs::BdevModuleIter`, and the `Nexus` bdev data type. It is used throughout nexus creation, rebuild callbacks, snapshot tasks, child event handlers, and self-shutdown paths.

Risks: `NexusModule::current()` panics if the module is not registered. NQN parsing is simplistic and may mis-handle NQNs with unexpected colon structure. Mutable lookups expose pinned mutable references, so callers must respect reactor/thread ownership and avoid aliasing with other references.

Test signals: lookup by name, UUID, name-or-UUID collision behavior, mutable lookup state mutation, NQN parsing for expected and malformed NQNs, empty module iteration, and behavior before module registration.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_iter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_module.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_module.rs

Purpose: registers the SPDK bdev module that owns nexus bdev instances, provides module lifecycle callbacks, declares per-I/O context size, and emits JSON configuration for existing nexus devices.

Important APIs/types/functions: `NEXUS_MODULE_NAME`, `NexusModule`, `NexusModule::current`, `current_opt`, `WithModuleInit::module_init`, `WithModuleFini::module_fini`, `WithModuleGetCtxSize::ctx_size`, `WithModuleConfigJson::config_json`, `BdevModuleBuild`, and `register_module`.

Control flow: `register_module` builds and registers a module named `NEXUS_CAS_MODULE` with init/fini/context-size/config-json callbacks. `ctx_size` returns `size_of::<NioCtx>()` so SPDK allocates enough driver context for every nexus bdev I/O. `config_json` iterates current nexus bdevs and writes `create_nexus` JSON RPC entries with name, bdev UUID, child URIs, and requested size.

State and persistence: no runtime state is stored in this type. The generated config JSON can be used as external configuration persistence, but persistent nexus info is handled elsewhere.

Dependencies/integration: depends on `spdk_rs` bdev module traits, `NioCtx` from the I/O module, `nexus_iter`, and `serde_json`. `Nexus::new` uses `NexusModule::current().bdev_builder()`.

Risks: `current` panics when called before registration. Config JSON uses the bdev UUID, not necessarily the separate nexus UUID used by v2 creation. The config only includes basic create parameters and omits NVMe reservation parameters and persistence keys, so it may not fully reconstruct advanced nexus state.

Test signals: module registration before nexus creation, context size matching `NioCtx`, config JSON for zero and multiple nexuses, UUID field expectations for v1/v2 nexus names, and `current_opt` before/after registration.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_module.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_nbd.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_nbd.rs

Purpose: wraps SPDK NBD export support for nexus or other bdevs. It finds free `/dev/nbd*` devices, starts SPDK NBD, waits for kernel readiness, and disconnects NBD devices during cleanup.

Important APIs/types/functions: `NbdError`, `wait_until_ready`, `find_unused`, `start_cb`, `start`, `NbdDisk`, `NbdDisk::create`, `destroy`, `get_path`, and `as_uri`.

Control flow: `find_unused` reads the kernel NBD module `nbds_max`, scans `/sys/class/block/nbd*/pid` to skip in-use devices, and also asks SPDK whether a path is already in use. `start` calls `spdk_nbd_start` and waits on a oneshot callback. `NbdDisk::create` finds a path, starts SPDK NBD, then polls from an unaffinitized helper thread until the block device reports nonzero size or the retry loop gives up. `destroy` sets kernel NBD size to zero and calls `nbd_disconnect` from a helper thread while the reactor polls.

State and persistence: `NbdDisk` owns a raw `spdk_nbd_disk` pointer. No persistent configuration is written. Temporary readiness and destroy completion are coordinated with atomics and helper threads. The exported URI is `file:///dev/nbdX`.

Dependencies/integration: depends on SPDK NBD FFI, Linux NBD ioctls, sysfs parsing, Mayastor reactors and `Mthread`, oneshot channels, `ffihelper` errno conversion, and Unix file descriptors. `NexusTarget::NbdDisk` stores this wrapper when a nexus is shared over NBD.

Risks: Linux-specific sysfs/ioctl behavior and NBD kernel module availability are assumed. Several paths unwrap file opens and ioctl results inside helper threads, so device disappearance can panic. Readiness polling passes a pointer to an immutable zero `size` variable to ioctl, relying on kernel writes through const-looking Rust binding. Destroy uses raw pointer cast through `usize` to cross threads. NBD is described as mostly for testing, so production hardening is limited.

Test signals: missing NBD module, all devices busy, SPDK already using a candidate path, successful start callback, readiness timeout path, destroy while device path disappears, ioctl failure behavior, URI formatting, and repeated create/destroy without stale `/sys/class/block/nbd*/pid` state.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_nbd.rs -->
