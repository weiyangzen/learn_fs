# subset-b-000479 Research

Grouped research for Alluxio meta master, metastore, RocksDB-backed metadata, and metrics master files. Each section preserves the source path and is wrapped for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterConfigurationServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterConfigurationServiceHandler.java

## Purpose
`MetaMasterConfigurationServiceHandler` is the gRPC server adapter for meta-master configuration APIs. It translates protobuf requests into `MetaMaster` calls, wraps them through `RpcUtils.call` for uniform logging/error propagation, and caches serialized configuration responses to avoid rebuilding large protobuf payloads when the cluster/path configuration hashes have not changed.

## Important APIs and Types
- Extends `MetaMasterConfigurationServiceGrpc.MetaMasterConfigurationServiceImplBase`.
- Holds `MetaMaster mMetaMaster` plus volatile cached `GetConfigurationPResponse` objects for cluster and path configuration.
- `getConfiguration(GetConfigurationPOptions, StreamObserver<GetConfigurationPResponse>)` returns cluster configs, path configs, or both depending on ignore flags.
- `getConfigHash(...)` returns `ConfigHash` from the meta master.
- `setPathConfiguration(...)` converts string keys into `PropertyKey` and delegates to `MetaMaster.setPathConfiguration`.
- `removePathConfiguration(...)` either removes all path properties or only the supplied keys.
- `updateConfiguration(...)` delegates runtime config changes and returns a per-property boolean status map.

## Control Flow
`getConfiguration` first reads the volatile cached responses, fetches the current `ConfigHash`, then refreshes only the requested part whose cached hash differs. It calls `mMetaMaster.getConfiguration` with the opposite ignore flag set to isolate cluster and path configs, then merges cached protobuf fragments into a response builder. Mutation RPCs perform request normalization inside the `RpcUtils.call` lambda and return default protobuf responses.

## State and Persistence
The handler itself only caches serialized responses in volatile fields. Persistent state lives behind `MetaMaster`, especially cluster configuration, path configuration, and journaled path properties. The cache is invalidated by comparing hashes rather than by explicit mutation hooks, so stale cached objects are safe as long as hashes change on configuration updates.

## Dependencies and Integration Points
This class depends on Alluxio gRPC generated types, `PropertyKey`, `ConfigHash`, `MetaMaster`, and `RpcUtils`. It is installed as part of the meta master gRPC service surface and is used by clients and administrators querying or changing Alluxio configuration.

## Risks and Edge Cases
- Cached cluster/path responses are independent; mixed responses can combine a freshly refreshed side with a cached side, which relies on hash correctness.
- `PropertyKey.fromString` can reject unknown names in `setPathConfiguration`; callers must send valid property keys.
- `removePathConfiguration` treats an empty key list as "remove all", so client-side request construction must be explicit.
- Volatile caching prevents torn references but does not synchronize refresh races; duplicate refresh work is possible but behavior remains deterministic.

## Test Signals
Useful tests should cover cache reuse and refresh by hash, ignore-cluster/ignore-path option combinations, path property set/remove conversions, update status propagation, and RPC exception mapping through `RpcUtils.call`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterConfigurationServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterFactory.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterFactory.java

## Purpose
`MetaMasterFactory` is the master factory responsible for creating the Alluxio meta master. It is a small registry integration class that tells the master framework whether the meta master is enabled, names it, retrieves the already-registered `BlockMaster`, and constructs `DefaultMetaMaster`.

## Important APIs and Types
- Implements `MasterFactory<CoreMasterContext>`.
- `isEnabled()` always returns `true`, making the meta master a core master.
- `getName()` returns `Constants.META_MASTER_NAME`.
- `create(MasterRegistry, CoreMasterContext)` constructs `DefaultMetaMaster(registry.get(BlockMaster.class), context)` and registers it in the supplied `MasterRegistry`.

## Control Flow
The master bootstrap path discovers factories, calls `isEnabled`, then invokes `create`. This factory logs that it is creating the meta master, looks up the block master dependency from the registry, constructs the concrete default implementation, registers it, and returns it.

## State and Persistence
The factory is stateless. Persistence is entirely in the created `DefaultMetaMaster` and its journaled delegates.

## Dependencies and Integration Points
Depends on the master framework (`MasterFactory`, `MasterRegistry`, `CoreMasterContext`), `BlockMaster`, and constants. It is the bridge between service discovery/bootstrap and the meta master implementation.

## Risks and Edge Cases
The factory cannot disable the meta master, so configuration-based disablement is not supported here. Constructor or registry failures propagate during master startup. The factory assumes `BlockMaster` is already available in the registry.

## Test Signals
Tests can validate the factory name, enabled status, `BlockMaster` lookup, concrete type creation, and that the registry receives the created master.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterMasterServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterMasterServiceHandler.java

## Purpose
`MetaMasterMasterServiceHandler` exposes the leader meta-master RPCs used by standby masters. It handles standby master ID allocation, registration, and periodic heartbeat commands.

## Important APIs and Types
- Extends `MetaMasterMasterServiceGrpc.MetaMasterMasterServiceImplBase`.
- Holds `MetaMaster mMetaMaster`.
- `getMasterId(GetMasterIdPRequest, StreamObserver<GetMasterIdPResponse>)` delegates address-to-ID assignment.
- `registerMaster(RegisterMasterPRequest, StreamObserver<RegisterMasterPResponse>)` registers standby master metadata and configuration.
- `masterHeartbeat(MasterHeartbeatPRequest, StreamObserver<MasterHeartbeatPResponse>)` returns a `MetaCommand`.

## Control Flow
Each RPC is wrapped in `RpcUtils.call`. `getMasterId` extracts a wire `Address`, `registerMaster` passes the master ID and options, and `masterHeartbeat` passes heartbeat options to `mMetaMaster.masterHeartbeat`, placing the resulting command in the response.

## State and Persistence
This handler owns no state. Master identity, liveness, configuration records, and journal metrics are stored in `MetaMaster`/`DefaultMetaMaster` internals.

## Dependencies and Integration Points
It is the server-side counterpart to `RetryHandlingMetaMasterMasterClient` used by standby masters. It integrates with gRPC generated request/response types and Alluxio's meta master HA management.

## Risks and Edge Cases
- Incorrect master IDs or missing registrations are handled by `MetaMaster`; the handler does not prevalidate beyond protobuf parsing.
- Heartbeat errors are surfaced through the RPC wrapper.
- The class is annotated `NotThreadSafe`; the gRPC framework may call handlers concurrently, so thread safety must come from the delegated `MetaMaster` methods.

## Test Signals
Tests should exercise ID assignment, registration option propagation, heartbeat command propagation, and error conversion when the underlying meta master throws.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterMasterServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterProxyServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterProxyServiceHandler.java

## Purpose
`MetaMasterProxyServiceHandler` is the gRPC service adapter for Alluxio proxy heartbeats. It lets proxy processes report liveness and metadata to the meta master.

## Important APIs and Types
- Extends `MetaMasterProxyServiceGrpc.MetaMasterProxyServiceImplBase`.
- Holds `MetaMaster mMetaMaster`.
- `proxyHeartbeat(ProxyHeartbeatPRequest, StreamObserver<ProxyHeartbeatPResponse>)` forwards the whole proxy heartbeat request.

## Control Flow
The single RPC uses `RpcUtils.call`; it delegates the complete `ProxyHeartbeatPRequest` to `mMetaMaster.proxyHeartbeat` and returns an empty response built with `ProxyHeartbeatPResponse.newBuilder().build()`.

## State and Persistence
The handler has no local state. Proxy liveness and metadata are represented in meta-master state, commonly through `ProxyInfo` records.

## Dependencies and Integration Points
The class integrates gRPC proxy service definitions with `MetaMaster`. It is part of cluster monitoring and web/UI status paths that need proxy liveness.

## Risks and Edge Cases
- The handler does no request normalization; malformed or incomplete request fields rely on deeper validation.
- Annotated `NotThreadSafe`; concurrent correctness depends on `MetaMaster.proxyHeartbeat`.

## Test Signals
Test that the complete request is passed through, successful calls return an empty response, and failures are converted by `RpcUtils`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterProxyServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterSync.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterSync.java

## Purpose
`MetaMasterSync` is a heartbeat executor used by standby masters to synchronize with the leader meta master. It registers the standby, sends periodic master heartbeats, and obeys leader commands such as re-registration.

## Important APIs and Types
- Implements `HeartbeatExecutor`.
- Holds the standby `Address`, a `RetryHandlingMetaMasterMasterClient`, and an `AtomicReference<Long>` master ID initialized to `-1`.
- `heartbeat(long)` performs registration if needed, sends heartbeat, and handles `MetaCommand`.
- `close()` closes the retrying meta-master client.

## Control Flow
On each heartbeat, if no ID is assigned, `setIdAndRegister` calls `getId` and `register` with `Configuration.getConfiguration(Scope.MASTER)`. It then calls `mMasterClient.heartbeat`. `handleCommand` ignores `MetaCommand_Nothing`, re-registers for `MetaCommand_Register`, logs `MetaCommand_Unknown`, and throws for unrecognized values. IO failures are logged and force client disconnect so the next heartbeat reconnects.

## State and Persistence
Local state is the assigned standby master ID. Cluster state is maintained on the leader via registration and heartbeat records. No journal writes happen here directly.

## Dependencies and Integration Points
Depends on heartbeat scheduling, Alluxio configuration scoped to `MASTER`, leader RPC client, and `MetaCommand` gRPC enum. It is part of HA standby master lifecycle.

## Risks and Edge Cases
- The class is `NotThreadSafe`; heartbeat scheduling should avoid concurrent `heartbeat` calls.
- A failed command after a heartbeat causes disconnect but keeps the local ID; subsequent command handling may re-register if asked.
- Unknown commands are logged without re-registration, while default enum cases throw.

## Test Signals
Tests should simulate first heartbeat registration, command-driven re-registration, IO exception disconnects, and close propagation to the client.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterSync.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/PathProperties.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/PathProperties.java

## Purpose
`PathProperties` is the meta master source of truth for path-level configuration properties. It provides thread-safe read/write access, journals all mutations, computes a hash for configuration cache invalidation, and exposes a journaled delegate state object.

## Important APIs and Types
- Implements `DelegatingJournaled`.
- Uses a `ReadWriteLock` to guard `State mState` and `Hash mHash`.
- `snapshot()` returns `PathPropertiesView` with a deep copy, current hash, and last update time.
- `get()` returns a deep copy of all path-to-property maps.
- `add(Supplier<JournalContext>, String, Map<PropertyKey,String>)` merges properties for a path and journals a full path properties entry.
- `remove(..., Set<String>)` removes selected keys and journals either an updated full path entry or a remove entry.
- `removeAll(...)` removes all properties for a path.
- Nested `State implements Journaled` stores `Map<String, Map<String,String>>`, processes journal entries, resets state, and emits checkpoint journal entries.

## Control Flow
Writers acquire the write lock, derive a copy of the path's current properties, apply the requested mutation, call `State.applyAndJournal`, and mark the hash outdated. Reads acquire the read lock and return copies. Journal replay enters `State.processJournalEntry`, which applies `PathPropertiesEntry` by replacing a path's full map and `RemovePathPropertiesEntry` by deleting the path.

## State and Persistence
The in-memory state is a nested map keyed by path and property name. Persistence uses Alluxio journal entries with checkpoint name `PATH_PROPERTIES`. The class intentionally journals the complete property set for a path after each path mutation, trading write size for simple replay semantics. The hash is computed from path/key/value strings and tracks last update time.

## Dependencies and Integration Points
Integrates with `MetaMaster` path configuration RPCs, `JournalContext`, `Journaled` checkpoint/replay machinery, `PropertyKey`, and configuration hash consumers such as `MetaMasterConfigurationServiceHandler`.

## Risks and Edge Cases
- The implementation assumes path property operations are not highly concurrent; a single read/write lock may become a bottleneck under heavy mutation.
- `getProperties(path)` returns a copy; write paths must journal the modified copy or changes would be lost.
- The hash supplier streams over map entries; deterministic hashing depends on the `Hash` class handling ordering or on callers tolerating hash changes from map iteration order.
- Empty add maps are ignored; removal of missing paths does not journal.

## Test Signals
Tests should cover add merge/overwrite, selective removal, remove-all, no-op empty mutations, deep-copy isolation, hash update after mutations, journal replay, reset, and checkpoint iterator output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/PathProperties.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/PathPropertiesView.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/PathPropertiesView.java

## Purpose
`PathPropertiesView` is an immutable-style value object returned by `PathProperties.snapshot`. It packages a point-in-time view of path properties with the corresponding hash and last update time.

## Important APIs and Types
- Fields: `Map<String, Map<String,String>> mProperties`, `String mHash`, `long mLastUpdateTime`.
- Constructor accepts the full properties map, hash, and timestamp.
- Getters expose properties, hash, and last update time.

## Control Flow
There is no behavior beyond construction and getters. Snapshot consistency is provided by `PathProperties`, which builds this object under a read lock.

## State and Persistence
This class is not journaled. It carries copied state from `PathProperties`; callers should treat the map as a snapshot payload.

## Dependencies and Integration Points
Used by meta master configuration hash and path configuration response building. It depends only on Java collections.

## Risks and Edge Cases
The class does not defensively copy or wrap its constructor argument. Correct immutability depends on the producer passing a copy and consumers not mutating it unexpectedly.

## Test Signals
Tests are simple value-object checks: getters return constructor values and `PathProperties.snapshot` supplies an isolated map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/PathPropertiesView.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/ProxyInfo.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/ProxyInfo.java

## Purpose
`ProxyInfo` stores liveness and version metadata for an Alluxio proxy process as tracked by the meta master.

## Important APIs and Types
- Fields include immutable `NetAddress mAddress`, last heartbeat time, start time, version, and revision.
- Constructor initializes address and sets last heartbeat to current time.
- Getters expose address, heartbeat time, start time, version, and revision.
- Setters update start time, version, and revision.
- `updateLastHeartbeatTimeMs()` refreshes liveness timestamp via `CommonUtils.getCurrentMs()`.
- `toString()` uses Guava `MoreObjects.toStringHelper`.

## Control Flow
Meta master proxy heartbeat handling creates or updates `ProxyInfo`, sets metadata from heartbeat options, and calls `updateLastHeartbeatTimeMs` on each heartbeat.

## State and Persistence
This is in-memory liveness state. It is not itself journaled in this file.

## Dependencies and Integration Points
Uses wire `NetAddress`, `CommonUtils`, and Guava string helper. Integrated with proxy heartbeat service handling and cluster status reporting.

## Risks and Edge Cases
Annotated `NotThreadSafe`; callers must synchronize or confine updates. Default version/revision are empty strings and start time defaults to zero until reported.

## Test Signals
Tests should verify initial heartbeat timestamp, setters/getters, heartbeat time refresh, and string representation including expected fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/ProxyInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/RetryHandlingMetaMasterMasterClient.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/RetryHandlingMetaMasterMasterClient.java

## Purpose
`RetryHandlingMetaMasterMasterClient` is the standby master's retrying gRPC client for leader meta-master master-service RPCs. It wraps ID allocation, heartbeat, and registration calls with `AbstractMasterClient` retry/reconnect behavior.

## Important APIs and Types
- Extends `AbstractMasterClient`.
- Creates `MetaMasterMasterServiceGrpc.MetaMasterMasterServiceBlockingStub` in `afterConnect`.
- `getRemoteServiceType`, `getServiceName`, and `getServiceVersion` identify the target service.
- `getId(Address)` calls `getMasterId`.
- `heartbeat(long)` sends journal checkpoint metrics when available and returns `MetaCommand`.
- `register(long, List<ConfigProperty>)` sends config, version, revision, start time, and last lose-primacy time when gauges exist.

## Control Flow
Each public RPC uses `retryRPC`, so connection failures are retried according to `AbstractMasterClient` policy. `heartbeat` reads Dropwizard gauges from `MetricsSystem.METRIC_REGISTRY` and conditionally populates `MasterHeartbeatPOptions`. `register` similarly reads start/lose-primacy gauges and includes build metadata from `ProjectConstants`.

## State and Persistence
The client keeps only the current blocking stub. All persisted/cluster state is updated remotely on the leader meta master.

## Dependencies and Integration Points
Used by `MetaMasterSync`. Depends on generated gRPC stubs, `MasterClientContext`, `MetricsSystem`, metric keys, Alluxio constants, and wire addresses.

## Risks and Edge Cases
- Gauge values are cast to `long`; unexpected gauge value types would fail at runtime.
- Missing gauges are tolerated and omitted.
- Thread-safety follows `AbstractMasterClient`; the stub field is replaced after connect.

## Test Signals
Tests should mock the blocking stub/retry layer and verify request payloads, optional metric fields, service identity values, retries on transient failures, and registration metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/RetryHandlingMetaMasterMasterClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/UpdateChecker.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/UpdateChecker.java

## Purpose
`UpdateChecker` is a heartbeat executor that periodically checks for newer Alluxio versions, logs update availability with coarse cluster-size information, and marks the meta master when a newer version is detected.

## Important APIs and Types
- Implements `HeartbeatExecutor`.
- Holds a `MetaMaster` reference.
- `heartbeat(long)` builds additional info including worker count and calls `UpdateCheck.getLatestVersion` with 3-second connect/read/write timeouts.
- `close()` is a no-op.

## Control Flow
On heartbeat, it calls `mMetaMaster.getWorkerAddresses().size()` to report worker count, using `-1` when no workers are known, asks the update checker for the latest version, and compares it with `ProjectConstants.VERSION`. If they differ, it logs an upgrade message and calls `mMetaMaster.setNewerVersionAvailable(true)`. All throwables are caught and logged at debug level.

## State and Persistence
No local persistent state. It performs outbound version-check IO, logging, and updates the meta master's in-memory newer-version flag.

## Dependencies and Integration Points
Depends on `HeartbeatExecutor`, `ProjectConstants`, `MetaMaster`, and `alluxio.check.UpdateCheck`. It is scheduled by meta master maintenance when update checking is enabled.

## Risks and Edge Cases
- Network and unexpected failures are intentionally non-fatal and only debug logged.
- The class is `NotThreadSafe`; scheduler should not invoke concurrently.
- Version-check behavior depends on external service availability and privacy policy around reported info.
- A null or unexpected latest-version value would compare unequal to the current version and set the newer-version flag.

## Test Signals
Tests can mock `MetaMaster`/update-check utility to verify worker count formatting, `-1` for no workers, newer-version flag updates, logging on version mismatch, and swallowed throwables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/UpdateChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/checkconf/ConfigRecord.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/checkconf/ConfigRecord.java

## Purpose
`ConfigRecord` is a small mutable data holder for one reported configuration property from a master or worker. It records the `PropertyKey`, source, and optional value.

## Important APIs and Types
- Fields: `PropertyKey mKey`, `String mSource`, `Optional<String> mValue`.
- Has a no-arg constructor for fluent population and a full constructor.
- Getters return key, source, and optional value.
- Fluent setters return `this` for stream mapping in `ConfigurationStore`.

## Control Flow
There is no complex control flow. `setValue` and the full constructor wrap nullable values with `Optional.ofNullable`.

## State and Persistence
State is in-memory and lives inside `ConfigurationStore`. It is not journaled here.

## Dependencies and Integration Points
Used by `ConfigurationStore` and `ConfigurationChecker` to compare effective server-side configuration values across nodes.

## Risks and Edge Cases
The no-arg constructor allows partially initialized records. Callers must set key/source/value before records are consumed by `ConfigurationChecker`.

## Test Signals
Tests should cover nullable value handling, fluent setter chaining, and getter correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/checkconf/ConfigRecord.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/checkconf/ConfigurationChecker.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/checkconf/ConfigurationChecker.java

## Purpose
`ConfigurationChecker` compares server-side configuration reported by masters and workers, classifies inconsistencies as warnings or errors according to each `PropertyKey` consistency level, and exposes a cached `ConfigCheckReport`.

## Important APIs and Types
- Holds master and worker `ConfigurationStore` instances.
- Maintains `ConfigCheckReport mConfigCheckReport` and volatile dirty flag.
- Registers change listeners on both stores to set the dirty flag.
- `getConfigCheckReport()` lazily regenerates when dirty.
- `regenerateReport()` builds maps of `PropertyKey -> Optional<value> -> node addresses`.
- `logConfigReport()` logs status-specific summaries, limiting output volume.

## Control Flow
When stores change, the dirty flag is set. On `getConfigCheckReport`, the method clears the dirty flag before regeneration so concurrent changes during regeneration cause a later refresh. Regeneration merges live master and worker configs, skips keys with `ConsistencyCheckLevel.IGNORE`, treats keys with multiple distinct values as inconsistent, maps `Scope.ALL` to `Scope.SERVER`, and chooses status `FAILED`, `WARN`, or `PASSED`.

## State and Persistence
The checker keeps an in-memory cached report. Configuration inputs come from `ConfigurationStore`; no journal persistence is performed here.

## Dependencies and Integration Points
Depends on `PropertyKey`, `Scope`, `ConfigStatus`, `ConfigCheckReport`, and `InconsistentProperty`. It feeds web UI and `fsadmin doctor` style diagnostics through the meta master.

## Risks and Edge Cases
- `logConfigReport` compares against the previous report status before replacing it; transitions are logged, but unchanged bad states are not repeatedly logged.
- Address strings use host:rpcPort, so duplicate addresses would collapse at store level.
- Unknown/unregistered keys can still participate if their `PropertyKey` consistency level is not ignore.
- All public methods are synchronized; report generation can block concurrent readers.

## Test Signals
Tests should cover passed/warn/failed status derivation, ignore-level filtering, `Scope.ALL` remapping, dirty flag lazy regeneration, limited logging, and live-node filtering through stores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/checkconf/ConfigurationChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/checkconf/ConfigurationStore.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/checkconf/ConfigurationStore.java

## Purpose
`ConfigurationStore` records reported configuration for a class of nodes and tracks which registered nodes are currently lost. It provides live-node configuration snapshots for consistency checking.

## Important APIs and Types
- `Map<Address, List<ConfigRecord>> mConfMap` stores node configs.
- `Set<Address> mLostNodes` filters out lost nodes.
- `List<Runnable> mChangeListeners` notifies checkers.
- `registerNewConf(Address, List<ConfigProperty>)` converts gRPC config properties to `ConfigRecord`s.
- `handleNodeLost`, `lostNodeFound`, and `handleNodeDelete` update liveness/deletion state.
- `getConfMap()` returns a copy containing only non-lost nodes.
- `getLiveNodeAddresses()` returns non-lost known addresses.
- `registerChangeListener(Runnable)` installs dirty callbacks.

## Control Flow
All mutating and read methods are synchronized. Registering new config validates inputs, converts property names with `toPropertyKey`, stores the records, removes the node from lost state, then runs listeners. Unknown property names are converted into unregistered `PropertyKey` instances so mixed-version or UFS-specific worker configs can still be represented.

## State and Persistence
State is in-memory; it reflects currently known node reports and lost-node flags. It is not journaled in this class.

## Dependencies and Integration Points
Used by `ConfigurationChecker` for master and worker stores. Integrates with gRPC `ConfigProperty`, wire `Address`, and `PropertyKey` registry.

## Risks and Edge Cases
- `getConfMap` creates a new map but reuses the `List<ConfigRecord>` instances, so consumers should not mutate lists or records.
- `reset` does not run change listeners, so callers expecting dirty reports after reset must handle that externally.
- Listener callbacks run while holding the store monitor; expensive callbacks could block store updates.

## Test Signals
Tests should cover unknown property conversion, live/lost/delete transitions, listener invocation, filtering of lost nodes, and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/checkconf/ConfigurationStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/BlockMetaStore.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/BlockMetaStore.java

## Purpose
`BlockMetaStore` defines the master-side storage contract for block metadata and block locations. It abstracts heap and RocksDB implementations used by the block master.

## Important APIs and Types
- `getBlock`, `putBlock`, and `removeBlock` manage `BlockMeta` by block ID.
- `getLocations`, `addLocation`, and `removeLocation` manage `BlockLocation` entries by block ID and worker ID.
- `clear`, `close`, and `size` provide lifecycle and accounting operations.
- `getCloseableIterator()` returns a closeable iterator over `Block` objects and explicitly documents that callers must close it.
- Nested `Block` holds an ID and `BlockMeta`.
- Nested `Factory extends Supplier<BlockMetaStore>`.

## Control Flow
The interface imposes no implementation flow, but the contract expects block metadata operations and location operations to be available independently. Iteration clients use try-with-resources to avoid leaking backend resources.

## State and Persistence
State is implementation-specific. `HeapBlockMetaStore` keeps concurrent maps in memory; `RocksBlockMetaStore` persists in RocksDB column families and supports checkpointing through `RocksCheckpointed`.

## Dependencies and Integration Points
Uses protobuf `BlockMeta`/`BlockLocation` and `CloseableIterator`. It is consumed by block master metadata management, block integrity scans, and journal/checkpoint dumping.

## Risks and Edge Cases
- Interface does not require atomic coupling between block metadata and locations; callers must handle consistency.
- `removeBlock` contract says nothing about clearing locations; implementation behavior differs and callers must know whether orphaned locations are possible.
- Iterator leaks are explicitly called out as a risk.

## Test Signals
Shared implementation tests should cover put/update/remove, no-op removals, duplicate location add behavior, location removal by worker, clear/size, and iterator closure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/BlockMetaStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/DelegatingReadOnlyInodeStore.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/DelegatingReadOnlyInodeStore.java

## Purpose
`DelegatingReadOnlyInodeStore` is a forwarding wrapper for read-only access to an underlying mutable `InodeStore`. It lets callers expose only the `ReadOnlyInodeStore` surface while delegating all reads to the underlying store.

## Important APIs and Types
- Implements `ReadOnlyInodeStore`.
- Holds `InodeStore mDelegate` supplied by the constructor.
- Forwards inode lookup, child ID lookup/listing, child lookup, `hasChildren`, `allEdges`, `allInodes`, and `close`.

## Control Flow
Every method is a thin pass-through to the delegate. The wrapper does not expose write APIs even though the delegate is mutable.

## State and Persistence
The class owns no durable metadata. State and persistence live in the delegated store.

## Dependencies and Integration Points
Sits between callers needing a `ReadOnlyInodeStore` and concrete mutable stores such as heap, Rocks, or cache-backed stores. It depends on inode metadata types and `ReadOption`.

## Risks and Edge Cases
- Correctness depends on the delegate being non-null and having the intended lifecycle; the constructor does not perform a null check.
- Closing the wrapper closes the delegate; wrapper owners must avoid double-close surprises if the delegate is shared.

## Test Signals
Tests should use a fake delegate to verify every method forwards arguments and return values, including close and testing-only set accessors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/DelegatingReadOnlyInodeStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/InodeStore.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/InodeStore.java

## Purpose
`InodeStore` defines the mutable metadata store contract for filesystem inodes and parent-child edges. It extends read-only access with write, remove, checkpoint, and optional batch-write APIs.

## Important APIs and Types
- Extends `ReadOnlyInodeStore`, `Checkpointed`, and `Closeable`.
- `getMutable(long, ReadOption)` returns mutable inode metadata; default `get` wraps it as immutable `Inode`.
- `remove`, `writeInode`, `writeNewInode`, `clear` mutate inode entries.
- `addChild` and `removeChild` mutate parent-child edge entries.
- `supportsBatchWrite`/`createWriteBatch` expose optional batched writes.
- `getInodePathString` traverses parent links for corruption diagnostics.
- Nested `WriteBatch` supports inode and edge operations plus `commit`.
- Nested `Factory` maps an `InodeLockManager` to an `InodeStore`.

## Control Flow
The interface documents required external locking: inode mutations require inode locks and edge mutations require edge locks. Default methods implement convenience wrappers, combined inode-and-edge removal, and debug parent traversal capped at 100 iterations.

## State and Persistence
Actual state is implementation-specific. Checkpointing is required by the interface. Write batches may or may not be atomic depending on the implementation.

## Dependencies and Integration Points
Core dependency for `InodeTree`/file master metadata. Integrates with `InodeLockManager`, `MutableInode`, `InodeView`, `Checkpointed`, and read-only traversal APIs.

## Risks and Edge Cases
- Violating the external lock contract can race with asynchronous cache flush or concurrent store updates.
- `writeInode` semantics are implementation-dependent; the heap implementation currently uses `putIfAbsent`, while Rocks overwrites.
- `removeInodeAndParentEdge` is not atomic unless the implementation/caller provides atomicity.
- Batch write atomicity is explicitly not guaranteed by the interface.

## Test Signals
Contract tests should validate lock-sensitive mutation behavior, child edge consistency, `writeNewInode` optimizations, batch-write support flags, checkpoint round-trips, and debug traversal on malformed parent chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/InodeStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/ReadOnlyInodeStore.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/ReadOnlyInodeStore.java

## Purpose
`ReadOnlyInodeStore` defines read and traversal operations for inode metadata. It provides default implementations for child iteration and descendant traversal, including closeable/skippable iterators that interact with inode path locks.

## Important APIs and Types
- `get(long, ReadOption)` fetches an inode.
- `getChildIds`, `getChildId`, `getChild`, `getChildren`, and prefix/from variants provide directory listing primitives.
- `getSkippableChildrenIterator(ReadOption, DescendantType, boolean, LockedInodePath)` returns iterators for base-only, one-level, or recursive traversal.
- `hasChildren` checks directory children.
- `allEdges` and `allInodes` are testing/debug accessors.

## Control Flow
Default `getChildren` maps child IDs to inodes and skips missing inode metadata to tolerate weakly consistent concurrent modifications. `getSkippableChildrenIterator` handles missing base paths with an empty iterator, `DescendantType.ALL` with `RecursiveInodeIterator`, `DescendantType.NONE` with a single base result, and one-level traversal by locking each child path as it is returned. The one-level iterator closes the previously locked path before advancing.

## State and Persistence
The interface owns no state. Traversal state lives in iterator objects and locked paths; persistence is implementation-specific.

## Dependencies and Integration Points
Uses `LockedInodePath`, `InodeTree.LockPattern`, `DescendantType`, `CloseableIterator`, and inode view/result types. It is a central read abstraction for file-master path resolution, listing, and recursive operations.

## Risks and Edge Cases
- Iterators are weakly consistent under concurrent mutation; callers must tolerate skipped removed inodes and uncertain inclusion of new ones.
- Iterator close discipline is important because traversal can hold inode path locks.
- One-level traversal uses `WRITE_EDGE` locking, so incorrect caller lock ordering can deadlock elsewhere.
- Empty iterator for missing base path hides `FileDoesNotExistException` by design.

## Test Signals
Tests should cover default child iteration skipping missing inodes, prefix/from listing, all descendant modes, close releasing locked paths, `skipChildrenOfTheCurrent`, and behavior when base path disappears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/ReadOnlyInodeStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/ReadOption.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/ReadOption.java

## Purpose
`ReadOption` carries read modifiers for inode-store operations: whether to bypass caches, where ordered directory listing should start, and what child-name prefix to filter.

## Important APIs and Types
- Immutable fields: `mSkipCache`, `mStartFrom`, `mPrefix`.
- Static `defaults()` returns the default no-skip/no-range option.
- `newBuilder()` creates a builder with setters for skip cache, start-from, and prefix.
- Getters expose nullable start/prefix values.

## Control Flow
Callers build options and pass them into inode store methods. Heap and Rocks implementations use `startFrom`/`prefix` to seek sorted child maps or RocksDB key ranges. Cache implementations use `shouldSkipCache` to bypass population.

## State and Persistence
No persistence; this is an immutable request object once built.

## Dependencies and Integration Points
Used throughout `ReadOnlyInodeStore`, `Cache`, `CachingInodeStore`, `HeapInodeStore`, and `RocksInodeStore`.

## Risks and Edge Cases
- `startFrom` and `prefix` are nullable; implementations must handle all combinations consistently.
- `skipCache` may still return a cached value if it is already present in the generic cache path's skip-cache implementation.

## Test Signals
Tests should cover builder defaults, each setter, nullable fields, and consistent prefix/start behavior across heap and Rocks stores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/ReadOption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/RecursiveInodeIterator.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/RecursiveInodeIterator.java

## Purpose
`RecursiveInodeIterator` implements depth-first recursive traversal over inode metadata while managing `LockedInodePath` lifetimes. It supports skipping children of the current inode and resuming from a `ReadOption.startFrom` path component sequence.

## Important APIs and Types
- Implements `SkippableInodeIterator`.
- Holds a stack of child iterators paired with locked paths.
- Tracks current name components, optional `startAfter` components, the root path, the first/base inode, and whether the current inode is a directory.
- `skipChildrenOfTheCurrent()` pops the current directory iterator when the last returned inode was a directory.
- `hasNext()` computes and caches availability.
- `next()` returns `InodeIterationResult`.
- `close()` closes all stacked iterators/paths.

## Control Flow
The iterator starts with the base inode when requested, then lists directory children in sorted order. For each directory child, it locks the child path and pushes a new iterator for its children. It closes the previous locked path when advancing away. `populateStartAfter` uses the configured start path components to seek into child listings and skip earlier subtrees. `tryOnIterator` wraps iterator operations and converts checked close failures.

## State and Persistence
Traversal state is in-memory and lock-bearing. No metadata persistence occurs.

## Dependencies and Integration Points
Used by `ReadOnlyInodeStore.getSkippableChildrenIterator` for `DescendantType.ALL`. Depends on `LockedInodePath`, `InodeTree` lock patterns, `ReadOption`, and `CloseableIterator`.

## Risks and Edge Cases
- Close order is critical; leaked iterators can leak locks.
- Recursive traversal under concurrent mutation is weakly consistent and must handle disappeared children.
- `skipChildrenOfTheCurrent` only affects the current inode when it was a directory.
- Start-after path handling depends on sorted child iteration semantics from the backing store.

## Test Signals
Tests should cover depth-first order, include/exclude base, start-from resume, prefix interactions through `ReadOption`, skip-children behavior, close on partial traversal, and concurrent missing child handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/RecursiveInodeIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/SkippableInodeIterator.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/SkippableInodeIterator.java

## Purpose
`SkippableInodeIterator` is the closeable iterator interface for inode traversal that can prune descendants of the current inode.

## Important APIs and Types
- Extends Java `Iterator<InodeIterationResult>` and `Closeable`.
- Adds default `skipChildrenOfTheCurrent()` that throws `UnsupportedOperationException`.

## Control Flow
Consumers call `next()` to receive an inode plus its locked path, and may call an implementation-supported `skipChildrenOfTheCurrent` before the next advance to avoid traversing the current inode's children.

## State and Persistence
No state in the interface. Implementations carry traversal and lock state.

## Dependencies and Integration Points
Implemented by `RecursiveInodeIterator` and anonymous iterators in `ReadOnlyInodeStore`. Used by recursive file-master operations that may prune subtrees.

## Risks and Edge Cases
Semantics depend on implementation: unsupported implementations inherit the throwing default, base-only and one-level anonymous iterators override skip as a no-op, and recursive traversal prunes directories.

## Test Signals
Interface-level tests should exercise the default throwing behavior plus concrete implementations for skip behavior and close discipline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/SkippableInodeIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/caching/Cache.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/caching/Cache.java

## Purpose
`Cache` is a generic write-back cache for metastore entries. It supports concurrent per-key access, lazy loading from a backing store, asynchronous eviction to a backing store, metrics, and optional cache bypass reads.

## Important APIs and Types
- Abstract `Cache<K,V>` implements `Closeable`.
- Configured by `CacheConfiguration` max size, high/low watermarks, and eviction batch size.
- `get(K, ReadOption)` loads on misses unless skip-cache or full-cache behavior bypasses population.
- `put`, `putNewEntry`, and `remove` update cached dirty entries.
- `flush()` writes all dirty entries to backing store without evicting them.
- `clear()` clears in-memory entries and invokes callbacks.
- Abstract hooks: `load`, `writeToBackingStore`, `removeFromBackingStore`, `flushEntries`.
- Callback hooks: `onCacheUpdate`, `onCacheRemove`, `onPut`, `onRemove`.
- Inner `EvictionThread` performs CLOCK-like eviction; inner `Entry` stores key, nullable value, dirty bit, and referenced bit.

## Control Flow
Reads first honor skip-cache or full-cache bypass. Normal reads use `ConcurrentHashMap.compute` to serialize per-key loads and mark hits as referenced. Writes use `compute` to invoke callbacks atomically with cache changes; if a new entry arrives while the cache is full, it synchronously writes through and does not cache. Removes store a dirty tombstone (`mValue == null`) so eviction can delete from backing storage. The eviction thread starts lazily when the high watermark is reached, scans entries, clears referenced bits on first pass, flushes dirty candidates, then removes clean unreferenced entries until the low watermark target is met.

## State and Persistence
State is the concurrent map plus eviction thread. Persistence is delegated to subclasses. Dirty entries must be flushed before eviction or checkpoint. Metrics record hits, misses, load times, evictions, and size gauges.

## Dependencies and Integration Points
Used by `CachingInodeStore` for inode and edge caches. Integrates with `ReadOption`, `MetricKey`, `MetricsSystem`, and `StatsCounter`.

## Risks and Edge Cases
- Subclasses must set `entry.mDirty = false` after successful `flushEntries`; otherwise entries cannot be evicted.
- `clear()` is explicitly not threadsafe and requires external synchronization.
- Eviction callbacks and backing writes run in the eviction thread, so slow backing stores can cause the cache to fill and force synchronous writes.
- Tombstone semantics require subclasses to handle null values carefully.
- `close()` interrupts and joins the eviction thread but does not itself flush dirty entries.

## Test Signals
Tests should cover single-flight miss loading, skip-cache reads, write-through when full, dirty tombstone removal, eviction watermarks and referenced bit behavior, flush clearing dirty bits through subclass behavior, metrics counters, and close interruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/caching/Cache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/caching/CacheConfiguration.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/caching/CacheConfiguration.java

## Purpose
`CacheConfiguration` is an immutable configuration object for metastore caches. It packages max size, high/low eviction watermarks, and eviction batch size.

## Important APIs and Types
- Fields: max size, high watermark, low watermark, eviction batch size.
- Static `newBuilder()` returns `Builder`.
- Builder setters configure each integer and `build()` creates the configuration.

## Control Flow
`CachingInodeStore` computes values from Alluxio configuration and builds one shared `CacheConfiguration` for inode, edge, and listing caches.

## State and Persistence
No persistence. Values are immutable after construction.

## Dependencies and Integration Points
Consumed by `Cache` and `CachingInodeStore.ListingCache`.

## Risks and Edge Cases
The class itself does not validate ratios or ordering; callers such as `CachingInodeStore` must ensure positive max size and low <= high.

## Test Signals
Tests should cover builder defaults if any, setters, getter values, and validation at the caller level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/caching/CacheConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/caching/CachingInodeStore.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/caching/CachingInodeStore.java

## Purpose
`CachingInodeStore` is a write-back, heap-cached `InodeStore` wrapper over another `InodeStore` backing store. It caches inode records, parent-child edges, and complete directory listings to reduce slow backing-store access while preserving checkpointability.

## Important APIs and Types
- Implements `InodeStore` and `Closeable`.
- Holds backing `InodeStore`, `InodeLockManager`, `InodeCache`, `EdgeCache`, `ListingCache`, and `mBackingStoreEmpty`.
- Public store methods delegate to caches for inode/edge reads and writes.
- Checkpoint methods flush inode and edge caches before delegating to the backing store.
- `InodeCache extends Cache<Long, MutableInode<?>>`.
- `EdgeCache extends Cache<Edge, Long>` and maintains parent-to-child index plus unflushed deletes.
- `ListingCache` is a weighted complete-listing cache, not a source of truth.

## Control Flow
Construction validates cache size/watermark configuration, creates the three caches, and registers heap-size metrics. Inode writes go to `InodeCache`; new directory writes prime an empty listing. Edge writes go to `EdgeCache`, which updates `ListingCache` through callbacks. Reads first consult caches and load from backing store as needed. `hasChildren` uses cached listings when available, otherwise queries merged edge/backing data.

`InodeCache.flushEntries` and `EdgeCache.flushEntries` try to acquire inode or edge write locks before writing/removing from the backing store, optionally using backing-store write batches. Entries whose locks cannot be acquired remain dirty for later. `EdgeCache.getChildIds` merges cache entries, unflushed deletes, and backing-store child IDs to provide consistency despite asynchronous eviction. `ListingCache.getChildIds` creates a loading placeholder, computes complete listings from `EdgeCache`, and caches them only if no concurrent modification was observed.

## State and Persistence
The authoritative recent state is the cache plus backing store. Dirty cache entries represent updates not yet persisted to the backing store. Checkpointing flushes dirty inode and edge entries, then checkpoints the backing store. Restore clears caches, restores backing store, and marks `mBackingStoreEmpty=false`.

## Dependencies and Integration Points
Integrates `InodeStore`, `InodeLockManager`, lock resources, `ReadOption`, metrics, object-size calculation, `HeapInodeStore.sortedMapToIterator`, and optional backing-store batch writes. It is used when the master metastore is configured for caching over RocksDB or another persistent store.

## Risks and Edge Cases
- The external lock contract is essential; cache eviction serializes mutable inodes under inode/edge locks.
- `clear()` clears inode and edge caches and backing store but does not clear listing cache in the public method, leaving potential stale listing entries unless callers reset the whole store lifecycle.
- `close()` registers backing store before caches with `Closer`, relying on reverse close order so cache eviction threads close before the backing store.
- `mBackingStoreEmpty` is an optimization; once false, it never becomes true except new instance creation.
- Listing cache weight must stay accurate across concurrent add/remove/evict paths.
- Skipping cache can still merge with cached edge state to preserve unflushed updates.

## Test Signals
Tests should cover cache hits/misses, dirty flush with lock acquisition failure and retry, backing-store-empty fast paths, edge merge with unflushed deletes, listing cache concurrent modification invalidation, checkpoint flush delegation, restore clearing caches, batch write usage, close ordering, and index verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/caching/CachingInodeStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/caching/StatsCounter.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/caching/StatsCounter.java

## Purpose
`StatsCounter` centralizes counter-based cache metrics accounting for metastore caches.

## Important APIs and Types
- Package-private final class constructed with metric keys for evictions, hits, load times, and misses.
- Records hits, misses, evictions, and aggregate load duration against `MetricsSystem` counters.
- Registers the global `MASTER_INODE_CACHE_HIT_RATIO` gauge from hit and miss counters.

## Control Flow
Cache implementations call `recordHit`, `recordMiss`, `recordLoad`, and `recordEvictions` at read, load, and eviction points. The class maps those calls to configured counters and exposes hit ratio as hits divided by hits plus misses.

## State and Persistence
No metadata persistence. Metrics are accumulated in the global metrics registry counters/gauge.

## Dependencies and Integration Points
Used by `Cache` and `ListingCache`. Depends on `MetricKey`, `MetricsSystem`, and Dropwizard `Counter`.

## Risks and Edge Cases
Incorrect metric key wiring can report cache activity under the wrong name. Recording is side-effect-only and should remain lightweight because it runs on hot read/write paths. The hit-ratio gauge can compute `0 / 0` before any access, producing a non-finite value depending on metric consumer behavior.

## Test Signals
Tests should validate each record method increments the expected counter, load times accumulate as nanoseconds, evictions add counts, and the hit-ratio gauge behavior before and after hits/misses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/caching/StatsCounter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/heap/HeapBlockMetaStore.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/heap/HeapBlockMetaStore.java

## Purpose
`HeapBlockMetaStore` is the in-memory `BlockMetaStore` implementation backed by concurrent maps. It is suitable when block metadata is kept on heap rather than in RocksDB.

## Important APIs and Types
- `mBlocks` maps block ID to `BlockMeta`.
- `mBlockLocations` is a two-key concurrent map from block ID and worker ID to `BlockLocation`.
- Implements all `BlockMetaStore` methods.
- Constructor optionally registers heap-size metrics.

## Control Flow
Block meta operations read/write/remove `mBlocks`. Location operations update `mBlockLocations` by block ID and worker ID. `getCloseableIterator` wraps the concurrent map entry iterator in a no-op-close `CloseableIterator`. `clear()` clears only `mBlocks`.

## State and Persistence
State is process-local heap memory. The class itself does not checkpoint. The block master journal/checkpoint layer must reconstruct state if needed.

## Dependencies and Integration Points
Uses `TwoKeyConcurrentMap`, protobuf block types, `MetricsSystem`, and object-size calculator. It implements the block metadata abstraction used by the block master.

## Risks and Edge Cases
- Class comment requires external synchronization for same-block operations.
- `clear()` clears block metadata but not `mBlockLocations`, which can leave stale location entries if callers expect full store reset.
- `removeBlock` also does not remove locations.
- Iterator is weakly consistent due to `ConcurrentHashMap`.

## Test Signals
Tests should cover block put/update/remove/size, location add/idempotence/remove, stale locations after block removal/clear expectations, iterator contents, and heap metric registration when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/heap/HeapBlockMetaStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/heap/HeapInodeStore.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/heap/HeapInodeStore.java

## Purpose
`HeapInodeStore` is the on-heap `InodeStore` implementation. It stores inode objects in a concurrent map and sorted parent-child edges in a two-key sorted map, with checkpoint serialization as inode protobufs.

## Important APIs and Types
- `mInodes` maps inode ID to `MutableInode<?>`.
- `mEdges` maps parent ID and child name to child ID with sorted child-name order.
- Implements inode/edge write and read methods, `allEdges`, `allInodes`, `clear`, checkpoint write/restore, and child ID iteration.
- Static `sortedMapToIterator(SortedMap<String, Long>, ReadOption)` applies `startFrom` and `prefix` filters.

## Control Flow
`writeNewInode` uses `compute` to keep an existing inode if present, logging corruption if the existing name differs. `writeInode` uses `putIfAbsent`, so it does not overwrite existing entries. Child lookups read the sorted edge map. `getChildren` maps child IDs back to inodes. Checkpoint writing emits all inode protos; restore reads inode protos and rebuilds both `mInodes` and `mEdges`.

## State and Persistence
Heap maps are volatile process state. Checkpoint type is `INODE_PROTOS`, and checkpoint name is `HEAP_INODE_STORE`. Restoring from checkpoint reconstructs parent-child edges from each inode's parent ID/name.

## Dependencies and Integration Points
Depends on `TwoKeyConcurrentSortedMap`, inode metadata classes, `ReadOption`, checkpoint streams, metrics, and object-size calculation. It is a backing or standalone inode store for the file master.

## Risks and Edge Cases
- `writeInode` not overwriting existing inode metadata may be surprising for updates; callers must rely on mutating existing mutable inode objects or use implementation-specific expectations.
- Restoring root or special parent IDs into the edge map depends on inode proto parent fields.
- `sortedMapToIterator` prefix/start comparisons must match RocksDB behavior for cross-store consistency.
- Concurrent sorted-map iteration is weakly consistent.

## Test Signals
Tests should cover write-new conflict logging, write/update semantics, sorted listing with start/prefix combinations, checkpoint round-trip, edge rebuild on restore, clear behavior, and heap metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/heap/HeapInodeStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/rocks/RocksBlockMetaStore.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/rocks/RocksBlockMetaStore.java

## Purpose
`RocksBlockMetaStore` is the RocksDB-backed `BlockMetaStore` implementation. It stores block metadata and block locations in separate RocksDB column families, exposes RocksDB operational metrics, and participates in checkpoint/restore through `RocksCheckpointed`.

## Important APIs and Types
- Implements `BlockMetaStore` and `RocksCheckpointed`.
- Uses column families `block-meta` and `block-locations` under database name `blocks`.
- Holds `WriteOptions mDisableWAL`, prefix/iterator `ReadOptions`, `RocksStore`, column handle references, `mToClose`, and `LongAdder mSize`.
- Public methods implement block CRUD, location CRUD, iteration, clear, close, size, `getRocksStore`, and `getCheckpointName`.

## Control Flow
Construction loads the RocksDB native library, configures options either from a Rocks config file or built-in column-family options, applies table-cache/bloom/index settings from Alluxio properties, creates the Rocks store, and registers many cached Rocks property gauges. Reads and writes acquire `RocksStore` shared locks. `putBlock` checks prior existence to increment `mSize`, writes with WAL disabled, and overwrites existing metadata. `removeBlock` decrements size if the key existed. `getLocations` uses prefix iteration over block-location keys. Full block iteration uses `RocksUtils.createCloseableIterator` and abort checks.

## State and Persistence
Block metadata and locations persist in RocksDB. `mSize` is in-memory accounting updated by put/remove and reset by clear/close; it is not rebuilt in this file after restore. Checkpoint name is `BLOCK_MASTER`, and checkpoint bytes are produced by `RocksStore`.

## Dependencies and Integration Points
Depends on RocksDB Java APIs, `RocksStore`, `RocksUtils`, `RocksCheckpointed`, Alluxio configuration, metrics, protobuf block types, and path/file utilities. It is used by the block master when Rocks metastore is enabled.

## Risks and Edge Cases
- WAL is disabled, so durability relies on Alluxio journal/checkpoint semantics rather than Rocks WAL.
- `getLocations` iterates with prefix-same-as-start and assumes one block has bounded locations.
- `removeBlock` does not remove block-location records.
- `mSize` can become inaccurate if state is restored or externally modified without replaying put/remove accounting.
- Native RocksDB resources must be closed in reverse order after taking the exclusive close lock.

## Test Signals
Tests should cover column-family config validation, put/remove size accounting, location prefix iteration, clear resetting Rocks and size, checkpoint/restore via `RocksCheckpointed`, close resource order, Rocks property gauges, and iterator abort behavior during close/rewrite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/rocks/RocksBlockMetaStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/rocks/RocksCheckpointed.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/rocks/RocksCheckpointed.java

## Purpose
`RocksCheckpointed` provides default `Checkpointed` implementations for classes backed by `RocksStore`. It standardizes exclusive locking around RocksDB checkpoint and restore operations.

## Important APIs and Types
- Extends `Checkpointed`.
- Requires `getRocksStore()`.
- Default async and stream `writeToCheckpoint` methods take `lockForCheckpoint`.
- Default async and stream restore methods take `lockForRewrite`.
- Wraps failures in `AlluxioRuntimeException` for async paths.

## Control Flow
Async checkpoint writes run on the supplied executor, create a subdirectory named by `getCheckpointName`, acquire checkpoint lock, and ask `RocksStore` to snapshot. Stream checkpoint writes acquire the same lock and stream compressed checkpoint data. Restores acquire rewrite locks because database contents are replaced.

## State and Persistence
No local state. It coordinates persistence of the underlying RocksDB directory/checkpoint stream.

## Dependencies and Integration Points
Implemented by `RocksInodeStore` and `RocksBlockMetaStore`. Depends on Alluxio checkpoint interfaces, `RocksStore`, executor services, and gRPC status/error typing for runtime exceptions.

## Risks and Edge Cases
- Async methods use `CompletableFuture.runAsync`; callers must observe future failures.
- Subdirectory names must match checkpoint names expected by restore.
- Long checkpoint/restore operations block or abort concurrent Rocks readers through `RocksStore` locks.

## Test Signals
Tests should verify lock type selection, subdirectory naming, async exception wrapping, stream checkpoint/restore delegation, and concurrent reader abort behavior through RocksStore fakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/rocks/RocksCheckpointed.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/rocks/RocksInodeStore.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/rocks/RocksInodeStore.java

## Purpose
`RocksInodeStore` is the RocksDB-backed `InodeStore` implementation. It stores inode protobufs and parent-child edges in separate column families, supports prefix/range listing, batch writes, checkpoints, and RocksDB memory/health metrics.

## Important APIs and Types
- Implements `InodeStore` and `RocksCheckpointed`.
- Uses database name `inodes` and columns `inodes` and `edges`.
- Uses key encoding: inode IDs as 8-byte longs; edge keys as parent ID bytes followed by child name bytes.
- Public methods cover inode CRUD, edge CRUD, mutable/read-only child lookup, child ID iteration, `hasChildren`, full debug sets, closeable inode iteration, batch writes, clear, close, checkpoint name, and RocksStore access.
- Inner `RocksIter` iterates child IDs while enforcing optional child-name prefix.
- Inner `RocksWriteBatch` batches inode/edge puts/deletes and commits via RocksDB write batch.

## Control Flow
Construction configures RocksDB options from an optional config file or default hash memtable/prefix extractor setup, applies table config properties, initializes `RocksStore`, and registers many RocksDB gauges plus aggregate memory gauges. Each normal operation acquires a `RocksSharedLockHandle`. Child iteration creates a Rocks iterator, seeks to parent/prefix/start key, then returns a closeable iterator holding a second shared lock for the lifetime of iteration; each `next` checks whether RocksDB has been closed or rewritten. `getChild` warns if an edge points to a missing inode. `clear` uses rewrite exclusive locking. Close uses closing exclusive lock and closes Rocks objects in reverse order.

## State and Persistence
Inodes and edges persist in RocksDB. WAL is disabled, so persistence is coordinated by Alluxio journal/checkpoint. Checkpoint name is `ROCKS_INODE_STORE`; checkpoint/restore is inherited from `RocksCheckpointed`. Full iteration and all-inode/all-edge debugging read from RocksDB using total-order seek.

## Dependencies and Integration Points
Depends on RocksDB Java APIs, `RocksStore`, `RocksUtils`, `ReadOption`, inode metadata/protobufs, metrics, and Alluxio configuration. It is commonly used as the backing store under `CachingInodeStore`.

## Risks and Edge Cases
- Prefix checking in `RocksIter` must match key encoding exactly; malformed key lengths or default charset assumptions for child names can break listing.
- Iterator clients must close returned iterators to release shared Rocks locks and native iterator resources.
- `hasChildren` checks iterator validity after seeking parent ID; correctness depends on prefix-same-as-start.
- `allInodes` calls `getMutable` while already holding a shared lock, relying on shared-lock reentrancy/ref-count behavior.
- WAL disabled plus batch writes mean crash consistency depends on upstream journal replay.

## Test Signals
Tests should cover key encoding/decoding, prefix/start listing combinations matching heap behavior, missing child edge warning, batch write commit/close, clear/rewrite lock behavior, checkpoint round-trip, iterator close and abort on rewrite, and Rocks metrics registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/rocks/RocksInodeStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/rocks/RocksStore.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/rocks/RocksStore.java

## Purpose
`RocksStore` manages a RocksDB instance for Alluxio master metastores. It owns database creation, reset, close, checkpoint compression, checkpoint restore, table config helpers, and a custom shared/exclusive lock protocol that protects native RocksDB resources during concurrent reads, writes, checkpoints, clears, restores, and shutdown.

## Important APIs and Types
- Constructor accepts store name, DB path, checkpoint path, DB options, column-family descriptors, and column handle references.
- `getDb`, `clear`, `close`, `writeToCheckpoint`, and `restoreFromCheckpoint` manage lifecycle and persistence.
- `checkAndAcquireSharedLock()` returns `RocksSharedLockHandle`.
- `lockForClosing`, `lockForCheckpoint`, and `lockForRewrite` return exclusive handles with different release semantics.
- `shouldAbort(int)` lets long-running readers abort after close/rewrite requests.
- `mRocksDbStopServing` is an `AtomicStampedReference<Boolean>` carrying stop flag plus DB version.
- `mRefCount` tracks shared lock holders.
- Static `checkSetTableConfig` applies block cache, bloom filter, index, and data-block-index settings.

## Control Flow
Initialization takes a rewrite exclusive lock and calls `resetDb`, which stops any existing DB, formats directories, and opens RocksDB with default plus configured column families. Shared lock acquisition checks the stop flag, increments ref count, then checks the flag again to avoid races with close. Exclusive acquisition sets the stop flag, waits up to the configured timeout for shared refs to drain, optionally resets the ref counter if forced, and returns a handle whose close action resets stop/version according to checkpoint or rewrite semantics. Checkpoint writes create a RocksDB checkpoint directory and compress it as either parallel zip or single tar.gz. Restore stops the DB, replaces/decompresses data, and reopens it.

## State and Persistence
Owns the live RocksDB and Checkpoint objects plus column handles. Persistence is the RocksDB directory and checkpoint streams/directories. Version stamps increment on rewrites/restores/clears but not on checkpoints.

## Dependencies and Integration Points
Used by Rocks-backed inode and block stores. Depends on RocksDB Java APIs, Alluxio configuration, retry utilities, compression utilities, file utilities, and runtime exceptions. The lock protocol is consumed by `RocksSharedLockHandle` and `RocksExclusiveLockHandle`.

## Risks and Edge Cases
- Ref-count correctness is critical to avoiding native crashes during close/restore; test mode enforces strict canaries, production logs and resets.
- Forced exclusive locks can invalidate slow readers; long iterators must call `shouldAbort`.
- Checkpoint paths are deleted/recreated; misconfiguration can destroy unexpected directories if paths are wrong.
- Parallel checkpoint restore writes to a temp path under the first configured temp directory and must clean it on failure.
- `checkSetTableConfig` contains a misspelled local variable but behavior is unaffected.

## Test Signals
Tests should cover shared lock race prevention, exclusive timeout and ref-counter reset, version increments on rewrite but not checkpoint, checkpoint single/parallel formats, restore from directory and stream, column handle close/reopen, config-file and property table options, and abort signaling for iterators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/rocks/RocksStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/CloudCostUtils.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/CloudCostUtils.java

## Purpose
`CloudCostUtils` estimates cloud object-store API cost savings from avoided UFS metadata operations. It maps UFS operation types to hard-coded per-operation prices for S3, ABFS, GCS, and OSS.

## Important APIs and Types
- Static immutable cost maps for `UFSOps.CREATE_FILE`, `GET_FILE_INFO`, `DELETE_FILE`, and `LIST_STATUS`.
- `COSTMAP` maps UFS type strings (`abfs`, `gcs`, `s3`, `oss`) to cost maps.
- `calculateCost(String, Map<String, Long>)` totals operation count times per-operation price, ignoring unknown operation names.

## Control Flow
If the UFS type is unsupported, `calculateCost` returns zero. Otherwise it iterates the per-UFS operation count map, parses each string as `UFSOps`, multiplies by the configured price if present, and ignores invalid enum names.

## State and Persistence
No mutable state or persistence. Pricing constants are embedded in code with comments noting last update dates from 2021.

## Dependencies and Integration Points
Depends on `DefaultFileSystemMaster.Metrics.UFSOps` and Guava `ImmutableMap`. Used by metrics/reporting code that converts saved UFS operations into estimated monetary savings.

## Risks and Edge Cases
- Prices are static and likely stale; output should be treated as an estimate.
- UFS type matching is lowercase and exact.
- Unknown operations and unsupported UFS types silently contribute zero.

## Test Signals
Tests should cover each provider map, unsupported provider returning zero, invalid operation names ignored, and expected arithmetic for mixed operation counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/CloudCostUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/DefaultMetricsMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/DefaultMetricsMaster.java

## Purpose
`DefaultMetricsMaster` is the core master responsible for receiving client/worker metrics, maintaining cluster metrics, exposing the metrics master gRPC service, and registering derived throughput and multi-value aggregate gauges.

## Important APIs and Types
- Extends `CoreMaster`; implements `MetricsMaster` and `NoopJournaled`.
- Holds `Map<String, MultiValueMetricsAggregator> mAggregatorRegistry`.
- Holds `MetricsStore mMetricsStore`.
- Constructors set clock/executor and register aggregators.
- `registerThroughputGauge` creates bytes-per-minute gauges from counters and last clear time.
- `getServices` exposes `METRICS_MASTER_CLIENT_SERVICE`.
- `start(Boolean isLeader)` initializes metrics and starts cluster metric updater heartbeat only on leader.
- `clientHeartbeat` and `workerHeartbeat` asynchronously submit metrics to `MetricsStore`.
- `clearMetrics` clears store; `getMetrics` returns all metrics from `MetricsSystem`.
- Inner `ClusterMetricsUpdater` periodically calls `updateMultiValueMasterMetrics`.

## Control Flow
At construction, the master registers throughput gauges for read/write counters and creates a `SingleTagValueAggregator` per UFS operation. On start, it initializes metric keys, clears existing metrics, and, if leader, schedules a fixed-interval heartbeat. The updater fetches master metrics matching registered filters, lets each aggregator compute output values, and registers gauges for newly produced aggregate metric names. Heartbeat RPC handlers enqueue writes into the master executor instead of synchronously updating the store.

## State and Persistence
Metrics are in-memory and this master is `NoopJournaled`; metrics are cleared on start and via `clearMetrics`. Derived gauges live in the global `MetricsSystem` registry.

## Dependencies and Integration Points
Integrates with `CoreMaster`, `MetricsMasterClientServiceHandler`, `MetricsStore`, `MetricsSystem`, Dropwizard gauges, heartbeat framework, authentication interceptor, and Alluxio configuration for service thread count and update interval.

## Risks and Edge Cases
- Metrics updates are asynchronous; immediate reads after heartbeat may not include submitted metrics.
- Throughput gauge divides by uptime in minutes since last clear; for uptime <= 0 it returns the raw counter value.
- Gauges capture aggregator instances and read current aggregate values at scrape time.
- Non-leader masters do not start the cluster metrics updater.

## Test Signals
Tests should cover service registration with interceptor, leader-only heartbeat scheduling, client/worker heartbeat asynchronous storage, clear semantics, throughput gauge arithmetic, aggregate gauge creation, and no-op journaling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/DefaultMetricsMaster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/MetricsMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/MetricsMaster.java

## Purpose
`MetricsMaster` is the interface for the Alluxio master that aggregates cluster-level metrics from workers and clients and exposes those metrics to RPC clients.

## Important APIs and Types
- Extends `Master`.
- `clearMetrics()` clears current master metrics.
- `clientHeartbeat(String, List<Metric>)` accepts client-side metric reports.
- `workerHeartbeat(String, List<Metric>)` accepts worker metric reports.
- `getMasterServiceHandler()` returns the metrics client service handler.
- `getMetrics()` returns metric name to protobuf `MetricValue`.

## Control Flow
Implementations receive heartbeat metrics from service handlers, store or aggregate them, and serve queries through `getMetrics`.

## State and Persistence
The interface does not prescribe persistence. `DefaultMetricsMaster` keeps metrics in memory and is `NoopJournaled`.

## Dependencies and Integration Points
Used by `MetricsMasterClientServiceHandler`, master service registration, worker/client metric heartbeat paths, and monitoring endpoints. Depends on Alluxio `Metric` and gRPC `MetricValue`.

## Risks and Edge Cases
Implementations must define concurrency and eventual consistency semantics for heartbeat ingestion and metric reads.

## Test Signals
Contract tests should verify clear, client heartbeat, worker heartbeat, service handler availability, and metric map output for concrete implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/MetricsMaster.java -->
