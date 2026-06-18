# Research Report: subset-b-008486

This grouped report covers the requested FoundationDB TLog and worker metric/lineage files. Each source file section is wrapped with the required reconciliation markers and preserves the original source path in the section title.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tlog/TLogServer.cpp -->
# sources/storage-engines/foundationdb/fdbserver/tlog/TLogServer.cpp

## Purpose
`TLogServer.cpp` implements the FoundationDB transaction log server actor. It owns the shared physical TLog state for one worker, multiplexes one active and multiple old log generations, receives commit RPCs, makes commits durable through a disk queue, spills old log data into a key-value store, serves peek/pop/lock/recovery RPCs, and restores TLog state from disk after process restart. It is a central durability and recovery component for tag-partitioned log systems.

## Important APIs, Types, And Functions
The public surface is the `tLog(...)` actor declared in `TLogServer.h` plus `effectiveTLogMinAvailableSpaceRatio()`. Internally, `TLogQueueEntryRef` is the durable queue entry for normal commits, while `AlternativeTLogQueueEntryRef` serializes already-parsed recovered messages without rebuilding a single commit blob. `TLogQueue` wraps `IDiskQueue` with packet framing, valid flags, recovery zero-fill, version-location indexing, commit, pop, and forget-before support.

`TLogData` is shared process-level state: persistent stores, active/old log maps, pop/spill order, commit queue coordination, memory/durable byte accounting, flow locks, log-system cache, disk-space controls, and histogram/counter metrics. `LogData` is per-log-generation state: version progress, known committed state, tag data, recovery state, spill metadata, pop tracking, peek trackers, log-system consumer, and role/counter registration. `LogData::TagData` tracks per-tag in-memory messages, popped versions, persistent popped state, popped disk locations, and old-generation recovery participation.

Key actors/functions include `tLogStart`, `tLogCore`, `ServeTLogInterface::run`, `tLogCommit`, `commitQueue`, `doQueueCommit`, `updateStorageLoop`, `updatePersistentData`, `popDiskQueue`, `tLogPeekMessages`, `tLogPeekStream`, `tLogPopCore`, `tLogLock`, `pullAsyncData`, `restorePersistentState`, `initPersistentState`, `rejoinClusterController`, `respondToRecovered`, and `trackRecoveryReq`.

## Control Flow
Startup enters `tLog`, initializes the IKVS, either verifies an empty disk queue plus writes the format key or calls `restorePersistentState`, then starts shared actors for queue commits, storage spilling, and role tracing. It listens for `InitializeTLogRequest`s, caches duplicate recruitment requests by recruitment ID, and launches `tLogStart`.

`tLogStart` creates a `TLogInterface`, stops older active logs, builds `LogData`, persists initial metadata, optionally pulls recovery data from older log systems, sends recovery-finished/track-recovery handlers, waits until the commit queue has begun processing, replies with the interface, and then delegates to `tLogCore`. `tLogCore` starts endpoint servers, failure handling, metrics tracing, peek tracker cleanup/logging, and log-router pull loops for non-primary logs. Removal or recruitment failure flows through `removeLog`.

Commit flow waits for the requested previous version, applies memory backpressure, appends messages to per-tag structures, writes a queue entry, updates unknown committed version tracking if version-vector unicast is enabled, advances `logData->version`, and waits for `queueCommittedVersion` before replying. `commitQueue` serializes durable queue commits for the one non-stopped active log, while `doQueueCommit` commits `TLogQueue`, advances durable known-committed/version state, publishes log-router pops, and unblocks any old logs that missed their final queue commit.

Peek flow normalizes special tag IDs, enforces streaming sequence order through `peekTracker`, waits for requested versions when safe, reads from persistent spill data and/or in-memory deques, handles popped replies, batches empty peeks, supports streamed replies, and records per-peek latency/size metrics. Pop flow updates per-tag popped versions, handles pseudo localities via the current log system, stores delayed pop requests during snapshot ignore windows, and triggers old-generation recovery bookkeeping.

## State And Persistence Behavior
The durable queue stores framed TLog queue entries with an outer size field, a versioned payload, and a one-byte valid flag. On recovery, incomplete trailing packets are zero-filled and ignored, preserving packet-level atomicity on top of byte-prefix `IDiskQueue` durability.

The IKVS persistent format uses keys for format, protocol version, spill type, recovery count, current version, known committed version, recovery location, locality, log-router tag count, transaction-state tag count, per-tag spilled message data, per-tag queue reference batches, and per-tag popped versions. `updatePersistentData` spills messages by value for selected tags and by reference for most mutation tags, commits the IKVS, then erases durable in-memory data and updates byte accounting. `popDiskQueue` computes the earliest still-needed queue location from reference-spilled tags and queue committed location and calls `TLogQueue::pop`.

Restoration reads persistent metadata, reconstructs stopped `LogData` objects, restores persisted popped tags, replays queue entries from the recovery location into memory, periodically spills during large queue recovery, starts old-log serving actors, and re-registers with the cluster controller. Shutdown disposes persistent data/queue only for permanent worker removal or recruitment failure; otherwise it closes them.

## Dependencies And Integration Points
This file integrates with Flow actors, `TLogInterface`, `LogSystem` and `LogSystemConsumer`, `IDiskQueue`, `IKeyValueStore`, `ServerDBInfo`, cluster-controller rejoin RPCs, role tracing, transaction debug tracing, simulation policy hooks, failure monitoring, histograms/counters, and knobs from `SERVER_KNOBS`. It is built around FoundationDB actor semantics and priority scheduling.

## Risks And Edge Cases
Major risk areas are durability ordering between in-memory version state, disk queue commits, and IKVS spill commits; recovery correctness across partial queue commits; memory accounting and hard-limit backpressure; old generation retention and popped-version tracking; concurrent recruitment/stop/removal races; stream peek sequence obsolescence; log-router pseudo-locality mapping; and low-disk recovery failure behavior. The reference-spill path depends on accurate `versionLocation` data and queue locations. Several comments flag known complexity, including O(n) tag scans, queue forget cost, and spill behavior for inactive shared TLogs.

## Test Signals
The file includes a unit test for `VERSION_MESSAGES_OVERHEAD_FACTOR` using a counting deque allocator. Additional direct signals come from `TestTLogServer.cpp`, which drives commit, peek, pop, and recovery-generation flows through `tLog`. Many simulation-only paths use `buggify`, `CODE_PROBE`, and simulation policy gates to exercise partial commits, slow recovery, old generation GC blocking, and queue-recovery memory pressure.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tlog/TLogServer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tlog/TestTLogServer.cpp -->
# sources/storage-engines/foundationdb/fdbserver/tlog/TestTLogServer.cpp

## Purpose
`TestTLogServer.cpp` is a local actor-based test harness for creating in-process TLog actors, pushing synthetic commits through a `LogSystem`, peeking and popping committed data, and optionally creating a second TLog generation to validate recovery from old logs.

## Important APIs, Types, And Functions
Helper functions build old-log configuration, storage filenames, and `InitializeTLogRequest`s. `TempStorageFiles` and `StorageResources` manage temporary disk queue and KV store files. `setupPersistentStorage` opens the `IDiskQueue` and memory KV store used by each TLog. `initTLogTestContext` constructs `TLogTestContext` and optionally seeds it from an old generation. Main actors are `getTLogCreateActor`, `TLogTestContext::sendPushMessages`, `TLogTestContext::peekCommitMessages`, `buildTLogSet`, and `startTestsTLogRecoveryActors`.

## Control Flow
The test creates one or more `TLogContext` objects and starts real `::tLog` actors with a `PromiseStream<InitializeTLogRequest>`. After each actor replies with a `TLogInterface`, `buildTLogSet` installs those interfaces into `ServerDBInfo.logSystemConfig` and releases the push actors. `sendPushMessages` builds deterministic set-value mutations, maps tags to log server IDs according to replica/team layout, records expected versions in `commitHistory`, and calls `LogSystem::push`. `peekCommitMessages` peeks each expected version from the selected TLog/tag, decodes the version header and mutation payload, validates key/value data, then sends a pop.

When recovery is enabled, the harness locks old TLogs, builds epoch-two contexts, constructs recovery `InitializeTLogRequest`s with `recoverFrom`, `recoverTags`, `startVersion`, `recoverAt`, and old IDs, then validates the recovered generation through the same peek/pop path.

## State And Persistence Behavior
The test uses real disk queue and KV store implementations with per-TLog filenames derived from TLog ID and epoch. `TempStorageFiles` deletes queue/KV segment files at scope end or after actor shutdown. The expected data model is held in `commitHistory`, keyed by `(tagID, logID)`.

## Dependencies And Integration Points
The file depends on TLog server construction, `LogSystemFactory`, `ServerDBInfo`, Flow transport, mutation serialization, `IDiskQueue`, memory KV store, locality and replication policy types, and unit-test assertions. It exercises the production `tLog` actor rather than a mock.

## Risks And Test Signals
The active `TEST_CASE` definitions are commented out, so the harness may not currently run in normal unit-test discovery. It also assumes specific message serialization order, write tracing branches, and a default replica/team mapping. Still, it is a strong integration signal for TLog commit/peek/pop/recovery because it validates data through the same RPC interfaces used by storage servers and recovery consumers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tlog/TestTLogServer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tlog/TestTLogServer.h -->
# sources/storage-engines/foundationdb/fdbserver/tlog/TestTLogServer.h

## Purpose
`TestTLogServer.h` declares the state containers and options used by the TLog server test harness. It keeps test configuration, per-log handles, synchronization promises, and expected commit history in one place.

## Important APIs, Types, And Functions
`TestTLogOptions` reads `UnitTestParameters` for disk queue base/extension, KV store filename/extension, data folder, KV memory limit, tag/log/commit counts, initial version, recovery flag, and replica count. `TLogContext` stores one test TLog's `UID`, `TLogInterface`, optional mock router interface, initialize stream, storage pointers, process/tag ID, and promises indicating created/started/completed states. `TLogTestContext` stores group-wide options, log contexts, expected commit history, `LogSystem`, `ServerDBInfo`, locality values, epoch, and helper methods forwarding to static actor implementations.

## Control Flow
The header only declares state and method entry points. The `.cpp` file fills `TLogTestContext`, starts actors, pushes messages, and peeks/pops data. Promises in `TLogContext` coordinate actor readiness and shutdown.

## State And Persistence Behavior
Persistent state is not managed directly here, but `TLogContext` owns raw pointers to the per-test `IKeyValueStore` and `IDiskQueue` created in the `.cpp`. `TLogTestContext::commitHistory` is the in-memory oracle for recovery and peek validation.

## Dependencies And Integration Points
The header includes FDB types, disk queue and KV store interfaces, log system interfaces, resolver/TLog interfaces, storage server interface, and Flow primitives. These declarations bind the test harness to real production TLog and log-system APIs.

## Risks And Test Signals
There is a signature mismatch risk to watch: the member wrapper names and static declarations must stay aligned with the `.cpp` definitions. Because it exposes raw storage pointers, lifetime is controlled externally by actor shutdown and cleanup helpers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tlog/TestTLogServer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tlog/include/fdbserver/tlog/TLogServer.h -->
# sources/storage-engines/foundationdb/fdbserver/tlog/include/fdbserver/tlog/TLogServer.h

## Purpose
This header is the public declaration for the transaction log server actor used by worker startup and tests. It intentionally exposes a small surface: disk-space threshold helper, the `tLog` actor factory, and a `TLogFn` function-pointer alias.

## Important APIs, Types, And Functions
`effectiveTLogMinAvailableSpaceRatio()` returns the runtime minimum available-space ratio for TLog recovery writes, with simulation-specific behavior implemented in the `.cpp`. `tLog(...)` accepts persistent KV and queue storage, database info, locality, initialization request stream, TLog/worker IDs, restore flag, old/recovered promises, data folder, degraded and low-disk state variables, active shared TLog tracking, and the health-check toggle. `using TLogFn = decltype(&tLog);` enables dependency injection or typed references to the actor.

## Control Flow
Callers create or pass persistent stores, then call `tLog`. The actor initializes storage, optionally restores from disk, handles future recruitment requests from `tlogRequests`, and completes or errors the supplied promises.

## State And Persistence Behavior
The header does not define state. Its signature makes persistence explicit through `IKeyValueStore*`, `IDiskQueue*`, `restoreFromDisk`, folder naming, and shared state references for recovery/degradation.

## Dependencies And Integration Points
It includes `TLogInterface` and Flow primitives and forward-declares storage and server-info types. Worker code, tests, and TLog recruitment paths consume this API.

## Risks And Test Signals
The broad parameter list is a stability contract: changes ripple into worker startup and tests. The raw storage pointers imply ownership and close/dispose behavior must remain clear in the implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tlog/include/fdbserver/tlog/TLogServer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbserver/worker/CMakeLists.txt

## Purpose
This CMake file defines the `fdbserver_worker` static library, its link smoke test, its unit-test target, include directories, and library dependencies.

## Important APIs, Types, And Functions
`fdb_find_sources(FDBSERVER_WORKER_SRCS)` discovers worker sources. `add_flow_target(STATIC_LIBRARY NAME fdbserver_worker ...)` creates the library. `add_fdbserver_link_test` builds a worker link-test target against the worker library and many fdbserver role libraries. `add_fdbserver_unit_test(fdbserver_worker_test worker ...)` defines the worker test executable. `configure_fdbserver_common_includes`, `target_include_directories`, and `target_link_libraries` configure compilation and linkage.

## Control Flow
CMake first discovers sources, creates the library, creates test/link targets, installs common include configuration, adds public and private include roots, and finally declares public/private link dependencies.

## State And Persistence Behavior
There is no runtime state or persistence. Build-system state is the set of source files, include paths, and dependency graph.

## Dependencies And Integration Points
The worker library publicly links `fdbctl` and privately links backup worker, cluster controller, commit proxy, consistency scan, coordinator, data distributor, GRV proxy, log router, log system, ratekeeper, resolver, sequencer, storage server, tester, tlog, and core libraries. The public include directory is `worker/include`; private includes include source and generated include trees.

## Risks And Test Signals
Because worker code references many roles, the link test helps catch missing symbols across role libraries. Dependency drift here can break actor-generated headers, role integrations, or worker unit-test linkage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/MetricClient.cpp -->
# sources/storage-engines/foundationdb/fdbserver/worker/MetricClient.cpp

## Purpose
`MetricClient.cpp` implements `UDPMetricClient`, the process-local UDP emitter for FoundationDB metrics. It supports both OTLP msgpack emission and StatsD line emission depending on `FLOW_KNOBS->METRICS_DATA_MODEL`.

## Important APIs, Types, And Functions
The constructor chooses metric model, target address, and target port from knobs, allocates a reusable `MsgpackBuffer`, parses the destination address, and creates a UDP socket. `send_packet` wraps nonblocking `::send` on non-Windows platforms. `send(MetricCollection*)` serializes and emits metric sums, histograms, gauges, or StatsD messages.

## Control Flow
`send` returns early until the UDP socket future is ready and a native handle exists. For OTLP, it batches sums under a conservative packet-size cap, emits histograms one per packet, and emits gauges as a group, clearing each source map after emission. For StatsD, it concatenates newline-delimited messages up to `IUDPSocket::MAX_PACKET_SIZE` and sends the accumulated string.

## State And Persistence Behavior
The client has no durable state. It mutates the supplied `MetricCollection` by moving metric objects into temporary vectors and clearing maps/messages after attempted send. The reusable msgpack buffer is reset after packet emission.

## Dependencies And Integration Points
It depends on Flow network abstractions, UDP sockets, knobs, OTEL serialization helpers, TD metrics, Msgpack, trace events, and platform socket headers. It is driven by `runMetrics()` in `MetricLogger.actor.cpp`.

## Risks And Test Signals
Packet sizing and mutation semantics are the main risks. OTLP sums are moved out of maps before clear; histograms are sent individually because they can be large. The StatsD overflow branch currently calls `send_packet(socket_fd, buf.buffer.get(), buf.data_size)` instead of sending the accumulated `messages`, which is a potential bug if a packet fills before the final flush. Error handling records `errno` trace events for OTLP sends but does not retry or check return codes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/MetricClient.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/MetricClient.h -->
# sources/storage-engines/foundationdb/fdbserver/worker/MetricClient.h

## Purpose
`MetricClient.h` declares the abstract metric emission interface and the UDP implementation used by worker metric logging.

## Important APIs, Types, And Functions
`IMetricClient` stores a `MetricsDataModel` and declares virtual `send(MetricCollection*)`. `UDPMetricClient` owns a UDP socket future, native socket fd, msgpack buffer, destination address/port, and private `send_packet`. It exposes a constructor and `send` override. `MAX_OTELSUM_PACKET_SIZE` is set to 75 percent of UDP max packet size to avoid oversize OTLP sum batches.

## Control Flow
The header defines no behavior beyond virtual dispatch. Construction and emission behavior live in `MetricClient.cpp`.

## State And Persistence Behavior
There is no persistence. State is process-local and reused across metric emission intervals.

## Dependencies And Integration Points
The header includes UDP socket, Msgpack, TDMetric, and Flow network types. `MetricLogger.actor.cpp` instantiates `UDPMetricClient` from `runMetrics()`.

## Risks And Test Signals
The base and derived classes both contain a `model` member, which can be confusing because the derived member shadows the protected base member. Packet sizing constants and socket lifetime must stay aligned with Flow network behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/MetricClient.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/MetricLogger.actor.cpp -->
# sources/storage-engines/foundationdb/fdbserver/worker/MetricLogger.actor.cpp

## Purpose
`MetricLogger.actor.cpp` implements two metric pipelines. `runMetrics(Future<Database>, Key)` persists TDMetric data and metric registration/rules into a FoundationDB database prefix. The parameterless `runMetrics()` periodically emits process metrics over UDP using `UDPMetricClient`, with a simulation UDP server for validation.

## Important APIs, Types, And Functions
`MetricsRule` represents a DB-backed rule with substring pattern fields for name, type, address, and ID plus enable/min-level settings. `MetricsConfig` builds system-key subspaces/maps for rules, enum maps, and change keys. `metricRuleUpdater` reads DB rules and applies them to registered TD metrics. `MetricDB` implements `IMetricDB::getLastBlock` for metric callbacks. `dumpMetrics` flushes metric batches, runs callbacks, and writes inserts/appends/updates. `updateMetricRegistration` registers metric field keys and enum keys. `runMetrics(fcx, prefix)` orchestrates DB-backed TD metric logging. `startMetricsSimulationServer` receives and validates UDP metrics in simulation. `runMetrics()` emits UDP metrics at `FLOW_KNOBS->METRICS_EMISSION_INTERVAL`. The `TraceEvents` unit test writes synthetic trace events and TDMetric handles to an external metrics database.

## Control Flow
The DB-backed path waits until `TDMetricCollection` exists and initializes, constructs config, waits for the database future, then races rule update, dump, and registration actors. Any non-cancellation error disables all metrics and rethrows.

`metricRuleUpdater` repeatedly reads all rules under system-key access, disables every metric, applies rules in reverse order so later rules win, watches the rule-change key, commits, and waits for either rule changes or new metrics. `dumpMetrics` flushes each metric into a `MetricBatch`, invokes callbacks with retry-on-error, commits batch mutations, and waits based on roll times or metric-enabled triggers. `updateMetricRegistration` writes missing field and enum keys, then waits for registration changes or new metrics.

The UDP path returns immediately if metric model is `NONE`, optionally starts a simulated UDP server, then loops: fetch global `MetricCollection`, call `UDPMetricClient::send`, and sleep for the emission interval.

## State And Persistence Behavior
DB-backed metrics persist under the caller-supplied prefix using key-backed rule, address, name/type, field, enum, and block keys. Transactions use `ACCESS_SYSTEM_KEYS`. Runtime state lives in `TDMetricCollection`, `MetricCollection`, registered flags, roll-time queues, and metric enabled/config flags. UDP metrics are not durable.

## Dependencies And Integration Points
The file integrates with FoundationDB database APIs, ReadYourWrites transactions, KeyBackedTypes, TDMetric and OTEL metrics, Flow actor compiler, UDP sockets, Msgpack, knobs, unit tests, and the `UDPMetricClient`. External environment variables `METRICS_CONNFILE` and `METRICS_PREFIX` drive the trace-event metrics test.

## Risks And Test Signals
Rule matching is simple substring matching and full rescans may become expensive with many metrics/rules. Transaction retries in dump callbacks must be idempotent. The simulation server switch lacks `break` statements, so `STATSD` falls through to the OTLP port assignment; that is a potential correctness issue for StatsD validation. The `/fdbserver/metrics/TraceEvents` test is manual/environment-driven and writes a large synthetic stream for plotting/inspection.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/MetricLogger.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/MetricLogger.actor.h -->
# sources/storage-engines/foundationdb/fdbserver/worker/MetricLogger.actor.h

## Purpose
This actor header declares the worker metric logging entry points and handles actor-compiler include conventions.

## Important APIs, Types, And Functions
It declares `ACTOR Future<Void> runMetrics(Future<Database> fcx, Key metricsPrefix);` for DB-backed TDMetric persistence and `ACTOR Future<Void> runMetrics();` for UDP process metric emission. It forward-declares `Database` and includes FDB/Flow types.

## Control Flow
No behavior is implemented here. Consumers include the header, and actor-generated code is included under the `NO_INTELLISENSE`/include guard pattern.

## State And Persistence Behavior
The header has no state. Persistence semantics are defined by the DB-backed overload in the `.cpp`.

## Dependencies And Integration Points
It depends on actorcompiler/unactorcompiler conventions and is consumed by worker startup code that launches metric logging.

## Risks And Test Signals
The main risk is actor-compiler include ordering; the `flow/actorcompiler.h` include must remain last before actor declarations and `flow/unactorcompiler.h` must close the block.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/MetricLogger.actor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/RoleLineage.cpp -->
# sources/storage-engines/foundationdb/fdbserver/worker/RoleLineage.cpp

## Purpose
`RoleLineage.cpp` provides the out-of-class definition for the static lineage property name used by `RoleLineage`.

## Important APIs, Types, And Functions
It defines `std::string_view RoleLineage::name = "RoleLineage"sv;`, enabling `LineageProperties<RoleLineage>` to identify the property set by name.

## Control Flow
There is no runtime control flow beyond static initialization.

## State And Persistence Behavior
The only state is a static string view; there is no persistence.

## Dependencies And Integration Points
It includes `RoleLineage.h` and uses `std::literals`. The definition is required by any translation unit that uses the `RoleLineage::name` static member.

## Risks And Test Signals
Risk is low. Missing this definition would produce link errors for lineage profiling users.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/RoleLineage.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/RoleLineage.h -->
# sources/storage-engines/foundationdb/fdbserver/worker/RoleLineage.h

## Purpose
`RoleLineage.h` defines actor-lineage metadata for FoundationDB worker roles, allowing lineage profiling to record and collect a process role abbreviation.

## Important APIs, Types, And Functions
`RoleLineage` derives from `LineageProperties<RoleLineage>`, declares static `name`, and stores `ProcessClass::ClusterRole role`, defaulting to `NoRole`. Its `isSet` helper treats any role other than `NoRole` as present. `RoleLineageCollector` derives from `IALPCollector<RoleLineage>` and returns the role abbreviation from `Role::get(...)` when present.

## Control Flow
Collectors call `collect(ActorLineage*)`, retrieve the nearest lineage role property, and return either an `std::any` containing the abbreviation or an empty optional.

## State And Persistence Behavior
State is in-memory actor-lineage metadata only. It is intended for profiling/diagnostic collection, not persistence.

## Dependencies And Integration Points
The header integrates `ActorLineageProfiler` with worker role definitions from `WorkerInterface.actor.h`. It maps internal `ProcessClass::ClusterRole` values to user-facing `Role` abbreviations.

## Risks And Test Signals
The collector assumes `Role::get` supports every collected cluster role. Roles left as `NoRole` are intentionally omitted. Coverage is likely through actor-lineage profiling rather than direct unit tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/RoleLineage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/include/fdbserver/worker/Worker.h -->
# sources/storage-engines/foundationdb/fdbserver/worker/include/fdbserver/worker/Worker.h

## Purpose
`Worker.h` declares the top-level worker process entry point and profiling registration hook for fdbserver worker code.

## Important APIs, Types, And Functions
`Future<Void> fdbd(...)` is the main worker actor entry point. It receives the cluster connection record, locality, process class, data/tlog/coord folders, memory limit, metrics connection/prefix, memory profiling threshold, binary whitelist paths, and consistency-check urgent-mode flag. `registerThreadForProfiling()` registers the current thread with profiling infrastructure.

## Control Flow
The header only declares functions. The implementation is responsible for launching worker roles, metrics, coordination, storage, TLog spill folders, and consistency-check behavior.

## State And Persistence Behavior
The function signature exposes persistent and runtime configuration: data folder, TLog spill folder, coordination folder, metrics database information, and memory limits. No state is defined in the header.

## Dependencies And Integration Points
It depends on client cluster connection records, coordination interface, FDB types, locality data, process class, and Flow futures. It is the public include used by process startup.

## Risks And Test Signals
Because `fdbd` is broad and process-level, signature changes have high integration cost. Tests are likely indirect through worker startup/link tests rather than this header itself.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/worker/include/fdbserver/worker/Worker.h -->
