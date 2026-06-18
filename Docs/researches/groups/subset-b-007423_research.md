# Research Report: subset-b-007423

Grouped research for Hadoop HDFS client protocol files under `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol`. Each section preserves the source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ClientProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ClientProtocol.java

## Purpose
`ClientProtocol` is the central private/evolving Java interface used by `DFSClient` and `DistributedFileSystem` to talk to the NameNode while insulating callers from the protobuf wire protocol. Its comments explicitly require any interface change to be mirrored in `ClientNamenodeProtocol.proto`; `versionID` is fixed at `69L` because this class no longer directly drives serialization versioning. It covers file I/O, namespace mutation, leases, block allocation, snapshots, cache directives, ACLs, xattrs, encryption zones, erasure coding, HA/read consistency, and administrative operations.

## Important APIs and Control Flow
The interface is organized around RPC families. File content APIs include `getBlockLocations`, `create`, `append`, `addBlock`, `getAdditionalDatanode`, `complete`, `abandonBlock`, `updateBlockForPipeline`, and `updatePipeline`. Namespace APIs include `rename`, `rename2`, `concat`, `truncate`, `delete`, `mkdirs`, and listing/status calls. Admin/stat APIs include safe mode, namespace save/roll, datanode reports, storage policies, quotas, rolling upgrade, slow datanode reports, and edit-log/inotify calls. Security and metadata APIs include delegation tokens, data encryption keys, snapshots, cache pools/directives, ACLs, xattrs, encryption zones, re-encryption, EC policy management, open-file listing, `msync`, and `getEnclosingRoot`.

## State, Persistence, and Dependencies
The interface does not store state itself; state is held in the NameNode namespace, edit log, block manager, lease manager, cache manager, encryption zone manager, and EC policy manager. Annotations such as `@Idempotent`, `@AtMostOnce`, and `@ReadOnly` are critical integration metadata for retry, HA observer routing, and failover behavior. Return and parameter DTOs in this subset include `LocatedBlocks`, `LocatedBlock`, `LastBlockWithStatus`, `HdfsFileStatus`, `DirectoryListing`, `CorruptFileBlocks`, `DatanodeInfo`, `ECBlockGroupStats`, `ReplicatedBlockStats`, `RollingUpgradeInfo`, `EncryptionZone`, `ErasureCodingPolicy`, and `OpenFileEntry`.

## Integration Points
Callers are primarily `DFSClient`, `DistributedFileSystem`, admin tools, and Router-Based Federation forwarding paths. The protocol integrates with Kerberos and delegation tokens via `@KerberosInfo` and `@TokenInfo`; with HA via `ReadOnly` annotations and `HAServiceProtocol.HAServiceState`; and with tracing/listing iterators through batched APIs. Many methods are documented as active-only or coordinated reads because observer/standby NameNodes may not have sufficiently fresh quota, atime, or alignment state.

## Risks and Test Signals
The highest risk is RPC contract drift between this interface and protobuf definitions. Retry semantics must match side effects: mutating calls marked `@AtMostOnce` should not be retried blindly, while idempotent calls must remain truly idempotent. Tests should cover client retry/failover, active-only routing, namespace write rejection in safe mode/snapshots, lease recovery retry loops, block pipeline recovery, batched listing cursors, ACL/xattr/encryption permission enforcement, EC policy lifecycle, and compatibility of stats-array indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ClientProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CorruptFileBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CorruptFileBlocks.java

## Purpose
`CorruptFileBlocks` is a small immutable response object for `ClientProtocol.listCorruptFileBlocks`. It carries a batch of corrupt file paths plus a cookie used as the cursor for subsequent calls.

## APIs and Behavior
The default constructor returns an empty file array and empty cookie. The primary constructor stores `String[] files` and `String cookie`, exposed through `getFiles()` and `getCookie()`. Equality requires both cookie equality and array-content equality via `Arrays.equals`; `hashCode()` folds each file into the cookie hash using a fixed prime.

## State, Dependencies, and Integration
There is no persistence or control flow beyond value comparison. The class depends only on `java.util.Arrays` and is serialized through the HDFS client protocol conversion layer. It is consumed by admin and fsck-like clients that repeatedly call NameNode corrupt-file listing until the returned cookie/list indicates exhaustion.

## Risks and Test Signals
The constructor does not defensively copy `files`, so callers retaining the original array can mutate an instance after construction. Tests should cover empty responses, repeated-cookie pagination, equality/hash consistency, and mutation hazards if the object is stored in maps or caches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CorruptFileBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DSQuotaExceededException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DSQuotaExceededException.java

## Purpose
`DSQuotaExceededException` specializes `QuotaExceededException` for disk-space quota violations. It is part of the public/evolving HDFS exception surface and is thrown by namespace operations such as create, append, replication changes, and rename when storage-space quota would be exceeded.

## APIs and Behavior
The class provides default, message, and `(quota, count)` constructors. `getMessage()` delegates to the superclass when an explicit message exists; otherwise it builds a detailed disk-space message using inherited `pathName`, `quota`, and `count`, including both raw bytes and human-readable binary-prefix strings via `long2String`.

## State, Dependencies, and Integration
State is inherited from `QuotaExceededException`. The exception is serialized across RPC as part of NameNode error propagation and is expected by client-side code that distinguishes namespace quota from disk-space quota. No persistence happens in this class.

## Risks and Test Signals
Formatting is user-visible and should remain stable enough for diagnostics, though callers should not parse it. Tests should cover explicit-message preservation, null and non-null `pathName`, large byte values, and correct propagation through create/append/setReplication RPC failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DSQuotaExceededException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeAdminProperties.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeAdminProperties.java

## Purpose
`DatanodeAdminProperties` models static administrator-specified host configuration for datanode administration. The class is used by `CombinedHostFileManager` to deserialize JSON-based host include/exclude configuration and differs from runtime `DatanodeInfo` state.

## APIs and Behavior
It exposes JavaBean-style getters and setters for `hostName`, `port`, `upgradeDomain`, `adminState`, and `maintenanceExpireTimeInMS`. Defaults are `AdminStates.NORMAL` and `Long.MAX_VALUE` for maintenance expiry. The comments specify `AdminStates.DECOMMISSIONED` for decommission configuration.

## State, Dependencies, and Integration
The class is mutable and intentionally simple for configuration binding. Its key dependency is `DatanodeInfo.AdminStates`, so configured states map directly to runtime administrative state names. Persistence happens outside this class in the JSON host file and NameNode host manager.

## Risks and Test Signals
There is no validation for host name, port range, or maintenance times. Tests should cover JSON deserialization defaults, explicit decommission/maintenance states, upgrade domain propagation into runtime reports, and behavior when invalid ports or null states are supplied by configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeAdminProperties.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeID.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeID.java

## Purpose
`DatanodeID` is the primary identity/contact descriptor for a DataNode. It combines IP address, host name, peer host name, data-transfer/IPC/info ports, transfer address cache, and the DataNode UUID used to identify the node across registrations and block ownership.

## APIs and Behavior
Constructors copy from another `DatanodeID` or accept explicit network fields. The class caches UTF-8 `ByteString` forms for protobuf serde and caches `xferAddr` after `setIpAndXferPort`. Public accessors expose IP, host, peer host, transfer, info, secure info, and IPC addresses, with hostname/IP selection helpers. `updateRegInfo()` updates contact fields from a new registration but intentionally does not update the UUID. `compareTo()` orders by transfer address.

## State, Dependencies, and Integration
The object is mutable for registration contact fields but immutable for `datanodeUuid`. It integrates with protobuf through `ByteString`, client/network code through `InetSocketAddress`, and `DatanodeInfo`, which extends it. Equality requires both transfer address equality and UUID equality; hash code is based on UUID.

## Risks and Test Signals
`checkDatanodeUuid()` normalizes null/empty UUID to `null`, but `equals()` and `hashCode()` dereference `datanodeUuid`, so placeholder or not-yet-assigned IDs can throw if used in hashed collections. Tests should cover registration updates, hostname/IP address formatting, UUID preservation, byte-string cache consistency, equality/hash behavior with null UUIDs, and sorted ordering by transfer address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeID.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeInfo.java

## Purpose
`DatanodeInfo` extends `DatanodeID` with runtime DataNode state returned to clients and admin tools: capacity, DFS/non-DFS/block-pool/cache usage, heartbeat and block-report timestamps, xceiver count, rack, upgrade domain, dependent hosts, software version, block count, and administrative state.

## APIs and Control Flow
The `AdminStates` enum covers normal, decommissioning, decommissioned, entering maintenance, and in maintenance. Methods compute usage percentages through `DFSUtilClient`, format detailed and compact reports, mutate admin state through decommission/maintenance methods, test stale heartbeat state with `Time.monotonicNow()`, and implement `Node` topology methods (`parent`, `level`, `networkLocation`). The nested `DatanodeInfoBuilder` creates complete instances from raw values or an existing node.

## State, Dependencies, and Integration
Most fields are mutable snapshots from NameNode heartbeat/block-report tracking. Rack location is normalized with `NodeBase.normalize`; report formatting uses `NetUtils`, `StringUtils`, and `Date`. Equality delegates to `DatanodeID`, so runtime metrics do not affect identity. `DatanodeInfoWithStorage`, reports from `ClientProtocol`, block locations, and admin commands all depend on this shape.

## Risks and Test Signals
The builder’s `setFrom()` comment says `numBlocks` must be set explicitly, but the method copies `lastBlockReport` fields and omits dependent hosts; copying semantics should be tested. `adminState == null` means normal, which is compact but can surprise serializers. Tests should cover percent calculations with zero capacity, stale detection using monotonic time, state transitions for maintenance/decommission, report text, topology parent/level behavior, and equality ignoring mutable metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeInfoWithStorage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeInfoWithStorage.java

## Purpose
`DatanodeInfoWithStorage` augments `DatanodeInfo` with the specific storage ID and `StorageType` for a replica. It is used inside `LocatedBlock` so clients know which DataNode storage contains a block replica.

## APIs and Behavior
The constructor copies a `DatanodeInfo`, assigns `storageID` and `storageType`, and explicitly carries over software version, dependent hosts, topology level, and parent. `getStorageID()` and `getStorageType()` expose the extra fields. `equals()` and `hashCode()` deliberately delegate to `DatanodeInfo` so the object can be used interchangeably with the base DataNode identity; `toString()` includes storage metadata.

## State, Dependencies, and Integration
It is immutable with respect to storage metadata but inherits mutable DataNode fields. It depends on `StorageType` and is integrated into block-location conversion, cached storage arrays, and provided-storage sorting.

## Risks and Test Signals
Equality ignores storage ID/type, which is intentional but risky in sets/maps where multiple storages on the same DataNode must be represented distinctly. Tests should cover interchangeability with `DatanodeInfo`, preservation of topology fields, and block-location callers that need storage-level rather than node-level uniqueness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeInfoWithStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeLocalInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeLocalInfo.java

## Purpose
`DatanodeLocalInfo` is a small private/evolving value object for information available locally from a DataNode: software version, configuration version, and uptime in seconds.

## APIs and Behavior
The constructor initializes final fields. Getters expose each field, and `getDatanodeLocalReport()` returns a compact human-readable status line.

## State, Dependencies, and Integration
There is no persistence or mutation in this class. It is likely returned by DataNode-side admin/client commands that inspect a single local node rather than cluster-wide NameNode reports.

## Risks and Test Signals
Inputs are not validated, so null versions or negative uptime can be represented. Tests should cover report formatting, uptime units, and serialization/RPC compatibility for admin tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeLocalInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeVolumeInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeVolumeInfo.java

## Purpose
`DatanodeVolumeInfo` describes locally available storage-volume metrics for a DataNode volume: path, used/free/reserved space, reserved space for replicas, block count, and storage type.

## APIs and Behavior
The constructor initializes mutable private fields, and getters expose all metrics. `getDatanodeVolumeReport()` formats a multi-line report using `StringUtils.byteDesc` for byte values.

## State, Dependencies, and Integration
The class depends on `StorageType` and Hadoop `StringUtils`. It is a reporting DTO; persistence and metric collection occur in DataNode storage components outside this class.

## Risks and Test Signals
The class does not validate negative space values, null paths, or null storage type. Tests should cover report formatting, byte description values, storage type propagation, and edge cases such as zero-capacity or reserved-space-heavy volumes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeVolumeInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DirectoryListing.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DirectoryListing.java

## Purpose
`DirectoryListing` is the response type for iterative single-directory listing through `ClientProtocol.getListing`. It carries a partial array of `HdfsFileStatus` plus a count of remaining entries.

## APIs and Behavior
The constructor rejects null listings and the inconsistent state of an empty listing with nonzero remaining entries. `getPartialListing()` returns the array, `getRemainingEntries()` exposes the remaining count, `hasMore()` checks whether the count is nonzero, and `getLastName()` returns the local-name bytes of the last entry for use as the next `startAfter` cursor.

## State, Dependencies, and Integration
The object is mutable only through its exposed array reference. It integrates with `ClientProtocol.getListing`, `DFSClient` directory iteration, and `HdfsFileStatus` path-name encoding. No persistence happens here.

## Risks and Test Signals
The array is not defensively copied, so cursor behavior can be corrupted by caller mutation. Tests should cover constructor validation, empty terminal listings, cursor extraction from the last entry, and correct handling of UTF-8 local-name bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DirectoryListing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ECBlockGroupStats.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ECBlockGroupStats.java

## Purpose
`ECBlockGroupStats` is the public/evolving statistics DTO for striped erasure-coded block groups returned by `ClientProtocol.getECBlockGroupStats()`.

## APIs and Behavior
It stores low-redundancy, corrupt, missing, bytes-in-future, and pending-deletion counts plus optional `badlyDistributedBlocks` and `highestPriorityLowRedundancyBlocks`. Getters and `has...` methods distinguish absent optional metrics from zero values. `equals`, `hashCode`, and `toString` include all fields. `merge(Collection<ECBlockGroupStats>)` sums all required counters and only includes optional counters if at least one input had them.

## State, Dependencies, and Integration
The class is immutable and depends on Apache Commons Lang builders. It is used by NameNode block-management metrics, client/admin reporting, and federation-style aggregation.

## Risks and Test Signals
`merge()` returns a constructor without optional counters unless both optional categories are present somewhere; if only one optional metric family is present, it drops both optional sums. Tests should cover merge with none, one, and both optional metrics, toString visibility, equality, and overflow assumptions for large clusters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ECBlockGroupStats.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ECTopologyVerifierResult.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ECTopologyVerifierResult.java

## Purpose
`ECTopologyVerifierResult` reports whether the current cluster topology can support one or more erasure coding policies.

## APIs and Behavior
The constructor stores `isSupported` and a human-readable `resultMessage`. `isSupported()` and `getResultMessage()` are the only accessors.

## State, Dependencies, and Integration
The object is immutable and private to HDFS protocol use. It is returned by `ClientProtocol.getECTopologyResultForPolicies` and consumed by admin/client code before enabling or applying EC policies.

## Risks and Test Signals
There is no equality or validation. Tests should cover supported and unsupported results, null/empty messages, and propagation through EC policy verification RPCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ECTopologyVerifierResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/EncryptionZone.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/EncryptionZone.java

## Purpose
`EncryptionZone` is a public/evolving DTO representing an HDFS encryption zone. It carries a unique ID for batched listing, the zone root path, cipher suite, crypto protocol version, and key name.

## APIs and Behavior
The constructor initializes final fields. Accessors expose all fields. `equals`, `hashCode`, and `toString` include ID, path, suite, version, and key name, using Commons Lang builders for equality/hash.

## State, Dependencies, and Integration
The object is immutable and integrates with `ClientProtocol.getEZForPath`, `listEncryptionZones`, `EncryptionZoneIterator`, and file encryption metadata. Dependencies include Hadoop crypto types `CipherSuite` and `CryptoProtocolVersion`.

## Risks and Test Signals
The class performs no null validation, so malformed protocol conversion can create zones with missing suite/version/key. Tests should cover equality, listing cursor IDs, string rendering without leaking sensitive key material beyond key name, and compatibility across crypto protocol versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/EncryptionZone.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/EncryptionZoneIterator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/EncryptionZoneIterator.java

## Purpose
`EncryptionZoneIterator` adapts the batched NameNode encryption-zone listing RPC into a `BatchedRemoteIterator<Long, EncryptionZone>` that supports retries across failover.

## APIs and Control Flow
The constructor starts the cursor at `0L` and stores `ClientProtocol` plus a `Tracer`. `makeRequest(prevId)` opens a tracing scope named `listEncryptionZones` and calls `namenode.listEncryptionZones(prevId)`. `elementToPrevKey(entry)` returns `entry.getId()` for the next cursor.

## State, Dependencies, and Integration
State is only the remote iterator cursor inherited from `BatchedRemoteIterator`. It integrates with NameNode `ClientProtocol` batching, tracing, and `EncryptionZone` IDs.

## Risks and Test Signals
Correctness depends on stable monotonic zone IDs from the NameNode. Tests should cover empty first batch, multi-batch cursor advancement, retry/failover behavior, trace-scope closure, and zones created/deleted during iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/EncryptionZoneIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ErasureCodingPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ErasureCodingPolicy.java

## Purpose
`ErasureCodingPolicy` is a lightweight immutable policy object describing how an erasure-coded file is written, read, and reconstructed. It is cached by `SystemErasureCodingPolicies` and can be returned in `HdfsFileStatus`.

## APIs and Behavior
Constructors require non-null name/schema and a positive 1024-aligned cell size. `composePolicyName()` builds names as `CODEC-data-parity-cellk`. Getters expose name, `ECSchema`, cell size, data/parity unit counts, codec, and policy ID. `isReplicationPolicy()` compares the ID with the special replication policy, and `isSystemPolicy()` checks whether the ID is below the user-defined start ID. Equality and hash code include name, schema, cell size, and ID.

## State, Dependencies, and Integration
The class is serializable and immutable. It depends on erasure-code schema constants and integrates with EC policy management RPCs, `HdfsFileStatus`, `LocatedBlocks`, and topology verification.

## Risks and Test Signals
Name composition is part of user/admin-visible policy identity, so schema and cell-size changes can affect compatibility. Tests should cover invalid cell sizes, replication/system ID classification, equality with same schema but different ID/name, serialization, and policy propagation through file status and RPC conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ErasureCodingPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ErasureCodingPolicyInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ErasureCodingPolicyInfo.java

## Purpose
`ErasureCodingPolicyInfo` wraps an `ErasureCodingPolicy` with its mutable lifecycle state: disabled, enabled, or removed.

## APIs and Behavior
The primary constructor requires non-null policy and state; the convenience constructor defaults to `DISABLED`. `getPolicy()`, `getState()`, `setState()`, and boolean predicates expose and mutate state. Equality, hash code, and `toString()` include both policy and state.

## State, Dependencies, and Integration
The policy reference is final, but state is mutable. It is serializable and consumed by `ClientProtocol.getErasureCodingPolicies`, policy enable/disable/remove operations, and admin display code.

## Risks and Test Signals
Mutable state inside an otherwise value-like wrapper can surprise caches. Tests should cover null rejection, default disabled state, state transitions, equality changes after mutation, and RPC conversion for removed policies that may still be referenced by existing files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ErasureCodingPolicyInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ErasureCodingPolicyState.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ErasureCodingPolicyState.java

## Purpose
`ErasureCodingPolicyState` enumerates policy lifecycle states: `DISABLED`, `ENABLED`, and `REMOVED`.

## APIs and Behavior
Each enum constant has a 1-based `value`; `fromValue(int)` maps values 1..N to cached enum instances and returns null otherwise. `read(DataInput)` reads a byte and maps it with `fromValue`. `write(DataOutput)` writes `ordinal()`.

## State, Dependencies, and Integration
There is no mutable state. The enum is used by `ErasureCodingPolicyInfo` and any legacy writable serialization path for EC policy state.

## Risks and Test Signals
There is an apparent serialization mismatch: `getValue()` is 1-based, `fromValue()` expects 1-based values, but `write()` emits zero-based `ordinal()`. That makes `DISABLED` serialize as `0`, which `read()` maps to null. Tests should explicitly round-trip every state through `write/read`, verify protobuf conversion paths if they bypass this method, and guard compatibility before changing wire behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ErasureCodingPolicyState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ExtendedBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ExtendedBlock.java

## Purpose
`ExtendedBlock` identifies a block uniquely across block pools by pairing a block-pool ID with a local `Block` containing block ID, length, and generation stamp.

## APIs and Behavior
Constructors create empty, copied, pool+ID, pool+`Block`, or full block instances. Pool IDs are interned when non-null. Getters and setters delegate block fields, `set(poolId, blk)` replaces both fields, `getLocalBlock()` exposes the contained `Block`, and static `getLocalBlock()` handles null input. Equality compares the local block plus nullable pool ID; hash and `toString()` include both.

## State, Dependencies, and Integration
The class is mutable and wraps `Block`, used by block-location, write-pipeline, recovery, and DataNode transfer protocols. Persistence is external in block maps, edit logs, and DataNode storage.

## Risks and Test Signals
Because `getLocalBlock()` returns the mutable `Block`, callers can mutate identity after use in collections. Tests should cover equality/hash under mutation, null pool IDs, copy-constructor isolation, generation-stamp updates during pipeline recovery, and interning behavior where many blocks share pool IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ExtendedBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/FsPermissionExtension.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/FsPermissionExtension.java

## Purpose
`FsPermissionExtension` is a deprecated HDFS-private subclass of `FsPermission` that encodes ACL, encryption, and erasure-coded flags in high bits while preserving base permission compatibility.

## APIs and Behavior
One constructor wraps a base `FsPermission` and explicit booleans; another decodes the high bits from a short. `toExtendedShort()` ORs permission bits with ACL, encrypted, and EC flags. `getAclBit()`, `getEncryptedBit()`, and `getErasureCodedBit()` expose flags. Equality and hash code intentionally delegate to the base class.

## State, Dependencies, and Integration
The class integrates with `HdfsFileStatus.convert`, which uses it to preserve redundant flags for compatibility with older applications. The preferred source of these attributes is now `FileStatus`.

## Risks and Test Signals
Equality ignores extension flags through superclass behavior, which can hide differences. Tests should cover bit encode/decode, compatibility with plain `FsPermission`, assertions in `HdfsFileStatus.convert`, and deprecation-safe behavior for old clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/FsPermissionExtension.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsConstants.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsConstants.java

## Purpose
`HdfsConstants` centralizes HDFS protocol constants and enums used across clients, NameNode RPCs, storage policies, leases, snapshots, safe mode, rolling upgrade, datanode reports, and re-encryption.

## APIs and Behavior
Constants include quota sentinel values, URI scheme, storage-policy IDs/names, snapshot/reserved path components, grandfather generation/inode IDs, delegation-token HA prefix, protocol names, read/write timeouts, and lease soft limit. Enums include `StoragePolicy` with ID mapping, `SafeModeAction`, `StoragePolicySatisfierMode` with case-insensitive map lookup, `RollingUpgradeAction` with empty-string query mapping, `UpgradeAction`, `DatanodeReportType`, and `ReencryptAction`.

## State, Dependencies, and Integration
The class is final-ish through a protected hidden constructor and has static state for enum lookup maps. It depends on `Path`, client config keys, and `StringUtils`. Nearly every HDFS client protocol layer uses these constants for wire values and user-visible behavior.

## Risks and Test Signals
Storage-policy numeric IDs and quota sentinel values are compatibility-sensitive. Tests should cover enum string parsing, invalid storage-policy IDs returning null, snapshot path constants, HA token prefix use, timeout expectations, and safe-mode/rolling-upgrade action mapping from CLI input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsFileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsFileStatus.java

## Purpose
`HdfsFileStatus` is the HDFS-specific metadata interface for filesystem entities. It extends writable, comparable, serializable, and validation contracts while exposing inode ID, local-name bytes, symlink bytes, encryption info, EC policy, storage policy, child count, namespace, and FileStatus-like methods.

## APIs and Control Flow
The nested `Builder` collects file status fields and decides whether to build `HdfsNamedFileStatus` or `HdfsLocatedFileStatus`: no locations and not directory/symlink yields the named variant; otherwise it uses the located variant for compatibility. Default methods convert local bytes to strings, build full paths, and qualify status paths. Static `convert` methods map HDFS flags into `FsPermissionExtension` and `FileStatus.AttrFlags`.

## State, Dependencies, and Integration
Implementations store local names as Java UTF-8 byte arrays until qualified by a parent path. The interface integrates with `FileStatus`, `LocatedFileStatus`, `DFSUtilClient`, encryption metadata, EC policies, and listing/status RPCs.

## Risks and Test Signals
Builder defaults are explicitly compatibility-sensitive. The builder defensively copies path and symlink arrays, but downstream implementations return raw arrays. Tests should cover variant selection, permission/flag conversion, default permissions for files/dirs/symlinks, path qualification, namespace fields, and compatibility with `FsPermissionExtension`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsLocatedFileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsLocatedFileStatus.java

## Purpose
`HdfsLocatedFileStatus` is a `LocatedFileStatus` implementation carrying HDFS-specific metadata and optional `LocatedBlocks`. Directories and symlinks may also be represented as this class for backward compatibility.

## APIs and Behavior
The constructor initializes superclass `LocatedFileStatus` using converted permission and attribute flags, then stores local path bytes, symlink bytes, inode ID, child count, file encryption info, storage policy, EC policy, and transient HDFS block locations. `makeQualifiedLocated()` qualifies the path and converts `LocatedBlocks` into user-facing `BlockLocation[]`. It exposes namespace get/set and HDFS-specific getters.

## State, Dependencies, and Integration
It depends on `DFSUtilClient`, `FileEncryptionInfo`, `ErasureCodingPolicy`, and `LocatedBlocks`. The `hdfsloc` field is transient, so serialized forms depend on superclass block locations after qualification.

## Risks and Test Signals
`setGroup(String)` calls `super.setOwner(group)`, which appears to set the owner instead of the group. Raw path/symlink arrays are returned without copies. Tests should cover group setter behavior, symlink detection and error path, block-location conversion before/after `makeQualifiedLocated`, serialization of transient locations, namespace preservation, and mutation of returned byte arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsLocatedFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsNamedFileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsNamedFileStatus.java

## Purpose
`HdfsNamedFileStatus` is the non-located `FileStatus` implementation for HDFS metadata. It is used when a regular file status does not carry block locations.

## APIs and Behavior
The constructor passes converted permission and attribute flags to `FileStatus`, then stores local path bytes, symlink bytes, inode ID, child count, file encryption info, storage policy, and EC policy. It implements HDFS-specific getters, symlink conversion to `Path`, namespace accessors, and visible permission/owner/group setters.

## State, Dependencies, and Integration
It depends on `DFSUtilClient`, `FileEncryptionInfo`, `ErasureCodingPolicy`, and `HdfsFileStatus.convert`. It is produced by `HdfsFileStatus.Builder` for plain named file statuses and consumed by listing/status calls.

## Risks and Test Signals
Like the located variant, `setGroup(String)` calls `super.setOwner(group)`, apparently overwriting owner instead of group. Raw byte arrays are returned. Tests should cover group setter correctness, local/full path behavior, symlink error handling, default flag conversion, namespace fields, and equality/hash delegating to `FileStatus`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsNamedFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsPartialListing.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsPartialListing.java

## Purpose
`HdfsPartialListing` represents one parent-indexed result from the batched multi-directory listing API. It can hold either a successful list of `HdfsFileStatus` objects or a `RemoteException`.

## APIs and Behavior
Two public constructors create success or failure entries. The private constructor enforces exactly one of `partialListing` or `exception` using XOR. Accessors expose `parentIdx`, `partialListing`, and `exception`; `toString()` includes all fields.

## State, Dependencies, and Integration
It depends on Hadoop `Preconditions`, Commons `ToStringBuilder`, and IPC `RemoteException`. It integrates with batched directory listing responses that need to correlate each partial result to the input parent path.

## Risks and Test Signals
The successful listing list is not defensively copied. Tests should cover constructor XOR validation, exception propagation per parent, parent index ordering, and toString output for mixed success/failure batches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsPartialListing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsPathHandle.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsPathHandle.java

## Purpose
`HdfsPathHandle` is an opaque HDFS `PathHandle` implementation that can bind a path to optional inode ID and modification time constraints.

## APIs and Behavior
One constructor accepts a path plus optional inode ID and mtime. Another parses a protobuf `HdfsPathHandleProto` from a `ByteBuffer`. `verify(HdfsLocatedFileStatus)` rejects unresolved handles, content changes when `mtime` is constrained, and wrong files when `inodeId` is constrained. `bytes()` serializes the handle to a read-only protobuf byte buffer. Equality and hash code compare only path, while `toString()` emits JSON-like fields.

## State, Dependencies, and Integration
The class is immutable and serializable. It depends on protobuf-generated `HdfsPathHandleProto`, `PathHandle`, and `InvalidPathHandleException`. It integrates with APIs that reopen files using stable handles rather than only paths.

## Risks and Test Signals
Equality ignoring inode ID and mtime can conflate handles with different validation strength. Tests should cover protobuf round-trips, null byte-buffer errors, verify success/failure for changed mtime and inode, read-only byte buffers, and equality/hash behavior for constrained versus unconstrained handles on the same path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsPathHandle.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/LastBlockWithStatus.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/LastBlockWithStatus.java

## Purpose
`LastBlockWithStatus` is the append-response wrapper containing the last partial `LocatedBlock` and the file status returned by `ClientProtocol.append`.

## APIs and Behavior
The constructor stores final `lastBlock` and `fileStatus` references. `getLastBlock()` and `getFileStatus()` expose them.

## State, Dependencies, and Integration
There is no logic or persistence. It integrates with append setup, allowing clients to resume writing from the last block while also refreshing status metadata.

## Risks and Test Signals
The wrapper does not validate null values, which may be valid for some server capabilities but should be explicit in callers. Tests should cover append responses with and without a partial last block/status, and downstream client behavior when either field is null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/LastBlockWithStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/LocatedBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/LocatedBlock.java

## Purpose
`LocatedBlock` associates an `ExtendedBlock` with replica locations, storage IDs/types, cached locations, file start offset, corruption status, and a block access token.

## APIs and Control Flow
Constructors convert `DatanodeInfo[]` to `DatanodeInfoWithStorage[]`, defaulting offset to `-1` and no corruption. Accessors expose block token, block, locations, storage arrays, offset, block size, corruption flag, and cached locations. `updateCachedStorageInfo()` synchronizes storage arrays after location mutation. `moveProvidedToEnd(activeLen)` stable-sorts provided-storage replicas after normal storage. `addCachedLoc()` avoids duplicates, reuses an existing located DataNode object when possible, and requires a backing disk replica for cached-only additions. `isStriped()` and `getBlockType()` default to contiguous.

## State, Dependencies, and Integration
The class is mutable and central to read/write pipeline setup, token authorization, DataNode selection, and block reports returned by `ClientProtocol`. It depends on `StorageType`, `Token<BlockTokenIdentifier>`, `DatanodeInfoWithStorage`, and utility collection/precondition helpers.

## Risks and Test Signals
Returned location arrays are mutable by contract, but callers must remember to update cached storage arrays. Constructor conversion assumes storage arrays are at least as long as the locations array when non-null. Tests should cover provided-storage ordering, cached-location duplicate handling, storage array sync after mutation, null location handling, corrupt flag filtering expectations, token set/get, and subclass behavior for striped blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/LocatedBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/LocatedBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/LocatedBlocks.java

## Purpose
`LocatedBlocks` is the collection-level response for block-location lookup. It stores file length, an ordered list of located blocks, under-construction status, last block metadata, file encryption info, and EC policy.

## APIs and Control Flow
Getters expose blocks, count, indexed access, file length, last block, construction status, encryption info, and EC policy. `findBlock(offset)` performs binary search using a synthetic one-byte key and a comparator that returns equality when ranges overlap. `insertRange(blockIdx, newBlocks)` merges refreshed block ranges into the sorted existing list, replacing same-offset entries and inserting new earlier entries. `getInsertIndex()` converts a binary-search result to an insertion index.

## State, Dependencies, and Integration
The list is stored by reference and mutated by `insertRange`. The class integrates with `ClientProtocol.getBlockLocations`, DFSInputStream block refresh, encryption metadata, and erasure-coded files.

## Risks and Test Signals
The default constructor leaves `blocks` null; callers must use `locatedBlockCount()` or avoid direct `getLocatedBlocks()` iteration. `insertRange()` asserts sorted input rather than throwing. Tests should cover binary search at block boundaries, empty/null lists, range insertion/replacement, under-construction last-block flags, and EC/encryption metadata propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/LocatedBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/LocatedStripedBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/LocatedStripedBlock.java

## Purpose
`LocatedStripedBlock` specializes `LocatedBlock` for erasure-coded striped block groups. Each storage location is associated with a block index inside the group and may have an individual block token.

## APIs and Behavior
The constructor delegates common block-location state to `LocatedBlock`, copies the supplied indices array, and initializes one empty token per index. It overrides `isStriped()` and `getBlockType()` to report striped blocks. Getters/setters expose block indices and per-internal-block tokens; `toString()` includes indices.

## State, Dependencies, and Integration
The class is mutable for indices and tokens. It depends on `StorageType`, `DatanodeInfo`, `Token<BlockTokenIdentifier>`, and `BlockType.STRIPED`. It is produced by NameNode block-location conversion for EC files and consumed by client read reconstruction logic.

## Risks and Test Signals
`setBlockIndices()` stores the provided array directly, unlike the constructor copy. Token array length must stay aligned with indices and locations. Tests should cover defensive copying, token/index alignment, block type reporting, toString diagnostics, and EC read-path conversion to user-facing block locations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/LocatedStripedBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/NSQuotaExceededException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/NSQuotaExceededException.java

## Purpose
`NSQuotaExceededException` specializes `QuotaExceededException` for namespace quota violations, i.e. file and directory count limits.

## APIs and Behavior
It offers default, message, and `(quota, count)` constructors. `getMessage()` preserves explicit superclass messages; otherwise it builds a namespace quota message using inherited path/quota/count and optional prefix set by `setMessagePrefix()`.

## State, Dependencies, and Integration
State is inherited plus a mutable `prefix`. The class is public/evolving and propagates through NameNode RPCs for create, mkdir, rename, and other namespace mutations.

## Risks and Test Signals
The prefix is mutable and only affects generated messages. Tests should cover explicit-message bypass, prefix rendering, null path handling, and RPC propagation from operations that exceed directory namespace quotas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/NSQuotaExceededException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/NoECPolicySetException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/NoECPolicySetException.java

## Purpose
`NoECPolicySetException` is an HDFS-private/evolving `IOException` thrown when a directory has no explicit erasure coding policy where one was required.

## APIs and Behavior
It only defines a message constructor and inherits all behavior from `IOException`.

## State, Dependencies, and Integration
The class has no additional state. It integrates with EC policy query/unset flows and client/admin error reporting.

## Risks and Test Signals
Tests should verify that the right exception is thrown for directories inheriting replication or lacking explicit EC policy, and that RPC conversion preserves the message and exception type where clients rely on it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/NoECPolicySetException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/OpenFileEntry.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/OpenFileEntry.java

## Purpose
`OpenFileEntry` represents one open file for DFSAdmin/open-file listing commands. It identifies the inode ID, file path, client name, and client machine.

## APIs and Behavior
The constructor initializes final fields. Accessors expose `id`, `filePath`, `clientName`, and `clientMachine`.

## State, Dependencies, and Integration
It is immutable and used by `ClientProtocol.listOpenFiles` and `OpenFilesIterator`. The ID acts as the batching cursor.

## Risks and Test Signals
There is no validation and no equality implementation. Tests should cover batched cursor ordering by ID, filtering by path/type, and display behavior when client fields are null or empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/OpenFileEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/OpenFilesIterator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/OpenFilesIterator.java

## Purpose
`OpenFilesIterator` adapts batched open-file listing into a retryable remote iterator. The listing is explicitly not a consistent snapshot across batches.

## APIs and Control Flow
`OpenFilesType` defines filter modes `ALL_OPEN_FILES` and `BLOCKING_DECOMMISSION`, each with a short mode and reverse lookup. The iterator starts at `HdfsConstants.GRANDFATHER_INODE_ID`, stores filter type set and path, and calls `namenode.listOpenFiles(prevId, types, path)` inside a tracing scope. `elementToPrevKey()` returns the entry inode ID.

## State, Dependencies, and Integration
State is inherited cursor plus immutable filter references. It integrates with DFSAdmin, NameNode lease/open-file tracking, decommission workflows, and tracing.

## Risks and Test Signals
The path field is mutable only internally but not final. `OpenFilesType.valueOf(short)` returns null for unknown modes. Tests should cover filter mode conversion, default path `/`, cursor advancement, non-atomic listing changes across batches, tracing, and permissions for superuser-only listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/OpenFilesIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ProvidedStorageLocation.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ProvidedStorageLocation.java

## Purpose
`ProvidedStorageLocation` identifies data for a block replica located in an external/provided storage system. It carries a `Path`, byte offset, length, and nonce.

## APIs and Behavior
The constructor stores path, offset, length, and a defensive copy of nonce. Getters expose path, offset, length, and a fresh copy of nonce. Equality and hash code include all fields and array contents.

## State, Dependencies, and Integration
The object is immutable if the `Path` is treated as immutable. It integrates with provided-storage block mapping and `LocatedBlock` behavior that moves `StorageType.PROVIDED` locations after normal replicas.

## Risks and Test Signals
The constructor assumes `nonce` is non-null. There is no validation for negative offsets/lengths. Tests should cover nonce defensive copies, equality/hash behavior, null nonce failure, external path identity, and read behavior for provided-storage replicas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ProvidedStorageLocation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/QuotaByStorageTypeExceededException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/QuotaByStorageTypeExceededException.java

## Purpose
`QuotaByStorageTypeExceededException` specializes quota failures for storage-type-specific space quotas.

## APIs and Behavior
It provides default, message, and `(quota, count, StorageType)` constructors. `getMessage()` preserves explicit messages or builds a storage-type quota message with path, quota, and consumed space formatted via `long2String`.

## State, Dependencies, and Integration
It extends `QuotaExceededException` and adds `StorageType type`. It is thrown by storage policy/quota enforcement when a path exceeds quota for a specific storage media type.

## Risks and Test Signals
Generated-message path calls `type.toString()`, so a null type will throw. Tests should cover explicit messages, all relevant storage types, null path behavior, null type behavior, and propagation through storage-type quota RPCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/QuotaByStorageTypeExceededException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/QuotaExceededException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/QuotaExceededException.java

## Purpose
`QuotaExceededException` is the base public/evolving HDFS quota exception for namespace and disk/storage-space quota violations. It extends `ClusterStorageCapacityExceededException`.

## APIs and Behavior
Protected constructors support no-arg, explicit message, and `(quota, count)` creation for subclasses. `setPathName(String)` sets the path included by subclass-generated messages. `getMessage()` delegates to the superclass; specialized subclasses generate detailed text when no explicit message is present.

## State, Dependencies, and Integration
It stores mutable `pathName`, `quota`, and `count` for subclasses. It integrates with NameNode quota enforcement and client RPC exception propagation.

## Risks and Test Signals
The base class itself does not generate details, so using it directly with quota/count yields an empty superclass message. Tests should cover subclass message behavior, path mutation after construction, serialization across RPC, and callers catching the base type for all quota failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/QuotaExceededException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ReconfigurationProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ReconfigurationProtocol.java

## Purpose
`ReconfigurationProtocol` is an HDFS admin RPC interface for reloading and applying configuration changes on NameNode/DataNode services without restart.

## APIs and Behavior
It defines `VERSIONID = 1L` and three idempotent RPCs: `startReconfiguration()` to asynchronously reload/apply changes, `getReconfigurationStatus()` to query the current or previous task, and `listReconfigurableProperties()` to list allowed property keys.

## State, Dependencies, and Integration
The interface has no state. Implementations manage background task state and return `ReconfigurationTaskStatus`. It integrates with HDFS admin tooling and retry logic via `@Idempotent`.

## Risks and Test Signals
Although marked idempotent, starting a background reconfiguration must avoid spawning duplicate incompatible tasks under retry. Tests should cover repeated starts, status before/during/after a task, property list stability, partial failures, and RPC permission checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ReconfigurationProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ReencryptionStatus.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ReencryptionStatus.java

## Purpose
`ReencryptionStatus` tracks re-encryption progress for encryption zones. It stores one `ZoneReencryptionStatus` per zone and aggregate metrics for completed zones.

## APIs and Control Flow
The class maintains a `TreeMap<Long, ZoneReencryptionStatus>` to preserve zone ID ordering. State transition methods mark zones for retry, started, or completed. `getNextUnprocessedZone()` scans for the first submitted zone. `hasRunningZone()` checks non-completed status. `updateZoneStatus()` adds a zone from `ReencryptionInfoProto` if absent, otherwise updates completion, submission, or in-progress checkpoint state. `removeZone()`, testing counters, `resetMetrics()`, `toString()`, and `getZoneStatuses()` expose management and diagnostics.

## State, Dependencies, and Integration
Comments state FSDirectory lock provides synchronization except for test-only methods. Dependencies include `ZoneReencryptionStatus`, protobuf `ReencryptionInfoProto`, batched-listing empty entries, `Preconditions`, SLF4J logging, and Hadoop list utilities. It integrates with encryption zone re-encryption RPCs and `ReencryptionStatusIterator`.

## Risks and Test Signals
The copy constructor shallow-copies `ZoneReencryptionStatus` objects, so mutations can leak between copies. `zonesReencrypted` increments when adding completed zones and when marking completion, so reconciliation must avoid double counting. Tests should cover submission/retry/processing/completion transitions, update paths with/without last-file checkpoint, removal, metric reset, copy isolation expectations, and lock discipline in NameNode callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ReencryptionStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ReencryptionStatusIterator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ReencryptionStatusIterator.java

## Purpose
`ReencryptionStatusIterator` adapts batched listing of encryption-zone re-encryption statuses into a retryable remote iterator.

## APIs and Control Flow
The constructor starts the cursor at `0L` and stores `ClientProtocol` plus tracer. `makeRequest(prevId)` opens a `listReencryptionStatus` trace scope and calls `namenode.listReencryptionStatus(prevId)`. `elementToPrevKey(entry)` returns the zone status ID.

## State, Dependencies, and Integration
State is inherited from `BatchedRemoteIterator`. It depends on `ZoneReencryptionStatus`, tracing, and `ClientProtocol`. It is used by admin/client code displaying re-encryption progress.

## Risks and Test Signals
Correctness depends on stable increasing zone IDs and NameNode-side batching. Tests should cover empty status lists, cursor advancement, tracing cleanup, failover retry behavior, and zones completing or being removed during iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ReencryptionStatusIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ReplicatedBlockStats.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ReplicatedBlockStats.java

## Purpose
`ReplicatedBlockStats` is the public/evolving statistics DTO for contiguous replicated blocks returned by `ClientProtocol.getReplicatedBlockStats()`.

## APIs and Behavior
It stores low-redundancy, corrupt, missing replica, missing replication-one, bytes-in-future, and pending-deletion counts, plus optional badly distributed and highest-priority low-redundancy counts. Getters and `has...` methods expose required and optional metrics. `toString()` renders present optional fields. `merge(Collection<ReplicatedBlockStats>)` sums counters across inputs and includes optional metrics only if both optional categories are present somewhere.

## State, Dependencies, and Integration
The class is immutable. It integrates with NameNode block manager statistics, admin reporting, and federation aggregation.

## Risks and Test Signals
Unlike `ECBlockGroupStats`, this class does not override `equals()`/`hashCode()`, so object identity is used in tests/collections. `merge()` can drop a single present optional category if the other optional category is absent. Tests should cover merge optional-field combinations, toString formatting, identity versus value comparison expectations, and large-count aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ReplicatedBlockStats.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/RollingUpgradeInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/RollingUpgradeInfo.java

## Purpose
`RollingUpgradeInfo` extends `RollingUpgradeStatus` with rolling-upgrade timing and rollback-image state.

## APIs and Behavior
The constructor sets block pool ID, rollback image flag, start time, and finalize time, passing finalized status to the superclass based on nonzero finalize time. It exposes `createdRollbackImages`, setter for that flag, `isStarted`, `getStartTime`, `isFinalized`, `finalize(finalizeTime)`, and `getFinalizeTime`. Equality and hash include superclass identity plus times. `toString()` renders start/finalize times with readable date and raw timestamp. Nested `Bean` exposes JMX-style fields.

## State, Dependencies, and Integration
The class is mutable for finalize time and rollback image flag. It integrates with `ClientProtocol.rollingUpgrade`, admin CLI/JMX, and NameNode upgrade state persisted elsewhere.

## Risks and Test Signals
Calling `finalize(0)` is ignored; finalizing with nonzero time clears rollback image state. Tests should cover not-started/not-finalized rendering, equality before/after finalize, Bean values, rollback image flag changes, and RPC behavior for query/prepare/finalize actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/RollingUpgradeInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/RollingUpgradeStatus.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/RollingUpgradeStatus.java

## Purpose
`RollingUpgradeStatus` is the base status object for rolling upgrade state, carrying block pool ID and finalized flag.

## APIs and Behavior
The constructor initializes final fields. `getBlockPoolId()` and `isFinalized()` expose state. Equality compares block pool ID and finalized flag, while hash code uses block pool ID only. `toString()` renders the block pool ID.

## State, Dependencies, and Integration
The object is immutable and used as the superclass for `RollingUpgradeInfo`. It integrates with NameNode rolling-upgrade RPC responses.

## Risks and Test Signals
Hash code omits finalized status while equality includes it, which is legal but can increase collisions. Null block pool IDs will break hash/equality. Tests should cover equality/hash contract, finalized differences, null handling if protocol conversion allows it, and status display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/RollingUpgradeStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotAccessControlException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotAccessControlException.java

## Purpose
`SnapshotAccessControlException` is the HDFS protocol exception for snapshot access violations, especially attempts to mutate read-only snapshot paths.

## APIs and Behavior
It extends `AccessControlException` and provides constructors for a message or cause.

## State, Dependencies, and Integration
There is no additional state. It appears in `ClientProtocol` method documentation for create, append, rename, delete, mkdir, set quota/times, symlink creation, and other namespace mutations that must reject read-only snapshot paths.

## Risks and Test Signals
Tests should verify the specific exception is raised for snapshot mutation attempts, that cause/message are preserved across RPC, and that normal permission-denied cases still use the correct access-control exception type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotAccessControlException.java -->
