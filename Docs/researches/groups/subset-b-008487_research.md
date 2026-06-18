# Research: subset-b-008487

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/worker.actor.cpp -->
# sources/storage-engines/foundationdb/fdbserver/worker/worker.actor.cpp

## Purpose
`worker.actor.cpp` is the main `fdbd` worker-process orchestration file. It discovers persisted worker-local state, starts the process-level services exposed through `WorkerInterface` and `ProcessInterface`, registers the worker with the cluster controller, restores durable storage/TLog roles from disk, accepts role recruitment requests, monitors health and local issues, and turns role actor failures into process-level reboot/termination semantics. It is one of the central integration points between Flow actors, cluster-controller leadership, durable storage engines, transaction logs, backup/data-distribution/ratekeeper/resolver/proxy roles, system monitoring, profiling, and process bootstrap.

## Important APIs, Types, and Functions
- `fdbd(...)`: public process entry actor for an FDB server. It starts protocol/process services, optional coordination server, locks data/spill folders with `processId`, verifies/writes software-version compatibility, starts or monitors cluster-controller candidacy, extracts the cluster interface, and launches `workerServer`.
- `workerServer(...)`: long-running actor that owns one `WorkerInterface`, restores on-disk storage/TLog roles, starts background monitors, registers with CC, and handles all role recruitment and operational request streams.
- `registrationClient(...)`: repeatedly sends `RegisterWorkerRequest` to the current cluster controller, carrying process class, priority info, optional role interfaces, degraded state, worker issues, recovered-disk signal, incompatible peer list, cluster-file mismatch issue, and cluster id.
- `ErrorInfo`, `forwardError`, `workerHandleErrors`, `handleIOErrors`: normalize actor/store errors, emit role lifecycle ending events, convert global ASIO timeout state to `io_timeout`, and decide which errors should reboot the process or KV store.
- Disk discovery helpers: `KeyValueStoreSuffix`, `TLogOptions`, `DiskStore`, `filenameFromSample`, `filenameFromId`, and `getDiskStores(...)` map file/directory naming conventions to storage or TLog state.
- Health helpers: `addressInDbAndPrimaryDc`, `addressesInDbAndPrimarySatelliteDc`, `addressesInDbAndRemoteDc`, `addressIsRemoteLogRouter`, `shouldCheckPeer`, `doPeerHealthCheck`, `getStorageServers`, and `healthMonitor` classify the worker/peer topology and report degraded, disconnected, and recovered peers to the CC.
- Profiling helpers: `registerThreadForProfiling`, `runProfiler`, `runCpuProfiler`, `runHeapProfiler`, and `monitorHighMemory` expose gperftools/Flow profiler control through worker requests.
- Storage cleanup/reboot helpers: `TrackRunningStorage`, `storageServerRollbackRebooter`, `cleanupStaleStorageDisk`, `cleanupStorageDisks`, and `deleteStorageFile` manage double recruitment and storage-engine reboot loops.
- Process persistence helpers: `createClusterIdFile`, `updateClusterId`, `readClusterId`, `createAndLockProcessIdFile`, `testSoftwareVersionCompatibility`, `updateNewestSoftwareVersion`, `testAndUpdateSoftwareVersionCompatibility`, `getCCPriorityInfo`, and `monitorAndWriteCCPriorityInfo`.
- Leadership/process services: `monitorLeaderWithDelayedCandidacy`, `serveProtocolInfo`, `serveProcess`, and `loadedPonger`.
- Embedded test cases cover address-classification helpers, software-version file behavior, and storage-engine in-flight commit clearing.

## Control Flow
`fdbd` starts with protocol and process endpoints, optional coordination server, and data/spill folder locking. It assigns a stable process id into locality, validates the software-version file, creates async variables for CC, cluster interface, priority info, DB info, and cluster id, then chooses whether to run the cluster controller directly, monitor a leader, or delay worst-fit candidacy. It then starts `workerServer` under `reportErrorsExcept` and waits for one core actor to terminate.

`workerServer` initializes a `WorkerInterface`, metrics logging, degraded reset, ping/wait-failure servers, trace-log and TLog issue monitors, tester server, high-memory profiler monitor, and system-monitor machine state. It scans data and TLog spill folders with `getDiskStores`. For each discovered storage file, it opens the correct KV store, builds a `StorageServerInterface`, starts `storageServer`, wraps store errors through `handleIOErrors`, and then wraps the actor with `storageServerRollbackRebooter`. For each discovered TLog file, it opens both KV store and disk queue, starts the shared TLog actor, and records it under `sharedLogs`. Only after all recovery promises complete does the registration client advertise the worker as recovered for stateful recruitment.

The main `choose` loop handles DB info broadcasts, reboot and failure-injection requests, profiler requests, and recruitment for master, data distributor, ratekeeper, consistency scan, backup, range backup, TLog, storage, commit proxy, GRV proxy, resolver, and log router. Most recruitment paths initialize a role-specific interface, call `startRole`, dump endpoint tokens for debugging, start the role actor, forward failures through `forwardError`, and reply with the recruited interface. TLog recruitment reuses or creates a shared TLog per `SharedLogsKey`; storage recruitment guards against double recruitment except when using different storage engines or seed tags. The loop also serves event-log/trace-batch/disk-store/snapshot requests and periodic system-monitor logging.

## State and Persistence Behavior
Persistent state includes storage-engine files/directories, TLog KV stores, TLog disk queues, the `processId` lock file, `clusterId`, `fitness`, `sw-version`, and `_validate`. Storage filenames encode component, UID, storage engine, and sometimes TLog options. `processId` is opened with `OPEN_LOCK`, preventing two processes from using the same data or spill folder; spill folder process id must match the data folder. `sw-version` is atomically written and checked against protocol compatibility. The `fitness` file persists CC priority information. `_validate` is consumed on reboot with `checkData` to force validation on next open. `TrackRunningStorage` and `storageCleaners` keep in-memory state for running storage roles and deferred stale disk cleanup; if a storage server is confirmed removed by commit proxy rejoin info, its KV store is reopened and disposed to delete disk state.

TLog state can live in `dataFolder` or `tLogSpillFolder`; duplicate TLog IDs across folders are treated as recovery failure. `clusterId` is created once from `ServerDBInfo.client.clusterId` and prevents joining a mismatched cluster later through `invalid_cluster_id` handling.

## Dependencies and Integration Points
This file depends on nearly every major server subsystem: cluster controller, master/sequencer, commit and GRV proxies, resolvers, TLogs, storage server, data distributor, ratekeeper, consistency scan, log router, backup workers, coordinator, tester, metrics logger, storage engines, disk queues, Flow transport/failure monitor, gRPC control services, simulator, system monitor, profiler, and NativeAPI. It integrates with `WorkerInterface.actor.h` request streams as the server side of role recruitment and with `IClusterConnectionRecord`/leader election for cluster membership.

## Risks and Edge Cases
- Error classification is process-critical. `please_reboot`, TLog IO errors/timeouts, storage IO timeouts under the reboot knob, and KV-store reboot requests deliberately escape to process restart paths; misclassification can either hide data-path corruption or cause unnecessary process churn.
- Disk-store filename parsing is a recovery boundary. New storage engines or TLog option formats must preserve parsing in `getDiskStores`, `TLogOptions::FromStringRef`, and `filenameFromId`.
- TLog spill folder handling can fail recovery if a non-TLog store appears in the spill folder or duplicate TLog IDs exist across folders.
- Health-monitor classification relies on DB info locality and log-system structure. Incorrect primary/remote/satellite classification can create false gray-failure reports or miss real ones.
- `workerServer` has many actor lifetime dependencies. `filesClosed`, reboot promises, `sharedLogs`, and `errorForwarders` are carefully ordered to avoid broken promises and dangling file handles.
- Snapshot execution uses external `execHelper` payloads and whitelist paths; duplicate request handling is subtle because retries can replace an ongoing reply promise.
- Profiler request path sanitization depends on `abspath` prefix checks under `SERVER_KNOBS->LOG_DIRECTORY`.
- `AsyncVar`-driven registration re-runs on many changes; excessive churn or wrong issue propagation can affect CC recruitment decisions.

## Test Signals
Embedded `TEST_CASE`s validate primary/remote/satellite address classification, remote log-router identification, software-version file compatibility/update behavior, and storage-engine clearing of in-flight commits. Runtime test signals include trace events such as `WorkerRegister`, `WorkerRegisterReply`, `DiskFileRecoveriesComplete`, `WorkerHealthMonitor`, `HealthMonitorDetectDegradedPeer`, `StorageServerInitProgress`, `WorkerShutdownComplete`, `StartingFDBD`, and software-version traces. Simulation buggify paths exercise delayed zombie endpoint destruction, skipped log-router replies, injected IO/failure conditions, and process reboot behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/worker.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ApiCorrectness.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ApiCorrectness.cpp

## Purpose
`ApiCorrectness.cpp` implements the `ApiCorrectness` tester workload. It validates FoundationDB transaction API behavior by running deterministic randomized sets, gets, range reads, key-selector range reads, key resolution, point clears, and range clears against both the real database and an in-memory `MemoryKeyValueStore` model. It exercises several client API implementations through the common `ApiWorkload` transaction wrapper layer.

## Important APIs, Types, and Functions
- `OperationType`: enumerates random operations: `SET`, `GET`, `GET_RANGE`, `GET_RANGE_SELECTOR`, `GET_KEY`, `CLEAR`, `CLEAR_RANGE`.
- `ApiCorrectnessWorkload : ApiWorkload`: workload registration type with `NAME = "ApiCorrectness"`.
- Constructor options: `numGets`, `numGetRanges`, `numGetRangeSelectors`, `numGetKeys`, `numClears`, `numClearRanges`, `minSizeAfterClear`, `maxRandomTestKeys`, `randomTestDuration`, `maxTransactionBytes`, and `resetDBTimeout`.
- `performSetup`: selects a random transaction wrapper type from NativeAPI, ReadYourWrites, ThreadSafe, and MultiVersion.
- `performTest`: runs a scripted API sequence, resets DB state by re-setting generated data, then runs the timed random test.
- `runScriptedTest`: fixed sequence covering all operation families and range-clear reset behavior.
- `runRandomTest`: unbounded loop selecting operation density based on memory-store size, bounded externally by `randomTestDuration`.
- Operation helpers: `runSet`, `runGet`, `runGetRange`, `runGetRangeSelector`, `runGetKey`, `runClear`, and `runClearRange`.
- Optional compile-time `debugKey` helpers trace activity for one target key when enabled.

## Control Flow
Setup chooses the transaction factory. `performTest` first invokes `runScriptedTest` with generated data. `runScriptedTest` sets the full dataset, validates point gets, range gets, selector ranges, key selectors, clears, and range clears. If range clears shrink the memory model below `minSizeAfterClear`, it restores the original data to keep subsequent tests meaningful. If the scripted phase succeeds, `performTest` attempts a bounded reset with `runSet` and then starts `runRandomTest` under a timeout.

Each operation helper creates one or more `TransactionWrapper` instances, performs API calls in chunks capped by `maxKeysPerTransaction`, retries via `transaction->onError(err)`, updates the memory model after successful commits, and validates the database against memory where applicable. Reads compare real results to `MemoryKeyValueStore`; write/clear paths call `compareDatabaseToMemory`. Range-selector logic rejects selectors that drift outside the client prefix, except for legal beginning/end sentinels for first/last clients, and filters `0xff` keyspace results at the end boundary.

## State and Persistence Behavior
The workload persists mutations into the real FDB keyspace under the per-client `clientPrefix` inherited from `ApiWorkload`. The expected state is mirrored in `store`, an in-memory `MemoryKeyValueStore`. `success` is the workload pass/fail latch. The workload uses transaction conflict ranges intentionally around set/clear operations to make transactions self-conflicting enough to avoid ambiguous commit behavior in this correctness test. The generated `data` vector grows during random SET operations and is used as the source for selecting existing keys.

## Dependencies and Integration Points
The file depends on `ApiWorkload.h` for transaction abstraction and data generation, `MemoryKeyValueStore` for the oracle, `ManagementAPI` for configuration retrieval, `MutationTracking` debug macros, `QuietDatabase`, Flow actors, simulator random, and the tester `WorkloadFactory`. It integrates with FDB transaction retry semantics through `TransactionWrapper::onError`, with client API variants chosen by `ApiWorkload::chooseTransactionFactory`, and with tester metrics through `PerfIntCounter`.

## Risks and Edge Cases
- The random operation selection uses a custom density array where probabilities change with `store.size()`. Mistakes here can overfill or overclear the model and reduce coverage.
- `runGetRangeSelector` has complicated boundary filtering around per-client prefixes and `0xff`; selector semantics regressions are likely to surface here, but false positives are possible if prefix-boundary assumptions change.
- The code intentionally chunks large operations by `maxKeysPerTransaction`; increasing value/key sizes without adjusting this can create large transactions or transaction-too-old behavior.
- `runSet` and `runClear` perform a read before write/clear and add read conflict ranges. This is a test design choice, not a general API usage model.
- `runClearRange` updates the memory model before the database commit; if retry semantics around range clear changed unexpectedly, the memory model must still correspond to the eventual committed operation.

## Test Signals
Primary pass/fail signal is `check()` inherited from `ApiWorkload` returning `success`. Failures emit stdout and `TraceEvent(SevError, "TestFailure")` with workload context. Metrics include `Number of Random Operations Performed`. Debug mutation signals `ApiCorrectnessSet` and `ApiCorrectnessClear` are emitted with committed versions, and comparison failures include detailed range dumps and trace events from `ApiWorkload::compareResults`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ApiCorrectness.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ApiWorkload.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ApiWorkload.cpp

## Purpose
`ApiWorkload.cpp` implements the shared behavior for API-oriented tester workloads. It prepares a per-client keyspace, generates randomized test keys and values, chooses a transaction API implementation, compares real database results to an in-memory model, and exposes common setup/start/check/failure helpers used by workloads such as `ApiCorrectness`.

## Important APIs, Types, and Functions
- `ApiWorkload::setup` and helper `setup`: install a default native transaction factory, clear this client's key range, then call subclass `performSetup`.
- `ApiWorkload::start` and helper `start`: generate short-key and long-key data under `clientPrefix`, then call subclass `performTest`.
- `clearKeyspace`: clears `[clientPrefixInt, clientPrefixInt + 1)` with retry handling.
- `testFailure`: prints and traces a workload failure and latches `success = false`.
- `compareResults`: compares database range output to memory-store output, including detailed trace/stdout diagnostics and read version.
- `compareDatabaseToMemory`: scans the client prefix range in chunks and validates every key/value against `store`.
- Random-data helpers: `generateData`, `generateKey`, `generateKeySelector`, `selectRandomKey`, and `generateValue`.
- `chooseTransactionFactory`: randomly selects Native, ReadYourWrites, ThreadSafe, or MultiVersion transaction wrappers and builds the appropriate `TransactionFactory`.
- `createTransaction` and `hasFailed`.

## Control Flow
For participating clients, setup clears the client-owned key range with retry-aware transactions, then delegates workload-specific setup. Start builds a vector of randomized key/value pairs by combining short-key and long-key populations and delegates to `performTest`. Subclasses use `createTransaction` for all API activity; the chosen factory determines whether operations run through Flow `Transaction`, `ReadYourWritesTransaction`, thread-safe `ITransaction`, or multi-version debug wrappers.

Comparison control flow pages through the database from `clientPrefix` to `clientPrefix + "\xff"`, fetching up to 100 rows per transaction and comparing to `MemoryKeyValueStore`. Random key/value generation uses deterministic random sources and can inject plaintext marker strings into keys and values in simulation when data-at-rest validation is configured.

## State and Persistence Behavior
The persistent database surface is a per-client key prefix, making each client independently comparable to its in-memory `store`. `success` is the durable-in-workload failure latch for the test run. `transactionFactory` and `transactionType` are runtime state selecting the API under test. `useExtraDB` and `extraDB` allow simulation to route some Flow transactions through an extra simulated database; `FlowTransactionWrapper::onError` can replace the underlying transaction with one using either the primary or extra DB after an error.

## Dependencies and Integration Points
This file depends on `ApiWorkload.h`, `FDBTypes`, `MultiVersionTransaction`, simulator policy state, Flow arena/reference utilities, deterministic random, and `fmt`. It integrates with `ThreadSafeDatabase::createFromExistingDatabase`, `MultiVersionApi::selectApiVersion`, and `MultiVersionDatabase::debugCreateFromExistingDatabase`. The subclass contract is the abstract `performSetup`/`performTest` pair declared in `ApiWorkload.h`.

## Risks and Edge Cases
- `compareDatabaseToMemory` advances `startKey` to the last returned key, so correctness depends on `MemoryKeyValueStore::getRange` and FDB `getRange` having matching continuation semantics for this test's range.
- Random binary keys are converted through `std::string` after adding a NUL terminator; embedded NUL bytes are supported by string construction from `prefix + keyBuffer` only until the first NUL, so key entropy is not a full arbitrary byte array despite random uint32 writes.
- Plaintext marker injection must avoid the first key byte and only occurs when the generated size exceeds the marker size.
- Multi-version and thread-safe paths bridge thread futures to Flow futures; API mismatch bugs can appear only in selected transaction modes.
- `clearKeyspace` uses formatted decimal prefixes and assumes adjacent formatted client ids define a non-overlapping lexical range.

## Test Signals
Failures emit `TestFailure`, `*_CompareSizeMismatch`, `*_CompareValueMismatch`, and `FailedComparisonToMemory` trace events, plus stdout dumps of mismatched DB and memory ranges. Transaction-mode selection prints the selected API per client. `check` returns the `success` latch.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ApiWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ApiWorkload.h -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ApiWorkload.h

## Purpose
`ApiWorkload.h` declares the common transaction abstraction and base workload used by FoundationDB API correctness workloads. It allows the same workload logic to run against native Flow transactions, ReadYourWrites transactions, thread-safe transactions, and multi-version transactions while maintaining a per-client in-memory oracle.

## Important APIs, Types, and Functions
- `TransactionType`: `NATIVE`, `READ_YOUR_WRITES`, `THREAD_SAFE`, `MULTI_VERSION`.
- `TransactionWrapper`: abstract reference-counted interface for set, commit, get, range reads, mapped range reads, key selectors, clear, `onError`, read/commit version, version vector, span context, debug, and conflict range operations.
- `FlowTransactionWrapper<T>`: adapts Flow transaction types such as `Transaction` and `ReadYourWritesTransaction` to `TransactionWrapper`. It can optionally recreate transactions against an extra simulated DB after errors.
- `ThreadTransactionWrapper`: adapts thread-safe `ITransaction` by converting thread futures to Flow futures.
- `TransactionFactoryInterface` and templated `TransactionFactory<T, DB>`: construct wrapper instances for the selected API.
- `ApiWorkload : TestWorkload`: owns workload options, per-client prefix, success flag, data-generation parameters, memory store, and the selected transaction factory.
- Abstract hooks `performSetup` and `performTest` define the subclass contract.

## Control Flow
Subclasses rely on `ApiWorkload::setup` and `ApiWorkload::start` from the `.cpp` file. The base class constructor reads options, computes the decimal client prefix, initializes random key/value size controls, and discovers whether the simulator has an extra database available. A subclass calls `chooseTransactionFactory`, then uses `createTransaction` to obtain `TransactionWrapper` instances without caring which API implementation is underneath.

The wrapper methods mostly forward directly to the underlying transaction. `FlowTransactionWrapper::onError` stores the old transaction and creates a new one when extra DB routing is enabled. `ThreadTransactionWrapper` wraps every async operation with `unsafeThreadFutureToFuture`.

## State and Persistence Behavior
`ApiWorkload` maintains a client-local keyspace prefix and an in-memory `MemoryKeyValueStore` oracle. It does not itself persist anything except through transactions created by subclasses. Key generation options influence the density of collisions and range behavior. `transactionFactory` is reference-counted runtime state; `transactionType` records the chosen mode. `extraDB` is only used in simulation and is sourced from `fdbSimulationPolicyState().extraDatabases`.

## Dependencies and Integration Points
The header depends on tester workload infrastructure, `ClusterConnectionMemoryRecord`, `ReadYourWrites`, `ThreadSafeTransaction`, and `MemoryKeyValueStore`. It is included by workload implementations such as `ApiWorkload.cpp` and `ApiCorrectness.cpp`. It is also an API compatibility layer across NativeAPI, RYW, ThreadSafe, and MultiVersion transaction stacks.

## Risks and Edge Cases
- The abstract wrapper must stay aligned with FDB transaction API changes. New required methods or option semantics must be implemented in both Flow and thread-safe wrappers.
- `ThreadTransactionWrapper` ignores `extraDB`/`useExtraDB`, so tests involving extra simulated DB routing only cover Flow wrappers.
- `FlowTransactionWrapper::lastTransaction` preserves the previous transaction after `onError`; lifetime behavior depends on move semantics and may matter if outstanding futures are still referenced.
- `getMappedRange`, version-vector, and span-context methods are exposed even if only some workloads exercise them, so regressions may remain latent.
- The base class uses an explicit constructor with `maxClients = -1` default, and clients with `clientId >= maxClients` are skipped by implementation logic in the `.cpp`.

## Test Signals
This header contributes no standalone tests, but its wrappers are exercised by `ApiCorrectness` when it randomly selects transaction types. Failures propagate through subclass `testFailure` and comparison traces. Compile coverage itself is significant because every wrapper must satisfy the `TransactionWrapper` virtual interface.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ApiWorkload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFile.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFile.cpp

## Purpose
`AsyncFile.cpp` implements the common support classes for async file tester workloads. It provides deterministic random byte generation, aligned buffer allocation, temporary file cleanup, common workload options, and a trivial default check.

## Important APIs, Types, and Functions
- `RandomByteGenerator`: precomputes a 16 MiB deterministic random buffer and fills output by XORing two random aligned slices.
- `AsyncFileWorkload::_PAGE_SIZE`: 4096-byte page alignment constant.
- `AsyncFileWorkload::AsyncFileWorkload`: reads options `testDuration`, `unbufferedIO`, `uncachedIO`, `fillRandom`, and `fileName`; enables only `clientId == 0`.
- `AsyncFileWorkload::allocateBuffer`: returns `AsyncFileBuffer` with alignment matching `unbufferedIO`.
- `AsyncFileWorkload::check`: default success result for throughput-style workloads.
- `AsyncFileBuffer`: allocates/free normal or page-aligned buffers and zeroes memory.
- `AsyncFileHandle`: stores an `IAsyncFile`, path, and temporary flag; destructor deletes temporary files.

## Control Flow
The constructor initializes common options and path state. Workload subclasses call `allocateBuffer` for IO buffers and `openFile` from the header to open or create files. `RandomByteGenerator::writeRandomBytesToBuffer` chooses two distinct offsets into the precomputed random buffer, XORs 64-bit words into the caller's buffer, and is used by file creation/read-write mixed workloads.

## State and Persistence Behavior
`AsyncFileHandle` owns whether a file is temporary. If `temporary` is true, its destructor calls `deleteFile(path)`, so workloads that create unnamed test files clean up when the handle drops. `AsyncFileBuffer` owns heap memory only. `AsyncFileWorkload` stores `fileHandle`, `fileSize`, and path but leaves actual file mutation to subclasses and `openFile`.

## Dependencies and Integration Points
The file depends on tester workload infrastructure, `ActorCollection` indirectly for workload patterns, and `AsyncFile.h`. It integrates with Flow deterministic random and `IAsyncFile` via types declared in the header. It is shared by `AsyncFileCorrectness`, `AsyncFileRead`, and `AsyncFileWrite`.

## Risks and Edge Cases
- `RandomByteGenerator::~RandomByteGenerator` uses `delete` on an array allocated with `new char[]`; this is a memory-management risk and should be checked against compiler/runtime expectations.
- `writeRandomBytesToBuffer` assumes 8-byte-aligned buffers and byte counts; callers with unaligned sizes could violate the comment contract.
- On POSIX, `posix_memalign` failure leaves `buffer = nullptr`, then logs `TestFailure` and asserts. There is no graceful workload failure path.
- Temporary file cleanup happens in a destructor and ignores delete errors.

## Test Signals
The file has no direct tests. It emits `TestFailure` for allocation failure through `AsyncFileBuffer`. Behavior is indirectly tested by all async file workloads through successful setup/start and cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFile.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFile.h -->
# sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFile.h

## Purpose
`AsyncFile.h` declares shared async file workload utilities and implements the common `openFile` actor inline. It centralizes file opening, option handling, aligned buffer requirements, file prefill behavior, and cleanup semantics for async file correctness and throughput workloads.

## Important APIs, Types, and Functions
- `RandomByteGenerator`: deterministic random filler used for optional random file contents.
- `AsyncFileBuffer`: reference-counted buffer wrapper with optional 4 KiB alignment.
- `AsyncFileHandle`: reference-counted `IAsyncFile` wrapper with path and temporary cleanup flag.
- `AsyncFileWorkload`: base `TestWorkload` with options for unbuffered/uncached IO, random filling, enablement, test duration, file handle, file size, and path.
- `AsyncFileWorkload::openFile`: actor that closes/replaces an existing handle, chooses a temporary file name if needed, adjusts flags, opens through `IAsyncFileSystem`, optionally truncates and fills the file in chunks, and records the handle.

## Control Flow
`openFile` first clears an existing `fileHandle->file` and waits briefly to let outstanding references drain. If no path is configured, it generates `asyncfile.<UID>`, forces read-write/create flags, and marks the handle temporary. If filling an existing file, it forces read-write. It adds `OPEN_UNBUFFERED` and/or `OPEN_UNCACHED` from options, opens the file, records or updates `fileHandle`, then optionally grows/truncates to a page-aligned size and writes 256 KiB chunks. Writes are pipelined one chunk behind by awaiting the previous write after issuing the next.

## State and Persistence Behavior
The actor may create a temporary file and later delete it through `AsyncFileHandle` destruction. Fill behavior aligns the target size upward to page boundaries and can truncate existing files before writing. The file path remains in `self->path` after temporary-name generation, so later reopen operations target the same file. `fileSize` is a workload field but `openFile` receives the desired size as a parameter and does not always update `self->fileSize` directly; callers usually read `file->size()` afterward.

## Dependencies and Integration Points
The header depends on tester workload infrastructure and `flow/IAsyncFile.h`. It is included by all async file workload implementations. Its `openFile` actor integrates directly with `IAsyncFileSystem::filesystem()->open`, `IAsyncFile::write`, `truncate`, and `sync` semantics.

## Risks and Edge Cases
- Existing handles are nulled before a fixed 0.1-second delay; long outstanding uncancellable IO may still hold references, so callers rely on `holdWhile` in workload operations.
- Fill size is rounded up to 4 KiB. Tests expecting exact configured size need to account for this.
- The fill loop starts at `oldSize & ~(chunkSize - 1)`, so extending a partially filled chunk can rewrite from the previous chunk boundary.
- The open failure path logs `TestFailure` and rethrows, leaving the caller to mark workload failure or abort.
- Unbuffered IO correctness depends on callers using aligned buffers, offsets, and sizes.

## Test Signals
Open failures emit `TraceEvent(SevError, "TestFailure").detail("Reason", "Could not open file")`. File-building progress prints per GiB. Success is observed indirectly through async file workload setup and operation metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFileCorrectness.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFileCorrectness.cpp

## Purpose
`AsyncFileCorrectness.cpp` implements the `AsyncFileCorrectness` workload. It stress-tests `IAsyncFile` read, write, sync, reopen, and truncate behavior against an in-memory file model while allowing multiple outstanding operations and respecting byte-level locks to avoid ambiguous overlapping IO.

## Important APIs, Types, and Functions
- `OperationType`: `READ`, `WRITE`, `SYNC`, `REOPEN`, `TRUNCATE`.
- `OperationInfo`: operation descriptor containing buffer, offset, length, flush requirement, operation type, and operation slot index.
- `AsyncFileCorrectnessWorkload : AsyncFileWorkload`: workload registration type with options `maxOperationSize`, `numSimultaneousOperations`, and `targetFileSize`.
- `_setup`: allocates memory model, lock vector, validity mask, initializes file size, and opens/creates the test file.
- `_start`: runs the correctness loop under `testDuration`, samples CPU utilization, and drains outstanding operations.
- `runCorrectnessTest`: schedules concurrent operations, validates reads, manages postponed flushing operations, and replaces completed operation slots.
- `generateOperation`: randomly chooses operation type, offset, length, and locking behavior.
- `checkFileLocked`: prevents write/write and read/write overlap in ambiguous regions.
- `processOperation`: executes actual file operation and updates or validates in-memory model.

## Control Flow
Setup allocates a target-sized memory buffer, byte lock vector, validity mask, and creates the file. Start begins custom system monitoring, runs `runCorrectnessTest` until timeout, computes CPU utilization, then gives outstanding operations up to ten seconds to finish. The correctness loop keeps up to `numSimultaneousOperations` live operations unless a flushing operation (`REOPEN` or `TRUNCATE`) is pending. Reads and writes can run concurrently only when byte locks permit; flushing operations are postponed until all live operations are drained and then run serially.

Read completion checks the number of bytes read and compares valid ranges against the memory model. Unknown ranges, tracked by `fileValidityMask`, become known after reading. Write operations fill a buffer with deterministic random bytes, update the memory model and validity mask, perform an uncancellable write, and update `fileSize` if extended. Reopen verifies that file size did not shrink and did not grow by at least a page; truncate verifies the resulting file size and resizes the memory model/lock/mask arrays.

## State and Persistence Behavior
The real file is the persistent test target, usually temporary via `AsyncFileWorkload`. `memoryFile` mirrors expected bytes. `fileLock` stores `0xFFFFFFFF` for write locks and read counts otherwise. `fileValidityMask` marks which byte ranges are known and comparable; unknown bytes can arise from sparse/unwritten areas and are learned on reads. `fileSize` tracks expected logical size, while `targetFileSize` defines the main operating range and can be expanded when concurrency and operation size would otherwise make locking impractical. `success` latches failures.

## Dependencies and Integration Points
The workload depends on `AsyncFile.h`, `IAsyncFile`, Flow deterministic random, `ActorCollection`, `SystemMonitor`, and tester `WorkloadFactory`. It uses `uncancellable` and `holdWhile` to protect file handles and buffers for IO that may not be cancellable.

## Risks and Edge Cases
- The read validation code appears to compare `fileValidityMask` bytes against read data in one branch where it likely intended `memoryFile`; this should be treated as a high-value review target.
- Byte-level lock vectors can be large for large target files and are updated per byte, which is expensive but precise.
- Operations that read or write past current file size require careful `min` calculations; signed/unsigned mixing around `fileSize - info.offset` deserves attention.
- Reopen allows less than one page of apparent size growth, reflecting alignment behavior; changing filesystem semantics may require adjusting this tolerance.
- Truncate/reopen flush all outstanding operations through `flushOperations`; missing a new flushing operation type could introduce model races.

## Test Signals
`check` returns `success`. Failures print messages for incorrect reads, incorrect read lengths, reopen size changes, and truncate size mismatches. Metrics include `Number of Operations Performed` and average CPU utilization. Workload registration is `AsyncFileCorrectnessWorkloadFactory`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFileCorrectness.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFileRead.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFileRead.cpp

## Purpose
`AsyncFileRead.cpp` implements the `AsyncFileRead` throughput workload. It opens or creates a file, optionally fills/resizes it, issues parallel reads or mixed read/write operations, supports batched and unbatched modes, and reports bytes-per-second plus CPU utilization. It is primarily a performance and stress workload rather than a content correctness oracle.

## Important APIs, Types, and Functions
- `IOLog` and nested `ProcessLog`: rolling trace metrics for issue rate, completion rate, and latency, split by read/write.
- `AsyncFileReadWorkload : AsyncFileWorkload`: workload registration type with `NAME = "AsyncFileRead"`.
- Options: `numParallelReads`, `readSize`, `fileSize`, `unbatched`, `sequential`, `writeFraction`, `randomData`, and `fixedRate`.
- `_setup`: aligns read size for unbuffered IO, allocates read buffers, opens/fills file, and records actual file size.
- `_start`: runs the read test under `testDuration`, samples CPU, and drains outstanding read futures.
- `readLoop`: unbatched per-buffer loop that optionally rate-limits, chooses random offsets, optionally writes, logs IO timing, and accumulates bytes.
- `runReadTest`: either starts unbatched loops or repeatedly issues batches of parallel reads and waits for all.

## Control Flow
Setup prepares buffers and opens the file read-write/create. If `fileSize` is nonzero, the common `openFile` helper fills/truncates the file. In unbatched mode, `runReadTest` creates one actor per parallel slot and each actor loops independently, optionally waiting on a Poisson process derived from `fixedRate / numParallelReads`. Each unbatched iteration randomly chooses an offset, optionally turns into a write based on `writeFraction`, logs issue/completion, and waits uncancellably with `holdWhile`.

In batched mode, the workload maintains an offset. Sequential mode advances by `readSize` and wraps at EOF; random mode chooses random offsets, page-aligned for unbuffered IO. It issues `numParallelReads` reads, waits for all, accounts bytes, clears futures, and yields.

## State and Persistence Behavior
The workload reads from and may write to a file target managed by `AsyncFileWorkload`. In unbatched mixed mode, writes mutate the file but no memory model validates contents. `bytesRead` is incremented by requested read/write size rather than actual bytes returned. `readBuffers` must remain alive across uncancellable IO through `holdWhile`. `ioLog` is dynamically allocated during unbatched mode and rolls trace metrics every five seconds.

## Dependencies and Integration Points
The file depends on tester workload infrastructure, `ActorCollection`, `SystemMonitor`, `IAsyncFile`, `AsyncFile.h`, and `DeterministicRandom`. It uses `poisson` for fixed-rate pacing and Flow trace events through `IOLog`.

## Risks and Edge Cases
- `randomData` is read from options but not used; writes always use `RandomByteGenerator` data when `writeFraction` selects a write.
- Offsets are chosen from `fileSize - 1`; zero-sized files would be invalid for random reads.
- Unbatched mode deletes `ioLog` only after `waitForAll(readers)`, which is effectively never reached except by cancellation/error.
- Byte accounting uses requested `readSize`, not actual bytes read near EOF.
- Mixed read/write mode is performance-oriented and does not verify data consistency.

## Test Signals
Metrics include `Bytes read/sec` and `Average CPU Utilization (Percentage)`. `IOLog` emits `ProcessLog` trace events for issue/completion/duration rates and latencies. Workload completion success is inherited from `AsyncFileWorkload::check`, which returns true unless setup/start throws.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFileRead.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFileWrite.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFileWrite.cpp

## Purpose
`AsyncFileWrite.cpp` implements the `AsyncFileWrite` throughput workload. It repeatedly issues parallel asynchronous writes to a file, optionally sequentially wrapping through a fixed-size file or randomly targeting offsets, syncs between batches, and reports write throughput and CPU utilization.

## Important APIs, Types, and Functions
- `AsyncFileWriteWorkload : AsyncFileWorkload`: workload registration type with `NAME = "AsyncFileWrite"`.
- Options: `numParallelWrites`, `writeSize`, `fileSize`, and `sequential`, plus inherited async file options.
- `_setup`: aligns write size for unbuffered IO, allocates the write buffer, opens the file with initial size zero for sequential mode or configured size for random mode, and records actual size if nonzero.
- `_start`: runs `runWriteTest` under `testDuration`, samples CPU utilization, and drains outstanding write futures.
- `runWriteTest`: issues `numParallelWrites` writes per batch, waits for them, waits for the previous sync, starts a new sync, clears futures, and increments `bytesWritten`.

## Control Flow
Setup prepares one shared write buffer. Sequential mode opens/truncates initial size to zero but retains the configured `fileSize` target for wraparound behavior; non-sequential mode opens with the configured file size. The write loop starts at `offset = fileSize`, then for each parallel write submits an uncancellable write protected by `holdWhile`. After submission, it advances or randomizes the next offset. Once a batch is issued, it waits for all writes, waits for the previous batch's sync, starts syncing the current batch, clears the future vector, and accounts bytes.

## State and Persistence Behavior
The workload mutates the target file through writes and syncs. It does not validate file contents. The write buffer is zero-filled by `AsyncFileBuffer` and is reused for every write unless a subclass or future change mutates it. `bytesWritten` counts requested bytes per batch. Temporary file persistence/cleanup follows `AsyncFileHandle` semantics from the base class.

## Dependencies and Integration Points
The file depends on tester workload infrastructure, `ActorCollection`, `SystemMonitor`, `IAsyncFile`, and `AsyncFile.h`. It integrates with the Flow actor runtime through `uncancellable`, `holdWhile`, `waitForAll`, and `timeout`.

## Risks and Edge Cases
- The first write in sequential mode is submitted at offset equal to `fileSize` before the offset is wrapped, which can extend the file by a partial or zero-length write depending on `std::min(writeSize, fileSize - offset)`. This is a notable behavior to review for intended throughput semantics.
- If `numParallelWrites` is zero, the loop repeatedly waits on empty futures, syncs, and accounts zero bytes, providing no useful load.
- Random offset selection uses `fileSize - 1`; invalid when file size is zero.
- Byte accounting uses configured write size, not the actual length passed to writes near the end of the file.
- Reusing one buffer across parallel writes is safe only because the buffer is not modified while writes are outstanding.

## Test Signals
Metrics include `Bytes written/sec` and `Average CPU Utilization (Percentage)`. The inherited check returns true. Setup/start exceptions are the main failure signal. Workload registration is `AsyncFileWriteWorkloadFactory`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFileWrite.cpp -->
