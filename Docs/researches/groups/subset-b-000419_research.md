# Research: subset-b-000419

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/replica_thin_no_space.rs -->
# sources/control-plane/mayastor/io-engine/tests/replica_thin_no_space.rs

Purpose: fault-injection-enabled Tokio integration tests for ENOSPC propagation from thin replicas. It verifies both real thin-pool exhaustion and injected NVMe `NO_SPACE` errors become fio-visible `ENOSPC`.

Important APIs/types/functions: `replica_thin_nospc` builds an io-engine container, malloc pool, thin 80 MiB replica on a 100 MiB backing pool, and a second thick filler replica. `replica_nospc_inject` uses `InjectionBuilder`, `FaultDomain::BdevIo`, `FaultIoStage::Submission`, and `NvmeStatus::NO_SPACE`. Both use `PoolBuilder`, `ReplicaBuilder`, `GrpcConnect`, `FioBuilder`, and `FioJobResult`.

Control flow: each test initializes composer, starts one io-engine, creates/shares a replica, opens the exported NVMe-oF target, runs a direct libaio write workload, then asserts the single fio job failed with `Errno::ENOSPC`.

State/persistence: all state is transient docker/malloc/SPDK state cleaned by the compose harness. The tests depend on thin allocation accounting and fault injection state inside io-engine during the run.

Dependencies/integration: integrates io-engine gRPC v1 helpers, the fault injection subsystem, SPDK NVMe status translation, NVMe-oF host connect helpers, and fio result parsing.

Risks: feature-gated by `fault-injection`; requires fio, NVMe-oF, and container networking. The real exhaustion case is sensitive to pool sizing and write pattern; the injection case is sensitive to matching device name `r0`.

Test signals: passing tests show ENOSPC survives both bdev submission injection and backend allocation failure all the way to host I/O.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/replica_thin_no_space.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/replica_timeout.rs -->
# sources/control-plane/mayastor/io-engine/tests/replica_timeout.rs

Purpose: ignored integration test for NVMe-oF child timeout/fault behavior when a replica container is suspended and later thawed.

Important APIs/types/functions: `replica_stop_cont` uses v0 gRPC bdev create/share RPCs, `Config::get_or_init` with short `NvmeBdevOpts`, `nexus_create`, `nexus_lookup_mut`, `UntypedBdev`, `bdev_get_name`, `NexusStatus`, and an external `initiator` binary.

Control flow: the test starts a replica io-engine container, creates/shares a malloc bdev, creates a local nexus with the remote child, pauses the replica container, submits a read expected to time out, waits past KATO, thaws the container, verifies subsequent read failure, then unshares a faulted nexus.

State/persistence: transient gRPC-created bdevs, one local nexus, and kernel/container pause state. Timeout configuration is applied globally through `Config`.

Dependencies/integration: covers docker-compose pause/thaw, SPDK NVMe bdev timeouts, nexus child faulting, the `initiator` binary, and NVMe-oF exported nexus access.

Risks: marked `#[ignore]` because it is timing-heavy and environment-dependent. It assumes fixed ports, localhost access, and reliable container suspension semantics.

Test signals: when run manually, success means a timed-out remote child is destroyed/faulted cleanly and a faulted nexus can still be unpublished.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/replica_timeout.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/replica_uri.rs -->
# sources/control-plane/mayastor/io-engine/tests/replica_uri.rs

Purpose: integration test ensuring replica share URIs carry a per-replica unique `uuid=` query parameter distinct from the volume UUID and usable in nexus children.

Important APIs/types/functions: `replica_uri` uses v0 Mayastor RPCs for pools, replicas, sharing, and nexus creation. Helpers `pool_name`, `get_bdev`, and `check_replica_uri` parse `Replica.uri` via `url::Url` and compare its `uuid` query value with the backing `Bdev.uuid`.

Control flow: two io-engine containers are started, pools are created, one replica is created shared over NVMe-oF and one local/loopback replica is created unshared then shared/unshared. Each URI is validated, then a nexus is created with both URIs.

State/persistence: transient pools, replicas, bdev UUIDs, and a nexus. The test asserts UUID identity state is exposed consistently through both replica and bdev listings.

Dependencies/integration: covers v0 gRPC API compatibility, replica URI formatting, bdev metadata, NVMe-oF sharing, and MOAC-style volume/nexus child addressing.

Risks: query parsing assumes `uuid=` exists and is the only query value used for the assertion. The fixed `VOLUME_UUID` is reused across two replicas, making the per-replica bdev UUID distinction critical.

Test signals: failure indicates URI generation no longer exposes unique replica identity or nexus child URI consumption regressed.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/replica_uri.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/reset.rs -->
# sources/control-plane/mayastor/io-engine/tests/reset.rs

Purpose: integration smoke test that a mirrored nexus bdev can be opened and reset successfully.

Important APIs/types/functions: `nexus_reset_mirror` uses compose v0 bdev create/share RPCs, `nexus_create`, `MayastorTest`, `MayastorCliArgs`, and `UntypedBdevHandle::open(...).reset()`.

Control flow: two io-engine containers create and share malloc bdevs over NVMe-oF. A local Mayastor instance creates a 50 MiB nexus over both child URIs, opens it for I/O, and awaits a reset.

State/persistence: transient child bdevs and one nexus; reset state is in SPDK bdev/nexus runtime only.

Dependencies/integration: covers remote NVMe-oF child setup, local nexus creation, bdev handle acquisition, and reset path propagation through mirrored children.

Risks: no post-reset I/O validation; success only means reset returned `Ok`. Requires NVMe-oF network setup and fixed malloc sizes.

Test signals: useful low-level signal for nexus reset path not panicking or returning immediate errors.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/reset.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/resource_stats.rs -->
# sources/control-plane/mayastor/io-engine/tests/resource_stats.rs

Purpose: integration test for v1 I/O statistics across pools, replicas, and a nexus with two remote children and one local child.

Important APIs/types/functions: `test_resource_stats` uses v1 `stats` RPCs, `reset_io_stats`, `get_pool_io_stats`, `get_replica_io_stats`, `get_nexus_io_stats`, `IoStats`, `ReplicaIoStats`, `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, and `test_fio_to_nexus`.

Control flow: three io-engine containers are started on separate core masks. Each creates a thick 60 MiB replica in an 80 MiB pool; the nexus node also hosts a local replica. After publishing a three-child nexus, all stats are reset and asserted zero. A 10 second random read/write fio run is issued through the nexus, then stats are fetched and cross-checked.

State/persistence: runtime counters on pools, replicas, and nexus are reset and then accumulated during fio. No persistent state survives compose cleanup.

Dependencies/integration: integrates stats gRPC service, fio workload generation, nexus read/write distribution, local and remote replica accounting, and latency tick aggregation.

Risks: random fio can be timing-sensitive. The test assumes mirrored writes give equal write op counts across children and that pool-level counters match replica counters exactly.

Test signals: validates nonzero write counts, read aggregation across replicas, write equality across mirrored replicas/pools, and latency ordering between pool, replica, and nexus layers.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/resource_stats.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/snapshot_lvol.rs -->
# sources/control-plane/mayastor/io-engine/tests/snapshot_lvol.rs

Purpose: broad local and gRPC-backed test suite for LVS logical-volume snapshots, clones, snapshot metadata, allocation accounting, deletion semantics, and restore data integrity.

Important APIs/types/functions: helpers include `get_ms`, `create_test_pool`, `find_snapshot_device`, `check_snapshot`, `check_clone`, `clean_snapshots`, `test_lvol_alloc_after_snapshot`, and `check_snapshot_descriptor`. Tests use `Lvs`, `Lvol`, `LvsLvol`, `LogicalVolume`, `LvolSnapshotOps`, `ISnapshotDescriptor`, `SnapshotParams`, `CloneParams`, `SnapshotXattrs`, `CloneXattrs`, `PoolArgs`, `PoolBackend`, `UntypedBdev`, `device_create/open`, and gRPC helper builders for replica snapshot/clone validation.

Control flow: early tests create malloc or aio-backed pools and lvols, create snapshots through either `Lvol` or a bdev handle, validate xattrs and UUIDs, and enumerate snapshots by lvol, pool, or all devices. Middle tests verify thick-to-thin transition after snapshot, cluster-aligned referenced size, clone creation/provenance, and snapshot listing after source destruction. Later tests cover snapshot attribute persistence across pool export/import, discarded snapshot behavior when clones exist, retry cleanup of pending discarded snapshots, data restore equivalence through snapshot clones, and usage recomputation after destroying snapshots, parents, clones, and clone snapshots.

State/persistence: most state is transient SPDK blobstore state. `test_snapshot_attr` uses `/tmp/disk1.img` and pool export/import to prove blob xattrs persist. Snapshot and clone metadata are stored as blob xattrs; allocation/usage state is derived from cluster ownership and snapshot ancestry.

Dependencies/integration: integrates local Mayastor reactor context, SPDK LVS blobstore, bdev I/O helpers, UUID and timestamp generation, gRPC v1 replica/snapshot builders, NVMe-oF write helpers, and replica comparison utilities.

Risks: long scenario file with shared global `OnceCell<MayastorTest>` means unique pool/device names are important. Several assertions rely on exact cluster sizes and SPDK allocation behavior. Discarded snapshot deletion is subtle because clone count, failed destroy paths, and retry cleanup must agree.

Test signals: passing tests indicate snapshot metadata correctness, list filters, clone provenance, persistent attrs, allocation accounting, discarded-snapshot lifecycle, and snapshot-clone restore data all work across local and exported paths.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/snapshot_lvol.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/snapshot_nexus.rs -->
# sources/control-plane/mayastor/io-engine/tests/snapshot_nexus.rs

Purpose: integration tests for remote replica snapshots created directly through handles, through nexus snapshot orchestration, and through gRPC list/query APIs.

Important APIs/types/functions: helpers `launch_instance`, `create_nexus`, `create_device`, `check_replica_snapshot`, and `check_nexus_snapshot_status` coordinate compose, remote replicas, local nexus objects, and snapshot metadata checks. Tests use v1 pool/replica/snapshot RPCs, `NexusReplicaSnapshotDescriptor`, `NexusCreateSnapshotReplicaDescriptor`, `NexusSnapshotStatus`, `SnapshotParams`, `ListSnapshotsRequest`, `ListReplicaOptions`, `CreateReplicaSnapshotRequest`, `CreateSnapshotCloneRequest`, and `DestroySnapshotRequest`.

Control flow: the suite starts a remote io-engine with two shared replicas, optionally creates local NVMe bdevs and nexuses, then creates snapshots via remote bdev handles or nexus orchestration. It validates empty listings, duplicate snapshot UUID/name status mapping, ancestor/referenced-byte accounting after nexus writes and multiple snapshots, discarded snapshot list filters after clone/destroy, replica list filters for replica/snapshot/clone combinations, and multi-replica nexus snapshot request validation.

State/persistence: pools, replicas, snapshots, clones, and nexus objects are transient but distributed between a remote io-engine and local Mayastor context. Snapshot usage counters persist in replica metadata while NVMe-oF host devices and connections are explicitly connected/disconnected.

Dependencies/integration: covers compose networking, gRPC v1 services, NVMe-oF host discovery, SPDK nexus snapshot fan-out, errno status conversion, query filter semantics, and replica usage reporting.

Risks: relies on fixed NQNs, localhost NVMe-oF connects, exact snapshot ordering logic, and timeout options. Duplicate and multi-replica paths are especially sensitive to request validation and per-replica status contracts.

Test signals: passing tests show nexus snapshot fan-out, remote snapshot metadata, duplicate handling, usage/referenced-byte accounting, clone/discard filters, and multi-replica validation remain compatible.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/snapshot_nexus.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/snapshot_rebuild.rs -->
# sources/control-plane/mayastor/io-engine/tests/snapshot_rebuild.rs

Purpose: local tests for rebuilding from snapshots or snapshot-like source devices into malloc devices and LVS replicas.

Important APIs/types/functions: uses `SnapshotRebuildJob::builder`, `RebuildJobOptions`, `ReadOptions`, `RebuildState`, `device_create`, `device_destroy`, `LvsLvol`, `PoolBuilderLocal`, and helper functions `create_replica`, `destroy_replica`, and `mb_to_blocks`.

Control flow: each test runs in Mayastor context. `malloc_to_malloc` rebuilds one malloc bdev into another and verifies full block transfer. `malloc_to_replica` rebuilds malloc source into a replica by destination UUID. `replica_to_rebuild_full` disables partial reads and expects full transfer. `replica_to_rebuild_partial` uses default read options and expects only the 8 MiB initially written/zeroed region to transfer.

State/persistence: transient malloc devices, local LVS pool, replicas, and rebuild job registry state. Jobs are `.store()`d for lookup and explicitly destroyed after completion.

Dependencies/integration: exercises rebuild job creation, lookup by name/replica UUID, async completion channel, statistics reporting, and logical-volume share URI use as snapshot source.

Risks: exact `blocks_transferred` expectations depend on block size, replica initialization/write-zero behavior, and partial rebuild semantics. Cleanup must destroy replicas/devices/jobs even after failure.

Test signals: passing tests prove snapshot rebuild succeeds across malloc and replica destinations and that full versus partial read options affect transferred block counts correctly.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/snapshot_rebuild.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/thread.rs -->
# sources/control-plane/mayastor/io-engine/tests/thread.rs

Purpose: concurrency/runtime test verifying transitions between Mayastor reactor threads, Tokio runtime tasks, blocking tasks, and primary reactor dispatch.

Important APIs/types/functions: `mayastor_to_runtime`, `runtime_to_mayastor`, `running_on_thread`, and `thread_tokio` use `Cores`, `Mthread`, `Reactor::spawn_at_primary`, `runtime::spawn`, `runtime::spawn_blocking`, `bdev_create`, and `UntypedBdev::share_nvmf`.

Control flow: a Mayastor instance starts with reactor mask `0x3`. A malloc bdev is created on the primary reactor. A future sent from Mayastor asserts it is on the first core with an SPDK thread, spawns onto Tokio, asserts it has no Mayastor core/thread, sleeps, then dispatches back to the primary reactor to share the bdev. A blocking task asserts it also has no Mayastor core/thread.

State/persistence: transient bdev `malloc0` and runtime thread-local core/thread state.

Dependencies/integration: validates Mayastor runtime helpers, Tokio scheduling, SPDK thread affinity, and bdev sharing from cross-runtime callbacks.

Risks: timing is simple but thread-local assertions are brittle if runtime identity semantics change. The test assumes `malloc0` is created before the reactor callback uses it.

Test signals: passing test shows safe cross-runtime dispatch and correct absence/presence of SPDK thread context in each execution domain.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/thread.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/wipe.rs -->
# sources/control-plane/mayastor/io-engine/tests/wipe.rs

Purpose: v1 test-service integration test for streamed replica wipe progress, chunk validation, and write-zero data effects.

Important APIs/types/functions: `replica_wipe` drives scenarios through `issue_wipe_replica`, `collect_stream`, `validate_wipe_replica`, `wipe_replica`, `create_pool_replica`, and `nvme_device`. It uses `WipeMethod`, `WipeReplicaRequest`, `StreamWipeOptions`, `WipeReplicaResponse`, `NmveConnectGuard`, `dd_urandom_blkdev`, and `compare_devices`.

Control flow: a containerized io-engine creates a 1 GiB thick replica. Multiple `WipeMethod::None` cases validate streamed notification counts, chunk sizing, last chunk sizing after GPT backup exclusion, invalid non-512-aligned chunks, and too-many-chunk errors. The test then recreates a small NVMe-oF-shared replica, writes random data, performs no-op and write-zero wipes, and compares the connected block device against `/dev/zero`.

State/persistence: transient pool/replica state and host NVMe device contents. The test mutates `replica.size` locally to account for reserved GPT backup bytes before expected-progress calculations.

Dependencies/integration: covers v1 test gRPC streaming, replica builder helpers, NVMe-oF connect/list utilities, host block-device comparison, and wipe implementation chunk accounting.

Risks: depends on host NVMe discovery returning exactly one Mayastor device and on `/tmp` bind mount/container privileges. Progress formulas are sensitive to GPT backup size and 512-byte alignment rules.

Test signals: passing test confirms streamed wipe responses are internally consistent and `WriteZeroes` actually clears device data while `None` does not.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/tests/wipe.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/jsonrpc/Cargo.toml -->
# sources/control-plane/mayastor/jsonrpc/Cargo.toml

Purpose: crate manifest for the `jsonrpc` Rust library, version `1.0.0`, edition 2018.

Important APIs/types/functions: declares dependencies on workspace `nix`, `serde`, `serde_json`, `tonic`, `tokio` with `full` features, and `tracing`.

Control flow: no runtime flow; Cargo uses it to compile the JSON-RPC Unix-socket client and tests.

State/persistence: none directly. Dependency choices determine async socket behavior, serialization, errno mapping, and gRPC status conversion.

Dependencies/integration: integrated into the Mayastor workspace as a library crate that can bridge JSON-RPC errors to tonic status codes.

Risks: Tokio `full` expands dependency surface. Edition 2018 and crate version should stay aligned with workspace expectations.

Test signals: `scripts/cargo-test.sh` runs `cargo test` in this crate, covering manifest resolution and unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/jsonrpc/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/jsonrpc/src/error.rs -->
# sources/control-plane/mayastor/jsonrpc/src/error.rs

Purpose: error model for JSON-RPC client requests and response parsing, including conversion to tonic gRPC status.

Important APIs/types/functions: `RpcCode` enumerates parse/invalid/method/internal plus `NotFound` and `AlreadyExists`. `Error` covers invalid JSON-RPC version/id, I/O, parse, connect, RPC error, and generic string errors. `From<RpcCode> for Code`, `From<Error> for tonic::Status`, `Display`, `std::error::Error`, and `From` conversions for `io::Error`, `serde_json::Error`, `&str`, and `String` are implemented.

Control flow: conversion maps `InvalidParams` to `InvalidArgument`, `NotFound` to `NotFound`, `AlreadyExists` to `AlreadyExists`, and most other RPC codes to `Internal`. Non-RPC client errors become tonic internal statuses with formatted messages.

State/persistence: no persistent state; error values carry messages and source errors.

Dependencies/integration: used by `jsonrpc::call`/`parse_reply` and by higher layers that expose JSON-RPC failures over tonic.

Risks: `std::error::Error::cause` is legacy and always returns `None`, so source chains are not exposed. `ConnectError` is defined but the current client maps Unix connect errors through `IoError`.

Test signals: unit tests in `src/test.rs` cover parse errors, invalid version/id, connect errors, and JSON-RPC errno mapping.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/jsonrpc/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/jsonrpc/src/lib.rs -->
# sources/control-plane/mayastor/jsonrpc/src/lib.rs

Purpose: async JSON-RPC 2.0 client over Unix domain sockets.

Important APIs/types/functions: public `Request`, `Response`, and `RpcError` structs are serde-serializable/deserializable. `call<A, R>` builds request id `0`, serializes optional params, connects via `tokio::net::UnixStream`, writes and shuts down the socket, reads the full response, and delegates to private `parse_reply<T>`.

Control flow: `parse_reply` deserializes `Response`, accepts missing `jsonrpc` but rejects non-`2.0`, requires numeric id `0`, maps JSON-RPC standard negative codes and negative errno values to `RpcCode`, returns `Error::RpcError` when `error` is present, otherwise deserializes `result` or JSON null into `T`.

State/persistence: no long-lived state; each call opens one Unix socket connection and consumes one complete request/response exchange.

Dependencies/integration: depends on Tokio async I/O, serde JSON, nix errno mapping, tracing logs, and the local `error` module.

Risks: fixed request id `0` prevents multiplexing and assumes one in-flight request per socket. Missing `jsonrpc` is accepted for compatibility. `reply.result.unwrap_or(Null)` can turn absent result into unit success but will parse-error for non-unit expected types.

Test signals: tests exercise normal reply, invalid JSON, missing/wrong version, wrong id, empty result behavior, connect failure, and RPC error conversion.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/jsonrpc/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/jsonrpc/src/test.rs -->
# sources/control-plane/mayastor/jsonrpc/src/test.rs

Purpose: unit tests for the JSON-RPC Unix-socket client.

Important APIs/types/functions: `run_test` starts a per-thread Unix listener, invokes `call`, and runs assertion callbacks under `panic::catch_unwind`. Tests define `EmptyArgs`, request handlers returning raw JSON bytes, and result assertions for several `Result<R, Error>` types.

Control flow: each async test binds `/tmp/jsonrpc-ut.sock.<thread-id>`, spawns a one-shot server that reads the request, deserializes `Request`, writes handler output, then the client call is awaited and checked. Cleanup removes the socket after callback execution.

State/persistence: temporary Unix socket path under `/tmp`; no persistent test state. Per-thread suffix mitigates Rust parallel-test collisions.

Dependencies/integration: covers Tokio UnixListener/UnixStream behavior, serde request/response encoding, `nix::Errno`, and the crate error model.

Risks: `panic::UnwindSafe` is manually implemented for `Error`; server task panics would surface indirectly. `connect_error` uses a runtime manually and expects `ErrorKind::NotFound`.

Test signals: validates happy-path inversion, parse failures, invalid/missing version, wrong id, unit-result handling, and `ENOENT` to `RpcCode::NotFound`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/jsonrpc/src/test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/libnvme-rs/Cargo.toml -->
# sources/control-plane/mayastor/libnvme-rs/Cargo.toml

Purpose: crate manifest for `libnvme-rs`, Rust bindings and safe-ish wrappers around Linux `libnvme`.

Important APIs/types/functions: package metadata sets build script `build.rs`, Apache-2.0 license, edition 2018, and dependencies on `glob`, `libc`, `snafu`, `url`, `mio` with `os-ext`, `udev` with `hwdb`/`mio`, and `uuid` v4. Build dependencies are `bindgen` and `cc`.

Control flow: Cargo invokes bindgen at build time and links against system `libnvme`.

State/persistence: no direct runtime state; dependency set enables NVMe host config reads, udev monitoring, and generated FFI.

Dependencies/integration: consumed by tests/tools needing NVMe-oF connect/disconnect and device enumeration without shelling out to `nvme`.

Risks: tightly coupled to installed libnvme headers/library ABI. Workspace dependency changes can affect generated bindings.

Test signals: build success proves headers and library are available; `nvme_parse_uri` covers URI parsing.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/libnvme-rs/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/libnvme-rs/build.rs -->
# sources/control-plane/mayastor/libnvme-rs/build.rs

Purpose: build script that generates Rust FFI bindings for libnvme.

Important APIs/types/functions: `main` emits `cargo:rustc-link-lib=nvme`, rerun tracking for `wrapper.h`, configures `bindgen::Builder` with `wrapper.h`, `CargoCallbacks`, disabled layout tests, and writes `bindings.rs` into `OUT_DIR`.

Control flow: build fails if bindgen cannot parse headers or cannot write generated bindings.

State/persistence: generated bindings live under Cargo build output, not source control.

Dependencies/integration: integrates Cargo, bindgen, clang header parsing, and system libnvme linking.

Risks: generated API varies with installed libnvme version. Disabled layout tests avoid target-specific failures but reduce ABI safety checks.

Test signals: any crate compile requires successful binding generation and linking.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/libnvme-rs/build.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/libnvme-rs/src/error.rs -->
# sources/control-plane/mayastor/libnvme-rs/src/error.rs

Purpose: typed error enum for libnvme wrapper operations.

Important APIs/types/functions: `NvmeError` derives `Snafu` and includes `IoError`, `LookupHostError`, `CreateCtrlrError`, `AddCtrlrError`, `FileIoError`, and `UrlError`. `From<std::io::Error>` maps I/O failures into `IoError`.

Control flow: wrapper functions construct variants with libnvme return codes or URL parse errors and return `Result<_, NvmeError>`.

State/persistence: carries return codes and source errors only.

Dependencies/integration: used by `NvmeTarget` connect/disconnect/list parsing paths and exposes failure reasons to callers.

Risks: display strings for some variants omit the source value text after `IO error:`. Return code sign conventions vary by libnvme call and need caller interpretation.

Test signals: URI parse tests indirectly exercise `UrlError`; runtime NVMe tests would exercise libnvme return-code variants.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/libnvme-rs/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/libnvme-rs/src/lib.rs -->
# sources/control-plane/mayastor/libnvme-rs/src/lib.rs

Purpose: crate root exposing generated libnvme bindings plus wrapper modules.

Important APIs/types/functions: includes generated `bindings.rs` from `OUT_DIR` under a clippy-allowed module, re-exports all generated symbols, declares `error`, `nvme_device`, private `nvme_tree`, and private `nvme_uri`, and publicly re-exports `NvmeDevice` and `NvmeTarget`.

Control flow: no runtime flow except compile-time include of generated bindings.

State/persistence: none directly; generated bindings mirror system libnvme stateful APIs.

Dependencies/integration: central integration point for downstream crates to access both raw FFI and higher-level wrapper types.

Risks: public `pub use bindings::*` exposes unsafe C API broadly, so consumers can bypass wrapper invariants. Generated symbol set depends on host libnvme.

Test signals: crate build verifies bindgen output is available and wrapper modules compile.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/libnvme-rs/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/libnvme-rs/src/nvme_device.rs -->
# sources/control-plane/mayastor/libnvme-rs/src/nvme_device.rs

Purpose: plain Rust data model for an NVMe namespace/block device discovered through libnvme.

Important APIs/types/functions: `NvmeDevice` has `namespace`, `device`, `firmware`, `model`, `serial`, `utilisation`, `max_lba`, `capacity`, and `sector_size`, and derives `Clone` and `Debug`.

Control flow: none; instances are constructed by `NvmeTarget::get_device_from_ns`.

State/persistence: snapshot of kernel/libnvme namespace metadata at discovery time.

Dependencies/integration: returned by `NvmeTarget::list` and likely consumed by tests that need to find Mayastor NVMe devices.

Risks: fields are public and unvalidated; `device` is a name such as `nvme0n1` rather than an absolute path.

Test signals: enumeration tests should check capacity/sector size and device naming against actual kernel devices.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/libnvme-rs/src/nvme_device.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/libnvme-rs/src/nvme_tree.rs -->
# sources/control-plane/mayastor/libnvme-rs/src/nvme_tree.rs

Purpose: RAII and iterator adapters over libnvme's scanned topology tree.

Important APIs/types/functions: `NvmeRoot` owns `*mut nvme_root` and frees it in `Drop`. Iterators `NvmeHostIterator`, `NvmeSubsystemIterator`, `NvmeCtrlrIterator`, `NvmeNamespaceIterator`, and `NvmeNamespaceInCtrlrIterator` wrap libnvme `first`/`next` traversal functions.

Control flow: each iterator stores the current raw pointer; `next` calls the relevant first function when null, otherwise next function, returning `None` on null.

State/persistence: owns a libnvme tree snapshot for the lifetime of `NvmeRoot`; child pointers are valid only while the root/tree remains alive.

Dependencies/integration: used by `nvme_uri.rs` for block device discovery, disconnect, and listing.

Risks: raw pointers and lifetimes are only partially encoded. Iterators other than host do not tie their lifetime to `NvmeRoot`, so misuse outside current module patterns could access freed tree memory.

Test signals: device list/disconnect tests exercise traversal across hosts, subsystems, controllers, and namespaces.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/libnvme-rs/src/nvme_tree.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/libnvme-rs/src/nvme_uri.rs -->
# sources/control-plane/mayastor/libnvme-rs/src/nvme_uri.rs

Purpose: higher-level NVMe-oF target wrapper for parsing target URIs, connecting/disconnecting through libnvme, discovering block devices, and monitoring udev events.

Important APIs/types/functions: `NvmeStringWrapper` frees libnvme-allocated C strings. `NvmeTransportType` supports TCP and RDMA. `NvmeTarget` stores target address, port, subsystem NQN, transport, and hostnqn autogen flag. Methods include `TryFrom<&str/String>`, `with_rand_hostnqn`, `connect`, `block_devices`, `disconnect`, `list`, `start_poll`, `poll`, `handle_event`, and `Drop`.

Control flow: URI parsing accepts `nvmf`/`nvmf+tcp` as TCP and `nvmf+rdma+tcp` as RDMA, defaulting port to 4420. `connect` scans/creates a libnvme root, reads or generates host identity, creates a controller, and calls `nvmf_add_ctrl`. `block_devices` repeatedly scans until namespaces for the target NQN are found or retries expire. `disconnect` scans matching subsystems and disconnects each controller. `list` collects namespace metadata from subsystem and controller namespace iterators.

State/persistence: modifies kernel NVMe controller state on connect/disconnect. `Drop` attempts disconnect on target destruction. Host identity may come from `/etc/nvme` or generated UUID/NQN.

Dependencies/integration: uses generated libnvme bindings, libc free, mio/udev polling, URL parsing, UUID generation, and internal tree iterators/device model.

Risks: many `unsafe` C calls and `unwrap()` conversions can panic on unexpected null/non-UTF8 metadata. Drop-side disconnect may surprise callers if multiple users share a controller. Udev polling currently has only a FIXME callback. RDMA scheme spelling looks unusual and should be validated against callers.

Test signals: `nvme_parse_uri` validates TCP URI parsing. Runtime tests should cover connect/list/disconnect, hostnqn autogen, retry behavior, and nonmatching NQN filtering.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/libnvme-rs/src/nvme_uri.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/libnvme-rs/wrapper.h -->
# sources/control-plane/mayastor/libnvme-rs/wrapper.h

Purpose: minimal C header used by bindgen to expose libnvme declarations.

Important APIs/types/functions: includes `<stddef.h>` and `<libnvme.h>`.

Control flow: no runtime behavior.

State/persistence: none; controls generated binding surface.

Dependencies/integration: consumed by `build.rs`; changes trigger Cargo rebuild through `rerun-if-changed`.

Risks: broad include exposes the full installed libnvme API, which may vary by distro/package version.

Test signals: binding generation and crate compilation fail quickly if the header or libnvme development package is missing.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/libnvme-rs/wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/nix/pkgs/ms-buildenv/root/etc/group -->
# sources/control-plane/mayastor/nix/pkgs/ms-buildenv/root/etc/group

Purpose: static group database for the Mayastor Nix build environment root filesystem.

Important APIs/types/functions: defines `root`, `wheel`, `tty`, `users`, `nixbld` with builders `nixbld1` through `nixbld30`, and `nogroup`.

Control flow: no executable flow; libc/NSS group lookup reads it.

State/persistence: persistent image configuration for build users and group IDs.

Dependencies/integration: works with the buildenv passwd/shadow files and `nsswitch.conf` to support multi-user Nix builds.

Risks: group IDs and builder membership must match Nix daemon expectations. Missing builder users in passwd would break group membership usefulness.

Test signals: Nix builds in the image should be able to use all configured `nixbld` users.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/nix/pkgs/ms-buildenv/root/etc/group -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/nix/pkgs/ms-buildenv/root/etc/nsswitch.conf -->
# sources/control-plane/mayastor/nix/pkgs/ms-buildenv/root/etc/nsswitch.conf

Purpose: NSS lookup policy for the Mayastor build environment.

Important APIs/types/functions: configures `passwd` and `group` lookup through `files mymachines systemd`, `shadow` through `files`, `hosts` through `files mymachines dns myhostname`, and local files for networks/ethers/services/protocols/rpc.

Control flow: no script flow; glibc NSS uses the listed lookup order.

State/persistence: persistent rootfs configuration that affects name resolution and user/group lookup.

Dependencies/integration: supports local `/etc` files, systemd container users, and DNS resolution inside build/test environments.

Risks: DNS resolution depends on the runtime image having matching NSS modules. Lookup ordering can affect container hostnames and systemd-managed identities.

Test signals: build shell should resolve local users/groups and DNS hostnames without NSS errors.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/nix/pkgs/ms-buildenv/root/etc/nsswitch.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/block_devs.sh -->
# sources/control-plane/mayastor/scripts/block_devs.sh

Purpose: helper script creating eight 1 GiB file-backed NVMe target namespaces on localhost.

Important APIs/types/functions: uses `truncate`, `modprobe nvmet_tcp`, configfs paths under `/sys/kernel/config/nvmet`, subsystem names `replica0` through `replica7`, namespace `device_path`, `enable`, and port subsystem symlinks.

Control flow: creates `/tmp/<n>.blk` files, configures NVMe TCP port 1 at `127.0.0.1:4420`, then loops creating subsystems/namespaces and linking them into the port.

State/persistence: mutates `/tmp`, loads kernel module, and writes persistent-until-reboot configfs NVMe target state.

Dependencies/integration: useful for local NVMe-oF testing outside io-engine. Requires root privileges and Linux nvmet configfs.

Risks: not idempotent; existing configfs entries cause failures. No cleanup path. Fixed port and paths can conflict with other tests.

Test signals: after running, `nvme discover/connect` against localhost should see the eight replicas.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/block_devs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/cargo-test.sh -->
# sources/control-plane/mayastor/scripts/cargo-test.sh

Purpose: CI/developer wrapper for Rust cargo tests and io-engine integration tests.

Important APIs/types/functions: defines `cleanup_handler`, invokes `clean-cargo-tests.sh`, prints `rustc --version`, extends `PATH`, checks `rdma_rxe`/`nvme_rdma` modules, validates NVMe config via `nvme-conf.sh --check`, runs `cargo test` in `jsonrpc`, builds bins with `io-engine-testing`, and runs `io-engine` tests single-threaded.

Control flow: cleanup runs before and after via trap. With `set -euo pipefail`, missing NVMe config exits early after warning.

State/persistence: cleans stale test devices/containers before and after; builds target artifacts and may leave cargo cache.

Dependencies/integration: integrates Rust toolchain, kernel modules, NVMe host config, cleanup script, and test feature flags.

Risks: cleanup at script start can remove active test resources if run concurrently. It exits on invalid NVMe config even though warning text says "may not be valid".

Test signals: successful completion is the main Rust CI gate for jsonrpc and io-engine integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/cargo-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/check-coredumps.sh -->
# sources/control-plane/mayastor/scripts/check-coredumps.sh

Purpose: CI diagnostic script that reports and fails on new system coredumps.

Important APIs/types/functions: parses `--since DATE`, requires `coredumpctl`, `gdb`, and `jq`, lists coredumps, filters out `sshd` and `udisksd`, and runs `thread apply all bt` in coredump gdb sessions.

Control flow: default since date is very old. For each matching PID from JSON output, it increments a count and attempts a backtrace, tolerating missing core files. Nonzero count exits `1`.

State/persistence: reads systemd coredump journal/storage; writes only stdout/stderr diagnostics.

Dependencies/integration: used by CI after tests to catch crashes not reflected in test exit codes.

Risks: depends on systemd coredump availability and jq despite jq not being preflight-checked. Date parsing is delegated to coredumpctl.

Test signals: no coredumps produces exit `0`; any relevant coredump produces backtraces and exit `1`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/check-coredumps.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/check-submodule-branches.sh -->
# sources/control-plane/mayastor/scripts/check-submodule-branches.sh

Purpose: verifies submodule HEADs are contained in the branch configured in `.gitmodules`.

Important APIs/types/functions: `submodule_check` iterates `git config --file .gitmodules --get-regexp path`, reads `submodule.<path>.branch`, and checks `git branch -r --contains HEAD` for `origin/<branch>`.

Control flow: enters repo root, loops submodules with file-style `.git`, records any failure, and exits `1` if at least one submodule is off-branch.

State/persistence: read-only git state.

Dependencies/integration: CI/release guard for submodule branch hygiene.

Risks: skips submodules whose `.git` is a directory rather than file. Unquoted variables can break on paths with spaces, though submodule paths likely do not contain spaces.

Test signals: clean exit means every initialized submodule HEAD is reachable from its configured remote branch.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/check-submodule-branches.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/ci-report.sh -->
# sources/control-plane/mayastor/scripts/ci-report.sh

Purpose: gathers system diagnostics into a compressed CI report bundle.

Important APIs/types/functions: sets `ROOT_DIR`, chooses `nix-sudo` or `sudo`, uses `CI_REPORT_START_DATE`, writes `journalctl.txt`, `dmesg.txt`, `lsblk.txt`, `nvme.txt`, `meminfo.txt`, masks GitHub tokens matching `ghs_...`, and creates `ci-report.tar.gz`.

Control flow: creates `ci-report` directory, collects logs and hardware state, then tars `.txt` and `.xml` files found in that directory.

State/persistence: writes/overwrites files under `ci-report`.

Dependencies/integration: used by CI for post-failure artifacts; integrates journalctl, lsblk, nvme-cli, sudo/nix-sudo, and tar.

Risks: token masking is narrow and may not catch all secrets. It appends `nvme list-subsys` output to the same file and assumes sudo access.

Test signals: generated tarball should contain recent logs and NVMe/block-device state.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/ci-report.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/clean-cargo-tests.sh -->
# sources/control-plane/mayastor/scripts/clean-cargo-tests.sh

Purpose: aggressive cleanup script for resources left by io-engine cargo/integration tests.

Important APIs/types/functions: requires `nix-sudo`, disconnects all NVMe controllers, removes ublk devices backed by `/tmp/io-engine-tests/`, removes loop devices and LVM metadata, deletes soft RDMA link `io-engine-rxe0`, kills/removes docker containers and networks labeled by composer, kills target-directory processes, and removes `/var/run/dpdk/*`.

Control flow: scans ublk and loop devices, performs best-effort cleanup with many tolerated failures, restarts docker if network removal fails, and exits `0`.

State/persistence: mutates host kernel devices, docker state, LVM metadata, DPDK runtime files, and `/tmp/io-engine-tests`.

Dependencies/integration: central cleanup hook for cargo/grpc test scripts; depends on jq, losetup, ublk, LVM tools, docker, rdma, and sudo/nix-sudo.

Risks: intentionally destructive for test resources and uses broad process killing under `$ROOT_DIR/target`. Concurrent tests can be disrupted.

Test signals: after running, stale NVMe, ublk, loop, docker, DPDK, and composer resources should be gone.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/clean-cargo-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/e2e_check_pod_restarts.sh -->
# sources/control-plane/mayastor/scripts/e2e_check_pod_restarts.sh

Purpose: simple Kubernetes e2e guard that fails when Mayastor or MOAC pods restarted.

Important APIs/types/functions: runs `kubectl get pods -n mayastor`, filters names containing `mayastor` or `moac`, extracts column 4 restart counts, and exits `255` after dumping pods if any count is nonzero.

Control flow: linear shell loop over restart counts.

State/persistence: read-only Kubernetes API access.

Dependencies/integration: used after e2e tests to catch restarts/crashes in the Mayastor namespace.

Risks: parses human table output and assumes the restart column remains fourth. Grep may match unrelated pod names containing those strings.

Test signals: exit `0` means no matching pod reported restarts.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/e2e_check_pod_restarts.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/generate-deploy-yamls.sh -->
# sources/control-plane/mayastor/scripts/generate-deploy-yamls.sh

Purpose: Helm wrapper for generating Mayastor deployment YAMLs with profile-specific defaults.

Important APIs/types/functions: supports options for cores, output dir, pool node/device pairs, registry, tag, helm `--set`, helm values files, and namespace. Profiles `develop`, `release`, and `test` set defaults for CPU count, image tag, pull policy, huge pages, and MOAC debug.

Control flow: parses options, validates profile and helm availability, prepares a temp directory, builds comma-separated Helm values, updates chart dependencies, runs `helm template`, moves Mayastor templates into deploy output, moves Bitnami etcd templates into `deploy/etcd`, and trims trailing whitespace.

State/persistence: overwrites generated YAML output directories; temporary files are removed by trap.

Dependencies/integration: integrates repository Helm chart, profile values files, generated deploy directory, and optional pool placement values.

Risks: `--set "$helm_string"` and `-f "$helm_file"` are passed even when empty, depending on helm tolerance. Pool parsing is comma-based and unquoted namespace may break on unusual values.

Test signals: generated YAMLs under deploy and deploy/etcd should be valid Kubernetes manifests for the selected profile.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/generate-deploy-yamls.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/grpc-test.sh -->
# sources/control-plane/mayastor/scripts/grpc-test.sh

Purpose: CI wrapper for JavaScript gRPC integration tests.

Important APIs/types/functions: cleanup handler invokes `clean-cargo-tests.sh`; builds Rust bins with `io-engine-testing`; enters `test/grpc`, runs `npm install --legacy-peer-deps`, kills existing `io-engine`, validates NVMe config, and runs mocha suites `cli`, `replica`, `nexus`, and `rebuild` with `multi_reporter.js`.

Control flow: cleanup runs before and after via traps. Each suite emits both xunit and spec output with per-suite XML reports.

State/persistence: installs node dependencies, builds cargo artifacts, kills processes, cleans host resources, and writes xunit XML reports.

Dependencies/integration: integrates Rust binaries, Node/mocha tests, custom reporter, NVMe config, and cleanup script.

Risks: `sudo pkill io-engine` and cleanup are broad. `npm install` during test runs can be slow/flaky and network-dependent if cache is cold.

Test signals: passing script means legacy JS gRPC suites pass and xunit reports were generated.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/grpc-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/js-check.sh -->
# sources/control-plane/mayastor/scripts/js-check.sh

Purpose: semistandard formatter/linter wrapper for gRPC JavaScript test files.

Important APIs/types/functions: filters incoming paths to those under `test/grpc/`, strips the prefix, and runs `npx semistandard --fix` in the test/grpc directory.

Control flow: loops arguments, accumulates relative grpc test paths, and only invokes semistandard if any are found.

State/persistence: modifies matching JS files in place because `--fix` is enabled.

Dependencies/integration: likely used by pre-commit/CI formatting workflows for JS tests.

Risks: unquoted variables and backticks can mishandle spaces. Auto-fixing in a check script can dirty the worktree unexpectedly.

Test signals: after running, selected gRPC JS tests should satisfy semistandard style.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/js-check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/nix-sudo/nix-sudo -->
# sources/control-plane/mayastor/scripts/nix-sudo/nix-sudo

Purpose: wrapper that runs commands under `sudo -E` while resolving the first non-option argument to its Nix-shell binary path.

Important APIs/types/functions: builds `CMD` by escaping backslashes and quotes, treats `*=*` and `-*` arguments as pre-binary flags/env assignments, resolves the command with `which`, then executes `bash -c "sudo -E $CMD"`.

Control flow: iterates all args, shifts as it consumes them, preserves options before the command, and quotes all accumulated arguments.

State/persistence: no direct state; executes privileged commands preserving environment.

Dependencies/integration: used by cleanup/report scripts so sudo can find Nix-provided tools.

Risks: hand-built shell quoting is security-sensitive. If the command cannot be resolved by `which`, `BIN` may become empty and execution will fail oddly.

Test signals: commands like `nix-sudo nvme list` should run the Nix-shell `nvme` binary via sudo.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/nix-sudo/nix-sudo -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/nvme-conf.sh -->
# sources/control-plane/mayastor/scripts/nvme-conf.sh

Purpose: validates and optionally writes NVMe host identity files under the NVMe sysconf directory.

Important APIs/types/functions: defaults to `/etc/nvme`, fixed hostid `03f79caf-dc58-475a-a111-bf0b75214a51`, and matching hostnqn. Options include `--apply`, `--check`, `--overwrite`, `--hostid`, `--hostnqn`, `--sysconfdir`, and help.

Control flow: parses args, reads existing `hostid` and `hostnqn`, prints current/requested state, exits success on valid/matching config, exits failure if check fails without apply, enforces overwrite for existing files, creates directory/files when allowed, checks write permissions, and writes requested values.

State/persistence: mutates `/etc/nvme/hostid` and `/etc/nvme/hostnqn` or an alternate sysconfdir.

Dependencies/integration: used by cargo, grpc, and pytest wrappers to ensure stable NVMe host identity for tests.

Risks: apparent bug checks `-f "$NVME_SYSCONFDIR_HOSTID_P"` before reading hostnqn, so hostnqn detection depends on hostid file existence. Missing quote in one permission error message. Requires elevated permissions for default path.

Test signals: `--check` returning `0` indicates nonempty hostid and hostnqn are present.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/nvme-conf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/pytest-tests.sh -->
# sources/control-plane/mayastor/scripts/pytest-tests.sh

Purpose: orchestrates Python docker-compose pytest suites and report generation.

Important APIs/types/functions: requires `SRCDIR`, creates `test/python/reports`, activates `test/python/venv`, defines `cleanup_handler`, `trap_setup`, `clean_all`, `is_test`, and `run_tests`. Supports `--clean-all`, `--clean-all-exit`, direct test paths/selectors, and pass-through pytest args.

Control flow: validates environment and NVMe config, cleans reports, resolves arguments to tests or extra args, installs traps, then runs selected tests or a built-in suite list with `python -m pytest --tc-file test_config.ini --docker-compose=... --junit-xml=...`.

State/persistence: removes/recreates reports, tears down docker-compose clusters, and writes junit XML under reports.

Dependencies/integration: integrates Python virtualenv, pytest, pytest-docker-compose config, NVMe host config, and many Mayastor test suites.

Risks: `clean_all` scans from current directory after `cd "$SRCDIR/test/python"` and can affect all compose tests. Argument parsing with `realpath $1` is unquoted. Duplicate `tests/cli_controller` appears in the default list.

Test signals: per-suite XML reports and exit status provide Python e2e regression signals.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/pytest-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/reclaim-space.sh -->
# sources/control-plane/mayastor/scripts/reclaim-space.sh

Purpose: frees root filesystem space by running Nix and Docker garbage collection when available space is below a requested threshold.

Important APIs/types/functions: expects first argument `MIN_FREE_GIB`, defines `get_avail_gib` using `df --output=avail /`, runs `nix-collect-garbage` and `docker image prune --force --all`.

Control flow: prints current free GiB, exits early if above threshold, otherwise enables shell tracing for cleanup commands and prints free space afterward.

State/persistence: deletes unreferenced Nix store paths and all unused Docker images.

Dependencies/integration: CI maintenance helper for disk pressure before large builds/tests.

Risks: `$1` is read under `set -e` without default, so calling with no argument fails. Docker prune all can remove useful cached images and slow subsequent jobs.

Test signals: output free-space number should increase or meet the requested threshold.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/reclaim-space.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/release.sh -->
# sources/control-plane/mayastor/scripts/release.sh

Purpose: Mayastor-specific wrapper around shared dependency release tooling for Docker image builds/uploads.

Important APIs/types/functions: sets `SOURCE_REL` default to `utils/dependencies/scripts/release.sh`, initializes submodules when needed outside CI, sets `IMAGES`, `CARGO_DEPS`, and `PROJECT`, sources the shared release script, and calls `common_run "$@"` unless `NO_RUN=true`.

Control flow: mostly delegates to sourced release logic after project variables are set.

State/persistence: may initialize submodules and build/push Docker images depending on shared script arguments.

Dependencies/integration: integrates with repository dependency submodule release framework and Docker registry credentials.

Risks: behavior is opaque without the sourced script. Sourcing external shell code means variable/function names can collide.

Test signals: dry-run or release CI should show expected image list: `mayastor.io-engine`, `mayastor.casperf`, and `fio-spdk`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/release.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/rust-linter.sh -->
# sources/control-plane/mayastor/scripts/rust-linter.sh

Purpose: Rust clippy wrapper using the repository's SPDK Rust linter environment.

Important APIs/types/functions: sources `spdk-rs/scripts/rust-linter-env.sh` and runs `$CARGO clippy --all --all-targets --features=io-engine-testing -- -D warnings -A clippy::result-large-err`.

Control flow: linear shell execution.

State/persistence: read-only except build artifacts in target directory.

Dependencies/integration: CI style/lint gate for all Rust targets with io-engine testing features enabled.

Risks: depends on relative spdk-rs submodule path and exported `$CARGO`. Allows large error result lint while denying other warnings.

Test signals: exit `0` means clippy found no denied warnings.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/rust-linter.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/rust-style.sh -->
# sources/control-plane/mayastor/scripts/rust-style.sh

Purpose: Rust formatting wrapper using the repository linter environment.

Important APIs/types/functions: sets `FMT_OPTS` default to `--config imports_granularity=Crate`, sources `rust-linter-env.sh`, and runs `$CARGO fmt --all -- $FMT_OPTS`.

Control flow: linear shell execution.

State/persistence: modifies Rust files in place when formatting changes are needed.

Dependencies/integration: formatting gate for workspace Rust code; depends on rustfmt through the selected cargo toolchain.

Risks: default import granularity can reorder imports across the whole workspace. Running it in a dirty tree may mix unrelated formatting changes.

Test signals: clean formatter run leaves Rust code in expected style.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/rust-style.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/scripts/set-submodule-branches.sh -->
# sources/control-plane/mayastor/scripts/set-submodule-branches.sh

Purpose: helper for setting or updating git submodule tracking branches based on the current or requested branch.

Important APIs/types/functions: `submodule_set_branch_all` runs `git submodule set-branch`; `submodule_update` runs `git submodule update --remote` and recursive update inside modules. Options include `--branch`, `--clear`, `--update`, and `--update-modules`.

Control flow: defaults branch to current branch. It sets branch tracking only for `develop` or `release/*`, updates modules when requested, clears branch tracking when requested, otherwise prints no modification.

State/persistence: mutates `.gitmodules` branch settings and/or submodule worktrees.

Dependencies/integration: supports release/develop submodule maintenance and pairs with `check-submodule-branches.sh`.

Risks: bug `CLEAR_BRANCH=="y"` is a comparison-like command, not assignment, so `--clear` may not work. Unquoted module paths and command substitution are fragile for unusual paths.

Test signals: after setting/updating, `check-submodule-branches.sh` should pass.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/scripts/set-submodule-branches.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/sysfs/Cargo.toml -->
# sources/control-plane/mayastor/sysfs/Cargo.toml

Purpose: crate manifest for a small `sysfs` helper library, version `1.0.0`, edition 2018.

Important APIs/types/functions: no dependencies are declared, so the crate uses only Rust standard library.

Control flow: none; Cargo metadata only.

State/persistence: none directly.

Dependencies/integration: workspace utility crate for reading/writing sysfs-style files.

Risks: minimal; dependency-free crate should remain portable.

Test signals: compile checks confirm manifest and library remain valid.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/sysfs/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/sysfs/src/lib.rs -->
# sources/control-plane/mayastor/sysfs/src/lib.rs

Purpose: standard-library helpers for reading, parsing, and writing sysfs-like files.

Important APIs/types/functions: `parse_value<T>` reads `dir/file`, trims it, parses via `FromStr`, and returns `InvalidData` on parse failure. `write_value<T>` writes `ToString` content. `parse_dict` reads `KEY=val` lines into `HashMap<String, String>`.

Control flow: file paths are built with `Path::join`; parse failures include the path and raw trimmed value. `parse_dict` splits lines on `=` and only stores lines with exactly two parts.

State/persistence: reads and writes filesystem/sysfs state through `std::fs`.

Dependencies/integration: reusable by code interacting with Linux sysfs or configfs attributes.

Risks: `parse_dict` uses `line.unwrap()`, so read errors panic instead of returning `Err`. Values containing `=` are ignored because split must produce exactly two parts.

Test signals: should be covered with temp-file tests for parse success/failure, write behavior, and dictionary edge cases.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/sysfs/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/terraform/aws-linux/meta-data.yaml -->
# sources/control-plane/mayastor/terraform/aws-linux/meta-data.yaml

Purpose: cloud-init metadata for an AWS/Linux-style local image instance.

Important APIs/types/functions: sets `instance-id: id-0`, `local-hostname: amz-linux`, and DHCP config for `eth0`.

Control flow: no executable flow; cloud-init consumes it during instance boot.

State/persistence: becomes instance metadata and network configuration for the booted VM.

Dependencies/integration: paired with `user-data.yaml` in Terraform image provisioning.

Risks: static instance ID/hostname can collide if multiple instances share the same seed data.

Test signals: VM should boot with hostname `amz-linux` and DHCP networking on `eth0`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/terraform/aws-linux/meta-data.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/terraform/aws-linux/user-data.yaml -->
# sources/control-plane/mayastor/terraform/aws-linux/user-data.yaml

Purpose: cloud-init user data creating an SSH-capable privileged user for AWS/Linux-style Terraform images.

Important APIs/types/functions: creates default user and templated `${ssh_user}` with passwordless sudo, bash shell, groups `users,wheel`, plaintext password `mayastor`, unlocked password, and `${ssh_key}` authorized key. Enables SSH password auth and sets `ec2-user:mayastor`.

Control flow: cloud-init applies users, SSH config, and password changes on first boot.

State/persistence: persists users, password hashes, sudo rights, and authorized keys in the VM.

Dependencies/integration: templated by Terraform variables and paired with metadata seed.

Risks: plaintext default password and `ssh_pwauth: True` are risky outside disposable test environments.

Test signals: provisioned VM should allow SSH with the injected key and passwordless sudo for `${ssh_user}`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/terraform/aws-linux/user-data.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/terraform/mod/k8s/kubeadm_config.yaml -->
# sources/control-plane/mayastor/terraform/mod/k8s/kubeadm_config.yaml

Purpose: templated kubeadm configuration for creating a Kubernetes cluster.

Important APIs/types/functions: `InitConfiguration` sets bootstrap token, API advertise address `${master_ip}`, and bind port 6443. `ClusterConfiguration` sets API timeout, cert SAN `${cert_sans}`, cluster name `gilanetes`, and pod subnet `${pod_cidr}`. `KubeletConfiguration` sets systemd cgroup driver and `failSwapOn: false`.

Control flow: consumed by `kubeadm init --config`.

State/persistence: creates cluster certificates/config and kubelet config on the master.

Dependencies/integration: rendered by Terraform and used by `master.sh`; token must match node join script.

Risks: kubeadm API version `v1beta2` may be unsupported by newer Kubernetes. `certSANs` as a single templated scalar must render valid YAML.

Test signals: `kubeadm init` should complete and nodes should join with the same token and pod CIDR.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/terraform/mod/k8s/kubeadm_config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/terraform/mod/k8s/master.sh -->
# sources/control-plane/mayastor/terraform/mod/k8s/master.sh

Purpose: bootstraps the Kubernetes control-plane node for Terraform-provisioned test clusters.

Important APIs/types/functions: runs `kubeadm init --config /tmp/kubeadm_config.yaml` with swap/CPU/system verification preflight ignores, installs kubeconfig into `$HOME/.kube/config`, waits for localhost port 6443 with `nc`, and applies kube-router daemonset from GitHub.

Control flow: `set -ex` aborts on failures; after kubeadm init it loops until API server is reachable, then installs networking.

State/persistence: creates Kubernetes control-plane state, user kubeconfig, and cluster network daemonset.

Dependencies/integration: depends on `repo.sh` package setup, rendered kubeadm config, network access to GitHub, kubeadm/kubectl/nc.

Risks: applying a remote master-branch kube-router manifest is not pinned and can drift. Ignores significant preflight errors.

Test signals: local `kubectl` should work and kube-router pods should be created.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/terraform/mod/k8s/master.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/terraform/mod/k8s/node.sh -->
# sources/control-plane/mayastor/terraform/mod/k8s/node.sh

Purpose: configures worker node kernel prerequisites and joins it to the kubeadm cluster.

Important APIs/types/functions: functions `addKernelModules` and `addHugePages`; conditionally skips host kernel setup inside LXC; loads `nbd` and `xfs`, optionally installs Ubuntu extra modules and loads `nvme-tcp`/`nvmet`, waits for `${master_ip}:6443`, and runs `kubeadm join`.

Control flow: under `set -ex`, host setup runs unless `/proc/1/environ` contains `container=lxc`; then it waits for API server and joins with token and unsafe CA skip.

State/persistence: writes hugepage sysctl, module-load config, loads kernel modules, installs packages, and joins Kubernetes node state.

Dependencies/integration: templated variables include hugepage count, master IP, token, and image name. Integrates with kubeadm config and repo package setup.

Risks: unsafe CA skip, image-name-specific NVMe module logic, and appending duplicate module/sysctl lines on reruns.

Test signals: node should join the cluster with required hugepages and storage modules available for Mayastor.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/terraform/mod/k8s/node.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/terraform/mod/k8s/repo.sh -->
# sources/control-plane/mayastor/terraform/mod/k8s/repo.sh

Purpose: installs Docker, containerd, kubelet, kubeadm, and kubectl prerequisites on Ubuntu nodes.

Important APIs/types/functions: adds Google Kubernetes and Docker apt keys/repos, installs packages, marks Kubernetes packages held, writes Docker daemon config with systemd cgroup driver and overlay2, loads overlay/br_netfilter modules, writes containerd default config, and adds a systemd override intended for containerd kill behavior.

Control flow: updates apt, installs dependencies, writes config files, restarts Docker and containerd, and applies sysctl.

State/persistence: mutates apt sources/keys, packages, Docker/containerd configs, systemd drop-ins, modules-load config, and sysctl state.

Dependencies/integration: run before `master.sh` or `node.sh` in Terraform provisioning.

Risks: uses deprecated `apt-key` and old Kubernetes xenial repo. The containerd override path appears to write under `/etc/sysctl.d/system/containerd.service.d/override.conf` instead of `/etc/systemd/system/...`, likely a bug.

Test signals: kubeadm/kubectl/docker/containerd should be installed and using systemd cgroups.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/terraform/mod/k8s/repo.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/terraform/mod/libvirt/network_config.cfg -->
# sources/control-plane/mayastor/terraform/mod/libvirt/network_config.cfg

Purpose: netplan network config for libvirt Terraform guests.

Important APIs/types/functions: configures version 2, interface `ens3`, and DHCPv4.

Control flow: consumed by cloud-init/netplan on boot.

State/persistence: persists guest network configuration.

Dependencies/integration: used by libvirt module where the primary NIC is named `ens3`.

Risks: fails on images whose primary interface has a different name.

Test signals: libvirt guest should obtain IPv4 DHCP on `ens3`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/terraform/mod/libvirt/network_config.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/terraform/mod/lxd/network_config.cfg -->
# sources/control-plane/mayastor/terraform/mod/lxd/network_config.cfg

Purpose: netplan network config for LXD Terraform guests/containers.

Important APIs/types/functions: configures version 2, interface `eth0`, and DHCPv4.

Control flow: consumed by cloud-init/netplan on boot.

State/persistence: persists guest/container network configuration.

Dependencies/integration: used by LXD module where the primary interface is `eth0`.

Risks: minimal, but interface naming must match the LXD image/runtime.

Test signals: LXD instance should obtain IPv4 DHCP on `eth0`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/terraform/mod/lxd/network_config.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/grpc_enums.js -->
# sources/control-plane/mayastor/test/grpc/grpc_enums.js

Purpose: dynamically extracts enum constants from Mayastor protobuf descriptors for JavaScript gRPC tests.

Important APIs/types/functions: uses `@grpc/proto-loader`, `grpc.loadPackageDefinition`, and `path.join` to load `utils/dependencies/apis/io-engine/protobuf/mayastor.proto`; iterates loaded `mayastor` definitions and stores every enum variant name/number into `constants`.

Control flow: load proto synchronously with protobufjs include dir, flatten package definitions, detect entries whose `format` mentions `EnumDescriptorProto`, then export a name-to-number object.

State/persistence: in-memory constants object only.

Dependencies/integration: consumed by grpc JS tests to avoid hard-coding enum numeric values.

Risks: relies on internal descriptor shape (`ent.format` and `ent.type.value`) of grpc/proto-loader output. Duplicate enum variant names across enums would overwrite each other.

Test signals: JS tests using exported constants should match current protobuf enum values after proto changes.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/grpc_enums.js -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/multi_reporter.js -->
# sources/control-plane/mayastor/test/grpc/multi_reporter.js

Purpose: custom Mocha reporter wrapper that fans out events to multiple built-in reporters.

Important APIs/types/functions: `MultiReporter(runner, options)` reads `options.reporterOptions.reporters`, splits it on spaces, looks up each `mocha.reporters[report]`, instantiates it with the same runner/options, stores instances, and `epilogue` calls each child reporter's epilogue.

Control flow: if reporters option is missing or invalid, it prints diagnostics and continues with whatever valid reporters were instantiated.

State/persistence: reporter instances hold Mocha run state and may write reports according to their own options.

Dependencies/integration: used by `grpc-test.sh` to run `xunit` and `spec` reporters in one mocha invocation.

Risks: only proxies `epilogue`; it relies on reporter constructors registering their own runner listeners. Invalid reporter names do not fail the process.

Test signals: a grpc mocha run should emit both console spec output and xunit XML when configured with `reporters="xunit spec"`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/multi_reporter.js -->
