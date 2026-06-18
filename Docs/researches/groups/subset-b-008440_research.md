# Research Report: subset-b-008440

This grouped report covers the FoundationDB fdbclient files assigned to work item `subset-b-008440`. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/StatusClient.cpp -->
# sources/storage-engines/foundationdb/fdbclient/StatusClient.cpp

## Purpose
`StatusClient.cpp` implements client-side status collection and JSON status document merging for FoundationDB. It has two major responsibilities: strict parsing/merging/cleanup of JSON status fragments through `JSONDoc`, and asynchronous status fetching from coordinators plus the cluster controller through `StatusClient::statusFetcher`.

## Important APIs, types, and functions
`readJSONStrictly()` parses a complete JSON string with `json_spirit`, allowing only trailing whitespace and throwing `json_malformed` or `json_eof_expected` on malformed input. `JSONDoc::mergeValueInto()`, `mergeInto()`, `cleanOps()`, and `mergeOperator` specializations implement status-document operators such as `$and`, `$or`, `$count_keys`, `$latest`, `$last`, and `$expires`. `clientCoordinatorsStatusFetcher()` probes coordinator leader and protocol endpoints and reports quorum reachability. `clientStatusFetcher()` builds the client section, including cluster-file freshness. `clusterStatusFetcher()` requests the selected status field from the cluster controller. `getClientDatabaseStatus()` derives `healthy` and `available` booleans from client and cluster status JSON. `statusFetcherImpl()` orchestrates deadlines and merges client/cluster output. `timeoutMonitorLeader()` keeps `monitorLeader` active only while status is being requested. `StatusClient::statusFetcher()` is the public entry point.

## Control flow
Status collection first computes a deadline using `CLIENT_KNOBS->STATUS_TIMEOUT`, probes coordinators, and checks whether the cluster file is current. If quorum is reachable, it waits briefly for `db->statusClusterInterface` to be populated by `monitorLeader`, then asks `databaseStatus` on the cluster controller. Messages are accumulated instead of generally throwing so partially complete status is still returned. Once cluster data is present, coordinator fault tolerance is folded into the cluster fault tolerance section. The final document always gets `client.messages`, `client.database_status`, and a default `cluster.layers._valid` field.

## State and persistence behavior
This file does not persist database keys directly. It reads cluster connection state from `IClusterConnectionRecord` and caches status leader monitoring state in `DatabaseContext` fields `statusClusterInterface`, `statusLeaderMon`, and `lastStatusFetch`. `JSONDoc::expires_reference_version` is a process-static version threshold used when resolving `$expires` operators.

## Dependencies and integration points
It integrates with `CoordinationInterface`, `MonitorLeader`, `ClusterInterface`, `Status`, generic RPC retry helpers, `json_spirit`, Flow coroutines, and client knobs. The status output feeds CLI and management status consumers, and its message types must stay consistent with `fdbclient/Status.h`.

## Risks and edge cases
JSON merging is type-sensitive: mismatched scalar values or operators produce embedded `ERROR` objects rather than exceptions. `$expires` behavior depends on `expires_reference_version`, and a missing or zero version is treated as unexpired. Coordinator probing races a quorum wait against timeout delay; partial readiness can produce incomplete but valid status. Health derivation is intentionally conservative and catches JSON access exceptions by leaving availability or health false. The idle monitor resets the cached cluster interface after `STATUS_IDLE_TIMEOUT`, so callers must tolerate re-monitoring cost after idle periods.

## Test signals
There are no local `TEST_CASE`s in this file. Useful test signals are simulation malformed JSON checks, status command tests with unavailable coordinators or cluster controller, cluster-file mismatch tests, JSON operator merge tests, and status timeout behavior. Trace events `ClientStatusFetchError` and `ClusterStatusFetchError` are operational diagnostics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/StatusClient.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/StorageCheckpoint.cpp -->
# sources/storage-engines/foundationdb/fdbclient/StorageCheckpoint.cpp

## Purpose
`StorageCheckpoint.cpp` implements serialization accessors for `CheckpointMetaData::serializedCheckpoint`. In production it is a pass-through. In simulation it pads checkpoint payloads to deterministic size buckets so simulation replay remains stable for a fixed seed.

## Important APIs, types, and functions
`CheckpointMetaData::setSerializedCheckpoint()` stores a checkpoint payload. `CheckpointMetaData::getSerializedCheckpoint()` returns the original payload. The anonymous constants `PAYLOAD_ROUND_TO_NEXT` and `FOOTER_BYTE_SIZE` define simulation padding granularity and footer size.

## Control flow
When not running under `g_network->isSimulated()`, setter and getter store and return `serializedCheckpoint` unchanged. In simulation, the setter rounds payload size up to a multiple of 5000 bytes with a minimum target of 5000 bytes, appends `p` padding bytes, and appends a 16-byte ASCII footer containing the padding byte count followed by `f` fill bytes. The getter reads the footer from the final 16 bytes, parses leading decimal digits as the padding byte count, computes the original payload size, and returns a `Standalone<StringRef>` into the stored arena covering only the unpadded prefix.

## State and persistence behavior
The only mutated field is the in-memory `CheckpointMetaData::serializedCheckpoint`; when the metadata is serialized elsewhere, simulation runs may persist the padded internal representation. External consumers using the getter see the original unpadded checkpoint. Production persistence is unaffected.

## Dependencies and integration points
The code depends on `fdbclient/StorageCheckpoint.h`, Flow `StringRef`/arena ownership, and the global network simulation flag. Checkpoint values are encoded and decoded through `SystemData.cpp` helpers using object serialization.

## Risks and edge cases
The footer parser assumes simulation serialized values are at least 16 bytes and contain a decimal padding length at the footer start. Corrupt or manually constructed simulation payloads can assert. The protocol is deliberately internal; bypassing `getSerializedCheckpoint()` exposes padding bytes. Determinism depends on the exact constants and footer format, so changing them can affect simulation compatibility.

## Test signals
The strongest tests are simulation round trips across payload sizes 0, below 5000, exactly 5000, and above 5000, plus production round trips verifying no mutation. Determinism tests should compare serialized byte sizes across repeated simulation runs with the same seed.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/StorageCheckpoint.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/StorageServerInterface.cpp -->
# sources/storage-engines/foundationdb/fdbclient/StorageServerInterface.cpp

## Purpose
`StorageServerInterface.cpp` initializes the endpoint set derived from a storage server's `getValue` endpoint and implements reply comparison/tracing specializations used for testing storage server replicas and TSS shadow reads.

## Important APIs, types, and functions
`StorageServerInterface::initEndpointsFromGetValue()` derives all request streams from adjusted endpoint tokens. `initEndpoints()` registers all streams with `FlowTransport`. `traceChecksumValue()` formats small values directly and large values as size plus CRC32C checksum. Template specializations of `TSS_doCompare`, `LB_mismatchTraceName`, and `TSS_traceMismatch` cover `GetValue`, `GetKey`, `GetKeyValues`, `GetMappedKeyValues`, `GetKeyValuesStream`, watch and metric-style requests. `TSSMetrics::recordLatency()` specializations record latency for read operations.

## Control flow
Endpoint initialization starts from `getValue` and assigns fixed adjusted endpoint offsets for point reads, range reads, mapped reads, watches, metrics, change feeds, checkpointing, audit, checksum, bulk dump, and other storage server requests. Comparison flow is type-specific: point reads compare optional values; range reads compare `more` plus returned data; mapped/streaming reads follow similar summary behavior; key-selector reads apply special tolerance for incomplete selectors caused by shard boundary movement. Mismatch tracing emits request selectors, versions, summarized reply sizes, first differing key/value, and checksums instead of potentially huge values.

## State and persistence behavior
This file does not persist data. It mutates request stream members during endpoint initialization and records in-memory latency metrics through `TSSMetrics`. Trace output is persisted only through the normal tracing/logging subsystem.

## Dependencies and integration points
It depends on `StorageServerInterface.h`, Flow transport endpoint registration, `crc32c`, request/reply types declared in the storage server interface header, and the load-balancing/TSS comparison templates. The file is central to clients, storage servers, TSS validation, replica reads, checkpoint fetches, and audit/bulk-dump requests because endpoint offsets must match across serialization and process boundaries.

## Risks and edge cases
Endpoint offset order is a wire contract; adding or reordering streams without matching all serializers/deserializers can break RPC compatibility. `GetKeyReply` comparison is intentionally permissive around shard boundaries and may defer detection to other read paths or consistency checks. Some request types return `true` and assert if traced because they are duplicated only for load or are not expected to be compared. Trace value checksumming avoids log blowups but can hide exact large value contents.

## Test signals
The local `TEST_CASE("/StorageServerInterface/TSSCompare/TestComparison")` exercises point reads, range reads, key-selector boundary tolerance, and checksum formatting. Additional useful tests include endpoint serialization compatibility, mismatch trace field coverage, replica comparison for mapped/streaming reads, and latency metric recording for all compared read types.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/StorageServerInterface.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/Subspace.cpp -->
# sources/storage-engines/foundationdb/fdbclient/Subspace.cpp

## Purpose
`Subspace.cpp` implements the client-side `Subspace` helper, which models a raw key prefix plus tuple suffix packing. It is a small abstraction used throughout fdbclient code to build structured keyspaces.

## Important APIs, types, and functions
Constructors accept a `Tuple` plus raw prefix as `StringRef` or `Standalone<VectorRef<uint8_t>>`, or a raw prefix alone. `key()` returns the raw prefix as a `Key`. `pack()` returns `tuple.pack()` with the raw prefix. `unpack()` validates containment and decodes the suffix as a `Tuple`. `range()` creates the half-open range for all keys under the subspace plus optional tuple suffix. `contains()` checks prefix membership. `subspace()` and `get()` derive nested subspaces.

## Control flow
Construction appends the raw prefix and packed tuple bytes into the object's arena-backed `rawPrefix`. `pack()` delegates ordering semantics to `Tuple::pack()` and prefixes the result. `range()` constructs begin and end keys by appending the tuple encoding and then `0x00` or `0xff`, respectively. `unpack()` rejects keys outside the subspace by throwing `key_not_in_subspace`.

## State and persistence behavior
`Subspace` only stores an arena-backed prefix. It does not read or write the database by itself, but callers persist keys generated by it. Because the packed tuple encoding is part of the persisted key layout, changes to tuple encoding or prefix composition are compatibility-sensitive.

## Dependencies and integration points
It depends on `fdbclient/Subspace.h`, `Tuple`, Flow arena-backed key types, and `KeyRange`. `TaskBucket`, system metadata helpers, and many higher-level APIs use this helper for structured key construction.

## Risks and edge cases
`range()` assumes the `prefix + tuple + 0x00` to `prefix + tuple + 0xff` convention is the intended tuple subspace range. `contains()` is a raw prefix check and does not validate tuple boundaries. Repeated calls to `tuple.pack()` in constructors can incur extra work, though behavior is straightforward. `unpack()` throws for keys outside the prefix, so callers need to handle this when scanning broader ranges.

## Test signals
There are no local tests in this file. Useful coverage includes constructor equivalence for raw-prefix overloads, nested subspace composition, `pack`/`unpack` round trips, `range()` boundaries, and negative containment tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/Subspace.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/SystemData.cpp -->
# sources/storage-engines/foundationdb/fdbclient/SystemData.cpp

## Purpose
`SystemData.cpp` defines FoundationDB's system key constants and the encoding/decoding helpers for metadata stored in those keyspaces. It is a compatibility-critical registry for shard ownership, storage server metadata, server tags, audit/checkpoint/data-move state, process and worker records, backup/restore metadata, bulk load/dump, range locks, throttling keys, global configuration keys, and transaction/system markers.

## Important APIs, types, and functions
Global `KeyRef` and `KeyRangeRef` constants define normal, system, special, metadata, configuration, backup, audit, tag, server, bulk, and lock keyspaces. Helper families include `keyServersKey()`, `keyServersValue()`, `decodeKeyServersValue()`, audit key/value helpers, checkpoint and data-move helpers, log value helpers, server key helpers, `newDataMoveId()` and `decodeDataMoveId()`, TSS quarantine helpers, server tag helpers, datacenter/tLog helpers, server list and software version serialization, process/worker/backup helpers, log range helpers, construct value helpers, and healthy-zone helpers. `SystemKey::SystemKey()` checks prefix conflicts in simulation.

## Control flow
Most functions are deterministic encoders or decoders around `BinaryWriter`, `BinaryReader`, `ObjectWriter`, and `ObjectReader`. Compatibility branches inspect serialized protocol versions to support older `keyServersValue`, shard metadata IDs, and tag-encoded layouts. Decoders usually clear output vectors, parse values, map tags back to UIDs using either a `RangeResult` or a `std::map<Tag, UID>`, sort server IDs, and assert or trace when required mappings are missing. Data-move IDs encode data-move type and reason in low bits of the UID second half while preserving special values for anonymous, empty, and unassigned shards.

## State and persistence behavior
This file is almost entirely about persisted state. The constants are database key contracts. Values encode protocol-versioned binary or object-serialized data for cluster metadata. Mutating these formats can affect upgrades, downgrades, recovery, data distribution, backup/restore, bulk operations, and storage server recruitment. The simulation-only `SystemKey` known-key set tracks prefix conflicts in process memory to catch accidental overlapping system key definitions.

## Dependencies and integration points
Dependencies include `KeyBackedTypes`, `SystemData.h`, `FDBTypes`, `StorageServerInterface`, Flow arenas/serialization/unit tests, and protocol-version feature flags. Integration points span data distribution, storage servers, coordinators, backup agents, audit, TSS, bulk load/dump, global configuration, metrics, and client management APIs.

## Risks and edge cases
This file has high upgrade risk because key names, ranges, and binary layouts are durable contracts. Prefix overlap can route scans incorrectly; simulation catches only keys constructed through `SystemKey`. Version-specific decoding paths must preserve behavior for legacy values. Tag-to-UID decoding can assert when a tag map is incomplete. `decodeDataMoveId()` tolerates out-of-scope type/reason values with warnings for upgrade compatibility, but this can affect fetch throttling or physical shard move choices. Several encode functions use string forms, big-endian values, or object serializers, so byte-order and protocol flags are part of the contract.

## Test signals
Local tests cover storage server interface serialization, key server value compatibility, and data move ID encoding/decoding. Additional signals should include upgrade/downgrade fixture tests for all protocol-versioned value formats, prefix-range overlap checks, tag mapping failure tests, and end-to-end tests through data distribution, backup/restore, audit, bulk load/dump, and TSS quarantine flows.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/SystemData.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/TagThrottle.cpp -->
# sources/storage-engines/foundationdb/fdbclient/TagThrottle.cpp

## Purpose
`TagThrottle.cpp` implements transaction tag set handling and the persistent key encoding for tag throttles. It supports client validation limits, readable tag messages, key serialization for throttle records, and value decoding.

## Important APIs, types, and functions
`ClientTagThrottleLimits::NO_EXPIRATION` is the sentinel expiration time. `TagSet::addTag()` validates and deduplicates transaction tags. `TagSet::size()` and `TagSet::toString()` expose tag count and user-facing descriptions. `TagThrottleKey::toKey()` serializes throttle type, priority, and tag list under `tagThrottleKeysPrefix`. `TagThrottleKey::fromKey()` reverses that format. `TagThrottleValue::fromValue()` decodes the value with the protocol version that includes throttle reason.

## Control flow
Adding a tag enforces knob limits for maximum tag length and maximum tags per transaction, copies the tag into the set arena, and increments byte accounting only for new tags. Key encoding writes the system prefix, one byte for throttle type, one byte for priority, then each tag as one length byte plus tag bytes. The current implementation asserts exactly one tag per throttle even though the wire format has a tag-list shape.

## State and persistence behavior
Throttle records are persisted under the system throttled-tags keyspace declared in `SystemData.cpp`. The encoded key is part of the durable API used to view or control tag throttling. `TagSet` itself is in-memory arena state attached to requests or throttle operations.

## Dependencies and integration points
It depends on `SystemData.h` for key prefixes, `TagThrottle.h` for tag/throttle types, `CLIENT_KNOBS` for validation limits, and Flow binary serialization for values. It integrates with transaction tagging, manual or automatic throttling management, and system-key clients that scan throttled tag records.

## Risks and edge cases
The length and count fields are single bytes, so knob assertions require both limits to remain below 256. `TagSet::toString()` asserts non-empty. The key format claims sorted tags but `TagSet` only deduplicates insertion order in this file; callers must not rely on multi-tag support because `toKey()` asserts `tags.size() == 1`. Malformed throttle keys can be decoded without explicit bounds checks beyond normal memory assumptions.

## Test signals
The local `TEST_CASE("TagSet/toString")` covers singular/plural rendering and capitalization. Additional useful tests are tag limit exceptions, duplicate tag byte accounting, throttle key round trips for automatic/manual types and priorities, malformed key rejection behavior, and value decode compatibility with reason-bearing protocol versions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/TagThrottle.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/TaskBucket.cpp -->
# sources/storage-engines/foundationdb/fdbclient/TaskBucket.cpp

## Purpose
`TaskBucket.cpp` implements a persistent, FoundationDB-backed task queue and future/callback mechanism. It lets tasks be enqueued, claimed, run by registered task functions, timeout-extended, requeued after timeout, finished, paused, and chained through `TaskFuture` callbacks.

## Important APIs, types, and functions
Registered task functions include `UnblockFutureTaskFunc`, `AddTaskFunc`, and `IdleTaskFunc`. `Task` stores reserved parameter keys and exposes `getDoneFuture()`, `getVersion()`, and `getPriority()`. `TaskBucketImpl` owns most actor logic: `getTaskKey()`, `getOne()`, `taskVerify()`, `finishTaskRun()`, `doTask()`, `dispatch()`, `watchPaused()`, `run()`, `isEmpty()`, `isBusy()`, `isFinished()`, `checkActive()`, `getTaskCount()`, `requeueTimedOutTasks()`, and `extendTimeout()`. Public `TaskBucket` wraps those helpers. `FutureBucket`, `TaskFuture`, and `TaskCompletionKey` implement persistent future state, joins, callbacks, and dependent task enqueueing.

## Control flow
Tasks are stored in an available subspace by priority unless they have a scheduled version, in which case they start in timeout space. `getOne()` optionally requeues timed-out tasks, searches priorities from high to low, randomly samples task IDs to reduce contention, moves the selected task's parameter keys from available space to timeout space, sets a timeout version, and updates an active marker. `doTask()` verifies optional validation keys, runs the registered task function while racing it with repeated timeout extension, then finishes inside a transaction. Dispatch keeps up to `maxConcurrentTasks` running, dynamically batches claims, and respects a pause key watched by `watchPaused()`. Future callbacks either run immediately if the future is set or are persisted under callback subspace until blocks are cleared.

## State and persistence behavior
All task state is persisted under the bucket prefix: available tasks under `av` or `avp`, active marker under `ac`, pause key, timeout records under `to`, and `task_count`. Future state is persisted under the future bucket prefix with block keys under `bl` and callback tasks under `cb`. Claiming, timeout extension, requeue, and finish are transactional transformations across these subspaces.

## Dependencies and integration points
It depends on `TaskBucket.h`, `FDBTypes`, `ReadYourWritesTransaction`, `Subspace`, tuples, Flow actors, `CLIENT_KNOBS`, transaction options, and registered `TaskFuncBase` factories. It is used by higher-level management workflows that need durable asynchronous task orchestration.

## Risks and edge cases
The queue relies on correct subspace layout and atomic task count updates. `requeueTimedOutTasks()` batches by key order and only safely moves complete tasks when range limits are respected; partial batches clear up to the last complete key. Long-running tasks must extend timeouts or they can be requeued and executed again. Validation keys abort stale tasks, but missing validation parameters make tasks invalid. `TaskFuture::performAllActions()` reconstructs callback tasks from key order, so callback subspace layout is critical. Recursive retry and dispatch loops can hide repeated transient errors unless trace counters are monitored.

## Test signals
No local `TEST_CASE`s are in this file, but useful tests include enqueue/claim/finish round trips, priority ordering, scheduled tasks, timeout requeue, timeout extension, pause/resume, task count watch, validation-key cancellation, future set/onSet/onSetAddTask behavior, joined futures, and duplicate execution resistance under injected transaction conflicts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/TaskBucket.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ThreadSafeTransaction.cpp -->
# sources/storage-engines/foundationdb/fdbclient/ThreadSafeTransaction.cpp

## Purpose
`ThreadSafeTransaction.cpp` provides the thread-safe client API facade around `DatabaseContext` and `ReadYourWritesTransaction`. It lets foreign threads use database and transaction operations by copying inputs and scheduling the actual work on the FoundationDB network thread.

## Important APIs, types, and functions
`ThreadSafeDatabase` implements connection creation, `onConnected()`, transaction creation, database options, management operations, client status, shared state, busyness, and protocol queries. `ThreadSafeTransaction` wraps reads, ranges, mapped ranges, conflict ranges, mutations, watches, commit, version vector/span context/cost/versionstamp queries, options, deferred error checks, `onError()`, reset, debug trace, and debug print. `ThreadSafeApi` owns API version selection, client version string, network options/setup/run/stop, database creation, and network-thread completion hooks.

## Control flow
Foreign-thread methods copy `StringRef`, `KeyRef`, `KeyRangeRef`, selectors, and optional values into owning `Key`, `Value`, `Standalone`, or other safe objects, capture raw pointers, and call `onMainThread` or `onMainThreadVoid`. The network-thread lambda checks deferred errors where appropriate and delegates to the underlying `DatabaseContext` or `ReadYourWritesTransaction`. Constructors allocate objects on the calling thread when needed but run actual initialization on the network thread. Destructors defer reference release back to the network thread.

## State and persistence behavior
This file does not define database key layouts, but it can mutate database state through the underlying transaction methods. In-process state includes raw `DatabaseContext*`, raw `ReadYourWritesTransaction*`, an atomic initialization flag for committed-version safety, API version, external transport id, lazily built client version string, and registered network completion hooks.

## Dependencies and integration points
It depends on cluster connection records, `DatabaseContext`, `GenericManagementAPI`, `NativeAPI.actor.h`, Flow arenas/protocol versions, and option metadata. It is a major integration layer for the C API and other clients that call from threads outside the network thread.

## Risks and edge cases
The file explicitly warns that methods must not implicitly `addRef()` because users may share `Reference<ThreadSafe...>` across threads in limited ways. Lifetimes depend on network-thread ordering of deferred addref/delref calls. Returning `invalidVersion` from `getCommittedVersion()` before initialization avoids touching an unconstructed transaction. `clear(begin,end)` checks inverted ranges inside the network-thread lambda. `runNetwork()` captures errors, runs shutdown hooks with isolated error handling, and rethrows the original network error afterward. Completion hooks are protected by a mutex because they must be visible when registration returns.

## Test signals
No local tests are present. Useful tests include foreign-thread get/set/commit, option pass-through, deferred error propagation, destruction while initialization is pending, network shutdown hooks on normal and error termination, external transport id parsing, and invalid option handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ThreadSafeTransaction.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/Tracing.cpp -->
# sources/storage-engines/foundationdb/fdbclient/Tracing.cpp

## Purpose
`Tracing.cpp` implements concrete OpenTelemetry-style span tracing backends for fdbclient/Flow spans. It supports disabled tracing, trace-event logfile emission, and a lossy UDP MessagePack transport, with simulation validation for UDP serialization.

## Important APIs, types, and functions
`NoopTracer`, `LogfileTracer`, `UDPTracer`, and non-Windows `FastUDPTracer` implement `ITracer`. `openTracer()` switches the global tracer. `Span::~Span()` and move assignment emit sampled spans when a span lifetime ends. `simulationStartServer()` runs a UDP listener in simulation to validate packet shape. `fastTraceLogger()` periodically traces UDP sender counters. MessagePack helper methods serialize spans, linked contexts, events, and attributes.

## Control flow
When a sampled `Span` is destroyed or overwritten by move assignment, it records end time with `g_network->now()` and sends the span to `g_tracer`. Logfile tracing emits a primary `TracingSpan` event plus separate events for links, tags, events, and event attributes. UDP tracing serializes a 12-field array including trace ID, span ID, parent ID, location, begin/end, kind, status, links, events, and attributes. `FastUDPTracer::prepare()` lazily starts logging, creates a UDP socket, starts the simulation UDP server when needed, validates literal listener addresses, and records unready/send-failure counters. `write()` sends with `MSG_DONTWAIT` and disables further sends after an error.

## State and persistence behavior
Global `g_tracer` owns the active backend. `FastUDPTracer` maintains a reusable `MsgpackBuffer`, counters, socket future, socket fd, send-error flag, and background actors. Persistence is through trace logs or network-delivered UDP packets; no database keys are touched.

## Dependencies and integration points
The file depends on Flow MessagePack helpers, random/network/socket primitives, knobs, unit tests, UDP sockets, and span types from `Tracing.h`. It integrates with every subsystem that constructs `Span` objects and with trace log consumers or external UDP collectors.

## Risks and edge cases
UDP tracing is lossy by design. Hostnames are rejected because `NetworkAddress::parse()` expects literal IP addresses; invalid listener addresses disable sending with a warning. Serialization vector sizes above supported bounds assert or warn. The global tracer is replaced by `openTracer()` without synchronization visible here, so it should be configured in controlled phases. Move assignment emits the existing sampled span before stealing the new span's arena-backed fields, which is important for avoiding dangling references.

## Test signals
Local tests cover span sampling inheritance, adding events, attributes, links, and FastUDP MessagePack byte layout including long strings. Additional useful tests include invalid listener address handling, send-error backoff, simulation UDP server validation, tracer switching, and logfile field completeness.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/Tracing.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/TransactionLineage.cpp -->
# sources/storage-engines/foundationdb/fdbclient/TransactionLineage.cpp

## Purpose
`TransactionLineage.cpp` provides the translation unit that instantiates the process-local transaction lineage collector declared in `TransactionLineage.h`.

## Important APIs, types, and functions
The file includes `fdbclient/TransactionLineage.h` and defines an anonymous-namespace `TransactionLineageCollector transactionLineageCollector;`.

## Control flow
There is no function-level control flow in this file. Static initialization constructs the collector before normal runtime use, and static destruction occurs at process teardown according to C++ object lifetime rules.

## State and persistence behavior
The collector is process-local state. This file does not persist database keys or serialize values. Any behavior, retention policy, or externally visible API is defined in the header and related implementation, not here.

## Dependencies and integration points
The sole dependency is `TransactionLineage.h`. The anonymous namespace gives the collector internal linkage, so integration likely depends on registration or side effects declared by the collector type.

## Risks and edge cases
Static initialization order can matter if other global objects expect the collector to exist before or after their own initialization. Because the symbol has internal linkage, accidental duplicate collector definitions in other translation units would create independent collectors.

## Test signals
No local tests exist. Useful checks are link-time presence of the translation unit, tests in the lineage subsystem that verify collector side effects, and startup/shutdown tests if collector construction registers global state.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/TransactionLineage.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/Tuple.cpp -->
# sources/storage-engines/foundationdb/fdbclient/Tuple.cpp

## Purpose
`Tuple.cpp` implements FoundationDB tuple packing and unpacking for ordered key encoding. It supports byte strings, UTF-8 strings, signed integers, floats, doubles, booleans, null, 96-bit versionstamps, and restricted user-defined terminal types.

## Important APIs, types, and functions
Constants include `VERSIONSTAMP_96_CODE`, `USER_TYPE_START`, and `USER_TYPE_END`. Helpers `bigEndianFloat()`, `bigEndianDouble()`, `findStringTerminator()`, and `adjustFloatingPoint()` implement sortable encodings. Constructors parse packed data and populate element offsets. Public methods include `unpack()`, `unpackUserType()`, `tupleToString()`, append overloads, `getType()`, typed getters, `range()`, `subTuple()`, and `subTupleRawString()`.

## Control flow
Parsing walks the packed byte string, records each element offset, and advances according to the type code. Byte and UTF-8 strings terminate on `0x00` not followed by escaped `0xff`; integers use type-code-relative byte lengths around `0x14`; floats and doubles have fixed lengths; versionstamps have `VERSIONSTAMP_TUPLE_SIZE`; user types are allowed only when explicitly requested and consume the remaining bytes. Append methods write canonical ordered encodings: strings escape embedded NULs as `00 ff`, integers use minimal big-endian sign-aware lengths, floating point values are endian-swapped then sign-adjusted for lexical order, and null/bool/versionstamp/user types write fixed codes. Getters validate index and type before decoding.

## State and persistence behavior
`Tuple` stores packed bytes and offsets in arena-backed vectors. It does not write the database directly, but packed tuple bytes are widely persisted as keys and subspace suffixes. Encoding changes are therefore persistent format changes.

## Dependencies and integration points
It depends on `Tuple.h`, `TupleVersionstamp`, Flow unit tests, endian helpers, arenas, `KeyRange`, and FoundationDB error types. `Subspace`, `TaskBucket`, and many system key helpers use tuple packing.

## Risks and edge cases
Tuple parsing throws on unknown data types, and user-defined types are rejected unless `unpackUserType()` is used. `exclude_incomplete` can drop incomplete trailing elements, while `getInt(..., allow_incomplete)` has special sort-preserving behavior for truncated integers. Floating-point encoding depends on bit reinterpretation and endian conversion. `getString()` reconstructs escaped strings into a new arena; callers should not expect zero-copy. `range()` uses appended `0x00`/`0xff` bounds and should be used consistently with tuple prefix semantics.

## Test signals
Local tests cover `makeTuple()` equivalence with append chains and `unpackUserType()` behavior, including rejection by normal unpack. Additional coverage should include integer ordering across negative/zero/positive boundaries, embedded NUL strings, float/double ordering including negative values, incomplete tuple parsing, subtuple extraction, range bounds, and versionstamp round trips.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/Tuple.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/TupleVersionstamp.cpp -->
# sources/storage-engines/foundationdb/fdbclient/TupleVersionstamp.cpp

## Purpose
`TupleVersionstamp.cpp` implements the fixed-size tuple versionstamp value used by `Tuple`. A tuple versionstamp contains an 8-byte transaction version, 2-byte batch number, and 2-byte user version in big-endian order.

## Important APIs, types, and functions
Constructors accept either an existing `StringRef` of exactly `VERSIONSTAMP_TUPLE_SIZE` bytes or individual `version`, `batchNumber`, and `userVersion` fields. Accessors include `getVersion()`, `getBatchNumber()`, `getUserVersion()`, `begin()`, `size()`, and equality comparison.

## Control flow
The `StringRef` constructor validates exact size and throws `invalid_versionstamp_size` otherwise. The field constructor allocates a 12-byte string and writes all fields in big-endian form. Accessors read from fixed offsets, convert from big-endian, and return typed values. Equality compares decoded field values rather than raw bytes.

## State and persistence behavior
The object owns a 12-byte `Standalone<StringRef>` value. It does not persist by itself, but `Tuple::append(TupleVersionstamp)` embeds this byte sequence into ordered tuple keys.

## Dependencies and integration points
It depends on `TupleVersionstamp.h`, endian helpers, Flow string ownership, and tuple constants. It integrates directly with `Tuple.cpp` versionstamp append/get behavior and any API that stores versionstamped tuple keys.

## Risks and edge cases
The code uses fixed-offset reinterpret casts, so size validation is essential. Batch and user versions are returned as signed `int16_t` even constructor parameters are `uint16_t`, which can matter for values above `INT16_MAX`. Equality normalizes through decoded values, so it is robust for canonical byte representation but still assumes the 12-byte layout.

## Test signals
Useful tests include constructor size validation, field constructor byte layout, accessor round trips for boundary values, equality comparisons, and integration through `Tuple::append()` and `Tuple::getVersionstamp()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/TupleVersionstamp.cpp -->
