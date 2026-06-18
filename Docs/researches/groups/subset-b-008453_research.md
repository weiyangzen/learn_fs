# subset-b-008453 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/sim2.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/sim2.cpp

### Purpose
`sim2.cpp` is FoundationDB's simulated network, process, socket, and filesystem backend. It installs `g_simulator`/`g_network`, implements the `ISimulator` and `INetworkConnections` behaviors used by simulation tests, and provides simulated TCP connections, UDP sockets, process/machine lifecycle operations, failure injection, disk timing, and a simulation-aware `IAsyncFileSystem`.

### Important APIs, Types, And Functions
The file defines global simulator state (`g_simulator`, thread-local `ISimulator::currentProcess`, `ISimulator::isMainThread`) and several core helper types. `SimClogging` records send/receive clogs, pair latencies, and temporary disconnections. `Sim2Conn` implements `IConnection` with in-memory byte queues, sender/receiver actors, simulated latency, random connection failure, stable local child-process connections, and leak tracking. `SimpleFile` wraps platform file descriptors as `IAsyncFile`, adds simulated disk delays, fault injection, random logging, atomic `.part` writes, and corruption-map maintenance. `Sim2Listener` implements `IListener` using a `PromiseStream`. `Sim2` implements `ISimulator` and `INetworkConnections`; key methods include `delay`, `orderedDelay`, `yield`, `connect`, `connectExternal`, DNS resolution helpers, `run`, `newProcess`, kill/reboot APIs, clog/disconnect APIs, HTTP simulation registration, `onProcess`, and `onMachine`. `UDPSimSocket` implements `IUDPSocket`. Top-level entry points include `startNewSimulator`, `startUnitTestSimulator`, `doReboot`, `waitUntilDiskReady`, `enableConnectionFailures`, `disableConnectionFailures`, `extendConnectionFailures`, and the `Sim2FileSystem` methods.

### Control Flow
Simulation time advances in `Sim2::runLoop`: the `TaskQueue` sleeps until the next timer, advances `time`, processes ready timers and thread-ready tasks, then executes ready `PromiseTask` instances by temporarily switching `currentProcess`. Network delay APIs enqueue `PromiseTask`s into that same task queue, so actor scheduling, process switching, and time progression are deterministic under `deterministicRandom()`.

TCP connection setup creates paired `Sim2Conn` instances, connects both ends, derives a simulated peer endpoint, and sends the server side through the peer process listener after a short delay. Writes copy bytes into the peer's receive buffer subject to peer send-buffer capacity; sender/receiver actors advance sent and received byte counters after simulated send and receive latency. Reads consume bytes once `receivedBytes` has advanced. Random close logic can close either side and optionally throw `connection_failed`.

Process lifecycle flows through `newProcess`, kill helpers, and `doReboot`. `newProcess` registers listeners in `addressMap`, attaches the process to a `MachineInfo`, initializes process globals, and applies protected/excluded/cleared state. Kill APIs select machines, zones, data halls, or datacenters, consult simulation policy via `canKillProcesses`, downgrade protected kills to reboots where needed, then call `killProcess_internal` or `doReboot`. Reboot sends the process shutdown signal and may clear data or switch cluster state.

### State And Persistence Behavior
Most state is in-memory simulator state: machine/process maps, address maps, DNS cache, HTTP server registrations, disk-space map, clog maps, UDP socket bindings, `currentlyRebootingProcesses`, protected/cleared/excluded state inherited from `ISimulator`, fault-injection fields on `ProcessInfo`, and process-specific globals. File persistence uses real underlying files via platform open/read/write/truncate/rename/delete, but the simulator layers non-durable behavior, per-machine file caches, delayed disk availability, fault injection, atomic `.part` rename on sync, and corruption block remapping around those real operations. `getDiskBytes` synthesizes total/free disk space and subtracts approximate sizes of machine-local open files.

### Dependencies And Integration Points
This file sits at the center of simulation integration. It depends on Flow actors and task scheduling, `fdbrpc/simulator.h`, `FlowTransport`, `Net2FileSystem`, `AsyncFileCached`, `AsyncFileNonDurable`, `AsyncFileChaos`, `AsyncFileWriteChecker`, TLS config stubs, simulated HTTP context support, fault injection, trace events, protocol versioning, Swift job ABI hooks, UDP and connection interfaces, and platform file APIs. `startUnitTestSimulator` integrates with unit-test binaries by creating a normal unit-test process plus an HTTP server process, setting simulated filesystems, and binding `FlowTransport`.

### Risks And Edge Cases
The implementation is intentionally nondeterministic under deterministic random choices; small changes can alter simulation schedules and invalidate existing seeds. `currentProcess` is thread-local and must be restored carefully, especially during destruction and cross-process actors. Stable connections bypass clogging and bit-flip behavior, so child-process topology affects network semantics. `SimpleFile` combines real filesystem effects with simulated durability; rename, corruption tracking, and open-file cache consistency are high-risk areas. Kill logic has many policy and protection gates, so changing it can make simulations either too destructive or unable to make progress. UDP send returns success even when no peer exists, matching datagram semantics but hiding delivery failures. The signal between `connectionFailuresDisableDuration`, `speedUpSimulation`, and fault injection is subtle and affects many tests.

### Test Signals
Direct test signals come from simulation tests and unit-test binaries that call `startNewSimulator` or `startUnitTestSimulator`. Runtime trace events and `CODE_PROBE` calls are extensive and should be watched for connection failures, durable/non-durable delete paths, reboot/kill outcomes, UDP packet drop, fault injection, disk-space exhaustion, and leaked connections. Build coverage should include simulation-enabled fdbrpc/fdbserver tests, HTTP simulation tests, file durability tests, and Swift-enabled builds when `WITH_SWIFT` is on.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/sim2.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/sim_validation.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/sim_validation.cpp

### Purpose
`sim_validation.cpp` provides debug-only simulation validation helpers for tracking committed/restored version bounds and version timestamps. It is used to detect durability and relocation regressions during simulated runs, while automatically disabling itself outside simulation or when the active simulation policy says version validation should not run.

### Important APIs, Types, And Functions
The file owns static validation state: `validationData` maps `UID` plus `"min"`/`"max"` suffix to committed-version bounds, `timedVersionsValidationData` maps versions to maximum allowed times, `disabledMachines` records IDs excluded from version checking, and `checkRelocationDuration` toggles relocation duration checks. Public debug helpers include `debug_setVersionCheckEnabled`, `debug_advanceCommittedVersions`, `debug_advanceMinCommittedVersion`, `debug_advanceMaxCommittedVersion`, `debug_checkRestoredVersion`, `debug_checkMinRestoredVersion`, `debug_checkMaxRestoredVersion`, `debug_removeVersions`, `debug_versionsExist`, `debug_setCheckRelocationDuration`, `debug_isCheckRelocationDuration`, `debug_advanceVersionTimestamp`, and `debug_checkVersionTime`.

### Control Flow
Every externally visible validation path first checks `versionValidationDisabled()`, which returns true outside simulation or when the simulation policy disables version validation. Advance functions update monotonic min/max records unless the machine is disabled. Check functions compare restored versions against the recorded min or max using a sign flip: min checks fail when restored is lower than recorded min, max checks fail when restored is higher than recorded max. Timestamp checks report when a checked time exceeds the recorded timestamp for that version.

### State And Persistence Behavior
All state is static process memory and is not persisted. `debug_setVersionCheckEnabled(false)` also removes any existing version records for that ID. Because keys are string-concatenated `UID` values plus suffixes, state is shared globally within the process and assumes the suffix vocabulary stays limited to `"min"` and `"max"`.

### Dependencies And Integration Points
The code depends on `fdbrpc/sim_validation.h`, `TraceFileIO`, `flow/network.h`, and `fdbrpc/simulator.h`. Its main integration point is simulation policy via `g_simulator->getSimulationPolicy()->shouldRunVersionValidation()`, and its output is trace events named with caller-provided context plus suffixes such as `UnknownVersion`, `DurabilityError`, `UnknownTime`, and `VersionTimeError`.

### Risks And Edge Cases
Unknown versions only emit warnings and return false, so missing instrumentation may hide a durability issue. Disabled machines suppress both updates and checks. The global static maps are not isolated per simulation run unless process lifetime resets them. The helper returns booleans indicating an error was detected but does not itself throw or fail tests; callers must act on the result or rely on trace severity.

### Test Signals
Useful signals are `DurabilityError` and `VersionTimeError` trace events under simulation policies that enable validation. Tests should also cover disabled-machine behavior, missing version warnings, timestamp checks, and policy-disabled/no-simulation no-op paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/sim_validation.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/swift_sim2_hooks.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/swift_sim2_hooks.cpp

### Purpose
`swift_sim2_hooks.cpp` bridges Swift concurrency into the FoundationDB simulator. It implements the Swift global enqueue hook for Sim2 so Swift jobs scheduled while running in simulation are inserted into the simulator task queue instead of being executed by the normal Swift runtime executor path.

### Important APIs, Types, And Functions
The sole exported implementation is `sim2_enqueueGlobal_hook_impl(swift::Job*, void (*)(swift::Job*) swiftcall)`, declared with `SWIFT_CC(swift)`. It obtains `g_simulator`, asserts it exists, and calls `ISimulator::_swiftEnqueue(job)`. The second function-pointer parameter is intentionally unused because Sim2 provides the enqueue behavior.

### Control Flow
Swift runtime code calls this hook when a Swift job is globally enqueued under the configured concurrency hooks. The hook synchronously forwards the job to the simulator. In `sim2.cpp`, `_swiftEnqueue` maps the Swift job priority to a Flow `TaskPriority`, captures the current simulated process, wraps the job in a `PromiseTask`, and places it in `taskQueue`. The job is later executed by the simulation run loop under the captured process context.

### State And Persistence Behavior
This file owns no state. It depends on global simulator state and requires `g_simulator` to be initialized. All durable behavior is delegated to the simulator queue and Swift job execution.

### Dependencies And Integration Points
It includes simulator, Flow, network, TLS, Swift concurrency hooks, and Swift ABI task headers. It is only meaningful in Swift-enabled builds where FoundationDB's Swift interoperability hooks are active. Its correctness depends on `Sim2::_swiftEnqueue` preserving process context and priority mapping.

### Risks And Edge Cases
Calling the hook before simulator startup aborts on `ASSERT(sim)`. If the Swift runtime changes the hook ABI or job ownership semantics, this bridge can break silently at integration time. The hook ignores the original enqueue function, so fallback behavior is unavailable in simulation.

### Test Signals
Swift-enabled simulation tests should show Swift tasks executing deterministically on the expected simulated process. Build/link failures around Swift ABI headers or unresolved hook symbols are the primary static signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/swift_sim2_hooks.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/tests/AuthzTlsTest.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/tests/AuthzTlsTest.cpp

### Purpose
`AuthzTlsTest.cpp` is a standalone non-Windows TLS authorization integration test for fdbrpc. It forks a server and client using real `Net2` and `FlowTransport`, generates in-memory certificates, probes whether the server sees the peer as trusted, and verifies expected outcomes across TLS, no-TLS, expired certificate, missing certificate, and password-protected key cases.

### Important APIs, Types, And Functions
Key test enums are `ExitCodes`, `Role`, `ChainLength` with `NO_TLS = -1`, and `Result` (`ERROR`, `TRUSTED`, `UNTRUSTED`, `TIMEOUT`). `TLSCreds` carries PEM bytes and password state. `makeCreds` generates certificate chains or password-protected certs through `mkcert`. `SessionInfo`, `SessionProbeRequest`, and `SessionProbeReceiver` define a small fdbrpc request/response protocol; the receiver reads `FlowTransport::currentDeliveryPeerIsTrusted()` and `currentDeliveryPeerAddress()`. `runHost<IsServer>` starts either a server or client transport. `runTlsTest` sets up credentials, pipes, forked children, stdout capture, and process status checking. `main` generates a matrix of chain-length categories plus password tests.

### Control Flow
For each test case, the main process creates pipes and forks the server. The server configures `TLSConfig`, binds `FlowTransport` to `127.0.0.1:0` or `:tls`, registers the probe endpoint, starts the network in a thread, writes its bound address and endpoint token to the address pipe, then waits for a completion flag. The main process then forks the client. The client reads the server address/token, adjusts the TLS flag according to its credentials, sends a `SessionProbeRequest`, runs the network until either a reply or timeout, writes completion to the server, and exits with a status matching the expected result. The parent drains child stdout, waits for both subprocesses, and records failed cases.

### State And Persistence Behavior
The test uses process-local globals (`role`, `g_network`) in each forked process. Certificates are generated in memory and passed by value before fork. Pipes carry the server network address, endpoint token, and completion signal. Trace files are opened in the working directory with client/server prefixes. There is no persistent product state, but subprocess and pipe cleanup is critical to avoid hangs.

### Dependencies And Integration Points
The test depends on POSIX APIs (`fork`, `pipe`, `dup2`, `waitpid`, `read`, `write`), `fmt`, Flow errors and arenas, `mkcert`, `TLSConfig`, `newNet2`, `openTraceFile`, and `FlowTransport`. It is built only when not on Windows and is registered in CTest by `fdbrpc/tests/CMakeLists.txt` as `authorization_tls_unittest` with a 120 second timeout.

### Risks And Edge Cases
The test has blocking pipe reads/writes that are acceptable for this controlled scenario but can hang if child startup fails before pipe closure. It relies on raw `NetworkAddress` and endpoint token writes across forked processes; a static assertion covers trivial destructibility for `NetworkAddress`, but this is still tightly coupled to object layout. Randomized chain lengths use `std::rand`, so failures need the printed seed. Timeout expectations can be sensitive to host scheduling or TLS handshake behavior. Server bad-password cases expect bind failure and client pipe-read failure, so exit-code interpretation is part of correctness.

### Test Signals
Passing output ends with `Test OK`, while failure logs include the specific chain pairs and password cases. Important subprocess signals are `SERVER_BIND_ERROR`, `CLIENT_PIPE_READ_ADDR_FAILED`, `CLIENT_TEST_RESULT_MISMATCH`, and waitpid messages for abnormal exit or signal termination.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/tests/AuthzTlsTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/tests/CMakeLists.txt -->
## sources/storage-engines/foundationdb/fdbrpc/tests/CMakeLists.txt

### Purpose
This CMake file wires fdbrpc test and benchmark targets into the build. It conditionally builds and registers the TLS authorization unit test, conditionally generates gRPC/protobuf code for the echo proto, and always builds the fdbrpc transport benchmark.

### Important APIs, Types, And Functions
The file uses project CMake helpers `add_flow_target` and `generate_grpc_protobuf`. It defines executable targets `authz_tls_unittest` and `fdbrpc_transport_bench`, links them to project libraries, and registers CTest test `authorization_tls_unittest` when `OPEN_FOR_IDE` is false.

### Control Flow
On non-Windows platforms, `authz_tls_unittest` is built from `AuthzTlsTest.cpp` and linked with `flow`, `fdbrpc`, and `fmt::fmt`. If not generating IDE-only projects, it is added as a CTest test with `TIMEOUT 120`. If `WITH_GRPC` is enabled, protobuf/gRPC sources are generated from `protos/echo.proto`. Finally, `fdbrpc_transport_bench` is built from `fdbrpc_bench.cpp` and linked with `flow`, `fdbrpc`, and Boost program options.

### State And Persistence Behavior
The file itself does not manage runtime state. Its build state is expressed through generated targets, test registrations, and optional generated protobuf outputs controlled by `WITH_GRPC`.

### Dependencies And Integration Points
It integrates fdbrpc tests with CTest, the Flow target macro system, the project's gRPC generation helper, `fmt`, Boost program options, and platform conditionals. The TLS test target depends on POSIX behavior and is therefore excluded on Windows.

### Risks And Edge Cases
Because the benchmark target is always added, builds must provide Boost program options even when only tests are desired. The authorization test is omitted under `OPEN_FOR_IDE`, so IDE project generation will not expose the CTest signal. gRPC code generation is conditional; users expecting echo service generated code must enable `WITH_GRPC`.

### Test Signals
CTest should show `authorization_tls_unittest` on non-Windows non-IDE builds. Build-system validation should check target creation with `WITH_GRPC` both on and off, and verify `fdbrpc_transport_bench` links successfully.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/tests/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/tests/fdbrpc_bench.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/tests/fdbrpc_bench.cpp

### Purpose
`fdbrpc_bench.cpp` implements a simple fdbrpc echo throughput benchmark. It can run as a server or client against `127.0.0.1:9001`, sends fixed-size payloads through `FlowTransport`, and prints request throughput from both sides.

### Important APIs, Types, And Functions
The benchmark defines `EchoServerInterface` with `getInterface` and `echo` request streams, `GetInterfaceRequest`, and `EchoRequest`. `WLTOKEN_ECHO_SERVER` is the well-known endpoint token. `StatCounter` tracks a sliding average over recent seconds. `EchoServer` serves interface discovery, echo requests, and periodic throughput printing. `echoServer` and `echoClient` are actor entry points selected from the `actors` map. `randString` creates client payloads. `main` parses `--mode` and `--payload_size`, initializes platform/network/transport, binds the server when needed, runs selected actors, and enters the network run loop.

### Control Flow
Server mode initializes `FlowTransport` as a server, binds to `127.0.0.1:9001`, exposes a well-known `getInterface` endpoint, and then races three infinite actors: interface request handling, echo request handling, and periodic throughput logging. Client mode initializes `FlowTransport` as a client, resolves the server interface via the well-known endpoint, creates one random payload, then loops in 10 second windows sending echo requests and printing completed requests per second.

### State And Persistence Behavior
Runtime state is in-memory: global `serverAddress`, global `payload_size_bytes`, server-side `EchoServerInterface`, and a `StatCounter` vector of `(timestamp, count)` buckets. There is no persistence. The process owns `g_network` and a single `FlowTransport` instance.

### Dependencies And Integration Points
The file depends on Boost program options, Flow platform/network/TLS primitives, fdbrpc serialization/request streams, and `FlowTransport`. It is built by `fdbrpc/tests/CMakeLists.txt` as `fdbrpc_transport_bench` and linked with `boost_target_program_options`.

### Risks And Edge Cases
`randString` reseeds `std::rand` on every call, which is harmless for the current single payload but would be poor if reused in a loop. `EchoServerInterface::serialize` serializes only `echo`, not `getInterface`; this is likely intentional because `getInterface` is well-known, but it is a coupling worth preserving carefully. The benchmark uses fixed port `9001`, so local conflicts cause bind failures. Actors run indefinitely and rely on process termination rather than a benchmark duration flag. `StatCounter::avg` divides by the configured window size and may underreport immediately after startup.

### Test Signals
Useful signals are successful server bind, client interface discovery, repeated `Sent N requests` client logs, and server `Throughput` logs. Build failures usually indicate Boost program options or fdbrpc serialization/linkage issues.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/tests/fdbrpc_bench.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/tests/protos/echo.proto -->
## sources/storage-engines/foundationdb/fdbrpc/tests/protos/echo.proto

### Purpose
`echo.proto` defines a small gRPC echo service for fdbrpc tests. It supplies unary, server-streaming, and client-streaming echo RPC shapes over simple string request/response messages.

### Important APIs, Types, And Functions
The proto uses `syntax = "proto3"` and package `fdbrpc.test`. `TestEchoService` exposes `Echo(EchoRequest) returns (EchoResponse)`, `EchoRecvStream10(EchoRequest) returns (stream EchoResponse)`, and `EchoSendStream10(stream EchoRequest) returns (EchoResponse)`. `EchoRequest` and `EchoResponse` each contain `string message = 1`.

### Control Flow
There is no executable control flow in the proto. When `WITH_GRPC` is enabled, CMake invokes `generate_grpc_protobuf(fdbrpc.test protos/echo.proto)`, producing generated service and message code for tests.

### State And Persistence Behavior
The schema has no persistent storage. The only state carried on the wire is the `message` string in request and response messages.

### Dependencies And Integration Points
The file integrates with protobuf/gRPC tooling through `fdbrpc/tests/CMakeLists.txt`. Its package name determines generated namespaces/packages for test code. The method names indicate coverage for unary calls and both streaming directions.

### Risks And Edge Cases
Changing field numbers or package names would break generated-code compatibility. The `RecvStream10` and `SendStream10` names encode an expected count in the method name, but the schema itself does not enforce a count of 10; test implementations must do that.

### Test Signals
Builds with `WITH_GRPC=ON` should generate and compile the protobuf/gRPC artifacts. Runtime tests should exercise unary echo, ten-response receive streaming, and ten-request send streaming semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/tests/protos/echo.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/CMakeLists.txt -->
## sources/storage-engines/foundationdb/fdbserver/CMakeLists.txt

### Purpose
This CMake file defines how the main `fdbserver` executable and its component libraries are assembled. It discovers fdbserver sources, excludes workload sources from the main source list, adds many server subdirectories, configures optional RocksDB/liburing/Swift/Jemalloc/gperftools support, links server component libraries, and installs the server binary.

### Important APIs, Types, And Functions
Important build helpers include `fdb_find_sources`, `configure_fdbserver_common_includes`, `configure_fdbserver_target_includes`, `add_flow_target`, `add_subdirectory`, `add_swift_to_cxx_header_gen_target`, `generate_modulemap`, `fdb_install`, and optional package helpers such as `find_package(LZ4)`, `find_package(uring)`, `include(CompileRocksDB)`, `include(FindSwiftLibs)`, `include(SwiftToCXXInterop)`, and `include(GenerateModulemap)`.

### Control Flow
The script first gathers `FDBSERVER_SRCS`, removes workload files and `FDBServerUnitTestMain.cpp`, and defines include helper functions. It configures RocksDB dependencies if enabled, adds server subsystem subdirectories, creates a workload binary directory, and defines the `fdbserver` executable. Under `WITH_SWIFT`, it defines `fdbserver_swift`, configures Swift/C++ include paths and compile flags, generates Swift-to-C++ headers, wires dependencies among Flow, fdbrpc, fdbclient, and fdbserver actor targets, links Swift object files into `fdbserver`, and generates a module map. It then configures includes and links the server against all component libraries, RocksDB or normal storage dependencies, memory/profiling libraries, TOML/RapidJSON, optional Swift libraries, install rules, and public `fdbctl`.

### State And Persistence Behavior
The file controls generated build state: source lists, target dependency graph, generated Swift headers/module maps, object-file link options, compile definitions, install outputs, and generated package binaries. It does not define runtime persistence, but build options such as RocksDB/liburing directly change the storage engine code linked into the server.

### Dependencies And Integration Points
It is the integration hub for fdbserver submodules: `core`, `kvstore`, `logsystem`, `mocks3`, `clustercontroller`, `backupworker`, `commitproxy`, `coordinator`, `datadistributor`, `consistencyscan`, `grvproxy`, `logrouter`, `ratekeeper`, `resolver`, `sequencer`, `storageserver`, `tester`, `tlog`, `worker`, and `workloads`. It links external dependencies including `fdbclient`, `sqlite`, RocksDB, LZ4, liburing, Jemalloc, TOML11, RapidJSON, Swift runtime libraries, gperftools, and `fdbctl`.

### Risks And Edge Cases
Swift integration is fragile because it relies on generated headers, virtual filesystem overlays, object-library link options, and explicit target dependencies. RocksDB with liburing changes compile definitions to disable epoll and enable io_uring in Boost.Asio, which can affect unrelated networking assumptions. `WHOLE_ARCHIVE` on workloads intentionally preserves workload registrations but can increase link sensitivity. Removing `FDBServerUnitTestMain.cpp` is required so the production server does not pick up the unit-test main. Install behavior differs depending on `GENERATE_DEBUG_PACKAGES`.

### Test Signals
Primary signals are successful configure/generate for combinations of `WITH_SWIFT`, `WITH_ROCKSDB`, `WITH_LIBURING`, `USE_JEMALLOC`, and `GPERFTOOLS_FOUND`, plus successful `fdbserver` link. Swift builds should validate generated headers/module map and object-file linking. Packaging tests should validate both stripped and debug-package install paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/FDBServerUnitTestMain.cpp -->
## sources/storage-engines/foundationdb/fdbserver/FDBServerUnitTestMain.cpp

### Purpose
`FDBServerUnitTestMain.cpp` is the main entry point for fdbserver unit-test binaries. It initializes randomized simulated server knobs, starts the unit-test simulator, and delegates test execution to Flow's `runUnitTests`.

### Important APIs, Types, And Functions
The file requires `FDBSERVER_UNIT_TEST_SUITE` to be defined at compile time. `initializeSimulation()` calls `resetServerKnobs(Randomize::True, IsSimulated::True)` and `startUnitTestSimulator()`. `main` calls `runUnitTests(argc, argv, UnitTestRunnerConfig(FDBSERVER_UNIT_TEST_SUITE, initializeSimulation))`.

### Control Flow
At startup, `main` constructs a `UnitTestRunnerConfig` containing the suite identifier and simulation initializer. The unit-test runner invokes `initializeSimulation` before running tests that need simulated Flow/fdbrpc state. The initializer resets fdbserver knobs for randomized simulation and creates the unit-test simulator/process/transport setup provided by `sim2.cpp`.

### State And Persistence Behavior
The file itself owns no persistent state. It mutates global server knob state and global simulator/network state during initialization. Test persistence behavior depends on the simulator filesystem configured by `startUnitTestSimulator`.

### Dependencies And Integration Points
It depends on `fdbrpc/simulator.h`, `fdbserver/core/Knobs.h`, and `flow/UnitTestRunner.h`. It is intentionally removed from production `fdbserver` sources in `fdbserver/CMakeLists.txt` and should be compiled only into unit-test targets that define `FDBSERVER_UNIT_TEST_SUITE`.

### Risks And Edge Cases
Missing `FDBSERVER_UNIT_TEST_SUITE` causes a compile-time error. Because knobs are randomized for simulation, tests must tolerate knob variability or explicitly override needed values. Any regression in `startUnitTestSimulator` affects all fdbserver unit tests using this main.

### Test Signals
Successful build of each fdbserver unit-test target proves the suite macro is set. Runtime signals include simulator startup, randomized knob initialization, and normal `runUnitTests` pass/fail reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/FDBServerUnitTestMain.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/SigStack.cpp -->
## sources/storage-engines/foundationdb/fdbserver/SigStack.cpp

### Purpose
`SigStack.cpp` installs a signal handler that prints the current actor stack lineage when `SIGUSR1` is received. It is an initial diagnostic hook for observing FoundationDB actor stack traces from a running server process.

### Important APIs, Types, And Functions
`stackSignalHandler(int sig)` calls `getActorStackTrace()`, pops entries from the returned stack, converts each `StringRef`-like entry to `std::string_view`, and writes indexed frames to `std::cout`. `setupStackSignal()` registers the handler with `std::signal(SIGUSR1, &stackSignalHandler)`. On Windows, fallback numeric definitions for `SIGUSR1` and `SIGUSR2` are provided.

### Control Flow
When setup code calls `setupStackSignal`, the process signal disposition for `SIGUSR1` points at `stackSignalHandler`. On signal delivery, the handler synchronously retrieves actor stack lineage and prints frames in reverse pop order until the stack is empty.

### State And Persistence Behavior
This file owns no state and persists nothing. It observes actor lineage state maintained by `fdbclient/StackLineage` and writes diagnostic output to standard output.

### Dependencies And Integration Points
It depends on Flow basics, `fdbclient/StackLineage.h`, C signal APIs, iostream, and string views. Its integration point is whichever fdbserver initialization path calls `setupStackSignal`.

### Risks And Edge Cases
The file explicitly notes the handler is not async-signal-safe. Calling C++ allocation, iostreams, or stack-lineage helpers from a signal handler can deadlock or corrupt state in production scenarios. The `sig` parameter is unused. Windows signal numbers are only placeholders and may not correspond to real POSIX-like user signals.

### Test Signals
Manual or integration testing can call `setupStackSignal`, send `SIGUSR1`, and verify actor stack frames print. Static review should treat this as diagnostic-only and not a robust crash-signal handler.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/SigStack.cpp -->
