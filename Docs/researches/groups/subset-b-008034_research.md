# subset-b-008034 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHADBTransactionBufferStub.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHADBTransactionBufferStub.java

Purpose: Test and Recon-oriented `SCMHADBTransactionBuffer` implementation that batches table writes without the full production HA transaction-info bookkeeping.

Important APIs and types: Constructors accept no store or a `DBStore`; `addToBuffer`, `removeFromBuffer`, `flushIfNeeded`, `flush`, and `close` implement the useful part of the interface. Transaction and snapshot methods are stubs returning null or doing nothing.

Control flow: Writes acquire the read lock, lazily create either a `DBStore` batch or an atomic RocksDB batch, and enqueue table puts/deletes. `flush` takes the write lock, commits through `DBStore` when present, closes the batch, and resets it.

State and persistence behavior: The only meaningful mutable state is `currentBatchOperation`. With a real `DBStore`, flush persists queued mutations; without one, the in-memory atomic operation is closed without durable commit.

Dependencies and integration points: Used by `SCMHAManagerStub` and Recon/test paths that need the same buffer API as production SCM HA.

Risks and test signals: It deliberately omits latest transaction and snapshot tracking, so tests that exercise snapshot, checkpoint, or term-index behavior must not rely on it. Useful assertions are batched table mutation visibility after `flush` and correct cleanup on `close`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHADBTransactionBufferStub.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAManager.java

Purpose: Top-level SCM HA service contract used by `StorageContainerManager` to own Ratis, snapshots, transaction buffering, membership changes, and checkpoint installation.

Important APIs and types: Lifecycle methods are `start`, `stop`, and `close`. Accessors expose `SCMRatisServer`, `SCMSnapshotProvider`, generic `DBTransactionBuffer`, and HA-specific `SCMHADBTransactionBuffer`. Operational APIs include `addSCM`, `removeSCM`, `downloadCheckpointFromLeader`, `getSecretKeysFromLeader`, `verifyCheckpointFromLeader`, and `installCheckpoint`.

Control flow: Implementations start HA transport and consensus services, route replicated writes through the returned Ratis server/buffer, and use checkpoint download/verify/install during follower catch-up.

State and persistence behavior: The interface defines persistence boundaries rather than state itself: DB transaction buffering, RocksDB checkpoints, Ratis `TermIndex`, and replicated secret keys.

Dependencies and integration points: Used by Ratis state machine callbacks, SCM bootstrap/add/remove commands, secret-key manager, snapshot provider, and metadata reload code.

Risks and test signals: Correctness depends on implementations honoring term-index checks before replacing the DB. Tests should cover membership validation, null snapshot-provider handling, checkpoint freshness checks, and proper type from `asSCMHADBTransactionBuffer`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAManagerImpl.java

Purpose: Production HA manager that wires SCM to Apache Ratis, inter-SCM gRPC checkpoint transfer, transaction-buffer flushing, SCM membership changes, and DB checkpoint replacement.

Important APIs and types: Builds `SCMHADBTransactionBufferImpl`, `SCMRatisServerImpl`, `SCMSnapshotProvider`, and `InterSCMGrpcProtocolService`. Key methods are `start`, `createStartTransactionBufferMonitor`, `downloadCheckpointFromLeader`, `getSecretKeysFromLeader`, `verifyCheckpointFromLeader`, `installCheckpoint`, `startServices`, `stopServices`, `addSCM`, and `removeSCM`.

Control flow: Startup starts Ratis, bootstrapped nodes with an empty group submit `AddSCMRequest` through `HAUtils.addSCM`, then starts gRPC and the transaction-buffer monitor. Snapshot install verifies the downloaded checkpoint transaction info against the local last-applied index, stops the metadata store, replaces the DB directory with a checkpoint, reloads SCM managers from the new tables, and deletes the backup.

State and persistence behavior: Owns persistent RocksDB replacement, Ratis term/index checks, transaction-buffer lifecycle, secret-key synchronization, and dependent manager reinitialization for sequence IDs, pipelines, containers, deleted blocks, service configs, certificates, and finalization state.

Dependencies and integration points: Integrates `StorageContainerManager`, `SCMDBDefinition`, `HAUtils`, `SCMMetadataStore`, `SecretKeyProtocolClientSideTranslatorPB`, `OzoneSecurityUtil`, and Ratis `TermIndex`.

Risks and test signals: Checkpoint rollback and exit behavior are high risk: corrupt checkpoints force DB restoration and process exit. Membership operations must reject mismatched cluster IDs. Tests should assert service stop/restart ordering, DB backup deletion, reinitialize calls, bootstrapped add behavior, and secret-key retrieval only when enabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAManagerStub.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAManagerStub.java

Purpose: Lightweight HA manager for Recon and tests that simulates Ratis submission and leader/follower behavior without running a real Raft server.

Important APIs and types: Static factories create leader/follower instances and optionally wrap a `DBStore` in `SCMHADBTransactionBufferStub`. Inner `RatisServerStub` implements `SCMRatisServer`, stores `ScmInvoker` handlers by `RequestType`, and exposes `submitRequest`, `triggerNotLeaderException`, and fixed role strings.

Control flow: On leader mode, `submitRequest` decodes the requested invoker and calls `invokeLocal`, wrapping success or `StateMachineException` in a synthetic `RaftClientReply`. On follower mode, it returns a `NotLeaderException`.

State and persistence behavior: Persists only through the supplied transaction buffer. Snapshot provider, checkpoint download/install, add/remove SCM, and real Ratis division/state machine paths are intentionally no-ops or null.

Dependencies and integration points: Used by components that build HA proxies through `getProxyHandler` but need deterministic local execution in unit tests or Recon.

Risks and test signals: Null `getDivision` and `getSCMStateMachine` make it unsuitable for code paths that need real Raft metadata. Tests can assert leader local invocation, follower not-leader translation, invoker registration, and buffer close behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAManagerStub.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAMetrics.java

Purpose: Hadoop metrics source that reports whether the current SCM node is the SCM HA leader.

Important APIs and types: `create(nodeId, leaderId)` registers a `MetricsSource` named `SCMHAMetrics`; `unRegister` removes it. `getMetrics` emits a `NodeId` tag and `SCMHALeaderState` gauge. Inner `SCMHAMetricsInfo` stores current values for test visibility.

Control flow: Metrics collection compares the configured current node id with the leader id, sets state to `1` for leader and `0` for follower, then emits the record.

State and persistence behavior: No durable state. Runtime state is the fixed `currNodeId`/`leaderId` pair and last values in `SCMHAMetricsInfo`.

Dependencies and integration points: Registered through Hadoop `DefaultMetricsSystem`; updated from SCM HA leadership notifications.

Risks and test signals: The leader id is captured at construction, so callers must recreate/update metrics when leadership changes. Tests should assert registration, node tag, leader/follower gauge values, unregister behavior, and visible-for-testing getters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHANodeDetails.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHANodeDetails.java

Purpose: Loads and holds local and peer SCM node configuration for HA clusters, including Ratis, gRPC, RPC, client, block, and datanode addresses.

Important APIs and types: `loadDefaultConfig`, `loadSCMHAConfig`, `getHASCMNodeDetails`, `getLocalNodeDetails`, and `getPeerNodeDetails`. It uses `SCMNodeDetails` as the node value object and applies node-specific config suffixes through `ConfUtils`.

Control flow: HA loading selects service ids from `ozone.scm.default.service.id` or `ozone.scm.service.ids`, iterates configured SCM node ids, resolves per-node RPC/Ratis/gRPC settings, identifies the local address, accumulates peers, sets node-specific keys, and returns local-plus-peer details. Missing node lists or SCM addresses raise configuration exceptions; no HA address falls back to default config.

State and persistence behavior: No persistence. It mutates the provided `OzoneConfiguration` by applying local node-specific overrides.

Dependencies and integration points: Used during SCM startup, Ratis peer creation, inter-SCM gRPC snapshot downloads, and command/bootstrap code.

Risks and test signals: Local-node detection is sensitive to DNS/FQDN resolution and multiple matching addresses. Tests should cover default mode, missing node ids, unresolved but flexible FQDNs, duplicate local matches, per-node port fallback, and peer list construction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHANodeDetails.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHATransactionBufferMonitorTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHATransactionBufferMonitorTask.java

Purpose: Periodic task that asks the HA transaction buffer to flush when its configured interval or snapshot wait policy requires it.

Important APIs and types: Implements `Runnable`; constructed with `SCMHADBTransactionBuffer` and a flush interval. `run` delegates to `transactionBuffer.flushIfNeeded(flushInterval)`.

Control flow: The task is scheduled by `SCMHAManagerImpl` through `BackgroundSCMService`. Each run catches `IOException` and logs failure without throwing out of the background service.

State and persistence behavior: No local state beyond the buffer reference and interval. Persistence is entirely delegated to the transaction buffer, which may flush batched RocksDB mutations and transaction metadata.

Dependencies and integration points: Connects SCM HA transaction buffering to the generic SCM background-service framework.

Risks and test signals: Because failures are logged and swallowed, persistent flush failure may repeat without stopping SCM immediately. Tests should assert delegation, configured interval use, and that thrown IOExceptions are contained.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHATransactionBufferMonitorTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMNodeDetails.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMNodeDetails.java

Purpose: SCM-specific extension of generic `NodeDetails`, adding SCM client, block, datanode protocol, and gRPC endpoint metadata.

Important APIs and types: Builder setters define service id, node id, RPC address, Ratis port, gRPC port, HTTP/HTTPS addresses, and protocol server address/key pairs. Getters expose all SCM-specific endpoints, and `getRpcAddressString` returns host:port through Hadoop `NetUtils`.

Control flow: The builder accumulates endpoint fields and `build` creates an immutable `SCMNodeDetails`. The constructor passes common identity/RPC/Ratis/HTTP data to `NodeDetails` and stores SCM-specific fields.

State and persistence behavior: No persistence; values are configuration-derived runtime metadata.

Dependencies and integration points: Built by `SCMHANodeDetails`, used by Ratis peer creation, checkpoint download host/port lookup, protocol server binding, diagnostics, and config key selection.

Risks and test signals: The builder does not validate required fields, so nulls can propagate to later startup failures. Tests should assert endpoint formatting, getter preservation, `toString` coverage, and behavior with unresolved addresses when flexible FQDN support is enabled elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMNodeDetails.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMRatisRequest.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMRatisRequest.java

Purpose: Encodes SCM replicated method calls into Ratis `Message` payloads and decodes committed log entries back into typed local invocations.

Important APIs and types: `of`, `encode`, `decode`, `getType`, `getOperation`, `getArguments`, `getParameterTypes`, and `smProtoToString`. It serializes `RequestType`, method name, parameter type names, and argument bytes using `ScmCodecFactory`.

Control flow: Creation verifies parameter count equals argument count. Encoding records declared parameter types, not runtime subclass types, then resolves the codec type and serializes each argument. Decoding validates required proto fields, loads parameter classes by name, resolves codecs, and deserializes argument values.

State and persistence behavior: No local persistence, but encoded bytes become Ratis log data and therefore define the replicated operation format.

Dependencies and integration points: Produced by `ScmInvoker`, consumed by `SCMRatisServerImpl.submitRequest`, `SCMStateMachine.applyTransaction`, and the test stub.

Risks and test signals: Codec coverage and declared parameter types are compatibility-critical. Tests should cover missing proto fields, subclass parameter resolution, lists, enums, generated messages, and debug string handling for malformed state-machine log entries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMRatisRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMRatisResponse.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMRatisResponse.java

Purpose: Converts local SCM method return values and Ratis client replies into a uniform success/result/exception wrapper for HA proxies.

Important APIs and types: `encode(result, type)` serializes non-null results into `SCMRatisResponseProto`; `decode(RaftClientReply)` returns a success wrapper, empty success for empty messages, or failure wrapper for reply exceptions.

Control flow: Encoding resolves the declared return type through `ScmCodecFactory` and writes type name plus serialized bytes. Decoding first checks `reply.isSuccess`; failed replies keep the exception. Successful non-empty responses validate type and value fields, resolve the class, and deserialize the value.

State and persistence behavior: No persistent state; response messages are transient Ratis replies.

Dependencies and integration points: Used by generated invokers, `SCMRatisServerImpl`, and `SCMHAManagerStub` to bridge method return values across Ratis.

Risks and test signals: Void/null results intentionally become `Message.EMPTY`, so callers must not expect a typed null. Tests should cover exception preservation, empty success, primitive wrapper returns, list returns, and invalid response protos with missing fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMRatisResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMRatisServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMRatisServer.java

Purpose: Abstraction over the SCM Ratis server used by managers and generated proxies to submit replicated requests, manage snapshots, inspect roles, and change membership.

Important APIs and types: Defines `start`, `stop`, `isStopped`, `submitRequest`, `triggerSnapshot`, `registerStateMachineHandler`, `getDivision`, `getRatisRoles`, `triggerNotLeaderException`, `addSCM`, `removeSCM`, `getSCMStateMachine`, `getGrpcTlsConfig`, and `getLeaderId`. Default `getProxyHandler` registers an invoker and returns its proxy.

Control flow: Implementations register `ScmInvoker` handlers before replicated APIs are used. Proxies submit `SCMRatisRequest` values and receive `SCMRatisResponse` values.

State and persistence behavior: State belongs to implementations: Ratis log, state machine, membership, TLS config, and snapshot index.

Dependencies and integration points: Central boundary between SCM services, generated invokers, Ratis, and HA membership commands.

Risks and test signals: `getProxyHandler` registration order is required for local apply success. Tests should cover request submission, not-leader exception content, snapshot trigger result, role rendering, membership reconfiguration, and TLS config propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMRatisServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMRatisServerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMRatisServerImpl.java

Purpose: Production Apache Ratis server wrapper for SCM HA, responsible for server construction, request submission, snapshots, peer roles, and dynamic SCM membership.

Important APIs and types: Constructor builds `RaftServer`, `SCMStateMachine`, `RaftGroupId`, and TLS parameters. Static `initialize`, `buildRaftGroupId`, `getSelfPeerId`, and `buildRaftGroup` support SCM init/bootstrap. Runtime APIs include `submitRequest`, `triggerSnapshot`, `addSCM`, `removeSCM`, `getLeader`, `getRatisRoles`, and `triggerNotLeaderException`.

Control flow: Server creation uses the cluster UUID as Raft group id and starts with group id only in bootstrapped mode. `submitRequest` builds a write `RaftClientRequest`, waits with configured timeout, and decodes the reply. Membership changes submit `SetConfigurationRequest` with an updated peer list. Initialization starts a temporary server and waits for leader readiness.

State and persistence behavior: Ratis persists logs and state machine snapshots under configured storage. The implementation tracks client id, monotonically increasing call id, stop state, request timeout, division, and TLS config.

Dependencies and integration points: Integrates `RatisUtil`, `HASecurityUtils`, `StorageContainerManager`, `SCMStateMachine`, SCM node details, and Ratis server APIs.

Risks and test signals: Request timeout is read from a local `OzoneConfiguration` field rather than the passed config, which is worth regression coverage. Hostname strings are intentionally not pre-resolved for peer addresses. Tests should assert group-id derivation, DNS-preserving peer address, timeout validation, setConfiguration error propagation, role formatting, and server close/state-machine close sequencing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMRatisServerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMService.java

Purpose: Common lifecycle and status-notification interface for SCM background services such as replication, block deletion, pipeline creation, and HA transaction monitoring.

Important APIs and types: Methods include `notifyStatusChanged`, optional `notifyEventTriggered`, `shouldRun`, `getServiceName`, `start`, and `stop`. Nested enums define `ServiceStatus` and one-time `Event` values.

Control flow: `SCMServiceManager` calls notification methods when safe mode, leader status, or other SCM events change. Service implementations use `shouldRun` to decide whether a scheduled iteration should execute.

State and persistence behavior: No persistence in the interface. Implementations may own runtime state and, for `StatefulService`, durable configuration.

Dependencies and integration points: Used throughout SCM service registration and status propagation. It is also the base for `StatefulService`.

Risks and test signals: Event handling is optional by default, so missing overrides can silently ignore new events. Tests should assert service managers notify all registered services, start errors are handled, and `shouldRun` semantics match leader/safe-mode transitions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMServiceException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMServiceException.java

Purpose: Checked exception type used by `SCMService.start` to report service startup failures.

Important APIs and types: Provides the standard constructors: no-arg, message, message-with-cause, and cause-only.

Control flow: `SCMServiceManager.start` catches this exception per service, logs a warning, and continues starting other services.

State and persistence behavior: No state beyond standard `Exception` message/cause fields and no persistence behavior.

Dependencies and integration points: Couples background service implementations to the service manager without forcing unchecked startup failure.

Risks and test signals: Because the manager logs and continues, a service can fail to start without failing SCM startup. Tests should assert that exceptions preserve cause/message and that manager-level startup proceeds to later services after one service throws.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMServiceException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMServiceManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMServiceManager.java

Purpose: Synchronized registry and broadcaster for SCM background services.

Important APIs and types: `register`, `notifyStatusChanged`, `notifyEventTriggered`, `start`, and `stop` operate over an internal `List<SCMService>`.

Control flow: Register validates non-null services and appends them. Notification methods iterate over all services and call the relevant hook. `start` invokes each service, catching `SCMServiceException` and logging warnings. `stop` calls each service's stop method.

State and persistence behavior: Maintains only in-memory service registration order. No persistence.

Dependencies and integration points: Used by `SCMHAManagerImpl` to register the transaction-buffer monitor, by `SCMStateMachine` leadership callbacks, and by other SCM server code that coordinates background services.

Risks and test signals: Coarse synchronization prevents concurrent mutation but means a slow service hook blocks all notifications. `stop` does not catch runtime failures. Tests should cover registration ordering, null rejection, notification fan-out, start exception isolation, and stop invocation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMServiceManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMSnapshotDownloader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMSnapshotDownloader.java

Purpose: Protocol-neutral contract for downloading an SCM DB snapshot from a remote SCM.

Important APIs and types: Extends `Closeable`; `download(Path destination)` returns a `CompletableFuture<Path>` for asynchronous download progress/completion.

Control flow: Implementations, currently the inter-SCM gRPC client path, write snapshot contents to the requested destination and complete the future with the downloaded path.

State and persistence behavior: Persistence is the downloaded snapshot archive/file at the destination path. The interface does not mandate temporary-file or atomic-write semantics.

Dependencies and integration points: Used by `SCMSnapshotProvider` to fetch the leader's RocksDB checkpoint during Ratis install-snapshot catch-up.

Risks and test signals: Callers must close implementations and handle asynchronous failures. Tests should cover future completion, failure propagation, close behavior, destination path correctness, and partial download cleanup in concrete implementations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMSnapshotDownloader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMSnapshotProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMSnapshotProvider.java

Purpose: Downloads the leader SCM's RocksDB checkpoint into the local Ratis snapshot directory and exposes it as a `DBCheckpoint`.

Important APIs and types: Constructor validates SCM Ratis and snapshot directories, builds a peer-node map, and stores `CertificateClient`. `getSCMDBSnapshot` downloads a `.tar` through `InterSCMGrpcClient`, untars it, deletes the archive, and returns `RocksDBCheckpoint`. `setPeerNodesMap` and `getScmSnapshotDir` support tests.

Control flow: For each request, it creates a timestamped snapshot name, looks up leader host and gRPC port, downloads the archive synchronously via `CompletableFuture.get`, extracts to a directory, and wraps that directory.

State and persistence behavior: Writes checkpoint archives and extracted checkpoint directories under the configured SCM Ratis snapshot directory. It does not cache download clients.

Dependencies and integration points: Called by `SCMHAManagerImpl.downloadCheckpointFromLeader` and `SCMStateMachine.notifyInstallSnapshotFromLeader`; uses inter-SCM gRPC and certificate credentials.

Risks and test signals: Peer lookup, host resolution via `getInetAddress().getHostAddress`, directory preconditions, and interruption handling are important. Tests should cover missing directories, unknown leader id, download failure, tar extraction, archive deletion, and returned checkpoint path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMSnapshotProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMStateMachine.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMStateMachine.java

Purpose: Ratis state machine that applies committed SCM HA operations to `StorageContainerManager`, maintains last-applied transaction metadata, handles leadership callbacks, and installs checkpoints from leaders.

Important APIs and types: Extends `BaseStateMachine`; key methods are `registerInvoker`, `applyTransaction`, `notifyInstallSnapshotFromLeader`, `notifyLeaderChanged`, `notifyLeaderReady`, `notifyTermIndexUpdated`, `takeSnapshot`, `pause`, `reinitialize`, and `close`.

Control flow: `applyTransaction` begins transaction-buffer application, decodes `SCMRatisRequest`, invokes the registered `ScmInvoker`, treats nonfatal `SCMException` as client failure, refreshes safe mode when ready, updates transaction info and last-applied index, and terminates on fatal exceptions. Snapshot install asynchronously downloads and verifies a leader checkpoint, stores checkpoint/secret keys, and later `reinitialize` installs it, reinitializes the transaction buffer, sets the last-applied index, restores secret keys, and transitions lifecycle back to running.

State and persistence behavior: Stores invokers, transaction buffer, latest installing checkpoint/secret keys, current leader term, readiness flag, and Ratis storage. Snapshots flush the transaction buffer and persist transaction info.

Dependencies and integration points: Integrates Ratis callbacks with SCM safe mode, service manager, finalization manager, deleted block log, decommission manager, sequence ID generator, metrics, and HA manager checkpoint APIs.

Risks and test signals: Fatal exception handling can terminate SCM. Snapshot install depends on peer address matching and single pending checkpoint state. Tests should cover local apply dispatch, nonfatal/fatal exception behavior, safe-mode refresh, leader step-down/leader-ready notifications, transaction-info updates, snapshot flush semantics, secret-key reinitialize, and close behavior from SCM versus Ratis.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMStateMachine.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SequenceIdGenerator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SequenceIdGenerator.java

Purpose: HA-safe sequence ID allocator for SCM ids such as local id, deleted transaction id, container id, and certificate id.

Important APIs and types: `getNextId`, `invalidateBatch`, `reinitialize`, static upgrade helpers, inner `StateManager`, `StateManagerImpl`, `StateManagerImpl.Builder`, and `Batch`. `StateManager.allocateBatch` is annotated `@Replicate` and proxied through `SequenceIdGeneratorStateManagerInvoker`.

Control flow: `getNextId` locks globally, serves from an in-memory batch when possible, otherwise CAS-replicates the DB last id from expected to next batch end. Failed CAS reloads the last id and retries. Leadership change invalidates unused batch ranges so a new leader allocates after the persisted last id.

State and persistence behavior: Runtime batches track `lastId` and `nextId`. `StateManagerImpl` caches DB last ids in a concurrent map and persists new last ids through `DBTransactionBuffer.addToBuffer`. Upgrade helpers seed sequence ids from existing local-id time, deleted-block transaction table, container table, and certificate tables.

Dependencies and integration points: Used by SCM managers that allocate persistent ids and reinitialized from `SCMMetadataStore` after checkpoint install.

Risks and test signals: Batch invalidation intentionally skips unused ids to preserve monotonicity. Certificate ids allocate one at a time. Tests should cover CAS retry, batch boundaries, leader invalidation, reinitialize clearing cache, upgrade id derivation, root certificate cleanup, and overflow preconditions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SequenceIdGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/StatefulService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/StatefulService.java

Purpose: Abstract base for SCM services that need replicated, RocksDB-backed configuration bytes.

Important APIs and types: Parameterized by protobuf message type `CONF`. Constructor accepts `StatefulServiceStateManager` and a protobuf `Parser<CONF>`. Protected final helpers are `saveConfiguration`, `readConfiguration`, and `deleteConfiguration`; `getServiceName` returns the class simple name.

Control flow: Subclasses call save/read/delete helpers; the manager keys persisted configuration by the service name. Reads return null when no bytes exist and otherwise parse the stored `ByteString`.

State and persistence behavior: Runtime state is service name, state manager, and parser. Durable state is the `statefulServiceConfig` table entry keyed by service name.

Dependencies and integration points: Used by background services that implement `SCMService` and need HA-replicated configuration.

Risks and test signals: Class-simple-name keys can collide after refactors or subclass renames, so compatibility matters. Tests should cover save/read/delete round trips, parse failures, null reads, and that subclass service names are stable.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/StatefulService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/StatefulServiceStateManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/StatefulServiceStateManager.java

Purpose: Replicated state manager API for saving, reading, deleting, and reinitializing `StatefulService` configuration entries.

Important APIs and types: `saveConfiguration` and `deleteConfiguration` are annotated `@Replicate`; `readConfiguration` is local read-only; `reinitialize` swaps in a new `Table<String, ByteString>`. Default `getType` returns `RequestType.STATEFUL_SERVICE_CONFIG`.

Control flow: Proxied implementations submit save/delete through Ratis so all SCMs apply the same table mutations. Reads fetch the local persisted bytes for the service name.

State and persistence behavior: Persists protobuf bytes in the `statefulServiceConfig` column family. Reinitialize points the manager at the table from a newly loaded SCM DB checkpoint.

Dependencies and integration points: Used by `StatefulService` and implemented by `StatefulServiceStateManagerImpl` with an invoker.

Risks and test signals: Save/delete consistency depends on generated invoker mapping and codec support for `ByteString`. Tests should cover replicated save/delete, local read, table swap after checkpoint install, and request type registration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/StatefulServiceStateManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/StatefulServiceStateManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/StatefulServiceStateManagerImpl.java

Purpose: Concrete state manager that stores service configuration bytes in a RocksDB table through the SCM DB transaction buffer and exposes a Ratis proxy.

Important APIs and types: Implements `saveConfiguration`, `readConfiguration`, `deleteConfiguration`, `reinitialize`, and `newBuilder`. Builder requires stateful-service table, transaction buffer, and Ratis server, then returns a proxy from `StatefulServiceStateManagerInvoker`.

Control flow: Save enqueues a table put in the transaction buffer and immediately flushes when the buffer is an `SCMHADBTransactionBuffer`. Read fetches the table value. Delete currently calls `statefulServiceConfig.delete` directly. Reinitialize replaces the table reference.

State and persistence behavior: Owns a mutable table reference plus a transaction buffer. Save is buffered and flushed; delete bypasses the transaction buffer in this implementation, which is an important persistence-path distinction.

Dependencies and integration points: Used by SCM services through `StatefulService`; reloaded by `SCMHAManagerImpl.startServices` after checkpoint install.

Risks and test signals: Direct delete may bypass HA transaction metadata unlike save. Tests should cover builder null validation, save flush behavior, delete replication/local persistence, read after reinitialize, and generated proxy routing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/StatefulServiceStateManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/CertificateStoreInvoker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/CertificateStoreInvoker.java

Purpose: Generated non-reflection invoker/proxy for HA replication of `CertificateStore` operations.

Important APIs and types: `ReplicateMethod` covers `removeAllExpiredCertificates` and `storeValidCertificate(BigInteger, X509Certificate, NodeType)`. `newProxy` delegates read/local methods to the implementation and routes selected writes through Ratis.

Control flow: `storeValidCertificate` uses `invokeReplicateClient`, while `removeAllExpiredCertificates` uses `invokeReplicateDirect`. `invokeLocal` switches on method names, casts arguments, calls the underlying store, and encodes non-void results through `SCMRatisResponse`.

State and persistence behavior: The invoker has no own persistence; it replicates mutations against certificate tables in `SCMMetadataStore`.

Dependencies and integration points: Depends on certificate codecs for `BigInteger` and `X509Certificate`, `NodeType` enum codec, and the shared `ScmInvoker` exception translation path.

Risks and test signals: Generated parameter arrays must match overload arity. `storeValidScmCertificate` is local-only here, so callers must understand its HA semantics elsewhere. Tests should cover replicated valid cert storage, expired certificate removal return list, read-only pass-throughs, and method-not-found failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/CertificateStoreInvoker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/ContainerStateManagerInvoker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/ContainerStateManagerInvoker.java

Purpose: Generated invoker/proxy for `ContainerStateManager` so container lifecycle mutations are applied through SCM Ratis.

Important APIs and types: Replicated methods are `addContainer`, `removeContainer`, `transitionDeletingOrDeletedToTargetState`, `updateContainerInfo`, and `updateContainerStateWithSequenceId`. The local dispatch also supports reads and replica/container helper updates.

Control flow: Proxy methods for replicated mutations call `invokeReplicateDirect`; read queries and in-memory replica updates call the local implementation. `invokeLocal` resolves overloaded `getContainerInfos` cases by argument count/type, casts protobuf IDs and lifecycle enums, and encodes results where needed.

State and persistence behavior: The invoker itself is stateless. It coordinates mutations that update container state tables and in-memory container state in the real manager.

Dependencies and integration points: Uses protobuf container ids/info, lifecycle enums, pipeline ids, replica sets, table reinitialize hooks, and `ScmCodecFactory` support for these types.

Risks and test signals: Overload disambiguation and generated parameter type arrays are fragile. Tests should cover each replicated method, overloaded list queries, invalid lifecycle transitions, reinitialize pass-through, and that non-replicated replica mutations remain local.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/ContainerStateManagerInvoker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/DeletedBlockLogStateManagerInvoker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/DeletedBlockLogStateManagerInvoker.java

Purpose: Generated HA invoker for replicated deleted-block transaction table mutations.

Important APIs and types: `ReplicateMethod` includes overloaded `addTransactionsToDB` and `removeTransactionsFromDB`, with optional `DeletedBlocksTransactionSummary`. Local methods include read-only iterator, `onFlush`, and `reinitialize`.

Control flow: Proxy write methods call `invokeReplicateDirect` with either one or two arguments. `invokeLocal` collapses overloads by checking argument length, applies the mutation to the underlying `DeletedBlockLogStateManager`, and returns `Message.EMPTY` for void paths.

State and persistence behavior: Mutations affect the deleted blocks transaction table and stateful service config table through the underlying manager; `onFlush` lets the local manager react to DB buffer flushes.

Dependencies and integration points: Used by SCM block manager/deleted block log, checkpoint reload, and HA request serialization for `ArrayList` and protobuf summary values.

Risks and test signals: Raw `ArrayList` element typing relies on list codec support and homogeneous elements. Tests should cover both overloads, remove/add replication, iterator pass-through, `onFlush`, and table reinitialize after checkpoint install.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/DeletedBlockLogStateManagerInvoker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/FinalizationStateManagerInvoker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/FinalizationStateManagerInvoker.java

Purpose: Generated invoker for SCM upgrade finalization state so finalization marks and layout-feature completion are replicated through Ratis.

Important APIs and types: Replicated methods are `addFinalizingMark`, `finalizeLayoutFeature(Integer)`, and `removeFinalizingMark`. Local methods include `crossedCheckpoint`, `getFinalizationCheckpoint`, `reinitialize`, and `setUpgradeContext`.

Control flow: Proxy replicated operations call `invokeReplicateDirect`; status/checkpoint queries and context updates call the local implementation. `invokeLocal` switches by method name, casts integer layout feature ids, and encodes boolean or checkpoint results.

State and persistence behavior: Underlying finalization state is stored in SCM metadata, especially the meta table and checkpoint markers. The invoker does not persist directly.

Dependencies and integration points: Used by SCM finalization manager and by `SCMHAManagerImpl.startServices` after DB reload.

Risks and test signals: Finalization is upgrade-sensitive; missing replication can split cluster layout state. Tests should cover all replicated mark transitions, checkpoint reads, reinitialize with new meta table, and exception translation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/FinalizationStateManagerInvoker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/PipelineStateManagerInvoker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/PipelineStateManagerInvoker.java

Purpose: Generated HA invoker/proxy for `PipelineStateManager` pipeline table and lifecycle mutations.

Important APIs and types: Replicated methods are `addPipeline`, `removePipeline`, and `updatePipelineState`. Local dispatch covers container membership in pipelines, query methods, counts, `close`, and `reinitialize`.

Control flow: Proxy write methods submit direct Ratis requests using protobuf pipeline ids/states. Read/query methods call the local implementation. `invokeLocal` handles overloaded `getPipelines` variants and encodes returned `Pipeline`, collection, count, or void responses.

State and persistence behavior: The underlying manager updates the pipeline table and in-memory pipeline state. The invoker has no persistence but defines what crosses the replicated boundary.

Dependencies and integration points: Used by pipeline manager, Ratis state machine, pipeline codecs, and checkpoint reload.

Risks and test signals: Query overload selection and generated parameter arrays are compatibility-sensitive. Tests should cover duplicate/not-found/invalid-state exceptions, replicated add/remove/update, reinitialize table swap, local container membership operations, and list serialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/PipelineStateManagerInvoker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/RootCARotationHandlerInvoker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/RootCARotationHandlerInvoker.java

Purpose: Generated invoker for HA replication of root CA rotation protocol state.

Important APIs and types: Replicated methods are `rotationPrepare`, `rotationPrepareAck`, `rotationCommit`, and `rotationCommitted`. Local operations include `resetRotationPrepareAcks`, `rotationPrepareAcks`, and `setSubCACertId`.

Control flow: Most rotation transitions use `invokeReplicateDirect`; `rotationPrepareAck` uses `invokeReplicateClient`, allowing client-style submission to the current Raft group. Local dispatch casts string ids and returns ack counts when requested.

State and persistence behavior: The invoker does not persist itself; underlying root CA rotation handler tracks sub-CA id and prepare/commit acknowledgements, which must remain consistent across SCMs.

Dependencies and integration points: Integrates SCM security/certificate rotation workflows with `ScmInvoker`, string codecs, and Ratis client/direct submission paths.

Risks and test signals: Rotation is distributed and ordering-sensitive. Tests should cover prepare, ack, commit, committed paths, client/direct routing differences, ack count reset/local query, and not-leader/timeout translation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/RootCARotationHandlerInvoker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/ScmInvoker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/ScmInvoker.java

Purpose: Base class for generated non-reflection SCM HA invokers, providing proxy construction, Ratis request submission, and exception translation.

Important APIs and types: Stores the real implementation, proxy, and `SCMRatisServer`. Exposes `getType`, `getApi`, `getImpl`, `getProxy`, abstract `invokeLocal`, `invokeReplicateDirect`, `invokeReplicateClient`, and `translateException`. Inner `NameAndParameterTypes` supplies method names and declared parameter types.

Control flow: Direct replication submits `SCMRatisRequest` through the local Ratis server. Client replication encodes the request and sends it through `HASecurityUtils.submitScmRequestToRatis`. Both decode `SCMRatisResponse` and translate errors to `SCMException`.

State and persistence behavior: Stateless with respect to DB; it is the replication transport boundary for persistent mutations owned by implementations.

Dependencies and integration points: All generated invokers extend it; `SCMRatisServer.getProxyHandler` registers them with `SCMStateMachine`.

Risks and test signals: Exception mapping controls client-visible error codes for timeout, not-leader, IO, and internal failures. Tests should cover nested `ExecutionException`/`InvocationTargetException`, existing `SCMException` preservation, direct versus client submission, and missing invoker handling in the state machine.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/ScmInvoker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/SecretKeyStateInvoker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/SecretKeyStateInvoker.java

Purpose: Generated invoker/proxy for HA replication of SCM secret-key state updates.

Important APIs and types: `ReplicateMethod` contains `updateKeys(List)`. Proxy read methods `getCurrentKey`, `getKey`, and `getSortedKeys` call the local implementation; `reinitialize` is local; `updateKeys` is replicated direct.

Control flow: Replicated updates are encoded as list arguments and submitted to Ratis. Local dispatch returns managed secret keys or lists through `SCMRatisResponse` when invoked from a committed log entry.

State and persistence behavior: The invoker does not store keys; the underlying `SecretKeyState` tracks current/sorted managed secret keys and is reinitialized after snapshot install.

Dependencies and integration points: Uses `ManagedSecretKey` codec and participates in `SCMStateMachine.reinitialize` when secret keys are fetched from the leader.

Risks and test signals: List serialization assumes all keys share the supported managed-key type. Tests should cover update replication, key lookup pass-through, sorted key list round trip, reinitialize after checkpoint, and error translation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/SecretKeyStateInvoker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/SequenceIdGeneratorStateManagerInvoker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/SequenceIdGeneratorStateManagerInvoker.java

Purpose: Generated HA invoker for `SequenceIdGenerator.StateManager`, replicating sequence-id batch allocation.

Important APIs and types: `ReplicateMethod` includes `allocateBatch(String, Long, Long)`. Proxy methods replicate allocation and locally delegate `getLastId` and `reinitialize`.

Control flow: `allocateBatch` builds a direct Ratis request with sequence id name, expected last id, and new last id. On apply, `invokeLocal` calls the real state manager and encodes the Boolean CAS result.

State and persistence behavior: Persistent sequence-id table updates occur in the underlying state manager through the DB transaction buffer. Local cache reads and table reinitialization are not replicated.

Dependencies and integration points: Used by `SequenceIdGenerator.StateManagerImpl.Builder`; relies on string and long codecs and `RequestType.SEQUENCE_ID` registration.

Risks and test signals: CAS result correctness is central to monotonic id allocation. Tests should cover successful allocation, failed expected-last-id allocation, local last-id read, reinitialize table swap, and null/invalid sequence-id name handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/SequenceIdGeneratorStateManagerInvoker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/StatefulServiceStateManagerInvoker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/StatefulServiceStateManagerInvoker.java

Purpose: Generated HA invoker for replicated `StatefulServiceStateManager` save/delete operations.

Important APIs and types: `ReplicateMethod` includes `deleteConfiguration(String)` and `saveConfiguration(String, ByteString)`. Proxy read and reinitialize paths are local; save/delete use `invokeReplicateDirect`.

Control flow: Proxy save/delete submit direct Ratis requests. Local apply casts service name and protobuf `ByteString`, invokes the real manager, and returns empty responses for void operations. Reads return local bytes.

State and persistence behavior: The invoker has no state beyond its implementation and Ratis server. Underlying manager persists bytes in the `statefulServiceConfig` table.

Dependencies and integration points: Used by `StatefulServiceStateManagerImpl.Builder`, `StatefulService`, and checkpoint reload paths.

Risks and test signals: ByteString codec must distinguish shaded Ratis `ByteString` from non-shaded protobuf `ByteString`. Tests should cover save/read/delete round trip through proxy, reinitialize pass-through, and method-not-found handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/StatefulServiceStateManagerInvoker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/package-info.java

Purpose: Package documentation for generated SCM HA invokers that dispatch method calls without reflection.

Important APIs and types: Declares the `org.apache.hadoop.hdds.scm.ha.invoker` package and documents that it contains SCM HA invoker implementations.

Control flow: No executable control flow.

State and persistence behavior: No state or persistence.

Dependencies and integration points: The package groups generated `ScmInvoker` subclasses used by `SCMRatisServer`, `SCMStateMachine`, and HA-aware SCM managers.

Risks and test signals: No direct tests are needed beyond package compilation and generated invoker coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmBigIntegerCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmBigIntegerCodec.java

Purpose: SCM HA request/response codec for `BigInteger` values, mainly certificate serial numbers.

Important APIs and types: Implements `ScmCodec<BigInteger>` with `serialize` and `deserialize`.

Control flow: Serialization wraps `BigInteger.toByteArray()` in a Ratis shaded `ByteString`. Deserialization creates a new `BigInteger` from the received byte array.

State and persistence behavior: Stateless. The encoded bytes travel in Ratis request/response messages, not directly in RocksDB.

Dependencies and integration points: Registered in `ScmCodecFactory` for certificate-store invocations and any HA method using `BigInteger`.

Risks and test signals: `BigInteger.toByteArray` is signed two's-complement, so byte compatibility depends on Java's standard form. Tests should cover positive, zero, large, and sign-bit-boundary values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmBigIntegerCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmBooleanCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmBooleanCodec.java

Purpose: SCM HA codec for boxed `Boolean` values.

Important APIs and types: Implements `ScmCodec<Boolean>` and uses constant shaded `ByteString` values for `"true"` and `"false"`.

Control flow: Serialization returns the true constant when the object is true, otherwise the false constant. Deserialization compares the input to the true constant and returns `Boolean.TRUE`; every other value returns `Boolean.FALSE`.

State and persistence behavior: Stateless and used only for Ratis message payloads.

Dependencies and integration points: Registered in `ScmCodecFactory`; used when HA methods return or accept Boolean values, such as sequence-id CAS results.

Risks and test signals: Deserialization is permissive: malformed bytes decode to false rather than failing. Tests should cover true/false round trips and decide whether invalid bytes should remain false-compatible.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmBooleanCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmByteStringCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmByteStringCodec.java

Purpose: Pass-through codec for Ratis shaded protobuf `ByteString` values.

Important APIs and types: Implements `ScmCodec<org.apache.ratis.thirdparty.com.google.protobuf.ByteString>`.

Control flow: `serialize` returns the input object; `deserialize` returns the input bytes unchanged.

State and persistence behavior: Stateless. It preserves bytes inside HA request/response payloads without conversion.

Dependencies and integration points: Registered in `ScmCodecFactory` for shaded `ByteString` values. Distinct from `ScmNonShadedByteStringCodec`, which handles `com.google.protobuf.ByteString`.

Risks and test signals: Shaded/non-shaded ByteString confusion is the primary risk. Tests should assert factory resolution picks the correct codec for both classes and that bytes are preserved exactly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmByteStringCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmCodec.java

Purpose: Minimal serialization contract for objects carried in SCM HA Ratis messages.

Important APIs and types: Generic methods `serialize(T object)` and `deserialize(ByteString value)` use Ratis shaded protobuf `ByteString` and can throw shaded `InvalidProtocolBufferException`.

Control flow: Implementations convert a supported Java/protobuf type to bytes and back; `ScmCodecFactory` selects implementations by resolved type.

State and persistence behavior: The interface has no state. Encoded data is persisted indirectly when requests are stored in the Ratis log.

Dependencies and integration points: Used by `SCMRatisRequest`, `SCMRatisResponse`, and all concrete `Scm*Codec` classes.

Risks and test signals: Codec implementations define HA wire compatibility. Tests should assert round trips for every registered type and failure behavior for malformed bytes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmCodecFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmCodecFactory.java

Purpose: Singleton registry that maps SCM HA request/response parameter and return types to serialization codecs and resolves subclasses to supported base types.

Important APIs and types: Registers generated protobuf messages, primitives/wrappers, strings, booleans, `BigInteger`, certificates, shaded and non-shaded `ByteString`, `ManagedSecretKey`, protobuf enums, and `List`. Public methods are `getInstance`, `resolve(String)`, `resolve(Class<?>)`, `getCodec`, and `getClass`. Inner `ClassResolver` handles assignable-type lookup and caches resolutions.

Control flow: Constructor populates exact codecs, then builds a resolver from known types, then adds list codec. Resolution first checks provided exact class names, then cached values, then loads the class and finds an assignable registered base.

State and persistence behavior: Runtime singleton state includes codec maps and class-resolution caches. No direct persistence, but serialized forms become Ratis log payloads.

Dependencies and integration points: Central to `SCMRatisRequest` and `SCMRatisResponse`, generated invokers, and all HA codecs.

Risks and test signals: Adding a replicated API parameter requires factory support. List codec assumes homogeneous lists and infers element type from the first element. Tests should cover exact and subclass resolution, unknown classes, unknown codecs, enum mapping, list handling, and shaded/non-shaded protobuf classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmCodecFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmEnumCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmEnumCodec.java

Purpose: Generic SCM HA codec for protobuf-backed enum types implementing `ProtocolMessageEnum`.

Important APIs and types: Constructor accepts enum class and `forNumber` function, validates that every enum constant maps back from its protobuf number, then serializes/deserializes integer wire numbers.

Control flow: Serialization writes `object.getNumber()` through `IntegerCodec`. Deserialization reads an integer, applies `forNumber`, and throws `InvalidProtocolBufferException` if the number is unknown or bytes cannot be decoded.

State and persistence behavior: Holds enum class and lookup function; no persistence except Ratis payload bytes.

Dependencies and integration points: Used by `ScmCodecFactory` for lifecycle events/states, pipeline states, and node types.

Risks and test signals: Unknown enum numbers fail rather than mapping to an unknown value. Tests should cover all registered enum constants, malformed integer bytes, and unknown number rejection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmEnumCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmIntegerCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmIntegerCodec.java

Purpose: SCM HA codec for `Integer` values.

Important APIs and types: Implements `ScmCodec<Integer>` and delegates byte conversion to the shared DB `IntegerCodec`.

Control flow: Serialization wraps the newly allocated integer byte array in a shaded `ByteString`; deserialization reads bytes back through `IntegerCodec`.

State and persistence behavior: Stateless and used for HA message payloads.

Dependencies and integration points: Registered in `ScmCodecFactory`, notably for finalization layout feature ids and integer return values.

Risks and test signals: Compatibility depends on `IntegerCodec`'s stable byte format. Tests should cover min, max, zero, positive, negative, and malformed input behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmIntegerCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmListCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmListCodec.java

Purpose: SCM HA codec for Java `List` arguments and return values.

Important APIs and types: Encodes lists into `SCMRatisProtocol.ListArgument` containing an element type name and repeated serialized element bytes. Uses `ScmCodecFactory.ClassResolver` and element codecs.

Control flow: Serialization rejects non-list objects, uses a special empty-list encoding with `Object` type, otherwise resolves the first element's class and serializes each element with that codec. Deserialization parses `ListArgument`, validates type, resolves the element class, deserializes each element, and returns `ArrayList<Object>`.

State and persistence behavior: Stateless apart from resolver reference; bytes are part of Ratis messages.

Dependencies and integration points: Needed for secret keys, certificate lists, deleted-block transaction lists, and other generated invoker list return values.

Risks and test signals: Empty lists lose concrete element type, and mixed-type lists are unsafe because the first element determines the codec. Tests should cover empty list, homogeneous supported lists, malformed argument bytes, unsupported element classes, and mixed-list failure or documented behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmListCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmLongCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmLongCodec.java

Purpose: SCM HA codec for `Long` values.

Important APIs and types: Implements `ScmCodec<Long>` and delegates to shared DB `LongCodec`.

Control flow: Serialization wraps the `LongCodec` byte array in a shaded `ByteString`; deserialization converts the byte array back to a `Long`.

State and persistence behavior: Stateless, used in Ratis request/response serialization.

Dependencies and integration points: Registered for sequence-id allocation, transaction ids, and other long-valued replicated methods.

Risks and test signals: Stable byte ordering is delegated to `LongCodec`. Tests should cover min, max, zero, positive, negative, and invalid byte arrays.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmLongCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmManagedSecretKeyCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmManagedSecretKeyCodec.java

Purpose: SCM HA codec for `ManagedSecretKey` values used by secret-key replication and checkpoint reinitialization.

Important APIs and types: Serializes with `ManagedSecretKey.toProtobuf()` and deserializes by parsing `SCMSecretKeyProtocolProtos.ManagedSecretKey` followed by `ManagedSecretKey.fromProtobuf`.

Control flow: Serialization wraps the non-shaded protobuf bytes in a shaded Ratis `ByteString`. Deserialization catches non-shaded protobuf parse exceptions and rethrows shaded `InvalidProtocolBufferException`.

State and persistence behavior: Stateless; encoded secret keys are transported in Ratis payloads rather than stored by this codec directly.

Dependencies and integration points: Registered in `ScmCodecFactory`; used by `SecretKeyStateInvoker` and list codec for key lists.

Risks and test signals: Secret key wire compatibility depends on protobuf schema stability. Tests should cover round trips, malformed bytes, list round trips, and preservation of key id/material/metadata fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmManagedSecretKeyCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmNonShadedByteStringCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmNonShadedByteStringCodec.java

Purpose: Bridges non-shaded protobuf `com.google.protobuf.ByteString` values into shaded Ratis `ByteString` HA payloads.

Important APIs and types: Public `ScmCodec<com.google.protobuf.ByteString>` implementation with pass-through byte wrapping between protobuf namespaces.

Control flow: Serialization wraps the non-shaded byte buffer using Ratis shaded `UnsafeByteOperations`. Deserialization wraps the shaded read-only byte buffer using non-shaded protobuf `UnsafeByteOperations`.

State and persistence behavior: Stateless. It preserves bytes for Ratis messages.

Dependencies and integration points: Registered in `ScmCodecFactory` for `StatefulServiceStateManager` configuration bytes.

Risks and test signals: ByteBuffer lifetime and namespace confusion are the main risks. Tests should assert byte equality, factory resolution, and no accidental use of the shaded `ScmByteStringCodec` for non-shaded values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmNonShadedByteStringCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmNonShadedGeneratedMessageCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmNonShadedGeneratedMessageCodec.java

Purpose: Generic codec for non-shaded protobuf `Message` types carried in SCM HA Ratis requests.

Important APIs and types: Parameterized by message type and constructed with a display name plus protobuf `Parser<T>`.

Control flow: Serialization wraps `object.toByteString().asReadOnlyByteBuffer()` in shaded Ratis bytes. Deserialization parses from the shaded byte buffer using the supplied non-shaded parser, converting parse errors to shaded `InvalidProtocolBufferException`.

State and persistence behavior: Holds parser/name only. Encoded message bytes become Ratis request/response payloads.

Dependencies and integration points: Registered by `ScmCodecFactory.putProto` for container, pipeline, deleted-block transaction, and summary protobuf messages.

Risks and test signals: Parser must match the registered class, and schema compatibility matters for Ratis logs. Tests should cover each registered proto type, malformed bytes, and error messages naming the failed proto.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmNonShadedGeneratedMessageCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmStringCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmStringCodec.java

Purpose: SCM HA codec for UTF-8 `String` values.

Important APIs and types: Public `ScmCodec<String>` implementation using `StandardCharsets.UTF_8`.

Control flow: Serialization converts the string to UTF-8 bytes and wraps them in shaded `ByteString`; deserialization builds a new Java string from the byte array using UTF-8.

State and persistence behavior: Stateless and used for Ratis messages.

Dependencies and integration points: Registered in `ScmCodecFactory`; used by sequence id names, service names, root CA rotation ids, and other string parameters.

Risks and test signals: No null handling is provided, so null string arguments would fail before or during serialization. Tests should cover ASCII, non-ASCII, empty strings, and malformed UTF-8 behavior if compatibility requires it.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmStringCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmX509CertificateCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmX509CertificateCodec.java

Purpose: SCM HA codec for `X509Certificate` values, serializing certificates as PEM text.

Important APIs and types: Uses `CertificateCodec.getPEMEncodedString` and `CertificateCodec.getX509Certificate`; implements `ScmCodec<X509Certificate>`.

Control flow: Serialization converts the certificate to a PEM string, encodes UTF-8 bytes, and wraps them in shaded `ByteString`. Deserialization reads UTF-8 PEM text and parses an X.509 certificate. Any exception is converted to shaded `InvalidProtocolBufferException`.

State and persistence behavior: Stateless. HA messages carry PEM bytes; RocksDB certificate persistence uses a separate metadata codec.

Dependencies and integration points: Registered for certificate-store invocations and certificate list responses.

Risks and test signals: PEM formatting and certificate parser behavior define wire compatibility. Tests should cover round trips for generated certs, malformed PEM, serial number preservation, and distinction from metadata `X509CertificateCodec`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmX509CertificateCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/package-info.java

Purpose: Package documentation for SCM HA serialization codecs.

Important APIs and types: Declares `org.apache.hadoop.hdds.scm.ha.io` and states that it contains classes related to SCM HA serialization.

Control flow: No executable control flow.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Groups codecs consumed by `SCMRatisRequest`, `SCMRatisResponse`, and generated HA invokers.

Risks and test signals: Compile/package visibility tests and codec-specific tests provide coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/package-info.java

Purpose: Package documentation for SCM HA classes.

Important APIs and types: Declares the `org.apache.hadoop.hdds.scm.ha` package and documents that it contains classes related to SCM HA.

Control flow: No executable control flow.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Names the package that contains SCM HA manager, Ratis server, state machine, snapshot, service, and sequence-id support.

Risks and test signals: No direct runtime risks; package compilation and package-level documentation generation are sufficient signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/BigIntegerCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/BigIntegerCodec.java

Purpose: RocksDB metadata codec for `BigInteger` keys, used for certificate serial-number tables in `scm.db`.

Important APIs and types: Singleton `Codec<BigInteger>` with `get`, `getTypeClass`, `toPersistedFormat`, `fromPersistedFormat`, and `copyObject`.

Control flow: Persists a `BigInteger` using Java's standard `toByteArray`; restores using the byte-array constructor. `copyObject` returns the same immutable object.

State and persistence behavior: Stateless singleton. Defines durable key format for `validCerts` and `validSCMCerts` column families.

Dependencies and integration points: Referenced by `SCMDBDefinition` certificate table definitions. Separate from HA message `ScmBigIntegerCodec`.

Risks and test signals: Key ordering and sign representation matter for RocksDB scans. Tests should cover positive serials, large serials, sign-bit-boundary values, and compatibility with existing DB data.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/BigIntegerCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/SCMDBDefinition.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/SCMDBDefinition.java

Purpose: Authoritative RocksDB schema definition for SCM metadata database `scm.db`.

Important APIs and types: Defines column families for `deletedBlocks`, `validCerts`, `validSCMCerts`, `pipelines`, `containers`, `scmTransactionInfos`, `sequenceId`, `move`, `meta`, and `statefulServiceConfig`. Singleton `get` returns the definition; `getName` returns `scm.db`; `getLocationConfigKey` returns `OZONE_SCM_DB_DIRS`.

Control flow: Static column-family definitions pair table names with key/value codecs, then build an unmodifiable map consumed by `DBStoreBuilder`.

State and persistence behavior: Defines all persistent SCM RocksDB column families and their key/value encodings, including transaction info for HA snapshots and stateful service config bytes.

Dependencies and integration points: Used by `SCMMetadataStoreImpl`, checkpoint transaction-info reading in `SCMHAManagerImpl`, and any DB tooling that opens SCM metadata.

Risks and test signals: Changing names/codecs is upgrade-sensitive. Tests should assert all expected column families exist, codecs round-trip values, DB location key is stable, and checkpoint readers can locate transaction info.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/SCMDBDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/SCMMetadataStoreImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/SCMMetadataStoreImpl.java

Purpose: RocksDB-backed implementation of `SCMMetadataStore`, opening `scm.db`, initializing typed table handles, and exposing them to SCM managers.

Important APIs and types: Constructor calls `start`; `start` creates the DB store from `SCMDBDefinition`, checks the transient inconsistency marker, initializes all table fields, and populates `tableMap`. Getters expose deleted blocks, certificates, pipelines, containers, transaction info, sequence ids, move table, meta table, stateful service config, batch handler, and raw `DBStore`. `stop` closes the store.

Control flow: Startup is idempotent when `store` is non-null. It derives the metadata directory, terminates if `DB_TRANSIENT_MARKER` exists, opens the store with `DBStoreBuilder`, fetches each table from its column-family definition, and rejects null table references.

State and persistence behavior: Owns the live `DBStore`, typed table handles, and table map. The DB is durable RocksDB state under the configured SCM DB directory.

Dependencies and integration points: Used by nearly every SCM manager, HA checkpoint install/reload, sequence-id upgrades, and finalization.

Risks and test signals: Inconsistent-marker handling terminates the process. Reopen after `stop` depends on `store` nulling and existing table fields being replaced. Tests should cover table initialization, marker termination, stop/restart, null table failure, and all getter references matching `SCMDBDefinition`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/SCMMetadataStoreImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/X509CertificateCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/X509CertificateCodec.java

Purpose: RocksDB metadata codec for `X509Certificate` values stored in SCM certificate tables.

Important APIs and types: Singleton `Codec<X509Certificate>` with codec-buffer support. Methods include `toCodecBuffer`, `fromCodecBuffer`, `toPersistedFormat`, `fromPersistedFormat`, `copyObject`, and `supportCodecBuffer`.

Control flow: Writes certificates as PEM through `CertificateCodec.writePEMEncoded` into a `LengthOutputStream` and codec buffer. Reads parse PEM bytes using `CertificateCodec.readX509Certificate`. Raw byte persistence delegates through heap codec buffers or `ByteArrayInputStream`.

State and persistence behavior: Stateless singleton. Defines durable value format for `validCerts` and `validSCMCerts` tables.

Dependencies and integration points: Used by `SCMDBDefinition` certificate column families and SCM certificate stores. Separate from HA message `ScmX509CertificateCodec`.

Risks and test signals: PEM parser/writer compatibility and codec-buffer lifecycle are important. Tests should cover round trips, malformed PEM, buffer allocation paths, copy identity, and compatibility with existing certificate table entries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/metadata/X509CertificateCodec.java -->
