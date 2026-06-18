# subset-b-008442 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClientLogEvents.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClientLogEvents.h

Purpose: Defines serialized client transaction profiling event records and trace-log emission helpers for get-version, get, get-range, commit, and error paths. The file explicitly marks these structures as persistent internal FDB format, so schema changes can break upgrade simulation and old metadata replay.

Important APIs/types/functions: `FdbClientLogEvents::EventType` classifies persisted events. `TransactionPriorityType` is a fixed-size persisted enum whose numeric values intentionally differ from `TransactionPriority`. Base `Event` carries `type`, `startTs`, optional `dcId`, and a legacy empty tenant field retained for old data. Concrete event records include `EventGetVersion`, `EventGetVersion_V2`, `EventGetVersion_V3`, `EventGet`, `EventGetRange`, `EventCommit`, `EventCommit_V2`, `EventGetError`, `EventGetRangeError`, and `EventCommitError`. `logEvent()` methods emit `TraceEvent` rows with transaction id, latency, key/range/mutation details, errors, priority, read version, or commit version.

Control flow: Producers construct the versioned event matching the current persisted schema, serialize it into client log data, and later replay/deserializers recover only subclass-local fields on deserialization because the base event header is already consumed by type dispatch. Commit events iterate read conflict ranges, write conflict ranges, and mutations before emitting a summary trace.

State and persistence behavior: Serialized layout is compatibility-sensitive. Versioned structs add fields without mutating old versions: get-version V2 adds priority, V3 adds read version, commit V2 adds commit version. Commit events serialize only `CommitTransactionRequest::transaction` and `arena`, not the full request state. The legacy tenant field remains in the base event for old metadata.

Dependencies and integration points: Depends on `FDBTypes.h` for keys, versions, priorities, and arenas, and `CommitProxyInterface.h` for `CommitTransactionRequest`. Trace emission integrates with Flow `TraceEvent` and transaction tracing analyzers; `TransactionPriorityType` has a static size assertion for external analyzer assumptions.

Risks: Reordering fields, removing legacy tenant state, changing enum values, or serializing different `CommitTransactionRequest` members would break old persisted event records. Trace logging full keys, ranges, and mutations can produce large events, so `setMaxFieldLength()`/`setMaxEventLength()` behavior matters for observability safety. Priority conversion must preserve the intentional enum mismatch.

Test signals: Upgrade simulation that reads old client event records; serialization round trips for each event version; transaction tracing tests for get/getRange/commit/error events; analyzer tests that assume the priority field size; large-key and large-mutation trace truncation checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClientLogEvents.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClientVersion.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClientVersion.h

Purpose: Provides `ClientVersionRef`, the lightweight serialized representation of a client binary version, source version, and protocol version reported to cluster coordination/open-database paths.

Important APIs/types/functions: `ClientVersionRef` stores three `StringRef` fields: `clientVersion`, `sourceVersion`, and `protocolVersion`. Constructors support unknown initialization, arena-deep-copy, direct three-part construction, and parsing a comma-separated version string. `serialize()` writes the three fields. `expectedSize()` reports aggregate string size. `operator<` sorts primarily by protocol version, then client version, then source version.

Control flow: Open-database and coordination request producers encode supported versions as `ClientVersionRef` values. String parsing accepts exactly three comma-separated parts; otherwise all fields become `"Unknown"`. Ordering is used for maps/sets that summarize client populations by version.

State and persistence behavior: The type is arena-backed when copied through the arena constructor and otherwise references external string memory via `StringRef`. There is no validation beyond the three-part split, and unknown initialization is the fallback persistence/display state.

Dependencies and integration points: Depends only on `flow/Arena.h` and Flow string utilities. Used by `ClusterInterface::OpenDatabaseRequest::supportedVersions` and `CoordinationInterface::OpenDatabaseCoordRequest::supportedVersions` to report client compatibility.

Risks: A malformed version string silently collapses all fields to unknown, reducing diagnostics. Because fields are `StringRef`, callers must ensure referenced memory outlives the object unless copied into an arena. Ordering is explicitly arbitrary except for protocol version, so it should not be interpreted as semantic release ordering.

Test signals: Parse tests for valid and invalid comma-separated strings; arena copy lifetime tests; map ordering/grouping by protocol; open-database client info aggregation with unknown and mixed versions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClientVersion.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClientWorkerInterface.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClientWorkerInterface.h

Purpose: Declares the subset of worker RPC streams that clients can safely call for management operations: reboot, profiling, failure injection, and optional gRPC address discovery.

Important APIs/types/functions: `ClientWorkerInterface` contains `RequestStream<RebootRequest>`, `RequestStream<ProfilerRequest>`, `RequestStream<SetFailureInjection>`, and optional `grpcAddress`. It exposes identity via the reboot endpoint token and primary address. `initEndpoints()` initializes the reboot endpoint and records the Flow gRPC server address when enabled. `RebootRequest` carries delete/check-data flags and a wait duration. `ProfilerRequest` carries reply promise, profiling `Type` (`GPROF`, `FLOW`, `GPROF_HEAP`), `Action` (`DISABLE`, `ENABLE`, `RUN`), duration, and output file. `SetFailureInjection` supports disk stall/throttle and bit-flip commands.

Control flow: Workers embed this as the first element of their broader worker interface, initialize endpoints, then cluster management clients retrieve `ClientWorkerInterface` values and send management requests to the relevant streams. Requests with replies complete through `ReplyPromise<Void>`.

State and persistence behavior: This is an RPC contract, not durable state. Serialized endpoint fields determine remote routing, and optional gRPC address is discovery metadata. Failure-injection command values are transient and affect worker runtime behavior.

Dependencies and integration points: Depends on Flow gRPC support, `FDBTypes.h`, failure monitoring, status, and commit proxy types. Integrated through `ClusterInterface::GetClientWorkersRequest`, management API reboot/profiler commands, and worker process control handlers.

Risks: Endpoint identity is derived from the reboot stream, so endpoint initialization/order must remain stable. Failure injection is powerful and can corrupt or stall disks in tests, so caller authorization and simulation gating matter. `grpcAddress` is conditional on `FLOW_GRPC_ENABLED`, so clients must handle absence.

Test signals: Worker interface serialization round trips; client-worker discovery; reboot request handling with flags and delay; profiler enable/run/disable; disk stall/throttle and bit-flip failure-injection simulation; builds with and without Flow gRPC.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClientWorkerInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClusterConnectionFile.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClusterConnectionFile.h

Purpose: Declares a file-backed implementation of `IClusterConnectionRecord`, the abstraction used to store, read, update, and persist the cluster connection string.

Important APIs/types/functions: Constructors load an existing cluster file or create one from a `ClusterConnectionString`. `openOrDefault()` resolves empty inputs to the default cluster file. `setAndPersistConnectionString()`, `getStoredConnectionString()`, `upToDate()`, `getLocation()`, `makeIntermediateRecord()`, `toString()`, and protected `persist()` implement the record interface. Static helpers `lookupClusterFileName()` and `getErrorString()` support default path resolution and user-facing constructor errors.

Control flow: Native API startup opens a specified or default file, parses the connection string, and stores it in memory. When coordinators forward a changed connection string, `setAndPersistConnectionString()` updates memory and writes the file. `upToDate()` rereads persistent storage to detect external modifications.

State and persistence behavior: Persistent state is the cluster file contents at `filename`; in-memory state is inherited `IClusterConnectionRecord::cs`. `makeIntermediateRecord()` creates a modified non-persisted record for connection transitions. Successful persistence is reported as a future so callers can chain actor flow.

Dependencies and integration points: Depends on `CoordinationInterface.h` for `ClusterConnectionString` and record interface. Used by native API database connection setup, cluster-file change handling, hot-standby switching, and coordinator forwarding.

Risks: File parsing and path lookup are startup-critical. Partial writes, permissions, stale external edits, or invalid cluster file format can prevent cluster connection or persist wrong coordinators. Intermediate records must not be mistaken for durable state until persistence completes.

Test signals: Default path lookup; constructor error strings for missing/unreadable/invalid files; set-and-persist then reopen; external file edit detection via `upToDate`; intermediate record behavior; connection-string forwarding updates; permission and atomic-write failure scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClusterConnectionFile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClusterConnectionMemoryRecord.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClusterConnectionMemoryRecord.h

Purpose: Declares an in-memory `IClusterConnectionRecord` implementation for clients/tests that need a connection string record without durable cluster-file backing.

Important APIs/types/functions: The constructor stores a `ClusterConnectionString`, marks persistence as unnecessary, and assigns a deterministic-random `UID` for display/location. It overrides `setAndPersistConnectionString()`, `getStoredConnectionString()`, `upToDate()`, `getLocation()`, `makeIntermediateRecord()`, `toString()`, and protected `persist()`.

Control flow: Callers construct the record with a known connection string. Updates modify in-memory state; `persist()` is a no-op returning success. `upToDate()` always reports true and returns the in-memory connection string because there is no external storage.

State and persistence behavior: All state is process-local. The `UID id` only distinguishes records in logs/locations. No cluster-file write occurs, and connection string changes vanish when the record is destroyed.

Dependencies and integration points: Uses `CoordinationInterface.h` abstractions, Flow references, and deterministic random UID generation. Useful in tests, internal clients, and code paths where coordinators are supplied directly.

Risks: Because `upToDate()` always succeeds, this record cannot detect coordinator changes from persistent storage. Accidentally using it where a durable cluster file is expected can break reconnection across process restarts. The generated id is diagnostic only and not a stable identity.

Test signals: In-memory update/read behavior; no-op persist success; `makeIntermediateRecord()` copy with different connection string; location/toString include type and id; connection setup without any filesystem access.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClusterConnectionMemoryRecord.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClusterInterface.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClusterInterface.h

Purpose: Defines the cluster controller client-facing RPC interface and request/reply types for opening databases, failure monitoring, status, worker discovery, recovery, shard movement/splitting, and system-data repair.

Important APIs/types/functions: `ClusterInterface` contains request streams for open database, failure monitoring, status, ping, client workers, force recovery, move shard, repair system data, split shard, and trigger audit. `OpenDatabaseRequest` reports client counts, issues, supported versions, max protocol support, and known client info id, then returns `ClientDBInfo`. `FailureMonitoringRequest/Reply` carry self-diagnosed failures and delta-compressed failure status. `StatusRequest/Reply` returns JSON status. Other contracts include `GetClientWorkersRequest`, `ForceRecoveryRequest`, `MoveShardRequest`, `RepairSystemDataRequest`, `SplitShardRequest/Reply`, and `ClusterControllerClientInterface`.

Control flow: Clients/coordinators send `OpenDatabaseRequest` with their last known client info id and wait until `ClientDBInfo` changes. Participants poll failure monitoring using the interval from the previous reply. Management operations target cluster-controller streams and complete by reply promises. `hasMessage()` checks whether any stream has pending input for controller actors.

State and persistence behavior: This file defines wire state. `StatusReply` persists status as a string during serialization and reconstructs `StatusObject` on deserialization, strict in simulation and lenient outside simulation. Open-database request aggregates client version and issue samples but does not itself persist data.

Dependencies and integration points: Depends on FDB types, failure monitor, status JSON, commit and worker interfaces, and client version. Instantiated by `NativeAPI.actor.cpp` and used by cluster controller actors, fdbcli/status clients, and management API paths.

Risks: Stream ordering and adjusted endpoint identity are part of the RPC contract. `OpenDatabaseRequest::serialize()` asserts protocol support for open database. Status JSON parse leniency outside simulation can mask malformed status fields. Force recovery and repair requests are operationally dangerous and require careful caller gating.

Test signals: Open database long-poll behavior; client info change propagation; failure monitoring deltas and timeout intervals; status JSON strict parse in simulation; worker discovery; force recovery/move/split/repair request routing; serialization compatibility for each request/reply.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ClusterInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/CommitProxyInterface.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/CommitProxyInterface.h

Purpose: Defines the commit proxy client/server RPC surface and the `ClientDBInfo` structure returned to clients so they can commit transactions, locate storage servers, retrieve commit versions, query DD metrics, manage idempotency ids, and run proxy management commands.

Important APIs/types/functions: `CommitProxyInterface` serializes `processId`, `provisional`, and primary `commit` stream, then reconstructs adjusted streams for legacy GRV, key-server locations, storage-server rejoin, wait-failure, transaction state, proxy snapshot, exclusion safety, DD metrics, idempotency expiration, and throttled-shard updates. `ClientDBInfo` carries GRV proxies, commit proxies, forwarding info, global config history, cluster id, and cluster type. `CommitID` returns commit version, batch id, metadata version, and optional conflicting key-range indices. `CommitTransactionRequest` carries transaction ref, reply, flags, debug id, cost estimate, tag set, span context, idempotency id, and arena. Supporting request/reply types cover key-server locations, raw committed version, storage rejoin info, transaction state broadcast, DD metrics, snapshots, exclusion safety, throttled shards, and idempotency expiration.

Control flow: Clients choose a commit proxy from `ClientDBInfo`, send `CommitTransactionRequest`, and receive a `CommitID`; invalid version indicates conflict. Location lookups send `GetKeyServerLocationsRequest` and receive ranges with storage server interfaces plus TSS/tag mappings. Proxies reconstruct adjusted streams on deserialization from the commit endpoint, so only the primary endpoint is serialized.

State and persistence behavior: The interface is wire state; persistent effects occur when commit proxies process transactions and idempotency expiration. `ClientDBInfo::history` carries `VersionHistory` entries for global config synchronization. `getBytes()` estimates request size from mutations and conflict ranges using commit overhead knobs.

Dependencies and integration points: Depends on commit transaction types, global config, GRV proxy interface, idempotency ids, storage server interface, FDB types, and Flow transport. Used by native API transactions, GRV/commit proxy model selection in `DatabaseContext`, storage server rejoin, fdbcli management, and DD metrics callers.

Risks: Adjusted endpoint numbering is compatibility-sensitive; the legacy GRV slot is reserved even though commit proxies no longer serve GRV. Miscomputed flags (`LOCK_AWARE`, first-in-batch, bypass quota) can alter commit semantics. Arena/shared string lifetime matters for transaction payloads. Idempotency expiration is version/batch-index sensitive. Adding streams requires preserving endpoint numbers.

Test signals: Commit request/response serialization; adjusted endpoint reconstruction; transaction conflict and conflicting-key reporting; commit request byte accounting; key-server location responses with TSS/tag mappings; storage rejoin replies; DD metrics requests; snapshot/exclusion/throttled-shard management; client DB info refresh and global config history propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/CommitProxyInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/CommitTransaction.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/CommitTransaction.h

Purpose: Defines mutation, transaction, and mutation-version payload types used on the commit path, including compact wire serialization, mutation checksum support, and conflict/mutation collections.

Important APIs/types/functions: `MutationRef` stores a mutation `type`, `param1`, `param2`, optional CRC32C checksum, optional accumulative checksum index, and corruption flag. Mutation types include set/clear, atomic operations, versionstamped mutations, comparison clear, and reserved log/span/partition slots. Helper methods classify atomic/single-key/non-associative operations, copy parameters into arenas, format traces, populate/validate checksums, offload serialized checksum/index suffixes, and serialize with protocol-sensitive checksum flags. `CommitTransactionRef` carries read and write conflict ranges, mutations, read snapshot, conflicting-key reporting, lock awareness, span context, and legacy tenant ids. `MutationsAndVersionRef` bundles mutations with committed and known committed versions.

Control flow: Transaction builders push mutations and conflict ranges into `CommitTransactionRef`. During serialization, `MutationRef` may compact single-key clear ranges by serializing end plus empty begin, and may append checksum then accumulative checksum index to `param2` while setting high bits in `type`. During deserialization, it validates suffix sizes, strips accumulative index before checksum, reconstructs single-key clear ranges, and validates CRC before marking corruption.

State and persistence behavior: Mutation type low 6 bits are the operation, while high bits are wire flags for checksum and accumulative checksum index. Type enum values and reserved slots are protocol/persistence-sensitive. `CommitTransactionRef::serialize()` gates span context handling on protocol versions and contains a tenant-ids TODO retained for older internal paths.

Dependencies and integration points: Depends on FDB types, knobs, tracing, Flow encryption utilities, unit testing, and crc32c. Used by commit proxy requests, TLog messages, global config history, client log events, management configuration writes, and high-contention allocator atomic operations.

Risks: The same byte stores operation and wire flags, so incorrect masking can misclassify operations. Checksum suffix order is strict: checksum first, accumulative index second; deserialization strips in reverse order. Clear-range compaction assumes `keyAfter` form. Changes to enum values or serialization gates require protocol-version and downgrade consideration.

Test signals: Mutation serialization round trips across protocol versions; checksum and accumulative checksum enable/disable cases; corrupt suffix size detection; CRC mismatch detection; single-key clear compact/decompact behavior; operation classification masks; commit transaction span context compatibility; arena lifetime tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/CommitTransaction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ConsistencyScanInterface.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ConsistencyScanInterface.h

Purpose: Declares the consistency scan worker RPC interface and the database-backed state model controlling scan configuration, range inclusion/skipping, current round stats, history, and lifetime stats.

Important APIs/types/functions: `ConsistencyScanInterface` exposes `waitFailure`, `haltConsistencyScan`, locality, and id. `HaltConsistencyScanRequest` identifies the requester and returns `Void`. `ConsistencyScanState` is a `KeyBackedClass` under `\xff/consistencyScanState`. Nested `Config` controls enablement, max read byte rate, target/min round time, minimum start version, and history retention. `RangeConfig` stores optional included/skip overlays with `apply()` and JSON conversion. `LifetimeStats` and `RoundStats` track logical bytes, replicated bytes, errors, skipped ranges, versions, timestamps, completion state, and last end key. Accessors return key-backed range/object properties and history maps. `clearStats()` clears current, lifetime, and history stats in one transaction after reading them for conflicts.

Control flow: Scan actors read `config()` and `rangeConfig()` triggers to decide whether and where to scan. They update `currentRoundStats()` and `lifetimeStats()` during execution and move completed or aborted rounds into `roundStatsHistory()`. Management paths can halt the role or clear stats; clearing reads keyspaces first to establish write conflicts, then resets stats and erases history.

State and persistence behavior: State is persisted in system keyspace through `KeyBackedTypes` and `KeyBackedRangeMap`. Config/range updates fire the class trigger; frequent stats updates intentionally do not except when resets explicitly update the trigger to prevent stale overwrite. JSON methods expose status-friendly snapshots.

Dependencies and integration points: Depends on system data, JSON spirit, commit proxy/database config/FDB types, RYW transactions, key-backed types, range maps, RPC/locality. Integrated with the consistency scan role, management/special key commands, status surfaces, and database transactions.

Risks: Trigger semantics are subtle: stats resets need explicit trigger handling or scan loops can overwrite reset values. Optional `RangeConfig` fields are overlays, so incorrect `apply()` semantics can unintentionally inherit old range settings. History retention uses versions-per-second assumptions. `clearStats()` is rare but must conflict correctly.

Test signals: Config/range key-backed read/write and trigger firing; range overlay application; JSON status output; round lifecycle from current to history; clearStats conflict behavior; halt request routing; scan restart after reset; persistence across role restart.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ConsistencyScanInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ConvertUTF.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ConvertUTF.h

Purpose: Provides Unicode conversion declarations between UTF-8, UTF-16, and UTF-32, imported from the Unicode sample implementation, plus legality checking for UTF-8 sequences.

Important APIs/types/functions: Defines `UTF32`, `UTF16`, `UTF8`, `Boolean`, Unicode maximum/replacement constants, `ConversionResult` (`conversionOK`, `sourceExhausted`, `targetExhausted`, `sourceIllegal`), and `ConversionFlags` (`strictConversion`, `lenientConversion`). C-linkage functions convert UTF8/16/32 in every direction and update source/target pointers in place. `isLegalUTF8Sequence()` validates a bounded UTF-8 sequence.

Control flow: Callers pass pointer-to-current source and target positions plus end pointers. Conversion proceeds until input is exhausted, target is full, or an illegal/incomplete sequence is found. On return the pointers identify the last successfully converted positions or the problematic source start.

State and persistence behavior: Stateless buffer conversion only; no persistent data. Strict mode rejects irregular sequences and isolated surrogates; lenient mode converts some irregular/surrogate cases but still rejects illegal sequences and handles over-maximum values per documented behavior.

Dependencies and integration points: Standalone C-compatible header with no FDB-specific dependency. Used wherever FoundationDB needs portable UTF validation/conversion without relying on platform `wchar_t`.

Risks: Callers must allocate sufficient target buffers and handle pointer advancement after partial conversion. Lenient mode can hide invalid Unicode shape that strict callers may require. The typedefs assume unsigned fixed minimum widths but not exact platform-native Unicode types.

Test signals: Round trips among UTF-8/16/32; strict rejection of malformed UTF-8, overlong forms, isolated surrogates, and code points above U+10FFFF; target exhaustion and source exhaustion pointer behavior; lenient replacement-character behavior; C and C++ linkage builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ConvertUTF.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/CoordinationInterface.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/CoordinationInterface.h

Purpose: Defines coordinator-facing client registration interfaces, cluster connection string parsing/storage abstractions, leader discovery messages, protocol info checks, and descriptor mutability checks.

Important APIs/types/functions: `ClientLeaderRegInterface` exposes public get-leader and open-database streams plus descriptor mutability checks and optional hostname. `ClusterConnectionString` parses and serializes `description:id@coords` plus hostnames, exposes cluster key/name, coordinator counts, hostname resolution, and local source IP detection. `IClusterConnectionRecord` abstracts persisted or in-memory connection string records and persistence-on-connect behavior. `LeaderInfo` wraps leader change id, serialized cluster info or forward connection string, and priority bits for process class/exclusion/DC fitness. RPCs include `GetLeaderRequest`, `OpenDatabaseCoordRequest`, `ProtocolInfoRequest/Reply`, and `CheckDescriptorMutableRequest/Reply`. `ClientCoordinators` groups leader registration endpoints, key, and connection record.

Control flow: Clients parse a cluster connection string, create coordinator registration interfaces from addresses/hostnames, ask coordinators for leader info, then open the database through coordination. If leader info has `forward`, clients update their connection record with new coordinators. Leader election compares masked `changeID` priority bits to decide when a leader change is required.

State and persistence behavior: Connection strings are serialized as coordinates/hostnames/key/keyDesc and are persisted through `IClusterConnectionRecord` implementations. `LeaderInfo::changeID` packs priority state into high bits while preserving internal process identity in the rest. `MAX_CLUSTER_FILE_BYTES` bounds cluster file size.

Dependencies and integration points: Depends on FDB types, RPC, locality, commit/cluster interfaces, well-known endpoints, and hostnames. Used by cluster file implementations, NativeAPI connection monitoring, coordinators, cluster controller election, and protocol compatibility probes.

Risks: Connection string parsing rules are strict; accepting duplicate or malformed addresses would break connection or update wrong files. `changeID` bit packing is fragile and tied to `ClusterControllerPriorityInfo` width. Forwarded leader info can mutate durable cluster files. Protocol info reply uses a peer compatibility policy requiring stable interfaces.

Test signals: Valid/invalid connection string parsing; hostname resolution and local source IP detection; file/memory record persistence-on-connect; leader priority bit packing/unpacking and `leaderChangeRequired()` cases; coordinator open-database routing; protocol info compatibility; descriptor mutable checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/CoordinationInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/DataDistributionConfig.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/DataDistributionConfig.h

Purpose: Declares user-controlled data distribution range configuration stored in system keyspace, including per-range replication factor and team-id overrides.

Important APIs/types/functions: `DDRangeConfig` stores optional `replicationFactor` and optional `teamID`, supports overlay `apply()`, equality, `toString()`, serialization, JSON conversion, and trace/fmt formatting. `DDConfiguration` is a `KeyBackedClass` under `\xff\x02/ddconfig/`, with `RangeConfigMap` over keys to `DDRangeConfig`, `userRangeConfig()` accessor, and static `toJSON()` for snapshots.

Control flow: Management or special-key code writes range-map entries. DD reads a local snapshot and applies optional overlays across ranges so unspecified fields inherit from preceding/default ranges. JSON conversion produces status/inspection output, optionally including default ranges.

State and persistence behavior: Configuration persists in key-backed range map entries. Because both fields are optional, absence means continuation/inheritance rather than an explicit default. Updating user range config fires the class trigger.

Dependencies and integration points: Depends on serialization, NativeAPI/SystemData/FDB types, key-backed types/range maps, RYW/run transaction helpers, `DatabaseContext`, and JSON. Integrated with data distribution team selection and management APIs.

Risks: Optional overlay semantics can be misread as explicit null/default, causing wrong replication or team isolation. `teamID` is advisory for keeping different IDs on different teams, not an enforcement guarantee. Prefix/key-backed layout changes would orphan existing config.

Test signals: Range map set/clear/read snapshots; overlay application across adjacent ranges; JSON output with and without default ranges; DD behavior with replication-factor and team-id overrides; trigger firing on updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/DataDistributionConfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/DatabaseConfiguration.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/DatabaseConfiguration.h

Purpose: Defines the in-memory and serialized database configuration model used to interpret system configuration keys for proxies, resolvers, logs, storage, regions, satellites, backup workers, storage migration, encryption, exclusions, and policies.

Important APIs/types/functions: `SatelliteInfo` and `RegionInfo` describe region/satellite priorities and satellite TLog replication/quorum policies. `DatabaseConfiguration` applies mutations, sets/clears/gets options, validates configuration, serializes raw sorted config, converts to string/JSON/configure command, derives desired component counts, computes required datacenters/zones and tolerated failures, checks exclusions, and resolves auto counts. Public fields expose all major configured values, policies, store types, migration/encryption modes, regions, and backup/perpetual wiggle settings.

Control flow: Configuration key-values are loaded via `fromKeyValues()` or serialized raw config, then `setInternal()` populates derived fields and policies. Mutations from the system keyspace are applied with `applyMutation()`. Before serialization/comparison, mutable maps are made immutable into sorted `rawConfiguration`; on deserialization, raw entries are replayed through `setInternal()` and defaults are restored.

State and persistence behavior: The durable representation is sorted `rawConfiguration` key-values from system config keys. Enums such as store type, TLog version, spill type, storage migration, and deprecated encryption mode are persisted via stable numeric values. Auto counts use `-1` sentinel to select computed auto values.

Dependencies and integration points: Depends on FDB types, commit mutations, replication policies, and status. Used by cluster controller, management configure APIs, recruitment, DD, log system, storage server exclusion, status output, and recovery validation.

Risks: Config validation spans many subsystems, so accepting an inconsistent policy can make recruitment/recovery impossible. Serialization mutates internal representation by freezing mutable config. Persisted enum numeric values must never be reordered. Region and satellite quorum math is availability-critical. Exclusion checks must match locality/address semantics.

Test signals: Build/apply/serialize round trips from config key-values; configure JSON/string conversion; validity checks for replication, regions, store types, backup options, and migration modes; desired count auto override tests; region/satellite quorum and failure tolerance tests; exclusion matching; upgrade tests for persisted enum values.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/DatabaseConfiguration.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/DatabaseContext.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/DatabaseContext.h

Purpose: Declares the native client database runtime context: connection record, client info monitoring, proxy selection, storage location cache, watches, tag throttling, metrics, status, special key space, global config, version vector cache, and backoff.

Important APIs/types/functions: Helper types include `StorageServerInfo`, `LocationInfo`, `CommitProxyInfo`, `GrvProxyInfo`, `ClientTagThrottleData`, `WatchParameters`, `WatchMetadata`, `MutationAndVersionStream`, `EndpointFailureInfo`, and `KeyRangeLocationInfo`. `DatabaseContext` creates/clones databases, manages location cache get/set/invalidate, tracks failed endpoints, samples read tags/costs, updates and returns GRV/commit proxies, fetches health/storage metrics, splits storage metrics, queries hot ranges and cluster protocol, manages watch counters/maps/ref-counts, applies database options, handles connection changes/hot-standby switch, runs management actions, exposes client status JSON, and maintains request backoff. `Backoff` is a standalone exponential randomized delay helper.

Control flow: A database context is built from a connection record and `AsyncVar<ClientDBInfo>`, then monitors client info to update proxy models and global config. Transactions and reads consult caches, proxies, throttles, and version-vector state. Watches are tracked by key/version to survive connection changes and avoid cancellation races. Management methods route to cluster/worker/proxy RPCs. Errors can be deferred and checked before operations.

State and persistence behavior: Most state is process-local: caches, counters, throttled tags, watches, metrics, status snapshots, proxy models, and backoff. Persistent influence comes through the connection record, global config, special key space transactions, and management RPCs. `minAcceptableReadVersion` prevents reads from an old cluster after switching connection records.

Dependencies and integration points: Depends on NativeAPI, key range maps, commit/GRV/storage interfaces, special key space, queue model, event metrics, smoothers, DDSketch, version vectors, global config, and Flow actors. It is the core integration point for client transactions and status.

Risks: This class owns many asynchronous actors and shared references; destruction and `StorageServerInfo::notifyContextDestroyed()` must avoid dangling context pointers. Watch ref-count uses version multisets to avoid races during connection-file changes. Cache invalidation mistakes can direct reads to wrong storage servers. Proxy provisional state must keep GRV and commit proxy use consistent. Backoff and throttle handling affect client-wide throughput.

Test signals: Database clone/create lifecycle; proxy update and change trigger behavior; location cache hit/miss/invalidation; failed endpoint tracking refresh/clear; watch count/ref-count race cases across connection switch; hot standby min-version validation; health/storage metric fetching; tag throttle expiry; client status JSON; global config initialization; backoff growth/reset behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/DatabaseContext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/EventTypes.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/EventTypes.h

Purpose: Defines a typed metric descriptor for completed get-value latency events.

Important APIs/types/functions: `GetValueCompleteDescriptor` contains `int64_t latency`. The `Descriptor<GetValueCompleteDescriptor>` specialization names the event `"GetValueComplete"` and declares the `latency` field with unit `"ns"` using Flow TDMetric descriptor helpers.

Control flow: `DatabaseContext` owns an `EventMetricHandle<GetValueCompleteDescriptor>` and can emit this descriptor when get-value operations complete. The metric framework uses the descriptor specialization to map the struct field to a named metric event.

State and persistence behavior: No durable state; this is a compile-time descriptor for telemetry shape. Runtime samples are emitted through TDMetric infrastructure.

Dependencies and integration points: Depends on `flow/flow.h` and `flow/TDMetric.h`. Integrated into client read metrics through `DatabaseContext`.

Risks: Renaming the descriptor or field changes telemetry consumers. Unit mismatch would corrupt downstream latency interpretation. Additional fields require descriptor updates.

Test signals: Metric registration/compilation; get-value completion emits latency in nanoseconds; telemetry consumer/schema tests for `"GetValueComplete"`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/EventTypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/FDBOptions.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/FDBOptions.h

Purpose: Provides generic option metadata and ordered unique option storage used by generated database/transaction option tables and default-option handling.

Important APIs/types/functions: `FDBOptionInfo` stores name, comment, parameter comment, parameter presence, hidden/persistent/sensitive flags, default target option code, and parameter type (`None`, `String`, `Int`, `Bytes`). `FDBOptionInfoMap<T>` wraps a map from `T::Option` to metadata and invokes `T::init()` in its constructor. `UniqueOrderedOptionList<T>` stores each option at most once while preserving the most recent insertion order and value. `ADD_OPTION_INFO` inserts metadata into a type's static option map.

Control flow: Generated option classes initialize their metadata through `ADD_OPTION_INFO`. Callers look up metadata with `getMustExist()` and store default options with `UniqueOrderedOptionList::addOption()`, which removes older entries before appending the latest value.

State and persistence behavior: Option metadata is static/in-memory. Unique ordered option lists are runtime state, but options marked persistent in metadata may affect durable option handling elsewhere. Sensitive flags guide redaction/display decisions.

Dependencies and integration points: Depends on `flow/Arena.h` for `Optional<Standalone<StringRef>>`. Used by generated `FDBOptions.g.h`, NativeAPI option parsing, transaction default options in `DatabaseContext`, fdbcli/help surfaces, and bindings.

Risks: `T::init()` in the map constructor depends on generated static initialization patterns. Incorrect metadata can expose hidden/sensitive options or misparse parameter types. `defaultFor` semantics replace prior default values, so duplicate handling must remain unique and ordered.

Test signals: Generated option metadata initialization; lookup assertions for every generated option; duplicate option insertion order; parameter type validation; hidden/sensitive display filtering; database transaction default option application.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/FDBOptions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/FDBTypes.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/FDBTypes.h

Purpose: Defines the central client/server vocabulary for versions, keys, ranges, tags, storage engine enums, health/data-distribution metrics, priorities, versionstamps, read options, and many trace/serialization helpers.

Important APIs/types/functions: Core aliases include `Version`, `LogEpoch`, `Sequence`, `KeyRef`, `ValueRef`, `Generation`, `SpanID`, and `CoordinatorsHash`. `Tag` is a packed 3-byte log tag with locality/id, hashing, tracing, and struct-like serialization. `TagsAndMessage` parses log-message headers. `KeyRangeRef`, `KeyValueRef`, `KeySelectorRef`, `RangeResultRef`, `MappedKeyValueRef`, and `MappedRangeResultRef` define key/value and read result shapes. Utility functions include `keyAfter`, `singleKeyRange`, `prefixRange`, `keyBetween`, `randomKeyBetween`, printable/describe helpers, and `toPrefixRelativeRange`. Stable config enums/types include `KeyValueStoreType`, `TLogVersion`, `TLogSpillType`, `StorageMigrationType`, and `EncryptionAtRestModeDeprecated`. Operational structs include `StorageBytes`, `LogMessageVersion`, `ClusterControllerPriorityInfo`, `HealthMetrics`, `DDMetricsRef`, `WorkerBackupStatus`, `StorageMetadataType`, `StorageWiggleValue`, `ReadOptions`, `Versionstamp`, `GRVCacheSpace`, and `DatabaseSharedState`.

Control flow: Read and commit paths use selectors/range results to continue scans, storage/server code uses tags and log message versions to route mutations, configuration code serializes stable enum values, status code consumes health/storage metrics, and clients use version vector/read options/versionstamps for consistency and API semantics. Range/result helpers encode compact single-key ranges and continuation points.

State and persistence behavior: Many values are persisted in system keys, logs, or wire messages. Comments explicitly forbid reordering storage engine, spill, migration, and encryption enum values. `Tag` is packed and unversioned. `KeyRangeRef` serializes single-key ranges as `(end, empty)` and reconstructs on read. `Versionstamp` serializes big-endian version and batch number. `DatabaseSharedState` fixes member order for multi-version client compatibility.

Dependencies and integration points: Depends on Flow references/protocol/string/serialization, status, and locality. Included by most fdbclient interfaces and server components. Hash/trace/format specializations integrate it with STL containers, Flow tracing, status, and binary serialization.

Risks: This file is extremely broad; small semantic changes can affect wire compatibility, persistent config, log routing, or client API behavior. Packed `Tag` layout and stable enum numeric values are especially sensitive. Range-result `more/readThrough` semantics must be honored or range scans can skip/repeat keys. `StringRef` fields often depend on arena lifetime.

Test signals: Serialization round trips for all core structs; persisted enum upgrade/downgrade tests; tag hashing/order/layout checks; key range inversion and single-key compact serialization; range continuation helpers forward/reverse; key selector resolution helpers; storage type string aliases; health metrics detail update behavior; versionstamp endian encoding; multi-version `DatabaseSharedState` compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/FDBTypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/GenericManagementAPI.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/GenericManagementAPI.h

Purpose: Declares templated management APIs that work across NativeAPI and generic client API transaction/database types for configuring the database, auto-configuration, and coordinator-result messaging.

Important APIs/types/functions: `ConfigurationResult` enumerates normal configure outcomes and validation failures. `CoordinatorsResult` describes coordinator-change outcomes. `ConfigureAutoResult` stores current/auto/desired process counts, replication strings, address process classes, and machine/process counts. Free functions `buildConfiguration()`, `isCompleteConfiguration()`, and `parseConfig()` convert mode tokens/status into configuration maps. In namespace `ManagementAPI`, `getWorkers()` reads process classes and worker list, `changeConfig()` validates and writes config changes, `autoConfig()` writes auto-derived process classes and counts, overloads accept strings/vectors/maps, and `generateErrorMessage()` formats coordinator errors.

Control flow: `changeConfig()` builds a transaction with system-key, system-immediate, lock-aware, and provisional-proxy options. For non-forced updates it reads current config and worker/server/locality state, builds old/new `DatabaseConfiguration`, validates regional and worker sufficiency constraints, checks storage migration rules, writes config keys, optionally clears backup progress or resets storage wiggle metrics, takes the move-keys lock owner conflict, and commits with retry. Creating a database writes a random init id and distinguishes self-created from already-created after commit uncertainty. `autoConfig()` updates process class keys and auto counts similarly.

State and persistence behavior: Writes persistent system config keys, process class keys, backup progress clears, storage wiggle metric resets, database lock versionstamped value, and move-keys lock owner. It uses transaction conflict ranges to make emergency config changes retry-self-conflicting.

Dependencies and integration points: Depends on client boolean params, database configuration, status/system data, storage wiggle metrics, and transaction/database templates with `FutureT`, `createTransaction`, `getRange`, `setOption`, `commit`, and `onError`. Used by fdbcli, special keys, management tooling, and database creation/configuration code.

Risks: This code is safety-critical: incorrect validation can permit unrecruitable or unavailable configurations. The timeout path returns database unavailable if config/worker reads stall. Region change checks distinguish legacy dcid replication cases. Backup worker option changes clear backup progress. The `perpetualStorageWiggleKey` branch contains a suspicious `i->first == "1"` comparison where `i->second` likely was intended.

Test signals: Configure token parsing; create database success/already-created/uncertain commit; invalid/incomplete/conflicting options; region and dcid validation; not-enough-workers cases; storage migration disabled/gradual warning; sharded RocksDB warnings; backup/range-backup progress clearing; autoConfig process class writes; transaction retry behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/GenericManagementAPI.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/GenericTransactionHelper.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/GenericTransactionHelper.h

Purpose: Provides a small template trait for retrieving the future type associated with a transaction type, pointer to transaction type, or `Reference<Transaction>` wrapper.

Important APIs/types/functions: Primary template `transaction_future_type<Transaction, T>` aliases `Transaction::FutureT<T>`. Specializations for `Transaction*` and `Reference<Transaction>` recursively resolve to the underlying transaction's future type.

Control flow: Generic templated code can use `typename transaction_future_type<Tr, RangeResult>::type` without caring whether it received a transaction object type, pointer, or Flow `Reference`.

State and persistence behavior: No runtime or persistent state; compile-time type selection only.

Dependencies and integration points: Depends on `flow/FastRef.h` for `Reference`. Supports generic management/transaction helpers and other template code that abstracts over native and external client transaction handles.

Risks: The trait assumes the underlying type exposes `template FutureT<T>`. Missing aliases fail at compile time. Additional smart-pointer wrappers require more specializations.

Test signals: Compile-only tests for raw transaction type, pointer, and `Reference`; use in generic functions returning futures for several payload types.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/GenericTransactionHelper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/GlobalConfig.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/GlobalConfig.h

Purpose: Declares the eventually consistent global configuration framework used to synchronize small typed key-value pairs to clients and servers through database history and GRV proxy refreshes.

Important APIs/types/functions: `VersionHistory` stores a version and mutations for global config history. Extern keys include client transaction sample rate/size limit, transaction tag sampling rate/cost, and sampling frequency/window. `ConfigValue` owns an arena plus `std::any` decoded value. `GlobalConfig` constructs with `DatabaseContext*`, initializes against an `AsyncVar<ClientDBInfo>`, applies transactional changes with `applyChanges()`, prefixes keys with the global config system prefix, reads single/range values, returns arithmetic defaults, exposes `onInitialized()` and `onChange()`, and registers per-key callbacks with `trigger()`.

Control flow: `init()` starts an updater actor and forwards client-info changes to an internal trigger. The updater uses `ClientDBInfo::history` and/or `refresh()` to update the local key-value map. Local `insert()`/`erase()` mutate in-memory config and trigger callbacks; persistent writes must be done by applying mutations to a transaction through `applyChanges()`.

State and persistence behavior: Persistent state lives under `\xff\xff/global_config/<key>` encoded with FDB tuple typecodes. Local state is an unordered map from string refs to `ConfigValue` references, last update version, initialization promise, change trigger, and callbacks. Values containing allocated objects rely on `ConfigValue` arenas for lifetime.

Dependencies and integration points: Depends on commit mutations, FDB types, Flow actors, `DatabaseContext`, `ClientDBInfo`, and `Transaction`. Integrated with GRV proxy `GlobalConfigRefreshRequest/Reply`, `ClientDBInfo::history`, `DatabaseContext::globalConfig`, and sampling/throttling knobs.

Risks: `trigger()` requires keys to be global config string literals to guarantee memory validity. `std::any` casts can fail if decode/type assumptions drift. Large values or too many keys can slow synchronization. Persistent writes that bypass tuple encoding cannot be decoded correctly.

Test signals: Applying insert/clear mutations to transactions; prefix generation; local refresh from version history and full range refresh; callback invocation on set/clear; arithmetic default reads; arena lifetime for object values; GRV proxy refresh integration; initialization/onChange futures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/GlobalConfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/GrvProxyInterface.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/GrvProxyInterface.h

Purpose: Defines the GRV proxy RPC contract for read-version acquisition, health metrics, and global configuration refreshes.

Important APIs/types/functions: `GetReadVersionReply` extends `BasicLoadBalancedReply` with version, locked flag, metadata version, mid-shard size, ratekeeper throttled flags, tag throttle info, storage-server version vector delta, and proxy id. `GetReadVersionRequest` carries span context, transaction count, priority flags, transaction priority, tags, debug id, reply, client max version-vector version, and optional max GRV queue delay. Priority is encoded into high bits of `flags`. `GetHealthMetricsReply/Request` serialize health metrics through a binary string to avoid direct field compatibility issues. `GlobalConfigRefreshReply/Request` return a range result and version for global config state. `GrvProxyInterface` serializes process id, provisional flag, and the primary `getConsistentReadVersion` stream, reconstructing wait-failure, health metrics, and refresh streams as adjusted endpoints.

Control flow: Clients batch or send GRV requests to `getConsistentReadVersion`; deserialization recovers priority from flags. Replies update cached read versions, tag throttles, ratekeeper state, health metrics, and version-vector caches. Global config code asks GRV proxies for refreshes from a last-known version.

State and persistence behavior: Interface state is wire/transient. Health metrics reply stores a serialized binary copy and reconstructs `HealthMetrics` on deserialization. Global config refresh data mirrors persistent global config keyspace but is transported through GRV proxies.

Dependencies and integration points: Depends on tag throttling, version vectors, Flow file identifiers/RPC/load balancing/stats/timed requests, and FDB types. Integrated with `DatabaseContext` GRV batching, ratekeeper throttling, health/status, global config, and commit-proxy client info.

Risks: Priority flag masks overlap by design; incorrect masking can downgrade system-immediate requests. Adjusted endpoint numbering must remain stable. `proxyId` is used to detect stale GRV proxies. Version-vector maxVersion/delta handling affects causal read correctness. Health metrics binary serialization must stay compatible with `IncludeVersion()`.

Test signals: GRV priority encode/decode; tagged and untagged request serialization; ratekeeper throttled reply handling; tag throttle updates; version-vector delta cache updates; health metrics detailed/non-detailed serialization; global config refresh; adjusted endpoint reconstruction.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/GrvProxyInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/HighContentionPrefixAllocator.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/HighContentionPrefixAllocator.h

Purpose: Implements the high-contention prefix allocator used by the directory layer style allocation pattern to choose unique numeric prefixes with low transaction conflict under heavy concurrency.

Important APIs/types/functions: `HighContentionPrefixAllocator` owns `counters` and `recent` subspaces derived from the supplied subspace. Public `allocate()` runs the actor template against a transaction. `windowSize()` grows allocation windows: 64 for starts below 255, 1024 below 65535, then 8192. The private actor reads the highest counter, increments it with `MutationRef::AddValue`, advances windows when half full, samples a random candidate in the current window, writes a marker in `recent`, and adds a write conflict range only on the chosen candidate.

Control flow: Allocation first discovers the current window from the highest counter key. It atomically increments the window counter and reads the count snapshot. If occupancy is too high, it advances the window and clears older counter/recent ranges with `NEXT_WRITE_NO_WRITE_CONFLICT_RANGE`. It then repeatedly samples candidates, writes a no-conflict recent marker, checks whether the current window advanced and whether the candidate was unused, and returns tuple-packed candidate after adding a write conflict on that recent key.

State and persistence behavior: Persistent allocator state lives under the supplied subspace: counter keys by window start and recent keys by candidate. Atomic counter increments are little-endian 8-byte `AddValue` operands. Old windows are cleared as the allocator advances.

Dependencies and integration points: Depends on client boolean params, commit transaction mutations, generated FDB options, subspaces, and Flow unit tests. Used by high-contention directory/prefix allocation code with generic transaction types.

Risks: The code assumes 8-byte counter values; malformed values throw `invalid_directory_layer_metadata`. It relies on no-conflict writes and a final conflict range to reduce contention while preserving uniqueness. Endianness and signed integer interpretation of `AddValue` operands must match FDB atomic op semantics. Random candidate selection can spin under extreme contention.

Test signals: Concurrent allocation uniqueness; window advancement at half-full thresholds; malformed counter value error; old window cleanup; transaction retry behavior; distribution of candidates; tuple-packed prefix compatibility with directory layer consumers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/HighContentionPrefixAllocator.h -->
