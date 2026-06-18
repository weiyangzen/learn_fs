# Research Group: subset-b-008430

This grouped report covers FoundationDB client-side bulk loading, build wiring, knob initialization, client status reporting, cluster connection record implementations, commit/coordination helpers, data-distribution JSON export, DR backup orchestration, and database configuration parsing. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BulkLoading.cpp -->
# sources/storage-engines/foundationdb/fdbclient/BulkLoading.cpp

## Purpose

`BulkLoading.cpp` provides small but central utility functions for FoundationDB bulk dump/load metadata. It validates whether a data movement ID represents a logical or physical bulk-load move, converts manifest metadata into native `Key` values, normalizes blobstore/local paths, formats bulk-load enum values for diagnostics, and builds simple `BulkLoadTaskState` / `BulkLoadJobState` instances for manual or test submission.

## Important APIs, Types, And Functions

The public helpers are free functions declared by `fdbclient/BulkLoading.h`. `getConductBulkLoadFromDataMoveId()` decodes the encoded data-move UID via `decodeDataMoveId()` and asserts the invariants required for bulk-load moves: non-empty range, valid non-anonymous shard ID, and assigned state. `dataMoveIdIsValidForBulkLoad()` is the simpler validity predicate used by that assertion. `stringRemovePrefix()` is a strict manifest parser helper that throws `bulkload_manifest_decode_error` if the expected prefix is absent.

`getKeyFromHexString()` converts a space-delimited hex byte string such as `01 02 03` into an FDB `Key`, asserting the exact two-hex-digits-plus-space layout. Filename helpers standardize the job manifest name, byte-sample suffix, and empty manifest name. `convertBulkLoadJobPhaseToString()` and `convertBulkLoadTransportMethodToString()` translate enums into stable trace/user strings and emit error trace events on unexpected values.

The URL helpers use `BLOBSTORE_URL_PATTERN` plus Boost.URL. `getPath()` strips blobstore credentials before parsing and returns the object path without a leading slash. `appendToPath()` preserves the blobstore scheme and optional credentials while replacing the parsed path with a `joinPath()` result. `getBackupDataPath()` rewrites the path under `data/<original>/<suffix>` for backup-container data layout. `getBulkLoadJobRoot()` appends the job UID string to a root URL/path.

## Control Flow

Most functions are synchronous validators/formatters. Blobstore path functions first check whether the input matches `blobstore://...`; local paths fall back to `joinPath()`, while blobstore URLs are parsed after credentials are removed because Boost.URL cannot digest the credential format used here. Parse failures are traced and rethrown as `std::invalid_argument`.

`createBulkLoadTask()` constructs a `BulkLoadManifest`, places it into a single-entry `BulkLoadManifestSet`, and wraps it in `BulkLoadTaskState`. `createBulkLoadJob()` directly constructs a `BulkLoadJobState`.

## State And Persistence

This file does not persist state itself. It encodes naming and path conventions that downstream bulk dump/load actors use when writing manifests and data to local files or blobstore. The task/job construction helpers create in-memory state objects that other bulk-loading code persists through system keys or task metadata.

## Dependencies And Integration Points

Dependencies include `fdbclient/BulkLoading.h`, `fdbclient/SystemData.h`, Boost.URL, Flow tracing/assertion utilities, and system-data functions such as `decodeDataMoveId()`. The helpers integrate with data movement, backup-container path layout, bulk dump/load manifest parsing, and tests or manual task submission flows.

## Risks And Test Signals

The blobstore regex only supports the current `blobstore://` form and has a TODO for `file://`; any credential or URL grammar change can break path preservation. `getKeyFromHexString()` relies on assertions for layout validation, so malformed release-build input may surface as `std::stoul` exceptions or unchecked behavior. Important tests include `bulkload_test` from this directory's CMake file and unit or simulation coverage around credentialed blobstore URLs, local paths, empty keys, and invalid manifest prefixes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/BulkLoading.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbclient/CMakeLists.txt

## Purpose

This CMake file defines the build graph for the `fdbclient` static library, generated option bindings, the sampling-enabled client variant, the `s3client` executable, optional Swift support, optional Azure/AWS backup integrations, link tests, and client-focused tests.

## Important Targets And Build APIs

`fdb_find_sources(FDBCLIENT_SRCS)` discovers client sources, then removes standalone/test entry points and appends `sha1/SHA1.cpp`. The build requires `VEXILLOGRAPHER_COMMAND`; it generates `include/fdbclient/FDBOptions.g.h` and `.cpp` from `fdbclient/vexillographer/fdb.options`, and separately generates the C option header via `vexillographer_compile()`. `fdboptions` is an `ALL` custom target depended on by downstream targets.

`add_flow_target(STATIC_LIBRARY NAME fdbclient ...)` builds the main client library with generated option sources. It publishes source and generated include directories and links `fdbrpc` and `msgpack` publicly while keeping `rapidxml` private. `fdbclient_sampling` repeats the library build with `fdbrpc_sampling` and `ENABLE_SAMPLING`, allowing server-side code to retain sampling without imposing it on pure clients.

`s3client` is built as a Flow executable with explicit include directories for Flow, fdbrpc, md5, libb64, Boost, and generated headers, and links the client, Flow/RPC libraries, compression/hash/support libraries, Boost program options, and platform coroutine/memcpy libraries as needed.

## Control Flow

Configuration first generates headers and build flags, then conditionally augments sources and definitions for Azure and AWS backup. Azure support bootstraps an external `azure-storage-lite` build through configure/build `execute_process()` calls before adding the generated subdirectory. Swift support creates `fdbclient_swift`, generates a module map, wires Swift compiler overlays, and links Swift object files into `fdbclient`.

## State And Persistence

The persistent outputs are generated headers/sources in `${CMAKE_CURRENT_BINARY_DIR}/include/fdbclient/`, configured `BuildFlags.h` and `versions.h`, optional downloaded Azure source/build trees, and CMake targets. The file caches `FDB_OPTIONS_H` for use by other build logic.

## Dependencies And Integration Points

The file depends on repository CMake functions/macros such as `add_flow_target`, `fdb_find_sources`, `vexillographer_compile`, and optional modules `awssdk`, `FindSwiftLibs`, and `GenerateModulemap`. It is the integration point between `fdbclient` actor compilation, generated public option APIs, backup storage providers, Swift interop, and test registration.

## Risks And Test Signals

Hard-coded Boost include path usage in `s3client` can be brittle outside the expected build image. Azure bootstrapping performs configure/build during CMake configuration, so failures surface early and can make reproducibility sensitive to generator and network/cache state. The tests registered on non-Windows non-IDE builds are `s3client_test`, `gcs_client_test` with `USE_MOCK_GCS=true`, and `bulkload_test`; link correctness is also checked by `fdbclientlinktest` and the excluded-by-default `fdbclient_test`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ClientKnobs.cpp -->
# sources/storage-engines/foundationdb/fdbclient/ClientKnobs.cpp

## Purpose

`ClientKnobs.cpp` owns initialization, parsing, and mutation of client-side FoundationDB knobs. These knobs control retry/backoff behavior, location cache sizes, task-bucket and backup behavior, blobstore IO limits, dynamic configuration timeouts, client status reporting, transaction tag throttling, consistency checking, CLI behavior, and simulation randomization.

## Important APIs, Types, And Functions

`ClientKnobs::ClientKnobs()` delegates to `initialize()`. Global state is held by `globalFlowKnobs`, `globalClientKnobs`, `bootstrapGlobalClientKnobs`, and the exported pointer `CLIENT_KNOBS`, initially pointed at the bootstrap instance. `resetClientKnobs()` resets Flow and client knobs to the global mutable instances, while `initializeClientKnobs()` reinitializes the current instances in place.

`tryParseClientKnobValue()` and `parseClientKnobValue()` first ask `FLOW_KNOBS`, then `CLIENT_KNOBS`, to parse a named string value. `trySetClientKnob()` applies a typed `KnobValueRef` to both Flow and client knob sets and reports whether either accepted the name. `setClientKnob()` throws `invalid_option_value` and traces `FailedToSetKnob` on failure. `setupClientKnobs()` is the user-facing batch path; it catches invalid names/values, prints warnings, traces them, and rethrows only unexpected errors.

`ClientKnobs::initialize()` is a long table of `INIT_KNOB` assignments. Many defaults are conditionally perturbed under `randomize && buggify()` to stress simulation: for example proxy counts can drop to one, cache sizes can shrink, timeouts can shorten, and blobstore or consistency-check behavior can vary. `getSimulatedTxnTimeoutSeconds()` feeds simulated transaction lifetime selection.

## Control Flow

Initialization is single-pass and intentionally order-sensitive where knobs derive from earlier values, such as task-bucket timeout versions depending on `CORE_VERSIONSPERSECOND` and blobstore concurrency depending on `BACKUP_TASKS_PER_AGENT`. Parsing/setting paths use typed generated knob maps and reject unknown names. The file also preserves backwards compatibility by adding a `double_knobs` alias from `global_tag_throttling_rw_fungibility_ratio` to the newer non-global field.

## State And Persistence

Knobs are process-global in-memory configuration. They are not persisted here, but they materially influence persistent client/backup behavior by controlling transaction size, task durations, mutation block size, backup log/range partitioning, blobstore IO, and dynamic cluster configuration timeouts. Because the global pointers are mutable through reset/setup helpers, test and simulation code can change effective behavior process-wide.

## Dependencies And Integration Points

Dependencies include `fdbclient/Knobs.h`, Flow knobs, deterministic randomization, Flow unit tests, tracing, and generated knob metadata. The values are consumed throughout `fdbclient`, notably by `DatabaseBackupAgent.cpp`, commit proxy helpers, status reporting, blobstore/backup containers, transaction throttling, and CLI setup.

## Risks And Test Signals

Derived defaults can become stale if base knobs are changed after initialization. The included unit test `/fdbclient/knobs/initialize` explicitly verifies that reinitialization recomputes derived `TASKBUCKET_TIMEOUT_VERSIONS` after `CORE_VERSIONSPERSECOND` is set. Other risk areas are process-global mutation in multi-test environments, simulation-only buggify values hiding production assumptions, and compatibility aliases drifting from public option names.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ClientKnobs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ClientStatusReport.cpp -->
# sources/storage-engines/foundationdb/fdbclient/ClientStatusReport.cpp

## Purpose

`ClientStatusReport.cpp` implements `DatabaseContext::getClientStatus()`, producing a JSON string that describes a client's view of coordinators, proxies, storage servers, transport connections, and overall health.

## Important APIs, Types, And Functions

The implementation is encapsulated in the local `ClientReportGenerator` class. `generateReport()` returns a `Standalone<StringRef>` containing JSON text from `json_spirit`. If the `DatabaseContext` is already in an initialization error state, it reports `InitializationError` and marks health false. Otherwise it calls `reportCoordinators()`, `reportClientInfo()`, `reportStorageServers()`, and `reportConnections()` before writing the `Healthy` flag.

`reportCoordinators()` reads the current `IClusterConnectionRecord`, serializes hostname and address coordinators, records resolved coordinator addresses for later connection checks, and reports the current coordinator if present. `reportClientInfo()` emits cluster ID, GRV proxies, and commit proxies from `ClientDBInfo`. `reportStorageServers()` walks `cx.server_interf` and records SSID/address pairs. `connectionStatusReport()` inspects `FlowTransport::transport().getAllPeers()` and `IFailureMonitor` state for each known server address and adds counters such as failed connects, compatibility, ping samples, timeout count, byte totals, and protocol version.

## Control Flow

The report builds a set of server addresses while traversing coordinators, proxies, and storage servers. A second pass converts that set into connection objects. Health is pessimistically downgraded when there are no coordinators, no current coordinator, no GRV or commit proxies, or any failed connection.

## State And Persistence

No state is persisted. The function snapshots live in-memory client state, transport peer state, and failure monitor state at report generation time. Reported timings such as last connect time and bytes sample time are relative to `now()`.

## Dependencies And Integration Points

The file depends on `DatabaseContext`, `CommitProxyInterface`, `CoordinationInterface`, `FlowTransport`, `IFailureMonitor`, and `json_spirit`. It integrates with client status APIs, management tooling, and diagnostics that need client-side rather than cluster-side visibility.

## Risks And Test Signals

Health is a coarse heuristic and can mark a client unhealthy because a previously known server address is failed even if the cluster has already moved away from it. The report exposes only addresses already known to the client caches. Useful tests include initializing a `DatabaseContext` with missing coordinators/proxies, simulating failed peers, and validating JSON fields for connected, connecting, disconnected, and failed peer states.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ClientStatusReport.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ClusterConnectionFile.cpp -->
# sources/storage-engines/foundationdb/fdbclient/ClusterConnectionFile.cpp

## Purpose

`ClusterConnectionFile.cpp` implements an `IClusterConnectionRecord` backed by a local cluster file. It loads, validates, compares, and atomically persists FoundationDB cluster connection strings.

## Important APIs, Types, And Functions

The read constructor checks `fileExists()`, reads up to `MAX_CLUSTER_FILE_BYTES`, and parses a `ClusterConnectionString`, throwing `no_cluster_file_found` or parse errors as appropriate. The write constructor stores a provided `ClusterConnectionString` and marks it as needing persistence. `openOrDefault()` resolves an explicit path, `FDB_CLUSTER_FILE`, `./fdb.cluster`, or the platform default via `lookupClusterFileName()`.

`setAndPersistConnectionString()` updates `cs` and returns `persist()`. `getStoredConnectionString()` reloads the file synchronously and returns either the parsed string or an error future. `upToDate()` reloads the file unless the record has not yet been persisted, copies the file string into the output parameter, and compares by `toString()`. `getErrorString()` formats user-facing load errors with special handling for default lookup failure.

## Control Flow

Persistence writes a generated warning header plus the connection string through `atomicReplace()`, then immediately calls the base `IClusterConnectionRecord::upToDate()` to verify the file still matches. If another process races and overwrites the file after replacement, it traces `ClusterFileChangedAfterReplace` and returns false.

## State And Persistence

Persistent state is the cluster file named by `filename`. The object also tracks the in-memory `ClusterConnectionString` and the base-class persisted/needs-persisted flag. Persistence is atomic at the file replacement level, but concurrent writers are only detected after the fact.

## Dependencies And Integration Points

The file depends on `fdbclient/ClusterConnectionFile.h`, `MonitorLeader`, platform path lookup, file helpers, Flow futures, and trace events. It is used by clients and servers opening a cluster through a conventional cluster file and by leader-monitoring code that updates connection strings.

## Risks And Test Signals

`toString()` returns a naive `file://` string and does not URI-escape spaces or Windows backslashes. A missing environment-specified file intentionally does not fall back, which should be covered by user-facing error tests. Important test signals include atomic replacement, concurrent writer mismatch, invalid connection strings, default path resolution, and absent cluster file diagnostics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ClusterConnectionFile.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ClusterConnectionKey.cpp -->
# sources/storage-engines/foundationdb/fdbclient/ClusterConnectionKey.cpp

## Purpose

`ClusterConnectionKey.cpp` implements an `IClusterConnectionRecord` whose connection string is stored in a key inside an FDB database. This supports dynamically persisted connection records without relying on a local cluster file.

## Important APIs, Types, And Functions

The constructor stores the target `Database`, the `connectionStringKey`, and the in-memory `ClusterConnectionString`. If constructed from an already persisted value, it also records `lastPersistedConnectionString` for optimistic update checks. `loadClusterConnectionKey()` creates a transaction, reads the key, throws `connection_string_invalid` on absence, parses the value as `ClusterConnectionString`, and retries through `tr.onError()`.

`getStoredConnectionString()` and `upToDate()` are actor wrappers that add a reference to `this` and delegate to static implementations. `upToDateImpl()` reloads the key unless persistence is still pending and compares the loaded string with the in-memory value. `makeIntermediateRecord()` creates a modified but unpersisted copy. `toString()` formats the record as `fdbkey://<printable key>`.

## Control Flow

`persistImpl()` is an optimistic compare-and-set loop. It reads the existing value. If the database already contains the desired value, it records success. If the existing value differs from the last value this object believes it persisted, the function refuses to overwrite it, traces `UnableToChangeConnectionKeyDueToMismatch`, and returns false. Otherwise it writes the new string and commits, retrying retryable errors through `tr.onError()`.

## State And Persistence

Persistent state is one FDB key containing the serialized connection string. In-memory state includes `cs`, the key, database handle, persisted flag, and optional `lastPersistedConnectionString`. The mismatch guard prevents blind overwrites but can leave the stored string stuck if different processes observe and write intermediate states out of order.

## Dependencies And Integration Points

Dependencies include `ClusterConnectionKey.h`, `NativeAPI.actor.h`, transactions, Flow actors/futures, trace events, and `CoordinationInterface` types. It integrates with code that wants `IClusterConnectionRecord` semantics backed by database state rather than files or memory.

## Risks And Test Signals

The main concurrency risk is the documented stuck-state case when connection strings change twice and only an intermediate update reaches storage. Absence of the key maps to invalid connection string rather than a separate missing-key error. Tests should exercise initial load, retry behavior, idempotent persist, mismatch refusal, and `upToDate()` after external updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ClusterConnectionKey.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ClusterConnectionKey.h -->
# sources/storage-engines/foundationdb/fdbclient/ClusterConnectionKey.h

## Purpose

`ClusterConnectionKey.h` declares the database-key-backed `ClusterConnectionKey` connection record. It adapts a `Database` plus `Key` into the `IClusterConnectionRecord` interface used by cluster coordination and leader-monitoring code.

## Important APIs And Types

`ClusterConnectionKey` inherits from `IClusterConnectionRecord`, `ReferenceCounted<ClusterConnectionKey>`, and `NonCopyable`. Its public API exposes construction from a `Database`, key, connection string, and optional `ConnectionStringNeedsPersisted`; static `loadClusterConnectionKey()`; overrides for `setAndPersistConnectionString()`, `getStoredConnectionString()`, `upToDate()`, `getLocation()`, `makeIntermediateRecord()`, and `toString()`; and reference-count forwarding through `addref()` / `delref()`.

Protected `persist()` performs the virtual persistence hook. Private static actor helpers take a `Reference<ClusterConnectionKey>` so async code can safely retain the object across yields. Private state is the backing `Database`, the `connectionStringKey`, and `lastPersistedConnectionString` used for optimistic concurrency checks.

## Control Flow And State

The header establishes a pattern where public virtual methods are thin wrappers and async work is performed by static methods holding explicit references. The object is non-copyable, reference-counted, and stores only the backing location plus last-known persisted value; actual durable data lives in the target database key.

## Dependencies And Integration Points

It includes `fdbclient/CoordinationInterface.h` for `IClusterConnectionRecord` / `ClusterConnectionString` and `fdbclient/NativeAPI.actor.h` for `Database`, `Transaction`, and `Future` types. It is compiled with the implementation in `ClusterConnectionKey.cpp`.

## Risks And Test Signals

Because this header exposes a reference-counted type through an interface, lifetime correctness depends on every async implementation using `Reference<...>::addRef(this)` before yielding. Interface tests should validate that all virtual methods behave consistently with file and memory connection records and that `getLocation()` / `toString()` are stable for diagnostics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ClusterConnectionKey.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ClusterConnectionMemoryRecord.cpp -->
# sources/storage-engines/foundationdb/fdbclient/ClusterConnectionMemoryRecord.cpp

## Purpose

`ClusterConnectionMemoryRecord.cpp` implements a non-persistent in-memory `IClusterConnectionRecord`. It is useful for tests, simulations, or callers that already manage connection-string lifetime externally.

## Important APIs And Functions

`setAndPersistConnectionString()` just assigns `cs` and returns `Void`. `getStoredConnectionString()` returns the current in-memory string. `upToDate()` copies `cs` into the output parameter and always returns true because there is no external durable store to compare. `getLocation()` returns the generated record `id`, while `toString()` prefixes it with `memory://`. `makeIntermediateRecord()` returns a new memory record holding a modified connection string. `persist()` is a successful no-op.

## Control Flow

All operations are synchronous future completions. No retry, IO, or conflict handling is needed.

## State And Persistence

State is limited to the object's in-memory `ClusterConnectionString` and record ID. Nothing survives process lifetime, and `setAndPersistConnectionString()` can mislead callers if they assume persistence means durability rather than successful interface completion.

## Dependencies And Integration Points

The file depends on `fdbclient/ClusterConnectionMemoryRecord.h` and the shared `IClusterConnectionRecord` contract. It integrates with code paths that accept any connection record implementation and do not require a cluster file or database key.

## Risks And Test Signals

The main risk is accidental use where durable connection-string changes are expected. Tests should compare behavior against file/key records, especially `upToDate()` and `persist()` semantics, and ensure generated `memory://` identifiers are useful for trace diagnostics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ClusterConnectionMemoryRecord.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/CommitProxyInterface.cpp -->
# sources/storage-engines/foundationdb/fdbclient/CommitProxyInterface.cpp

## Purpose

`CommitProxyInterface.cpp` supplies explicit template instantiations for client/commit-proxy network types and implements backup mutation chunk helper functions used to split large mutation payloads.

## Important APIs And Functions

The file instantiates `ReplyPromise<ClientDBInfo>`, `ReplyPromise<CachedSerialization<ClientDBInfo>>`, `NetNotifiedQueue<OpenDatabaseCoordRequest, true>`, `ReplyPromise<GetKeyServerLocationsReply>`, and `NetSAV<GetKeyServerLocationsReply>`. These force template code generation in this translation unit for RPC and network serialization types declared in headers.

`getBackupKey(BinaryWriter& wr, uint32_t** partBuffer, int part)` appends or mutates a big-endian part number at the end of a serialized mutation key. The first call serializes `part` and records a pointer to the part field inside the writer buffer; later calls rewrite the pointed-to field without rebuilding the whole key. `getBackupValue(Key& content, int part)` returns a `StringRef` slice of `content` for the requested part using `CLIENT_KNOBS->MUTATION_BLOCK_SIZE`.

## Control Flow

The backup-key helper has two modes: initialize the part suffix and pointer, then update in place for subsequent parts. The value helper computes offset and length with `std::min()` so the last block can be smaller than the block size.

## State And Persistence

No durable state is stored here. The only mutable state is the caller-owned `BinaryWriter` buffer and `partBuffer` pointer. The resulting keys and values are used by backup/commit paths that persist split mutation content elsewhere.

## Dependencies And Integration Points

The file includes `CommitProxyInterface.h`, `CoordinationInterface.h`, and uses `CLIENT_KNOBS`. It integrates with RPC serialization and backup mutation block storage.

## Risks And Test Signals

The pointer returned through `partBuffer` is valid only while the writer buffer is not reallocated; callers must not append in ways that invalidate it after caching the pointer. Tests should cover multi-part mutation key generation, big-endian ordering, exact block boundaries, and final short block slicing.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/CommitProxyInterface.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/CoordinationInterface.cpp -->
# sources/storage-engines/foundationdb/fdbclient/CoordinationInterface.cpp

## Purpose

Despite the stale file banner naming `AutoPublicAddress.cpp`, this file implements `ClusterConnectionString::determineLocalSourceIP()`. It determines the local source IP address the OS would use to reach one of the cluster coordinators.

## Important APIs And Functions

`determineLocalSourceIP()` iterates across `coords` first and `hostnames` second. For hostnames it calls `Hostname::resolveBlocking()` and throws `lookup_failed` if resolution fails. It converts the chosen `NetworkAddress` into a Boost.Asio UDP endpoint, connects an unbound UDP socket to that endpoint, and reads `socket.local_endpoint().address()` to determine the selected local IPv4 or IPv6 source address. If all coordinator candidates fail, it prints to stderr and throws `bind_failed`.

## Control Flow

The method keeps an index over the combined coordinate/hostname list. Each iteration constructs a local `io_service` and UDP socket, resolves the coordinator if necessary, connects, extracts the local endpoint address, closes the socket, and returns. Any exception advances to the next candidate until exhaustion.

## State And Persistence

No persistent state is changed. The function uses kernel routing state and DNS resolution at call time. It does not send application data; UDP `connect()` only binds/defaults the local endpoint for the selected remote.

## Dependencies And Integration Points

The implementation disables Boost auto-link macros, includes Boost.Asio and `CoordinationInterface.h`, and depends on FoundationDB `IPAddress`, `NetworkAddress`, `Hostname`, and Flow error types. It is used by code needing a public/local address choice compatible with coordinator reachability.

## Risks And Test Signals

The function performs blocking hostname resolution and catches all exceptions without tracing individual failures. It assumes at least one coordinator or hostname exists; an empty connection string immediately reaches the failure path. Tests should cover IPv4, IPv6, hostname resolution failure, mixed coord/hostname fallback, and no-candidate behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/CoordinationInterface.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/DataDistributionConfig.cpp -->
# sources/storage-engines/foundationdb/fdbclient/DataDistributionConfig.cpp

## Purpose

`DataDistributionConfig.cpp` serializes a data-distribution range configuration snapshot into JSON for diagnostics or management output.

## Important APIs And Functions

`DDConfiguration::toJSON(RangeConfigMapSnapshot const& config, bool includeDefaultRanges)` returns a `json_spirit::mValue`. It builds an object with a `ranges` array, `numConfiguredRanges`, `numDefaultRanges`, and `numBoundaries`.

Each range in `config.ranges()` is compared with a default-constructed `DDRangeConfig`. Non-default ranges count as configured; default ranges count separately. The function emits a range object with `begin`, `end`, and `configuration` fields when either `includeDefaultRanges` is true or the range is configured.

## Control Flow

The function is a single pass over the range map snapshot. The map boundary count is taken from `config.map.size()`, while emitted range count depends on `includeDefaultRanges`.

## State And Persistence

No state is mutated. The function snapshots an already materialized `RangeConfigMapSnapshot` into a JSON value. Persistent configuration remains in the range config map elsewhere.

## Dependencies And Integration Points

Dependencies include `fdbclient/DataDistributionConfig.h` for `DDConfiguration`, `DDRangeConfig`, and `RangeConfigMapSnapshot`, plus `json_spirit`. It integrates with status or CLI paths that expose data-distribution range configuration.

## Risks And Test Signals

The default/non-default distinction relies on `DDRangeConfig::operator!=` matching user expectations. If `config.map.size()` includes sentinel boundaries, consumers must treat `numBoundaries` as internal map boundary count rather than emitted range count. Tests should cover empty/default-only snapshots, mixed configured ranges, and `includeDefaultRanges` true/false output shape.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/DataDistributionConfig.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/DatabaseBackupAgent.cpp -->
# sources/storage-engines/foundationdb/fdbclient/DatabaseBackupAgent.cpp

## Purpose

`DatabaseBackupAgent.cpp` implements FoundationDB's database-to-database DR backup agent orchestration. It owns task-bucket task functions for full range copy, mutation-log copy, differential backup, legacy upgrade/abort compatibility, status reporting, submit/discontinue/abort flows, and atomic switchover between source and destination clusters.

## Important APIs, Types, And Functions

`DatabaseBackupAgent` constructs subspaces under `databaseBackupPrefixRange` for `states`, `config`, `errors`, `ranges`, tag-name indexes, source-side state, a `TaskBucket`, and a `FutureBucket`. The source-taking constructor also sets `taskBucket->src`.

`DRConfig` stores newer per-DR metrics keyed by UID, notably `rangeBytesWritten()` and `logBytesWritten()`, and can clear its config subspace. `copyDefaultParameters()` propagates common task parameters: folder/backup UID, config log UID, destination UID, and add/remove prefixes. `checkTaskVersion()` rejects task versions newer than the task function supports and logs an error under the backup error subspace.

The registered task functions are the core execution graph:

- `BackupRangeTaskFunc` splits source key ranges on shard boundaries, reads committed source KV data, applies add/remove prefix mapping, writes destination keys, and records per-range version coverage in the apply-mutations key-version map.
- `FinishFullBackupTaskFunc` writes `copy_stop` at a source read version so log-copy work knows when full-copy catch-up can stop.
- `CopyLogRangeTaskFunc` streams mutation log ranges from source backup log keys into destination apply-log keys, batching by `BACKUP_LOG_WRITE_BATCH_MAX_SIZE`, prefetching with `COPY_LOG_PREFETCH_BLOCKS`, and breaking tasks by duration.
- `CopyLogsTaskFunc` repeatedly schedules `CopyLogRangeTaskFunc` slices and old-log erasure while advancing `applyMutationsEndRange`.
- `BackupRestorableTaskFunc` marks the backup restorable, then either schedules final cleanup for stop-when-done or starts differential log copying.
- `FinishedFullBackupTaskFunc` waits until apply has caught up, erases remaining log data, clears config/apply-log state, and marks the backup completed.
- `CopyDiffLogsTaskFunc`, `CopyDiffLogsUpgradeTaskFunc`, `OldCopyLogRangeTaskFunc`, `SkipOldEraseLogRangeTaskFunc`, and `AbortOldBackupTaskFunc` support differential mode and upgrade/abort paths for older task names and layouts.
- `StartFullBackupTaskFunc` initializes source mutation logging, destination UID mapping, begin versions, metadata version bumping, and schedules full-copy/log-copy/restorable tasks.

`DatabaseBackupAgentImpl` provides the public operation bodies: `submitBackup()`, `discontinueBackup()`, `abortBackup()`, `atomicSwitchover()`, `unlockBackup()`, `getStatus()`, `getStateValue()`, `getDestUid()`, `getLogUid()`, `waitUpgradeToLatestDrVersion()`, `waitBackup()`, and `waitSubmitted()`. The public `DatabaseBackupAgent` methods at the end delegate to these static helpers.

## Control Flow

Submission chooses or reuses a log UID, rejects existing runnable backups, coalesces requested ranges, optionally verifies or clears destination ranges, clears old config/state/errors, writes tag/config/state records, initializes apply-mutation version maps and prefix transforms, enqueues `dr_start_full_backup`, and locks or checks the database lock.

`StartFullBackupTaskFunc` then initializes the source-side destination UID and latest-version keys, writes destination-side begin version/config, enables source mutation logging for each backed-up range, bumps metadata version, and schedules parallel full-range copy and log-copy branches. The range-copy branch recursively splits on shard boundaries or restarts from `backupRangeBeginKey` when timeout/map-size pressure occurs. The log-copy branch continuously copies mutation log blocks, erases obsolete source log ranges, and advances apply boundaries until `copy_stop` is reached.

Abort first marks destination config as partially aborted and clears apply endpoints/logs using `COMMIT_ON_FIRST_PROXY` ordering to fence outstanding apply commits, then optionally cleans source-side mutation logs and finally marks the backup aborted. Atomic switchover validates status/locks/mutation stream IDs unless forced or simulated, locks the source, waits for destination apply to reach the lock commit version, stops destination backup, raises destination commit version if needed, starts reverse DR, waits for submission, and unlocks the old destination.

## State And Persistence

State is heavily persisted in FDB system-key subspaces. Destination-side state includes backup config, task-bucket tasks/futures, errors, status text, backup folder UID, DR version, prefix transforms, backup ranges, stop-when-done marker, apply-log keys, apply-mutation begin/end keys, and key-version maps/counts. Source-side state includes mutation log range registrations, destination UID lookup, backup latest-version keys, source status/folder ID, and source tag mapping. `DRConfig` persists byte counters separately under `uid->config`.

## Dependencies And Integration Points

This file depends on BackupAgent primitives, TaskBucket/FutureBucket, NativeAPI actors, management lock APIs, status client, key-backed types, system key encoders such as `applyMutations*`, `backupLogKeys`, `logRangesEncodeKey`, `destUidLookupPrefix`, and many `CLIENT_KNOBS` backup/log constants. It integrates source and destination databases, DR agents, mutation logging, apply-mutation machinery, cluster lock management, status JSON, and simulation probes.

## Risks And Test Signals

Important risks are ordering-sensitive abort/switchover commits, source/destination UID reuse, unbounded retries around non-retryable logical mistakes, legacy task compatibility, task version skew, key-version map growth throttling, and prefix transform correctness. `COMMIT_ON_FIRST_PROXY`, explicit conflict ranges, database-lock checks, byte locks, and task futures are key correctness mechanisms. Test signals should include full backup, stop-when-done completion, differential continuation, abort with and without source cleanup, DR upgrade from old task names, atomic switchover, prefix add/remove mappings, shard-split range copy, log-copy timeout continuation, and byte-counter reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/DatabaseBackupAgent.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/DatabaseConfiguration.cpp -->
# sources/storage-engines/foundationdb/fdbclient/DatabaseConfiguration.cpp

## Purpose

`DatabaseConfiguration.cpp` parses, stores, validates, mutates, and serializes FoundationDB database configuration state read from system keys. It covers replication, storage/log engines, proxy/resolver/log counts, remote and satellite regions, backup workers, perpetual storage wiggle, storage migration, exclusions, and conversion between internal key-value form and JSON/configure strings.

## Important APIs, Types, And Functions

`DatabaseConfiguration::resetInternal()` restores derived fields to invalid/default values while intentionally preserving raw configuration storage. Primitive `parse()` helpers convert `ValueRef` text to integers, `int64_t`, doubles, replication policies, and region vectors. Region parsing reads a status JSON object with region/datacenter/satellite data, supports named satellite redundancy modes, fills fallback settings, and sorts by priority.

`setDefaultReplicationPolicy()` constructs default `PolicyAcross(..., "zoneid", PolicyOne)` policies for storage, tLogs, remote tLogs, and satellite tLogs when explicit policies are absent. `maxZoneFailuresTolerated()` computes tolerated zone failures for single-region and HA/georeplicated configurations, accounting for tLog anti-quorum, storage team size, usable regions, and satellite fallback replication.

`isValid()` enforces a large set of invariants: initialized config, positive process counts, supported tLog versions and engines, valid spill/storage settings, proxy auto-counts, replication policies, remote log settings, region cardinality, unique datacenter IDs, satellite validity, perpetual wiggle locality, and storage migration type. `toJSON()` emits a status/configuration object, using named redundancy modes when the current numeric/policy combination matches known modes and falling back to custom replica/policy fields otherwise. `configureStringFromJSON()` converts JSON back into a configure command string, with legacy compatibility for missing `log_engine`.

`setInternal()` is the central key decoder for `\xff/conf/` keys. It updates fields for proxy counts, logs, replication, engines, workers, regions, exclusions, wiggle, migration, and legacy `proxies`. `overwriteProxiesCount()` splits legacy total `proxies` into commit and GRV proxy counts using explicit overrides or default ratios. `applyMutation()`, `involveMutation()`, `set()`, and `clear()` apply mutations to the configuration view. `makeConfigurationMutable()` and `makeConfigurationImmutable()` convert between sorted `VectorRef<KeyValueRef>` and `std::map` representations.

## Control Flow

Reading from storage calls `fromKeyValues()`, which resets internals, stores raw key-values, applies each key through `setInternal()`, then fills default replication policies. Mutation application switches to mutable map form, updates or clears keys, and reparses when needed. JSON serialization is conditional: default values are omitted unless overridden, known redundancy modes compress multiple fields into a mode string, and backwards-compatible `proxies` is synthesized from commit/GRV counts.

## State And Persistence

The class mirrors persistent system keys under `configKeysPrefix` but does not write transactions itself. It stores either immutable raw configuration or mutable string maps, plus parsed derived fields. Exclusion helpers read excluded/failed server and locality keys from the same configuration snapshot.

## Dependencies And Integration Points

Dependencies include `DatabaseConfiguration.h`, `SystemData.h`, `FDBTypes.h`, Flow tracing/platform/unit-test support, replication policy serialization, status JSON helpers, and `CLIENT_KNOBS` defaults. It integrates with recruitment/recovery, configure command handling, status output, server exclusion logic, storage migration, backup worker enablement, and process-count selection.

## Risks And Test Signals

Parsing uses `atoi`/`atoll`/`atof` with FIXME sanity-check comments, so malformed numeric values may silently become zero. Several compatibility paths are subtle: legacy `proxies` splitting, ignored JSON fields in `configureStringFromJSON()`, missing `log_engine` fallback, and custom policy serialization. The included unit test `/fdbclient/databaseConfiguration/overwriteCommitProxy` verifies legacy proxy splitting equivalence. Additional test signals should cover invalid regions, duplicate datacenter IDs, satellite redundancy modes, excluded server/locality reads, clear-range reparse behavior, known redundancy JSON round trips, and tLog engine/spill validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/DatabaseConfiguration.cpp -->
