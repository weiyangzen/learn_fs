# subset-b-000411 Research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_persistence.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_persistence.rs

### Purpose
`nexus_persistence.rs` persists nexus restart-safety metadata into `PersistentStore`, primarily child health, clean shutdown, and a control-plane-requested self-shutdown bit. It protects nexus consistency by freezing I/O resubmissions while durable state is being changed and by self-shutting down when persistence cannot be trusted.

### Important APIs, Types, And Functions
`PersistentNexusInfo` wraps the stored `NexusInfo` plus an optional externally supplied store key. `NexusInfo` is the serialized state: `clean_shutdown`, `do_self_shutdown`, and `children`. `ChildInfo` records child UUID and health. `PersistOp` drives mutations: create, add/remove child, update child health, conditional update, and shutdown. `Nexus::persist()` is the main API, with `save()` and `save_txn()` performing retrying store writes and compare-and-set transactions.

### Control Flow
`persist()` exits early when persistence is disabled, which supports tests without a configured store. Otherwise it locks `nexus_info`, freezes nexus I/O mode, mutates the in-memory `NexusInfo` according to the requested operation, and writes the result to the store. `Create` rebuilds children from current nexus children and rejects a single unhealthy child. `UpdateCond` first evaluates its predicate under the nexus info lock, clones the expected state, applies the mutation, and calls `save_txn()`; a compare failure updates `do_self_shutdown` from the current store value and returns an error that triggers self-shutdown. Non-transactional writes call `save()` and retry with one-second sleeps until retry count expires.

### State, Persistence, And Dependencies
The durable JSON value is written via `PersistentStore::put()` or `txn_create_execute()` under either the supplied key or the nexus UUID. In-memory mutation is protected by the async `nexus_info` lock; I/O is frozen during persistence to avoid resubmission storms while etcd is slow or unavailable. Dependencies include `NexusChild::uuid()`, `IoMode`, serde JSON conversion, etcd client errors, `StoreError`, and `mayastor_sleep`.

### Integration Points
This file is used by nexus create/destroy and child state transitions. The conditional transaction is designed for control-plane republish races where another nexus may have picked up a replica while this nexus is marking it unhealthy. `try_self_shutdown()` is the enforcement path when persistence cannot be completed safely.

### Risks
The code uses `expect()` and `unwrap()` when parsing child UUIDs or current transaction values, so malformed internal state or unexpected store data can panic. I/O is restored to normal on most returns, but any added early return in the locked/frozen region must preserve that invariant. Transaction failure intentionally shuts the nexus down, so false compare failures from encoding drift would be disruptive. PersistentStore retry count underflow would be risky if configured as zero.

### Test Signals
Useful coverage includes disabled-store create/update, create with single unhealthy child, add-child replacement by UUID, remove-child idempotency, update-only changed child, conditional predicate false restoring normal I/O, transaction compare failure setting `do_self_shutdown`, retry exhaustion, shutdown write failure not self-shutting down, and store-key versus UUID-key selection.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_persistence.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_share.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_share.rs

### Purpose
`nexus_share.rs` adapts nexus devices to the generic `Share` API and manages nexus-specific sharing state. It handles NVMf exports with ANA, allowed hosts, controller-id ranges, and PTPL metadata, and preserves legacy NBD sharing for tests that request `Protocol::Off`.

### Important APIs, Types, And Functions
The `Share for Nexus` implementation forwards NVMf share/unshare/property operations to the pinned inner bdev and exposes `shared()`, `share_uri()`, `allowed_hosts()`, and URI accessors. `Nexus::share()`, `share_ext()`, `unshare_nexus()`, `get_share_uri()`, and `ptpl()` manage the higher-level nexus target enum. `NexusPtpl` implements `PtplFileOps` for nexus reservation persistence files under `nexus/<uuid>.json`.

### Control Flow
`share_nvmf()` is idempotent: if unshared it calls the bdev NVMf share path and returns the resulting URI; if already NVMf shared it returns the existing URI. `share_ext()` first checks `nexus_target`; same-protocol requests update allowed hosts and return the current URI, while different protocols fail with `AlreadyShared`. `Protocol::Nvmf` builds `NvmfShareProps` with controller-id range, ANA, allowed hosts, and PTPL props, then records `NexusNvmfTarget`. `Protocol::Off` creates an `NbdDisk` and records that target. `unshare_nexus()` clears the target, destroys NBD if needed, and always asks the bdev to unshare.

### State, Persistence, And Dependencies
Sharing state is split between SPDK bdev share state and the Rust `nexus_target` field. PTPL persistence is file-based through `PtplFileOps`; `destroy()` removes the per-nexus JSON file if it exists. Dependencies include `core::Share`, `NvmfShareProps`, `UpdateProps`, `UnshareProps`, `PtplProps`, `NbdDisk`, and nexus error contexts from `snafu`.

### Integration Points
Control-plane publish/unpublish operations call this layer to expose nexus devices over NVMe-oF. Reservation persistence integrates with the target-share path through `create_ptpl()`. Allowed-host updates allow idempotent republish without unsharing the target.

### Risks
The implementation uses `unsafe` pin projection to mutate `nexus_target`, so structural changes to `Nexus` need care. `get_share_uri().unwrap()` is used after idempotent checks and assumes the underlying bdev state is coherent. Mapping `Protocol::Off` to NBD is legacy behavior and can surprise callers that interpret Off literally. PTPL file deletion errors surface as share failures when creating PTPL props.

### Test Signals
Tests should cover first NVMf share, repeated same-protocol share updating allowed hosts, different-protocol rejection, unshare from NVMf and NBD targets, unshare when `nexus_target` is `None`, PTPL subpath format and removal, `From<&NexusTarget> for Protocol`, and error propagation from bdev share/unshare/update calls.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_share.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/null_bdev.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/null_bdev.rs

### Purpose
`null_bdev.rs` implements the URI-backed SPDK null bdev adapter. It creates in-memory/discard devices for tests and benchmarks, with all writes discarded and read data undefined.

### Important APIs, Types, And Functions
`Null` stores name, alias URI, block count, block size, and optional UUID. `TryFrom<&Url>` parses `null:///name` URIs with `blk_size`, `size_mb`, `size`, `num_blocks`, and `uuid`. `GetName`, `Probe`, and `CreateDestroy` integrate it with the generic bdev URI API.

### Control Flow
URI parsing rejects empty paths, mutually exclusive size forms, invalid block sizes other than 512 or 4096, bad integers, bad byte-unit values, bad UUIDs, and unknown parameters. `create()` rejects existing bdev names, builds `null_bdev_opts`, calls `bdev_null_create()`, then looks up the bdev, optionally overwrites its UUID, and adds the original URI as an alias. `destroy()` looks up the bdev by name and calls `bdev_null_delete()` through a oneshot completion.

### State, Persistence, And Dependencies
State is not persisted; created devices live in SPDK until destroyed. The alias preserves the original URI for later matching. Dependencies include SPDK null bdev FFI, `UntypedBdev`, URI helpers, `reject_unknown_parameters`, byte-unit parsing, UUID parsing, and async callback helpers.

### Integration Points
This driver is selected by URI parsing and is useful for benchmarking the I/O stack without backing storage. It participates in generic `bdev_create`, `bdev_destroy`, and bdev alias matching.

### Risks
`create()` generates an SPDK UUID and then optionally overrides it with the requested UUID after creation, so failures between those steps leave a valid but differently identified bdev. The `num_blocks` parse error labels the parameter as `blk_size`, which can mislead users. A zero size and zero `num_blocks` is accepted and creates a zero-block null device.

### Test Signals
Cover size versus size_mb versus num_blocks parsing, block-size validation, UUID aliasing, unknown-parameter rejection, duplicate create, destroy missing bdev, callback cancellation, zero-size behavior, and alias-based URI lookup.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/null_bdev.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/null_ng.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/null_ng.rs

### Purpose
`null_ng.rs` is a newer SPDK Rust-module example for a null bdev. It demonstrates `spdk_rs` module, bdev, I/O device, channel, and poller abstractions rather than the older C null bdev FFI path.

### Important APIs, Types, And Functions
`NullIoPollerData` queues pending `BdevIo` objects behind a mutex. `NullIoChannelData` owns a poller that drains queued I/O every millisecond and completes each as success. `NullIoDevice` implements `IoDevice` and `BdevOps`. `NullBdevModule` implements module registration via `WithModuleInit` and `BdevModuleBuild`; `register()` registers the module named `NullNg`.

### Control Flow
`submit_request()` pushes read and write I/O into the channel poller queue and fails unsupported I/O. The poller drains all queued I/O and calls `ok()` on each completion. `destruct()` unregisters the I/O device. The example `create()` builder is present but not called by module init; `module_init()` currently returns success without creating a device.

### State, Persistence, And Dependencies
All state is runtime-only. Per-channel state tracks a poller and synthetic channel id; per-device state tracks a next channel id in a `RefCell`. Dependencies are `spdk_rs` traits and wrappers, `parking_lot::Mutex`, `RefCell`, and SPDK bdev module registration.

### Integration Points
The file registers a module but does not expose a URI adapter in this source. It is likely experimental or demonstrative infrastructure for future Rust-native bdev modules.

### Risks
`unsafe impl Send` is used because `BdevIo` contains `NonNull`; correctness relies on the poller/channel execution model. The builder sets required alignment to 12, which is unusual and should be validated if activated. The create log typo is harmless, but the inactive `create()` path means registering this module alone creates no usable device.

### Test Signals
Tests or examples should verify module registration, manual `NullIoDevice::create()`, read/write completion through the poller, unsupported I/O failure, channel create/destroy behavior, destruct unregistering the I/O device, and thread-safety assumptions around queued `BdevIo`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/null_ng.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvme.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nvme.rs

### Purpose
`nvme.rs` adapts local PCIe NVMe devices to the generic URI bdev create/destroy/probe API. It wraps SPDK `spdk_bdev_nvme_create()` for `pcie:///BDF`-style devices and validates host driver binding during probe.

### Important APIs, Types, And Functions
`NVMe` stores the PCI address-derived controller name and original URL. `TryFrom<&Url>` validates path segments. `GetName` returns the namespace bdev name by appending `n1`. `CreateDestroy` performs asynchronous SPDK creation and deletion. `Probe` checks `/sys` driver binding. `NvmeCreateContext` owns the transport id and namespace name output pointer array.

### Control Flow
`create()` rejects an existing controller name, fills default controller opts, builds a PCIe transport id with `traddr = name`, calls `spdk_bdev_nvme_create()`, waits for the create callback, then looks up `<name>n1` and adds the original URI alias. `destroy()` deletes the SPDK NVMe controller by base name if `<name>n1` exists and attempts to restore the alias if deletion fails. `probe()` accepts `vfio-pci` and `uio_pci_generic`, reports kernel-bound NVMe as `PciKernelBound`, and distinguishes unsupported PCI driver from non-NVMe PCI device.

### State, Persistence, And Dependencies
State is SPDK runtime controller/bdev state plus bdev alias metadata; nothing is persisted. Dependencies include sysfs, SPDK NVMe bdev FFI, `bdev_nvme_delete_async`, URI helpers, `UntypedBdev`, and callback conversion helpers.

### Integration Points
This is the legacy SPDK bdev path for local NVMe and is selected by URI parsing. Probe errors inform callers whether the device must be rebound to a userspace PCI driver before creation.

### Risks
The duplicate check uses the base controller name, while successful lookup uses `<name>n1`; naming mismatch can affect edge cases. The create callback ignores `bdev_count`, so a zero-namespace attach may fail later through the expect lookup rather than a structured error. Alias restoration on failed destroy is best effort.

### Test Signals
Test parsing empty paths, PCI transport id construction, sysfs probe outcomes for missing driver/kernel-bound/userspace-bound/unsupported driver, create callback errors, zero namespace behavior, alias addition failure logging, destroy missing bdev, and failed deletion alias restoration.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvme.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmf.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nvmf.rs

### Purpose
`nvmf.rs` implements the older SPDK bdev adapter for remote NVMe-oF targets. It parses `nvmf` URIs, connects using SPDK bdev NVMe create, attaches a single namespace, and adds the URI as a bdev alias.

### Important APIs, Types, And Functions
`Nvmf` holds controller name, alias, host, port, subsystem NQN, protection-check flags, and optional UUID. `TryFrom<&Url>` parses host/path/query. `GetName` returns `<controller>n1`. `CreateDestroy` wraps create/delete. `NvmeCreateContext` fills an NVMe TCP transport id and namespace output array.

### Control Flow
Parsing requires a host and exactly one path segment, supports `reftag`, `guard`, and `uuid`, defaults the port to 4420, and rejects unknown parameters. `create()` rejects existing namespace bdev names, constructs default controller opts and TCP transport id, calls `spdk_bdev_nvme_create()`, waits for bdev count, and deletes the partially created controller when count is zero. It then looks up `<name>n1`, checks but does not reject UUID mismatch, and adds the alias. `destroy()` deletes the NVMe controller by base name.

### State, Persistence, And Dependencies
All state is SPDK runtime state plus alias metadata. Protection-information flags are passed into the context but this file does not visibly apply `prchk_flags` to SPDK options, which is worth comparing with the newer `nvmx` path. Dependencies include SPDK NVMe bdev FFI, URI utilities, boolean/UUID parsing, `UntypedBdev`, and async callback helpers.

### Integration Points
This adapter supports generic bdev create/destroy for remote NVMe-oF targets and coexists with the newer `nvmx` implementation. Its `Probe` implementation is currently a no-op placeholder.

### Risks
UUID mismatch only logs an error and still returns success, so callers relying on UUID validation must enforce it elsewhere. `prchk_flags` in `NvmeCreateContext` appears unused. IPv6 bracket handling is absent here unlike the newer `nvmx::uri` path. The single-namespace assumption is hard-coded.

### Test Signals
Cover URI host/path validation, boolean query forms, unknown parameters, default port, UUID mismatch logging, zero namespace cleanup, create/delete callback cancellation, alias addition, and parity against `nvmx` for supported query parameters.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmf.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/channel.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/channel.rs

### Purpose
`nvmx/channel.rs` implements per-core NVMe I/O channel state for the Rust-native NVMe-oF block-device path. It owns I/O qpairs, SPDK poll groups, polling, channel reset/shutdown semantics, and per-channel I/O statistics.

### Important APIs, Types, And Functions
`NvmeIoChannel` is the SPDK channel context wrapper. `NvmeIoChannelInner` owns the optional `QPair`, `PollGroup`, `Poller`, stats controller, block device, controller reference, pending-I/O count, and shutdown flag. `IoStatsController` accumulates per-channel stats. `NvmeControllerIoChannel::create()` and `destroy()` are SPDK I/O channel callbacks. `nvme_poll()` processes poll-group completions and handles disconnected qpairs.

### Control Flow
Channel creation looks up the controller by ID, ensures it is `Running`, copies controller handle and namespace block size while holding the lock, releases the lock before qpair operations, looks up the block device, creates a qpair and poll group, adds the qpair, starts a poller, and stores a boxed `NvmeIoChannelInner` in the SPDK channel context. Reset drops the qpair and leaves the channel unusable until `reinitialize()` recreates and reconnects it. Shutdown performs reset, marks the channel one-way shutdown, and drops the controller reference. Destroy stops the poller, removes any qpair from the poll group, and frees the boxed inner state.

### State, Persistence, And Dependencies
State is runtime-only and bound to SPDK I/O channel lifetime. `num_pending_ios` is used by the submission layer for accounting and logging; byte counters are stored in block units until read out. Dependencies include `NVME_CONTROLLERS`, `QPair`, `PollGroup`, `BlockDevice`, `device_lookup`, SPDK poll group APIs, and configured poll intervals.

### Integration Points
Handles in `nvmx/handle.rs` obtain these channels via `spdk_get_io_channel`. Controller reset and shutdown traverse channels and call `reset()`, `reinitialize()`, or `shutdown()`. I/O stats aggregation in `controller.rs` reads each channel's `IoStatsController`.

### Risks
The code relies heavily on raw channel-context pointer arithmetic and boxed raw pointers. Qpair disconnect handling aborts queued requests but leaves shutdown commented out, so recovery depends on higher-level reset/failure detection. A failed `poll_group.add_qpair()` or qpair connect during reinitialize can leave resources partially created. Stats only account successful operations and ignore flush bytes.

### Test Signals
Exercise channel creation with missing, non-running, and running controllers; qpair/poll-group allocation failures; reset followed by reinitialize; reset racing shutdown; destroy with and without qpair; poll completion return values; disconnected qpair abort behavior; pending-I/O underflow warning; and stats aggregation by block size.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/channel.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/controller.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/controller.rs

### Purpose
`nvmx/controller.rs` is the core Rust-native NVMe controller implementation. It owns controller lifecycle, namespace discovery, admin queue polling, channel traversal for reset/shutdown, asynchronous event handling, listener notifications, and controller option/transport builders.

### Important APIs, Types, And Functions
`NvmeControllerInner` wraps the SPDK controller, adminq poller, namespace list, and SPDK I/O device. `NvmeController` stores name, id, protection flags, optional inner state, `ControllerStateMachine`, event dispatcher, and timeout config. Important methods include `new()`, `populate_namespaces()`, `reset()`, `shutdown()`, `hot_remove()`, `get_io_stats()`, `register_device_listener()`, `destroy_device()`, and `connected_attached_cb()`. The `options` module builds controller opts; `transport` builds and formats transport IDs.

### Control Flow
After `uri.rs` completes async attach, `connected_attached_cb()` transitions to `Initializing`, installs the SPDK controller into timeout config, assigns a pointer-derived ID, constructs `NvmeControllerInner`, configures timeouts, populates namespace 1, registers AER callbacks, inserts an ID alias into `NVME_CONTROLLERS`, transitions to `Running`, and wakes the waiter. Reset is allowed only from `Running` or `Faulted`, sets `ResetActive`, traverses channels to drop qpairs, then traverses again to recreate qpairs unless shutdown was observed. Shutdown transitions to `Unconfiguring`, marks destroy in progress, traverses channels to shut them down, fails the SPDK controller, clears namespaces, transitions to `Unconfigured`, and invokes the callback. `destroy_device()` runs shutdown, removes both name and id map entries, notifies listeners, then waits until the last `Arc` reference can be unwrapped so Drop can detach the SPDK controller.

### State, Persistence, And Dependencies
Controller state is in-memory and synchronized through `parking_lot::Mutex` and the global `NVME_CONTROLLERS` `RwLock`. Admin queue and I/O resources are SPDK runtime objects. Dependencies include `IoDevice`, `PollerBuilder`, `NvmxSubsystem`, `TimeoutConfig`, `ControllerStateMachine`, `NvmeNamespace`, `DeviceEventDispatcher`, and SPDK NVMe APIs for AER, detach, namespace lookup, and controller fail.

### Integration Points
This controller backs `NvmeBlockDevice`, `NvmeDeviceHandle`, and `NvmfDeviceTemplate`. Admin queue failures dispatch `AdminCommandCompletionFailed`, `AdminQNoticeCtrlFailed`, or `AdminQBroken` to registered listeners, enabling nexus fault/retire behavior. Namespace attribute-change AERs trigger namespace repopulation and removal notification.

### Risks
Correctness depends on strict state-machine transitions and `ResetActive` flag ownership. Drop asserts that controllers are `New` or `Unconfigured`; leaked references can delay destroy indefinitely. Controller ID is the SPDK pointer value and is also used as a global map key. `destroy_device()` loops until `Arc::try_unwrap()` succeeds, so listener/channel references must be released. Some shutdown reset comments indicate behavior is still under design. `connected_attached_cb()` sends attach failure if namespace population fails but leaves cleanup to the caller.

### Test Signals
High-value tests include attach success/failure, namespace absent transitioning to `Faulted`, AER namespace removal, reset from legal and illegal states, concurrent reset rejection, reset racing shutdown, shutdown channel failure, `destroy_device()` removing both keys and notifying listeners, adminq error event dispatch, option builder fields, IPv4/IPv6 transport ID builder, and Drop assertions through controlled lifecycle tests.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/controller.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/controller_inner.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/controller_inner.rs

### Purpose
`nvmx/controller_inner.rs` provides low-level controller wrappers and timeout handling for the Rust-native NVMe path. It translates configured timeout actions into abort, reset, hot-remove, or ignore behavior and wraps raw SPDK controller pointers.

### Important APIs, Types, And Functions
`DeviceTimeoutAction::try_from(u32)` maps SPDK config values plus hot-remove value `4`. `TimeoutConfig` holds atomically accessed timeout action, reset flags, SPDK controller wrapper, reset cooldown state, destroy/failure-report flags, and adminq-broken tracking. `SpdkNvmeController` wraps `NonNull<spdk_nvme_ctrlr>`. `DeviceIoController for NvmeController` exposes timeout action get/set. `NvmeController::configure_timeout()` registers SPDK timeout callbacks.

### Control Flow
Timeout callbacks call `io_timeout_handler()`, inspect the configured action and qpair, optionally escalate abort to reset, and either issue an abort command, reset the controller, hot-remove it, or ignore the timeout. `reset_controller()` is intended to serialize reset attempts, apply a cooldown after failures, and invoke `NvmeController::reset()` with `TimeoutConfig::reset_cb`. Admin queue polling uses `process_adminq()` and helper flags to report controller failure or adminq broken events only once. Hot-remove calls the controller hot-remove path, which fails the SPDK controller and resets channels.

### State, Persistence, And Dependencies
Timeout state is in-memory and uses `AtomicCell` for callback-path access without locking. The wrapped SPDK controller pointer is installed after attach. Dependencies include global `NVME_CONTROLLERS`, configured `nvme_bdev_opts`, SPDK timeout/admin/abort/fail APIs, `DeviceIoController`, and `DeviceTimeoutAction`.

### Integration Points
`controller.rs` owns allocation/drop of `TimeoutConfig` and passes its pointer to the adminq poller and SPDK timeout callback. `device.rs` lets users adjust timeout action through the block-device I/O controller.

### Risks
`reset_controller()` returns immediately when `compare_exchange(false, true).is_ok()`, which appears inverted for initiating an exclusive reset and may prevent resets from starting when the flag was successfully acquired. Raw pointer lifetime is critical because SPDK callbacks hold `TimeoutConfig` pointers. `SpdkNvmeController` exposes deref to mutable SPDK internals and is marked copyable, so use-after-detach must be prevented by lifecycle state.

### Test Signals
Cover timeout-action parsing, configure with zero timeout, abort success and abort failure escalation, reset cooldown, concurrent timeout callbacks, hot-remove path, adminq broken timeout threshold, one-shot failure reporting, `SpdkNvmeController` null handling, and the reset flag compare-exchange behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/controller_inner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/controller_state.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/controller_state.rs

### Purpose
`controller_state.rs` defines the NVMe controller lifecycle state machine and an exclusive flag mechanism used for reset serialization.

### Important APIs, Types, And Functions
`NvmeControllerState` has `New`, `Initializing`, `Running`, `Faulted(reason)`, `Unconfiguring`, and `Unconfigured`. `ControllerFailureReason` distinguishes reset, shutdown, and namespace initialization failures. `ControllerFlag` currently contains `ResetActive`. `ControllerStateMachine` exposes `transition()`, `transition_checked()`, `current_state()`, `set_flag_exclusively()`, and `clear_flag_exclusively()`.

### Control Flow
`check_transition()` enforces allowed state changes: new to initializing, initializing to running or faulted, running to unconfiguring or faulted, unconfiguring to unconfigured or faulted, faulted to running/unconfiguring/faulted, and no transitions out of unconfigured. Flag updates use atomic compare-exchange against the single stored boolean.

### State, Persistence, And Dependencies
State is in-memory only. The state machine stores a controller name for logs, the current enum value, and one atomic flag. Dependencies are `crossbeam::atomic::AtomicCell`, `snafu`, and `strum` display derivation.

### Integration Points
`controller.rs` uses state transitions to gate attach, namespace faulting, reset, shutdown, and drop safety. Reset code uses `ResetActive` to reject concurrent resets and assert that the reset owner clears the flag.

### Risks
Only one boolean flag is implemented, so adding more `ControllerFlag` values without changing `lookup_flag()` would alias them. `transition_checked()` reports the expected state as `current_state` in its error rather than the actual current state, which can make diagnostics confusing. Recovering from `Faulted` directly to `Running` is allowed and should remain deliberate.

### Test Signals
Tests should enumerate valid and invalid transitions, display strings, transition_checked mismatch behavior, exclusive flag set/clear success and failure, final-state immutability, and future multiple-flag expansion.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/controller_state.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/device.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/device.rs

### Purpose
`nvmx/device.rs` exposes a running NVMe controller namespace as the repository's generic `BlockDevice`, `BlockDeviceDescriptor`, and `DeviceIoController` abstractions.

### Important APIs, Types, And Functions
`NvmeBlockDevice` stores namespace, name, and cached geometry. `NvmeDeviceDescriptor` stores namespace, SPDK controller, I/O device id, name, and protection flags. `NvmeBlockDevice::open_by_name()` and free functions `lookup_by_name()`/`open_by_name()` are the lookup APIs. `NvmeDeviceIoController` forwards timeout action operations to the controller.

### Control Flow
Open and lookup paths read `NVME_CONTROLLERS`, require the controller to be `Running`, and create descriptors or block-device views from namespace 1. Descriptors can create synchronous or nonblocking `NvmeDeviceHandle`s. The `BlockDevice` implementation delegates geometry and capabilities to `NvmeNamespace`, gathers I/O stats through controller channel traversal, opens descriptors, returns an I/O controller, and registers event listeners on the controller.

### State, Persistence, And Dependencies
State is runtime-only and mostly references shared namespace/controller state. Cached block count and block size act as fallbacks if namespace queries later return zero. Dependencies include the global controller list, `NvmeDeviceHandle`, `NvmeNamespace`, `BlockDevice` traits, `DeviceEventSink`, and `DeviceTimeoutAction`.

### Integration Points
This file is the bridge from `nvmx` controller internals into generic bdev/device APIs used by nexus, initiator tools, and I/O paths. It also exposes per-device timeout action control to higher layers.

### Risks
Read-only open is logged but not enforced. Namespace absence after a running check uses `expect()` in lookup. The device supports `Reset`, `NvmeAdmin`, `NvmeIo`, and `Abort` based on controller namespace capabilities, but actual implementation sits in `handle.rs`; capability drift between files is possible.

### Test Signals
Cover lookup/open for missing, new, faulted, and running controllers; no-namespace errors; descriptor handle creation; geometry fallback; capability flags for compare/unmap/write-zeroes/metadata; I/O stats callback success/failure; timeout action get/set; and listener registration.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/device.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/handle.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/handle.rs

### Purpose
`nvmx/handle.rs` is the NVMe block-device I/O submission layer. It owns per-handle SPDK I/O channels, DMA allocation, read/write/compare/flush/unmap/write-zeroes dispatch, NVMe admin/I/O passthrough, reservations, snapshots, reset dispatch, completion translation, and I/O-context pooling.

### Important APIs, Types, And Functions
`NvmeDeviceHandle` implements `BlockDeviceHandle`. `NvmeIoCtx` is the pooled callback context for BIO-style I/O. `nvme_io_ctx_pool_init()`, `alloc_nvme_io_ctx()`, and `free_nvme_io_ctx()` manage the pool. Completion functions include `complete_nvme_command()`, `nvme_io_done()`, `nvme_writev_done()`, `nvme_unmap_completion()`, and `nvme_flush_completion()`. Helper functions validate I/O, map errors, walk SGLs, and check channel readiness.

### Control Flow
Handle creation gets an SPDK I/O channel by controller id, stores controller/namespace/protection flags, and connects the qpair synchronously or asynchronously. Deprecated async `read_at()`/`write_at()` validate byte alignment, submit a single-buffer SPDK command, await a oneshot completion, update stats, and decrement pending I/O. Callback-based vector operations allocate `NvmeIoCtx`, optionally inject faults, choose single-buffer or vectored SPDK calls, and account pending I/O. Completions update stats, translate NVMe status, invoke the caller callback with the block device, and free the context. Reset delegates to the controller. Flush and unmap use SPDK flush and dataset management commands. Admin and I/O passthrough build raw NVMe commands and await oneshot completions; reservation helpers and snapshot creation are layered on passthrough/admin.

### State, Persistence, And Dependencies
Per-handle state includes `ManuallyDrop<NvmeControllerIoChannel>`, controller wrapper, namespace `Arc`, protection flags, cached block size, and a block-device view. Per-I/O state is pooled in `NVME_IOCTX_POOL`; callbacks hold raw pointers to this state and the SPDK channel. Snapshot creation serializes `NvmeSnapshotMessage` into a DMA payload, but persistence happens on the target side. Dependencies include SPDK namespace/controller command APIs, `DmaBuf`, `IoVec`, `NvmeStatus`, `MemoryPool`, `Reactors`, `SnapshotParams`, and optional fault injection.

### Integration Points
`device.rs` constructs these handles from descriptors. `channel.rs` provides qpair and stats access. `controller.rs` services reset and timeout operations. Initiator and nexus paths rely on this implementation for actual NVMe I/O and management commands.

### Risks
On dispatch failure after allocating `NvmeIoCtx`, several paths return an error without freeing the context, unless the pool or caller handles it elsewhere. `unmap_blocks()` manually allocates a DSM range array and does not visibly free it on success or failure. Flush allocates a context but does not call `account_io()`, while completion skips pending decrement for flush; this is intentional for accounting but differs from other operations. Raw callback pointers require channel and handle lifetimes to remain valid. Some admin/reservation helpers unwrap DMA allocation.

### Test Signals
Exercise alignment validation, empty/uninitialized iovs, pool exhaustion, single and vectored read/write/compare, pending-I/O accounting on success/error, PI error detection, dispatch failure cleanup, unmap range splitting and limits, write-zeroes, flush accounting, reset callback translation, admin passthrough status handling, identify controller, reservation register/acquire/release/report, snapshot payload encoding, and fault-injection behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/handle.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/mod.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/mod.rs

### Purpose
`nvmx/mod.rs` is the module root for the Rust-native NVMe/NVMe-oF block-device stack. It re-exports public types, owns the global controller registry, and exposes running NVMe bdev configuration.

### Important APIs, Types, And Functions
`NVMeCtlrList` wraps a `RwLock<HashMap<String, Arc<Mutex<NvmeController>>>>`. It provides `lookup_by_name()`, `remove_by_name()`, `insert_controller()`, and `controllers()`. `NVME_CONTROLLERS` is the process-wide lazy registry. `nvme_bdev_running_config()` returns `Config::get().nvme_bdev_opts`. The module re-exports controller, device, handle, namespace, qpair, snapshot, and URI template types.

### Control Flow
Controllers are inserted first under their NQN-derived name, then after attach under the SPDK pointer-derived controller id. Removal by name removes both the name entry and the id entry by locking the controller to read its id. `controllers()` returns keys containing `nqn`, filtering out numeric id aliases.

### State, Persistence, And Dependencies
Controller registry state is in-memory only. Values are shared `Arc<Mutex<_>>` handles used by device lookup, channel creation, destroy, timeout, and event notification paths. Dependencies include `parking_lot`, `once_cell`, `Config`, and `CoreError`.

### Integration Points
Almost every `nvmx` submodule uses `NVME_CONTROLLERS` to move from URI-created controllers to block devices, I/O channels, timeouts, and destroy. External code imports `lookup_by_name`, `open_by_name`, `NvmeDeviceHandle`, and snapshot message types through this module.

### Risks
Using multiple keys for the same controller means insertion/removal must stay balanced; stale id aliases can keep controllers reachable. `controllers()` filters by substring `"nqn"`, so nonstandard names may be hidden. `remove_by_name()` locks a controller while holding the write lock, which should be checked for deadlock against paths that lock in the opposite order.

### Test Signals
Test insertion by name and id, lookup cloning, removal removing both keys, missing removal error, controller list filtering, duplicate insert overwrites, and lock ordering under concurrent lookup/remove.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/namespace.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/namespace.rs

### Purpose
`nvmx/namespace.rs` wraps an SPDK NVMe namespace pointer and exposes geometry, identity, alignment, metadata, and feature capability queries.

### Important APIs, Types, And Functions
`NvmeNamespace(NonNull<spdk_nvme_ns>)` exposes `size_in_bytes()`, `block_len()`, `num_blocks()`, `uuid()`, `supports_compare()`, `supports_deallocate()`, `supports_write_zeroes()`, `alignment()`, `md_size()`, `from_ptr()`, and `as_ptr()`.

### Control Flow
Methods are thin unsafe calls to SPDK namespace getters. `from_ptr()` converts a raw namespace pointer to `NonNull` and panics on null. Capability methods inspect SPDK flags for deallocate and write-zeroes support.

### State, Persistence, And Dependencies
The wrapper stores only the raw namespace pointer and is marked `Send`/`Sync`. It depends on the controller lifetime keeping the SPDK namespace valid and on `spdk_rs::Uuid` conversion.

### Integration Points
`controller.rs` populates namespaces after attach and AER changes. `device.rs` exposes namespace geometry and capabilities through `BlockDevice`. `handle.rs` uses `as_ptr()` for every namespace command.

### Risks
The file itself questions whether `NvmeNamespace` is truly `Send`/`Sync`; this is a real safety contract with SPDK. Any use after controller detach is undefined. `alignment()` returns optimal I/O boundary, which may not be a memory alignment in all contexts.

### Test Signals
Use SPDK-backed tests or mocks for geometry, UUID conversion, capability flags, metadata size, null pointer panic, and namespace lifetime across controller removal.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/namespace.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/poll_group.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/poll_group.rs

### Purpose
`nvmx/poll_group.rs` wraps SPDK NVMe poll groups used by per-core I/O channels to process qpair completions.

### Important APIs, Types, And Functions
`PollGroup(NonNull<spdk_nvme_poll_group>)` exposes `create()`, `add_qpair()`, `remove_qpair()`, and `as_ptr()`. `Drop` destroys the poll group and logs destroy errors.

### Control Flow
`create()` calls `spdk_nvme_poll_group_create()` with a channel context pointer and returns `CoreError::GetIoChannel` on null. Channel creation adds a qpair to the group, channel reset/removal removes it, and polling happens in `channel.rs` through `as_ptr()`.

### State, Persistence, And Dependencies
State is a runtime SPDK poll-group pointer. Dependencies are SPDK poll-group FFI, `QPair`, and `CoreError`.

### Integration Points
`NvmeIoChannelInner` owns a `PollGroup` for each SPDK I/O channel. Qpair lifecycle in `channel.rs` and completion polling both rely on this wrapper.

### Risks
Destroy errors are logged but cannot be recovered during Drop. The wrapper assumes all qpairs are removed or otherwise safe before destruction. Raw pointer validity depends on SPDK channel lifetime.

### Test Signals
Cover poll group creation failure, add/remove return codes, destroy logging on error, and channel teardown ordering around qpair removal.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/poll_group.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/qpair.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/qpair.rs

### Purpose
`nvmx/qpair.rs` wraps SPDK NVMe I/O qpairs, including allocation, synchronous connection, optional asynchronous connection, state tracking, waiter fan-out, and teardown.

### Important APIs, Types, And Functions
`QPairState` tracks disconnected, optionally connecting, connected, and dropped. `QPair` owns `Rc<RefCell<Inner>>`, with `create()`, `connect()`, `connect_async()`, `as_ptr()`, and `state()`. `Inner` stores raw qpair/controller pointers, controller name, state, and async waiters. With the async feature, `Connection` owns the poller and SPDK async connect context.

### Control Flow
`create()` gets default qpair options from SPDK, raises `io_queue_requests` to at least configured value, forces `create_only` and async mode, allocates a qpair, and starts disconnected. `connect()` is idempotent for already connected qpairs and otherwise calls SPDK sync connect. Drop marks abort-do-not-retry, aborts queued/transport requests, disconnects and frees the qpair, then nulls raw pointers and marks `Dropped`. Async connect coalesces concurrent waiters, polls the SPDK async context, and completes all listeners with the same result.

### State, Persistence, And Dependencies
State is runtime-only and qpair-local. `Rc<RefCell<_>>` indicates intended single-thread/reactor use. Dependencies include SPDK qpair allocation/connect/free APIs, configured NVMe bdev options, futures oneshot, and optional poller/unsafe-ref machinery.

### Integration Points
`channel.rs` creates, connects, drops, and reinitializes qpairs. `handle.rs` optionally awaits async qpair connect before I/O. Poll groups add qpairs by raw pointer.

### Risks
Drop always dereferences `self.as_ptr()` before nulling; double-drop or use after dropped state would be unsafe. Async connection leaks a boxed `Connection` intentionally until callback/poller completion; cancellation paths must free the SPDK probe manually. `Rc<RefCell>` is not thread-safe, so moving qpairs across cores would violate assumptions. The code always sets `async_mode = true` even for sync connect.

### Test Signals
Cover allocation failure, default option merging, sync idempotency, sync failure reverting state, drop abort/disconnect/free ordering, async multiple waiters, async poll errors, qpair dropped during async connect, and feature-disabled behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/qpair.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/snapshot.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/snapshot.rs

### Purpose
`nvmx/snapshot.rs` defines the serialized control message sent in a custom NVMe admin command to request snapshot creation.

### Important APIs, Types, And Functions
`NvmeSnapshotMessageV1` wraps `SnapshotParams` and exposes `new()` and `params()`. `NvmeSnapshotMessage` is a versioned enum currently containing only `V1`.

### Control Flow
`handle.rs` constructs `NvmeSnapshotMessage::V1`, serializes it with bincode, places it in a DMA buffer, and sends it through a custom CREATE_SNAPSHOT admin opcode. This file only defines the payload shape.

### State, Persistence, And Dependencies
No runtime state is stored here. The message derives serde serialization/deserialization and carries `SnapshotParams`; persistence or action occurs on the receiving target side.

### Integration Points
The enum is re-exported by `nvmx/mod.rs` and used by `NvmeDeviceHandle::create_snapshot()`. The versioned enum gives room for future wire-format changes.

### Risks
The fields in `NvmeSnapshotMessageV1` are private, so external deserializers must use the enum and accessor. Bincode format compatibility must be maintained between initiator and target builds. Adding variants requires receiver compatibility handling.

### Test Signals
Test round-trip serde/bincode encoding, accessor correctness, compatibility fixtures for V1, and `handle.rs` snapshot command payload construction.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/uri.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/uri.rs

### Purpose
`nvmx/uri.rs` converts NVMe-oF URLs into Rust-native NVMe controller instances. It owns async SPDK connect/probe setup, host NQN/host ID option construction, initial controller registry insertion, and cleanup on attach failure.

### Important APIs, Types, And Functions
`NvmfDeviceTemplate` stores name, alias, host, port, subsystem NQN, protection flags, optional UUID, and optional host NQN. `NvmeControllerContext` owns controller opts, transport ID, attach completion channel, poller, and attached flag. `connect_attach_cb()` handles SPDK attach completion. The `CreateDestroy` implementation performs create and destroy. `TryFrom<&Url>` parses the URI.

### Control Flow
Parsing requires a host and one path segment, accepts `reftag`, `guard`, `uuid`, and `hostnqn`, strips IPv6 brackets, and defaults port to 8420. `create()` rejects existing controller names, inserts a new uninitialized controller as a guard, builds connect context and transport options, calls `spdk_nvme_connect_async()`, installs the boxed context as callback context, starts a poller that drives `spdk_nvme_probe_poll_async()`, and awaits the attach result. Attach callback unregisters the poller, marks attached, and delegates successful controller setup to `connected_attached_cb()`. On attach error, `create()` destroys the partially initialized controller and returns the original create failure. `destroy()` delegates to `controller::destroy_device()`.

### State, Persistence, And Dependencies
State is runtime controller registry state plus an attach context temporarily owned through a raw pointer. Host identity is derived from explicit `hostnqn`, `MayastorEnvironment`, or `MAYASTOR_NVMF_HOSTID`. Dependencies include SPDK async connect/probe APIs, `controller` option and transport builders, global config, URI helpers, `NVME_CONTROLLERS`, and `BdevError`.

### Integration Points
This is the URI entry point for the newer `nvmx` stack. It creates controllers later discovered by `device.rs` and opened by generic device APIs. Host identity choices affect NVMe-oF target-side connection tracking and reservation/PTPL behavior.

### Risks
Unlike older URI adapters, this parser does not call `reject_unknown_parameters()`, so unexpected query parameters are silently ignored after known removals. `uuid` and `alias` are stored but not visibly enforced or added in this path. Raw attach context/poller management must unregister exactly once. On failure, cleanup calls full controller destroy while the controller may still be in `New`.

### Test Signals
Cover URI validation, IPv6 bracket stripping, default port 8420, protection flag parsing, hostnqn and hostid option selection, unknown query handling, duplicate create guard, async connect null failure cleanup, poller failure path invoking callback, namespace attach failure cleanup, successful running-state assertion, and destroy behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/uri.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/utils.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/utils.rs

### Purpose
`nvmx/utils.rs` centralizes small NVMe status and event constants used by the controller and handle layers.

### Important APIs, Types, And Functions
`nvme_cpl_is_pi_error()` detects guard, application tag, and reference tag media errors. `nvme_cpl_succeeded()` checks generic success status. Public enums expose media error codes, AER event types, notice info, NVM command set info, and dataset-management attributes.

### Control Flow
Both completion helpers read status-code type and status-code fields from an SPDK completion. PI detection matches media error SCT plus one of the three protection-information status codes. Success detection matches generic SCT and success SC.

### State, Persistence, And Dependencies
There is no state. The file depends only on SPDK completion layout from `spdk_rs`.

### Integration Points
`handle.rs` uses PI and success helpers for I/O completion logging and passthrough/admin completion mapping. `controller.rs` uses AER enum values to interpret async event completions. `handle.rs` uses `NvmeDsmAttribute::Deallocate` for unmap.

### Risks
The helper assumes the bindgen status bitfield layout matches the SPDK/NVMe headers in use. New NVMe status types or PI codes would require updates. Null completion pointers would be unsafe.

### Test Signals
Unit tests can construct synthetic completions for generic success, generic failure, each PI media error, non-PI media errors, null-safety expectations, and AER value matching used in `controller.rs`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nvmx/utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nx.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/nx.rs

### Purpose
`nx.rs` implements a URI adapter for creating and destroying nexus devices directly from `nexus:///name?size=...&children=...`. It is intended for testing and benchmarking rather than normal control-plane operation.

### Important APIs, Types, And Functions
`Nexus` stores name, size in bytes, and child URIs. `TryFrom<&Url>` parses the URI. `GetName` returns the nexus name. `CreateDestroy` calls `nexus_create()` and `nexus_lookup_mut().destroy()`.

### Control Flow
Parsing requires a nonempty path, `size` query parsed through byte-unit, and `children` query split on commas; unknown parameters are rejected. `create()` calls `crate::bdev::nexus::nexus_create()` with no UUID and returns the nexus name. `destroy()` looks up the mutable nexus by name and calls its async destroy method.

### State, Persistence, And Dependencies
State is owned by the nexus subsystem after creation; this adapter stores only parsed URI data. Dependencies include URI helpers, byte-unit parsing, unknown-parameter rejection, nexus create/lookup/destroy, and `BdevError` mapping.

### Integration Points
Generic `bdev_create()` can use this adapter to spin up nexus devices in tests or performance tools. It bypasses gRPC/control-plane workflows and therefore should not be treated as the primary product lifecycle path.

### Risks
Children are split by comma without escaping, which is acceptable for current URI forms but fragile for future child URI syntaxes. Empty children entries are not filtered. The adapter does not manage persistence keys or share state.

### Test Signals
Cover missing size, invalid size, missing children, unknown parameters, multiple child parsing, empty child entries, create error mapping, destroy missing nexus, and successful destroy error propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nx.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/uring.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/uring.rs

### Purpose
`uring.rs` adapts files or block devices to SPDK io_uring bdevs via the generic URI API.

### Important APIs, Types, And Functions
`Uring` stores path/name, original URI alias, block size, and optional UUID. `TryFrom<&Url>` parses paths and query parameters. `GetName`, `CreateDestroy`, and `Probe` integrate with generic bdev management.

### Control Flow
Parsing rejects empty paths, detects whether the path is a block device, defaults block size to `0` for block devices and `512` for regular files unless `blk_size` is supplied, parses optional UUID, and rejects unknown parameters. `create()` rejects an existing bdev, fills `bdev_uring_opts` with filename/name, calls `create_uring_bdev()`, optionally sets UUID, adds the alias, and returns the bdev name. `destroy()` calls `delete_uring_bdev()` through a oneshot completion. `probe()` delegates to `probe_file()`.

### State, Persistence, And Dependencies
The SPDK uring bdev is runtime state only; data persistence depends on the backing file/block device. Dependencies include Unix file type inspection, SPDK uring FFI, `UntypedBdev`, URI helpers, UUID parsing, and callback helpers.

### Integration Points
This adapter is selected for uring URIs and is used wherever generic bdev creation can attach local files or block devices. Alias metadata allows later URI-to-bdev matching.

### Risks
For block devices, block size `0` delegates sizing to SPDK; for regular files the default is fixed 512, so caller expectations must match file layout. `CString::new(self.get_name()).unwrap()` will panic if a path contains NUL. Create failure returns `BdevNotFound`, which may hide the real SPDK failure reason.

### Test Signals
Cover regular file and block device defaults, explicit `blk_size`, UUID parsing, unknown parameters, probe_file outcomes, duplicate create, alias failure logging, create null pointer, destroy cancellation, and missing destroy target.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/uring.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/util/mod.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/util/mod.rs

### Purpose
`bdev/util/mod.rs` declares utility submodules shared by bdev URI adapters and io_uring support.

### Important APIs, Types, And Functions
It exposes `pub(super) mod uri` for URI parsing helpers and `pub mod uring` for kernel io_uring support checks.

### Control Flow
There is no runtime logic in this file; it only controls module visibility.

### State, Persistence, And Dependencies
No state or persistence. Dependencies are the sibling `uri.rs` and `uring.rs` modules.

### Integration Points
Bdev adapters import `crate::bdev::util::uri` for path/query parsing. Other code can import `bdev::util::uring::kernel_support()`.

### Risks
`uri` is `pub(super)`, so helpers are intentionally limited to the bdev module tree. Adding new utility modules here changes public or internal API surface.

### Test Signals
Build tests are sufficient for module visibility; behavior is covered in the submodule reports.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/util/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/util/uri.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/util/uri.rs

### Purpose
`bdev/util/uri.rs` provides small URI query/path parsing helpers reused across bdev adapters.

### Important APIs, Types, And Functions
`segments(&Url)` returns normalized path segments with a lone empty segment removed. `boolean(value, empty)` parses yes/on/no/off, numeric booleans, Rust bool strings, and empty values. `uuid(value)` parses an optional UUID string.

### Control Flow
`segments()` delegates to `Url::path_segments()` and normalizes `/` to an empty vector. `boolean()` first handles empty strings, custom yes/no tokens, numeric strings where any nonzero value is true, then falls back to `str::parse::<bool>()`. `uuid()` maps optional strings through `uuid::Uuid::parse_str()` using `transpose()`.

### State, Persistence, And Dependencies
No state or persistence. Dependencies are `url`, `uuid`, and `ParseBoolError`.

### Integration Points
`null_bdev`, `nvmf`, `nvmx::uri`, `nx`, `uring`, and other URI adapters use these helpers for consistent query parsing and error context.

### Risks
Numeric booleans accept any `u32`, so `2` is true. Empty values map to the caller-provided default, which can differ by parameter. `segments()` does not percent-decode beyond what `url` returns in path segment iteration.

### Test Signals
Cover empty path, root path, multiple path segments, yes/on/no/off, true/false, numeric zero/nonzero, invalid boolean strings, empty boolean defaults, valid/invalid UUID, and `None` UUID.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/util/uri.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/util/uring.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev/util/uring.rs

### Purpose
`bdev/util/uring.rs` checks whether the running kernel supports io_uring with the queue depth expected by SPDK uring bdevs.

### Important APIs, Types, And Functions
`kernel_support()` attempts to create `io_uring::IoUring` with queue depth 512 and returns a boolean.

### Control Flow
The function returns true on successful ring creation. On error it logs the error at debug level and returns false.

### State, Persistence, And Dependencies
No persistent state. The function briefly creates and drops an io_uring instance. Dependency is the `io_uring` crate and logging.

### Integration Points
Capability checks can use this before enabling or selecting the uring bdev path.

### Risks
Successful creation at depth 512 is a proxy for support, not a complete guarantee that every SPDK uring operation will work with a given file/device. Permission and resource limits can make support appear false.

### Test Signals
Cover success on supported kernels, expected false on blocked/unsupported environments, and debug logging on creation failure. Unit testing likely needs a wrapper or integration environment because it depends on kernel features.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/util/uring.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev_api.rs -->
## sources/control-plane/mayastor/io-engine/src/bdev_api.rs

### Purpose
`bdev_api.rs` provides the generic URI-facing bdev create/destroy/name/equality API and central error type shared by URI adapters.

### Important APIs, Types, And Functions
`BdevError` enumerates URI parse, unsupported scheme, invalid parameter, duplicate/missing bdev, create/destroy/resize failures, canceled commands, and wipe failure. `ToErrno for BdevError` maps errors to `nix::Errno`. Public functions are `bdev_create()`, `bdev_destroy()`, `bdev_get_name()`, `bdev_uri_eq()`, and `bdev_url_eq()`. `TryFrom<Bdev<T>> for Url` extracts a bdev URI.

### Control Flow
Create/destroy/name parse the URI through `bdev::uri::parse()` and dispatch trait methods on the resulting adapter. URI equality parses the provided URL, compares parsed device name to the bdev name, then compares bdev driver against the URI scheme with NVMe-family schemes normalized to `"nvme"`. Conversion from bdev to URL asks the bdev for its stored URI and reports aliases when none match.

### State, Persistence, And Dependencies
No state is stored here. It depends on adapter registry/parsing in `bdev::uri`, core `Bdev`, `Share` import, `ToErrno`, `snafu`, `url`, and lower-level parse errors.

### Integration Points
CLI tools, control-plane handlers, tests, and nexus child creation use this as the top-level URI bdev API. The error type is used by many adapter files for consistent user-facing diagnostics.

### Risks
`BdevExists` maps to `ENOENT`, which is counterintuitive and may affect API consumers. `bdev_uri_eq()` and `bdev_url_eq()` are duplicate implementations. Scheme normalization must stay aligned with every URI adapter. String-based errors map to `EPERM`, which may be too generic.

### Test Signals
Cover every `ToErrno` mapping, parse dispatch for create/destroy/name, unsupported schemes, equality for nvmf/nvmf+tcp/nvmf+rdma+tcp/pcie mapping to nvme, alias extraction failure, and duplicate behavior of the two equality functions.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev_api.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/casperf.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/casperf.rs

### Purpose
`bin/casperf.rs` is a simple Mayastor/SPDK performance tool that creates bdevs from URIs and drives random read or write I/O at a configured queue depth, printing per-second throughput.

### Important APIs, Types, And Functions
`IoType` selects random read or write. `Job` owns the bdev, descriptor, I/O channel, queue depth, block sizing, I/O queue, counters, RNG, drain flag, and run period. `Io` owns a DMA buffer, operation type, offset, and raw job pointer. `sig_override()`, `perf_tick()`, and `main()` control lifecycle.

### Control Flow
`main()` disables NVMf target services, enables all-thread nexus channels, initializes Mayastor, registers nexus module, and on the master reactor creates one job per URI. Each job creates the bdev, opens it, computes I/O geometry, allocates `qd + 1` DMA buffers, starts on an `Mthread`, and submits initial I/O. Completion callbacks update counters, free SPDK bdev I/O, submit the next random operation unless draining, and stop the environment when all drained jobs finish. A poller prints average IO/s and MB/s once per second. Signal handlers unregister the perf poller and set all jobs to drain.

### State, Persistence, And Dependencies
State is thread-local `JOBLIST` and `PERF_TICK`, plus SPDK bdev/channel resources. Data written by random write persists only according to backing device semantics; the tool does not verify contents. Dependencies include Clap, random number generation, Mayastor environment/reactors/threads, `bdev_create`, SPDK bdev read/write APIs, `DmaBuf`, and signal-hook.

### Integration Points
The tool is a developer benchmark harness for any URI-supported bdev, including nexus and null/uring/nvme paths. It disables target services so it behaves as an initiator/workload generator.

### Risks
The queue is sized `0..=qd`, producing `qd + 1` I/O slots, so actual outstanding depth may exceed the user-specified queue depth. `io_size` is stored inconsistently: comments imply blocks, but later it is set to bytes after `io_blocks` calculation; SPDK offsets are byte offsets, so naming can confuse maintenance. `io_blocks = num_blocks / io_size` mixes blocks and bytes if `io_size` is bytes, which may produce bad ranges. Raw job pointers require jobs to outlive all queued I/O.

### Test Signals
Exercise CLI parsing, zero/large qd, io_size smaller/larger than block size, random offset bounds, read/write submission failure, drain on SIGINT/SIGTERM, poller unregister, all jobs complete stopping environment, and throughput calculation with controlled counters.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/casperf.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/initiator.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/initiator.rs

### Purpose
`bin/initiator.rs` is a command-line test initiator for connecting to, reading from, writing to, and issuing management commands against a replica or target URI understood by the nexus/device stack.

### Important APIs, Types, And Functions
`Error` flattens `CoreError`, `DmaError`, `BdevError`, and `io::Error` into printable messages. Helper async functions implement `create_bdev()`, `read()`, `write()`, `nvme_admin()`, `identify_ctrlr()`, `create_snapshot()`, and `connect()`. `Args` and `SubCommand` define the CLI. `run_static_initializers()` installs the config subsystem in the static initializer array.

### Control Flow
`main()` parses args, initializes logging and config with NVMf target services disabled, starts the Mayastor environment, dispatches the chosen subcommand on a reactor, logs any error, stops the environment, and exits with the command result. `read()` and `write()` create/open a device from the URI, allocate one block-sized DMA buffer, and transfer one block to or from a file at the requested byte offset. NVMe admin helpers open the device read/write and call handle methods. Snapshot creation builds placeholder `SnapshotParams` with generated UUIDs and current time.

### State, Persistence, And Dependencies
The tool creates runtime bdev/device state and may persist data to backing storage or snapshot state on the target. Local file I/O is used for read/write and identify output. Dependencies include Clap, Chrono, UUID, Mayastor environment/reactor/device APIs, bdev API, SPDK DMA errors, and config subsystem initialization.

### Integration Points
This binary is a manual/integration test utility for URI adapters and the `BlockDeviceHandle` management APIs, especially NVMe admin, identify, and snapshot commands.

### Risks
Many device open/handle/DMA calls use `unwrap()`, so operational failures can panic instead of returning the flattened `Error`. `write()` reads an arbitrary file but writes only one device block and warns if the DMA buffer is not fully initialized. `read()` always reads one block, regardless of file size expectations. Snapshot parameters are placeholders until nexus-level snapshots are complete.

### Test Signals
Cover each subcommand, invalid URI errors, open failures without panic if refactored, one-block read/write semantics, partial file write warning, NVMe admin opcode dispatch, identify output size, snapshot parameter generation, environment shutdown on success/failure, and config subsystem static initializer behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/initiator.rs -->
