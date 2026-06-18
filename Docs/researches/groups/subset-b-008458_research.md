# Research Report: subset-b-008458

This grouped report covers the FoundationDB cluster-controller status implementation and declarations plus the commitproxy build target listed for `subset-b-008458`. Each source file section is delimited for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/Status.cpp -->
# sources/storage-engines/foundationdb/fdbserver/clustercontroller/Status.cpp

## Purpose
`Status.cpp` builds FoundationDB cluster status JSON for the cluster controller. It gathers live worker trace events, cluster interface state, configuration system keys, data distribution state, ratekeeper metrics, storage/tlog/proxy metrics, client registration metadata, layer status JSON, lock state, consistency scan state, gray-failure data, and cross-datacenter lag into a `StatusReply`. It also derives the smaller fault-tolerance-only status view from a full status JSON string and includes unit tests for JSON building, JSON merge semantics, and status deadline behavior.

## Important APIs, Types, and Functions
- `RecoveryStatus::names` and `RecoveryStatus::descriptions` define the user-facing recovery-state names and remediation text indexed by `RecoveryStatus`.
- `StorageServerStatusInfo` extends `StorageServerMetaInfo` with an `EventMap` of fetched trace-event metrics.
- `ClusterGetStatusState` owns the shared `JsonBuilderObject`, message array, and incomplete-reason set used by the outer deadline race and the inner status actor.
- `LatencyProbeState` owns four `Transaction` instances used by asynchronous latency probes that can outlive their parent fetcher.
- `StatusCounter` parses and aggregates trace counter strings of the form `hz roughness counter`, then emits JSON.
- Worker/event helpers include `latestEventOnWorker`, `latestErrorOnWorkers`, and `getWorker`.
- JSON fetchers include `machineStatusFetcher`, `processStatusFetcher`, `clientStatusFetcher`, `recoveryStateStatusFetcher`, `latencyProbeFetcher`, `versionEpochStatusFetcher`, `consistencyCheckStatusFetcher`, `logRangeWarningFetcher`, `configurationFetcher`, `dataStatusFetcher`, `workloadStatusFetcher`, `clusterSummaryStatisticsFetcher`, `layerStatusFetcher`, `lockedStatusFetcher`, and `storageWigglerStatsFetcher`.
- Role and metric helpers include `RolesInfo`, `getServerMetrics`, `getStorageServerStatusInfos`, `getTLogsAndMetrics`, `getCommitProxiesAndMetrics`, `getGrvProxiesAndMetrics`, `tlogFetcher`, `faultToleranceStatusFetcher`, and `getPerfLimit`.
- Exported entry points are `clusterGetStatus(...)` and `clusterGetFaultToleranceStatus(const std::string&)`.

## Control Flow
`clusterGetStatus` creates a reference-counted `ClusterGetStatusState` and races `clusterGetStatusImpl` against `delay(deadlineTimeout)`. If the inner actor errors or misses the deadline, the outer actor records a `status_incomplete` reason but still appends outer fields that can be computed without waiting: client status, incompatible connections, datacenter/log/storage lag, and final messages. This design intentionally returns partial status rather than blocking indefinitely.

`clusterGetStatusImpl` first locates key workers for master, cluster controller, data distributor, ratekeeper, and consistency scan from the supplied `workers` list, recording messages when expected roles are unreachable. It then fetches latest `MachineMetrics`, `ProcessMetrics`, `NetworkMetrics`, latest error events, trace-file open errors, and `ProgramStart` from all workers, merging nonresponders into an `unreachable_processes` message. It concurrently retrieves recovery state, idempotency ID status, and version epoch status, then populates protocol version, connection string, bounce impact, and generation fields.

If configuration is readable, the implementation runs a latency probe before other expensive sections, sets `database_available`, and starts warning checks for consistency-check suspension and duplicate mutation streams. It concurrently launches storage-server, tlog, commit-proxy, and GRV-proxy metric fetches; data distribution, workload, layer, lock, and cache-statistics section fetches; active primary DC reads; optional storage-wiggler reads; and coordinator hostname resolution. It then derives logs, fault tolerance, configuration, workload, qos, data, lock state, page cache, process role sections, active TSS count, storage-wiggler details, degraded process count, consistency scan state, cluster-controller timestamp, and optional gray-failure status.

`processStatusFetcher` assembles one process object per worker. It builds a `RolesInfo` index from master, cluster controller, data distributor, ratekeeper, consistency scan, current and old logs, routers, backup workers, coordinators, commit proxies, GRV proxies, tlogs, storage servers, and resolvers. For each worker it adds process metrics, locality, uptime, CPU/disk/network/memory, version/command line, messages from latest errors/process issues/trace-file errors/lagging storage servers, exclusion state, process class, degraded flag, run-loop busyness, and all roles for that address.

`clusterGetFaultToleranceStatus` parses an existing full status JSON using `JSONDoc` and copies only `fault_tolerance`, `data`, `logs`, maintenance fields, `qos`, `recovery_state`, and `messages` into a new `StatusReply`.

## State and Persistence Behavior
Most state is ephemeral status JSON and live actor state. The function reads persistent cluster state from system keys such as configuration keys, datacenter replica keys, healthy-zone state, rebalance/data-distribution mode keys, layer status metadata, database lock key, primary datacenter key, storage-wiggle metrics, and consistency scan state. It also queries live state from worker trace-event buffers and current `ServerDBInfo` interfaces. The latency probes create lock-aware transactions and the commit probe performs a self-conflicting system-immediate commit, but the probe does not intentionally write user data. `clientStatusFetcher` and `getClientIssuesAsMessages` mutate the caller-owned client-status map by erasing stale entries older than twice the coordinator register interval.

## Dependencies and Integration Points
The file depends heavily on Flow actors, `JsonBuilder`, `json_spirit`, worker event-log request endpoints, `ServerDBInfo`, `DatabaseConfiguration`, `ServerCoordinators`, storage/log/proxy interfaces, system key constants, `ReadYourWritesTransaction`, `SystemDBWriteLockedNow`, ratekeeper limit reason tables, consistency scan state, storage wiggle APIs, backup/mutation-stream metadata, and global knobs. The entry point is declared in `Status.h` and is consumed by cluster-controller request handling to serve status requests. The status schema is an external integration surface for `fdbcli status json`, monitoring tools, tests, and administrative workflows.

## Risks and Edge Cases
Status collection intentionally tolerates partial data, so consumers must treat `messages` and `status_incomplete` as part of the contract. Many sections rely on exact trace-event field names; missing or renamed fields usually degrade to incomplete reasons, but some paths use `ASSERT` or unchecked map access and can fail harder if invariants are violated. `processStatusFetcher` reads `ssLag[address]`, which default-inserts zero for non-storage addresses. Rate calculations divide by elapsed values in several sections; some guard against zero elapsed, while cache hit-rate aggregation assumes nonzero process elapsed when metrics exist. `clientStatusFetcher` and `getClientIssuesAsMessages` both prune the same client-status map, so call ordering affects which stale samples remain for later reporting. Coordinator zone failure calculations map unresolved coordinator addresses to an empty zone if no matching worker exists. The deadline race leaves child actors able to continue briefly against reference-counted shared state, which is why `ClusterGetStatusState` and `LatencyProbeState` are heap-owned; future edits must preserve that lifetime property.

## Test Signals
The file contains `/status/json/builder` for JSON serialization and raw-number safety, `Lstatus/json/builderPerf` for large random JSON generation/serialization performance, `/status/json/merging` for `JSONDoc` merge operators such as `$sum`, `$min`, `$max`, `$latest`, `$last`, `$expires`, and `$count_keys`, and `/fdbserver/clustercontroller/clusterGetStatusTimeout` to verify `clusterGetStatus` returns partial results within a deadline even when internal database work hangs. Broader integration signals are successful `fdbcli status json` output, simulation status requests during recovery and degraded states, monitoring schema compatibility, and correct `status_incomplete` messages when workers or system-key reads time out.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/Status.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/Status.h -->
# sources/storage-engines/foundationdb/fdbserver/clustercontroller/Status.h

## Purpose
`Status.h` declares the cluster-controller status API used to produce full cluster status JSON and fault-tolerance-only status JSON. It also defines the small `ProcessIssues` carrier used to attach issue names to worker network addresses before status rendering.

## Important APIs, Types, and Functions
- `struct ProcessIssues` stores a `NetworkAddress address` and a `Standalone<VectorRef<StringRef>> issues`. The constructor takes both values and stores them directly.
- `clusterGetStatus(...)` returns `AsyncResult<StatusReply>` and accepts the live `ServerDBInfo`, database handle, worker list, process issues, storage-server metadata, client-status map pointer, coordinators, incompatible connection addresses, datacenter/log/storage lag versions, degraded-server gray-failure exclusions, and a deadline timeout.
- `clusterGetFaultToleranceStatus(const std::string& statusString)` returns a `StatusReply` containing a filtered subset of a full status JSON payload.

## Control Flow
The header contains declarations only. Its control-flow significance is in the async return type: callers start `clusterGetStatus` as a Flow actor and eventually receive a `StatusReply`; `clusterGetFaultToleranceStatus` is synchronous over an already available JSON string.

## State and Persistence Behavior
No state is persisted in the header. `ProcessIssues` owns its supplied issue vector and is passed by value in vectors to status collection. `clusterGetStatus` receives a pointer to a mutable client-status map; the implementation prunes stale clients while rendering status.

## Dependencies and Integration Points
The header includes RPC, coordination, worker, master, and cluster interface types from `fdbrpc`, `fdbserver/core`, and `fdbclient`. It is the narrow public declaration surface between the cluster-controller implementation and code that serves cluster status requests.

## Risks and Edge Cases
Because the API takes many by-value vectors and a raw pointer to the client-status map, callers must ensure the map outlives the actor and that copying worker/storage metadata is acceptable. `deadlineTimeout` is part of the public contract; callers that pass too large a timeout can delay status responses, while too small a timeout increases partial results. The fault-tolerance helper assumes its input is valid full status JSON and will throw on parse errors.

## Test Signals
The implementation file includes a focused timeout unit test for `clusterGetStatus` and JSON tests for supporting builders. Compile/link tests that include this header validate type visibility for `StatusReply`, `ServerDBInfo`, `WorkerDetails`, `StorageServerMetaInfo`, `OpenDatabaseRequest`, and `ServerCoordinators`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/Status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/include/fdbserver/clustercontroller/ClusterController.h -->
# sources/storage-engines/foundationdb/fdbserver/clustercontroller/include/fdbserver/clustercontroller/ClusterController.h

## Purpose
`ClusterController.h` declares the cluster-controller actor entry point. The cluster controller coordinates cluster leadership/identity state and exposes the full cluster-controller interface through async variables consumed elsewhere in the server.

## Important APIs, Types, and Functions
- Forward declaration `struct ClusterControllerFullInterface` avoids including the full interface definition in this public header.
- `clusterController(...)` returns `Future<Void>` and accepts the cluster connection record, an async variable for the current cluster-controller interface, an async variable for priority information, locality data for the process, and an async variable for the optional cluster ID.

## Control Flow
This header does not implement behavior. It establishes that the cluster controller is a long-running Flow actor. The actor receives shared references to mutable async state, updates those variables as leadership or metadata changes, and completes only on shutdown or error.

## State and Persistence Behavior
The declaration exposes no persistent state directly. The parameters identify the state channels the implementation owns or updates: the durable/coordination-backed cluster connection record, published current cluster-controller interface, priority info, process locality, and optional cluster ID.

## Dependencies and Integration Points
The header depends on `IClusterConnectionRecord`, FDB types, locality data, and Flow futures/async variables. It is included by server startup and cluster-controller implementation code that needs to spawn or refer to the cluster-controller actor without depending on the full implementation internals.

## Risks and Edge Cases
The API relies on shared `Reference<AsyncVar<...>>` objects; consumers can observe transitions, empty optionals, or stale values depending on actor timing. Forward-declaring `ClusterControllerFullInterface` keeps compile dependencies light but requires any user that dereferences the interface contents to include the full definition elsewhere. The actor signature includes both connection-record and cluster-ID state, so mismatches between persisted coordination state and published async variables are important integration risks handled by the implementation, not by this header.

## Test Signals
Build and link coverage are the main direct signals for this header. Runtime signals come from cluster startup/recovery tests that spawn the cluster controller, observe `currentCC`, update priority info, and publish a cluster ID.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/include/fdbserver/clustercontroller/ClusterController.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/commitproxy/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbserver/commitproxy/CMakeLists.txt

## Purpose
`CMakeLists.txt` defines the `fdbserver_commitproxy` static library target for the commit proxy server component. It discovers source files in the directory, configures common server includes, exposes the component's public include directory, adds private source/binary include paths, links required server libraries, and creates a link test target.

## Important APIs, Types, and Functions
- `fdb_find_sources(FDBSERVER_COMMITPROXY_SRCS)` populates the component source list from the current directory according to FoundationDB's CMake conventions.
- `add_flow_target(STATIC_LIBRARY NAME fdbserver_commitproxy SRCS ${FDBSERVER_COMMITPROXY_SRCS})` creates the Flow-enabled static library.
- `add_fdbserver_link_test(fdbserver_commitproxylinktest fdbserver_commitproxy fdbserver_logsystem fdbserver_core)` adds a link-only validation target for dependency completeness.
- `configure_fdbserver_common_includes(fdbserver_commitproxy)` applies common include configuration.
- `target_include_directories` publishes `${CMAKE_CURRENT_SOURCE_DIR}/include` and privately includes the source and binary dirs.
- `target_link_libraries(fdbserver_commitproxy PRIVATE fdbserver_core fdbserver_kvstore fdbserver_logsystem)` sets private link dependencies.

## Control Flow
CMake evaluates the file during configure/generate. Source discovery runs first, then the library target is created, the link-test target is declared, include paths are attached, and private dependencies are linked. There is no runtime control flow.

## State and Persistence Behavior
The file persists build graph state only: target names, include visibility, discovered source membership, and static-library dependencies. Generated build files encode this state, but no database or runtime state is touched.

## Dependencies and Integration Points
This component integrates with FoundationDB's custom CMake helpers for Flow actor compilation and server target setup. It depends on `fdbserver_core`, `fdbserver_kvstore`, and `fdbserver_logsystem`, which indicates commit proxy code uses core server interfaces, key-value store support, and log-system types. The public include directory allows downstream targets to include commitproxy headers.

## Risks and Edge Cases
Automatic source discovery can accidentally include or omit files if naming/location conventions are not followed. A missing dependency may pass compilation through transitive includes but fail the explicit link test, so the link test is important. Public include exposure should remain limited to headers intended for other components; moving private headers under `include` broadens the component API. Generated files that require `${CMAKE_CURRENT_BINARY_DIR}` must be produced before compilation by other build rules.

## Test Signals
The primary signals are successful CMake configure/generate, successful build of `fdbserver_commitproxy`, and successful `fdbserver_commitproxylinktest`. Broader server and simulation tests that exercise commit proxy recruitment, transaction commit, conflict handling, and log-system integration validate that the target is linked with the needed runtime dependencies.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/commitproxy/CMakeLists.txt -->
