# subset-b-007480 research

This grouped report covers the requested Hadoop HDFS files. Each file section is source-tree aligned and delimited for deterministic split into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNodeMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNodeMXBean.java

## Purpose
`JournalNodeMXBean` is the public, evolving JMX management contract for a JournalNode. It exposes read-only operational and storage metadata for the JournalNode process and its managed journals, including formatted state, network identity, cluster membership, Hadoop version, process start time, and journal storage info.

## Important APIs and types
The interface defines only accessors: `getJournalsStatus()`, `getHostAndPort()`, `getClusterIds()`, `getVersion()`, `getJNStartedTimeInMillis()`, and `getStorageInfos()`. Return values are deliberately simple JMX-friendly primitives or `List<String>` values.

## Control flow
There is no implementation logic in this file. Runtime control flow comes from the JournalNode implementation that registers an MXBean and answers JMX calls by aggregating local `Journal` and `JNStorage` state.

## State and persistence
The interface persists nothing. It reflects state held elsewhere: journal formatting status, storage layout/version fields, cluster IDs, and process start timestamp.

## Dependencies and integration points
It depends on Hadoop classification annotations and Java collections. It is consumed by JMX infrastructure and JournalNode management tooling, so method names and return shapes are an external monitoring surface.

## Risks and edge cases
Because status and storage info are serialized as strings, downstream tools can become coupled to formatting that is not type checked. Implementations must also handle multiple clusters per JournalNode and partially formatted journals without throwing from management calls.

## Test signals
Useful tests should verify MXBean registration, stable host/port and version reporting, correct listing of multiple cluster IDs, and robust status output when journals are missing, unformatted, or partially initialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNodeMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNodeRpcServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNodeRpcServer.java

## Purpose
`JournalNodeRpcServer` is the protobuf RPC front door for a JournalNode. It implements both `QJournalProtocol` for NameNode-to-JournalNode quorum journal operations and `InterQJournalProtocol` for JournalNode-to-JournalNode sync/recovery reads.

## Important APIs and types
The constructor builds an `RPC.Server` using `QJournalProtocolPB`, `QJournalProtocolServerSideTranslatorPB`, `InterQJournalProtocolPB`, and `InterQJournalProtocolServerSideTranslatorPB`. Lifecycle methods are `start()`, `join()`, `stop()`, and `getAddress()`. Protocol methods include journal formatting, epoch negotiation, journaling, log segment start/finalize/purge, recovery prepare/accept, manifest retrieval, storage info retrieval, edit cache reads, upgrade/rollback/finalize helpers, and inter-JournalNode manifest retrieval.

## Control flow
Construction copies the configuration, forces TCP_NODELAY for low-latency IPC, resolves the configured RPC bind address, validates the handler count, creates the main QJournal protobuf service, and adds the inter-Journal protocol to the same server. Most protocol methods are thin dispatchers: they resolve the target journal via `jn.getOrCreateJournal(journalId, nameServiceId)` and delegate to `Journal` or `JournalNode` methods. Manifest responses are wrapped with converted protobuf manifests plus HTTP port/URL so clients can download edit logs over HTTP.

## State and persistence
The server owns the RPC listener and configured handler count. Persistent journal state is owned by `Journal`, `JNStorage`, and `JournalNode`; this class only routes operations that mutate that state. It marks `NewerTxnIdException` and `JournaledEditsCache.CacheMissException` as terse exceptions to keep expected read-miss paths from producing noisy RPC logs.

## Dependencies and integration points
It integrates with Hadoop IPC, protobuf RPC engine 2, `HDFSPolicyProvider` for service ACLs, JournalNode HTTP serving, QJM protobuf translators, and storage protocol types such as `NamespaceInfo`, `StorageInfo`, `RemoteEditLogManifest`, and `SegmentStateProto`. It also attaches the JournalNode tracer to the RPC server.

## Risks and edge cases
Misconfigured or nonpositive handler counts are corrected to the default, but an incorrect bind host or address can still prevent service startup. Since most methods create journals on demand, malformed IDs can create unexpected local journal directories. The server exposes powerful upgrade and rollback operations, so service authorization must be enabled correctly in secure deployments.

## Test signals
Tests should cover handler count validation, bind address resolution, service ACL refresh under authorization, terse exception registration, protocol delegation for each Journal operation, manifest response URL/port fields, and inter-JournalNode service availability on the same RPC server.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNodeRpcServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNodeSyncer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNodeSyncer.java

## Purpose
`JournalNodeSyncer` is a background repair daemon for a single JournalNode journal. It periodically contacts peer JournalNodes, compares finalized edit-log manifests, and downloads missing finalized segments into local storage.

## Important APIs and types
Key lifecycle methods are `start(String nsId)`, `stopSync()`, and `isJournalSyncerStarted()`. Important helpers include `getOtherJournalNodeProxies()`, `startSyncJournalsDaemon()`, `formatWithSyncer()`, `syncWithJournalAtIndex()`, `getMissingLogList(...)`, and `downloadMissingLogSegment(...)`. The nested `JournalNodeProxy` wraps an `InterQJournalProtocol` RPC proxy and lazily caches the peer HTTP base URL.

## Control flow
Startup optionally updates the nameservice ID, discovers peer JournalNode addresses from shared-edits configuration, creates inter-Journal RPC proxies, and starts a daemon once. The daemon waits for local formatting; if enabled, it can format from another JournalNode's storage info only after confirming the peer has edit logs, avoiding a race with fresh NameNode formatting. During steady state it creates the `edits.sync` directory, round-robins peers, obtains local and remote manifests, computes missing finalized log segments by comparing start transaction IDs, and downloads each missing segment over HTTP. Downloads go to temporary storage first and are then moved into the current directory with `journal.moveTmpSegmentToCurrent`.

## State and persistence
Runtime state includes `shouldSync`, daemon reference, peer proxies, the current peer index, and whether the daemon started. Persistent effects are local journal formatting and finalized edit-log segment files under `JNStorage`. Temporary files live under the storage sync/current temp paths and are cleaned on shutdown or failed download. Metrics increment via `JournalMetrics.incrNumEditLogsSynced()` after a successful move.

## Dependencies and integration points
The syncer depends on `Journal`, `JournalNode`, `JNStorage`, QJournal inter-node RPC, `GetJournalEditServlet` URL construction, `Util.doGetUrl` transfer logic, secure `doAsLoginUser` execution, optional Kerberos relogin, `DataTransferThrottler`, shared-edits URI parsing, and JournalNode HTTP servers.

## Risks and edge cases
Peer discovery has several configuration fallbacks and can fail if nameservice-specific shared edits URIs disagree. The missing-log comparison assumes sorted manifest lists and compares by start transaction ID, not full segment identity. Formatting from peers is intentionally conservative but still powerful: a wrong peer or nameservice ID could format local storage incorrectly. HTTP host rewriting uses the RPC peer host with the manifest URL scheme/port, which matters behind proxies or unusual bind addresses. Partial downloads must be deleted or later sync attempts may see stale temp files.

## Test signals
Tests should exercise peer address exclusion for the local JournalNode, nameservice-specific config fallback, startup idempotence, formatting disabled/enabled behavior, empty peer manifests, sorted missing-log detection, successful and failed HTTP downloads, temp-file cleanup, throttler configuration, and daemon interruption during shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNodeSyncer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournaledEditsCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournaledEditsCache.java

## Purpose
`JournaledEditsCache` is an in-memory serialized edit cache used by `Journal#getJournaledEdits(long, int)` when in-progress tailing is enabled. It lets clients fetch recent contiguous journaled edits without reading the edit log from disk.

## Important APIs and types
The main methods are `storeEdits(byte[] inputData, long newStartTxn, long newEndTxn, int newLayoutVersion)` and `retrieveEdits(long requestedStartTxn, int maxTxns, List<ByteBuffer> outputBuffers)`. The cache stores a `TreeMap<Long, byte[]>` of batch start transaction ID to serialized edits. `CacheMissException` reports the amount by which the cache missed.

## Control flow
Construction validates the configured cache-size fraction, computes byte capacity from explicit size or JVM heap fraction, initializes a fair read/write lock, and starts empty. `storeEdits` rejects malformed transaction ranges, updates the edit-log layout header when the layout version changes, clears the cache when incoming batches are noncontiguous, evicts oldest batches until the new batch fits, and drops the whole cache if a single batch exceeds capacity. `retrieveEdits` validates that the requested start is cached, appends the serialized header, selects buffers from the floor entry through enough subsequent batches, then trims the first and last buffers by scanning serialized edit operations for exact transaction boundaries.

## State and persistence
All state is memory-only: layout version, serialized header, contiguous batch map, lowest/highest transaction IDs, initial transaction ID since reset, and total byte size. It persists nothing to disk and can be safely treated as an optimization. Locks protect map and metadata, while byte arrays are treated as immutable after insertion.

## Dependencies and integration points
It integrates with `Journal` write and tail-edit RPC paths, `EditLogFileOutputStream.writeHeader`, `FSEditLogOp.Reader`, `FSEditLogLoader.PositionTrackingInputStream`, `JournalMetrics` through cache-miss accounting outside this class, and DFS cache-size configuration keys.

## Risks and edge cases
`retrieveEdits` assumes there is at least one edit buffer after a successful nonempty range validation; callers requesting available but zero `maxTxns` would be risky if not guarded upstream. Transaction boundary trimming scans edit serialization, so corrupt cached bytes or incorrect layout versions surface as `IOException`. Noncontiguous writes reset the cache rather than representing holes, which is appropriate for tailing but can increase cache misses after recovery paths.

## Test signals
Tests should cover capacity validation, layout-version transitions, contiguous and noncontiguous `storeEdits`, over-capacity eviction, oversized single batch clearing, exact trimming across batch boundaries, empty/high-start responses, low-start cache misses with miss amounts, and concurrent reader/writer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournaledEditsCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/NewerTxnIdException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/NewerTxnIdException.java

## Purpose
`NewerTxnIdException` is a small checked exception used when a caller asks for edits newer than the JournalNode currently has available.

## Important APIs and types
It extends `IOException` and has a varargs constructor that formats a message with `String.format`.

## Control flow
There is no internal control flow beyond message formatting. The RPC server registers it as a terse exception, indicating it is an expected protocol condition rather than an operational failure that requires full stack traces.

## State and persistence
The class has no state beyond the inherited exception message and a `serialVersionUID`.

## Dependencies and integration points
It integrates with the QJournal edit retrieval path and Hadoop IPC exception handling. Callers can distinguish "too new" transaction requests from cache misses or other IO failures.

## Risks and edge cases
Because the constructor accepts a format string and arbitrary args, incorrect format strings can throw formatting exceptions at construction time. The exception should be used only for expected availability gaps, not data corruption.

## Test signals
Tests should verify formatted messages, IOException compatibility, and terse RPC logging behavior from `JournalNodeRpcServer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/NewerTxnIdException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockKey.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockKey.java

## Purpose
`BlockKey` is the HDFS-specific key type used to generate and verify block access tokens and data encryption keys. It specializes Hadoop's generic `DelegationKey` without adding new fields.

## Important APIs and types
The class inherits key ID, expiry date, secret-key material, serialization, and equality behavior from `DelegationKey`. It provides constructors for empty keys, `SecretKey` inputs, and encoded byte-array keys.

## Control flow
There is no additional logic. Construction delegates directly to the superclass.

## State and persistence
State is the inherited key ID, expiry timestamp, and encoded secret. Persistence is inherited Writable serialization through `DelegationKey`, and is used by `ExportedBlockKeys`.

## Dependencies and integration points
It is produced and consumed by `BlockTokenSecretManager`, transported in `ExportedBlockKeys`, and used by DataNodes, NameNodes, balancer, and data-transfer encryption paths.

## Risks and edge cases
Because it is only a typed wrapper, all correctness depends on the superclass serialization and careful lifecycle management in `BlockTokenSecretManager`. Null or empty key material can be represented by the parent class and must be handled by callers.

## Test signals
Tests should cover constructor parity with `DelegationKey`, Writable round trips through `ExportedBlockKeys`, and compatibility when encoded key bytes are used instead of `SecretKey`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockPoolTokenSecretManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockPoolTokenSecretManager.java

## Purpose
`BlockPoolTokenSecretManager` multiplexes one `BlockTokenSecretManager` per HDFS block pool. It lets common token code route generation, verification, key import, and data encryption key operations by block pool ID.

## Important APIs and types
The class extends `SecretManager<BlockTokenIdentifier>`. It exposes `addBlockPool`, `get`, `isBlockPoolRegistered`, `createIdentifier`, `createPassword`, `retrievePassword`, multiple `checkAccess` overloads, `addKeys`, `generateToken`, `generateDataEncryptionKey`, and `retrieveDataEncryptionKey`.

## Control flow
Each public operation derives the block pool ID either from the token identifier, the `ExtendedBlock`, or an explicit argument, then dispatches to the registered `BlockTokenSecretManager`. Missing block pools fail fast with `IllegalArgumentException`. The map is a `ConcurrentHashMap`, so reads and registrations can occur concurrently.

## State and persistence
The only local state is the in-memory block-pool-to-secret-manager map. Key material, token passwords, and encryption keys are held in the per-pool managers and are not persisted here.

## Dependencies and integration points
It integrates with the NameNode/DataNode block token subsystem, `ExtendedBlock`, `BlockTokenIdentifier`, `Token`, storage-type and storage-ID constraints, and data transfer encryption. Federated or multi-block-pool deployments rely on this router to keep token keys isolated by pool.

## Risks and edge cases
Operations against unregistered pools throw unchecked exceptions, so callers must ensure registration before serving traffic. There is no removal path, which is acceptable for stable block pools but matters for tests or long-lived dynamic setups. Cross-pool misuse is guarded by routing through the block's pool ID and downstream identifier checks.

## Test signals
Tests should verify routing for every overload, missing-pool errors, concurrent registration/read behavior, clear-all test helper behavior, and that token/password/encryption-key operations never leak to the wrong block pool.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockPoolTokenSecretManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockTokenSecretManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockTokenSecretManager.java

## Purpose
`BlockTokenSecretManager` manages HDFS block access token secrets. In master mode, typically in a NameNode, it generates and rotates block keys and exports them. In worker mode, typically in DataNodes and clients such as the balancer, it imports exported keys and verifies or generates tokens with the current key.

## Important APIs and types
Constructors distinguish worker mode from master mode and support HA NameNode key ID ranges. Key lifecycle methods are `generateKeys`, `exportKeys`, `addKeys`, `updateKeys`, and `removeExpiredKeys`. Token APIs include `generateToken`, `createPassword`, `retrievePassword`, `checkAccess` overloads, and `isTokenExpired`. Data encryption APIs are `generateDataEncryptionKey` and `retrieveDataEncryptionKey`.

## Control flow
Master construction computes a unique serial-number range from NameNode index and number of NameNodes, seeds a serial number, and generates current/next keys. `updateKeys` retires the old current key with a shorter final expiry, promotes `nextKey`, and creates a new future key. Worker `addKeys` removes expired keys, optionally updates the current key, and merges received key material. Token generation creates a `BlockTokenIdentifier` for user, block pool, block ID, access modes, storage types, and storage IDs; optionally wraps the established RPC QOP in the identifier. Verification deserializes token identifiers when needed, checks user/block/pool/expiry/mode/storage constraints, and recomputes HMAC-like passwords with the referenced `BlockKey`.

## State and persistence
State is in memory: `currentKey`, `nextKey`, `allKeys`, key update interval, token lifetime, serial number range, block pool ID, encryption algorithm, proto-token flag, QOP wrapping flag, random nonce generator, and testable `Timer`. Persistent transfer of key material occurs through `ExportedBlockKeys`; this class itself does not write storage.

## Dependencies and integration points
It depends on Hadoop `SecretManager`, `Token`, `BlockTokenIdentifier`, `ExtendedBlock`, `DataEncryptionKey`, storage types, server-side QOP, `UserGroupInformation`, `Timer`, and crypto primitives inherited from `SecretManager`. It is central to DataTransferProtocol authorization and encryption.

## Risks and edge cases
Incorrect HA `nnIndex` or `numNNs` can produce overlapping key ID ranges if configuration is wrong. Worker mode silently ignores `addKeys` when called on a master or with null exported keys. Missing keys cause token verification and data encryption key reconstruction failures, so clock skew and key distribution delays affect live IO. The static storage constraint checker allows empty candidate lists to mean unrestricted token side, but rejects empty requested lists as a likely configuration error.

## Test signals
Tests should cover master/worker constructor behavior, serial range partitioning, key rotation timing, export/import round trips, expired key removal, token creation and password retrieval, user/block/pool/mode/storage mismatch failures, QOP wrapping, data encryption key reconstruction, and timer-driven expiry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/block/BlockTokenSecretManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/block/ExportedBlockKeys.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/block/ExportedBlockKeys.java

## Purpose
`ExportedBlockKeys` is the Writable transport object for distributing block token key material and timing parameters from a master `BlockTokenSecretManager` to worker-side managers.

## Important APIs and types
Fields include `isBlockTokenEnabled`, `keyUpdateInterval`, `tokenLifetime`, `currentKey`, and `allKeys`. Accessors expose each field. Writable methods `write(DataOutput)` and `readFields(DataInput)` serialize the enabled flag, intervals, current key, key count, and each `BlockKey`. `DUMMY_KEYS` represents disabled or empty keys.

## Control flow
Constructors normalize null current keys to an empty `BlockKey` and null arrays to empty arrays. Static initialization registers a `WritableFactory` for reflective construction. Deserialization mutates the final `currentKey` by reading into it and replaces the `allKeys` array with newly constructed keys.

## State and persistence
The object is itself serialized state for block-token key distribution. It is not durable storage by itself, but its Writable representation crosses RPC and can be embedded in other persistent or transmitted structures.

## Dependencies and integration points
It depends on Hadoop `Writable` and `WritableFactories` and is consumed by `BlockTokenSecretManager.addKeys` and `BlockPoolTokenSecretManager.addKeys`. It is a compatibility-sensitive wire format.

## Risks and edge cases
There is no defensive copy in getters, so callers can mutate the returned key array. Deserialization trusts the incoming key count; invalid or huge counts can cause allocation pressure before higher-level validation. A disabled-key object can still contain key-like defaults, so callers should honor `isBlockTokenEnabled`.

## Test signals
Tests should verify Writable round trips, null normalization, factory registration, dummy-key behavior, and compatibility of serialized ordering with older readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/block/ExportedBlockKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/delegation/DelegationTokenSecretManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/delegation/DelegationTokenSecretManager.java

## Purpose
`DelegationTokenSecretManager` is the HDFS-specific `AbstractDelegationTokenSecretManager` implementation for NameNode delegation tokens. It manages token passwords, persisted token/key state, edit-log updates, HA standby behavior, and credential creation.

## Important APIs and types
Public APIs include constructors, `createIdentifier`, `retrievePassword`, `retriableRetrievePassword`, `getTokenExpiryTime`, compatibility and protobuf fsimage load/save methods, persisted token/key update methods, `getNumberOfKeys`, and static `createCredentials`. `SecretManagerState` carries protobuf fsimage state, while nested `SerializerCompat` handles legacy Writable fsimage format.

## Control flow
Token password retrieval first asks `FSNamesystem` whether a READ operation is allowed. A standby exception is wrapped as `InvalidToken` in the legacy method but surfaced directly in `retriableRetrievePassword`; during transition to active, unknown-token errors become `RetriableException` so clients can retry while edit logs catch up. Loading state is allowed only when the secret manager is not running. Protobuf loading restores current key/token sequence fields, all keys, then persisted tokens. Saving creates a `SecretManagerSection` plus key and token protobuf lists. Persisted add/renew/cancel methods replay fsimage/edit-log records into `currentTokens`. Key and token expiry logging acquire the FSNamesystem read lock and synchronize on `noInterruptsLock` to avoid interruption during edit-log sync.

## State and persistence
Core mutable state is inherited: current master key ID, delegation token sequence number, `allKeys`, `currentTokens`, running flag, and tracking-ID option. This class persists that state to fsimage in protobuf and legacy formats and writes key/token expiry changes to the NameNode edit log through `FSNamesystem`.

## Dependencies and integration points
It integrates tightly with `FSNamesystem`, `NameNode`, startup progress reporting, fsimage protobufs, delegation token identifiers, `Credentials`, `SecurityUtil`, `UserGroupInformation`, edit logs, HA operation gating, and RPC token authentication.

## Risks and edge cases
State-loading methods intentionally refuse to run while active; bypassing that would corrupt live token maps. Persisted tokens whose master key is missing are skipped with a warning, which can invalidate client tokens after image/edit-log inconsistency. The legacy `retrievePassword` standby wrapping is a compatibility hack that depends on RPC unwrapping. Interrupt handling in edit-log logging is delicate because interrupted log sync can close edit files.

## Test signals
Tests should cover protobuf and legacy fsimage round trips, edit-log replay add/renew/cancel, missing master-key behavior, duplicate persisted token failure, standby and transition-to-active password retrieval, credential creation with token service, startup progress counters, and interruption behavior around master-key/token-expiry logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/security/token/delegation/DelegationTokenSecretManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/aliasmap/InMemoryAliasMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/aliasmap/InMemoryAliasMap.java

## Purpose
`InMemoryAliasMap` implements `InMemoryAliasMapProtocol` using LevelDB to map HDFS `Block` records to `ProvidedStorageLocation` records. It supports provided storage alias lookup plus snapshot/archive transfer for standby NameNode bootstrap.

## Important APIs and types
Main protocol methods are `list(Optional<Block>)`, `read(Block)`, `write(Block, ProvidedStorageLocation)`, and `getBlockPoolId`. Static helpers initialize the LevelDB store, convert blocks and locations to/from protobuf bytes, transfer a bootstrap archive, create a snapshot copy, compress the snapshot as tar.gz, recursively archive files while skipping LevelDB `LOCK`, and complete bootstrap extraction.

## Control flow
`init` reads the configured LevelDB directory, appends the block pool ID when present, creates missing directories, opens LevelDB, and returns a configured alias map. `list` seeks to the marker or first key, reads up to the configured batch size, converts each LevelDB key/value pair into `FileRegion`, and returns an optional next marker when more entries remain. `read` gets one key and converts the value if present. `write` serializes both sides and stores them in LevelDB. Bootstrap transfer creates a consistent snapshot DB using a LevelDB snapshot iterator, archives the block-pool directory, sets HTTP verification/file-name headers, streams the tarball, and deletes temporary artifacts.

## State and persistence
Persistent state is LevelDB data under the configured alias map directory, optionally scoped by block pool ID. Runtime state is the opened DB handle, URI, config, and block pool ID. Snapshot transfer creates temporary `aliasmap_snapshot` and `aliasmap.tar.gz` files and cleans them in a finally block.

## Dependencies and integration points
It depends on LevelDB JNI, HDFS protocol protobuf conversion, provided-storage `FileRegion`, NameNode `ImageServlet`/`TransferFsImage` bootstrap transfer utilities, compression/archive libraries, `DataTransferThrottler`, and Hadoop configuration keys for alias map directory and batch size.

## Risks and edge cases
The class name says in-memory, but persistence is LevelDB; operational expectations must account for local disk state. `list` uses the marker as an inclusive seek and then selects a next marker by consuming one additional iterator entry, so callers must follow protocol semantics carefully to avoid duplicates or skips. Snapshot creation copies all K/V pairs and can be expensive for large maps. Cleanup errors after transfer are aggregated and thrown, which may surface after a successful stream copy.

## Test signals
Tests should cover missing directory creation, missing config error, read/write round trips, ordered paginated list behavior with markers and batch sizes, protobuf conversion failures, snapshot consistency while writes occur, archive contents excluding `LOCK`, bootstrap extraction, HTTP transfer headers, throttling, and cleanup failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/aliasmap/InMemoryAliasMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/aliasmap/InMemoryAliasMapProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/aliasmap/InMemoryAliasMapProtocol.java

## Purpose
`InMemoryAliasMapProtocol` defines the RPC-facing contract for reading, writing, and scanning provided-storage block aliases in an in-memory/LevelDB alias map implementation.

## Important APIs and types
The nested `IterationResult` contains a batch of `FileRegion` values and an optional next `Block` marker. Protocol methods are idempotent `list(Optional<Block>)`, `read(Block)`, `write(Block, ProvidedStorageLocation)`, and `getBlockPoolId()`.

## Control flow
The interface has no implementation. Implementations are expected to paginate `list`, return `Optional.empty()` on read miss, store a block-to-location association on write, and identify the associated block pool.

## State and persistence
No state is held here. Implementations provide storage behavior, and the protocol shape exposes only batch results and block-pool identity.

## Dependencies and integration points
It integrates with Hadoop retry annotations, HDFS `Block`, `ProvidedStorageLocation`, and `FileRegion` types, and the protobuf alias map translator/server stack.

## Risks and edge cases
`write` is annotated idempotent, which assumes repeated writes for the same block/location are safe. Pagination correctness depends on marker semantics shared by clients and server implementations. Optional return values must be preserved correctly through protobuf translation.

## Test signals
Tests should verify protocol translator round trips for empty and nonempty optionals, pagination markers, repeated writes, read misses, and block-pool ID exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/aliasmap/InMemoryAliasMapProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/aliasmap/InMemoryLevelDBAliasMapServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/aliasmap/InMemoryLevelDBAliasMapServer.java

## Purpose
`InMemoryLevelDBAliasMapServer` is the RPC server wrapper that exposes an `InMemoryAliasMap` over Hadoop protobuf IPC for NameNode and alias-map clients.

## Important APIs and types
The constructor accepts a checked initialization function and block pool ID. `setConf` initializes the underlying alias map. `start` builds and starts an `RPC.Server` for `AliasMapProtocolPB`. Protocol methods delegate `list`, `read`, `write`, and `getBlockPoolId` to the alias map. `close` shuts down the DB and RPC server.

## Control flow
On configuration, the server calls the injected `initFun` and wraps IO failures in `RuntimeException`, matching Hadoop `Configurable` constraints. Startup sets protobuf RPC engine, creates a server-side translator and reflective blocking service, resolves bind address and verbosity from DFS alias-map keys, builds the single-handler RPC server, and starts it. Close first tries to close the alias map, logs errors, then stops RPC.

## State and persistence
Runtime state includes configuration, RPC server handle, initialized alias map, and block pool ID. Persistent state is owned by the underlying `InMemoryAliasMap` LevelDB store.

## Dependencies and integration points
It depends on Hadoop IPC, protobuf alias map protocol classes, `DFSUtil.getBindAddress`, alias map configuration keys, and the protocol translator. It is the service entry point for provided-storage alias-map RPC.

## Risks and edge cases
Initialization errors become unchecked during `setConf`, which can fail service construction late. Only one handler is configured, so high-concurrency alias map workloads may bottleneck. `close` logs alias-map close errors but still stops RPC, which can mask DB close failures from callers.

## Test signals
Tests should cover address binding, verbose flag propagation, init function failure, delegation of all protocol methods, block-pool ID consistency, close ordering, and server behavior when `start` is called before a valid configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/aliasmap/InMemoryLevelDBAliasMapServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/Balancer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/Balancer.java

## Purpose
`Balancer` is the command-line and service implementation that rebalances HDFS disk utilization by moving blocks from over-utilized DataNode storage groups to under-utilized ones. It implements `BalancerMXBean` for version metadata and coordinates NameNode connectors, dispatch scheduling, metrics, optional HTTP UI, and CLI parsing.

## Important APIs and types
Core instance methods include the constructor, `runOneIteration`, `init`, `chooseStorageGroups`, `matchSourceWithTargetToMove`, `resetData`, and MXBean getters. Static orchestration methods include `run`, `doBalance`, `stop`, `startBalancerHttpServer`, `checkKeytabAndInit`, and `time2Str`. Nested `Result` records per-iteration outcome and counters. Nested `Cli` parses options and invokes the balancer through `ToolRunner`.

## Control flow
Construction validates relevant config values, creates a `Dispatcher`, stores filter/policy parameters, creates metrics, and registers the MXBean. Each iteration asks the dispatcher for DataNode storage reports, uses the selected `BalancingPolicy` to compute average utilization per storage type, classifies storage groups into over-utilized, above-average, below-average, and under-utilized collections, optionally sorts or limits over-utilized sources, and computes bytes left to move. If the cluster is already balanced or upgrade state forbids movement, it exits early. Otherwise it matches sources and targets by node group, rack, then any other topology, schedules tasks on sources/targets, and asks the dispatcher to move blocks until no progress or completion.

## State and persistence
Instance state is iteration-local scheduler state plus references to `Dispatcher`, `NameNodeConnector`, policy, filters, threshold, movement limits, metrics, and MXBean name. The shared persistent coordination marker is `/system/balancer.id`, created through `NameNodeConnector` to prevent concurrent balancers. The class does not persist moved-block state; it relies on NameNode block maps and DataNode storage reports.

## Dependencies and integration points
It integrates with `Dispatcher`, `NameNodeConnector`, block placement policy validation, NameNode RPC URIs, DataNode storage reports, `StorageType`, Hadoop metrics, MBeans, optional `BalancerHttpServer`, Kerberos login, host-list parsing, DFS configuration keys, and command-line scripts. It requires `BlockPlacementPolicyDefault` for contiguous blocks.

## Risks and edge cases
Balancing decisions are based on periodically refreshed reports, so concurrent client writes/deletes can make target utilization drift. Running during an unfinalized upgrade is blocked by default because moved source blocks may not reclaim space. Include/exclude/source/target filters can make a cluster appear unbalanceable. The service mode uses a static `serviceRunning` flag and retry counters, so tests must reset global state. Limiting over-utilized nodes after computing overload bytes can change scheduled work without recalculating the earlier byte estimate.

## Test signals
Tests should cover CLI parsing and mutual exclusion of host filters, threshold bounds, block-pool filtering, policy compatibility failures, utilization classification, source/target matching by topology level, max bytes-to-move calculations, upgrade blocking, no-move and no-progress exits, metrics/MXBean registration cleanup, service-mode duplicate start prevention, keytab login, and HTTP server lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/Balancer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancerHttpServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancerHttpServer.java

## Purpose
`BalancerHttpServer` starts the optional web server used by the HDFS balancer for HTTP/HTTPS status pages and servlet/JSP integration.

## Important APIs and types
Main methods are `start`, `setBalancerAttribute`, `stop`, `getHttpAddress`, and `getHttpsAddress`. It stores the current balancer under the `current.balancer` attribute and publishes configuration under `JspHelper.CURRENT_CONF`.

## Control flow
`start` resolves HTTP and HTTPS socket addresses from balancer-specific DFS keys, creates an `HttpServer2.Builder` through `DFSUtil.getHttpServerTemplate`, applies X-Frame options, builds and starts the server, then updates configuration with the actual bound connector addresses based on the selected HTTP policy. `stop` wraps server stop exceptions in `IOException`.

## State and persistence
Runtime state is configuration, bound HTTP/HTTPS addresses, and the `HttpServer2` instance. It persists nothing.

## Dependencies and integration points
It integrates with Hadoop `HttpServer2`, DFS HTTP policy and security template, SPNEGO/keytab configuration, `JspHelper`, `NetUtils`, and `Balancer` status exposure.

## Risks and edge cases
Connector index handling depends on HTTP policy ordering. If the server binds to port 0, the config is updated only after startup. Stop can throw if the underlying server stop fails. The balancer attribute must be set after a `Balancer` instance is created for UI code to see current state.

## Test signals
Tests should verify HTTP-only, HTTPS-only, and dual connector address updates; X-Frame config propagation; SPNEGO/keytab key usage; balancer attribute visibility; and stop behavior with and without a started server.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancerHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancerMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancerMXBean.java

## Purpose
`BalancerMXBean` defines the JMX management contract for balancer version and build metadata.

## Important APIs and types
It declares `getVersion()`, `getSoftwareVersion()`, and `getCompileInfo()`. `Balancer` implements these using `VersionInfo`.

## Control flow
There is no implementation flow in the interface. Runtime calls are made through JMX after `Balancer` registers itself with `MBeans.register("Balancer", "BalancerInfo", this)`.

## State and persistence
No state is held or persisted. Values reflect static Hadoop version/build metadata at runtime.

## Dependencies and integration points
It integrates with Hadoop metrics/JMX registration from `Balancer` and management tools that inspect balancer process metadata.

## Risks and edge cases
The contract is intentionally small, but external monitoring can depend on exact method availability. Implementations must avoid throwing from these simple metadata calls.

## Test signals
Tests should verify MBean registration exposes all three fields and that `Balancer.resetData` unregisters the MBean.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancerMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancerMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancerMetrics.java

## Purpose
`BalancerMetrics` registers per-balancer Hadoop metrics for iteration activity, bytes left, bytes moved, and counts of over/under-utilized nodes.

## Important APIs and types
The class is annotated with `@Metrics(context="dfs")`. It exposes a tag-like metric `getBlockPoolID()`, gauge-backed setters for iterate-running, bytes-left, under-utilized node count, and over-utilized node count, and a computed metric `getBytesMovedInCurrentRun()`.

## Control flow
`create` registers a new metrics source with `DefaultMetricsSystem` under a name derived from the block pool ID. `Balancer` updates the gauges during initialization and `runOneIteration`, and removes the source name during `resetData`.

## State and persistence
Runtime state is the `Balancer` reference and mutable gauge objects supplied by the metrics system. It persists nothing.

## Dependencies and integration points
It integrates with Hadoop metrics2 annotations, `DefaultMetricsSystem`, `MutableGaugeInt`, `MutableGaugeLong`, `Balancer`, and `NameNodeConnector` counters.

## Risks and edge cases
Metrics source names include block pool ID; duplicate registration without cleanup can fail or overwrite depending on metrics system behavior. The bytes moved metric reads from the connector live, so it reflects current run counters rather than a latched gauge.

## Test signals
Tests should cover source registration names, gauge updates, block-pool tag value, bytes-moved computation, and cleanup when balancer iteration resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancerMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancerParameters.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancerParameters.java

## Purpose
`BalancerParameters` is an immutable parameter bundle for the balancer CLI and run loop. It captures balancing policy, thresholds, host filters, block-pool filters, service-mode flags, and scheduling options.

## Important APIs and types
The class exposes getters for policy, threshold, max idle iteration, included/excluded nodes, source/target include/exclude sets, block pools, upgrade behavior, service mode, top-node sorting, over-utilized limit, and hot-block time interval. The nested `Builder` provides setters for each option and `build()`.

## Control flow
Defaults are defined in the builder: node-level policy, threshold 10.0, default max idle iterations from `NameNodeConnector`, empty filter sets, not running during upgrade, not service mode, no top sorting, unlimited over-utilized nodes, and zero hot-block interval meaning "use configuration". `Balancer.Cli.parse` mutates a builder according to command-line options and then builds an immutable instance.

## State and persistence
State is in-memory immutable after construction, except the sets themselves are stored by reference and are not defensively copied. There is no persistence.

## Dependencies and integration points
It integrates with `Balancer`, `BalancingPolicy`, `NameNodeConnector`, and CLI parser host/block-pool option handling.

## Risks and edge cases
Because sets are not copied or wrapped by the constructor, callers could mutate parameter contents after build. Defaults use `Collections.emptySet`, which is immutable, but parser-created sets are mutable. `limitOverUtilizedNum` default is `Integer.MAX_VALUE`, effectively no limit.

## Test signals
Tests should verify all defaults, each builder setter, `toString` coverage, parser-to-parameter mapping, and that mutable input sets can affect built parameters if changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancerParameters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancingPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancingPolicy.java

## Purpose
`BalancingPolicy` defines how the balancer computes utilization. It supports node-level balancing across all block pools and block-pool-level balancing for each pool on each node.

## Important APIs and types
Shared counters are `totalCapacities`, `totalUsedSpaces`, and `avgUtilizations`, keyed by `StorageType`. Abstract methods are `getName`, `accumulateSpaces`, and `getUtilization`. Shared helpers are `reset`, `initAvgUtilization`, `getAvgUtilization`, and `parse`. Concrete singleton policies are `Node.INSTANCE` and `Pool.INSTANCE`.

## Control flow
The balancer calls `accumulateSpaces` for every `DatanodeStorageReport`, then `initAvgUtilization` computes average utilization per storage type. It later calls `getUtilization` for each node/storage type to classify storage groups. `parse` maps CLI names `datanode` and `blockpool` to singleton policies.

## State and persistence
Policy instances hold mutable counters and averages across one balancer iteration and are reset between iterations by `Balancer.resetData`. They persist nothing. Since the concrete policies are singletons, reset discipline is important.

## Dependencies and integration points
It depends on `StorageType`, `DatanodeStorageReport`, `StorageReport`, `EnumCounters`, and `EnumDoubles`. It directly drives `Balancer.init` classification and byte estimates.

## Risks and edge cases
The singleton policy objects are mutable, so concurrent balancer runs sharing the same JVM could interfere if they use the same policy instance. The pool policy uses `remaining + blockPoolUsed` as capacity to avoid targeting nodes with little free space; this intentionally differs from raw disk capacity and changes scheduling behavior. Zero-capacity storage types produce null utilization.

## Test signals
Tests should verify policy parsing, reset behavior, average utilization by storage type, node policy aggregation across storage reports, pool policy use of block-pool-used plus remaining, null utilization on absent storage types, and singleton mutation isolation across iterations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancingPolicy.java -->
