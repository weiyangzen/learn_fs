# subset-b-007988 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/Server.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/Server.java

## Purpose
`Server` is the abstract Hadoop IPC server implementation vendored under Ozone's `org.apache.hadoop.ipc_` namespace. It owns the listening socket, nonblocking accept/read/write loops, per-connection state, SASL negotiation, service authorization, request deserialization, call queue integration, handler execution, response serialization, metrics, slow-RPC accounting, and idle connection cleanup. Subclasses implement the abstract `call(RPC.RpcKind, String, Writable, long)` hook to dispatch decoded RPC payloads to a protocol implementation.

## Important APIs, types, and functions
- Static RPC engine registry: `registerProtocolEngine`, `getRpcRequestWrapper`, and `getRpcInvoker` map an `RPC.RpcKind` to a request wrapper class and invoker. `getProtocolClass` caches protocol classes by name.
- Runtime context APIs: `getCurCall`, `getCallId`, `getRemoteIp`, `getClientId`, `getRemoteAddress`, and `getRemoteUser` expose the current handler-thread RPC context via `ThreadLocal`.
- `Call` implements `Schedulable` and `PrivilegedExceptionAction<Void>`. It carries call id, retry count, client id, caller context, processing details, scheduler priority, optional client state id, and response lifecycle counters.
- `RpcCall` extends `Call` with `Connection`, deserialized `Writable` request, response bytes, and response status/error fields. Its `run` method invokes the abstract server `call`, records processing timing, and schedules response send.
- `Listener` accepts sockets, binds to fixed or ranged ports, fans accepted sockets to `Reader` threads, and starts/stops idle scanning.
- `Listener.Reader` registers accepted channels with a read selector and calls `Connection.readAndProcess`.
- `Responder` owns the write selector and response queues. It writes immediately when possible, registers partial responses for `OP_WRITE`, purges responses that have been pending too long, and SASL-wraps queued responses when negotiated QoP requires it.
- `Connection` holds channel/socket state, connection header and context state, SASL state, auth method, user/proxy user, protocol name, packet buffers, response queue, outstanding RPC count, and remote address details.
- `ConnectionManager` tracks active connections, dropped connections, open connections per user, max connection enforcement, idle close policy, and timer-driven idle scans.
- Lifecycle and inspection APIs include `start`, `stop`, `join`, `getListenerAddress`, `getPort`, `getNumOpenConnections`, `getNumOpenConnectionsPerUser`, `getNumDroppedConnections`, `getCallQueueLen`, and `getServerName`.

## Control flow
Construction configures queue classes and scheduler classes from `ipc.<port>.*`, builds supported auth methods, binds `Listener`, creates metrics, initializes SASL helpers when security or tokens are enabled, and creates the `Responder`. `start` starts responder, listener, and handler threads.

Connection setup starts with `Listener.doAccept`, which configures nonblocking TCP, registers a `Connection` with `ConnectionManager`, and assigns it to a reader. `Connection.readAndProcess` first reads the Hadoop RPC magic header, validates IPC version and auth protocol, detects accidental HTTP GETs, then reads framed RPC packets. Negative call ids route to out-of-band handling: SASL negotiation, connection context, and ping. Nonnegative call ids require an authorized connection context, then flow through `processRpcRequest`.

`processRpcRequest` rejects unsupported Writable RPC and rejects unregistered RPC kinds before deserializing payloads. It creates a `RpcCall`, attaches caller context, assigns scheduler priority, optionally coordinates with `AlignmentContext`, and enqueues the call through `CallQueueManager`. Handler threads take calls, optionally requeue coordinated calls until state catches up, set `CurCall` and `CallerContext`, execute under the remote user's `doAs` when available, and update queue, lock, processing, response, detailed method, scheduler response time, and slow-RPC metrics.

Responses are assembled in `setupResponse`: protobuf-style responses are serialized into a preallocated byte array with a length prefix, while non-protobuf `Writable` responses use a reusable `ResponseBuffer`. Fatal responses mark the connection for close. `Responder.doRespond` appends the response to the per-connection queue, tries immediate nonblocking write, and uses the write selector for partial writes.

## State and persistence behavior
State is in-memory and thread-scoped: active connections, per-user connection counters, queues, response buffers, metrics objects, SASL contexts, `ThreadLocal` current calls, and scheduler state. The class does not persist user data. It does produce externally visible protocol state over sockets and metrics through Hadoop metrics. Idle scan scheduling uses a daemon `Timer`; shutdown cancels scans, closes sockets/channels, interrupts threads, and unregisters metrics.

## Dependencies and integration points
This class integrates with Hadoop configuration keys, `CallQueueManager`, `RpcScheduler`, `FairCallQueue`, `DecayRpcScheduler`, `RpcWritable`, protobuf RPC headers, `SaslRpcServer`, `SaslPropertiesResolver`, `UserGroupInformation`, delegation-token `SecretManager`, `ProxyUsers`, `ServiceAuthorizationManager`, `AlignmentContext`, and metrics classes `RpcMetrics`/`RpcDetailedMetrics`. It is extended by `RPC.Server` and depends on registered protocol engines such as protobuf RPC.

## Risks and edge cases
- Security-sensitive paths include SASL negotiation, token auth, proxy-user checks, protocol authorization, and the HADOOP-19864 pre-deserialization registered-protocol check.
- Multiple selector and handler threads coordinate through shared queues, atomics, and synchronized blocks. Races are intentionally tolerated in some areas, but response ordering and SASL wrapping rely on per-connection response queue synchronization.
- `Connection.readAndProcess` allocates a `ByteBuffer` of packet length after checking `maxDataLength`; incorrect limits would become memory pressure or denial-of-service risks.
- Fatal responses set `shouldClose`; callers must preserve that invariant so invalid protocol state cannot continue on a connection.
- Large responses are only logged, not rejected, so memory and socket backpressure still depend on caller behavior and `maxRespSize` only bounds buffer reuse.
- `ConnectionManager.getUserToConnectionsMap` exposes the concurrent map directly to JSON serialization while updates use a separate lock, so metric snapshots are eventually consistent.

## Test signals
Useful tests should cover version mismatch responses, HTTP-on-IPC response, unsupported auth protocol, SIMPLE disabled, SASL token/Kerberos negotiation, proxy user authorization failures, unregistered RPC kind rejection before deserialization, queue overflow/backoff, coordinated-call requeue, response serialization failure fallback, idle connection cleanup, per-user connection counters, metrics increments, and shutdown cleanup. Existing Hadoop IPC tests such as `TestServer`, `TestMultipleProtocolServer`, SASL/security tests, and queue/scheduler tests are the most relevant signal class.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/Server.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/UserIdentityProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/UserIdentityProvider.java

## Purpose
`UserIdentityProvider` is a simple `IdentityProvider` implementation for IPC scheduling/accounting. It groups schedulable RPC work by the short username of the call's `UserGroupInformation`.

## Important APIs, types, and functions
- `makeIdentity(Schedulable obj)` reads `obj.getUserGroupInformation()` and returns `ugi.getShortUserName()`, or `null` when no UGI is attached.

## Control flow
The implementation is branch-light: obtain the UGI, return `null` for anonymous or not-yet-authenticated calls, otherwise return the short username. Schedulers such as decay/fair-call queue components can use this identity to aggregate cost or priority by user.

## State and persistence behavior
The class is stateless and has no persistence. It depends entirely on the `Schedulable` argument.

## Dependencies and integration points
It depends on `IdentityProvider`, `Schedulable`, and Hadoop `UserGroupInformation`. It integrates with IPC schedulers that need a stable identity key.

## Risks and edge cases
Returning `null` for missing UGI must be accepted by downstream scheduler code. Short usernames intentionally collapse Kerberos realms and auth-specific identities; that is appropriate for user grouping but can merge identities that differ only by realm.

## Test signals
Tests should pass schedulables with null UGI, simple users, and Kerberos-style users where short-name mapping matters. Scheduler tests should verify null identity handling and aggregation by short username.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/UserIdentityProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/WeightedRoundRobinMultiplexer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/WeightedRoundRobinMultiplexer.java

## Purpose
`WeightedRoundRobinMultiplexer` chooses which priority queue a call consumer should inspect next. It gives higher priority queues more service opportunities while periodically serving lower priority queues to reduce starvation.

## Important APIs, types, and functions
- Config key `faircallqueue.multiplexer.weights`, namespaced by the caller, supplies one integer weight per queue.
- Constructor validates positive queue count, loads weights, applies defaults when absent, validates exact weight count, and initializes `currentQueueIndex` and `requestsLeft`.
- `getDefaultQueueWeights(int)` returns descending powers of two by priority, so queue 0 receives the largest default share.
- `getAndAdvanceCurrentIndex()` returns the current queue index and decrements remaining requests for the current queue.

## Control flow
On each call, the current index is read, then `advanceIndex` decrements `requestsLeft`. When the decrement result equals zero, `moveToNextQueue` advances `currentQueueIndex` modulo `numQueues` and resets `requestsLeft` to the next queue's configured weight. The design accepts extra reads from a queue under races because atomic operations avoid coarse locking.

## State and persistence behavior
Runtime state is in-memory: `numQueues`, `queueWeights`, `currentQueueIndex`, and `requestsLeft`. No data is persisted.

## Dependencies and integration points
It implements `RpcMultiplexer` and is used by fair-call-queue style IPC call queues. It reads weights from Hadoop `Configuration` using the queue namespace.

## Risks and edge cases
The constructor rejects zero or negative queue counts and mismatched custom weight lengths, but it does not explicitly reject zero or negative weight values. A zero weight can drive immediate or odd advancement behavior; negative values can prevent normal equality-to-zero advancement. Concurrent callers can observe more reads than the nominal weighted cycle by design.

## Test signals
Tests should cover default weights for 1, 2, and N queues; exact custom weights; mismatched custom weight length; invalid queue count; concurrent `getAndAdvanceCurrentIndex`; and behavior under zero or negative configured weights if the surrounding system permits such config.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/WeightedRoundRobinMultiplexer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/WeightedTimeCostProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/WeightedTimeCostProvider.java

## Purpose
`WeightedTimeCostProvider` computes the scheduler cost of an RPC as a weighted sum of its `ProcessingDetails` timing buckets. It is intended for use by cost-aware schedulers such as `DecayRpcScheduler`.

## Important APIs, types, and functions
- Config prefix `.weighted-cost.` is appended to the IPC namespace and lowercase `ProcessingDetails.Timing` name.
- Defaults bill `LOCKFREE`, `RESPONSE`, and `HANDLER` at weight 1, `LOCKSHARED` at 10, `LOCKEXCLUSIVE` at 100, and all other timing fields at 0.
- `init(String namespace, Configuration conf)` allocates one weight per timing enum and reads per-timing integer overrides.
- `getCost(ProcessingDetails details)` multiplies each recorded timing value by its configured weight and returns the sum.

## Control flow
Initialization iterates over all timing enum values, chooses a default by switch, builds the config key, and stores the configured weight. Cost calculation iterates over the same enum order and accumulates `details.get(timing) * weights[ordinal]`.

## State and persistence behavior
The provider stores only its configured `long[] weights`. It does not persist data and should be initialized before use.

## Dependencies and integration points
It implements `CostProvider`, depends on `ProcessingDetails`, and is selected through the Hadoop IPC cost-provider config key. It integrates with schedulers that use per-call cost rather than simple request counts.

## Risks and edge cases
`getCost` uses an `assert` to enforce initialization, so production JVMs without assertions can turn uninitialized use into a `NullPointerException`. Negative weights are not rejected and could create negative costs. Large timing values and weights can overflow `long`. Config uses `getInt`, so weights are integer-bounded even though stored as long.

## Test signals
Tests should verify default weights, per-timing override keys, ignored queue/wait timing defaults, cost units, uninitialized behavior, negative/large weights, and integration with `DecayRpcScheduler` cost accounting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/WeightedTimeCostProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/metrics/RpcDetailedMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/metrics/RpcDetailedMetrics.java

## Purpose
`RpcDetailedMetrics` publishes per-RPC-method timing rates through Hadoop metrics. It complements aggregate `RpcMetrics` by tracking method-name-specific processing samples.

## Important APIs, types, and functions
- Metrics source annotation: `@Metrics(about="Per method RPC metrics", context="rpcdetailed")`.
- `create(int port)` constructs and registers a metrics source named `RpcDetailedActivityForPort<port>`.
- `init(Class<?> protocol)` initializes `MutableRatesWithAggregation` from protocol methods.
- `addProcessingTime(String rpcCallName, long processingTime)` records a sample for a named RPC call.
- `shutdown()` unregisters the metrics source.

## Control flow
The constructor tags the registry with the RPC port. Registration goes through `DefaultMetricsSystem.instance().register`. Calls from `Server.updateMetrics` add samples after subtracting lock wait time from processing time.

## State and persistence behavior
State is in-memory metrics registry and mutable rate aggregation. No durable persistence exists; metrics are exposed through the process metrics system until `shutdown`.

## Dependencies and integration points
It depends on Hadoop metrics2 annotations and mutable metrics types. It is created by `Server` and consumed by JMX/metrics sinks configured for the Hadoop process.

## Risks and edge cases
Metric source names are port-based, so duplicate servers on the same port in one process would conflict. Dynamic method names can expand metric cardinality if call names are not controlled. `rates` is injected by metrics2 annotation processing; direct construction outside metrics registration may leave it unset.

## Test signals
Tests should verify registration name/tag, method initialization from a protocol class, adding processing samples, duplicate registration behavior, and source unregistration on shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/metrics/RpcDetailedMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/metrics/RpcMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/metrics/RpcMetrics.java

## Purpose
`RpcMetrics` publishes aggregate IPC server metrics: bytes sent/received, queue time, lock wait time, processing time, authentication/authorization counters, client backoff count, slow-RPC count, open connections, per-user connections, queue length, and dropped connections.

## Important APIs, types, and functions
- Metrics source annotation: `@Metrics(about="Aggregate RPC metrics", context="rpc")`.
- `create(Server, Configuration)` registers `RpcActivityForPort<port>`.
- Public metrics methods expose server-derived gauges: `numOpenConnections`, `numOpenConnectionsPerUser`, `callQueueLength`, and `numDroppedConnections`.
- Increment methods record auth, authorization, sent/received byte, client backoff, and slow-call events.
- `addRpcQueueTime`, `addRpcLockWaitTime`, and `addRpcProcessingTime` record rates and optional quantiles.
- Inspection helpers expose processing sample count, mean, stddev, slow calls, and registry tags.

## Control flow
Construction tags metrics with port and server name, reads percentile intervals and quantile enablement from configuration, and creates quantile metrics per interval when enabled. The server calls increment/add methods from read/write paths, auth paths, queue overflow paths, and handler completion.

## State and persistence behavior
All state lives in metrics2 mutable counters/rates/quantiles. It is not durable and is removed from the default metrics system on `shutdown`.

## Dependencies and integration points
It depends on `Server` for live gauge values, Hadoop `CommonConfigurationKeys` for quantile settings, and metrics2 classes. It is tightly integrated into `Server` request lifecycle and is visible to metrics sinks/JMX.

## Risks and edge cases
Port-based source names can collide in multi-server tests. Quantile arrays remain null when disabled; add methods guard with `rpcQuantileEnable`. Rate statistics used for slow-RPC detection depend on metrics snapshot behavior, so early sample counts and reset windows affect classification.

## Test signals
Tests should validate counters, rates, quantile creation by intervals, disabled quantile paths, server gauge delegation, slow-RPC counter behavior, processing mean/stddev accessors, tag retrieval, and unregister behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/metrics/RpcMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/metrics/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/metrics/package-info.java

## Purpose
This package descriptor documents that `org.apache.hadoop.ipc_.metrics` contains RPC-related metrics.

## Important APIs, types, and functions
It declares the package and carries package-level documentation only. There are no runtime APIs.

## Control flow
No executable control flow exists.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Javadoc and package scanners can use this descriptor. Runtime integration comes from classes in the package, especially `RpcMetrics` and `RpcDetailedMetrics`.

## Risks and edge cases
The descriptor is low risk. Its main maintenance risk is stale package documentation if metrics responsibilities expand.

## Test signals
No direct unit tests are needed; compilation and Javadoc/package checks cover it.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/metrics/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/package-info.java

## Purpose
This package descriptor documents `org.apache.hadoop.ipc_` as tools for defining network clients and servers.

## Important APIs, types, and functions
It contains package-level Javadoc and the package declaration. There are no executable APIs.

## Control flow
No runtime control flow exists.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
The descriptor supports Javadoc/package metadata for the vendored IPC implementation.

## Risks and edge cases
The only real risk is documentation drift because the package includes more than basic client/server helpers, including schedulers, security, RPC codecs, and metrics integration.

## Test signals
Compilation and documentation generation are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/ClientVersion.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/ClientVersion.java

## Purpose
`ClientVersion` enumerates protocol client feature versions and maps integer protobuf values to semantic version constants. It lets servers and clients reason about compatibility and feature availability.

## Important APIs, types, and functions
- Enum values include `DEFAULT_VERSION`, `VERSION_HANDLES_UNKNOWN_DN_PORTS`, `ERASURE_CODING_SUPPORT`, `BUCKET_LAYOUT_SUPPORT`, and `FUTURE_VERSION`.
- `CURRENT` and `CURRENT_VERSION` represent the latest known nonnegative version.
- `description()` and `toProtoValue()` implement `ComponentVersion`.
- `fromProtoValue(int)` maps wire values to enum constants, defaulting to `FUTURE_VERSION`.

## Control flow
Static initialization builds `BY_PROTO_VALUE` from enum values and computes `CURRENT` via maximum protobuf value. Unknown future positive values and any unrecognized integer map to `FUTURE_VERSION`.

## State and persistence behavior
State is static immutable enum metadata and a static lookup map. Version integers are persisted externally in protocol messages, not by this class.

## Dependencies and integration points
It implements `org.apache.hadoop.hdds.ComponentVersion` and is used by client/server protocol negotiation and feature gates.

## Risks and edge cases
`latest()` uses max `toProtoValue`, so `FUTURE_VERSION(-1)` is safely excluded while current versions remain nonnegative. Adding a new version must preserve unique integer values. Unknown negative values also map to `FUTURE_VERSION`, which may or may not match caller expectations.

## Test signals
Tests should verify current version, round-trip for each enum integer, unknown value mapping, and that new enum additions update `CURRENT_VERSION`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/ClientVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/OzoneConfigKeys.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/OzoneConfigKeys.java

## Purpose
`OzoneConfigKeys` is the central public/unstable constant catalog for Ozone and HDDS configuration keys and defaults. It gives all components a shared spelling and default value source for ports, storage paths, security, ACLs, replication, Ratis, datastream, client behavior, HTTP/HTTPS, snapshots, SCM client settings, metrics, and other service features.

## Important APIs, types, and functions
- The class is `final`, has only `public static final` constants, and prevents construction with a private constructor.
- Key groups include container IPC/Ratis/datastream ports and random-port flags, metadata/db directory keys and permissions, chunk write and unsafe byte operation toggles, container cache settings, SCM block size, EC gRPC retries/timeouts, admin/read-only/blacklist users and groups, REST client connection limits, client socket/connection/read timeouts, replication defaults, list cache sizes, block and snapshot service intervals/timeouts/workers, Ratis settings delegated from `ScmConfigKeys`, datanode storage thresholds and RocksDB cache, security and HTTP security toggles, ACL authorizer settings, S3 volume and bucket layout defaults, client failover/follower-read settings, Freon HTTP settings, topology-aware read, OM lock sizing, HTTPS keystore/truststore keys, key provider cache, required OM version, listing page sizes, snapshot compaction knobs, SCM close wait, SCM client retry settings, and crypto compliance mode.
- Several constants reuse typed defaults from `ScmConfigKeys`, `ReplicationFactor`, `ReplicationType`, `HttpConfig.Policy`, `TimeDuration`, and `TimeUnit`.

## Control flow
There is no runtime control flow beyond class loading and static initialization of constants. Defaults that call methods such as `ReplicationFactor.THREE.toString()`, `HttpConfig.Policy.HTTP_ONLY.name()`, or `TimeUnit.*.toMillis(...)` are evaluated at class initialization.

## State and persistence behavior
The class stores immutable constant values. It does not read or persist configuration; other components use these keys with configuration sources to produce runtime behavior and persistent metadata locations.

## Dependencies and integration points
Dependencies include HDDS annotations, replication enums, `ScmConfigKeys`, Hadoop HTTP policy, and Ratis `TimeDuration`. Integration is broad: Ozone Manager, SCM, DataNode containers, S3 gateway, clients, Freon, security, snapshots, and metrics all reference this constant surface.

## Risks and edge cases
- Because constants are public and unstable, renames or default changes can silently alter cluster behavior or break configuration compatibility.
- Delegating some Ratis constants to `ScmConfigKeys` avoids duplication but couples this catalog to SCM defaults.
- Time defaults mix strings such as `30s`, milliseconds as `long`, and `TimeDuration`; callers must use the matching config parsing API.
- Security-related defaults are sensitive: `OZONE_SECURITY_ENABLED_DEFAULT` and HTTP security default false, while `OZONE_AUTHORIZATION_ENABLED_DEFAULT` true only takes effect when security or test authorization is enabled.
- Typographical compatibility matters; misspelled or legacy keys should not be "fixed" casually if users may already depend on them.

## Test signals
Tests should cover that key strings and defaults match generated docs/config references, secure/insecure defaults are interpreted correctly by `OzoneSecurityUtil`, Ratis constants mirror `ScmConfigKeys`, typed time and size defaults parse in component config loaders, and compatibility checks detect accidental key/default changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/OzoneConfigKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/OzoneConsts.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/OzoneConsts.java

## Purpose
`OzoneConsts` is a private constant catalog for Ozone runtime identifiers, metadata keys, URI schemes, ACL symbols, DB names, audit field names, snapshot and container field names, Ranger endpoints, security literals, quota/unit values, and object-key validation. These constants standardize names that are persisted in metadata, exchanged over APIs, or logged.

## Important APIs, types, and functions
- The class is `final`, has only constants, a private constructor, and enum `Units { TB, GB, MB, KB, B }`.
- Cluster/storage identity constants cover SCM, cluster, datanode, storage, layout, ctime, and certificate ids.
- Namespace constants cover Ozone/OFS schemes, RPC/HTTP schemes, root path, URI delimiter, OM key/user/S3 prefixes, and trash/copying suffixes.
- Container and DB constants cover `.container`, checksum sidecar extension, metadata/chunks paths, schema versions, DB names, metadata keys, block delete markers, and checksum fields.
- ACL and audit constants cover ACL entity/action symbols and audit map keys for volumes, buckets, keys, quotas, replication, multipart upload, tenants, snapshots, and job status.
- Snapshot and RocksDB constants cover checkpoint/snapshot directories, transaction info, prepare markers, compaction backup/log tables, SST suffixes, and snapshot diff DB names.
- Security and Ranger constants cover Kerberos values, delegation token fields, SCM CA naming, Ranger REST endpoints, and tenant policy/role suffixes.
- `KEYNAME_ILLEGAL_CHARACTER_CHECK_REGEX` defines the allowed object key character pattern.

## Control flow
There is no dynamic control flow. Static initialization constructs `ROOT_PATH`, `SCM_ROOT_CA_COMPONENT_NAME`, and the key-name validation `Pattern`.

## State and persistence behavior
The constants are immutable, but many values are persistence-critical because they become RocksDB keys, marker filenames, metadata YAML fields, audit keys, HTTP endpoints, and object namespace delimiters. Changing them can make existing data unreadable or alter API behavior.

## Dependencies and integration points
Dependencies are light: HDDS `InterfaceAudience`, Java `Path/Paths`, charset constants, and regex `Pattern`. Integration spans OM, SCM, DataNode containers, S3 gateway, Ranger, audit logging, snapshots, compaction, and filesystem clients.

## Risks and edge cases
- Persistence and wire/API constants require strict backward compatibility.
- `KEYNAME_ILLEGAL_CHARACTER_CHECK_REGEX` is an allow-list; changes affect object name validation and S3 compatibility.
- Constants encode several sentinel values, such as `QUOTA_RESET`, `OLD_QUOTA_DEFAULT`, `DEFAULT_OM_UPDATE_ID`, and `EXPECTED_GEN_CREATE_IF_ABSENT`; misuse can invert semantics.
- Several strings include separators such as `/`, `$`, `#`, tab, and `:` that must match database key composition and parsing logic exactly.

## Test signals
Tests should verify DB key construction/parsing, persisted marker lookup, audit map field names, key-name validation, quota sentinel handling, URI scheme handling, Ranger endpoint composition, and backward compatibility against known metadata samples.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/OzoneConsts.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/OzoneManagerVersion.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/OzoneManagerVersion.java

## Purpose
`OzoneManagerVersion` enumerates server-side Ozone Manager protocol feature versions and maps protobuf integer values to enum constants for compatibility checks.

## Important APIs, types, and functions
- Enum values track OM features from `DEFAULT_VERSION` through `S3_BUCKET_TAGGING_API`, with `FUTURE_VERSION(-1)` for unknown newer server versions.
- `CURRENT` is the latest known concrete version.
- `description()` and `toProtoValue()` implement `ComponentVersion`.
- `fromProtoValue(int)` uses a static lookup map and defaults unknown values to `FUTURE_VERSION`.

## Control flow
Static initialization builds `BY_PROTO_VALUE`. `latest()` returns `values()[values.length - 2]`, intentionally selecting the enum before `FUTURE_VERSION`; this requires all real versions to appear before the sentinel.

## State and persistence behavior
State is static enum metadata. Version values are serialized externally in protocol messages; this class does not persist data itself.

## Dependencies and integration points
It implements `ComponentVersion` and is referenced by client compatibility requirements, including defaults in `OzoneConfigKeys`.

## Risks and edge cases
Adding new real versions after `FUTURE_VERSION` would break `CURRENT`. Duplicate integer values would break lookup semantics. Unknown older or malformed values map to `FUTURE_VERSION`, which callers should treat carefully.

## Test signals
Tests should verify `CURRENT` is `S3_BUCKET_TAGGING_API`, all known values round-trip, unknown values map to `FUTURE_VERSION`, and enum ordering constraints are enforced when new versions are added.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/OzoneManagerVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/OzoneSecurityUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/OzoneSecurityUtil.java

## Purpose
`OzoneSecurityUtil` centralizes shared security helper logic for Ozone: security enablement, HTTP security enablement, authorization enablement including test mode, existence checks for key/cert files, and PEM string to `X509Certificate` conversion.

## Important APIs, types, and functions
- `isSecurityEnabled(ConfigurationSource conf)` initializes the security provider and reads `ozone.security.enabled`.
- `isHttpSecurityEnabled(ConfigurationSource conf)` requires full security plus HTTP Kerberos enablement.
- `isAuthorizationEnabled(ConfigurationSource conf)` enables authorization when full security or test authorization is enabled and `ozone.authorization.enabled` is true.
- `checkIfFileExist(Path path, String fileName)` checks directory and child-file existence.
- `convertToX509(List<String> pemEncodedCerts)` converts each PEM string through `CertificateCodec.readX509Certificate`.

## Control flow
The security predicates compose configuration booleans. `isAuthorizationEnabled` explicitly supports an authorization test mode that does not require full security. Certificate conversion iterates in input order and propagates `IOException`.

## State and persistence behavior
The utility is stateless, but `isSecurityEnabled` calls `SecurityConfig.initSecurityProvider`, which may initialize process-wide security provider state. File existence checks observe filesystem state and certificate conversion constructs in-memory certificate objects.

## Dependencies and integration points
It depends on HDDS `ConfigurationSource`, `SecurityConfig`, `CertificateCodec`, and Ozone config constants. It is used by Ozone services and tests to gate Kerberos, HTTP security, ACL/admin authorization, and certificate processing.

## Risks and edge cases
Calling `isHttpSecurityEnabled` and `isAuthorizationEnabled` also calls `isSecurityEnabled`, causing provider initialization side effects. `checkIfFileExist` only checks existence, not type, readability, permissions, or symlink safety. PEM conversion trusts `CertificateCodec` for validation and fails the entire conversion on the first bad certificate.

## Test signals
Tests should cover all combinations of security, HTTP security, authorization, and test-authorization flags; provider initialization idempotence; existing/missing file checks; unreadable/non-file paths if relevant; and valid/invalid PEM certificate conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/OzoneSecurityUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/Versioned.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/Versioned.java

## Purpose
`Versioned` is a minimal interface for objects that expose an integer version.

## Important APIs, types, and functions
- `int version()` returns the implementing object's version.

## Control flow
No control flow exists beyond implementers providing the method.

## State and persistence behavior
The interface has no state. Implementers decide whether version is static, computed, or persisted.

## Dependencies and integration points
It has no imports and can be implemented by Ozone types that need a lightweight version contract separate from richer component-version enums.

## Risks and edge cases
The interface gives no semantics for monotonicity, compatibility, unknown versions, or serialization. Callers must know the implementing type's version domain.

## Test signals
No direct tests are needed for the interface; implementer tests should verify version values and compatibility rules.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/Versioned.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/audit/Auditable.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/audit/Auditable.java

## Purpose
`Auditable` marks an entity as able to render itself into key/value pairs for audit logging.

## Important APIs, types, and functions
- `Map<String, String> toAuditMap()` returns values to be logged in audit records.

## Control flow
There is no implementation control flow; each implementing entity chooses which fields to include.

## State and persistence behavior
The interface has no state or persistence. Returned maps are consumed by audit logging code and may become durable logs depending on audit sink configuration.

## Dependencies and integration points
It depends only on `java.util.Map`. Implementations typically use keys from `OzoneConsts` and are consumed by Ozone audit framework components in clients and servers.

## Risks and edge cases
Implementations can leak sensitive data, omit important identifiers, return mutable maps, or use inconsistent key names. Audit consumers should not assume all values are present.

## Test signals
Implementer tests should verify stable audit keys, redaction of sensitive fields, null handling, and consistency with command/action audit expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/audit/Auditable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/audit/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/audit/package-info.java

## Purpose
This package descriptor documents that `org.apache.hadoop.ozone.audit` in `hdds-common` contains shared client/server audit framework pieces and points readers to the server-framework package for more detail.

## Important APIs, types, and functions
It declares package documentation only. No runtime APIs are defined here.

## Control flow
No executable control flow exists.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Javadoc tooling and package scanners can use this descriptor. Runtime audit integration is provided by interfaces/classes in this and related packages.

## Risks and edge cases
Documentation can drift from the split between common and server-framework audit code.

## Test signals
Compilation and documentation generation cover this file.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/audit/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/Checksum.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/Checksum.java

## Purpose
`Checksum` computes and verifies per-chunk checksums for Ozone data buffers. It supports `NONE`, `CRC32`, `CRC32C`, `SHA256`, and `MD5`, splits data by `bytesPerChecksum`, and optionally uses `ChecksumCache` to avoid recomputing unchanged chunk segments.

## Important APIs, types, and functions
- Constructors accept checksum type, bytes per checksum, and optional cache enablement.
- `clearChecksumCache()` resets cache state when a new block chunk begins.
- `computeChecksum` overloads accept byte arrays, `ByteBuffer`, `List<ByteString>`, and `ChunkBuffer`, with optional cache use.
- `Algorithm` maps `ContainerProtos.ChecksumType` to functions backed by `MessageDigest` or `ChecksumByteBuffer`.
- `computeChecksum(ByteBuffer, Function, int)` temporarily limits a buffer to compute at most one checksum segment.
- Static verification helpers include `verifySingleChecksum`, `verifyChecksum(ByteBuffer, ChecksumData, int)`, `verifyChecksum(ChunkBuffer, ChecksumData, int)`, and `verifyChecksum(List<ByteString>, ChecksumData, int)`.
- `getNoChecksumDataProto()` returns a testing protobuf with checksum type `NONE`.

## Control flow
Computation short-circuits for `NONE`. Other types create a fresh algorithm function, wrap input in a read-only `ChunkBuffer`, iterate slices of `bytesPerChecksum`, compute one digest/checksum per slice, and return immutable `ChecksumData`. With cache enabled and requested, computation delegates to `ChecksumCache`, which recomputes only changed trailing checksum entries. Verification recomputes checksums for supplied data and delegates comparison to `ChecksumData.verifyChecksumDataMatches` with a start index.

## State and persistence behavior
Instances hold checksum type, bytes-per-checksum, and optional mutable cache. The class itself does not persist data, but `ChecksumData` output is serialized into container protobufs and stored/transmitted with chunk metadata.

## Dependencies and integration points
It depends on container protobuf `ChecksumType`, Ratis protobuf `ByteString`, `ChunkBuffer`, `BufferUtils`, `ChecksumByteBufferFactory`, `ChecksumCache`, `ChecksumData`, `IntegerCodec`, and `UnsafeByteOperations`. It integrates with Ozone clients, block streams, datanode chunk IO, and tests.

## Risks and edge cases
- The class is explicitly not thread-safe because algorithm functions and cache state are mutable.
- `bytesPerChecksum` must be positive for meaningful slicing; this class does not validate all invalid values directly.
- `computeChecksum(ByteBuffer, Function, int)` mutates and restores buffer limit but advances position through the algorithm.
- `verifySingleChecksum` sets limit to `offset + bytesPerChecksum`; callers must ensure bounds for short final chunks.
- MD5/SHA256 use a shared `MessageDigest` inside each function instance, so the function must not be shared concurrently.
- Cache correctness requires callers to clear cache whenever starting a new block chunk.

## Test signals
Tests should cover all checksum types, byte array/ByteBuffer/ChunkBuffer/List inputs, final partial chunk handling, start-index verification, mismatch exceptions, `NONE` short-circuit, read-only and direct buffers, cache reuse and cache clearing, invalid algorithm/type handling, and Java-version-specific CRC32C paths through the factory.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/Checksum.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumByteBuffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumByteBuffer.java

## Purpose
`ChecksumByteBuffer` extends `java.util.zip.Checksum` with an explicit `update(ByteBuffer)` method while maintaining Java 8 compatibility.

## Important APIs, types, and functions
- `void update(ByteBuffer buffer)` updates checksum state from the buffer and advances position to limit.
- Default `update(byte[] b, int off, int len)` wraps the byte range as a read-only `ByteBuffer` and delegates to `update(ByteBuffer)`.

## Control flow
Implementations provide ByteBuffer update behavior. The byte-array default path centralizes update logic through ByteBuffer handling.

## State and persistence behavior
The interface has no state. Implementations maintain checksum accumulator state and expose it through inherited `getValue`/`reset`.

## Dependencies and integration points
It integrates `java.util.zip.Checksum` implementations with Ozone checksum calculation, especially direct/read-only buffer support in `ChecksumByteBufferImpl`.

## Risks and edge cases
The missing `@Override` on `update(ByteBuffer)` is intentional for Java 8 compatibility because the JDK interface added that method later. Implementations must obey the position-advancing contract, or checksum slicing logic can break.

## Test signals
Tests should verify byte-array and ByteBuffer updates produce identical CRC values, buffer positions advance to limit, read-only buffers work, and reset/getValue semantics match `Checksum`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumByteBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumByteBufferFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumByteBufferFactory.java

## Purpose
`ChecksumByteBufferFactory` creates `ChecksumByteBuffer` wrappers for CRC32 and CRC32C, selecting the JDK Java 9+ CRC32C implementation when available and falling back to Hadoop's `PureJavaCrc32C`.

## Important APIs, types, and functions
- `crc32Impl()` returns a `ChecksumByteBufferImpl` around `java.util.zip.CRC32`.
- `crc32CImpl()` tries Java 9 `java.util.zip.CRC32C` when `useJava9Crc32C` is true, logs and disables it on unexpected failure, otherwise returns `PureJavaCrc32C`.
- Nested `Java9Crc32CFactory` uses `MethodHandles.publicLookup` and a constructor `MethodHandle` to instantiate `CRC32C` without requiring Java 9 at compile time.

## Control flow
Class initialization sets `useJava9Crc32C` from `JavaUtils.isJavaVersionAtLeast(9)`. The nested factory resolves the Java 9 constructor only when loaded. `crc32CImpl` attempts JDK CRC32C first and permanently switches the volatile flag off if creation fails.

## State and persistence behavior
The only mutable state is the process-wide volatile `useJava9Crc32C` fallback flag. No persistence exists.

## Dependencies and integration points
It depends on Java method handles, `CRC32`, optional runtime `CRC32C`, Hadoop `PureJavaCrc32C`, `JavaUtils`, and `ChecksumByteBufferImpl`. It is used by `Checksum.Algorithm` for CRC calculations.

## Risks and edge cases
Reflection/method-handle failures are handled differently in static nested initialization versus runtime creation. Once fallback is triggered, the process will continue using pure Java CRC32C. The logger uses `ChecksumByteBufferImpl.class`, which is harmless but slightly misleading.

## Test signals
Tests should verify CRC32 output, CRC32C output on Java 8 and Java 9+ runtimes, fallback after forced Java9 creation failure, direct-buffer support through the returned implementation, and thread visibility of the volatile fallback flag.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumByteBufferFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumByteBufferImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumByteBufferImpl.java

## Purpose
`ChecksumByteBufferImpl` adapts any `java.util.zip.Checksum` implementation to the Ozone `ChecksumByteBuffer` interface, adding efficient `ByteBuffer` update support across Java 8 and Java 9+.

## Important APIs, types, and functions
- Constructor stores the wrapped `Checksum`.
- Static initialization resolves Java 8 private `ByteBuffer.isReadOnly` field for a no-copy array path and Java 9+ `Checksum.update(ByteBuffer)` method handle for native ByteBuffer updates.
- `update(ByteBuffer buffer)` prefers Java 9+ `Checksum.update(ByteBuffer)`, otherwise tries to clear read-only state reflectively and update from backing array when present, falling back to copying remaining bytes into an array.
- `update(byte[]...)`, `update(int)`, `getValue()`, and `reset()` delegate to the wrapped checksum.

## Control flow
On Java 9+, `BYTE_BUFFER_UPDATE.invokeExact` is the primary path and advances the buffer per JDK behavior. On Java 8, reflection may allow `hasArray()` on read-only heap buffers, avoiding a copy; otherwise the method copies remaining bytes and updates the checksum.

## State and persistence behavior
Instances hold mutable checksum accumulator state in the wrapped `Checksum`. Static method handles/field references are process-wide. No persistence exists.

## Dependencies and integration points
It depends on `JavaUtils`, reflection, method handles, `ByteBuffer`, `Checksum`, and SLF4J. It is created by `ChecksumByteBufferFactory` and used by `Checksum`.

## Risks and edge cases
- Reflectively mutating `ByteBuffer.isReadOnly` on Java 8 is fragile and can violate buffer immutability expectations.
- In the Java 8 array-backed path, the code calls `checksum.update` but does not advance the buffer position, despite the interface contract saying position should reach limit. The copy path does advance because `buffer.get(b)` is used. Callers should not rely on position after array-backed Java 8 updates unless tests confirm behavior.
- Method-handle invocation wraps any failure as `IllegalStateException`.
- The class is not thread-safe unless the wrapped checksum is externally synchronized.

## Test signals
Tests should cover heap, read-only heap, direct, and sliced buffers; Java 8 and Java 9+ behavior; position advancement; values matching reference CRC implementations; reset; and error behavior if reflection/method handles are unavailable.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumByteBufferImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumCache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumCache.java

## Purpose
`ChecksumCache` caches checksums for a growing `ChunkBuffer` so repeated checksum computation during writes only recomputes the last partial checksum and newly appended checksum segments.

## Important APIs, types, and functions
- Constructor accepts `bytesPerChecksum`, initializes `prevChunkLength` to zero, and preallocates the checksum list based on a 4 MB block chunk size hint.
- `clear()` resets previous length and removes all cached checksums.
- `getChecksums()` returns the backing checksum list.
- `computeChecksum(ChunkBuffer data, Function<ByteBuffer, ByteString> function)` computes or updates checksum entries for data up to `data.limit()`.

## Control flow
If current chunk length equals the previous length, the cached list is returned. If current length is smaller, an `IllegalArgumentException` signals that the caller failed to clear cache for a new chunk. Otherwise, the method calculates the first checksum index needing recomputation from `prevChunkLength / bytesPerChecksum`, iterates `data.iterate(bytesPerChecksum)`, skips known stable entries, updates the previous last partial entry or appends new entries, verifies the expected end index, updates `prevChunkLength`, and returns the list.

## State and persistence behavior
State is mutable and in-memory: `prevChunkLength` and the backing `List<ByteString>`. The returned list is mutable and owned by the cache. No persistence exists, but its output is used to build persisted `ChecksumData`.

## Dependencies and integration points
It depends on `ChunkBuffer`, `Checksum.computeChecksum`, and Ratis `ByteString`. It is currently intended for `BlockOutputStream` through `Checksum` when cache use is explicitly requested.

## Risks and edge cases
- The cache is not thread-safe.
- Callers must clear it when starting a new block chunk; otherwise smaller lengths throw and equal/larger unrelated data can produce wrong reuse.
- `getChecksums()` exposes mutable internal state.
- `bytesPerChecksum` must be positive; no constructor validation is present.
- The algorithm recomputes the last partial checksum rather than incrementally extending CRC state, which is correct but leaves some performance on the table.

## Test signals
Tests should cover repeated same-length calls, append within a partial checksum, append crossing checksum boundaries, exact boundary lengths, shrink-without-clear exception, clear behavior, output equality with full recomputation, and invalid `bytesPerChecksum` handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumData.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumData.java

## Purpose
`ChecksumData` is an immutable Java wrapper around the container protobuf `ChecksumData` message. It stores checksum type, bytes per checksum, and ordered checksum bytes, and provides conversion, equality, hashing, string formatting, and mismatch verification.

## Important APIs, types, and functions
- Constructors accept checksum type and bytes-per-checksum, with optional checksum list.
- Accessors: `getChecksumType`, `getBytesPerChecksum`, and `getChecksums`.
- `getProtoBufMessage()` lazily builds and memoizes the protobuf via `MemoizedSupplier`.
- `getFromProtoBuf(ContainerProtos.ChecksumData)` converts protobuf to wrapper.
- `verifyChecksumDataMatches(int thisStartIndex, ChecksumData that)` compares this object's checksums from a start index against another computed checksum set.
- `equals`, `hashCode`, and `toString` implement value semantics and hex rendering.

## Control flow
Construction validates non-null type, wraps the checksum list with `Collections.unmodifiableList`, and sets up a memoized protobuf supplier. Verification first checks that the compared checksum count fits from the requested start index, then compares each checksum and throws `OzoneChecksumException` with detailed context on count or byte mismatch.

## State and persistence behavior
The wrapper is annotated immutable and stores final fields. The checksum list is unmodifiable but not defensively copied, so external mutation of the original list before or after construction can affect immutability if the source list is mutable. The protobuf representation is memoized in memory and is the serialized form used in container metadata.

## Dependencies and integration points
It depends on container protobufs, `ChecksumType`, Ratis `ByteString`, HDDS `StringUtils`, Apache Commons `HashCodeBuilder`, JCIP `@Immutable`, and Ratis `MemoizedSupplier`. It is produced by `Checksum` and consumed by verification and container/chunk metadata code.

## Risks and edge cases
- Lack of defensive copy weakens the immutability guarantee.
- `verifyChecksumDataMatches` assumes `thisStartIndex` is valid; negative values can lead to index errors rather than a clean checksum exception.
- `hashCode` converts the list to an array, which is fine for typical checksum counts but can cost memory for very large lists.
- `toString` renders all checksums in hex, which may be verbose and could expose checksum material in logs.

## Test signals
Tests should cover proto round-trip, memoized protobuf stability, equality/hash code, unmodifiable checksum list behavior, mutation of source list after construction, successful and failed verification at different start indexes, negative/out-of-range start indexes, and `toString` formatting for empty and non-empty checksum lists.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumData.java -->
