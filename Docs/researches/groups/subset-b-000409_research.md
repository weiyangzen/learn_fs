# Research: subset-b-000409

Grouped source research for the io-engine benchmark crate, io-engine test support crate, and selected io-engine bdev modules. Each section preserves its original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/.cargo/runner.sh -->
# sources/control-plane/mayastor/io-engine-bench/.cargo/runner.sh

Purpose: Cargo runner for `io-engine-bench`, wrapping benchmark execution in the privileges needed by io-engine/SPDK and moving Criterion output between `target/criterion` and the repository-owned `io-engine-bench/results/criterion`.

Important flow: captures all runner args as `ARGS`, chooses `sudo -E` when not already root, restores existing git Criterion results into `target/criterion`, then executes the target via `capsh` with `cap_setpcap` plus ambient `cap_sys_admin`, `cap_ipc_lock`, `cap_sys_nice`, and `cap_sys_resource`. After execution it attempts to chown the criterion target back to `$USER` and moves it into the bench results folder.

State and dependencies: depends on `SRCDIR`, `USER`, `sudo`, `capsh`, and writable target/results directories. It mutates benchmark result directories with `mv`, so interrupted runs may leave output in the alternate location.

Integration points: used by Cargo target runner configuration for benchmarks requiring elevated capabilities.

Risks and test signals: command injection exposure is limited to Cargo-provided args but uses `-- -c "${ARGS}"`; quoting matters for unusual test args. `mv` overwrites behavior and sudo/chown failures can affect repeatability. Validate by running a benchmark and confirming Criterion history survives across runs.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/.cargo/runner.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/Cargo.toml -->
# sources/control-plane/mayastor/io-engine-bench/Cargo.toml

Purpose: Defines the `io-engine-bench` crate, a Criterion benchmark package for io-engine workflows.

Important APIs/types/functions: no Rust API is declared here, but the manifest maps the `nexus` benchmark to `src/nexus.rs` with `harness = false`, allowing Criterion to own the benchmark main.

Dependencies: development dependencies include workspace `tokio` with `full`, workspace `uuid` with v4 generation, local `io-engine`, local `io-engine-tests`, and Criterion `0.5.1` with `async_tokio`. This positions the crate as a benchmark-only consumer of the runtime, gRPC compose test harness, and direct io-engine APIs.

Integration points: uses local path crates from the mayastor tree and expects the bench runner/build script to provide SPDK link/runtime setup.

State and persistence: Cargo metadata only; runtime state is created by bench code and Criterion outputs.

Risks and test signals: dependency drift is mostly tied to workspace versions plus Criterion. Because the benchmark uses test infrastructure, failures can come from docker/composer, SPDK privileges, or gRPC setup rather than benchmark logic. A healthy signal is `cargo bench -p io-engine-bench --bench nexus` reaching Criterion measurement rather than failing during setup.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/build.rs -->
# sources/control-plane/mayastor/io-engine-bench/build.rs

Purpose: Emits linker search and rpath directives so benchmark binaries can find native SPDK-related artifacts in the repository target directory.

Important flow: reads `PROFILE` and `SRCDIR`, builds `$SRCDIR/target/$PROFILE`, then prints `cargo:rustc-link-search=native=...` and `cargo:rustc-link-arg=-Wl,-rpath=...`.

Dependencies: relies on Cargo environment variable `PROFILE` and repository-specific `SRCDIR`. It has no fallback if either is absent.

Integration points: complements `.cargo/runner.sh`; the build script handles link/runtime lookup while the runner handles runtime privileges.

State and persistence: no persisted state. It affects Cargo build output by altering linker arguments for this crate.

Risks and test signals: hardwires native library lookup to a target profile under `SRCDIR`; cross-compilation or custom target directories can break. Test by building the benchmark and checking that generated binaries run without missing shared library errors.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/build.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/src/common.rs -->
# sources/control-plane/mayastor/io-engine-bench/src/common.rs

Purpose: Re-exports the entire `io_engine_tests` crate into the benchmark crate under a local `common` module.

Important APIs/types/functions: `pub use io_engine_tests::*` makes test helpers, compose support, MayastorTest, bdev/nexus builders, and macros visible through `common::...`.

Dependencies: the file depends wholly on the `io-engine-tests` crate declared as a dev dependency. There is no local logic or state.

Integration points: `src/nexus.rs` imports `common::compose` and calls `common::composer_init()`, using this file as a compatibility shim rather than importing `io_engine_tests` directly everywhere.

State and persistence: no state; all state comes from re-exported modules.

Risks and test signals: broad wildcard re-export can hide where APIs come from and may expose unrelated test helpers to benchmarks. Compile failures in this file generally indicate `io-engine-tests` dependency or module export changes.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/src/common.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/src/lib.rs -->
# sources/control-plane/mayastor/io-engine-bench/src/lib.rs

Purpose: Empty library target placeholder. The file contains no items.

Important APIs/types/functions: none.

Dependencies and integration: no direct dependencies. Cargo may still build a library target because the source exists, but benchmark behavior is in `src/nexus.rs`.

State and persistence: none.

Risks and test signals: the empty file is low risk. If crate-level docs or shared benchmark utilities are later needed, this is the natural place to add them; currently changes here should not affect benchmark execution.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/src/nexus.rs -->
# sources/control-plane/mayastor/io-engine-bench/src/nexus.rs

Purpose: Criterion benchmark comparing direct in-process nexus creation against legacy gRPC nexus creation using a four-container compose cluster and an in-binary Mayastor environment.

Important APIs/types/functions: `build_type()` infers build profile from `OUT_DIR`/`SRCDIR`; `new_compose()` initializes composer and starts four io-engine containers; `new_environment()` creates `MayastorTest`; `get_children()` lazily creates and shares malloc bdevs over NVMf; `DirectNexus` and `GrpcNexus` destroy created nexuses in `Drop`; `nexus_create_direct()` calls `io_engine::bdev::nexus::nexus_create`; `nexus_create_grpc()` calls v0 gRPC `create_nexus`; `criterion_benchmark()` registers async Criterion cases.

Control flow: setup is done once per benchmark group. Child URIs are cached in a `tokio::sync::OnceCell`. Each iteration creates a unique nexus with three children and relies on large-drop cleanup to run destruction after measurement.

State and dependencies: depends on composer containers, gRPC v0 generated clients, Tokio runtime, UUIDs, NVMf ports, malloc bdev state, and global io-engine runtime state inside `MayastorTest`.

Risks and test signals: `Drop` creates fresh runtimes and unwraps destroy calls, so cleanup failures panic. Cached children assume the compose cluster remains valid for the full run. Benchmark timing includes API path and internal create work but not full cluster setup. Healthy output is two Criterion functions under `<build>/nexus/create`: `direct` and `grpc`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/src/nexus.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/Cargo.toml -->
# sources/control-plane/mayastor/io-engine-tests/Cargo.toml

Purpose: Defines `io-engine-tests`, the shared support library for io-engine integration tests, benchmarks, and examples.

Important dependency surface: async helpers use `tokio`, `async-trait`, and `tonic`; command/test utilities use `run_script`, `regex`, `nix`, `chrono`, and `colored_json`; storage-facing helpers depend on local `io-engine`, `io-engine-api`, `spdk-rs`, `libnvme-rs`, `composer`, and the local proc-macro crate `io-engine-tests-macros`.

Integration points: this crate exposes builders and wrappers for bdevs, pools, replicas, nexus, snapshots, NVMf/NVMe devices, file I/O, FIO, compose clusters, and SPDK single-thread test execution. It is consumed by io-engine tests and by `io-engine-bench`.

State and persistence: no manifest-level state, but dependencies imply runtime access to SPDK, system block devices, docker/compose networking, and host binaries.

Risks and test signals: path dependencies mean this crate tracks local API changes tightly. Because many modules panic on setup failures, a Cargo build only proves API compatibility; meaningful tests require privileged host tools, SPDK environment variables, and available NVMe/fio/loopback resources.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/io-engine-tests-macros/Cargo.toml -->
# sources/control-plane/mayastor/io-engine-tests/io-engine-tests-macros/Cargo.toml

Purpose: Manifest for a small proc-macro crate used by `io-engine-tests`.

Important API surface: declares `[lib] proc-macro = true`, allowing `src/lib.rs` to export attribute macros. Dependencies are `proc-macro2`, `quote`, and `syn` with `extra-traits`, enough to parse function items and emit wrapper code.

Integration points: consumed by the parent test-support crate and re-exported as `spdk_test`, so tests can mark async SPDK tests with a single attribute.

State and persistence: no runtime state in the manifest. The generated macro code relies on `tokio` and `io_engine_tests` being available from the consuming test crate.

Risks and test signals: macro crate versions are pinned outside the workspace, so proc-macro parsing behavior can shift only on explicit version changes. `cargo test -p io-engine-tests-macros` mostly validates compilation; downstream macro expansion tests are more useful.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/io-engine-tests-macros/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/io-engine-tests-macros/src/lib.rs -->
# sources/control-plane/mayastor/io-engine-tests/io-engine-tests-macros/src/lib.rs

Purpose: Provides the `#[spdk_test]` attribute for tests that need all SPDK work to run on one designated thread while still using Tokio test syntax.

Important APIs/types/functions: `spdk_test(_args, item)` parses the annotated item as `syn::ItemFn`, keeps a clone of the original function, and emits a `#[tokio::test] async fn` with the same identifier. Inside the wrapper it defines the original function, then calls `io_engine_tests::test_task::run_single_thread_test_task(|| { #fn_ident(); }).await`.

Control flow: Cargo sees the wrapper as the test entry point. The original async function becomes a nested item and is invoked through the test-task executor; the single-thread executor serializes these tests through a channel.

State and dependencies: depends on downstream `tokio` and `io_engine_tests::test_task`. It does not use macro args.

Risks and test signals: the macro assumes the annotated function shape can be called as `#fn_ident()` inside a sync closure; it is intended for async Tokio tests but the generated closure does not explicitly await the nested function. Any change to `test_task` or async handling should be verified with a real annotated SPDK test.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/io-engine-tests-macros/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/bdev.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/bdev.rs

Purpose: Thin async helper wrappers around v1 bdev gRPC APIs for tests.

Important APIs: `create_bdev(rpc, uri)` locks a shared RPC handle and sends `CreateBdevRequest`; `list_bdevs(rpc)` sends `ListBdevOptions { name: None }`; `find_bdev_by_name(rpc, name)` lists and filters by name, returning `None` on list errors.

Control flow: all functions use `SharedRpcHandle::lock().await`, call the generated gRPC client, and unwrap response envelopes into `Bdev` vectors or values.

State and dependencies: depends on `compose::rpc::v1` generated API types and the shared handle lock. It mutates remote io-engine state only through create calls.

Integration points: used by higher-level tests that need simple bdev lifecycle or lookup without manually constructing protobuf requests.

Risks and test signals: `find_bdev_by_name` hides RPC errors as not found, which is convenient but can mask transport failures. Tests should assert create/list separately when diagnosing infrastructure issues.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/bdev.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/bdev_io.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/bdev_io.rs

Purpose: Direct in-process I/O helpers for tests using `UntypedBdevHandle` rather than gRPC or host device paths.

Important APIs: `write_some()` delegates to `write_blocks`; `write_blocks()` opens a bdev read/write, allocates DMA memory sized by block length and count, fills it with a byte, and writes at an offset; `read_some()` reads into DMA memory and asserts the first block matches the expected fill; `write_zeroes_some()` issues write-zeroes; `read_some_safe()` returns `Ok(false)` instead of panicking on byte mismatch.

Control flow: each helper opens a fresh handle by name and uses async SPDK handle methods. Buffer sizing is based on the target bdev block length.

State and dependencies: mutates bdev content. Depends on io-engine core DMA allocation and an initialized SPDK reactor context.

Risks and test signals: `read_some()` only checks the first 512 bytes, regardless of actual block size. Offsets are passed through as byte offsets to handle methods, so callers must match expected units. Useful test signals are exact read/write lengths and mismatch prints from `read_some_safe`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/bdev_io.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/cli_tools.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/cli_tools.rs

Purpose: Shared subprocess execution utility for test helpers that need external host commands.

Important APIs: `run_command_args(path, args, short_desc)` builds a `Command` then delegates to `run_command`; `run_command(cmd, desc, short_desc)` spawns, waits, joins an output reader thread, and returns exit status plus output lines as `OsString`; `spawn_child()` configures stdout/stderr piping and creates the child plus reader thread.

Control flow: stdout and stderr are merged by setting stderr to stdout. The reader consumes lines using `BufReader::read_until(b'\n')`, optionally echoes them prefixed by `short_desc`, and preserves raw bytes through `OsStringExt`.

State and dependencies: no persistent state; depends on host process spawning, pipes, and Unix `OsString` byte conversion.

Risks and test signals: commands can deadlock only if output reading stops, but the dedicated thread mitigates this. It does not treat nonzero exit as an error; callers must inspect `ExitStatus`. The raw-byte line handling is robust for non-UTF8 command output.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/cli_tools.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/compose/mod.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/compose/mod.rs

Purpose: Provides `MayastorTest`, an in-process io-engine test harness, while re-exporting the external `composer` crate for container-based integration tests.

Important APIs/types: `MayastorTest<'a>` owns CLI args, optional log level, a reactor handle, and a thread handle. Constructors initialize logging/CPS, create a bounded channel, spawn a named `ms-test` thread, initialize `MayastorEnvironment`, set the primary mthread current, and send the reactor back. `spawn()` schedules futures on the reactor and awaits their result. `start_grpc()` initializes resource locks and runs the gRPC server. `Drop` sends `mayastor_env_stop(0)` and joins the thread.

Control flow: tests create the harness, then call `spawn()` to execute io-engine futures on the correct reactor thread. Shutdown is asynchronous but triggered synchronously on drop.

State and dependencies: owns global Mayastor runtime, logger, CPS init, resource lock manager, and `/var/run/dpdk` assumptions through callers.

Risks and test signals: global runtime state means multiple harnesses can interfere if not serialized. Drop unwraps join unless panicking. Healthy tests show reactor startup, future completion through `spawn`, and clean environment stop.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/compose/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/compose/rpc/mod.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/compose/rpc/mod.rs

Purpose: Simple module aggregator for compose RPC clients.

Important APIs: declares `pub mod v0;` and `pub mod v1;`, exposing legacy and current gRPC helper modules.

Dependencies and integration: downstream tests choose v0 or v1 depending on API surface under test. The benchmark code uses v0 for legacy nexus creation, while most builder helpers use v1.

State and persistence: none.

Risks and test signals: low risk; failures indicate missing module files or generated API changes in the submodules.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/compose/rpc/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/compose/rpc/v0.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/compose/rpc/v0.rs

Purpose: Legacy gRPC client helpers for compose-managed io-engine containers.

Important APIs/types: re-exports `io_engine::grpc::v0` as `mayastor`; `RpcHandle` holds container name, endpoint, and v0 clients for mayastor, bdev, stats, and json. `RpcHandle::connect()` builds a `tonic::transport::Endpoint`, connects to `http://addr`, and constructs each client from the shared channel. `GrpcConnect` wraps a `ComposeTest` and provides `grpc_handles()` for all containers and `grpc_handle(name)` for one container.

Control flow: container IP/port data comes from `ComposeTest::containers()`, with gRPC hardcoded to port `10124`.

State and dependencies: depends on tonic channels and composer container metadata. No persistent state beyond client handles.

Risks and test signals: uses legacy v0 generated clients, so it is sensitive to API removal. `grpc_handles()` preserves container iteration order, which callers like the benchmark use by selecting the last handle for nexus operations. Failures usually surface as connect errors or missing container names.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/compose/rpc/v0.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/compose/rpc/v1.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/compose/rpc/v1.rs

Purpose: Current v1 gRPC client helpers for compose-managed tests.

Important APIs/types: re-exports `io_engine_api::v1::*` and `tonic::Status`. `SharedRpcHandle` wraps an `RpcHandle` in `Arc<tokio::sync::Mutex<_>>` and preserves name/endpoint. `RpcHandle` owns generated clients for bdev, pool, replica, nexus, snapshot, registration, host, json, and test services. `RpcHandle::connect()` builds one tonic channel and clones it into all clients. `GrpcConnect` creates handles from a `ComposeTest`.

Control flow: callers lock `SharedRpcHandle` before issuing gRPC requests, serializing access to the multi-client handle. Endpoints are `container_ip:10124`.

State and dependencies: transient tonic channel state plus composer container metadata. `PartialEq` for `SharedRpcHandle` compares endpoints, enabling builder locality checks.

Risks and test signals: lock serialization can hide concurrent client behavior, but simplifies tests. Generated service set must match io-engine API. Healthy signals are successful `grpc_handles()` creation and service-specific calls through builders.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/compose/rpc/v1.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/error_bdev.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/error_bdev.rs

Purpose: Test helpers for SPDK error vbdev creation and error injection.

Important APIs: re-exports SPDK read/write I/O type constants; defines `VBDEV_IO_FAILURE = 1`; `create_error_bdev(error_device, backing_device)` creates an AIO bdev around the backing file/device and then wraps it with `vbdev_error_create`; `inject_error(error_device, op, mode, count)` builds `vbdev_error_inject_opts` and calls `vbdev_error_inject_error`.

Control flow: all FFI calls are unsafe and immediately asserted to return zero. The injection CString is converted with `into_raw` and not reclaimed.

State and dependencies: mutates global SPDK bdev graph and error injection state. Depends on `spdk-rs` raw libspdk bindings.

Risks and test signals: assert-based error handling is acceptable for tests but poor diagnostics. The raw CString leak in `inject_error` is small but repeated use can accumulate. Validate by creating an error bdev, injecting read/write failures, and observing expected I/O failures.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/error_bdev.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/file_io.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/file_io.rs

Purpose: Async file data generation, write/read verification, checksum, and byte-by-byte comparison utilities for integration tests.

Important APIs/types: `DataSize(u64)` wraps byte sizes and provides constructors for bytes, KB, MB, GB, block counts, conversions, `Display`, and serde-as-u64 behavior. `set_test_buf_rng_seed()` fixes a global ChaCha8 seed. `test_write_to_file()` creates deterministic/random test buffers, writes repeated buffers at an offset, then seeks back and validates every byte. `compute_file_checksum()` streams MD5 over a file. `compare_files()` compares two files in 16 KiB chunks and reports size or byte mismatch.

Control flow: Tokio `OpenOptions`, async seek/read/write, and in-memory buffers are used throughout.

State and dependencies: global `OnceCell<ChaCha8Rng>` controls buffer seed and cannot be reset after first set. File contents are mutated by write tests.

Risks and test signals: cloning the RNG from `OnceCell` means repeated calls from the same seed create identical buffers, useful for reproducibility but surprising for randomness. `DataSize` conversions to `usize` can truncate on small platforms. Validation errors include exact offsets.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/file_io.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/fio.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/fio.rs

Purpose: Builder-based wrapper for running fio workloads from Rust tests and mapping fio JSON output back to per-job results.

Important APIs/types: `FioJobResult` tracks not-run/ok/error errno. `FioJob` is a serializable builder with job name, ioengine, filename, rw, direct, block size, offset, iodepth, runtime, size, verification, and randomization options. `FioJob::as_fio_args()` serializes non-null fields into CLI args, converting booleans to 1/0 and adding `--time_based=1` when runtime is set. `Fio` groups jobs and execution options; `Fio::run()` builds `sudo LD_PRELOAD=$FIO_SPDK $FIO --output-format=json ...`, runs it with `run_script`, records duration/exit/stderr, and parses job errors. `spawn_fio_task()` runs fio on a blocking Tokio task and converts nonzero exit to `io::Error`.

State and dependencies: depends on environment variables `FIO` and `FIO_SPDK`, sudo, fio JSON format, and `derive_builder`.

Risks and test signals: command is assembled as a shell string, so filenames are sensitive to quoting; NVMf filenames are explicitly quoted elsewhere. `update_result` filters `fio: ` lines before JSON parsing. Healthy tests inspect `exit`, `err_messages`, and each job result.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/fio.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/lib.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/lib.rs

Purpose: Root of the io-engine test support library, exporting modules and host/SPDK utility functions used across integration tests.

Important APIs: exports bdev, compose, fio, nexus, nvme/nvmf, pool, replica, snapshot, fault-injection, and single-thread SPDK test support. Defines retry, reactor polling macros, `test_init!`, global `MSTEST`, logging/CPS initialization, file/block-device helpers (`dd`, `truncate`, loopdev, mkfs, fsck, mount, cmp), fio verification scripts, device comparison, URI path extraction, rebuild waiting, RDMA rxe setup/cleanup, composer initialization, JSON formatting, UUID generation, and diagnostic printing.

Control flow: many helpers shell out through `Command` or `run_script`, assert success, and print command output. `wait_for_rebuild()` watches a rebuild job notification channel from an unaffinitized mthread while polling the reactor. `composer_init()` initializes composer from the mayastor source directory.

State and dependencies: mutates host files, loop devices, mounts, RDMA links, `/tmp/__test`, DPDK runtime directories, global logger, SPDK CPS, and Mayastor environment.

Risks and test signals: this file intentionally panics on missing prerequisites. External binaries, root privileges, network route discovery, and timing make failures environmental. The top comment notes a future need to return errors instead of asserting.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/nexus.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/nexus.rs

Purpose: High-level v1 gRPC test builder and helpers for nexus lifecycle, child operations, snapshots, NVMe reservation settings, and NVMf I/O validation.

Important APIs/types: `NexusBuilder` stores RPC handle, name, UUID, size, controller ID range, reservation/preemption settings, children, nexus info key, and serial. Fluent methods set name/uuid/size/children/replicas/reservation policy. Async methods create, shutdown, destroy, publish, resize, add/remove/online/offline children, wait for states, create nexus snapshots, list snapshots, get rebuild history, and add child fault injection. Free functions list/find nexuses, run write/fio tests against a nexus, and derive nexus serial/NQN.

Control flow: all remote operations lock the shared v1 RPC handle and send generated requests. Local versus remote replica URIs are selected by comparing `SharedRpcHandle` endpoints.

State and dependencies: mutates remote nexus state, child state, snapshot state, and fault-injection state. Depends on replica builders, NVMf helpers, io-engine snapshot params, and tonic status codes.

Risks and test signals: required fields are enforced with `expect`, so incomplete builders panic. Polling waits use 100 ms sleeps and return `Cancelled` on timeout. Useful assertions include child state/reason, list/find by UUID, rebuild history, and NVMf I/O success.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/nexus.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/nvme.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/nvme.rs

Purpose: Host-side NVMe CLI and libnvme helpers for connecting to Mayastor NVMf targets and finding resulting Linux NVMe devices.

Important APIs/types: `NmveConnectGuard` connects on creation and disconnects by NQN on drop. `nvme_discover()` parses `nvme discover` output into key/value maps. `nvme_connect()` runs `nvme connect` with transport/address/NQN and optional host ID/NQN env fallback. Disconnect helpers call `nvme disconnect-all` or `disconnect -n`. Device lookup filters libnvme devices by Mayastor controller model and serial. `get_nvme_resv_report()` runs `nvme resv-report -o json`.

Control flow: command helpers assert or panic when required host setup is missing unless `must_succeed` is false for connect.

State and dependencies: mutates host NVMe connections. Depends on `nvme` CLI, `/etc/nvme/hostid`, `/etc/nvme/hostnqn` or env replacements, libnvme-rs, and root/device permissions.

Risks and test signals: typo in type name (`Nmve`) is API-stable but confusing. A one-second sleep after connect handles device discovery latency. Tests should validate serial-based path lookup before issuing data I/O.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/nvme.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/nvmf.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/nvmf.rs

Purpose: NVMf target location and I/O helpers bridging io-engine nexus/replica metadata to host NVMe devices or SPDK fio target strings.

Important APIs/types: `NvmfLocation { addr, nqn, serial }` can be built from nexus address/name/uuid, opened into an `NmveConnectGuard` plus Linux device path, and converted to SPDK fio transport args. `test_write_to_nvmf()` connects, finds the device by serial, and delegates file write validation. `test_devices_identical()` opens multiple targets and compares their device files. `test_fio_to_nvmf()` configures Fio jobs for SPDK ioengine with NVMf transport args. `test_fio_to_nvmf_aio()` connects through kernel NVMe and runs fio with libaio on the device path.

State and dependencies: mutates host NVMe connection state and target data. Depends on `nvme` helpers, fio wrapper, and file comparison utilities.

Risks and test signals: `test_devices_identical` requires at least two locations and uses byte-for-byte comparison over device files. SPDK fio target args escape colons in NQN; quoting is important. Healthy tests prove both kernel and SPDK I/O paths.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/nvmf.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/pool.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/pool.rs

Purpose: Pool builder utilities for both remote v1 gRPC pools and local in-process LVS pools.

Important APIs/types: `PoolBuilderOpts` stores name, UUID, bdev URI, and cluster size. `PoolBuilderRpc` wraps opts plus `SharedRpcHandle`; `PoolBuilderLocal` wraps local opts. `PoolOps` abstracts pool operations over local and remote variants. RPC builders create/grow/destroy pools, list replicas, and create replicas through generated gRPC clients. Local builders use `io_engine::lvs::Lvs::create_or_import`, create lvols directly, and clean up in `Drop` through `Reactor::block_on`.

Control flow: fluent builder methods require name/uuid/bdev before operations. `with_malloc*` convenience methods synthesize malloc bdev URIs.

State and dependencies: mutates remote pool service state or local SPDK/LVS state. Local `PoolLocal` owns optional cleanup behavior.

Risks and test signals: local and RPC implementations are not perfectly symmetric; local `get_replicas` is unimplemented. `Drop` cleanup can hide destroy errors with `.ok()`. Test by listing pools after create/grow/destroy and by `validate_pools_used_space` for replicated expectations.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/replica.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/replica.rs

Purpose: v1 gRPC test builder for replica lifecycle, sharing, resizing, lookup, and data consistency validation.

Important APIs/types: `ReplicaBuilder` stores RPC handle, pool UUID, name, UUID, optional bdev URI, size, thin flag, share protocol, shared URI, and serial. Fluent setters configure name/uuid/pool/size/thin/NVMf. Accessors build NQN, bdev URI, NVMf location, serial, and shared URI. Async methods create, destroy, share, resize, and get a replica. Free functions list replicas, find by UUID, and validate multiple replicas by reading through NVMf.

Control flow: create/share/resize/destroy lock the shared v1 RPC handle and call generated replica client methods. Sharing records returned URI into the builder for later nexus-child use.

State and dependencies: mutates replica service state and remote NVMf sharing state. Depends on pool builders, `io_engine_api`, NVMf helpers, and UUID-derived serial generation.

Risks and test signals: missing fields panic through `expect`/`unwrap`. `destroy` can pass either a pool UUID selector or none. Healthy tests create, share, locate by UUID, then validate data across replicas.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/replica.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/snapshot.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/snapshot.rs

Purpose: v1 gRPC builders for replica snapshots and snapshot clones in tests.

Important APIs/types: `ReplicaSnapshotBuilder` stores RPC handle, replica UUID, snapshot UUID/name, entity ID, and txn ID. It can generate a snapshot UUID, create a replica snapshot, and filter listed snapshots by source replica. `SnapshotCloneBuilder` stores RPC handle, snapshot UUID, clone name, and clone UUID. It creates snapshot clones and filters listed clone replicas by snapshot UUID. Free functions `list_snapshot` and `list_snapshot_clone` expose unfiltered RPC list calls.

Control flow: builders lock the shared RPC handle and call generated snapshot service methods. Filtering is done client-side after listing all objects.

State and dependencies: mutates snapshot and clone state in io-engine. Depends on `io_engine_api::v1::snapshot` and tonic status.

Risks and test signals: required fields use `expect`/`unwrap`, so incomplete setup panics. `with_snapshot_uuid()` always generates a UUID and accepts no input, unlike clone UUID setter. Healthy tests assert create responses and list filters contain the new snapshot/clone.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/test.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/test.rs

Purpose: v1 test-service wrappers for dynamic fault injection management.

Important APIs: `add_fault_injection(rpc, inj_uri)`, `remove_fault_injection(rpc, inj_uri)`, and `list_fault_injections(rpc)` lock the shared RPC handle and call generated test service methods.

Control flow: each function maps a successful tonic response to its inner value, returning `Status` on RPC errors.

State and dependencies: mutates io-engine fault-injection registry, typically used by nexus tests after constructing an injection URI for a child device.

Integration points: `NexusBuilder::add_injection_at_replica()` calls `add_fault_injection` after resolving the child device name.

Risks and test signals: injection URI syntax is not validated locally; failures come from the remote test service. `list_fault_injections` is the primary verification signal after add/remove.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/test_task.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/test_task.rs

Purpose: Serializes special SPDK test tasks onto one designated OS thread for tests using the `spdk_test` macro.

Important APIs/types: `TestTask` packages a oneshot sender and boxed closure. `MAIN_THREAD` is a `OnceCell<Sender<TestTask>>`. `run_single_thread_test_task(f)` initializes a bounded channel and background thread on first use, sends the closure, and awaits the oneshot completion. `main_loop()` receives tasks forever, runs the closure, and signals completion.

Control flow: callers remain in async Tokio tests while the actual closure runs on the dedicated thread. Channel capacity one serializes submissions.

State and dependencies: owns a process-global background thread for the lifetime of the process. Depends on crossbeam channels and Tokio oneshot.

Risks and test signals: panics inside task closures can terminate the background thread and break later tests. There is no shutdown path. Successful annotated tests prove channel send, closure execution, and oneshot completion.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/test_task.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/.cargo/config.toml -->
# sources/control-plane/mayastor/io-engine/.cargo/config.toml

Purpose: Cargo target configuration ensuring io-engine test and binary execution uses the local privilege runner on Linux x86_64 and aarch64 targets.

Important configuration: sets `[target.x86_64-unknown-linux-gnu] runner = ".cargo/runner.sh"` and the same for `aarch64-unknown-linux-gnu`.

Dependencies and integration: integrates with Cargo's target runner mechanism. The referenced runner grants capabilities required by Mayastor/io-engine rather than requiring the entire cargo invocation to run as root.

State and persistence: no runtime state. It changes how `cargo run`/`cargo test` execute built binaries for these targets.

Risks and test signals: non-Linux or non-listed targets will not use the runner. Relative runner path assumes commands are launched with Cargo resolving from the package root. Test by running a small io-engine test and verifying `.cargo/runner.sh` is invoked.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/.cargo/config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/.cargo/runner.sh -->
# sources/control-plane/mayastor/io-engine/.cargo/runner.sh

Purpose: Privilege wrapper for running io-engine binaries/tests under Cargo with the Linux capabilities required by Mayastor/SPDK.

Important flow: captures command args, chooses `sudo -E --preserve-env=PATH` if not root, then invokes `capsh` with `cap_setpcap` plus ambient `cap_sys_admin`, `cap_ipc_lock`, `cap_sys_nice`, and `cap_sys_resource`, executing the original command via shell.

Dependencies: requires `sudo`, `capsh`, a working PATH under sudo, and the caller's environment variables to be preserved for SPDK/io-engine runtime configuration.

Integration points: referenced by `.cargo/config.toml` for Linux targets.

State and persistence: no persisted state; only affects process capabilities.

Risks and test signals: uses shell execution of captured args, so quoting matters. If sudo strips needed env vars despite `--preserve-env=PATH`, tests can fail in non-obvious ways. Healthy signal is binaries start without permission errors for hugepages, scheduling, resource limits, or IPC locking.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/.cargo/runner.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/Cargo.toml -->
# sources/control-plane/mayastor/io-engine/Cargo.toml

Purpose: Manifest for the main `io-engine` crate, including binaries, examples, feature flags, local API dependencies, and SPDK-adjacent dependencies.

Important configuration: default feature is `spdk-async-qpair-connect`; optional features include `io-engine-testing`, `extended-tests`, `fault-injection`, `nexus-io-tracing`, and `nvme-pci-tests`. Binaries include `io-engine`, `spdk`, `initiator`, `uring-support`, `io-engine-client`, `jsonrpc`, and `casperf`; example `lvs-eval` points to `examples/lvs-eval/main.rs`.

Dependencies: combines crates for async runtime, CLI, logging/tracing, serialization, NVMe/io_uring/system calls, tonic/prost, and local path crates such as `spdk-rs`, `io-engine-api`, event publisher, secret provider, version info, sysfs, and jsonrpc.

Integration points: dev-depends on `io-engine-tests`, `libnvme-rs`, `run_script`, and `prettytable-rs` for tests/examples.

State and risks: feature combinations gate fault injection, testing hooks, tracing, and async NVMe behavior. Build/test signals should include default build, feature-specific test builds, and example compilation when touching dependencies.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/examples/lvs-eval/display.rs -->
# sources/control-plane/mayastor/io-engine/examples/lvs-eval/display.rs

Purpose: Pretty-printer for the `lvs-eval` example, exposing internal SPDK blobstore, bdev, and lvol allocation state.

Important APIs: `print_lvs()` prints base bdev, blobstore data, and replicas. `print_bdev()` displays name, size, block length, and block count. `print_lvs_data()` dereferences `spdk_blob_store` internals and prints metadata layout, free clusters, page usage, and bit arrays. `print_replicas()` iterates lvols; `print_replica()` prints lvol name/uuid/thin flag/cluster counts/size and active blob data. `print_blob_data()` dumps cluster IDs, LBAs, and extent pages. Private helpers print tables, bit arrays/pools, separators, and translate LBA to cluster.

State and dependencies: read-only introspection of live SPDK/LVS structures through unsafe pointers. Depends on `prettytable`, io-engine `Lvs/Lvol` traits, and raw libspdk structures.

Risks and test signals: tightly coupled to SPDK internal struct layout and unsafe pointer validity. It is diagnostic/example code, not production API. Test by running `lvs-eval` and checking output tables match expected allocations.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/examples/lvs-eval/display.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/examples/lvs-eval/main.rs -->
# sources/control-plane/mayastor/io-engine/examples/lvs-eval/main.rs

Purpose: CLI example for creating/importing an LVS pool, creating replicas/filler lvols, printing allocation internals, and optionally destroying or exporting the pool.

Important APIs/types: `CliArgs` defines disk, replica count, replica cluster count, cluster size, thin flag, metadata expansion, extent-table flag, pool name, destroy flag, and filler option. `main()` creates a `MayastorTest` runtime, then runs pool/replica operations inside it. `create_lvs()` builds `PoolArgs` with a fixed UUID. `create_replica()`, `create_filler_replica()`, and `create_lvol()` create lvols with deterministic UUID patterns and optional extent-table control.

Control flow: parse CLI, set global `G_USE_EXTENT_TABLE`, start a two-reactor Mayastor environment, create pool, create fillers/replicas until failure, print, optionally destroy fillers, then destroy or export pool.

State and dependencies: mutates the disk/pool passed by CLI. Depends on `io_engine_tests::MayastorTest`, LVS backend, clap, and version-info.

Risks and test signals: uses `static mut` for extent-table flag and fixed pool UUID, so concurrent/repeated runs can collide. Intended as manual diagnostic tooling; verify by inspecting printed blobstore state.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/examples/lvs-eval/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/aio.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/aio.rs

Purpose: URI-backed implementation for SPDK AIO bdev creation, destruction, probing, and optional rescan.

Important APIs/types: `Aio` stores name/path, alias URI, block size, optional UUID, and rescan flag. `TryFrom<&Url>` parses path segments, detects whether the path is a block device, parses `blk_size`, `uuid`, and `rescan`, and rejects unknown query parameters. `CreateDestroy::create()` creates an AIO bdev with `create_aio_bdev`, sets UUID/alias, or rescans an existing bdev when requested. `destroy()` calls async `bdev_aio_delete`. `Probe` checks file existence with `probe_file`.

Control flow: existing bdev without `rescan` is an error; with `rescan`, `bdev_aio_rescan` updates block count. Creation looks up the bdev after SPDK returns success to attach metadata.

State and dependencies: mutates SPDK bdev registry and aliases. Depends on filesystem metadata, libspdk AIO APIs, futures oneshot callbacks, and `BdevError`.

Risks and test signals: default block size is `0` for block devices and `512` for files. Destroy is asynchronous and depends on callback delivery. Test with file-backed and block-device AIO URIs, UUID alias lookup, and resize/rescan scenarios.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/aio.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/crypto.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/crypto.rs

Purpose: Manages SPDK crypto vbdev creation/destruction and tracks crypto key usage across vbdevs.

Important APIs/types: global `KEY_CRYPTO_VBDEV_MAP` maps key names to crypto vbdev users under `RwLock`. `EncryptionKey` carries cipher, key name, key material, lengths, and optional second key. `Cipher` maps API cipher values and displays SPDK strings. `enable_dpdk_cryptodev_accel_module()` enables DPDK cryptodev and assigns encrypt/decrypt opcodes. `create_crypto_key()` creates or reuses SPDK accel crypto keys. `create_crypto_vbdev_on_base_bdev()` creates a key/user mapping, builds crypto opts, and calls `create_crypto_disk`. `destroy_crypto_vbdev()` deletes the disk, resolves/removes its key mapping, and destroys the key when last user is removed.

Control flow: key-user state is updated before crypto disk creation; destroy tolerates missing bdev but cleans key mapping when possible.

State and dependencies: mutates SPDK accel key registry, crypto vbdev registry, and process-global key map. Depends on raw libspdk crypto APIs and io-engine RPC cipher types.

Risks and test signals: if disk creation fails after `add_key_user`, map cleanup is not performed in this function. Key material is intentionally omitted from `Debug`. Test multiple vbdevs sharing a key, last-user key destruction, and creation failure cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/crypto.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/dev.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/dev.rs

Purpose: Central URI dispatcher and generic block-device lookup/open/create/destroy facade for supported bdev schemes.

Important APIs: `uri::parse()` converts a URI into a boxed `BdevCreateDestroy`; `try_parse_or_aio()` falls back to `aio://{uri}` when plain paths are supplied; `parse_url()` dispatches schemes including aio, bdev/loopback, ftl, malloc, null, nvmf variants, pcie, uring, nexus, and lvol. `reject_unknown_parameters()` enforces strict query parsing. Top-level `device_lookup`, `device_name`, `device_create`, `device_destroy`, and `device_open` expose scheme-neutral operations.

Control flow: device lookup/open prefer NVMf (`nvmx`) devices first, then native SPDK bdevs. URI parse errors are converted through `BdevError`.

State and dependencies: creation/destruction delegates state mutation to concrete device modules. Depends on `url`, concrete bdev modules, `SpdkBlockDevice`, and `BlockDevice` traits.

Risks and test signals: adding a new scheme requires implementing traits and updating this dispatcher. Strict unknown-parameter rejection is useful for safety but can break old URIs. Test each scheme parse plus plain-path AIO fallback.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/dev.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/device.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/device.rs

Purpose: Implements the generic `BlockDevice`, descriptor, and I/O handle traits for native SPDK bdevs.

Important APIs/types: `SpdkBlockDevice` wraps `UntypedBdev` and exposes size, block length, UUID, product/driver/name, alignment, I/O type support, stats, open, and event listener registration. `SpdkBlockDeviceDescriptor` wraps `UntypedDescriptorGuard` and creates I/O handles. `SpdkBlockDeviceHandle` wraps `UntypedBdevHandle` and implements DMA allocation plus read/write/compare/reset/unmap/write-zeroes/flush/NVMe admin/snapshot methods. `bdev_io_ctx_pool_init()` initializes a global memory pool for `IoCtx`. `bdev_event_callback()` translates SPDK remove/resize/media events into io-engine device events.

Control flow: vector I/O methods allocate `IoCtx`, optionally inject faults, submit SPDK bdev calls, and complete through `bdev_io_completion`, which maps status, invokes caller callback, returns context to the pool, and frees SPDK I/O.

State and dependencies: global event-dispatcher map and I/O context pool. Depends on SPDK bdev functions, io-engine core traits, fault injection feature, and replica snapshot factory.

Risks and test signals: I/O before pool initialization panics. Some dispatch errors map all negative reset/unmap/write-zeroes/flush failures to `ENOMEM`. Event listeners are keyed by device name and protected by a mutex. Tests should cover pool exhaustion, callback status mapping, event forwarding, and fault-injection feature behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/device.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/ftl.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/ftl.rs

Purpose: URI-backed implementation for SPDK FTL bdevs layered over base and cache bdevs.

Important APIs/types: `Ftl` stores name, alias, optional UUID, base bdev URI, and cache bdev URI. `TryFrom<&Url>` parses `uuid`, percent-decodes required `bbdev` and `cbdev` query parameters, and rejects unknowns. `Probe` recursively probes both nested URIs. `ftl_bdev_init_fn_cb()` bridges SPDK FTL init callback into a oneshot. `CreateDestroy::create()` creates nested base/cache bdevs, fills `spdk_ftl_conf`, calls `bdev_ftl_create_bdev`, waits for callback, sets UUID/alias, and returns the device name. `destroy()` deletes the FTL bdev and then destroys cache/base children.

Control flow: cache creation failure cleans up base. Immediate FTL create failure cleans both. Destroy records base-destroy result but still tries cache destroy.

State and dependencies: mutates multiple SPDK bdevs and FTL state. Depends on percent-encoded nested URIs, libspdk FTL APIs, and bdev API create/destroy.

Risks and test signals: nested URI encoding is fragile. Success requires callback delivery after initial zero return. Test create failure cleanup, destroy order, alias/UUID assignment, and recursive probe diagnostics.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/ftl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/loopback.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/loopback.rs

Purpose: URI adapter for exposing an already-existing SPDK bdev under a URI alias without creating a new backing device.

Important APIs/types: `Loopback` stores target bdev name, alias URI, and optional UUID. `TryFrom<&Url>` parses path segments and optional UUID, rejecting unknown params. `Probe` checks the named bdev exists. `create()` looks up the bdev, verifies UUID when provided, adds the alias, and returns the name. `destroy()` removes the alias and dispatches a loopback-removed event.

State and dependencies: mutates bdev alias list and device event dispatcher state. Depends on `UntypedBdev` lookup and `dispatch_loopback_removed`.

Integration points: dispatcher maps both `bdev` and `loopback` schemes here, so tests can use either URI style for existing bdevs.

Risks and test signals: destroy succeeds even if the bdev is absent, only warning. UUID mismatch is detected only on create. Test alias open/close behavior and event listeners that respond to loopback removal.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/loopback.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/lvs.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/lvs.rs

Purpose: URI-backed test/benchmark support for creating an LVS pool and an lvol in one bdev URI.

Important APIs/types: `Lvol` stores lvol name, size, and an `Lvs` spec. `Lvs` stores pool name, backing disk URI, mode, and optional encryption key. `TryFrom<&Url>` parses `lvol:///$name?size=...&lvs=...&disk=...`; nested `Lvs::try_from` parses pool `disk` and `mode`. `LvsMode` supports create, import, create_import, and purge. `CreateDestroy::create()` creates/imports the pool, destroys any existing lvol of the same name, and creates a new lvol. `destroy()` destroys the lvol and pool.

Control flow: purge wipes the first 8 MiB of the parsed backing bdev with write-zeroes before creating/importing. The code intentionally does not destroy the parsed bdev after wipe due to async NVMe deletion concerns.

State and dependencies: mutates pool metadata, backing disk contents, optional crypto vbdev settings, and lvol state. Depends on byte-unit parsing and `crate::lvs`.

Risks and test signals: defaulting unknown mode to import can mask typos. The URI shape is complex and testing-oriented. Validate create/import/purge modes, lvol replacement, and wipe behavior on disposable disks.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/lvs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/malloc.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/malloc.rs

Purpose: URI-backed implementation for SPDK malloc bdevs allocated from hugepage memory.

Important APIs/types: `Malloc` stores name, alias, block count, block size, optional UUID, and resize flag. `TryFrom<&Url>` parses `blk_size`, `size_mb`, `size`, `num_blocks`, `uuid`, and `resize`; validates block size is 512 or 4096; enforces exactly one size source. `Probe` rejects import mode because malloc devices are volatile. `create()` creates a malloc disk with `create_malloc_disk`, sets UUID/alias, or resizes an existing bdev when `resize` is present. `destroy()` asynchronously calls `delete_malloc_disk`. `try_resize()` calls `resize_malloc_disk`.

State and dependencies: mutates SPDK bdev registry and consumes hugepage memory. Depends on byte-unit parsing, SPDK malloc APIs, and callback oneshots for delete.

Risks and test signals: resize converts target size to whole MiB, losing sub-MiB precision. Missing hugepages surface as create failures. Test parameter validation, UUID aliasing, duplicate create versus resize, and cleanup after destroy.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/malloc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/mod.rs

Purpose: Public module facade and shared traits for io-engine block-device implementations.

Important APIs/types: re-exports generic device operations, `SpdkBlockDevice`, nexus types, and NVMe controller state. Declares internal modules for aio, dev, device, ftl, loopback, lvs, malloc, null, nvme, nvmf/nvmx, nexus, uring, and util. Defines `BdevCreateDestroy` as the combined trait of `CreateDestroy`, `Probe`, `GetName`, and `Debug`; `CreateDestroy` provides async create/destroy; `GetName` returns device name; `Probe` validates device availability with default `UriNotHandled`; `ProbeOpts` carries import/create context. Helper functions create `ProbeError`, probe files, probe existing bdevs, and recursively probe URIs. `PtplFileOps` abstracts reservation persistence file paths.

State and dependencies: `PtplFileOps` reads global `MayastorEnvironment` for PTPL directory and creates/deletes files as implemented by resources. Probe helpers inspect filesystem or SPDK bdev registry.

Risks and test signals: trait contracts are central to adding new bdev schemes. Probe defaults to unsupported unless implemented. Validate new modules by dispatcher parsing, probe behavior, create/destroy lifecycle, and PTPL path handling.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/mod.rs

Purpose: Nexus module facade, JSON-RPC registration entry point, shutdown orchestration, and runtime feature toggles for nexus behavior.

Important APIs/types: re-exports nexus creation (`nexus_create`, `nexus_create_v2`), `Nexus`, status/state/target/reservation types, child state/error types, iterators/lookups, persistence types (`NexusInfo`, `PersistentNexusInfo`, transactions), snapshot status/descriptor types, and internal channel/module/share/persistence helpers. `register_module(register_json)` registers the SPDK nexus module and optionally a JSON-RPC `nexus_share` method. `shutdown_nexuses()` collects mutable nexus iterators, destroys each nexus with persistence, and emits shutdown events. Static atomics toggle partial rebuild, nexus reset, channel debug, and all-thread nexus channel behavior.

Control flow: JSON-RPC share validates `protocol == "nvmf"`, looks up a bdev by name, shares it with ANA and controller ID range, and returns the share URI. Shutdown collects before iterating to avoid invalidation while SPDK destroys bdevs.

State and dependencies: mutates SPDK module registry, nexus lifecycle/persistence, event stream, bdev sharing state, and global atomic feature flags.

Risks and test signals: JSON-RPC comment notes it shares a bdev, not necessarily a nexus. Shutdown logs and emits events on errors rather than aborting the loop. Test registration, share RPC validation, clean shutdown persistence, and feature-flag-sensitive rebuild/reset behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/mod.rs -->
