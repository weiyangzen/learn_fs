# subset-b-000417 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/nvmf/target.rs -->
# sources/control-plane/mayastor/io-engine/src/subsys/nvmf/target.rs

Purpose: owns the Mayastor SPDK NVMe-oF target lifecycle. It wraps `spdk_nvmf_tgt`, drives SPDK subsystem init/fini through a Rust state machine, creates per-reactor poll groups, adds TCP/RDMA transports, starts listeners for nexus and replica ports, creates the discovery subsystem, and tears everything down during shutdown.

Important APIs/types/functions: `NVMF_TGT` is a master-core thread-local `RefCell<Target>`. `Target` stores the raw target pointer, poll-group count, next `TargetState`, and whether RDMA listeners were actually enabled. `TargetState` enumerates `Init`, `PollGroupInit`, `AddTransport`, `AddListener`, `Running`, shutdown phases, `Invalid`, and `ShutdownCompleted`. `Target::next_state` is the central dispatcher. `init` calls `spdk_nvmf_tgt_create` with configured target options. `init_poll_groups` creates an `Mthread` per reactor and schedules `create_poll_group`. `add_transport` calls `transport::create_and_add_transports`. `listen` and `listen_rdma` bind TCP/RDMA listener trids for both nexus and replica ports. `create_discovery_subsystem` makes the discovery NQN and sets the model number. `start_shutdown`, `stop_subsystems`, `destroy_pgs`, and `shutdown` handle fini.

Control flow: initialization starts at `TargetState::Init`; each state sets the next state before scheduling work so callbacks can resume the state machine. Poll-group creation runs on each reactor thread, then reports completion back to the master reactor; only when `poll_group_count == spdk_env_get_core_count()` does the target advance to transport creation. Transport creation is async on the master reactor and marks the target invalid on error. Listener setup creates TCP listeners first and optionally attempts RDMA; RDMA failures are warning-only after transport creation fallback. `running` starts the discovery subsystem, then calls `spdk_subsystem_init_next(0)`.

State and persistence: target state is in memory only and must run on the first core. Poll groups are retained in the `NVMF_PGS` thread-local/global registry. RDMA listener state is remembered in `Target::rdma` so shutdown stops only listeners that were added. No durable data is written here; persistent NVMf exports are represented by subsystem/lvol metadata elsewhere.

Dependencies and integration points: integrates with SPDK NVMf APIs, Mayastor `Config`, `MayastorEnvironment`, reactor/mthread scheduling, `PollGroup`, `NvmfSubsystem`, `TransportId`, and global `NVMF_PGS`. It participates directly in SPDK subsystem ordering by calling `spdk_subsystem_init_next` and `spdk_subsystem_fini_next`.

Risks and edge cases: many calls unwrap, so failures during target creation/listener setup can panic except for the explicit invalid path. `get_ip_address().unwrap()` in logging/listener code assumes environment validation happened earlier. Shutdown skips `spdk_nvmf_tgt_stop_listen` under ASAN because of a known use-after-free. The poll-group count is a `u16` derived from core count and must exactly match callbacks; missing callback would stall init/fini. RDMA failure degrades silently to TCP by design, which can mask performance regressions.

Test signals: this file is indirectly exercised by all NVMf share and block-device tests in this subset: `mount_fs.rs`, `ftl_mount_fs.rs`, `block_device_nvmf.rs`, `nexus_add_remove.rs`, and `nexus_children_add_remove.rs` require listeners, discovery, subsystem startup, and shutdown cleanup to work.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/nvmf/target.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/nvmf/transport.rs -->
# sources/control-plane/mayastor/io-engine/src/subsys/nvmf/transport.rs

Purpose: builds SPDK NVMe-oF transports and formats transport IDs/URIs for the target. It is the bridge from Mayastor configuration and environment IP selection to SPDK `spdk_nvme_transport_id` and `spdk_nvmf_transport_create` calls.

Important APIs/types/functions: `create_and_add_transports(add_rdma)` creates TCP transport from `Config::nvmf_tgt_conf.opts_tcp`, adds it to `NVMF_TGT`, then optionally creates/adds RDMA from `opts_rdma`. `TransportId` wraps `spdk_nvme_transport_id` with `Deref`, `DerefMut`, `Display`, `Debug`, `new`, and `as_ptr`. `get_ip_address` maps `MayastorEnvironment::get_nvmf_tgt_ip` into the local NVMf `Error`.

Control flow: TCP transport creation is mandatory; null creation maps to `Error::Transport`. Adding a transport uses an SPDK completion callback bridged through a futures oneshot channel. RDMA is optional: creation failure is logged and treated as success so the target can run TCP-only; add completion is awaited with `.ok()` and does not propagate a failed callback result. `TransportId::new` chooses TCP or RDMA constants, IPv4/IPv6 address family, fills SPDK fixed arrays via `copy_cstr_with_null`/`copy_str_with_null`, and asserts service-id length.

State and persistence: no durable state. Static lazy `CString`s provide stable C string storage for TCP/RDMA names. The generated transport ID includes the current configured target IP and port at construction time.

Dependencies and integration points: depends on SPDK NVMf/NVMe constants and functions, Mayastor `Config`, target thread-local `NVMF_TGT`, `MayastorEnvironment`, `SIpAddr`, and FFI callback helpers. `Display` output becomes the NVMf URI form used by share paths; RDMA displays as `nvmf+rdma+tcp://...` to signal dual support.

Risks and edge cases: RDMA add errors are ignored after channel await, so a transport-add failure can be hidden. `TransportId::new` unwraps IP resolution and asserts port string length. IPv6 scope IDs are explicitly not handled. The TCP add result is awaited but assigned to `_result` without `?`, so callback errno may not affect success; only transport creation failure is propagated.

Test signals: indirectly covered by NVMf share and connect tests, especially URI parsing/connection in `mount_fs.rs`, `ftl_mount_fs.rs`, and `block_device_nvmf.rs`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/nvmf/transport.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/nvmx/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/subsys/nvmx/mod.rs

Purpose: registers a Mayastor SPDK subsystem that creates per-reactor admin-queue polling threads for NVMx controllers and exposes lookup helpers for those threads.

Important APIs/types/functions: `NvmxSubsystem` owns a leaked/raw `spdk_subsystem`. `ADMINQ_POLL_THREADS` is a `OnceCell<HashMap<u32, u64>>` mapping reactor core IDs to `spdk_rs::Thread` IDs. `init` creates one `Thread` named `nvmx_poll_adminq_{core}` per reactor, stores the map, and advances SPDK init. `adminq_thread_id` and `adminq_thread` expose lookups. `fini` only advances SPDK fini. `register` calls `spdk_add_subsystem`.

Control flow: SPDK calls `init`; Mayastor iterates reactors, allocates adminq threads on the corresponding core, stores thread IDs once, then calls `spdk_subsystem_init_next(0)`. Callers can later resolve a core to a thread ID or `Thread` object. Fini logs and immediately continues.

State and persistence: state is process-local in `ADMINQ_POLL_THREADS`. The threads are not explicitly deleted in `fini`, as noted by the source comment. No persistent state.

Dependencies and integration points: uses SPDK subsystem registration, `crate::core::Reactors`, and `spdk_rs::Thread`. Consumers in NVMx controller code can use `adminq_thread` to schedule admin queue polling on a core-affine thread.

Risks and edge cases: `Thread::new(...).expect(...)` panics if allocation fails. Calling `adminq_thread_id` before init initializes the `OnceCell` to an empty map, which would prevent the real init map from being stored later; normal SPDK ordering should avoid this, but it is a subtle footgun. Fini does not reclaim threads.

Test signals: no direct tests in this subset; coverage is indirect through any NVMx controller paths not visible here. The absence of direct assertions means init ordering and early lookup behavior are important residual risks.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/nvmx/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/registration/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/subsys/registration/mod.rs

Purpose: defines the SPDK registration subsystem wrapper and default control-plane registration endpoint helpers. It connects SPDK fini with the gRPC registration component so Mayastor deregisters on shutdown.

Important APIs/types/functions: `registration_grpc` submodule contains the gRPC implementation. `default_port`, `default_endpoint_str`, and `default_endpoint` provide the default `https://core:50051` endpoint. `RegistrationSubsystem` wraps a raw `spdk_subsystem`. `init` simply advances SPDK init. `fini` checks `MayastorEnvironment::grpc_endpoint`; if registration was enabled and initialized, it calls `Registration::fini()` before advancing SPDK fini. `register` adds the subsystem.

Control flow: registration subsystem initialization has no async work; real registration is run elsewhere. On shutdown, closing the registration component's fini channel signals its run loop to deregister. SPDK fini proceeds immediately after sending that signal.

State and persistence: no durable state. The subsystem raw pointer is boxed and leaked to SPDK. Runtime registration state lives in `registration_grpc::GRPC_REGISTRATION`.

Dependencies and integration points: integrates with SPDK subsystem registration, Mayastor CLI/environment arguments, `http::Uri`, and the gRPC registration singleton. It is part of lifecycle coordination rather than data-plane I/O.

Risks and edge cases: SPDK fini does not await deregistration completion; it only closes the channel. If the registration run loop is not running, `fini` is a no-op beyond closing. Default endpoint uses HTTPS scheme and will panic only if the constant URI becomes invalid.

Test signals: no direct tests in this subset. Behavior is observable only in startup/shutdown integration tests that enable `grpc_endpoint`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/registration/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/registration/registration_grpc.rs -->
# sources/control-plane/mayastor/io-engine/src/subsys/registration/registration_grpc.rs

Purpose: implements Mayastor node registration/deregistration and heartbeat-like periodic register messages to a control-plane registration service over tonic gRPC.

Important APIs/types/functions: `ApiVersion` parses `v0`/`v1` and converts to protobuf enum. `Configuration` stores node ID, optional host NQN, advertised gRPC endpoint, heartbeat interval/timeout, supported API versions, and process `instance_uuid`. `Registration` holds config, tonic registration client, receive channel, and fini sender. `GRPC_REGISTRATION` is the global singleton. `init`, `new`, `get`, `instance_uuid`, `fini`, `register`, `deregister`, `run`, and `run_loop` are the main API.

Control flow: `init` creates the singleton lazily. `new` reads heartbeat overrides from `MAYASTOR_HB_INTERVAL_SEC` and `MAYASTOR_HB_TIMEOUT_SEC`, creates a lazy tonic channel with connect/request timeouts and HTTP/2 keepalive settings, and stores an unbounded channel pair. `run` clones the singleton and enters `run_loop`. The loop sends `register` immediately and then either sleeps until the next heartbeat or breaks when the channel closes. On exit it attempts one `deregister`.

State and persistence: registration state is in memory. `instance_uuid` is generated per process start to distinguish restarts. `register` includes node ID, endpoint, instance UUID, API versions, host NQN, feature bits, bugfix bits, and raw version string. No local durable storage is used.

Dependencies and integration points: depends on generated `io_engine_api::v1::registration` client/protos, tonic, futures `select`, async-channel, Mayastor feature/bugfix providers, environment variables, and `version_info`. Called from registration subsystem shutdown and from startup registration wiring elsewhere.

Risks and edge cases: register errors are rate-limited in logs by `show_error`, which avoids log spam but may hide repeated failures. `fini` closes the channel but does not itself await deregistration. `connect_lazy` defers connection errors to RPC time. Invalid heartbeat environment values silently fall back to defaults. The unbounded channel currently carries no implemented messages other than closure.

Test signals: no direct tests in this subset. Integration risk is mainly covered by full control-plane deployments rather than local unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/subsys/registration/registration_grpc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/add_child.rs -->
# sources/control-plane/mayastor/io-engine/tests/add_child.rs

Purpose: integration test for adding and removing nexus children on both unshared and NVMf-shared nexuses backed by AIO files.

Important APIs/types/functions: uses `nexus_create`, `nexus_lookup_mut`, `Nexus::add_child`, `remove_child`, `share(Protocol::Nvmf)`, and `unshare_nexus`. `test_start`/`test_finish` manage two 64 MiB temp disk files.

Control flow: creates a one-child nexus, adds the second child without rebuild, asserts two children and that the added child is opened unsynchronized, removes it, shares the nexus over NVMf, repeats add/remove while shared, then unshares and deletes files.

State and persistence: uses temporary files under `/tmp`; nexus state is in memory. The test observes child state transitions but does not persist metadata.

Dependencies and integration points: depends on `MayastorTest` reactor harness, AIO bdev creation through child URIs, and NVMf sharing stack.

Risks and edge cases: fixed `/tmp/disk1.img` and `/tmp/disk2.img` names can collide with parallel tests. It assumes NVMf target initialization succeeds. It does not verify rebuild completion, only initial unsync state.

Test signals: confirms child add/remove works before and after sharing and protects expected unsynchronized state for newly added children.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/add_child.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/block_device_nvmf.rs -->
# sources/control-plane/mayastor/io-engine/tests/block_device_nvmf.rs

Purpose: large integration suite for the generic block-device API when the backing device is a remote NVMe-oF namespace. It covers create/destroy, identify, event delivery, synchronous and callback I/O, vectored I/O, flush, stats, admin commands, reset, unmap/write-zeroes, reset-abort semantics, stale handle cleanup, and hot namespace removal.

Important APIs/types/functions: `launch_instance` starts a compose Mayastor target, configures NVMe bdev timeouts/retries, creates/shares `malloc:///disk0`, and returns an NVMf URL. Tests use `device_create`, `device_destroy`, `device_lookup`, `device_open`, `BlockDeviceHandle` methods (`read_at`, `write_at`, `readv_blocks`, `writev_blocks`, `flush_io`, `reset`, `nvme_identify_ctrlr`, `nvme_admin_custom`, `unmap_blocks`, `write_zeroes`), `DeviceEventSink`, `DeviceEventListener`, `IoCompletionStatus`, `DmaBuf`, and `AsIoVecs`. Helpers manage guard/data patterns, callback flags, and ad hoc I/O stats.

Control flow: each test launches a remote target, creates a local NVMe bdev from the NVMf URL, opens descriptors/handles inside `MayastorTest::spawn`, performs one operation pattern, sleeps or waits for callbacks where callback APIs are used, validates data/events/stats, then destroys the device. The vectored tests allocate multiple `DmaBuf`s and verify boundary guards. Reset-abort queues reads/writes and then resets the controller, expecting all queued I/O callbacks to complete with non-success. Hot-remove issues an SPDK JSON-RPC namespace removal on the remote target and expects local device removal notification.

State and persistence: remote target state is per compose container. Local NVMf controller state is created/destroyed per test. Static `OnceCell`s store expected device names for callbacks; global atomic callback flags and counters are reset in relevant tests. No durable disk state beyond temporary malloc device.

Dependencies and integration points: depends on compose orchestration, v0 gRPC bdev share API, SPDK NVMe-oF initiator stack, Mayastor block-device abstraction, async reactor execution, and JSON-RPC passthrough for namespace removal. It also validates `Config::nvme_bdev_opts` application.

Risks and edge cases: callback tests use sleeps rather than explicit completions, making timing sensitive. Some static `OnceCell` device-name storage is per test function but still static; repeated invocations in one process can be brittle. Raw pointers/`AtomicPtr` keep handles alive across async callbacks and require careful drop ordering. Tests depend on network/container startup and NVMf event timing.

Test signals: very strong coverage for NVMf initiator behavior and block-device API contracts, including data integrity, stats accounting, callbacks exactly once, device removal events, failure after cleanup, and no device creation after a namespace is gone.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/block_device_nvmf.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/child_size.rs -->
# sources/control-plane/mayastor/io-engine/tests/child_size.rs

Purpose: verifies nexus creation rejects children that are too small for requested nexus size or metadata requirements, and cleans up bdevs on failure.

Important APIs/types/functions: `create_nexus` builds malloc child URIs from requested sizes and calls `nexus_create`. Tests use `nexus_lookup_mut` and `UntypedBdev` enumeration/lookups.

Control flow: `child_size_ok` creates a 16 MiB nexus with larger/equal children, verifies nexus and child bdevs exist, destroys the nexus, and verifies cleanup. `child_too_small` attempts a 16 MiB nexus with an 8 MiB child and expects failure/no leaked bdevs. `too_small_for_metadata` attempts a 4 MiB nexus and expects failure because metadata consumes capacity.

State and persistence: malloc bdevs only; all state is in memory. `OnceCell<MayastorTest>` shares one Mayastor instance.

Dependencies and integration points: nexus creation/validation, malloc URI parser, bdev registry cleanup.

Risks and edge cases: assumes no other tests leave bdevs in the shared process because it asserts global bdev count is zero. Uses fixed names `core_nexus`, `m0`, `m1`, `m2`.

Test signals: covers successful cleanup and failure cleanup around size validation.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/child_size.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/common.rs -->
# sources/control-plane/mayastor/io-engine/tests/common.rs

Purpose: thin re-export module that exposes the shared `io_engine_tests` harness to integration tests in this directory.

Important APIs/types/functions: `pub use io_engine_tests::*;` makes compose builders, Mayastor test harnesses, file helpers, bdev I/O helpers, fio helpers, macros, and RPC builders available as `common::...`.

Control flow: no runtime logic.

State and persistence: none.

Dependencies and integration points: centralizes the external test support crate import for all sibling tests.

Risks and edge cases: any broad re-export can hide where helpers come from and can make tests sensitive to helper crate API changes.

Test signals: not a test itself; all sibling tests depend on it compiling.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/common.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/core.rs -->
# sources/control-plane/mayastor/io-engine/tests/core.rs

Purpose: core bdev/nexus integration tests covering basic nexus creation/destruction, descriptor/channel use, exclusive opens, size validation, shared device size, and failure when a child path is inaccessible.

Important APIs/types/functions: `do_uring` detects kernel io_uring support. `create_nexus` chooses AIO and optionally uring children. Tests use `nexus_create`, `nexus_lookup_mut`, `UntypedBdev::open_by_name`, `UntypedBdevHandle::open`, `bdev_create`, `bdev_destroy`, and `share(Protocol::Off)`.

Control flow: `core` prepares temp files and calls `works`. `works` creates/destroys a nexus and opens an I/O channel. `core_2` opens two write descriptors and channels, then drops them before destroy. `core_3` verifies exclusive handle open rejects a second exclusive opener. `core_4` iterates child-size/add-child size cases. `core_5` shares a single-child nexus with `Protocol::Off` and checks visible device size does not exceed requested nexus size. `core_6` creates a URI for a missing file and expects nexus creation failure.

State and persistence: uses `/tmp/disk*.img` temp files. `DO_URING` is cached in a mutable static guarded by `Once`. Mayastor instance is shared via `OnceCell`.

Dependencies and integration points: AIO/uring bdev providers, nexus size checks, bdev descriptor/channel lifecycle, sharing path, and kernel io_uring support.

Risks and edge cases: mutable static is used for uring support. Fixed temp file names and a shared Mayastor instance can interfere with parallel tests. Some tests assume previous file setup from earlier tests unless run order/environment provides the files.

Test signals: good coverage of bdev lifecycle invariants, exclusive open behavior, and child-size enforcement.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/core.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/fault_child.rs -->
# sources/control-plane/mayastor/io-engine/tests/fault_child.rs

Purpose: verifies nexus child faulting rules: the only healthy child cannot be faulted, but an unhealthy/unsynchronized child can be faulted permanently.

Important APIs/types/functions: `nexus_create`, `nexus_lookup_mut`, `add_child`, `fault_child`, `FaultReason::OfflinePermanent`, and child state helpers.

Control flow: creates a one-child malloc nexus, adds a second child without rebuild so it remains degraded/unsynced, expects faulting the original healthy child to fail, and expects faulting the unhealthy added child to succeed.

State and persistence: in-memory malloc bdevs and nexus state only.

Dependencies and integration points: nexus child state machine and fault policy.

Risks and edge cases: does not destroy the nexus explicitly at the end, relying on test process cleanup. Names are fixed.

Test signals: targeted regression guard for preventing data-loss by faulting the last healthy child.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/fault_child.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/ftl_mount_fs.rs -->
# sources/control-plane/mayastor/io-engine/tests/ftl_mount_fs.rs

Purpose: feature-gated NVMe PCI FTL filesystem tests. It creates an FTL bdev from base/cache NVMe devices, exports it through a nexus over NVMf, and verifies repeated mount/unmount and fio data verification.

Important APIs/types/functions: `create_connected_nvmf_nexus` creates the FTL-backed nexus, claims `ftl0` with `UntypedBdevHandle`, shares by `Protocol::Nvmf`, connects using `libnvme_rs::NvmeTarget`, and returns the block device path. `csal_fio_run_verify` runs fio with crc32 verify. `create_nexus` builds an `ftl:///ftl0?bbdev=...&cbdev=...` URI.

Control flow: `ftl_mount_fs_multiple` connects and mount/unmounts ten times, then disconnects/unshares/destroys. `ftl_mount_fs_fio` runs fio verification before cleanup. The whole file is behind `#[cfg(feature = "nvme-pci-tests")]`.

State and persistence: uses real PCI devices by default (`pcie:///0000:82:00.0` and `pcie:///0000:83:00.0`) with required LBA formats. Commented AIO fallback notes FTL minimum capacity and metadata constraints. Runtime state is FTL and NVMf target state.

Dependencies and integration points: FTL bdev URI handling, SPDK NVMe PCI devices, NVMf target/initiator, libnvme-rs, filesystem mount helpers, fio, and Mayastor compose harness.

Risks and edge cases: hardware-specific and feature-gated. Requires exact NVMe formatting and large capacity. Claiming/dropping `UntypedBdevHandle` around share is sensitive to bdev ownership.

Test signals: provides high-value end-to-end signal for FTL over NVMf with filesystem/fio workloads when the hardware feature is available.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/ftl_mount_fs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/io.rs -->
# sources/control-plane/mayastor/io-engine/tests/io.rs

Purpose: simple bdev I/O smoke test using an AIO file bdev with all-thread nexus channels enabled.

Important APIs/types/functions: `io_test` creates a 64 MiB temp file via `truncate`, starts `MayastorTest` with `enable_io_all_thrd_nexus_channels`, and calls `start`. `start` creates the AIO bdev and uses `common::bdev_io::write_some`/`read_some`.

Control flow: prepare file, spawn async bdev creation and write/read on Mayastor reactor, remove file.

State and persistence: temporary `/tmp/disk.img` file. The created bdev is not explicitly destroyed before file removal in this test.

Dependencies and integration points: AIO bdev provider, bdev I/O helper, Mayastor reactor harness, shell `truncate` and `rm`.

Risks and edge cases: fixed temp path and shell commands. Lack of explicit bdev destroy could leave state if sharing the same Mayastor process beyond test cleanup.

Test signals: basic verification that bdev create/read/write helpers work.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/io.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/lock.rs -->
# sources/control-plane/mayastor/io-engine/tests/lock.rs

Purpose: unit/integration tests for the async `ResourceLockManager` at global, subsystem, and resource granularity, including try-lock and timeout behavior.

Important APIs/types/functions: `LockLevel` selects global/subsystem/resource locks. `get_lock_manager` initializes manager config with subsystem `items`. `test_lock_level` runs two tasks contending for the same lock and verifies try-lock fails while held. `test_lock_timed_level` verifies timeout returns no guard.

Control flow: first task acquires lock, attempts nonblocking double-lock, signals second task, sleeps while protected counter should remain unchanged, then drops guard. Second task waits for signal and then acquires after release. Timed variant uses a 1 second timeout while the holder sleeps 2 seconds.

State and persistence: process-global `ResourceLockManager` singleton. Atomic `STEP_COUNT` is reset per non-timed helper invocation.

Dependencies and integration points: Tokio task scheduling, oneshot channels, lock manager config/subsystem/resource APIs.

Risks and edge cases: timing sleeps make the tests sensitive to very slow runtimes. Singleton initialization means config changes in other tests could matter if run in same process.

Test signals: covers serialization, nonblocking acquisition, and timeout semantics for all lock levels.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/lock.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/lock_lba_range.rs -->
# sources/control-plane/mayastor/io-engine/tests/lock_lba_range.rs

Purpose: SPDK reactor tests for LBA range locking on a nexus bdev, including overlapping lock serialization and front-end I/O blocking while a range lock is held.

Important APIs/types/functions: `test_ini`/`test_fini` create/destroy a two-child AIO nexus. `lock_range` and `unlock_range` use `UntypedBdev::lock_lba_range`/`unlock_lba_range`. `recv_from` polls current reactor until a crossbeam channel receives. Tests use `LbaRange`, `LbaRangeLock`, `DmaBuf`, and `reactor_poll!`.

Control flow: `lock_unlock` obtains and releases one range. `multiple_locks` acquires one lock, schedules another overlapping lock and confirms it does not complete until the first unlocks. `lock_then_fe_io` acquires a lock, schedules a write to an overlapping block, verifies the I/O does not complete, unlocks, then verifies the write completes.

State and persistence: temporary `/tmp/disk{n}.img` files and in-memory lock state on the nexus bdev. Tests run under `common::spdk_test`.

Dependencies and integration points: SPDK reactor polling, nexus front-end I/O path, bdev range locking, AIO children.

Risks and edge cases: manual reactor polling can be timing-sensitive. Fixed temp paths. The test allows holding RefCell refs across awaits via file-level lint allow.

Test signals: strong coverage that LBA locks serialize overlapping locks and gate front-end writes.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/lock_lba_range.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/lvs_grow.rs -->
# sources/control-plane/mayastor/io-engine/tests/lvs_grow.rs

Purpose: validates LVS pool growth after backing-device expansion through both internal Mayastor APIs and gRPC API, for malloc and AIO-backed devices.

Important APIs/types/functions: `TestPoolStats` normalizes capacity, disk capacity, and max expandable size from `Lvs` or gRPC `Pool`. `GrowTest` trait abstracts pool creation, stats, grow operation, device size, and device grow. `test_grow` encodes shared assertions. Concrete tests are `lvs_grow_ms_malloc`, `lvs_grow_api_malloc`, and `lvs_grow_api_aio`.

Control flow: shared test creates pool, checks initial capacity is near disk capacity, grows the underlying device, verifies pool capacity has not changed while disk capacity reflects growth, calls pool grow, then verifies capacity increases and remains below/near disk capacity. Malloc internal path uses `resize_malloc_disk`; gRPC malloc path recreates malloc bdev with `resize`; AIO path expands a tempfs file by `max_expandable_size - disk_capacity`.

State and persistence: malloc tests use in-memory bdevs; AIO test uses `/tmp/disk1.img` bind-mounted into a compose container. LVS metadata persists on the backing bdev within the test lifetime.

Dependencies and integration points: LVS pool APIs, gRPC v1 pool API, compose builders, `PoolBuilder`, bdev lookup/create helpers, SPDK malloc resize, and filesystem expansion helper.

Risks and edge cases: capacity comparison allows 10 percent tolerance to account for metadata. AIO disk capacity may lag new file size until pool/bdev refresh, which the test explicitly accounts for. Compose/network startup required for API paths.

Test signals: covers internal and external API growth behavior and protects against accidental capacity changes before explicit grow.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/lvs_grow.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/lvs_import.rs -->
# sources/control-plane/mayastor/io-engine/tests/lvs_import.rs

Purpose: stress/regression test for importing an LVS pool with many replicas and snapshots, verifying no volumes are lost or spuriously added.

Important APIs/types/functions: uses `Lvs::create_or_import`, `create_lvol`, `prepare_snap_config`, `create_snapshot`, `export`, and `lvols`. Constants create 100 replicas and 10 snapshots per replica on a 10 GB AIO file.

Control flow: prepares disk, creates LVS, records names of every replica and snapshot created, exports the pool, imports it again with the same args, collects imported lvol names, and compares set differences both ways.

State and persistence: relies on LVS on-disk metadata surviving export/import. Temporary disk file is `/tmp/disk0.img`. UUIDs and names are deterministic.

Dependencies and integration points: LVS metadata import/export, snapshot metadata, AIO bdev, `HashSet` comparison, Mayastor multi-thread reactor settings.

Risks and edge cases: creates 1100 volumes and can be slow or metadata-capacity sensitive. Fixed disk path. It prints timing but has no duration assertion.

Test signals: strong persistence signal for large-volume LVS import correctness.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/lvs_import.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/lvs_limits.rs -->
# sources/control-plane/mayastor/io-engine/tests/lvs_limits.rs

Purpose: verifies LVS metadata exhaustion is reported as `BsError::OutOfMetadata` while creating many replicas and snapshots.

Important APIs/types/functions: uses `Lvs::create_or_import`, `create_lvol`, `prepare_snap_config`, `create_snapshot`, and matches `LvsError::RepCreate`/`SnapshotCreate` source errors.

Control flow: prepares a 10 GB AIO disk, creates a pool, loops up to 100 replicas and 100 snapshots each, breaks when replica or snapshot creation returns `OutOfMetadata`, and panics on any other error.

State and persistence: LVS metadata on `/tmp/disk0.img`; volume names/UUIDs are deterministic.

Dependencies and integration points: LVS allocator/metadata space accounting, snapshot creation path, AIO bdev.

Risks and edge cases: if disk metadata sizing changes enough to avoid exhaustion within loop bounds, the test may pass without proving the limit. It does not assert that exhaustion definitely occurred, only validates error type when it does.

Test signals: focused guard that metadata-full conditions map to the intended error class.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/lvs_limits.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/lvs_pool.rs -->
# sources/control-plane/mayastor/io-engine/tests/lvs_pool.rs

Purpose: comprehensive LVS pool integration suite covering create/import/export/destroy, lvol and share persistence, sector-size support, encrypted pools, I/O error alerting, stall detection/recovery, and hot-remove/hot-reattach behavior.

Important APIs/types/functions: uses `Lvs`, `LvsLvol`, `PoolArgs`, `ReplicaArgs`, `PoolOps`, `pool_to_proto`, `PoolErrors`, `PoolAlerts`, `PoolState`, `NvmfSubsystem`, `UntypedBdev`, `bdev_create`, crypto `EncryptionKey`, LVM `VolumeGroup`, dmsetup state helpers, and reactor I/O helpers. Constants configure pool alert thresholds. `pool_info` converts a pool to proto and extracts error/alert state. `StallBdev` abstracts AIO vs uring stall cases. `TestHotRmGuard` creates/deletes ublk loop devices.

Control flow: `lvs_pool_test` walks the happy-path matrix: failed import of absent pool, create, duplicate create failure, import/export preserving UUID, destroy/recreate with new UUID, multiple lvol creation, second pool filtering, export/import preserving lvols, NVMf share cleanup on pool destroy, share property persistence/non-persistence, import restoring only persisted shares, 4K sector AIO/uring pools, final cleanup, default driver behavior, and encrypted pool creation with crypto base checks. `lvs_errors` borks an LVM logical volume to force EIO, verifies alert escalation from attention to warning at threshold, reset behavior, and cleanup on create/import/export/destroy failures. `lvs_stall` suspends dm devices to create stalled I/O, checks critical stall alerts, recovery after resume, intermittent stall alert escalation, and transition-window reset. `lvs_hot_remove` and `lvs_hot_detach_and_reattach` use ublk hot deletion to verify removing pools leave `iter_all` but not active `iter`, reject reimport while removing, eventually clean up, support reattach/import, and allow a faulted nexus child to be onlined after reattach.

State and persistence: uses `/tmp/io-engine-tests` disk files, loop devices, LVM VGs/LVs, ublk devices, LVS on-disk metadata, share properties stored as lvol properties, and encrypted crypto vbdev state. The hot-remove tests intentionally exercise transient removing state in the LVS registry.

Dependencies and integration points: SPDK LVS blobstore, AIO/uring bdevs, crypto vbdevs, NVMf subsystem registry, LVM/dmsetup shell tooling, ublk kernel module, pool gRPC proto conversion, device monitor, reactor scheduling, and Mayastor pool CLI thresholds.

Risks and edge cases: very environment-sensitive: requires loop, LVM, dmsetup, ublk support, kernel behavior, and enough privileges. Some cleanup is in `Drop` guards and shell scripts. Hot-remove paths have comments documenting known races around lvol destroy callbacks during bdev removal. Fixed paths and names can collide.

Test signals: broadest pool signal in this subset. It validates durable metadata, share restoration, cleanup invariants, alert thresholds, stalled I/O recovery, encrypted backing stack, and hot-remove state-machine behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/lvs_pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/lvs_pool_stress.rs -->
# sources/control-plane/mayastor/io-engine/tests/lvs_pool_stress.rs

Purpose: performance/regression tests for listing large numbers of LVS replicas and snapshots, including conversion to API protobufs and gRPC list latency.

Important APIs/types/functions: `ms` starts Mayastor with gRPC/device monitor and NVMe max namespaces. `lvol_list` creates nearly 8000 thin replicas, converts them to `io_engine_api::v1::replica::Replica`, shares all over NVMf, repeats conversion, and calls `ReplicaRpcClient::list_replicas`. `lvol_snap_list` creates 1024 replicas, 256 snapshots and clones for the first 10, then uses `Lvol::list_all_snapshots`.

Control flow: create large pool with metadata max expansion, populate replicas/snapshots, measure list loops with `Instant`, assert duration thresholds, and destroy all pools.

State and persistence: in-memory malloc-backed LVS pool but with LVS metadata for many lvols/snapshots/clones. gRPC state is served from the Mayastor instance.

Dependencies and integration points: LVS iteration, NVMf share URI lookup, replica protobuf conversion, gRPC server/client, snapshot/clone metadata, chrono timestamps.

Risks and edge cases: time thresholds are performance-sensitive and may fail on heavily loaded systems. Large object counts stress memory and namespace limits. The test sets `RUST_LOG=error` globally.

Test signals: protects against O(n^2) or expensive subsystem lookups during list operations and snapshot enumeration.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/lvs_pool_stress.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/malloc_bdev.rs -->
# sources/control-plane/mayastor/io-engine/tests/malloc_bdev.rs

Purpose: verifies malloc bdev creation using both `size_mb` and `num_blocks` produces equivalent capacity and supports basic read/write.

Important APIs/types/functions: `bdev_create`, `bdev_destroy`, `UntypedBdev::open_by_name`, `DmaBuf`, `write_at`, `read_at`.

Control flow: creates `malloc0` with `size_mb=100` and `malloc1` with equivalent `num_blocks`, opens both, compares size/block count and UUID inequality, writes the same pattern to each, reads back into DMA buffers, compares bytes, then destroys both.

State and persistence: malloc bdevs only; no durable state.

Dependencies and integration points: malloc URI parser, bdev registry, bdev handle I/O, DMA buffer allocation.

Risks and edge cases: destroy URI for `malloc1` uses `size_mb=100` although it was created with `num_blocks`; this intentionally relies on name matching rather than exact URI option matching.

Test signals: basic malloc bdev capacity and data-path sanity.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/malloc_bdev.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/mayastor_compose_basic.rs -->
# sources/control-plane/mayastor/io-engine/tests/mayastor_compose_basic.rs

Purpose: basic compose integration test that starts two Mayastor containers, creates and shares remote bdevs, then creates a local nexus over those NVMf exports and verifies device lookup behavior.

Important APIs/types/functions: compose `Builder`, v0 `GrpcConnect`, `BdevUri`, `BdevShareRequest`, `nexus_create`, `nexus_lookup_mut`, `bdev_create`, `UntypedBdev::bdev_first`, and `device_lookup`.

Control flow: bring up two debug containers, create/share `malloc:///disk0` on each, start an in-process Mayastor, create a two-child NVMf nexus, collect child device names, create an extra local malloc bdev, enumerate SPDK bdevs, assert only local/SPDK-visible devices count as two, and verify NVMf child devices are found by `device_lookup`.

State and persistence: compose containers and in-memory malloc devices. No durable state.

Dependencies and integration points: docker compose harness, v0 bdev gRPC API, NVMf target/initiator, local Mayastor reactor harness, device abstraction.

Risks and edge cases: asserts SPDK enumeration excludes NVMf device abstraction entries, so changes to enumeration semantics may require test updates. Fixed network CIDR/name.

Test signals: end-to-end signal for compose startup, remote share, local nexus creation, and NVMf device lookup outside SPDK bdev enumeration.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/mayastor_compose_basic.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/memory_pool.rs -->
# sources/control-plane/mayastor/io-engine/tests/memory_pool.rs

Purpose: validates generic fixed-size `MemoryPool<T>` allocation, initialization, exhaustion, address uniqueness, reuse of freed entries, and clean drop after all entries are returned.

Important APIs/types/functions: `MemoryPool::<TestCtx>::create`, `get`, `put`, and `TestCtx` payload fields. `POOL_SIZE` is `128 * 1024 - 1`; `TEST_BULK_SIZE` is 32K.

Control flow: allocate every pool item with unique data, track returned pointers in a map, assert one extra allocation fails, free a subset, allocate the same number again and verify addresses are reused from freed entries, verify no pool growth occurred, return all entries, and drop the pool.

State and persistence: in-memory pool only. Stores a raw C string pointer from a `CString` created outside the spawn.

Dependencies and integration points: Mayastor memory pool implementation and raw pointer safety.

Risks and edge cases: large allocation count. Uses raw pointers and relies on the `CString` staying alive while the spawned future runs. Map iteration `.take(TEST_BULK_SIZE)` chooses arbitrary entries.

Test signals: strong allocator behavior signal for pool capacity, reuse, and drop safety.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/memory_pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/mount_fs.rs -->
# sources/control-plane/mayastor/io-engine/tests/mount_fs.rs

Purpose: end-to-end filesystem tests for a mirrored nexus shared over NVMf, validating mount/write/read consistency, repeated mount cycles, and fio verify.

Important APIs/types/functions: `prepare_storage` creates two 400 MiB AIO files. `create_connected_nvmf_nexus` creates/shares a two-child nexus and connects with `libnvme_rs::NvmeTarget`. `mount_test` formats, mounts, writes a file, records md5, destroys the mirror, creates single-child nexuses for each disk, mounts each separately, and verifies md5. Tests call `common::mkfs`, `mount_and_write_file`, `mount_and_get_md5`, `mount_umount`, and `fio_run_verify`.

Control flow: `mount_fs_mirror` runs the md5 split verification for xfs and ext4. `mount_fs_multiple` mount/unmounts the NVMf device ten times. `mount_fn_fio` runs fio verification. Cleanup disconnects target, unshares, and destroys nexuses.

State and persistence: real temp disk files persist filesystem data across destroying the mirror and re-exporting each child individually.

Dependencies and integration points: filesystem tools, mount privileges, libnvme-rs, NVMf target/initiator, nexus mirroring, AIO bdevs, fio.

Risks and edge cases: requires root-like mount permissions and filesystem tools. Fixed `/tmp/disk1.img`/`disk2.img`. Data consistency check assumes both mirrored children contain identical filesystem contents.

Test signals: high-value data-integrity signal across NVMf, nexus mirroring, filesystem, and fio workloads.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/mount_fs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_add_remove.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_add_remove.rs

Purpose: compose-based integration test for creating, sharing, adding children to, removing/destroying, and handling child bdev destruction for NVMf-backed nexuses.

Important APIs/types/functions: helper functions `create_targets`, `nexus_3_way_create`, `nexus_destroy`, `nexus_share`, `nexus_create_2_way_add_one`, and `nexus_2_way_destroy_destroy_child`. Uses v0 bdev gRPC create/share, `nexus_create`, `nexus_lookup_mut`, `add_child`, `share_nvmf`, `bdev_destroy`, and `Share` trait.

Control flow: starts three Mayastor containers, creates/shares `disk0` on each, creates a three-way nexus and shares it then destroys it, creates a two-way nexus and adds the third remote child before sharing then destroys, creates another two-way shared nexus, adds a third child, then destroys one original child bdev by NVMf URL before stopping Mayastor and bringing compose down.

State and persistence: compose containers with malloc bdevs and in-process nexus state. No durable disk state.

Dependencies and integration points: docker compose, gRPC v0 bdev API, NVMf target/initiator, nexus dynamic child management, bdev destruction path.

Risks and edge cases: global `OnceCell` compose/Mayastor instances and fixed names make test order important. Last scenario does not explicitly assert post-destroy nexus state; it mainly checks no panic/error through teardown.

Test signals: covers NVMf remote child add/remove lifecycle and interaction with remote bdev destruction.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_add_remove.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_child_location.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_child_location.rs

Purpose: verifies nexus children can report whether they are local or remote.

Important APIs/types/functions: uses compose to create/share a remote malloc bdev, then local `nexus_create`, `nexus_lookup_mut`, `children`, and `child.is_local()`.

Control flow: starts one remote Mayastor container, creates/shares remote `disk0`, starts local Mayastor, creates a two-child nexus with one local malloc URI and one remote NVMf URI, and asserts the first child is local while the second is not.

State and persistence: in-memory malloc devices and nexus state.

Dependencies and integration points: v0 bdev share API, NVMf URI handling, nexus child device locality detection.

Risks and edge cases: assumes child order matches URI order. Does not destroy nexus/container explicitly beyond compose drop behavior.

Test signals: targeted coverage for locality metadata used by scheduling/control-plane decisions.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_child_location.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_child_online.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_child_online.rs

Purpose: gRPC v1 integration test for offlining and onlining a nexus child replica, including state reason reporting after a no-space offline.

Important APIs/types/functions: `create_compose_test` starts two replica nodes and one nexus node. `create_test_storage` builds pools, thin replicas, shares them, creates and publishes a two-child nexus. Test uses `test_write_to_nexus`, `offline_child_replica_wait`, `online_child_replica_wait`, `offline_child_replica`, and `wait_replica_state` with `ChildState` and `ChildStateReason`.

Control flow: write a small amount of data to nexus, offline replica 0 and wait, online it and wait, offline it again, then wait for Degraded state with reason `NoSpace`.

State and persistence: compose containers with malloc-backed pools/replicas and published NVMf nexus. No durable state beyond container lifetime.

Dependencies and integration points: gRPC v1 pool/replica/nexus builders, NVMf sharing, child state transitions, wait/poll helpers.

Risks and edge cases: one-second waits are tight on slow systems. The `NoSpace` reason for offline operation is a specific control-plane/API mapping that could be surprising.

Test signals: covers online/offline child workflow and API state/reason propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_child_online.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_child_retire.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_child_retire.rs

Purpose: fault-injection tests for nexus child retirement when persistent-store updates succeed, stall, or time out. It ensures I/O acknowledgement is coupled to durable recording of child health.

Important APIs/types/functions: gated by `fault-injection`. Uses compose `TestCluster` with etcd and three Mayastor nodes, `TestStorage` with two shared replicas and one nexus, `NexusBuilder` fault injection helpers, direct `add_fault_injection`, `PersistentStoreBuilder`, `NexusInfo`, `nexus_lookup_mut`, `bdev_io::write_blocks`, `CoreError`, `IoCompletionStatus::NvmeError`, and `NvmeStatus`.

Control flow: `nexus_child_retire_persist_unresponsive_with_fio` injects a write completion fault on replica 0, pauses etcd, starts fio to the nexus, asserts I/O freezes while etcd is paused, thaws etcd, asserts I/O completes, then checks child states and etcd `NexusInfo` mark replica 0 unhealthy and replica 1 healthy. Ignored `nexus_child_retire_persist_unresponsive_with_bdev_io` performs the same idea with direct bdev I/O. `nexus_child_retire_persist_failure_with_bdev_io` pauses etcd long enough for persistent-store operations to time out, expects frozen I/O to fail with internal device error, waits for nexus shutdown, and checks child states. `init_ms_etcd_test` starts local etcd, connects persistent store with timeout/retries, creates AIO-backed pools/replicas and a loopback nexus; `deinit_ms_etcd_test` destroys resources.

State and persistence: etcd stores serialized `NexusInfo` under nexus name/UUID. Temporary disk files back local pools. Fault injection state is process-local. Tests intentionally manipulate etcd availability.

Dependencies and integration points: etcd binary/client, persistent store builder, fault-injection feature, fio, gRPC v1 builders, nexus retirement state machine, child health persistence, NVMf sharing, and direct bdev I/O.

Risks and edge cases: highly timing-sensitive and feature-gated. One test is ignored. Requires `ETCD_BIN`, container pause/thaw support, and persistent-store timeouts. Shared in-process `MayastorTest` and fixed names/paths can make cleanup important.

Test signals: critical correctness signal for not acknowledging writes until retired-child state is durably recorded, and for shutting down/failing I/O when persistence cannot be completed.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_child_retire.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_children_add_remove.rs -->
# sources/control-plane/mayastor/io-engine/tests/nexus_children_add_remove.rs

Purpose: tests local uring-backed nexus child add/remove policies and remote replica add/remove under active I/O and concurrent qpair handle conditions.

Important APIs/types/functions: local tests use `nexus_create`, `nexus_lookup_mut`, `share_nvmf`, `remove_child`, `add_child`, and `destroy`. Compose tests use gRPC v1 `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `test_fio_to_nexus`, and Fio builders. Constants define pool/replica/nexus sizes.

Control flow: `remove_children_from_nexus` creates a two-child uring nexus, shares it, removes one child, verifies removing the last child fails, adds back an unsynced child, verifies removing the last healthy child fails, then destroys. `nexus_add_child` creates a two-child nexus, shares it, adds a third uring child, and destroys. `nexus_remove_child_with_io` creates two remote replicas and a published nexus, removes one child after a delay while fio runs for 10 seconds, and expects both tasks to complete. `nexus_channel_get_handles` creates three replicas across two remote and one local-to-nexus pool, then loops 20 times concurrently adding replica 0 and removing replica 2, restores original state, and asserts two children, reproducing/guarding qpair async/sync connect races.

State and persistence: local temp files `/tmp/disk1.img`..`disk3.img`; compose malloc pools/replicas; published NVMf nexus state. No durable metadata beyond test lifetime.

Dependencies and integration points: uring bdev provider, NVMf sharing, nexus child policy, rebuild/unsync state, fio workload, gRPC v1 storage builders, qpair/connection handling.

Risks and edge cases: uring support and fixed temp files. Concurrent add/remove test has explicit sleeps and can be timing-sensitive. Local tests share one Mayastor instance on reactor mask `0x2`.

Test signals: strong coverage for preventing removal of last/last-healthy child, dynamic child changes while shared, child removal during live I/O, and qpair handle race regressions.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/nexus_children_add_remove.rs -->
