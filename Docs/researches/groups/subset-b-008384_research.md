# Research Report: subset-b-008384

This grouped report covers the FoundationDB C API unit tests, C/C++/Rust workload bridge examples, and the Flow binding directory, tuple, subspace, allocator, and tester files assigned to `subset-b-008384`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/unit/unit_tests.cpp -->
## sources/storage-engines/foundationdb/bindings/c/test/unit/unit_tests.cpp

Purpose: comprehensive doctest-based regression coverage for the latest FoundationDB C API through the C++ convenience wrapper in `fdb_api.hpp`. The file sets up the FDB network, opens a database from a cluster file, scopes data under a caller-provided `prefix`, and exercises futures, transactions, range reads, mapped range reads, tuple/versionstamp behavior, watches, special key space, admin calls, error predicates, and allocator cleanup.

Important APIs and functions: `fdb_check`, `fdb_open_database`, `wait_future`, `strinc_str`, `insert_data`, `get_value`, `get_range`, and `get_mapped_range` centralize error handling and retry-friendly access. The test cases cover `FDBFuture` getters, callbacks, cancellation, memory release, `FDBTransaction` read/write/range/atomic/watch/conflict APIs, database options, special key space reads/writes, `fdb_database_get_server_protocol`, reboot/recovery/snapshot calls, and `fdb_error_predicate`.

Control flow: most transaction tests use a retry loop around `wait_future`, call `tr.on_error(err)` for retryable failures, and then assert once a successful attempt returns. Setup helpers clear the prefix range before installing test data. The `main` function selects `FDB_API_VERSION`, optionally configures an external client library, starts the network on a thread, runs doctest, destroys the database, and stops the network.

State and persistence: tests mutate real database keys under `prefix`, tuple-encoded record/index keys, system keys with access options, and special keys under `\xff\xff/tracing`. They explicitly reset database options changed during a test, such as transaction size limits and max watches. Watch and conflict tests rely on transaction lifecycle state, commit versions, and retry semantics.

Dependencies and integration points: depends on generated C API options, `foundationdb/fdb_c.h`, doctest, RapidJSON status parsing, Flow random/UID/config utilities, and `fdbclient/Tuple`. It validates the binding contract between the public C API, the wrapper classes, and a live local/test cluster.

Risks: tests assume a reachable single-process cluster for `fdb_database_reboot_worker`; comments note sensitivity to configuration and TSAN. Some assertions are guarded when commit unknown/retry behavior means an atomic operation may have committed multiple times. Hard-coded error codes make this an API compatibility sentinel but can require updates if semantics intentionally change.

Test signals: this file is itself a high-value integration test suite. It signals expected behavior for future memory ownership, callback ordering, read-your-writes options, range pagination flags, mapped-range restrictions, versionstamped mutations, special key space tracing, network thread blocking protection, and thread-local allocation cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/unit/unit_tests.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/unit/unit_tests_version_510.cpp -->
## sources/storage-engines/foundationdb/bindings/c/test/unit/unit_tests_version_510.cpp

Purpose: targeted C API compatibility test for API header version 510. It intentionally defines `FDB_API_VERSION 510`, selects that version, and uses older cluster/database creation functions to verify compatibility shims.

Important APIs and types: local RAII wrappers `Future` and `Transaction` destroy `FDBFuture*` and `FDBTransaction*`. Tests call `fdb_database_create_transaction`, `fdb_transaction_set`, `fdb_transaction_commit`, `fdb_transaction_get`, `fdb_future_get_value`, and `fdb_transaction_get_read_version`. `main` uses `fdb_create_cluster`, `fdb_future_get_cluster`, `fdb_cluster_create_database`, and `fdb_future_get_database`, which are important older-version surface area.

Control flow: the executable selects API version 510, starts the network thread, creates a cluster and database through the versioned API, runs doctest, destroys the database, and stops the network. `SET_AND_GET` commits a prefixed key/value and reads it in a second transaction. `GRV` only verifies a read version future completes.

State and persistence: persists one test key under the provided prefix and leaves cleanup to outer test isolation. The database handle is global for the small suite.

Dependencies and integration points: uses generated options, `foundationdb/fdb_c.h`, doctest, and Flow config. It integrates with the same cluster-file/prefix harness as latest-version tests while intentionally exercising old ABI behavior.

Risks: coverage is intentionally narrow and does not retry on transient transaction failures. The comments state the main motivation is assembly/emulation support for older API versions, so failures here likely point to ABI/version-dispatch regressions rather than directory or tuple logic.

Test signals: strong signal for API version selection and old handle acquisition paths; weak signal for broader transactional behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/unit/unit_tests_version_510.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/CWorkload.c -->
## sources/storage-engines/foundationdb/bindings/c/test/workloads/CWorkload.c

Purpose: sample external C workload implementation for the simulation workload ABI declared by `foundationdb/CWorkload.h`. It demonstrates how a C shared library exports a factory and implements setup/start/check/metrics/timeout/free callbacks.

Important APIs and types: `CWorkload` stores workload name, client id, and `FDBWorkloadContext`. `DelayParameter` keeps asynchronous delay callback state. The `WITH` macro calls function pointers in context, promise, string, and metric vtables. `workloadCFactory` is the exported entry point returning `FDBWorkload` with `FDB_WORKLOAD_API_VERSION` and `CWorkload_vt`.

Control flow: the factory copies the borrowed workload name, reads client metadata, logs options twice to show option consumption semantics, allocates `CWorkload`, and returns the vtable. `setup` and `check` trace and immediately resolve promises. `start` schedules a context delay whose callback logs elapsed time, sends the promise, frees the promise, and frees callback parameters. `getMetrics` reserves and pushes a `test=42` metric.

State and persistence: no database state is touched despite receiving `FDBDatabase*`. Runtime state is heap allocated per workload and callback. Promise ownership is explicitly released by `send` and `free`.

Dependencies and integration points: bridges dynamic C workloads into FoundationDB simulation, requiring `fdb_future_set_callback` and the workload context vtable. It is built as a shared object such as `libc_workload.so`.

Risks: manual memory management is central. Misordered promise free/send or failing to free copied strings would leak or double-free. The delay callback casts callback types across C declarations, so ABI drift in `CWorkload.h` is high risk.

Test signals: validates C workload lifecycle, tracing, option retrieval, asynchronous delay, metrics, and timeout plumbing.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/CWorkload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/Cargo.toml -->
## sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/Cargo.toml

Purpose: Rust crate manifest for the external Rust workload sample. It builds a `cdylib` named `rust-workload` so the FoundationDB C workload loader can load it as a dynamic library.

Important settings: package version is `0.1.0`, edition is 2021, library crate type is `cdylib`, and `bindgen 0.72.1` is a build dependency. The manifest has no runtime dependencies, keeping the example focused on generated FFI bindings and local wrapper code.

Control flow and build integration: Cargo invokes `build.rs` before compiling, which generates Rust bindings from `foundationdb/CWorkload.h` into `OUT_DIR`. The Rust source then includes those generated bindings.

State and persistence: no runtime state is defined here; its persistence significance is in producing a dynamic artifact compatible with the simulation workload loader.

Dependencies and integration points: integrates Cargo with FoundationDB's C workload header. The `cdylib` output must match the test configuration in `test_file.toml`, which refers to `libraryName = 'rust_workload'`.

Risks: `bindgen` output is sensitive to header layout, include paths, clang availability, and platform naming conventions for dynamic libraries.

Test signals: successful cargo build signals that the C workload ABI can be bound from Rust for this sample.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/build.rs -->
## sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/build.rs

Purpose: Cargo build script that generates Rust FFI bindings for the FoundationDB workload ABI header.

Important APIs and functions: `bindgen::Builder::default().header(c_workload_h).generate()` reads `../../../foundationdb/CWorkload.h`; `println!("cargo:rerun-if-changed=...")` ties rebuilds to header changes; `write_to_file(out_path.join("bindings.rs"))` stores generated bindings in Cargo `OUT_DIR`.

Control flow: resolve a relative header path, tell Cargo when to rerun, generate bindings, resolve `OUT_DIR`, and write `bindings.rs`. Failures panic with clear `expect` messages.

State and persistence: persists only generated Rust binding code in Cargo's build output directory. It does not modify repository files.

Dependencies and integration points: depends on `bindgen`, clang/libclang availability, and the header path being valid relative to the crate root. `src/bindings.rs` includes the generated output at compile time.

Risks: relative path drift or header dependency changes not tracked by the single rerun directive can lead to stale or failed generated bindings. Generated layout must match the C/C++ workload loader ABI.

Test signals: build success validates header parseability and Rust wrapper compatibility with current ABI definitions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/build.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/src/bindings.rs -->
## sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/src/bindings.rs

Purpose: safe-ish Rust convenience layer over bindgen-generated C workload ABI definitions. It converts raw generated types into Rust wrapper types for workload context, promises, metrics, string conversion, and severity values.

Important APIs and types: re-exports `FDBDatabase`, `FDBMetrics`, `FDBPromise`, `FDBWorkload`, `FDBWorkloadContext`, `FDBWorkload_VT`, and `OpaqueWorkload`. Defines `WorkloadContext`, `Promise`, `Metrics`, `Metric`, and `Severity`. `str_from_c` and `str_for_c` handle C string conversion. The `with!` macro calls vtable functions from generated C structs.

Control flow: wrapper methods convert Rust arguments to temporary `CString`s, build raw structs like `FDBStringPair` or `FDBMetric`, invoke C vtable calls, then rely on synchronous consumption by the C++ side. `Promise::send` consumes the promise wrapper; `Drop` calls the promise free vtable. `Metrics::extend` reserves then pushes each metric.

State and persistence: wraps borrowed simulation context and promise/metrics sinks. Option retrieval intentionally frees the returned `FDBString` and treats an empty default as `None`.

Dependencies and integration points: includes generated bindings from `OUT_DIR`, and is consumed by `lib.rs` and `mock.rs` to implement an exported Rust workload factory.

Risks: `unwrap_unchecked` assumes all vtable function pointers are present. Temporary C string lifetimes are only safe if the C++ callee copies synchronously. `Promise` drop always frees, so ownership must not be duplicated after `send`.

Test signals: exercises Rust bindings for trace, options, client metadata, randomness, promise completion, and metrics through the mock workload.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/src/bindings.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/src/lib.rs -->
## sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/src/lib.rs

Purpose: Rust workload framework layer that maps Rust traits to the C workload ABI. It defines how concrete Rust workloads are boxed, exposed through an `FDBWorkload` vtable, and created by an exported factory symbol.

Important APIs and types: `MockDatabase` is a non-null `FDBDatabase` pointer placeholder. `RustWorkload` declares lifecycle methods `setup`, `start`, `check`, `get_metrics`, and `get_check_timeout`, plus an associated static vtable. `RustWorkloadFactory` defines `create`. `register_factory!` emits the `workloadCFactory` symbol expected by the loader.

Control flow: `RustWorkload::wrap` boxes `self`, stores the raw pointer as `OpaqueWorkload`, and assigns the static vtable. Each unsafe extern callback casts the opaque pointer back to `W`, wraps raw database/promise/metrics arguments, and calls the Rust trait method. `workload_drop` reconstructs and drops the boxed workload.

State and persistence: workload state lives in a Rust `Box` controlled by the C ABI free callback. No database persistence is implemented here.

Dependencies and integration points: uses the wrappers from `bindings.rs` and is extended by `mock.rs`. It is the Rust analog of `CWorkload.c` and must match `CWorkload.h` layout exactly.

Risks: all FFI callbacks are unsafe and assume valid non-null pointers from the loader. Double-free or use-after-free can occur if `free` is called while callbacks still reference the workload. The macro must be invoked once to avoid duplicate symbol definitions.

Test signals: validates that Rust trait implementations can be loaded as C ABI workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/src/mock.rs -->
## sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/src/mock.rs

Purpose: concrete Rust mock workload used to test the Rust workload ABI bridge. It mirrors the C workload sample with lifecycle logging, tracing, metrics, option consumption, and factory selection by workload name.

Important APIs and types: `MockWorkload` stores `name`, `client_id`, and `WorkloadContext`. It implements `RustWorkload`. `MockFactory` implements `RustWorkloadFactory`, reads `client_id`, `client_count`, `FDB_WORKLOAD_API_VERSION`, server workload API version, and option `my_rust_option`.

Control flow: factory creation logs metadata, reads the same option twice, and constructs a `MockWorkload` only for `MockWorkload`, panicking on unknown names. `setup`, `start`, and `check` trace a `Test` event with `Layer=Rust` and phase-specific stage, then resolve the promise. `get_metrics` pushes `test=42`; `get_check_timeout` returns 3000; `Drop` logs free.

State and persistence: no database writes. Runtime state is held in the boxed workload created by `wrap` in `lib.rs`.

Dependencies and integration points: registered by `register_factory!(MockFactory)` as `workloadCFactory`; selected by `test_file.toml` via `workloadName = 'MockWorkload'`.

Risks: panic on unknown workload name crosses the dynamic library boundary and may abort the test process. Printed option label says `my_c_option` while reading `my_rust_option`, which is harmless but confusing.

Test signals: confirms Rust lifecycle, trace, metric, timeout, factory, drop, and option retrieval paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/src/mock.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/test_file.toml -->
## sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/test_file.toml

Purpose: FoundationDB simulation test configuration for loading and running the Rust external workload.

Important settings: defines a single `[[test]]` named `Rust_CAPI_Test` with one `External` workload. `useCAPI = true` selects the C workload ABI, `libraryPath = './target/release'`, `libraryName = 'rust_workload'`, and `workloadName = 'MockWorkload'` target the Rust cdylib and factory implementation. `my_rust_option = 'my_value'` feeds option retrieval in `MockFactory`.

Control flow: the simulator reads this TOML, loads the dynamic library from the release target directory, invokes `workloadCFactory`, and then drives setup/start/check/metrics through the returned vtable.

State and persistence: no direct database state; it configures runtime dynamic loading and workload options.

Dependencies and integration points: coupled to Cargo output naming, the `MockWorkload` string in `mock.rs`, and the external workload loader.

Risks: path/name mismatches are likely if Cargo target names or platform library prefixes/suffixes differ. Release build must exist before running this test file.

Test signals: verifies end-to-end loading of the Rust workload bridge when paired with a built cdylib.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/RustWorkload/test_file.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/SimpleWorkload.cpp -->
## sources/storage-engines/foundationdb/bindings/c/test/workloads/SimpleWorkload.cpp

Purpose: C++ workload implementation for C API simulation testing. It populates many keys through asynchronous actor-like state machines, then runs concurrent read/commit clients and reports throughput/retry metrics.

Important APIs and types: `SimpleWorkload` derives from `FDBWorkload`. Nested `ActorBase` converts C futures into callback-driven actor states with one outstanding wait. `PopulateActor` batches inserts and commits with retry handling. `ClientActor` randomly reads keys, commits after `opsPerTx`, tracks gets/commits/retries, and retries on errors. `FDBWorkloadFactoryT<SimpleWorkload>` registers it by name.

Control flow: `init` reads options (`numTuples`, `numActors`, `insertsPerTx`, `opsPerTx`, `runFor`), seeds RNG, and selects API version. `setup` skips population for client 0 and otherwise partitions insert ranges across populate actors. `start` launches client actors, aggregates per-actor rates on completion, and resolves the promise. `check` returns success.

State and persistence: writes keys under `csimple/` with numeric string values. Transaction objects are reused/reset across retries and commits. Metrics vectors persist per workload instance until `getMetrics`.

Dependencies and integration points: uses the C API directly, `foundationdb/CppWorkload.h` through `workloads.h`, and the workload factory registry.

Risks: callback state assumes at most one outstanding wait per actor and terminates otherwise. `accumulateMetric` divides by vector size, so no completed actors would be unsafe. Error callbacks capture `error` inconsistently in two lambdas, making diagnostic output fragile.

Test signals: provides load-oriented validation for async callbacks, retry loops, commits, random reads, metrics, and workload factory registration.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/SimpleWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/workloads.cpp -->
## sources/storage-engines/foundationdb/bindings/c/test/workloads/workloads.cpp

Purpose: implementation of the C++ workload factory registry exported to the simulation workload loader.

Important APIs and functions: `FDBWorkloadFactoryImpl::factories()` owns a static map from workload name to `IFDBWorkloadFactory*`; `create` looks up a name and returns a `shared_ptr<FDBWorkload>` or null; `workloadFactory(FDBLogger*)` exports a singleton `FDBWorkloadFactoryImpl`.

Control flow: workload implementations instantiate `FDBWorkloadFactoryT<T>` statics, which insert themselves into the static map before the loader calls `workloadFactory`. The loader then asks the returned factory to create named workloads.

State and persistence: only process-global registry state in the static map and factory singleton. No database state.

Dependencies and integration points: depends on `workloads.h` and `foundationdb/CppWorkload.h`; integrated by dynamic library loading and `DLLEXPORT` symbol lookup.

Risks: static initialization order matters between registration objects and factory lookup. Raw factory pointers are stored without ownership, assuming registration statics outlive all lookups.

Test signals: creation success for `SimpleWorkload` confirms registry wiring.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/workloads.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/workloads.h -->
## sources/storage-engines/foundationdb/bindings/c/test/workloads/workloads.h

Purpose: declares the C++ workload factory registry used by external workload shared libraries.

Important APIs and types: `IFDBWorkloadFactory` abstracts typed workload construction. `FDBWorkloadFactoryImpl` derives from `FDBWorkloadFactory`, owns static `factories()`, and implements name-based creation. Template `FDBWorkloadFactoryT<WorkloadType>` registers a workload type by name and creates `shared_ptr<WorkloadType>`. `extern "C" DLLEXPORT FDBWorkloadFactory* workloadFactory(FDBLogger*)` is the loader entry point.

Control flow: including this header in a workload file allows a static `FDBWorkloadFactoryT` instance to self-register with the map at load time.

State and persistence: defines process-global registration state, not database persistence.

Dependencies and integration points: includes `foundationdb/CppWorkload.h`; used by `SimpleWorkload.cpp` and implemented in `workloads.cpp`.

Risks: global static registration can fail silently if object files are not linked into the shared library. The registry uses raw pointers to static factory objects.

Test signals: exported `workloadFactory` plus registered names are required for any C++ workload test to run.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/workloads/workloads.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/CMakeLists.txt -->
## sources/storage-engines/foundationdb/bindings/flow/CMakeLists.txt

Purpose: build definition for the `fdb_flow` static library and its tester/package targets.

Important targets: `SRCS` lists directory layer, partition/subspace, loaner types, high contention allocator, tuple, and Flow C API wrapper sources. `add_flow_target(STATIC_LIBRARY NAME fdb_flow ...)` builds the library. It links `fdb_c` and `fdbclient`, exposes include directories, and adds the `tester` subdirectory.

Control flow: for non-IDE builds it collects headers, computes snapshot suffix, creates package directories, defines a tarball custom command copying the library and headers, adds `package_flow`, and hooks it into `packages`.

State and persistence: build artifacts include a static library and optional `fdb-flow-<version>` tarball under build package directories.

Dependencies and integration points: integrates Flow bindings with the top-level CMake helpers, FDB version variables, package aggregation, `fdb_c`, `fdbclient`, and tester executable.

Risks: packaging assumes x86_64 tarball naming and copies only headers detected from `SRCS`. Missing a header in `SRCS` can omit it from package output.

Test signals: successful build of `fdb_flow` and `fdb_flow_tester` validates compile/link integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/DirectoryLayer.cpp -->
## sources/storage-engines/foundationdb/bindings/flow/DirectoryLayer.cpp

Purpose: implements the Flow binding directory layer, including directory metadata storage, prefix allocation, creation/opening, listing, moving, recursive removal, partition delegation, and version compatibility checks.

Important APIs and functions: static metadata keys define node/content layout. `find` walks path components through subdirectory mapping keys. `checkVersionInternal` validates or initializes metadata version. `getPrefix`, `nodeContainingKey`, and `isPrefixFree` allocate or validate content prefixes. `createInternal`, `_createOrOpenInternal`, `listInternal`, `moveInternal`, `removeRecursive`, `removeInternal`, and `existsInternal` implement the main asynchronous behavior.

Control flow: public methods wrap `this` in `Reference<DirectoryLayer>` and delegate to actor-style helper functions. Creation checks version, validates manual prefix policy, finds existing nodes, delegates into partitions when needed, allocates/free-checks a prefix, writes parent subdir mapping and node layer metadata, then returns a `DirectorySubspace` or `DirectoryPartition`. List/remove operations page through ranges until `more` is false.

State and persistence: stores version at `rootNode.pack(VERSION_KEY)`, subdirectory mappings under `SUB_DIR_KEY`, node layer at `LAYER_KEY`, allocator state under `hca`, and user content under allocated prefixes. Removes clear both content prefix ranges and node metadata ranges.

Dependencies and integration points: uses `Subspace`, `Tuple`, `HighContentionAllocator`, `DirectorySubspace`, `DirectoryPartition`, Flow actors, and `Transaction` wrapper range/read/write APIs.

Risks: correctness depends on tuple/key range boundaries, prefix-free checks, and partition path arithmetic. Metadata version is read as `uint32_t*`, so endian/alignment assumptions matter. Manual prefix policy differs for root versus partitions.

Test signals: exercised by `DirectoryTester.cpp` instruction functions and by cross-binding directory layer compatibility tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/DirectoryLayer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/DirectoryLayer.h -->
## sources/storage-engines/foundationdb/bindings/flow/DirectoryLayer.h

Purpose: declares the Flow `DirectoryLayer` implementation of `IDirectory` plus the nested `Node` traversal helper and constants defining directory metadata layout.

Important APIs and types: public methods implement create/open/createOrOpen/exists/list/move/remove against `Reference<Transaction>`. Constants include default node/content subspaces, `PARTITION_LAYER`, metadata keys, version, and allocator key. `Node` carries directory layer reference, optional node subspace, current path, target path, layer metadata, and loaded flag.

Control flow: public APIs dispatch to private `createOrOpenInternal`, `checkVersion`, `initializeDirectory`, `nodeWithPrefix`, `contentsOfNode`, and path helpers. `Node` supports lazy metadata loading and partition detection.

State and persistence: fields `rootNode`, `nodeSubspace`, `contentSubspace`, `allocator`, `allowManualPrefixes`, and `path` define where directory metadata and content live and whether callers can pick prefixes.

Dependencies and integration points: includes `IDirectory.h`, `DirectorySubspace.h`, and `HighContentionAllocator.h`. Friend access from `DirectoryPartition` and helper actors relies on exposed internals.

Risks: the header exposes many internals as public/commented private, so external code can depend on implementation details. `Path` uses vectors of `Standalone<StringRef>`, requiring careful arena ownership.

Test signals: API surface mirrors other FoundationDB directory layer bindings and is used by `DirectoryTester`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/DirectoryLayer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/DirectoryPartition.h -->
## sources/storage-engines/foundationdb/bindings/flow/DirectoryPartition.h

Purpose: represents a directory layer partition. A partition can be navigated as an `IDirectory`, but cannot be used directly as a `Subspace`.

Important APIs and types: `DirectoryPartition` derives from `DirectorySubspace`, constructs a nested `DirectoryLayer` rooted under the partition prefix, stores the parent directory layer, and overrides `key`, `contains`, `pack`, `unpack`, `range`, `subspace`, and `get` to throw `cannot_use_partition_as_subspace`.

Control flow: constructor builds a nested directory layer with node subspace `DEFAULT_NODE_SUBSPACE_PREFIX.withPrefix(prefix)` and content subspace `prefix`, sets nested layer path to the partition path, and marks layer as `PARTITION_LAYER`. `getDirectoryLayerForPath` returns the parent for empty path operations and the nested layer for subpaths.

State and persistence: partition metadata lives in the parent directory, while subdirectories/content under the partition use nested metadata and content prefixes rooted under the partition prefix.

Dependencies and integration points: tightly coupled to `DirectoryLayer`, `DirectorySubspace`, and directory operation delegation in `DirectoryLayer.cpp`.

Risks: path delegation rules are subtle; using a partition as a normal subspace is intentionally blocked to avoid ambiguous content ranges.

Test signals: directory tests should verify partition creation, operations inside partitions, and errors for subspace methods.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/DirectoryPartition.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/DirectorySubspace.cpp -->
## sources/storage-engines/foundationdb/bindings/flow/DirectorySubspace.cpp

Purpose: implements directory handles that are also usable as subspaces, forwarding directory operations relative to the stored directory path.

Important APIs and functions: constructor initializes `Subspace(prefix)`, `directoryLayer`, `path`, and `layer`. `create`, `open`, `createOrOpen`, `exists`, `list`, `move`, `moveTo`, `remove`, and `removeIfExists` delegate to an appropriate `DirectoryLayer` using `getPartitionSubpath`. Accessors return layer/path/directory layer.

Control flow: relative operations calculate a partition-relative subpath by stripping the owning directory layer path from `this->path` and appending the requested path. `moveTo` verifies the destination absolute path remains inside the same directory layer partition before calling layer `move`.

State and persistence: no direct metadata writes; all persistence is delegated to `DirectoryLayer`. The object stores immutable path/layer identity and raw prefix through `Subspace`.

Dependencies and integration points: used as the returned handle from directory open/create and as the base for `DirectoryPartition`.

Risks: incorrect `directoryLayer->getPath()` sizes or path prefix comparisons can produce wrong relative paths. `getDirectoryLayerForPath` is virtual so partitions alter delegation behavior.

Test signals: directory tester operations on currently selected directory/subspace exercise these relative forwarding methods.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/DirectorySubspace.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/DirectorySubspace.h -->
## sources/storage-engines/foundationdb/bindings/flow/DirectorySubspace.h

Purpose: declares the combined `IDirectory` and `Subspace` handle returned by directory layer operations.

Important APIs and types: exposes directory lifecycle operations relative to this directory, subspace functionality inherited from `Subspace`, and accessors `getDirectoryLayer`, `getLayer`, and `getPath`. Protected helpers `getPartitionSubpath` and `getDirectoryLayerForPath` allow partition-specific behavior.

Control flow: callers can treat normal directory handles as subspaces for packing/unpacking keys, or as directories for nested operations.

State and persistence: stores `Reference<DirectoryLayer> directoryLayer`, absolute `Path path`, and layer metadata string. Raw prefix is owned by the `Subspace` base class.

Dependencies and integration points: includes `IDirectory.h`, `DirectoryLayer.h`, and `Subspace.h`; returned by `DirectoryLayer::contentsOfNode`.

Risks: multiple inheritance means object lifetime and virtual dispatch must remain stable across `IDirectory` and `Subspace` uses. Path and layer values are copied `Standalone`/vector data to preserve memory safety.

Test signals: all directory handles in tester flows are instances of this class or `DirectoryPartition`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/DirectorySubspace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/FDBLoanerTypes.h -->
## sources/storage-engines/foundationdb/bindings/flow/FDBLoanerTypes.h

Purpose: supplies Flow-binding stand-ins for common FoundationDB client types: keys, values, key selectors, key-value pairs, range results, range limits, key ranges, and debug describe helpers.

Important APIs and types: defines `KeyRef`, `ValueRef`, `Version`, `Key`, `Value`, `KeySelectorRef`, `KeySelector`, `KeyValueRef`, `RangeResultRef`, `GetRangeLimits`, and `KeyRangeRef`. Helpers implement `keyAfter`, key selector constructors, range pagination helpers, range intersection, limit accounting declarations, and container `describe` functions.

Control flow: range reads return `RangeResultRef`, whose `more`, `readThrough`, `nextBeginKeySelector`, and `nextEndKeySelector` guide pagination. `KeyRangeRef` validates begin <= end and throws `inverted_range`.

State and persistence: no database writes; these types carry arena-backed views and standalones used by wrapper futures and directory logic.

Dependencies and integration points: used throughout `fdb_flow.*`, `Subspace`, `DirectoryLayer`, `Tuple`, and tests. `FDBStandalone` in `fdb_flow.h` often wraps these types to keep raw C future memory alive.

Risks: many types are borrowed `StringRef`/`VectorRef` views, so lifetime and arena ownership are critical. `keyAfter("\xff\xff")` special-cases the maximum system key boundary.

Test signals: range and directory tests validate key selector/range behavior indirectly.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/FDBLoanerTypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/HighContentionAllocator.cpp -->
## sources/storage-engines/foundationdb/bindings/flow/HighContentionAllocator.cpp

Purpose: implements FoundationDB directory layer high-contention prefix allocation for the Flow binding.

Important APIs and functions: `_allocate` is the actor implementation; `HighContentionAllocator::allocate` wraps it; `windowSize` selects allocation window sizes of 64, 1024, or 8192 depending on start.

Control flow: allocation reads the latest counter window, atomically increments a counter, advances the window when count pressure exceeds half the window, clears old counters/recent keys with no-write-conflict range where appropriate, then randomly probes recent candidate slots. It writes the candidate recent key with no-write-conflict, waits for latest counter and candidate read, adds a write conflict on unused candidate, and returns the candidate encoded as a tuple.

State and persistence: uses two subspaces: `counters` for window counters and `recent` for recently claimed candidates. The returned value becomes a directory prefix after `DirectoryLayer` prepends content subspace.

Dependencies and integration points: uses `Subspace`, `Tuple`, `deterministicRandom`, transaction atomic add, range reads, reads, sets, conflict keys, and transaction option `NEXT_WRITE_NO_WRITE_CONFLICT_RANGE`.

Risks: concurrency correctness depends on conflict ranges and recent candidate writes. Comments note thread safety would need locking if accessed concurrently outside the expected actor model. Values are interpreted as 8-byte integers and invalid metadata throws.

Test signals: indirectly tested by concurrent directory creation and prefix allocation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/HighContentionAllocator.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/HighContentionAllocator.h -->
## sources/storage-engines/foundationdb/bindings/flow/HighContentionAllocator.h

Purpose: declares the allocator used by `DirectoryLayer` to assign unique directory prefixes under contention.

Important APIs and types: constructor accepts a parent `Subspace` and derives `counters` as child 0 and `recent` as child 1. Public `allocate` returns a future string prefix; static `windowSize` exposes the range sizing policy.

Control flow: callers hold a transaction and await `allocate`; implementation performs all reads/writes inside that transaction so allocation participates in commit conflict checking.

State and persistence: allocator state is stored under the supplied subspace. The header itself only stores the two child subspaces.

Dependencies and integration points: includes `Subspace.h`; used by `DirectoryLayer` as `allocator(rootNode.get(HIGH_CONTENTION_KEY))`.

Risks: API is small, but callers must not treat allocation as durable until the surrounding transaction commits.

Test signals: directory creation tests cover this through automatic prefix assignment.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/HighContentionAllocator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/IDirectory.h -->
## sources/storage-engines/foundationdb/bindings/flow/IDirectory.h

Purpose: abstract interface for Flow directory-layer operations.

Important APIs and types: defines `Path` as `std::vector<Standalone<StringRef>>` and pure virtual methods for create, open, createOrOpen, exists, list, move, moveTo, remove, removeIfExists, getDirectoryLayer, getLayer, and getPath.

Control flow: concrete `DirectoryLayer`, `DirectorySubspace`, and `DirectoryPartition` implementations provide async methods returning Flow `Future`s and directory/subspace references.

State and persistence: interface only; persistent effects are defined by implementations.

Dependencies and integration points: includes Flow primitives and `fdb_flow.h`, forward declares directory classes, and provides the shared contract used by tester instruction functions.

Risks: all operations are transaction-scoped; callers must commit separately. `Path` component ownership through `Standalone<StringRef>` must remain intact across async boundaries.

Test signals: `DirectoryTester.cpp` interacts mostly through this interface, so it is the central compatibility surface.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/IDirectory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/Node.cpp -->
## sources/storage-engines/foundationdb/bindings/flow/Node.cpp

Purpose: implements `DirectoryLayer::Node`, the traversal state object used while resolving paths in the directory layer.

Important APIs and functions: constructor stores directory layer, optional subspace, current path, target path, and initializes `loadedMetadata=false`. `exists` checks subspace presence. `loadMetadata` reads the node layer key. `isInPartition`, `getPartitionSubpath`, and `getContents` interpret loaded metadata.

Control flow: `find` in `DirectoryLayer.cpp` constructs and updates `Node` instances while walking path components. `loadMetadata` must keep the node alive while its future is outstanding, as noted by the comment. Once metadata is loaded, partition checks can decide whether to delegate.

State and persistence: reads layer metadata from `subspace.pack(LAYER_KEY)` and caches it in the node. Does not write database state.

Dependencies and integration points: includes `DirectoryLayer.h`, uses transaction `get`, `DirectoryLayer::contentsOfNode`, and `PARTITION_LAYER`.

Risks: callers must not call `isInPartition` or `getContents` before metadata is loaded; assertions enforce this in debug builds. Async load on a pointer to `Node` requires lifetime discipline.

Test signals: all directory operations exercise node traversal and partition detection.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/Node.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/Subspace.cpp -->
## sources/storage-engines/foundationdb/bindings/flow/Subspace.cpp

Purpose: implements tuple-based subspace key packing, unpacking, range construction, containment, and nested subspace derivation.

Important APIs and functions: constructors combine raw prefixes and packed tuples into `rawPrefix`. `key` returns the prefix. `pack` prefixes packed tuple bytes. `unpack` validates containment before tuple unpacking. `range` builds `[prefix+tuple+\x00, prefix+tuple+\xff)` key ranges. `contains`, `subspace`, and `get` provide prefix checks and child subspaces.

Control flow: range/key construction uses arena-backed vectors inside returned `Standalone`/`KeyRange` values. `unpack` throws `key_not_in_subspace` on invalid prefixes.

State and persistence: owns only an in-memory `rawPrefix`; no database IO. Persistent behavior is by convention: all keys packed through the subspace share the prefix.

Dependencies and integration points: uses `Tuple`, `FDBLoanerTypes`, and Flow arenas. Directory handles inherit this behavior through `DirectorySubspace`.

Risks: range boundaries rely on the tuple layer guarantee that appending `\x00` and `\xff` captures all child tuple encodings. Comments note a desired test around arena usage.

Test signals: directory tester pack/unpack/range/contains/open_subspace instructions validate these methods.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/Subspace.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/Subspace.h -->
## sources/storage-engines/foundationdb/bindings/flow/Subspace.h

Purpose: declares the Flow subspace abstraction for prefixing tuple-encoded keys.

Important APIs and types: constructors accept a `Tuple` plus raw prefix or raw prefix alone. Methods expose `key`, `contains`, `pack`, `unpack`, `range`, `subspace`, and `get`, with template and string convenience overloads. `packNested` and `getNested` handle nested tuple items.

Control flow: callers build typed tuple keys without manually concatenating byte prefixes. Child subspaces are derived by appending packed tuple elements to the current raw prefix.

State and persistence: stores `Standalone<VectorRef<uint8_t>> rawPrefix`, preserving prefix bytes across async use.

Dependencies and integration points: includes Flow, `fdb_flow.h`, and `Tuple.h`; inherited by `DirectorySubspace`.

Risks: template overloads rely on `Tuple::append` support for each type. Invalid unpacking throws at runtime rather than returning optional.

Test signals: used heavily by tuple, directory, and allocator code paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/Subspace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/Tuple.cpp -->
## sources/storage-engines/foundationdb/bindings/flow/Tuple.cpp

Purpose: implements FoundationDB tuple wire encoding/decoding for Flow bindings, including type ordering, nested tuples, UUIDs, floats, doubles, booleans, ints, strings, nulls, and 96-bit versionstamps.

Important APIs and functions: constants define tuple type codes. Helpers handle string terminators, big-endian float/double conversion, and order-preserving floating point bit adjustment. `Tuple(StringRef)` parses packed data and computes element offsets. `append*` methods encode values. `get*` methods decode by type and index. `range`, `subTuple`, comparison operators, and `Uuid` methods complete the tuple API.

Control flow: unpack scans bytes, tracks nested tuple depth, and records offsets only at top level. String encodings escape embedded nulls as `\x00\xff`. Integers use variable-length signed encodings around `INT_ZERO_CODE`. Floats/doubles convert to sortable byte order. Nested tuple encoding escapes null elements and terminates with null.

State and persistence: owns packed tuple bytes in an arena-backed vector and an offsets vector. Packed bytes are persisted directly as keys or values by subspace and directory code.

Dependencies and integration points: depends on `fdb_flow.h`, `TupleVersionstamp`, endian helpers, Flow errors, and arena types. Used by C API mapped-range tests, directory layer metadata, subspaces, allocator candidates, and tester stack values.

Risks: decoding uses asserts for bounds in some paths and throws for invalid types/depth. Strict aliasing/alignment around float/int casts and endian conversion are portability-sensitive. Versionstamp size must remain 12 bytes for tuple-layer compatibility.

Test signals: latest C API unit tests cover versionstamp tuple behavior and mapped-range tuple mappers; directory tester exercises packing/unpacking across many operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/Tuple.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/Tuple.h -->
## sources/storage-engines/foundationdb/bindings/flow/Tuple.h

Purpose: declares the tuple and UUID API exposed by the Flow binding.

Important APIs and types: `Versionstamp` aliases `TupleVersionstamp`. `Uuid` validates and compares 16-byte UUID payloads. `Tuple` exposes `unpack`, `append` overloads for tuple/string/int/bool/float/double/UUID/null/versionstamp/nested, `pack`, typed getters, `range`, `subTuple`, and bytewise comparisons. `ElementType` describes decoded item types.

Control flow: users incrementally append items then call `pack`; unpacked tuples allow indexed type inspection and value retrieval. Comparison operators compare packed byte representation to preserve database sort order.

State and persistence: tuple data is arena-backed packed bytes plus element offsets. Packed tuple bytes become stable database key components.

Dependencies and integration points: includes `fdb_flow.h` and `fdbclient/TupleVersionstamp.h`; used by subspaces, directory layer, allocator, and tests.

Risks: API exposes typed getters that throw on wrong type or bad index. Users must choose UTF8 flag correctly for strings because bytes and UTF8 have distinct type codes.

Test signals: unit tests verify versionstamp tuple support and invalid versionstamp sizing; directory tester uses tuple packing as its instruction stack format.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/Tuple.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/fdb_flow.cpp -->
## sources/storage-engines/foundationdb/bindings/flow/fdb_flow.cpp

Purpose: implements Flow-style asynchronous wrappers around the FoundationDB C API, exposing `API`, `DatabaseImpl`, and `TransactionImpl`.

Important APIs and functions: `CFuture::blockUntilReady`, `backToFutureCallback`, and templated `backToFuture` bridge raw `FDBFuture*` callbacks onto the Flow network thread and convert results. `API` implements version selection, network options/setup/run/stop, database creation, predicate evaluation, and API version access. `DatabaseImpl` wraps database options and admin calls. `TransactionImpl` wraps reads, ranges, split points, conflicts, mutations, commit, versionstamp, size, onError, cancel, and reset.

Control flow: each C API future is wrapped in `Reference<CFuture>`, callback completion schedules a Flow promise on `g_network`, and conversion reads the future result after awaiting readiness. Returned `FDBStandalone<T>` values hold the `CFuture` reference so borrowed C result memory remains valid.

State and persistence: owns raw `FDBDatabase*` and `FDBTransaction*` lifetimes. Mutations persist through `commit`; read result memory persists through future ownership.

Dependencies and integration points: depends on C API, Flow actors/network, `FDBLoanerTypes`, deterministic random/test helpers in the local `fdb_flow_test`, and admin C API functions.

Risks: `backToFuture` assumes callback registration succeeds and that `g_network` is available. Range result casts C structs to Flow `KeyValueRef`/`KeyRef` layout-compatible types. API singleton is process-global and enforces one selected API version.

Test signals: unit tests and directory tester rely on these wrappers for all Flow binding database operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/fdb_flow.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/fdb_flow.h -->
## sources/storage-engines/foundationdb/bindings/flow/fdb_flow.h

Purpose: public Flow binding API declarations over the FoundationDB C API.

Important APIs and types: `CFuture` owns `FDBFuture*`; `FDBStandalone<T>` extends result types with a future reference; abstract `ReadTransaction`, `Transaction`, `Database`, and `API` define async operations, mutation operations, admin calls, network lifecycle, database creation, and error predicate evaluation.

Control flow: users select an API version, configure/run the network, create a database, create transactions, perform async operations returning Flow `Future`s, and commit or retry via `onError`.

State and persistence: abstract interfaces represent database and transaction handles. `FDBStandalone` is the important ownership state carrier for borrowed C future memory.

Dependencies and integration points: includes Flow primitives, latest bindings C API, and `FDBLoanerTypes`. Implemented by `fdb_flow.cpp` and consumed by directory, tuple, subspace, allocator, and tester code.

Risks: all operations assume correct network lifecycle. Borrowed result memory must be retained through `FDBStandalone`; dropping it too early invalidates refs. API version selection is singleton-based.

Test signals: compilation and execution of `fdb_flow_tester` and C API tests validate this interface.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/fdb_flow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/tester/CMakeLists.txt -->
## sources/storage-engines/foundationdb/bindings/flow/tester/CMakeLists.txt

Purpose: build definition for the Flow binding tester executable.

Important targets: `TEST_SRCS` lists `DirectoryTester.cpp`, `Tester.cpp`, and `Tester.h`. `add_flow_target(EXECUTABLE NAME fdb_flow_tester ...)` builds the tester, and `target_link_libraries(fdb_flow_tester fdb_flow)` links it to the Flow binding library.

Control flow: included from the parent Flow CMake file via `add_subdirectory(tester)`.

State and persistence: only build artifacts; no runtime state in this file.

Dependencies and integration points: depends on parent include directories and `fdb_flow` target.

Risks: tester source additions must be reflected here. Missing link dependencies would surface as build failures.

Test signals: building this target validates tester integration with the library.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/tester/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/tester/DirectoryTester.cpp -->
## sources/storage-engines/foundationdb/bindings/flow/tester/DirectoryTester.cpp

Purpose: instruction implementations for a Flow binding directory/subspace tester. It adapts stack-based test instructions into calls on `IDirectory`, `DirectoryLayer`, `DirectorySubspace`, and `Subspace`.

Important APIs and functions: helpers `popTuples`, `popTuple`, `popPaths`, `pathToString`, `combinePaths`, and `logOp` decode tester stack values. Registered instruction structs implement `DIRECTORY_CREATE_SUBSPACE`, `DIRECTORY_CREATE_LAYER`, `DIRECTORY_CHANGE`, `DIRECTORY_SET_ERROR_INDEX`, create/open/move/remove/list/exists operations, key pack/unpack/range/contains, subspace open, logging, and strip-prefix.

Control flow: each instruction pops encoded tuples/paths from `data->stack`, obtains the current directory/subspace from `data->directoryData`, performs async calls with `instruction->tr`, optionally through `executeMutation`, then pushes results or new directory/subspace handles. Logging is gated by `LOG_OPS`/`LOG_DIRS`.

State and persistence: mutating instructions write directory metadata/content through the transaction. Logging instructions write diagnostic tuples under caller-provided prefixes. Tester state stores a list of directory/subspace handles and current/error indices.

Dependencies and integration points: includes `Tester.h`, uses tuple and directory APIs from the Flow binding, and registers instruction handlers through `REGISTER_INSTRUCTION_FUNC`.

Risks: stack encoding must match the external tester protocol exactly. Some debug output in `DIRECTORY_CREATE_LAYER` prints `nodeSubspace` for both node and content subspace, which can confuse diagnostics. Error behavior depends on `executeMutation`.

Test signals: primary behavior test harness for Flow directory/subspace compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/flow/tester/DirectoryTester.cpp -->
