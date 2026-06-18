# subset-b-007506 Research

Grouped source research for Hadoop HDFS NameNode checkpointing, image transfer, HA state management, xattr storage, lock management, metrics, and snapshot diff utilities. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SecondaryNameNode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SecondaryNameNode.java

## Purpose

`SecondaryNameNode.java` implements the non-HA Secondary NameNode daemon and startup utility commands. It periodically checkpoints a primary NameNode by rolling the primary edit log, downloading the latest fsimage and finalized edits, replaying the edits into a local `FSNamesystem`, saving a new fsimage in checkpoint storage, and uploading that image back to the primary over the image transfer servlet. The source was read as a complete 1,116-line file for this report.

## Important APIs, Types, and Functions

The main type is `SecondaryNameNode`, which implements `Runnable` and `SecondaryNameNodeInfoMXBean`. Important methods are constructors, `initialize`, `startInfoServer`, `startCheckpointThread`, `doWork`, `doCheckpoint`, `downloadCheckpointFiles`, `doMerge`, `shutdown`, `main`, `processStartupCommand`, and JMX getters such as `getLastCheckpointTime` and `getCheckpointDirectories`. The nested `CommandLineOpts` parses `-checkpoint`, `-checkpoint force`, `-geteditsize`, `-format`, and help. The nested `CheckpointStorage` extends `FSImage` for checkpoint-local image/edit storage and owns `recoverCreate`, `deleteTempEdits`, merge-error accounting, and a `CheckpointLogPurger`.

## Control Flow

Construction rejects HA nameservices, initializes generic NameNode keys, logs in with the secondary keytab when security is enabled, creates JVM metrics, opens a `NamenodeProtocol` RPC proxy to the primary, initializes checkpoint image and edits directories, recovers or creates local storage, creates a checkpoint-only `FSNamesystem`, disables quota checks, and registers the JMX bean. In daemon mode `main` starts the HTTP server, starts a daemon thread, and joins the web server. The thread sleeps for the configured check period, refreshes Kerberos credentials, then checkpoints when either transaction count or elapsed time crosses `CheckpointConf` thresholds.

`doCheckpoint` is the critical path. It ensures `current/` directories exist, calls `namenode.rollEditLog`, uses the returned `CheckpointSignature` to align local storage identity and validate namespace compatibility, fetches the manifest from the primary, downloads changed fsimage and required edits, reloads the image if needed or after a previous merge error, applies edit logs with `Checkpointer.rollForwardByApplyingLogs`, saves the resulting image in all local directories, updates storage version outside rolling upgrade, uploads the new image through `TransferFsImage.uploadImageFromStorage`, and optionally writes a legacy OIV image. Startup command mode runs a single checkpoint or edit-size query and exits.

## State and Persistence Behavior

Persistent state is the checkpoint storage tree: VERSION files, fsimage files, finalized edits, temporary edits, md5 digests, and any legacy OIV output. `CheckpointStorage.recoverCreate` analyzes and recovers storage directories, optionally formats them, reads existing VERSION files, unlocks/restores removed storage, and deletes temporary edits. The local `FSNamesystem` holds the replayed namespace image in memory between checkpoint cycles, but a merge failure marks `mergeErrorCount` so the next checkpoint reloads from downloaded image and edits instead of trusting possibly inconsistent memory. `lastCheckpointTime` uses monotonic time for scheduling, while `lastCheckpointWallclockTime` is exposed to JMX.

## Dependencies and Integration Points

The class integrates with `NameNodeProxies`, `NamenodeProtocol`, `CheckpointSignature`, `RemoteEditLogManifest`, `FSImage`, `FSNamesystem`, `NNStorage`, `FileJournalManager`, `TransferFsImage`, `ImageServlet`, `HttpServer2`, `MBeans`, `CheckpointFaultInjector`, Hadoop security, and `CheckpointConf`. It is intentionally disabled in HA deployments because `StandbyCheckpointer` handles checkpointing there. The HTTP server exposes `ImageServlet` so the primary can pull the newly generated image.

## Risks and Edge Cases

The code is sensitive to namespace identity and layout-version mismatches; accepting the wrong signature would corrupt checkpoint storage. Partial downloads and rename failures can leave temp edits, which are cleaned on startup but still affect recovery. Merge errors can leave in-memory namespace state inconsistent, so the merge-error counter and reload behavior are important. The daemon terminates after too many merge failures to avoid unbounded edit growth. Security setups rely on correct keytab, SPNEGO, and relogin behavior. `downloadCheckpointFiles` requires a continuous manifest starting at `mostRecentCheckpointTxId + 1`.

## Test Signals

Useful tests cover daemon scheduling by transaction count and period, CLI parsing and single-shot checkpoint behavior, HA rejection, fresh and existing checkpoint storage recovery, temp edit cleanup, manifest gap detection, namespace signature mismatch, fsimage reload after merge failure, upload failure handling, rolling-upgrade storage-version behavior, legacy OIV failures that should not abort checkpointing, JMX fields, secure keytab/relogin paths, and injected failures through `CheckpointFaultInjector`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SecondaryNameNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SecondaryNameNodeInfoMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SecondaryNameNodeInfoMXBean.java

## Purpose

`SecondaryNameNodeInfoMXBean.java` defines the JMX management contract exposed by `SecondaryNameNode`. The source was read as a complete 65-line file.

## Important APIs, Types, and Functions

The interface extends `VersionInfoMXBean` and declares `getHostAndPort`, `isSecurityEnabled`, `getStartTime`, `getLastCheckpointTime`, `getLastCheckpointDeltaMs`, `getCheckpointDirectories`, and `getCheckpointEditlogDirectories`.

## Control Flow

There is no executable flow. `SecondaryNameNode` implements these getters and registers itself through Hadoop metrics/JMX utilities during initialization.

## State and Persistence Behavior

The interface owns no state. It exposes runtime state from the secondary daemon and configured checkpoint directories that point to persistent local fsimage/edit storage.

## Dependencies and Integration Points

It uses Hadoop classification annotations and inherits build/version methods from `VersionInfoMXBean`. It integrates with JMX object registration in `SecondaryNameNode.initialize`.

## Risks and Edge Cases

Because this is an operational interface, changes to method names or return types can break monitoring tools that rely on JMX naming conventions. Null or empty directory arrays would indicate bad initialization rather than an interface issue.

## Test Signals

Tests should register a `SecondaryNameNode` MBean and verify that values reflect configured directories, start time, security state, version fields, and checkpoint timestamp/delta before and after a checkpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SecondaryNameNodeInfoMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SerialNumberManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SerialNumberManager.java

## Purpose

`SerialNumberManager.java` manages shared string-to-integer tables for compact on-disk and in-memory metadata encodings, especially user, group, ACL entry names, and xattr names. The source was read as a complete 162-line file.

## Important APIs, Types, and Functions

The enum constants are `GLOBAL`, `USER`, `GROUP`, and `XATTR`. Each owns a `SerialNumberMap<String>` and a bit length derived from the fields that embed its IDs. Public methods include `getSerialNumber`, `getString`, `getString(int, StringTable)`, `getStringTable`, and `newStringTable`. The nested `StringTable` stores packed IDs to strings and exposes `put`, `iterator`, `size`, and `getMaskBits`.

## Control Flow

Static initialization computes how many high-order mask bits are needed to distinguish manager namespaces in a saved string table, narrows each manager's usable ID bit length, creates the maps, and logs their capacity. Runtime calls allocate serial numbers lazily through `SerialNumberMap`. Saving creates a snapshot `StringTable` by OR-ing manager-specific high bits into each entry ID. Loading creates an empty table with an expected size and mask width, then lookup re-applies the current manager mask when needed.

## State and Persistence Behavior

The enum instances hold process-wide maps that grow as metadata strings are encountered. `StringTable` is the persistence bridge for fsimage serialization: it snapshots string mappings so compact IDs in inodes, ACLs, and xattrs can be decoded during image load. ID `0` is reserved for null by the underlying map.

## Dependencies and Integration Points

The bit lengths are constrained by `PermissionStatusFormat.USER`, `PermissionStatusFormat.GROUP`, `AclEntryStatusFormat.NAME`, and `XAttrFormat.NAME`, all using `LongBitFormat.Enum`. `FSImage` serialization/deserialization consumes the string table when persisting compact metadata.

## Risks and Edge Cases

Capacity is finite and based on bit allocation; exceeding a map's maximum throws. String table mask bits must not exceed the current supported mask width or loading fails. Persisted IDs are only meaningful with the matching string table, so incorrect table reconstruction can misattribute owners, groups, ACL names, or xattr names.

## Test Signals

Tests should cover null ID behavior, lazy allocation stability, save/load `StringTable` masking for all managers, rejection of excessive mask bits, capacity overflow, lookup of missing IDs, and fsimage round trips with users, groups, ACL names, and xattr names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SerialNumberManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SerialNumberMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SerialNumberMap.java

## Purpose

`SerialNumberMap.java` is a thread-safe bidirectional map from arbitrary objects to compact positive integer serial numbers. The source was read as a complete 112-line file.

## Important APIs, Types, and Functions

The generic class `SerialNumberMap<T>` stores `t2i`, `i2t`, an atomic `current` counter starting at 1, and a maximum derived from bit length. Public APIs are `get(T)`, `get(int)`, `size`, and `toString`; package-visible helpers include `getMax` and `entrySet`.

## Control Flow

`get(T)` returns `0` for null, returns an existing serial if present, or synchronizes to allocate a new serial number, checking overflow and using `putIfAbsent` defensively. `get(int)` returns null for zero and otherwise requires an existing reverse mapping.

## State and Persistence Behavior

The map is in-memory only. Persistence is indirect through `SerialNumberManager.StringTable`, which snapshots `i2t` entries. The reverse map is the authoritative enumeration for size and snapshots.

## Dependencies and Integration Points

It uses Java concurrent maps and atomic counters and is owned primarily by `SerialNumberManager`. It supports compact encodings in NameNode metadata formats.

## Risks and Edge Cases

The maximum is `(1 << bitLength) - 1`, so bit lengths near integer limits must be kept valid by callers. Overflow rolls back the counter and throws. Missing reverse lookups throw `IllegalStateException`, which is appropriate for corrupted or inconsistent metadata but can surface during fsimage load.

## Test Signals

Tests should stress concurrent allocation of the same and different values, null handling, reverse lookup, overflow boundaries, snapshot entry-set immutability, and idempotent serial reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SerialNumberMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/StartupProgressServlet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/StartupProgressServlet.java

## Purpose

`StartupProgressServlet.java` exposes NameNode startup progress as JSON at `/startupProgress`. The source was read as a complete 139-line file.

## Important APIs, Types, and Functions

The servlet extends `DfsServlet`, declares `PATH_SPEC`, and overrides `doGet`. Helpers `writeNumberFieldIfDefined` and `writeStringFieldIfNotNull` omit undefined values. JSON keys include `elapsedTime`, `percentComplete`, `phases`, `steps`, `status`, `count`, `total`, `file`, and `size`.

## Control Flow

`doGet` sets the response content type, fetches `StartupProgress` from the NameNode HTTP server context, creates a snapshot `StartupProgressView`, and streams a JSON object using Jackson. It emits global progress fields, then iterates phases and phase steps, adding type descriptions, counts, totals, percentages, elapsed time, and optional file/size metadata. The generator is closed in a `finally` block.

## State and Persistence Behavior

The servlet owns no persistent state. It serializes a point-in-time view of in-memory startup progress maintained elsewhere by NameNode startup code.

## Dependencies and Integration Points

It integrates with `NameNodeHttpServer.getStartupProgressFromContext`, `StartupProgress`, `StartupProgressView`, `Phase`, `Step`, `StepType`, Jackson `JsonGenerator`, and the NameNode web UI/API surface.

## Risks and Edge Cases

Consumers may depend on stable JSON field names. Undefined size values are represented by omission, not null. Errors while writing response JSON are normal servlet IO failures. If the context lacks startup progress, the failure will occur outside this class's own validation.

## Test Signals

Tests should issue servlet GETs for empty, partial, and complete progress views; validate JSON shape, content type, optional field omission, phase/step ordering from the view, and cleanup on generator/write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/StartupProgressServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/StoragePolicySummary.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/StoragePolicySummary.java

## Purpose

`StoragePolicySummary.java` aggregates actual block storage-type allocations against each block's specified storage policy and renders a human-readable compliance summary. The source was read as a complete 260-line file.

## Important APIs, Types, and Functions

The class owns `storageComboCounts`, `storagePolicies`, and `totalBlocks`. Key methods are constructor, `add`, `sortByComparator`, `toString`, and `getStoragePolicy`. The nested `StorageTypeAllocation` stores sorted `StorageType[]`, specified and actual `BlockStoragePolicy`, formats descriptors, checks `policyMatches`, and implements equality/hash code.

## Control Flow

Callers add each block's storage type array and specified policy. `add` wraps the pair in `StorageTypeAllocation`, increments the count, and computes the matching actual policy for first-time combinations. `getStoragePolicy` sorts each candidate policy's storage types and matches it as a prefix, allowing extra replicas of the final storage type. `toString` sorts combinations by block count descending and emits separate compliant and non-compliant tables with percentages.

## State and Persistence Behavior

The summary is transient report state. It mutates input storage arrays by sorting them inside `StorageTypeAllocation`, so callers should not rely on the original ordering after calling `add`.

## Dependencies and Integration Points

It integrates with `BlockStoragePolicy`, `StorageType`, and NameNode reporting paths that inspect block placement and storage policy compliance.

## Risks and Edge Cases

`totalBlocks` can be zero if `toString` is called before any `add`, producing no rows but avoiding division because the loop is empty. Mutating the passed `StorageType[]` is a subtle side effect. Actual policy matching depends on sorted order and duplicate handling; changes to policy semantics need matching updates here.

## Test Signals

Tests should cover compliant and non-compliant mixes, duplicate storage types, extra replicas matching the last policy type, unknown actual policy, sorted output by count, percentage formatting, equality/hash behavior, and caller-visible mutation expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/StoragePolicySummary.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/StreamLimiter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/StreamLimiter.java

## Purpose

`StreamLimiter.java` defines a minimal package-private interface for streams that can enforce a byte-read limit. The source was read as a complete 34-line file.

## Important APIs, Types, and Functions

The interface declares `setLimit(long limit)` and `clearLimit()`.

## Control Flow

There is no implementation here. Implementing streams are expected to track remaining bytes after `setLimit` and disable enforcement after `clearLimit`.

## State and Persistence Behavior

The interface owns no state. Implementations hold transient stream-read state and should not persist limits beyond the stream instance.

## Dependencies and Integration Points

It is in the NameNode package and is used by metadata/image reading code that needs to bound reads to a section or advertised length.

## Risks and Edge Cases

Implementations must define behavior for negative limits, zero limits, and limit resets. Failure to enforce a limit can let one serialized section consume bytes belonging to a following section.

## Test Signals

Tests should target implementers: exact-limit reads, over-limit exception behavior, reset by `setLimit`, disabled behavior after `clearLimit`, zero length, and interaction with EOF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/StreamLimiter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/TransferFsImage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/TransferFsImage.java

## Purpose

`TransferFsImage.java` centralizes HTTP transfer of NameNode fsimage files, edit logs, and provided-storage alias maps between NameNodes, Secondary NameNodes, and Standby NameNodes. The source was read as a complete 463-line file.

## Important APIs, Types, and Functions

The `TransferResult` enum maps HTTP responses to upload outcomes. Public and package APIs include `downloadMostRecentImageToDirectory`, `downloadImageToStorage`, `handleUploadImageRequest`, `downloadEditsToStorage`, `downloadAliasMap`, `uploadImageFromStorage`, `copyFileToStream`, `getFileClient`, and `doGetUrl`. Internal helpers include `uploadImage`, `writeFileToPutRequest`, `parseMD5Header`, and `setTimeout`.

## Control Flow

Download paths construct servlet query strings through `ImageServlet`, resolve destination files from `Storage` or `NNStorage`, and call `Util.doGetUrl` to stream HTTP GET responses into one or more local paths, optionally validating md5 digests. Edit downloads write temporary finalized-edits names that include a monotonic timestamp, then rename each temp file into the final edits filename. Alias map downloads call `InMemoryAliasMap.completeBootstrapTransfer`.

Upload paths ask the remote NameNode to pull an image by sending an HTTP PUT with query parameters and verification headers. `uploadImage` finds the local image file, builds a parameterized `ImageServlet` URL, opens a secure-aware `HttpURLConnection`, enables chunked streaming for large images, sets timeouts and verification headers, streams file bytes through `copyFileToStream`, and checks for HTTP OK. HTTP failures are translated to `TransferResult` so standby checkpoint upload can distinguish authentication, inactive NameNode, old transaction ID, and unexpected failures.

## State and Persistence Behavior

The class writes fsimage, edits, and alias map files into local storage directories supplied by callers. It uses md5 headers and `Util.receiveFile`/`Util.doGetUrl` to persist and verify received files. Static `timeout` is lazily loaded from configuration and reused process-wide. Transfers are otherwise stateless.

## Dependencies and Integration Points

It is tightly integrated with `ImageServlet`, `NNStorage`, `Storage`, `NameNodeFile`, `RemoteEditLog`, `Util`, `DataTransferThrottler`, `Canceler`, `CheckpointFaultInjector`, `InMemoryAliasMap`, Hadoop security authentication, and NameNode metrics around get/put image servlet calls.

## Risks and Edge Cases

Image transfer is security and corruption sensitive. Incorrect md5 handling, advertised size, temp-to-final rename, or cancellation can leave incomplete metadata files. The static timeout can surprise tests or multiple configurations in one JVM. Upload response-code translation is part of HA checkpoint behavior; rethrowing the wrong failures can either hide real errors or abort too aggressively. `copyFileToStream` deliberately supports injected short/corrupt transfers for tests.

## Test Signals

Tests should cover fsimage download with digest, missing destination dirs, edit download skip when readable file exists, temp rename failure, upload success and each `TransferResult`, chunked upload threshold, cancellation, throttling, timeout configuration, md5 header parsing, corrupted/short transfer injection, alias map bootstrap, and secure connection behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/TransferFsImage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/UnsupportedActionException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/UnsupportedActionException.java

## Purpose

`UnsupportedActionException.java` defines a NameNode-private checked exception for unsupported operations. The source was read as a complete 38-line file.

## Important APIs, Types, and Functions

The class extends `IOException`, declares `serialVersionUID`, and provides a single message constructor.

## Control Flow

There is no internal branching. Callers throw it where a requested action is not supported in the current context.

## State and Persistence Behavior

The exception carries only the inherited message and stack trace. It owns no persistent state.

## Dependencies and Integration Points

It integrates with NameNode code paths that already use `IOException` as the RPC/operation failure surface, allowing unsupported action failures to propagate through existing checked-exception handling.

## Risks and Edge Cases

The value is mostly semantic. Catching broad `IOException` can erase the distinction unless callers log or inspect the concrete type.

## Test Signals

Tests should verify the relevant caller surfaces this exception type and message for unsupported operations, and that RPC or CLI layers report it without treating it as an internal crash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/UnsupportedActionException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/VersionInfoMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/VersionInfoMXBean.java

## Purpose

`VersionInfoMXBean.java` defines a small JMX contract for exposing build and software version information. The source was read as a complete 35-line file.

## Important APIs, Types, and Functions

The interface declares `getCompileInfo` and `getSoftwareVersion`.

## Control Flow

There is no executable control flow. Implementers such as `SecondaryNameNode` return values from Hadoop `VersionInfo`.

## State and Persistence Behavior

The interface owns no state. It exposes build metadata embedded in the running binaries.

## Dependencies and Integration Points

It is extended by `SecondaryNameNodeInfoMXBean` and can be reused by other NameNode-related MBeans that need version exposure.

## Risks and Edge Cases

Changing the method names would change JMX attribute names and break monitoring integrations.

## Test Signals

Tests should verify implementing MBeans publish compile and version attributes that match `VersionInfo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/VersionInfoMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/XAttrFeature.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/XAttrFeature.java

## Purpose

`XAttrFeature.java` stores extended attributes as an `INode.Feature`, optimizing small xattrs into a packed byte array while keeping large values in an immutable list. The source was read as a complete 122-line file.

## Important APIs, Types, and Functions

The class defines `PACK_THRESHOLD` of 1024 bytes, fields `attrs` and `xAttrs`, constructor, `getXAttrs`, `getXAttr`, `equals`, and `hashCode`.

## Control Flow

Construction partitions input xattrs: null values and values up to the threshold are packed with `XAttrFormat.toBytes`, while larger values are stored in an `ImmutableList`. `getXAttrs` unpacks the byte array and appends large xattrs if present. `getXAttr` first searches packed bytes by prefixed name, then scans large xattrs using `equalsIgnoreValue`.

## State and Persistence Behavior

The feature is attached to inodes and may be captured by snapshot inode attributes. Packed bytes use `XAttrFormat`, which is both in-memory and on-disk format. Large xattrs are immutable in memory but still serialized by higher-level fsimage code.

## Dependencies and Integration Points

It integrates with `INode.Feature`, `XAttrFormat`, `XAttrHelper`, Guava `ImmutableList`, and `XAttrStorage`. NameNode xattr operations build and replace this feature under directory locks.

## Risks and Edge Cases

The 1024-byte threshold affects memory layout and lookup cost. Equality reconstructs lists and hashes array copies, which is acceptable for metadata comparison but not free. Any incompatible change to `XAttrFormat` would affect this feature's persisted packed state.

## Test Signals

Tests should cover empty/null input, small-only, large-only, mixed ordering, exact threshold behavior, lookup by prefixed name, no-value xattrs, equality/hash consistency, and fsimage/snapshot round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/XAttrFeature.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/XAttrFormat.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/XAttrFormat.java

## Purpose

`XAttrFormat.java` defines the compact binary encoding for HDFS xattrs used both in memory and on disk. The source was read as a complete 195-line file.

## Important APIs, Types, and Functions

The enum fields are `RESERVED`, `NS_EXT`, `NAME`, and `NS`, each backed by `LongBitFormat`. Important methods are `getNamespace`, `getName`, `toInt`, `toXAttr`, `toXAttrs`, `getXAttr`, and `toBytes`. `XATTR_VALUE_LEN_MAX` caps values to less than 64 KiB in packed form.

## Control Flow

`toInt` allocates or retrieves a serial number for the xattr name and combines namespace low bits, namespace extension bits, and name ID into an integer record. `toBytes` emits for each xattr a big-endian 4-byte record, 2-byte unsigned value length, and optional value bytes. `toXAttrs` scans a byte array sequentially and reconstructs builders. `getXAttr` avoids unpacking all entries by comparing namespace and name while scanning.

## State and Persistence Behavior

This format is explicitly persistent and incompatible if changed. Name strings are persisted indirectly through `SerialNumberManager.XATTR` and fsimage string tables. Packed bytes are embedded in `XAttrFeature`.

## Dependencies and Integration Points

It integrates with `XAttr`, `XAttrHelper`, `SerialNumberManager`, Guava `Ints`, and `LongBitFormat`. FSImage load uses `toXAttr(record, value, stringTable)` to resolve historical string table IDs.

## Risks and Edge Cases

Malformed byte arrays can cause index errors because parsing assumes well-formed storage. Value length must fit in 16 bits; larger packed values are rejected and should be handled by `XAttrFeature` as large list entries. Namespace ordinal encoding depends on `XAttr.NameSpace` ordering.

## Test Signals

Tests should cover byte-level round trips, all namespaces including extended namespace bits, null and zero-length values, oversized value rejection, lookup by prefixed name, string table decoding, malformed/truncated bytes, and compatibility with existing fsimage fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/XAttrFormat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/XAttrPermissionFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/XAttrPermissionFilter.java

## Purpose

`XAttrPermissionFilter.java` enforces which xattr namespaces are visible or mutable through public HDFS APIs. The source was read as a complete 132-line file.

## Important APIs, Types, and Functions

The static APIs are `checkPermissionForApi(FSPermissionChecker, XAttr, boolean)`, `checkPermissionForApi(FSPermissionChecker, List<XAttr>, boolean)`, and `filterXAttrsForApi`.

## Control Flow

Permission checking allows `USER` xattrs for normal access and `TRUSTED` only for superusers, auditing superuser access via `checkSuperuserPrivilege`. `RAW` is allowed only when the path is under `/.reserved/raw`. The special security xattr `security.hdfs.unreadable.by.superuser` is allowed only without a value. All other `SECURITY` and `SYSTEM` cases are denied through `FSPermissionChecker.denyUserAccess`. Filtering mirrors the visibility rules but includes the special unreadable-by-superuser xattr.

## State and Persistence Behavior

The class is stateless. It gates access to xattrs that are persisted on inodes by `XAttrStorage` and fsimage/edit logs.

## Dependencies and Integration Points

It integrates with `FSPermissionChecker`, `XAttr`, `XAttrHelper`, `AccessControlException`, and `HdfsServerConstants.SECURITY_XATTR_UNREADABLE_BY_SUPERUSER`. It is used by xattr NameNode operations before reading or writing API-visible xattrs.

## Risks and Edge Cases

Incorrect raw-path detection can expose internal raw attributes. The special security xattr deliberately permits only a no-value form; accepting a value would change security semantics. Superuser auditing is an explicit side effect for trusted/user namespace access.

## Test Signals

Tests should cover each namespace for superuser and non-superuser, raw path and non-raw path, the unreadable-by-superuser xattr with and without value, list filtering, empty lists, and audit/deny callbacks on `FSPermissionChecker`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/XAttrPermissionFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/XAttrStorage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/XAttrStorage.java

## Purpose

`XAttrStorage.java` provides small static helpers for reading and replacing xattr features on inodes. The source was read as a complete 81-line file.

## Important APIs, Types, and Functions

The APIs are `readINodeXAttrByPrefixedName`, `readINodeXAttrs`, and `updateINodeXAttrs`.

## Control Flow

Read-by-name fetches the inode's `XAttrFeature` for a snapshot ID and delegates to `getXAttr`. Read-all fetches xattrs from `INodeAttributes` or returns an empty list. Update removes any existing feature from the inode, then adds a new `XAttrFeature` if the supplied list is non-empty.

## State and Persistence Behavior

The helpers mutate inode feature state under the caller's lock. Because inode feature state is serialized to fsimage and journaled by higher-level operations, replacing the feature is a persistent namespace mutation once logged.

## Dependencies and Integration Points

It integrates with `INode`, `INodeAttributes`, `XAttrFeature`, `XAttr`, and `QuotaExceededException`. Comments require callers to hold FSDirectory read or write locks as appropriate.

## Risks and Edge Cases

The update path removes before adding, so callers must ensure exceptions from adding a new feature are handled consistently by surrounding transaction logic. Locking is a caller contract, not enforced here.

## Test Signals

Tests should cover reading absent features, snapshot-specific reads, replacing existing xattrs, clearing with null/empty lists, quota exception propagation, and lock-contract coverage in higher-level xattr operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/XAttrStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/fgl/FSNLockManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/fgl/FSNLockManager.java

## Purpose

`FSNLockManager.java` defines the abstraction used by `FSNamesystem` to acquire global or fine-grained NameNode locks by `RwLockMode`. The source was read as a complete 187-line file.

## Important APIs, Types, and Functions

The interface declares read/write lock and unlock methods, interruptible variants, overloads with operation names and lock-report suppliers, hold checks, read hold count, queue length, long-hold counters, metrics toggles, threshold getters/setters, and testing hooks for a `ReentrantReadWriteLock`.

## Control Flow

There is no implementation flow. `GlobalFSNamesystemLock` maps all modes to one lock, while `FineGrainedFSNamesystemLock` maps modes to FS, BM, or both locks.

## State and Persistence Behavior

The interface owns no state. Implementations own in-memory synchronization primitives and metrics; no persistent data is written directly.

## Dependencies and Integration Points

It depends on `RwLockMode`, `Supplier<String>`, `ReentrantReadWriteLock`, and `VisibleForTesting`. It is the contract that lets NameNode code use `RwLockMode.GLOBAL`, `FS`, and `BM` without binding to a concrete lock layout.

## Risks and Edge Cases

Implementations must agree on lock order and reporting semantics. Returning sentinel values for unsupported global aggregate metrics must be understood by metrics consumers.

## Test Signals

Tests should run the same lock-behavior suite against global and fine-grained implementations, covering reentrancy, interruptible acquisition, supplier reporting, metrics toggles, threshold propagation, hold checks, and test-lock hooks where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/fgl/FSNLockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/fgl/FineGrainedFSNamesystemLock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/fgl/FineGrainedFSNamesystemLock.java

## Purpose

`FineGrainedFSNamesystemLock.java` implements `FSNLockManager` by splitting the NameNode lock into a namespace/tree lock (`FS`) and a block-manager/data-node lock (`BM`). The source was read as a complete 285-line file.

## Important APIs, Types, and Functions

The class owns two `FSNamesystemLock` instances, `fsLock` and `bmLock`. It implements all `FSNLockManager` methods, dispatching on `RwLockMode.GLOBAL`, `FS`, or `BM`.

## Control Flow

For global lock mode, acquisition always takes FS then BM, and unlock releases BM then FS. Single-mode operations take only the selected lock. Interruptible global acquisition releases the already-held FS lock if interrupted while acquiring BM. Hold checks require both locks for global write/read and one lock for single modes. Metrics and threshold setters propagate to both locks, while getters return FS values. Queue length and long-hold counters return `-1` for global because there is no single aggregate queue.

## State and Persistence Behavior

State is in-memory lock state and lock metrics. No metadata is persisted, but correctness protects all NameNode namespace and block state mutations.

## Dependencies and Integration Points

It integrates with `FSNamesystemLock`, `RwLockMode`, and `MutableRatesWithAggregation`. NameNode code relies on its lock ordering to avoid deadlocks when operations need both namespace and block-manager state.

## Risks and Edge Cases

The FS-before-BM order is the key invariant. Any caller or future lock path that takes BM then FS can deadlock. The global read hold count returns only FS count for content-summary use, which is not a full aggregate. Test lock replacement is unsupported and throws.

## Test Signals

Tests should cover global and single-mode locking, interrupt during second-lock acquisition, unlock order, hold checks while write-locked, read hold counts, metrics propagation to both locks, unsupported test hooks, and concurrency scenarios that would reveal order inversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/fgl/FineGrainedFSNamesystemLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/fgl/GlobalFSNamesystemLock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/fgl/GlobalFSNamesystemLock.java

## Purpose

`GlobalFSNamesystemLock.java` implements `FSNLockManager` with a single traditional `FSNamesystemLock`, ignoring fine-grained lock modes. The source was read as a complete 150-line file.

## Important APIs, Types, and Functions

The class owns one `FSNamesystemLock` named `lock` and delegates every lock, unlock, metric, threshold, and testing hook method to it.

## Control Flow

All `RwLockMode` values acquire the same read or write lock. Unlock overloads pass operation names, suppression flags, or lock-report suppliers to the underlying lock. `hasReadLock` treats a current-thread write lock as satisfying read ownership.

## State and Persistence Behavior

State is the in-memory global read/write lock and its metrics. It protects persistent NameNode namespace state indirectly by serializing in-memory mutations before they are logged or saved.

## Dependencies and Integration Points

It integrates with `FSNamesystemLock`, `RwLockMode`, `MutableRatesWithAggregation`, and test replacement of the underlying `ReentrantReadWriteLock`.

## Risks and Edge Cases

Because all modes map to one lock, code tested only with this implementation can miss fine-grained ordering bugs. Conversely it provides simpler, conservative behavior for deployments not using fine-grained locking.

## Test Signals

Tests should verify delegation, read/write hold checks, queue and long-hold metrics, threshold changes, supplier reporting, interruptible acquisition, and `setLockForTests`/`getLockForTests`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/fgl/GlobalFSNamesystemLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/fgl/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/fgl/package-info.java

## Purpose

`package-info.java` declares the `org.apache.hadoop.hdfs.server.namenode.fgl` package for fine-grained NameNode locking classes. The source was read as a complete 17-line file.

## Important APIs, Types, and Functions

There are no types or functions beyond the package declaration.

## Control Flow

No executable control flow exists.

## State and Persistence Behavior

The file owns no runtime or persistent state.

## Dependencies and Integration Points

It groups `FSNLockManager`, `FineGrainedFSNamesystemLock`, and `GlobalFSNamesystemLock` in the NameNode fine-grained locking package.

## Risks and Edge Cases

There is no behavioral risk in the file itself. Package-level documentation could be expanded if lock ordering needs stronger generated docs.

## Test Signals

No direct tests are needed; compile/package discovery covers it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/fgl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ActiveState.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ActiveState.java

## Purpose

`ActiveState.java` implements the active HA state for a NameNode. The source was read as a complete 76-line file.

## Important APIs, Types, and Functions

The class extends `HAState` with `HAServiceState.ACTIVE`. It implements `checkOperation`, `shouldPopulateReplQueues`, `setState`, `enterState`, and `exitState`.

## Control Flow

Active state allows all operation categories. It permits transition only to `NameNode.STANDBY_STATE` through `setStateInternal`. Entering active calls `HAContext.startActiveServices`; exiting calls `HAContext.stopActiveServices`; IO failures are wrapped as `ServiceFailedException`.

## State and Persistence Behavior

The class itself is stateless aside from inherited transition time. Entering active starts services that write edits, serve clients, and populate replication queues.

## Dependencies and Integration Points

It integrates with `HAState`, `HAContext`, `NameNode.ACTIVE_STATE/STANDBY_STATE`, Hadoop HA service states, and NameNode operation categories.

## Risks and Edge Cases

An active transition must fully start active services or fail cleanly. Allowing all operations means fencing and state-transition correctness must be handled before reaching this state.

## Test Signals

Tests should cover allowed operations, replication queue population, active-to-standby transition, rejection of unsupported transitions, and service start/stop exception wrapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ActiveState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/BootstrapStandby.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/BootstrapStandby.java

## Purpose

`BootstrapStandby.java` implements the `hdfs namenode -bootstrapStandby` style tool that initializes a standby NameNode's local storage from another NameNode in an HA nameservice. The source was read as a complete 597-line file.

## Important APIs, Types, and Functions

The class implements `Tool` and `Configurable`. Key methods are `run`, `parseArgs`, `doRun`, `parseConfAndFindOtherNN`, `format`, `doPreUpgrade`, `doUpgrade`, `downloadImage`, `checkLogsAvailableForRead`, `checkLayoutVersion`, `parseProvidedConfigurations`, `formatAndDownloadAliasMap`, and static `run`. It defines error codes for connection, layout mismatch, already formatted storage, and unavailable logs. The nested `AliasMapStorageDirectory` supports formatting checks for alias map directories.

## Control Flow

`run` parses `-force`, `-nonInteractive`, and `-skipSharedEditsCheck`, disables in-progress tailing for bootstrap efficiency, validates HA/shared-edits configuration, logs in as the NameNode principal, and executes as the login user. `doRun` tries configured remote NameNodes until it obtains namespace information, upgrade state, and rolling-upgrade state. It validates layout compatibility, prints the bootstrap summary, creates `NNStorage`, formats or prepares upgrade directories, downloads fsimage and optional rollback image, writes `seen_txid`, finishes upgrade directory renames if needed, and optionally bootstraps an in-memory alias map.

## State and Persistence Behavior

The tool formats local name and edits directories, writes VERSION files, downloads fsimage files and md5 digests, writes `seen_txid`, may create `previous.tmp` and `previous` during upgrade bootstrap, and may delete/recreate the alias map directory. It checks shared edits readability from the downloaded checkpoint transaction through the active's current transaction unless skipped.

## Dependencies and Integration Points

It integrates with `HAUtil`, `DFSUtil`, `NameNodeProxies`, `NamenodeProtocol`, `NamespaceInfo`, `NNStorage`, `FSImage`, `TransferFsImage`, `NNUpgradeUtil`, `Storage.confirmFormat`, `RemoteNameNodeInfo`, `DFSHAAdmin` security configuration, and provided-storage alias map support.

## Risks and Edge Cases

Formatting is destructive and governed by `force`/`interactive`. Bootstrapping from a remote with incompatible layout must stop. Shared edits gaps can produce a standby that cannot catch up, so `checkLogsAvailableForRead` is important unless explicitly skipped. Rolling upgrade needs rollback image handling. Alias map deletion/creation must not erase data unexpectedly without confirmation.

## Test Signals

Tests should cover argument parsing, HA/shared-edits validation, active discovery with failed remotes, layout compatibility in normal and rolling upgrade modes, format confirmation combinations, already formatted storage, upgrade directory transitions, shared edits availability and skip behavior, fsimage and rollback downloads, `seen_txid`, alias map bootstrap, and secure login.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/BootstrapStandby.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/EditLogTailer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/EditLogTailer.java

## Purpose

`EditLogTailer.java` runs on standby/observer NameNodes to continuously read shared edit logs and apply transactions to the local `FSNamesystem`. The source was read as a complete 681-line file.

## Important APIs, Types, and Functions

The main class owns an `EditLogTailerThread`, `FSNamesystem`, `FSEditLog`, remote NameNode iterator, active proxy cache, timing fields, retry settings, and lock batching configuration. Important APIs are constructor, `start`, `stop`, `catchupDuringFailover`, `doTailEdits`, `triggerActiveLogRoll`, test timer hooks, and metrics getters. The nested `MultipleNameNodeProxy` lazily finds a remote active NameNode for `rollEditLog`.

## Control Flow

Construction reads tailing, log-roll, backoff, timeout, retry, in-progress, and max-transactions-per-lock settings; discovers remote NameNodes for log rolling; validates IPC addresses; and initializes metrics timing. The tailer thread runs as the login subject. Each loop optionally triggers active log rolling when too long has elapsed since successful loading and new transactions have been loaded since the last trigger, then takes the checkpoint lock, calls `doTailEdits`, records metrics, updates name-dir size after triggered rolls, and sleeps with exponential backoff when no edits are available.

`doTailEdits` selects input streams after the last applied txid, records fetch time, takes the global namesystem write lock interruptibly, verifies the image txid did not change before loading, applies edits through `FSImage.loadEdits` with `maxTxnsPerLock`, records loaded count, updates `lastLoadTimeMs` and `lastLoadedTxnId`, and releases the lock. `catchupDuringFailover` repeatedly tails without in-progress streaming until no more edits load, intended to run after the background thread has stopped.

## State and Persistence Behavior

The tailer mutates the standby namespace in memory by replaying persisted edit logs from shared storage or journal managers. It does not write namespace edits itself, but loaded txids and metrics reflect durable journal progress. It may ask the active to roll logs so finalized segments become available.

## Dependencies and Integration Points

It integrates with `FSEditLog`, `FSImage`, `FSNamesystem`, `EditLogInputStream`, `EditLogInputException`, `NameNodeMetrics`, `RemoteNameNodeInfo`, `NamenodeProtocolPB`, `RPC.waitForProxy`, `NamenodeProtocolTranslatorPB`, `SecurityUtil`, `SubjectInheritingThread`, and `RwLockMode.GLOBAL`.

## Risks and Edge Cases

Deadlock avoidance depends on interruptible namesystem locking during failover. Empty stream selection during an active log roll is treated as transient, while read errors after streams are selected are significant. In-progress tailing changes latency and journal-manager behavior. Remote active discovery is intentionally slow and retry-based. `nnCount` must be nonzero when log rolling is enabled, or retry arithmetic would be unsafe. Exponential backoff must reset after successful loads.

## Test Signals

Tests should cover tailing finalized and in-progress logs, empty stream transient failures, edit load exceptions with partial counts, failover catchup, stopping while blocked on locks or RPC, active log rolling timeout and retry across remotes, backoff timing, max transactions per lock, metrics increments, name-dir size update after roll, and secure subject execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/EditLogTailer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/HAContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/HAContext.java

## Purpose

`HAContext.java` defines the context operations that HA state objects use to manipulate a NameNode. The source was read as a complete 86-line file.

## Important APIs, Types, and Functions

The interface declares state accessors, active and standby service start/stop methods, standby prepare-to-stop hook, namesystem write lock/unlock, `checkOperation`, and `allowStaleReads`.

## Control Flow

There is no implementation flow. `HAState` calls these methods during transitions and operation checks. Implementations provide the actual NameNode service lifecycle behavior.

## State and Persistence Behavior

The interface owns no state. Implementations control persistent side effects indirectly by starting edit-log writers, tailers, checkpointing, block managers, and RPC services appropriate to active or standby state.

## Dependencies and Integration Points

It integrates with `HAState`, `ServiceFailedException`, `NameNode.OperationCategory`, and `StandbyException`.

## Risks and Edge Cases

The comments call out a race where clients can block behind a standby holding the namesystem lock; operation checks should happen both before and after lock acquisition in relevant callers. Incorrect implementation can allow writes in standby or fail to stop checkpointing before activation.

## Test Signals

Tests should verify state classes call context methods in the expected order, operation checks are enforced around locks, stale-read configuration is honored, and service lifecycle failures propagate as transition failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/HAContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/HAState.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/HAState.java

## Purpose

`HAState.java` is the abstract base for NameNode HA service states and implements the shared transition skeleton. The source was read as a complete 163-line file.

## Important APIs, Types, and Functions

The class stores `HAServiceState state` and `lastHATransitionTime`. Key methods are `getServiceState`, `setStateInternal`, `getLastHATransitionTime`, `prepareToEnterState`, `enterState`, `prepareToExitState`, `exitState`, `setState`, `checkOperation`, `shouldPopulateReplQueues`, and `toString`.

## Control Flow

Allowed transitions in subclasses call `setStateInternal`. That method prepares the old state to exit, prepares the new state to enter, takes the context write lock, exits the old state, swaps context state, enters the new state, records transition wall-clock time, and unlocks. Base `setState` accepts no transitions except self-transition.

## State and Persistence Behavior

The class persists no disk state. Transition side effects are delegated to `HAContext`, which starts or stops services that affect edits, checkpoints, and replication queues. `lastHATransitionTime` is in-memory observability state.

## Dependencies and Integration Points

It integrates with Hadoop HA `HAServiceState`, `ServiceFailedException`, `StandbyException`, `Time`, and NameNode operation categories. `ActiveState` and `StandbyState` provide concrete behavior.

## Risks and Edge Cases

The prepare hooks run without the context lock and must avoid destructive changes because a later prepare hook may fail. The order of setting context state before entering the new state means callers must handle failures carefully at higher levels. Unsupported transitions intentionally fail.

## Test Signals

Tests should cover allowed and disallowed transitions, self-transition no-op, hook ordering, lock/unlock on success and failure, transition time update, and exception propagation from enter/exit hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/HAState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/NameNodeHAProxyFactory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/NameNodeHAProxyFactory.java

## Purpose

`NameNodeHAProxyFactory.java` creates non-HA NameNode RPC proxies for use by HA failover proxy providers. The source was read as a complete 52-line file.

## Important APIs, Types, and Functions

The generic class implements `HAProxyFactory<T>`. It provides two `createProxy` overloads and `setAlignmentContext`.

## Control Flow

Both factory methods delegate to `NameNodeProxies.createNonHAProxy` for a concrete NameNode address and return the proxy. The overload with `fallbackToSimpleAuth` passes the optional `AlignmentContext`, enabling coordinated client alignment behavior where supported.

## State and Persistence Behavior

The only state is the optional in-memory `alignmentContext`. No persistent data is written.

## Dependencies and Integration Points

It integrates with HDFS `NameNodeProxies`, Hadoop `Configuration`, `UserGroupInformation`, `AlignmentContext`, and the HA client proxy-provider stack.

## Risks and Edge Cases

The overload without `fallbackToSimpleAuth` does not pass `alignmentContext`; callers needing alignment must use the newer overload. Proxy creation failures propagate as IOExceptions and drive failover provider behavior.

## Test Signals

Tests should verify proxy creation delegates with retries and fallback auth, alignment context is passed in the supported overload, and failures from `NameNodeProxies` propagate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/NameNodeHAProxyFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/RemoteNameNodeInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/RemoteNameNodeInfo.java

## Purpose

`RemoteNameNodeInfo.java` represents another NameNode in the same HA nameservice, including its configuration, NameNode ID, IPC address, and HTTP address. The source was read as a complete 129-line file.

## Important APIs, Types, and Functions

Static factories are `getRemoteNameNodes(Configuration)` and `getRemoteNameNodes(Configuration, String)`. Instance methods expose IPC address, NameNode ID, HTTP address, configuration, mutable IPC setter, `toString`, `equals`, and `hashCode`.

## Control Flow

The factory resolves the nameservice ID, returns an empty list outside HA/federation, obtains configurations for other nodes from `HAUtil`, reads each peer's NameNode ID and service address, derives HTTP/HTTPS info-server URL using the original client's HTTP scheme, and creates `RemoteNameNodeInfo` entries. `equals` compares URL strings instead of `URL.equals` to avoid blocking DNS resolution.

## State and Persistence Behavior

The object is transient configuration state. `setIpcAddress` lets callers override service address resolution, for example to force service RPC address for log rolling.

## Dependencies and Integration Points

It integrates with `DFSUtil`, `HAUtil`, `NameNode.getServiceAddress`, `DFSUtil.getInfoServerWithDefaultHost`, `BootstrapStandby`, `EditLogTailer`, and `StandbyCheckpointer`-adjacent HA code.

## Risks and Edge Cases

Address validation is intentionally left to callers, so invalid port or wildcard addresses can appear until later checks. HTTP scheme is taken from the original configuration, while host defaults come from peer IPC addresses.

## Test Signals

Tests should cover no nameservice behavior, multiple peer discovery, HTTP and HTTPS schemes, NameNode ID extraction, IPC override, equals/hash without DNS blocking, and invalid address handling by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/RemoteNameNodeInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/StandbyCheckpointer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/StandbyCheckpointer.java

## Purpose

`StandbyCheckpointer.java` runs inside a standby NameNode to periodically save a local namespace checkpoint and upload it to peer NameNodes. The source was read as a complete 513-line file.

## Important APIs, Types, and Functions

The class owns `CheckpointConf`, `FSNamesystem`, `CheckpointerThread`, remote and local HTTP addresses, upload thread factory, cancellation state, and per-receiver upload state. Important methods are constructor, `setNameNodeAddresses`, `start`, `stop`, `triggerRollbackCheckpoint`, `doCheckpoint`, `cancelAndPreventCheckpoints`, `getLastCheckpointTime`, and `countUncheckpointedTxns`. The nested `CheckpointReceiverEntry` tracks last upload and whether this standby is primary for a receiver.

## Control Flow

The background thread runs as the login user, sleeps for the checkpoint check period, refreshes Kerberos credentials, checks for rollback image need, transaction threshold, or elapsed-period threshold, then creates a `Canceler` under `cancelLock` unless checkpoints are temporarily prevented. `doCheckpoint` takes the checkpoint lock, verifies edit log is open for read, compares current and previous checkpoint txids, chooses `IMAGE_ROLLBACK` during rolling upgrade when needed, calls `FSImage.saveNamespace`, optionally writes legacy OIV output, releases the lock, then uploads the saved image to remote NameNodes using a bounded executor. Uploads run when this standby is primary for the receiver or the receiver has been quiet long enough.

## State and Persistence Behavior

The checkpointer persists fsimage or rollback fsimage files in local NameNode storage and may upload them to remote active NameNodes through `TransferFsImage`. It updates `lastCheckpointTime` after success and receiver upload timestamps after accepted uploads. Cancellation is transient, but it protects state transition to active from racing with checkpoint save/upload.

## Dependencies and Integration Points

It integrates with `CheckpointConf`, `FSNamesystem`, `FSImage`, `TransferFsImage`, `NameNodeFile`, `HAUtil`, `DFSUtil`, `NameNode`, `CheckpointFaultInjector`, `Canceler`, `SaveNamespaceCancelledException`, `MultipleIOException`, and secure `SubjectInheritingThread` execution.

## Risks and Edge Cases

Checkpoint cancellation and failover prevention are critical; a standby must not continue a checkpoint while becoming active. Upload rejection can be normal when the peer is standby, already has a newer image, or recently accepted another image. More than half of uploads failing with exceptions aborts the checkpoint. Rollback checkpoint flags must be cleared only after rollback image exists.

## Test Signals

Tests should cover threshold and period triggering, rollback checkpoint triggering, no-op when txid unchanged, saveNamespace cancellation, prevent window during failover, parallel and serial upload modes, upload result handling, majority upload exception threshold, receiver quiet period/primary logic, legacy OIV errors, secure relogin, and remote address validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/StandbyCheckpointer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/StandbyState.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/StandbyState.java

## Purpose

`StandbyState.java` implements standby and observer HA states for the NameNode. The source was read as a complete 121-line file.

## Important APIs, Types, and Functions

The class extends `HAState`, stores `isObserver`, and implements `setState`, `enterState`, `prepareToExitState`, `exitState`, `checkOperation`, `shouldPopulateReplQueues`, and `toString`.

## Control Flow

Constructors choose `HAServiceState.STANDBY` or `OBSERVER`. Standby can transition to active or observer; observer can transition to standby. Entering starts standby services, preparing to exit asks the context to prepare stopping standby services, and exiting stops standby services. Operation checks allow unchecked operations and reads only when stale reads are allowed. Observer write attempts throw `ObserverRetryOnActiveException`; other disallowed operations throw `StandbyException`.

## State and Persistence Behavior

The class itself has only the observer flag and inherited transition time. Standby services include edit tailing and checkpointing that maintain local namespace state from persisted journals.

## Dependencies and Integration Points

It integrates with `HAContext`, `NameNode.ACTIVE_STATE`, `STANDBY_STATE`, `OBSERVER_STATE`, `OperationCategory`, `StandbyException`, and `ObserverRetryOnActiveException`.

## Risks and Edge Cases

Observer read behavior depends on `allowStaleReads`. Access-time updates can turn opens into writes, so observer write rejection intentionally directs clients to retry on active.

## Test Signals

Tests should cover standby and observer transition matrix, operation categories, stale read allowance, observer write retry exception type, replication queue non-population, and service lifecycle hook failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/StandbyState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/metrics/ECBlockGroupsMBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/metrics/ECBlockGroupsMBean.java

## Purpose

`ECBlockGroupsMBean.java` defines JMX metrics for erasure-coded block groups in `FSNamesystem`. The source was read as a complete 69-line file.

## Important APIs, Types, and Functions

The interface declares getters for low redundancy, corrupt, missing, bytes in future block groups, pending deletion EC blocks, total EC block groups, and enabled EC policies.

## Control Flow

There is no implementation flow. `FSNamesystem` or related metrics providers implement the getters.

## State and Persistence Behavior

The interface owns no state. Values reflect in-memory block-manager state derived from namespace and block reports.

## Dependencies and Integration Points

It complements `FSNamesystemMBean`, `ReplicatedBlocksMBean`, and `NameNodeMetrics` by splitting EC-specific block health from replicated block health.

## Risks and Edge Cases

Metric names become JMX attributes, so signature changes affect operators. Counts must be kept semantically distinct from replicated block counts.

## Test Signals

Tests should verify JMX exposure and values for EC policy enablement, low redundancy, corrupt, missing, future, pending deletion, and total EC block groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/metrics/ECBlockGroupsMBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/metrics/FSNamesystemMBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/metrics/FSNamesystemMBean.java

## Purpose

`FSNamesystemMBean.java` defines the stable JMX interface for NameNode filesystem state, capacity, block health, DataNode state, snapshots, locking, edit-log sync, tokens, and storage policy satisfier metrics. The source was read as a complete 271-line file.

## Important APIs, Types, and Functions

The interface declares many getters, including `getFSState`, block and capacity totals, file totals, pending reconstruction, low redundancy, scheduled replication, live/dead/stale/decommission/maintenance DataNode counts, snapshot stats, max objects, pending deletion blocks, top user op counts, encryption zone count, lock queue length, sync counts/times, current delegation tokens, pending SPS paths, and reconstruction queue initialization progress. Deprecated names for replication are retained.

## Control Flow

There is no executable flow. Implementers compute values from `FSNamesystem`, block manager, DataNode manager, edit log, snapshot manager, token manager, and other subsystems.

## State and Persistence Behavior

The interface owns no state. Metrics are views over live in-memory NameNode state, much of which is reconstructed from fsimage, edits, and block reports.

## Dependencies and Integration Points

It is part of the NameNode JMX surface and is referenced by EC and replicated block MBeans plus operator tooling. JMX naming conventions are explicitly part of the contract.

## Risks and Edge Cases

Because the interface is stable and externally visible, removing or renaming methods breaks monitoring. Deprecated methods must remain consistent with replacements. JSON-returning methods such as top user counts need stable encoding.

## Test Signals

Tests should validate JMX registration and representative values for capacity, block health, DataNode counts, snapshots, lock queue length, sync totals, tokens, SPS paths, maintenance states, deprecated aliases, and reconstruction queue progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/metrics/FSNamesystemMBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/metrics/NameNodeMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/metrics/NameNodeMetrics.java

## Purpose

`NameNodeMetrics.java` maintains mutable Hadoop metrics for NameNode runtime activity, edit-log latency, block reports, encryption key operations, image transfer servlet calls, and standby edit tailing. The source was read as a complete 484-line file.

## Important APIs, Types, and Functions

The class is annotated `@Metrics(name="NameNodeActivity", context="dfs")` and owns many `@Metric` counters, gauges, rates, stats, and quantile arrays. Important methods include constructor, static `create`, `shutdown`, `totalFileOps`, numerous `incr*` operation counters, block queue setters, transaction/sync metrics, block/cache report latencies, safe mode and image load time setters, get/put image metrics, EDEK/resource-check metrics, and edit-tail metrics.

## Control Flow

`create` obtains the metrics session ID, process name from `NamenodeRole`, registers JVM metrics, reads percentile intervals, and registers a new `NameNodeMetrics` instance with the default metrics system. The constructor tags process/session and creates quantile metrics for each configured interval. Increment/add methods update both aggregate rate/stat and corresponding quantile arrays where present. `totalFileOps` sums the operation counters considered filesystem operations.

## State and Persistence Behavior

All state is in-memory metrics state exported through Hadoop metrics sinks. There is no persistence, though external metrics systems may scrape or store values.

## Dependencies and Integration Points

It integrates with Hadoop metrics2 annotations, `DefaultMetricsSystem`, `MetricsRegistry`, `MutableCounterLong`, `MutableGaugeInt`, `MutableRate`, `MutableStat`, `MutableQuantiles`, `JvmMetrics`, `DFSConfigKeys`, and NameNode subsystems that call increment methods.

## Risks and Edge Cases

Metrics must be updated on all relevant operation paths or operator observability becomes misleading. Casting long elapsed times to int for safe mode and image load time can truncate extreme values. Percentile interval configuration controls quantile allocation; empty intervals mean no quantiles. `shutdown` shuts down the default metrics system, which affects process-wide metrics.

## Test Signals

Tests should verify registration tags, counters included in `totalFileOps`, each increment/add method mutates expected metrics, quantiles are updated for configured intervals, safe mode/image load setters, edit-tail metrics from `EditLogTailer`, image servlet metrics from transfer endpoints, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/metrics/NameNodeMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/metrics/ReplicatedBlocksMBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/metrics/ReplicatedBlocksMBean.java

## Purpose

`ReplicatedBlocksMBean.java` defines JMX metrics for contiguous replicated blocks in `FSNamesystem`. The source was read as a complete 73-line file.

## Important APIs, Types, and Functions

The interface declares getters for low redundancy, corrupt, missing, missing replication-one blocks, badly distributed blocks, bytes in future blocks, pending deletion replicated blocks, and total replicated blocks.

## Control Flow

There is no implementation flow. Implementers compute values from block-manager state.

## State and Persistence Behavior

The interface owns no state. Values are live views over block metadata and DataNode reports.

## Dependencies and Integration Points

It complements `ECBlockGroupsMBean` and `FSNamesystemMBean`, separating replicated block health from erasure-coded block group health.

## Risks and Edge Cases

Metric names are externally visible JMX attributes. Misclassifying EC block groups as replicated blocks, or vice versa, would distort operational health dashboards.

## Test Signals

Tests should verify JMX exposure and counts for replicated low redundancy, corrupt, missing, replication-one missing, badly distributed, future, pending deletion, and total block states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/metrics/ReplicatedBlocksMBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/AbstractINodeDiff.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/AbstractINodeDiff.java

## Purpose

`AbstractINodeDiff.java` is the base diff node for reconstructing inode state across HDFS snapshots. The source was read as a complete 138-line file.

## Important APIs, Types, and Functions

The abstract generic class is parameterized by inode type `N`, attribute snapshot type `A`, and concrete diff type `D`. It stores `snapshotId`, optional `snapshotINode`, and `posteriorDiff`. Methods include `compareTo`, `getSnapshotId`, `setSnapshotId`, `getPosterior`, `setPosterior`, `saveSnapshotCopy`, `getSnapshotINode`, `toString`, `writeSnapshot`, and abstract `combinePosteriorAndCollectBlocks`, `destroyDiffAndCollectBlocks`, and `write`.

## Control Flow

Diffs form a chronological list with posterior links toward newer diffs. To reconstruct a snapshot inode, `getSnapshotINode` walks this diff and posterior diffs until it finds a saved inode copy or reaches current state. Deletion and diff combination behavior are left to concrete directory/file diff implementations.

## State and Persistence Behavior

Each diff persists snapshot ID and concrete diff data through `write`. `snapshotINode` captures a point-in-time inode attribute copy when a change first needs snapshot preservation. Reclaim methods collect blocks and inodes when snapshots or diffs are destroyed.

## Dependencies and Integration Points

It integrates with `INode`, `INodeAttributes`, `SnapshotFSImageFormat.ReferenceMap`, `AbstractINodeDiffList`, and snapshot fsimage serialization.

## Risks and Edge Cases

Posterior link consistency is critical for correct reconstruction. Saving a snapshot copy twice is rejected. Concrete combine/destroy implementations must reclaim blocks without deleting data still referenced by remaining snapshots.

## Test Signals

Tests should cover snapshot copy save once, posterior traversal, compare ordering, snapshot ID rewriting, serialization of snapshot IDs, concrete diff deletion/combination, and reclaim behavior with chained snapshots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/AbstractINodeDiff.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/AbstractINodeDiffList.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/AbstractINodeDiffList.java

## Purpose

`AbstractINodeDiffList.java` manages the ordered list of inode snapshot diffs used to answer snapshot-state queries and delete snapshots. The source was read as a complete 351-line file.

## Important APIs, Types, and Functions

The abstract generic class owns a lazily allocated `DiffList<D>`. Important methods are `asList`, `isEmpty`, `clear`, abstract `createDiff` and `createSnapshotCopy`, `deleteSnapshotDiff`, `addDiff`, `addFirst`, `getFirst`, `getLast`, `getLastSnapshotId`, `getPrior`, `updatePrior`, `getDiffById`, `getSnapshotById`, `getDiffIndexById`, `changedBetweenSnapshots`, `getSnapshotINode`, `checkAndAddLatestSnapshotDiff`, `saveSelf2Snapshot`, `iterator`, and `toString`.

## Control Flow

Diffs are sorted chronologically by snapshot ID. Adding at the end updates the previous last diff's posterior link. Deleting a snapshot either renames the first diff to the prior snapshot, removes and destroys the first diff when no prior exists, or combines the removed diff into its previous diff and relinks posterior pointers. Lookup uses binary search; when an exact diff is absent, `getDiffById` returns the next diff because no change occurred between the requested snapshot and that next state. `changedBetweenSnapshots` computes the diff-index range between two snapshots.

## State and Persistence Behavior

The list is in-memory inode snapshot metadata persisted by concrete diff serialization. Deletions can reclaim blocks and inode state through `INode.ReclaimContext`. Lazy allocation avoids per-inode overhead for files/directories without snapshot changes.

## Dependencies and Integration Points

It integrates with `DiffList`, `DiffListByArrayList`, `Snapshot`, `SnapshotManager`, `INode`, `INodeAttributes`, and concrete file/directory diff classes.

## Risks and Edge Cases

Binary-search insertion-point semantics are subtle. Snapshot deletion ordering mode restricts deletion to the first diff. Renaming a diff to a prior ID instead of removing it preserves state but can be easy to misread. Posterior link maintenance must stay in sync with list operations.

## Test Signals

Tests should cover empty lists, add first/last, posterior links, prior lookup inclusive/exclusive, exact and inexact diff lookup, snapshot deletion for first/middle/no-prior cases, deletion-ordered mode assertions, changed-between-snapshots ranges, snapshot inode fallback to current inode, and reclaim behavior from concrete implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/AbstractINodeDiffList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DiffList.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DiffList.java

## Purpose

`DiffList.java` defines the list abstraction used by snapshot diff lists, allowing different backing implementations while preserving binary-search and range-minimization operations. The source was read as a complete 158-line file.

## Important APIs, Types, and Functions

The interface extends `Iterable<T extends Comparable<Integer>>`. It defines static `emptyList` and `unmodifiableList`, plus `get`, `isEmpty`, `size`, `remove`, `addLast`, `addFirst`, `binarySearch`, and `getMinListForRange`.

## Control Flow

The static empty list is a `DiffListByArrayList` over an empty Java list. `unmodifiableList` wraps another `DiffList` and delegates read/search/range operations while throwing `UnsupportedOperationException` for mutation methods.

## State and Persistence Behavior

The interface owns no state. Implementations hold in-memory snapshot diff references that are persisted through higher-level snapshot fsimage serialization.

## Dependencies and Integration Points

It integrates with `AbstractINodeDiffList`, `DiffListByArrayList`, and `INodeDirectory` for `getMinListForRange`, which supports efficient cumulative diff calculations.

## Risks and Edge Cases

The raw static `EMPTY_LIST` relies on generic casts through the static method. Callers must not mutate the unmodifiable wrapper. Binary search ordering depends on diff `compareTo(Integer)` implementation.

## Test Signals

Tests should cover empty list behavior, unmodifiable wrapper mutation failures, delegated binary search and iteration, add/remove ordering in concrete implementations, and minimal range list behavior for directory diffs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DiffList.java -->
