# subset-b-007424 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotDiffReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotDiffReport.java

## Purpose
`SnapshotDiffReport` is the client-visible value object returned for an HDFS snapshot diff between two snapshots or between a snapshot and the live directory. It deliberately exposes a compact report of changed relative paths and change types rather than the full NameNode-side inode diff graph. It also carries `DiffStats` counters for snapshot diff processing metrics.

## Important APIs, Types, and Functions
The `DiffType` enum defines the report vocabulary: `CREATE`, `MODIFY`, `DELETE`, and `RENAME`, with printable labels `+`, `M`, `-`, and `R`. `getTypeFromLabel` maps display labels back to enum values and returns `null` for unknown labels, while `parseDiffType` delegates to `valueOf` on an upper-case string and throws for invalid input.

`DiffReportEntry` is the per-change record. It stores a `DiffType`, a byte-array source path relative to the snapshot root, and an optional target path for renames. Constructors accept either already-flattened byte paths or path-component arrays, converting components through `DFSUtilClient.byteArray2bytes`. `toString` prints the label and a `./relative/path` display path; rename entries add ` -> ./target`. `getPathString` maps an empty path to `Path.CUR_DIR`.

The outer class stores `snapshotRoot`, `fromSnapshot`, `toSnapshot`, `diffList`, and `diffStats`. The simple constructor creates zeroed stats. `getLaterSnapshotName` returns `toSnapshot`, and `toString` emits a human-readable report header plus all entries.

`DiffStats` stores directory/file processed and compared counts and total children-listing time. The constructor currently assigns the processed and compared fields from the opposite constructor parameters for dirs and files, so callers and tests should watch for this field-order behavior.

## Control Flow
There is no external I/O or active diff computation in this class. The NameNode-side snapshot machinery constructs `DiffReportEntry` instances and a `SnapshotDiffReport`; clients then access fields or render it. Rendering normalizes `null` or empty snapshot names to "current directory" and otherwise prints "snapshot <name>".

Equality for `DiffReportEntry` checks type plus source and target byte-array content. `hashCode` uses only source and target paths, not the diff type, which is legal but can increase collisions if the same path appears with different types.

## State and Persistence Behavior
Instances are mostly immutable after construction. The list reference is stored directly, so the effective immutability depends on callers not mutating the supplied list. Paths are stored as raw byte arrays and returned directly, so callers can mutate arrays unless they copy them. There is no persistence in this class; persistence/serialization happens through protobuf/PB helper layers and NameNode snapshot code.

## Dependencies and Integration Points
This class depends on `DFSUtilClient` for HDFS byte/string path encoding, Hadoop `Path` constants for `.` and `/`, and shaded Guava `Objects` for hashes. It is constructed from NameNode snapshot diff code such as `SnapshotDiffInfo` and `SnapshotManager`, returned through `ClientProtocol`/`DistributedFileSystem`, and surfaced through WebHDFS JSON utilities and CLI snapshot commands.

## Risks and Edge Cases
Wire and API compatibility depends on stable `DiffType` names and labels. Empty paths are special and render as `.`, while non-empty paths render with a `./` prefix. `getTypeFromLabel` returning `null` can push validation to callers. Direct exposure of mutable byte arrays and list references can surprise clients. The `DiffStats` constructor parameter assignment deserves regression coverage because it can silently swap processed/compared counters.

## Test Signals
Snapshot diff behavior is covered by tests under `hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotDiffReport.java`, `TestRenameWithSnapshots`, `TestSnapshotDeletion`, `DFSTestUtil.verifySnapshotDiffReport`, WebHDFS tests in `TestWebHDFS`, and encryption-zone snapshot tests in `TestEncryptionZones`. Useful focused tests would assert label parsing, root/empty path rendering, rename target rendering, equality/hash behavior, and `DiffStats` getter values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotDiffReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotDiffReportListing.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotDiffReportListing.java

## Purpose
`SnapshotDiffReportListing` is the paged/listing form of snapshot diff output. Instead of returning one complete diff report, it carries bounded lists of modified, created, and deleted entries plus cursor state so clients can iterate over large diffs across multiple RPCs. The limit is tied to `dfs.snapshotdiff-report.limit` on the NameNode side.

## Important APIs, Types, and Functions
`DiffReportListingEntry` stores the inode ids (`dirId`, `fileId`), relative source path components, optional target path components, and an `isReference` flag used for rename/reference handling. Constructors accept either `byte[][]` path components or flattened byte paths, using `DFSUtilClient.bytes2byteArray` for conversion. `sourcePath` is required and checked with `Preconditions.checkNotNull`; `targetPath` is optional.

The outer class exposes `getModifyList`, `getCreateList`, `getDeleteList`, `getLastPath`, `getLastIndex`, and `getIsFromEarlier`. The no-arg constructor returns empty lists, an empty `lastPath`, index `-1`, and `isFromEarlier=false`.

## Control Flow
This class is a DTO. NameNode snapshot listing logic fills the three lists and cursor fields; `DistributedFileSystem.SnapshotDiffReportListingIterator` repeatedly calls `DFSClient.getSnapshotDiffReportListing` and advances using `lastPath`, `lastIndex`, and `isFromEarlier`. Consumers can then merge or render entries into a full report.

## State and Persistence Behavior
Fields are final and list references are stored as provided. Byte-array paths and path-component arrays are returned directly. There is no local persistence; it crosses RPC and JSON boundaries via protobuf/PB helper and WebHDFS JSON conversion code.

## Dependencies and Integration Points
The class depends on `DFSUtilClient` for path byte conversion and Hadoop `Preconditions`. It integrates with `ClientProtocol.getSnapshotDiffReportListing`, `DFSClient`, `DistributedFileSystem`, router-based federation snapshot routing, `JsonUtil`/`JsonUtilClient`, and `SnapshotDiffReportGenerator`.

## Risks and Edge Cases
Because lists and arrays are not defensively copied, callers can mutate DTO state. Pagination correctness depends on preserving `lastPath`, `lastIndex`, and direction (`isFromEarlier`) exactly. Empty/default reports are valid and should remain serializable. Target path may be null and must be handled by JSON/protobuf converters.

## Test Signals
`TestSnapshotDiffReport.testSnapshotDiffReportRemoteIterator*` exercises paged iteration. `TestJsonUtil.testSnapshotDiffReportListingEmptyReport` and `testSnapshotDiffReportListing` cover JSON round trips. Router tests cover federation pass-through. Focused tests should assert default cursor values, source-path null rejection, byte path conversion, and null target-path handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotDiffReportListing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotStatus.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotStatus.java

## Purpose
`SnapshotStatus` is client-side metadata for an individual snapshot. It wraps the snapshot directory's `HdfsFileStatus`, the numeric snapshot ID, deletion state, and parent path bytes, and provides formatting for `dfs lsSnapshottableDir`-style output.

## Important APIs, Types, and Functions
Constructors either build a directory `HdfsFileStatus` from primitive metadata or accept a prebuilt `HdfsFileStatus`. `getSnapshotID`, `isDeleted`, `getDirStatus`, `getParentFullPath`, and `setParentFullPath` expose the fields. `getFullPath` builds a `Path` under `<parent>/.snapshot/<localName>`, using `/` for null or empty parent paths.

`print` computes column widths across an array of statuses and emits permission, replication, owner, group, length, modification time, snapshot ID, deletion status, and snapshot path. `getSnapshotPath` constructs `.snapshot` paths, inserting a separator if the snapshottable directory path lacks a trailing slash. `getParentPath` strips the `.snapshot` portion when present.

## Control Flow
The main behavior is path construction and formatted printing. `print` first scans all rows for maximum field widths, then formats each row with a `SimpleDateFormat` of `yyyy-MM-dd HH:mm`. Null or empty input arrays print a blank line.

## State and Persistence Behavior
`dirStatus`, `snapshotID`, and `isDeleted` are final. `parentFullPath` is mutable via `setParentFullPath` and is returned directly as a byte array. The class does not persist state itself; it is populated from NameNode RPC responses and consumed by CLI/admin code.

## Dependencies and Integration Points
It depends on `HdfsFileStatus.Builder`, `FsPermission`, `HdfsFileStatus.Flags`, `DFSUtilClient`, `Path`, and `HdfsConstants.DOT_SNAPSHOT_DIR`. It integrates with client protocol calls that list snapshots and with shell/admin output formatting.

## Risks and Edge Cases
`getParentPath` assumes `.snapshot` is preceded by a separator and returns `substring(0, index - 1)`; malformed paths where `.snapshot` starts at index 0 would be unsafe. `print` calls `DFSUtilClient.bytes2String(status.parentFullPath)` without the null/empty guard used in `getFullPath`, so callers should supply populated parent paths before printing. Mutable parent bytes can affect later path rendering.

## Test Signals
Snapshot shell command tests and snapshot listing tests provide integration coverage. Focused tests should verify root parent handling, deleted vs active printing, `getSnapshotPath` separator behavior, `getParentPath` for paths with and without `.snapshot`, and printing with null/empty arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshottableDirectoryStatus.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshottableDirectoryStatus.java

## Purpose
`SnapshottableDirectoryStatus` is metadata for a directory on which snapshots are enabled. It reports ordinary directory status plus snapshot count/quota and parent path, and provides CLI-friendly formatting and a JMX/JSON-friendly nested bean.

## Important APIs, Types, and Functions
`COMPARATOR` sorts statuses by parent path bytes, then local name bytes, using `DFSUtilClient.compareBytes`. Constructors either build an `HdfsFileStatus` from primitive fields or accept a prebuilt one. Getters expose snapshot count, quota, parent path, and directory status.

`getFullPath` handles the root directory specially: null/empty parent plus empty local name becomes `/`; otherwise it builds either `new Path(localName)` or `new Path(parent, localName)`. `print` formats rows with directory permission, replication, owner, group, length, modification time, snapshot number, snapshot quota, and full path. The nested `Bean` exposes path, snapshot number/quota, modification time, short permission, owner, and group.

## Control Flow
The class is mostly declarative. `print` does a width pre-scan, builds a format string, and prints each status. `COMPARATOR` is used by callers that need deterministic output ordering.

## State and Persistence Behavior
Fields are final and there is no local persistence. As with other HDFS protocol DTOs, byte-array parent paths are returned directly and not defensively copied. It is serialized through RPC/PB conversion elsewhere.

## Dependencies and Integration Points
It depends on `HdfsFileStatus`, `FsPermission`, `DFSUtilClient`, and Hadoop `Path`. It is returned by NameNode/client protocol methods for listing snapshottable directories and consumed by DFS shell/admin display and metrics/JMX-style bean conversion.

## Risks and Edge Cases
Root handling is explicit and should not be regressed. The comparator assumes non-null parent path arrays. Direct byte-array exposure allows mutation by consumers. Formatting depends on `HdfsFileStatus` values being non-null enough for width calculation.

## Test Signals
Snapshot command tests and snapshottable-directory listing tests are the primary integration signals. Unit tests should cover comparator ordering, root path construction, null/empty parent path behavior, quota/count formatting, and bean field projection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshottableDirectoryStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/StripedBlockInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/StripedBlockInfo.java

## Purpose
`StripedBlockInfo` is a private, evolving DTO for erasure-coded striped block groups. It packages the block group, participating datanodes, per-internal-block tokens, block indices, and erasure coding policy so downstream code can perform block-group operations such as checksum calculation.

## Important APIs, Types, and Functions
The constructor accepts an `ExtendedBlock`, `DatanodeInfo[]`, `Token<BlockTokenIdentifier>[]`, `byte[]` block indices, and an `ErasureCodingPolicy`. Getters expose each field directly: `getBlock`, `getDatanodes`, `getBlockTokens`, `getBlockIndices`, and `getErasureCodingPolicy`.

## Control Flow
There is no control flow beyond construction and access. `Sender.blockGroupChecksum` consumes this object and serializes each component into `OpBlockGroupChecksumProto`.

## State and Persistence Behavior
All fields are final, but arrays are stored and returned directly, so object contents can be mutated externally. The class itself does not persist; it participates in DataTransferProtocol protobuf serialization.

## Dependencies and Integration Points
It depends on HDFS protocol block/datanode types, erasure coding policies, and block tokens. It integrates with `DataTransferProtocol.blockGroupChecksum`, the `Sender` implementation, DataNode checksum handling, and client-side erasure-coded checksum workflows.

## Risks and Edge Cases
Array lengths must stay aligned: datanodes, block tokens, and block indices refer to corresponding internal blocks. The class does not validate nulls or lengths, so misuse can surface later during protobuf conversion or DataNode processing.

## Test Signals
Block group checksum and erasure-coding integration tests should cover it indirectly. Focused tests would assert serialization preserves datanode/token/index ordering and handles missing/null fields according to caller contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/StripedBlockInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SystemErasureCodingPolicies.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SystemErasureCodingPolicies.java

## Purpose
`SystemErasureCodingPolicies` defines Hadoop HDFS's built-in erasure coding policies. Although the class is private, its policy IDs are effectively stable wire/storage compatibility points because older clients and NameNodes rely on consistent IDs.

## Important APIs, Types, and Functions
The class defines byte IDs for `RS_6_3`, `RS_3_2`, `RS_6_3_LEGACY`, `XOR_2_1`, and `RS_10_4`, all with a default 1 MiB cell size. It also defines a special replication policy using `ErasureCodeConstants.REPLICATION_POLICY_ID`.

`SYS_POLICIES` is an unmodifiable list of the EC policies, excluding the replication policy. Static maps `SYSTEM_POLICIES_BY_NAME` and `SYSTEM_POLICIES_BY_ID` are populated at class load. Public static accessors are `getPolicies`, `getByID`, `getByName`, and `getReplicationPolicy`.

## Control Flow
The static initializer iterates over `SYS_POLICIES` and builds name/id lookup maps. Runtime calls are simple lookups or list returns.

## State and Persistence Behavior
All state is static and process-local. Policy IDs and schema names must remain stable across releases because they are stored in metadata and exchanged with clients. `getPolicies` returns an unmodifiable list, and maps are private.

## Dependencies and Integration Points
It depends on `ErasureCodingPolicy` and `ErasureCodeConstants`. It integrates with NameNode policy management, client APIs that list/query EC policies, PB conversion, and DataTransferProtocol block-group checksum paths.

## Risks and Edge Cases
Changing IDs, removing policies, or changing default cell size for existing IDs can create cross-version inconsistency. `getByID` and `getByName` return `null` for unknown values, so callers need validation. The replication policy is not included in `getPolicies`, which is intentional and should be documented in callers.

## Test Signals
Erasure-coding API tests should assert built-in names, IDs, and lookup behavior. Compatibility tests should pin the exact ID-to-schema mapping and replication-policy special handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SystemErasureCodingPolicies.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/UnresolvedPathException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/UnresolvedPathException.java

## Purpose
`UnresolvedPathException` represents encountering a symbolic link while resolving an HDFS path. It extends `UnresolvedLinkException` and carries enough path components to compute the resolved path for clients.

## Important APIs, Types, and Functions
One constructor accepts a message for `RemoteException` instantiation. The main constructor stores the original path, preceding path component, remainder, and symlink target. `getResolvedPath` combines the target and remainder differently depending on whether the link target is absolute. `getMessage` returns the superclass message if present; otherwise it returns the resolved path string.

## Control Flow
`getResolvedPath` checks whether the remainder is null/empty. If the link target is absolute, it discards `preceding` and appends only the remainder. If relative, it joins `preceding`, `linkTarget`, and optional `remainder`.

## State and Persistence Behavior
The fields are plain strings populated at construction. There is no persistence, but the message constructor supports remote exception reconstruction where only a message is available.

## Dependencies and Integration Points
It depends on Hadoop `Path` and `UnresolvedLinkException`. It is thrown by path resolution logic and consumed by FileSystem link resolvers such as those in `DistributedFileSystem` methods.

## Risks and Edge Cases
Path joining behavior must preserve absolute-target semantics. The `path` field is stored but not used in resolution. Null `preceding` or `linkTarget` would fail through `Path` construction, so callers must populate them. The comment has a typo but no behavioral impact.

## Test Signals
Symlink resolution tests should assert absolute and relative target behavior with and without remainders. RemoteException wrapping tests should cover the message-only constructor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/UnresolvedPathException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/XAttrNotFoundException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/XAttrNotFoundException.java

## Purpose
`XAttrNotFoundException` is a specific `IOException` used when a requested extended attribute does not exist.

## Important APIs, Types, and Functions
The class defines `DEFAULT_EXCEPTION_MSG` as "At least one of the attributes provided was not found." The no-arg constructor uses that default, and the string constructor passes a custom message to `IOException`.

## Control Flow
There is no control flow beyond exception construction.

## State and Persistence Behavior
The only state is the inherited exception message and serial version UID. It is suitable for RPC propagation as an HDFS protocol exception type.

## Dependencies and Integration Points
It depends only on `IOException` and Hadoop interface annotations. It is used by xattr read/list paths in NameNode and client code to distinguish missing attributes from other I/O failures.

## Risks and Edge Cases
Callers that catch generic `IOException` can lose the specific "not found" signal. The default message intentionally handles one or more missing attributes, not a single named attribute.

## Test Signals
XAttr tests should assert the exception type and default/custom messages for missing extended attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/XAttrNotFoundException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ZoneReencryptionStatus.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ZoneReencryptionStatus.java

## Purpose
`ZoneReencryptionStatus` tracks the state of re-encryption for an HDFS encryption zone. It is consumed by crypto admin/listing APIs and updated by NameNode re-encryption logic. The class comment states that `FSDirectory` locking provides synchronization except for test-only methods.

## Important APIs, Types, and Functions
`State` has three values: `Submitted`, `Processing`, and `Completed`. The nested `Builder` validates that `id`, `state`, `ezKeyVersionName`, and `submissionTime` are set, then populates all status fields. Public getters expose zone id/name, state, key version, submission/completion time, cancellation, last checkpoint file, files re-encrypted, and failure count.

Mutable operations include `reset`, `setZoneName`, `cancel`, package-private `setState`, `markZoneCompleted`, `markZoneSubmitted`, and `updateZoneProcess`. `markZoneCompleted` loads completion time, cancellation flag, metrics, and clears the checkpoint. `markZoneSubmitted` resets then restores submitted state from protobuf. `updateZoneProcess` updates checkpoint and metrics while work is active.

## Control Flow
The object starts in `Submitted` state with zeroed times/metrics after `reset`. NameNode re-encryption code updates it as edit-log/protobuf information is replayed or as the re-encryption handler makes progress. Listing code resolves and sets `zoneName` for user-facing output.

## State and Persistence Behavior
This is a mutable status object. The comment explicitly says `state` is in-memory only: after failover it is restored as `Submitted`, or `Completed` if `completionTime != 0`, based on persisted protobuf fields. Persistent fields include id, key version, submission/completion times, cancellation, checkpoint file, and metrics. The last checkpoint stores a file name rather than inode id so replay can resume even if the inode was removed.

## Dependencies and Integration Points
It depends on `HdfsProtos.ReencryptionInfoProto` and Hadoop `Preconditions`. It integrates with `EncryptionZoneManager`, `ReencryptionHandler`, `ReencryptionUpdater`, `FSDirEncryptionZoneOp`, `FSNamesystem.listReencryptionStatus`, `DistributedFileSystem.listReencryptionStatus`, `CryptoAdmin`, and router/federation client protocols.

## Risks and Edge Cases
Correct lock ownership is critical because the class is mutable. Builder validation rejects id/submission time zero, which assumes zero is never a valid value. Failover semantics depend on protobuf restoration and completion time. `setZoneName` rejects null. Metrics can be reset or overwritten during state transitions, so tests should confirm no accidental loss during cancellation/completion.

## Test Signals
`hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestReencryption.java` heavily exercises re-encryption status listing and completion. Additional focused tests should cover builder validation, submitted/processing/completed transitions from `ReencryptionInfoProto`, cancellation behavior, checkpoint clearing on completion, and failover/replay semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ZoneReencryptionStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/BlockConstructionStage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/BlockConstructionStage.java

## Purpose
`BlockConstructionStage` enumerates the stages of HDFS block write, append, recovery, close, and transfer operations in the data transfer protocol.

## Important APIs, Types, and Functions
The enum values are ordered in regular/recovery pairs for append, streaming, and close. `PIPELINE_SETUP_CREATE`, `TRANSFER_RBW`, and `TRANSFER_FINALIZED` do not have recovery pairs. `getRecoveryStage` maps a regular stage to its recovery stage using `ordinal() | RECOVERY_BIT` and rejects `PIPELINE_SETUP_CREATE`.

## Control Flow
Callers use the enum to describe a `writeBlock` or transfer stage. Recovery mapping is purely ordinal-based.

## State and Persistence Behavior
Enum names are serialized through protobuf conversion in `DataTransferProtoUtil` by matching names. The ordinal order is also behaviorally significant for `getRecoveryStage`, even though protobuf uses names.

## Dependencies and Integration Points
It integrates with `DataTransferProtocol.writeBlock`, `Sender.writeBlock`, `DataTransferProtoUtil.toProto/fromProto`, DataNode block receiver/write pipeline code, and pipeline recovery logic.

## Risks and Edge Cases
Reordering enum values breaks `getRecoveryStage`. Adding new regular/recovery stages requires preserving the paired ordering rule. Calling `getRecoveryStage` on `PIPELINE_SETUP_CREATE` throws; calling it on already-recovery or transfer values can produce unintended enum values because only create is explicitly guarded.

## Test Signals
Pipeline recovery tests and write pipeline integration cover this indirectly. Unit tests should pin `getRecoveryStage` for each expected regular stage and reject unsupported stages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/BlockConstructionStage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/BlockPinningException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/BlockPinningException.java

## Purpose
`BlockPinningException` is a specific `IOException` used when a data transfer operation fails because of block pinning constraints.

## Important APIs, Types, and Functions
The class has a single string constructor and a serial version UID.

## Control Flow
It is thrown by `DataTransferProtoUtil.checkBlockOpStatus` when the response status is `ERROR_BLOCK_PINNED` and the caller opted into checking block-pinning errors.

## State and Persistence Behavior
Only the inherited exception message is stored. It participates in normal Java/RPC exception handling.

## Dependencies and Integration Points
It integrates with data transfer response handling, block movement/replacement paths, and balancing/pinning behavior where pinned blocks should not be moved.

## Risks and Edge Cases
If callers do not pass `checkBlockPinningErr=true`, the same status becomes a generic `IOException`, losing semantic detail. Tests should cover both branches.

## Test Signals
Data transfer and balancer tests involving pinned blocks should assert this exception type when requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/BlockPinningException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/DataTransferProtoUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/DataTransferProtoUtil.java

## Purpose
`DataTransferProtoUtil` contains static helpers for translating data transfer protocol objects to/from protobufs and for validating block operation responses.

## Important APIs, Types, and Functions
`fromProto` and `toProto` map `BlockConstructionStage` to `OpWriteBlockProto.BlockConstructionStage` by enum name. `toProto(DataChecksum)` and `fromProto(ChecksumProto)` translate checksum type and bytes-per-checksum through `PBHelperClient`; `fromProto` returns null for null input.

`buildClientHeader` creates a `ClientOperationHeaderProto` with a base header and client name. `buildBaseHeader` converts the block and token and optionally attaches tracing context from `Tracer.getCurrentSpan()` via `TraceUtils`.

`checkBlockOpStatus` validates a `BlockOpResponseProto`. Non-success statuses become `InvalidBlockTokenException` for `ERROR_ACCESS_TOKEN`, `BlockPinningException` for `ERROR_BLOCK_PINNED` when requested, or generic `IOException` otherwise. Error messages include the response message and caller-supplied log info.

## Control Flow
The class is stateless. Sender and receiver code call conversion helpers while building or parsing protocol messages. Response checking branches by protobuf status.

## State and Persistence Behavior
No persistent state. Trace context, if present, is captured into protobuf headers and crosses the wire.

## Dependencies and Integration Points
It depends on DataTransfer protobufs, HDFS `ExtendedBlock`, block tokens, `PBHelperClient`, `DataChecksum`, tracing classes, and exception types. It is used by `Sender`, DataNode receivers, clients reading operation responses, and tests for data transfer failures.

## Risks and Edge Cases
Enum-name mapping requires protobuf and Java enum names to stay aligned. `toProto(DataChecksum)` does not handle null checksums. Trace info must remain optional for compatibility. Status handling changes can alter retry behavior for invalid tokens or block pinning.

## Test Signals
`TestDataTransferProtocol` exercises response statuses. Focused tests should cover checksum round trips, trace header inclusion/exclusion, all non-success status branches, and enum conversion stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/DataTransferProtoUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/DataTransferProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/DataTransferProtocol.java

## Purpose
`DataTransferProtocol` defines the streaming protocol operations between HDFS clients and DataNodes and between DataNodes. It is the Java contract implemented by serializers like `Sender` and server-side DataNode handlers.

## Important APIs, Types, and Functions
The interface pins `DATA_TRANSFER_VERSION = 28`, with a warning that it must change when `DatanodeInfo` serialization changes. Operations include `readBlock`, `writeBlock`, `transferBlock`, short-circuit FD/shm requests, `replaceBlock`, `copyBlock`, `blockChecksum`, and `blockGroupChecksum`.

`writeBlock` carries extensive pipeline state: storage type/id, targets, target storage types/ids, source DataNode, construction stage, pipeline size, byte range/generation stamp, requested checksum, caching strategy, lazy persist flag, and pinning flags. `blockGroupChecksum` accepts `StripedBlockInfo` for erasure-coded checksums.

## Control Flow
The interface itself has no implementation. `Sender` writes the version/opcode/protobuf for each method; DataNode xceiver code reads the op and dispatches to matching server behavior.

## State and Persistence Behavior
There is no local state. The version number and method parameter schema are wire compatibility state. Tokens and checksums are serialized per operation.

## Dependencies and Integration Points
It depends on HDFS block/datanode types, storage types, block tokens, caching strategy, short-circuit shared memory slot IDs, checksums, and erasure-coded striped block info. It integrates with DFS input/output streams, `DataStreamer`, DataNode `DataXceiver`, balancer/dispatcher code, and encrypted/SASL transport setup.

## Risks and Edge Cases
Wire compatibility is the dominant risk. Adding/changing parameters requires matching protobuf and receiver changes. The version comment notes that serialization of supporting types can require a version bump. Misaligned target arrays or pinning/storage-id arrays can corrupt pipeline semantics.

## Test Signals
`TestDataTransferProtocol`, `TestClientProtocolForPipelineRecovery`, `TestDataXceiverBackwardsCompat`, EC checksum tests, short-circuit tests, and encrypted transfer tests are important. Tests should pin protocol version behavior, method support, and protobuf compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/DataTransferProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/IOStreamPair.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/IOStreamPair.java

## Purpose
`IOStreamPair` is a small container for the input and output streams used by data transfer connections, especially after SASL or crypto wrapping.

## Important APIs, Types, and Functions
It exposes public final `InputStream in` and `OutputStream out` fields. The constructor stores both. `close` closes both streams via `IOUtils.closeStream`.

## Control Flow
No active control flow. SASL/client code returns either a raw stream pair or a wrapped pair, and callers use the fields directly.

## State and Persistence Behavior
The pair owns references to streams but not underlying sockets by itself. Closing is best-effort through `IOUtils.closeStream`, which suppresses/logs close exceptions rather than failing early.

## Dependencies and Integration Points
It depends on Java stream types and Hadoop `IOUtils`. It is used by `SaslDataTransferClient`, `DataTransferSaslUtil.createStreamPair`, `SaslParticipant.createStreamPair`, and `EncryptedPeer`.

## Risks and Edge Cases
Public fields make ownership simple but allow direct misuse. Close order is input then output; callers that need a flush should flush before closing. Null streams are tolerated only if `IOUtils.closeStream` handles nulls.

## Test Signals
SASL/encrypted transfer tests indirectly cover stream wrapping. Focused tests could assert close behavior and integration with `EncryptedPeer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/IOStreamPair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/InvalidEncryptionKeyException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/InvalidEncryptionKeyException.java

## Purpose
`InvalidEncryptionKeyException` signals that an HDFS data transfer encryption key failed verification during SASL/data transfer negotiation.

## Important APIs, Types, and Functions
It extends `IOException`, has a no-arg constructor and a string-message constructor, and defines a serial version UID.

## Control Flow
`DataTransferSaslUtil.readSaslMessage` throws it when a SASL negotiation message has status `ERROR_UNKNOWN_KEY`. `DataEncryptionKeyFactory.clearDataEncryptionKey` is intended to be called by retry paths after this exception.

## State and Persistence Behavior
Only exception message state is stored. It influences retry behavior rather than persistent metadata.

## Dependencies and Integration Points
It integrates with encrypted data transfer SASL negotiation, `DataEncryptionKeyFactory`, DFS client retry logic, and DataNode SASL server responses.

## Risks and Edge Cases
Preserving this specific exception type matters because callers may refresh encryption keys and retry. Wrapping it as generic `IOException` could break recovery. Empty messages are possible from the no-arg constructor.

## Test Signals
Encrypted transfer tests should cover invalid key responses and key-cache clearing/retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/InvalidEncryptionKeyException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/Op.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/Op.java

## Purpose
`Op` defines one-byte operation codes for the HDFS data transfer protocol.

## Important APIs, Types, and Functions
Codes range from `WRITE_BLOCK` 80 through `BLOCK_GROUP_CHECKSUM` 90, with `CUSTOM` 127. `read(DataInput)` reads a byte and maps it to an enum with a private `valueOf(byte)`. `write(DataOutput)` writes the code.

## Control Flow
The mapping subtracts `FIRST_CODE` and indexes into `values()`, returning null for out-of-range codes. This assumes the enum values from 80 through 90 are contiguous and ordered exactly like their codes.

## State and Persistence Behavior
The byte codes are wire protocol state and must remain stable. There is no runtime mutable state.

## Dependencies and Integration Points
It integrates with `Sender.op`, DataNode operation dispatch, and all data transfer protocol readers/writers.

## Risks and Edge Cases
Adding an enum value before `CUSTOM` or creating non-contiguous codes can break `valueOf(byte)` because it indexes by ordinal. `CUSTOM` at 127 is not contiguous with 80-90, so reading byte 127 currently maps outside the contiguous range and returns null rather than `CUSTOM`.

## Test Signals
Data transfer protocol tests should pin every opcode byte and read/write round trip. A focused test should document the `CUSTOM` read behavior if intentional.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/Op.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/PacketHeader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/PacketHeader.java

## Purpose
`PacketHeader` represents the per-packet wire header for HDFS block data transfer. It describes block offset, packet sequence number, last-packet marker, data length, and optional sync-block flag, excluding checksums and data payload.

## Important APIs, Types, and Functions
The serialized header consists of a 4-byte packet length, a 2-byte protobuf-header length, and a `PacketHeaderProto`. `PKT_LENGTHS_LEN` is 6 bytes and `PKT_MAX_HEADER_LEN` is the length prefix plus the maximum default protobuf size.

Constructors either create an empty object for reading or build a proto from packet fields. The packet length must be at least four bytes. `syncBlock` is only set in the proto when true to avoid changing the header length unnecessarily. Getters expose proto fields and packet length.

`readFields` parses from a `ByteBuffer` or `DataInputStream`. `setFieldsFromData` parses a supplied header byte array. `putInBuffer`, `write`, and `getBytes` serialize the header. `sanityCheck` enforces positive data length except for the last packet, zero data length for the last packet, and sequence number increment by one.

## Control Flow
Writers construct and serialize headers before checksums/data. Receivers parse length prefixes and protobuf bytes, then validate sequencing through `sanityCheck` in higher-level code.

## State and Persistence Behavior
The object stores mutable `packetLen` and `proto` fields after construction/parsing. Wire format is compatibility-sensitive; comments note Hadoop 2.0.0-alpha incompatibility around variable-length headers and `syncBlock`.

## Dependencies and Integration Points
It depends on `PacketHeaderProto`, `ByteBufferOutputStream`, shaded protobuf, and Guava primitive byte sizes. It integrates with `PacketReceiver`, `BlockReceiver`, DFS output stream packet creation, and DataNode/client data pipelines.

## Risks and Edge Cases
The maximum proto size is computed from default fields and enforced with asserts, not runtime exceptions. Negative proto lengths or malformed protobufs surface during reads. `equals` compares only proto, not packet length; `hashCode` is seqno only. Compatibility depends on preserving prefix layout and optional `syncBlock` behavior.

## Test Signals
Packet receiver and data transfer tests should cover serialization round trips, sanity checks, last-packet rules, malformed lengths, sync-block headers, and equality behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/PacketHeader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/PacketReceiver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/PacketReceiver.java

## Purpose
`PacketReceiver` reads one HDFS data transfer packet at a time from an `InputStream` or `ReadableByteChannel`, parses the header, and exposes slices for checksums and data. It is used on both read and write pipeline paths.

## Important APIs, Types, and Functions
`MAX_PACKET_SIZE` is loaded from `DFS_DATA_TRANSFER_MAX_PACKET_SIZE` using a fresh `HdfsConfiguration`. The constructor chooses heap or direct buffers and allocates enough space for length prefixes.

`receiveNextPacket` delegates to `doRead`. `getHeader`, `getDataSlice`, and `getChecksumSlice` expose the most recently parsed packet. `mirrorPacketTo` writes the full last packet to an output stream, only for heap buffers. `close` returns direct buffers to a static `DirectBufferPool`.

`doRead` reads packet length and header length, validates payload and total sizes, reallocates the buffer if needed, reads the rest, parses `PacketHeader`, computes checksum length as `dataPlusChecksumLen - dataLen`, and calls `reslicePacket`.

## Control Flow
The receiver first reads the fixed 6-byte length prefix, then reads the variable header/checksum/data region. `Preconditions.checkState` prevents reading past a last-packet marker. `doReadFully` dispatches to channel reads or array-backed stream reads. `readChannelFully` loops until the buffer is full or throws premature EOF.

## State and Persistence Behavior
The object keeps the current full packet buffer plus slices and header. Direct buffers are pooled and should be returned by `close`; `finalize` attempts cleanup as a fallback. Slices are views into `curPacketBuf` and become invalid after reading the next packet.

## Dependencies and Integration Points
It depends on `PacketHeader`, `DirectBufferPool`, `HdfsClientConfigKeys`, `IOUtils`, and Java NIO buffers/channels. It is used by DataNode `BlockReceiver`, client-side block readers, and tests under `protocol/datatransfer/TestPacketReceiver.java`.

## Risks and Edge Cases
Malformed lengths can cause OOME if not capped, so `MAX_PACKET_SIZE` validation is critical. The InputStream path requires heap buffers; direct buffers are only safe with channels. `mirrorPacketTo` only works for non-direct buffers. Buffer reuse means callers must consume slices before the next receive. `finalize` is a weak safety net and close discipline matters.

## Test Signals
`TestPacketReceiver` covers packet receiving, mirroring, and configured max packet size. Additional tests should cover negative header lengths, payload length below four, oversized packets, premature EOF, direct-buffer close/pool behavior, and reading after last packet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/PacketReceiver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/PipelineAck.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/PipelineAck.java

## Purpose
`PipelineAck` represents acknowledgement messages flowing back through an HDFS write pipeline. It carries a sequence number, per-DataNode statuses, optional per-reply flags for ECN and slow-node signaling, and downstream ack latency.

## Important APIs, Types, and Functions
`UNKOWN_SEQNO` (`-2`, misspelled in the constant name) identifies out-of-band acks. `SLOW` and `ECN` enums each occupy two bits in a packed header. `StatusFormat` uses `LongBitFormat` to pack status (4 bits), a reserved bit, ECN bits, and slow bits.

Constructors build a `PipelineAckProto` from a seqno, packed reply headers, and optional downstream ack time. `getHeaderFlag` returns stored flags when available or synthesizes old-format flags from the reply status with disabled ECN/SLOW. `isSuccess` checks all statuses. `getOOBStatus` returns OOB statuses only when seqno is `UNKOWN_SEQNO`. `readFields` parses a vint-prefixed protobuf, and `write` writes a delimited protobuf.

Static helpers combine and extract status/ECN/SLOW fields and expose restart OOB status checks.

## Control Flow
DataNodes construct acks with per-hop reply headers; clients/DataStreamer parse them and decide success, retry, congestion, or slow-node handling. Old protobufs without `flag` fields remain readable because `getHeaderFlag` synthesizes default flags.

## State and Persistence Behavior
The mutable `proto` field is populated by constructors or `readFields`. The protobuf wire format and packed bit allocation are compatibility-sensitive. Downstream ack time is transient performance telemetry in the ack.

## Dependencies and Integration Points
It depends on DataTransfer protobufs, `Status`, `LongBitFormat`, `PBHelperClient.vintPrefixed`, and Hadoop test visibility annotations. It integrates with `DataStreamer`, DataNode `BlockReceiver`, pipeline recovery, ECN/slow-node detection, and data transfer tests.

## Risks and Edge Cases
`SLOW.valueOf(int)` and `ECN.valueOf(int)` index arrays without range checks; invalid packed bits can throw. OOB detection depends on protobuf enum numeric ordering. Backward compatibility with old acks depends on `getHeaderFlag` fallback. The typo in `UNKOWN_SEQNO` is part of the API and should not be casually renamed.

## Test Signals
`TestDataTransferProtocol` covers old/new ack compatibility and ECN/SLOW flags. `TestClientProtocolForPipelineRecovery` and `TestDataNodeECN` cover pipeline behavior. Focused tests should pin bit packing, old-proto fallback, OOB status range, and invalid packed header behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/PipelineAck.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/ReplaceDatanodeOnFailure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/ReplaceDatanodeOnFailure.java

## Purpose
`ReplaceDatanodeOnFailure` models the client-side policy for adding a replacement DataNode to a write pipeline after one DataNode fails.

## Important APIs, Types, and Functions
Policies are `DISABLE`, `NEVER`, `DEFAULT`, and `ALWAYS`. `DISABLE` and `NEVER` never replace, `ALWAYS` always replaces when replacement is otherwise meaningful, and `DEFAULT` replaces only when replication is at least three and either existing nodes are at or below half replication or the block is appended/hflushed.

`checkEnabled` throws `UnsupportedOperationException` for `DISABLE`. `isBestEffort` tells callers whether replacement failure should be tolerated. `satisfy` rejects replacement when there are zero existing nodes or enough existing nodes, then delegates to the policy condition. `get(Configuration)` reads enable, policy, and best-effort keys. `write` writes policy settings back to a configuration.

## Control Flow
During write-pipeline recovery, callers load the policy from configuration, check whether replacement is enabled/needed, and either try to add a DataNode or continue/fail depending on `bestEffort`.

## State and Persistence Behavior
Instances are immutable and hold only policy plus best-effort. Persistent behavior is configuration-driven through `HdfsClientConfigKeys.BlockWrite.ReplaceDatanodeOnFailure`.

## Dependencies and Integration Points
It depends on Hadoop `Configuration`, `HadoopIllegalArgumentException`, `HdfsClientConfigKeys`, and `DatanodeInfo`. It integrates with DFS output stream/DataStreamer pipeline recovery and client write behavior.

## Risks and Edge Cases
Invalid policy strings throw `HadoopIllegalArgumentException`. The default condition is sensitive to integer division and append/hflush flags. `DISABLE` and `NEVER` both refuse replacement but differ in `checkEnabled` semantics and config enable state.

## Test Signals
DFS output stream and pipeline recovery tests cover integration. Unit tests should cover each policy, replication/existing-node thresholds, append/hflush overrides, best-effort config, and invalid config values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/ReplaceDatanodeOnFailure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/Sender.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/Sender.java

## Purpose
`Sender` is the client-side serializer for `DataTransferProtocol`. Each method writes the data transfer version, operation code, and operation-specific protobuf to a `DataOutputStream`, then flushes.

## Important APIs, Types, and Functions
`op` writes `DATA_TRANSFER_VERSION` followed by the `Op` byte. `send` logs, writes the op, writes a delimited protobuf, and flushes. `getCachingStrategy` converts optional readahead/drop-behind fields into `CachingStrategyProto`.

Protocol methods build the corresponding protobufs: `OpReadBlockProto`, `OpWriteBlockProto`, `OpTransferBlockProto`, short-circuit request protos, `OpReplaceBlockProto`, `OpCopyBlockProto`, `OpBlockChecksumProto`, and `OpBlockGroupChecksumProto`. `writeBlock` converts target arrays with offsets because the receiver DataNode is not included in downstream target arrays. `releaseShortCircuitFds` and `requestShortCircuitShm` attach tracing context when present. `blockGroupChecksum` serializes striped block datanodes, tokens, indices, EC policy, requested bytes, and checksum options.

## Control Flow
Every public method follows build-protobuf then `send`. Optional fields such as source DataNode, storage ID, slot ID, and tracing info are set only when non-null or present.

## State and Persistence Behavior
The only instance state is the output stream. Wire state is the version/op/protobuf sequence. No local persistence.

## Dependencies and Integration Points
It depends on DataTransfer protobufs, `DataTransferProtoUtil`, `PBHelperClient`, HDFS block/datanode/storage/checksum types, `CachingStrategy`, block tokens, tracing utilities, and `Op`. It is used by DFS client/DataNode/balancer code to initiate operations against a DataNode.

## Risks and Edge Cases
Sender and receiver protobuf schemas must stay in lockstep. Array conversions with offset `1` must align with pipeline semantics. `targetStorageIds` is converted with `Arrays.asList` in `transferBlock`, so null arrays would fail. Flushing every op is required for handshake/protocol progress but affects buffering behavior.

## Test Signals
`TestDataTransferProtocol`, DataNode backward compatibility tests, short-circuit tests, and EC checksum tests cover serialized operations. Focused tests should inspect protobuf contents for optional fields, tracing, target offset handling, block-group checksum metadata, and null optional values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/Sender.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/TrustedChannelResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/TrustedChannelResolver.java

## Purpose
`TrustedChannelResolver` determines whether a data transfer channel should be considered trusted enough to skip SASL/encryption negotiation. The default implementation trusts nothing.

## Important APIs, Types, and Functions
`getInstance(Configuration)` reads `DFS_TRUSTEDCHANNEL_RESOLVER_CLASS`, defaulting to `TrustedChannelResolver`, and instantiates it through `ReflectionUtils`. It implements `Configurable` with `setConf`/`getConf`. `isTrusted()` checks local trust and `isTrusted(InetAddress)` checks remote peer trust; both return false by default.

## Control Flow
`SaslDataTransferClient` calls both local and remote trust checks. If either side is not trusted, it performs SASL/encryption negotiation; only when both are trusted can it skip the handshake.

## State and Persistence Behavior
The resolver stores a `Configuration` reference. Custom subclasses may add their own state, but this base class has no persistence.

## Dependencies and Integration Points
It depends on Hadoop configuration/reflection utilities and Java `InetAddress`. It integrates directly with data transfer SASL client setup and any site-specific trusted network policy.

## Risks and Edge Cases
Custom implementations are security-sensitive: returning true too broadly bypasses SASL/encryption. `getInstance` trusts configuration class loading. Default false is conservative.

## Test Signals
`TestSaslDataTransfer` includes trust-check tests for local and remote trust behavior. Custom resolver tests should verify both local and peer address checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/TrustedChannelResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/DataEncryptionKeyFactory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/DataEncryptionKeyFactory.java

## Purpose
`DataEncryptionKeyFactory` abstracts creation and cache invalidation of HDFS data transfer encryption keys for SASL encrypted handshakes.

## Important APIs, Types, and Functions
`newDataEncryptionKey` returns a new `DataEncryptionKey` or null when encryption is not enabled, depending on the implementation. `clearDataEncryptionKey` is a default no-op hook called after `InvalidEncryptionKeyException` so implementations can force refresh on retry.

## Control Flow
`SaslDataTransferClient` asks the factory for a key when a channel is not fully trusted. If a key is returned, it chooses the specialized encrypted SASL path; otherwise it may use general SASL or skip according to security configuration.

## State and Persistence Behavior
The interface has no state. Implementations may cache keys and use `clearDataEncryptionKey` to invalidate them.

## Dependencies and Integration Points
It depends on `DataEncryptionKey` and `IOException`. It integrates with DFS client encryption setup, DataNode-to-DataNode transfers, and retry handling for invalid encryption keys.

## Risks and Edge Cases
Implementations must distinguish "encryption disabled" from "failed to fetch key" correctly. Failure to clear a bad cached key can cause repeated negotiation failures. Returning keys on trusted channels can impose unnecessary encryption.

## Test Signals
Encrypted transfer tests should verify key creation, invalid-key retry, and cache clearing behavior. Mock factories are useful for asserting when the client requests a key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/DataEncryptionKeyFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/DataTransferSaslUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/DataTransferSaslUtil.java

## Purpose
`DataTransferSaslUtil` implements shared SASL negotiation helpers for HDFS data transfer. It handles QOP validation, configuration translation, SASL message framing, cipher-suite negotiation, crypto stream wrapping, and protocol-specific error mapping.

## Important APIs, Types, and Functions
`SASL_TRANSFER_MAGIC_NUMBER` is `0xDEADBEEF`, sent by clients to identify SASL negotiation instead of a normal data transfer version. `checkSaslComplete` verifies completion and ensures negotiated QOP is one of the requested values, treating null as `auth`. `requestedQopContainsPrivacy` checks for `auth-conf`.

`createSaslPropertiesForEncryption` builds privacy SASL properties with server auth and a digest cipher algorithm. `encryptionKeyToPassword` base64-encodes encryption keys for SASL password use. `getPeerAddress` parses a `Peer` remote address string into an `InetAddress`.

`getSaslPropertiesResolver` translates `dfs.data.transfer.protection` into `hadoop.rpc.protection`, selects the resolver class, and returns null when data transfer SASL protection is not configured.

SASL message readers parse `DataTransferEncryptorMessageProto` via `vintPrefixed`; `ERROR_UNKNOWN_KEY` maps to `InvalidEncryptionKeyException`, access-token errors map to `InvalidBlockTokenException`, generic errors map to `IOException`, and success invokes a handler. Variants read payloads, negotiation cipher options, negotiated cipher option, or handshake secrets.

`negotiateCipherOption` accepts configured AES/CTR/NoPadding or SM4/CTR/NoPadding, generates in/out keys and IVs through `CryptoCodec`, and returns a `CipherOption` if the client offered a supported suite. `createStreamPair` wraps underlying streams in `CryptoInputStream` and `CryptoOutputStream`, reversing in/out keys depending on server/client side. `wrap` and `unwrap` protect cipher keys through the SASL participant. Send helpers write delimited `DataTransferEncryptorMessageProto` messages with status, payload, optional cipher options, optional handshake secret, and optional access-token error flag.

## Control Flow
The negotiation flow uses delimited protobuf messages after the magic number. Client and server exchange SASL payloads, optionally negotiate a cipher suite when privacy is requested, validate QOP, unwrap/wrap cipher keys, and finally switch to either SASL streams or crypto streams.

## State and Persistence Behavior
The class is stateless. Negotiated keys/IVs are generated per handshake and are not persisted. Configuration drives resolver selection, QOP, cipher suite, and key bit length.

## Dependencies and Integration Points
It depends on Hadoop configuration keys, `SaslPropertiesResolver`, Java SASL constants, crypto APIs (`CipherOption`, `CipherSuite`, `CryptoCodec`, crypto streams), HDFS peer/protobuf/PB helper classes, block token exceptions, and shaded protobuf/Guava. It is used by `SaslDataTransferClient` and server-side SASL data transfer code.

## Risks and Edge Cases
Security risks are high: QOP validation must reject downgrade, cipher suite config must reject unsupported names, key/IV direction must be correct for client vs server, and protocol errors must retain specific exception types for retry. `getPeerAddress` depends on remote address string format. `assert codec != null` is not a runtime check when assertions are disabled, so invalid crypto provider setup can fail later. Only one configured cipher suite string is accepted.

## Test Signals
`TestEncryptedTransfer` and `TestSaslDataTransfer` cover encrypted and SASL negotiation. Focused tests should cover QOP validation, no-config resolver returning null, invalid cipher suite errors, AES and SM4 negotiation, error status mapping, handshake secret read/write, access-token error mapping, and stream key direction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/DataTransferSaslUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslDataTransferClient.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslDataTransferClient.java

## Purpose
`SaslDataTransferClient` performs client-side SASL negotiation for HDFS data transfer connections. It is used by both HDFS clients and DataNodes acting as clients to other DataNodes.

## Important APIs, Types, and Functions
Constructors accept configuration, a `SaslPropertiesResolver`, a `TrustedChannelResolver`, and optionally an `AtomicBoolean` that indicates fallback to simple auth.

`newSocketSend`, `socketSend`, and `peerSend` are entry points. They either return raw streams/peer when no handshake is required or wrapped streams/`EncryptedPeer` after negotiation. `checkTrustAndSend` requires both local and remote trust to skip negotiation.

`send` implements the handshake decision tree: use encrypted SASL when a `DataEncryptionKey` is available; skip in unsecured mode; skip on privileged DataNode transfer ports in secure mode; skip if fallback to simple auth is active; use general SASL when a resolver is configured; otherwise skip for the rare secured/no-SASL testing edge.

`getEncryptedStreams` builds privacy SASL props from a data encryption key, optionally updates the block token with a DataNode downstream secret/QOP, encodes the encryption key as username/password, and delegates to `doSaslHandshake`. `getSaslStreams` obtains client SASL properties for the peer address, optionally overwrites downstream QOP and token password, builds username/password from the block token, and delegates to the handshake.

`doSaslHandshake` writes the SASL magic number, sends the initial response plus optional handshake secret, processes server challenge, optionally sends supported cipher options for privacy QOP, reads the negotiated cipher option, validates SASL completion/QOP, unwraps negotiated cipher keys, and returns either crypto streams or SASL streams. On `IOException`, it attempts to send a generic SASL error message but rethrows the original exception with any send failure suppressed.

## Control Flow
The handshake is three-step client SASL exchange plus optional cipher negotiation. Secret-key token mutation is used for DataNode-to-DataNode downstream QOP changes. Trusted-channel checks happen before any key creation on peer/socket paths except `newSocketSend`, which checks local trust before asking for a key.

## State and Persistence Behavior
The object stores configuration, resolvers, fallback flag, and `targetQOP` for testing. It mutates `accessToken` in `updateToken` for downstream DataNode communication by changing the `BlockTokenIdentifier` handshake message and recomputing token password/id. No persistent state is written by this class.

## Dependencies and Integration Points
It depends on `DataTransferSaslUtil`, `SaslParticipant`, HDFS peer/socket abstractions, block tokens, data encryption keys, `TrustedChannelResolver`, `SaslPropertiesResolver`, `UserGroupInformation`, `SecurityUtil`, `SecretManager`, crypto cipher options, and configuration keys. It is constructed by `DFSClient`, DataNode, and balancer/dispatcher code.

## Risks and Edge Cases
Security and compatibility risks are significant. Incorrect trust resolver behavior can bypass negotiation. QOP overwrite mutates tokens and must only happen for DataNode downstream flows with a secret key. `doSaslHandshake` must preserve `InvalidEncryptionKeyException` and `InvalidBlockTokenException` for caller retry/refresh. Cipher-suite negotiation only sends options when privacy is requested. Fallback-to-simple-auth must not be accidentally enabled in secure clusters.

## Test Signals
`TestSaslDataTransfer` covers trust decisions and SASL negotiation; `TestEncryptedTransfer` covers encrypted handshakes and cipher options; `TestDataXceiverBackwardsCompat` covers handshake compatibility. Focused tests should cover every branch in `send`, token mutation in `updateToken`, handshake-secret presence/absence, invalid key/token error propagation, and AES/SM4 cipher negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslDataTransferClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslParticipant.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslParticipant.java

## Purpose
`SaslParticipant` abstracts over `SaslClient` and `SaslServer`, which have similar operations but no shared interface. It provides a single helper used by HDFS data transfer SASL client/server negotiation code.

## Important APIs, Types, and Functions
Static factory methods create server or client participants using `FastSaslServerFactory` or `FastSaslClientFactory`, mechanism from `SaslMechanismFactory`, protocol `hdfs`, and server name `0`. Factories are lazily initialized static fields.

`createFirstMessage` is client-only and returns the initial response or an empty byte array. `evaluateChallengeOrResponse` delegates to client `evaluateChallenge` or server `evaluateResponse`. `getNegotiatedQop`, `isNegotiatedQopPrivacy`, `wrap`, `unwrap`, and `isComplete` delegate to the active SASL object. `createStreamPair` wraps streams in Hadoop `SaslInputStream` and `SaslOutputStream`. `toString` identifies `SaslServer` or `SaslClient`.

## Control Flow
Each instance wraps exactly one of `SaslClient` or `SaslServer`; the other field is null. Methods branch on which side is active.

## State and Persistence Behavior
SASL negotiation state lives inside the wrapped `SaslClient` or `SaslServer`. Static factories are cached process-wide. There is no persistence.

## Dependencies and Integration Points
It depends on Java SASL APIs, Hadoop fast SASL factories, `SaslMechanismFactory`, Hadoop SASL streams, and `IOStreamPair`. It is used by `SaslDataTransferClient` and corresponding server-side SASL utilities.

## Risks and Edge Cases
Static factory initialization is not synchronized, though duplicate initialization is likely harmless. `Objects.requireNonNull` fails if a requested mechanism cannot create a client/server. `createFirstMessage` throws for server instances. Correct QOP privacy detection depends on negotiated property strings.

## Test Signals
SASL data transfer tests cover this indirectly. Focused tests with mock callback handlers should cover client/server creation, initial response handling, QOP reporting, wrap/unwrap after completion, and stream pair creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslParticipant.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslResponseWithNegotiatedCipherOption.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslResponseWithNegotiatedCipherOption.java

## Purpose
`SaslResponseWithNegotiatedCipherOption` is a small package-private response container for a SASL payload plus the cipher option negotiated by the server.

## Important APIs, Types, and Functions
The constructor stores a `byte[] payload` and a `CipherOption cipherOption`. Fields are final and package-visible.

## Control Flow
`DataTransferSaslUtil.readSaslMessageAndNegotiatedCipherOption` creates this object after parsing a server response. `SaslDataTransferClient.doSaslHandshake` evaluates the payload and unwraps/uses the cipher option if privacy was negotiated.

## State and Persistence Behavior
It is immutable by reference, though the payload byte array is mutable by callers. There is no persistence.

## Dependencies and Integration Points
It depends on Hadoop crypto `CipherOption` and the SASL utility/client classes in the same package.

## Risks and Edge Cases
Null cipher option is valid and means no separate crypto stream suite was negotiated; callers then fall back to SASL streams. Payload may be empty or null depending on protobuf response content.

## Test Signals
Encrypted transfer tests should assert negotiated and non-negotiated cipher option paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslResponseWithNegotiatedCipherOption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/package-info.java

## Purpose
`package-info.java` declares the `org.apache.hadoop.hdfs.protocol` package and carries the Apache license header. It does not define annotations or package-level documentation beyond the package declaration.

## Important APIs, Types, and Functions
There are no APIs, types, or functions in this file.

## Control Flow
No control flow.

## State and Persistence Behavior
No state or persistence behavior.

## Dependencies and Integration Points
The file participates only in Java package metadata for the HDFS client protocol package.

## Risks and Edge Cases
Low risk. If package-level annotations or docs are added later, generated Javadocs and package metadata can change.

## Test Signals
No direct tests are needed for the current content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ClientDatanodeProtocolPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ClientDatanodeProtocolPB.java

## Purpose
`ClientDatanodeProtocolPB` is the protobuf RPC interface used by clients to call DataNode administrative/local-block operations. It extends the generated blocking protobuf service and adds Hadoop security/protocol annotations.

## Important APIs, Types, and Functions
The interface extends `ClientDatanodeProtocolService.BlockingInterface`. `@KerberosInfo` points to the DataNode Kerberos principal key. `@TokenInfo` uses `BlockTokenSelector`. `@ProtocolInfo` names `org.apache.hadoop.hdfs.protocol.ClientDatanodeProtocol` and version `1`.

## Control Flow
No methods are implemented here; generated protobuf methods are inherited. RPC setup reads the annotations for security and protocol metadata.

## State and Persistence Behavior
There is no state. The protocol name/version and annotations are compatibility metadata.

## Dependencies and Integration Points
It depends on generated `ClientDatanodeProtocolProtos`, Hadoop RPC annotations, HDFS client config keys, and block token selector. It is used by `ClientDatanodeProtocolTranslatorPB`, server-side translators, and RPC engine setup.

## Risks and Edge Cases
Changing protocol name/version or token/Kerberos annotations can break RPC compatibility or authentication. Generated service method changes require matching translator updates.

## Test Signals
`TestIsMethodSupported` exercises method support through the translator. RPC/security integration tests should validate Kerberos and block token behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ClientDatanodeProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ClientDatanodeProtocolTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ClientDatanodeProtocolTranslatorPB.java

## Purpose
`ClientDatanodeProtocolTranslatorPB` adapts the public `ClientDatanodeProtocol` Java interface to the protobuf RPC interface `ClientDatanodeProtocolPB`. It builds request protobufs, invokes the RPC proxy, converts response protobufs back to client types, and manages proxy closure.

## Important APIs, Types, and Functions
Constructors create RPC proxies from a `DatanodeID` plus optional `LocatedBlock`, or from an explicit socket address and UGI. The `LocatedBlock` path creates a remote UGI named after the local block string, adds the block token, and sets IPC max idle time to zero to avoid connection reuse for one-off calls.

`createClientDatanodeProtocolProxy` configures `ProtobufRpcEngine2` and calls `RPC.getProxy`. `close` stops the proxy. `isMethodSupported` delegates to `RpcClientUtil.isMethodSupported`, and `getUnderlyingProxyObject` returns the raw proxy.

Translated operations include replica visible length, NameNode refresh, block pool deletion, local path info, DataNode shutdown, writer eviction, DataNode local info, reconfiguration start/status/list, block report trigger, balancer bandwidth, disk balancer plan submit/cancel/query/setting, and volume report. The class uses static empty request protos for no-argument calls and `ipc(...)` wrapper for protobuf RPC exception handling.

## Control Flow
Each protocol method builds a request proto, calls the matching `rpcProxy` method with a null controller, and converts the response when needed. Volume report iterates over `DatanodeVolumeInfoProto` records and constructs `DatanodeVolumeInfo` objects. Disk balancer query maps integer result ordinals back to `DiskBalancerWorkStatus.Result`.

## State and Persistence Behavior
The translator stores one RPC proxy. It does not persist state, but RPC calls mutate DataNode state for admin operations such as shutdown, refresh, reconfiguration, block pool deletion, disk balancer control, and block report triggering.

## Dependencies and Integration Points
It depends on generated ClientDatanode, Reconfiguration, and HDFS protos, `PBHelperClient`, Hadoop RPC classes, `NetUtils`, `UserGroupInformation`, block tokens, DataNode protocol model classes, and disk balancer status classes. It is used by DFS clients, tests, and admin tools needing direct DataNode RPCs.

## Risks and Edge Cases
Protocol conversion must stay aligned with generated protobuf schemas. The disk balancer result ordinal mapping can break if enum ordering changes. Proxy lifecycle matters because some constructors intentionally prevent idle reuse but still rely on `close`/`RPC.stopProxy`. Optional response fields are mapped to nulls. Admin operations require correct authentication/token setup.

## Test Signals
`TestIsMethodSupported` covers method support. DataNode admin, disk balancer, reconfiguration, and local block path tests cover translated calls. Focused tests should validate request fields, optional response handling, volume report conversion, disk balancer enum mapping, and proxy close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ClientDatanodeProtocolTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ClientNamenodeProtocolPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ClientNamenodeProtocolPB.java

## Purpose
`ClientNamenodeProtocolPB` is the protobuf RPC interface for client-to-NameNode operations. It extends the generated blocking protobuf service and adds Hadoop security and protocol metadata.

## Important APIs, Types, and Functions
The interface extends `ClientNamenodeProtocol.BlockingInterface` from generated protobufs. `@KerberosInfo` points to the NameNode Kerberos principal key. `@TokenInfo` uses `DelegationTokenSelector`. `@ProtocolInfo` uses `HdfsConstants.CLIENT_NAMENODE_PROTOCOL_NAME` and version `1`.

## Control Flow
No methods are implemented here. The RPC engine and translators use this interface and its annotations to configure protobuf RPC calls and authentication.

## State and Persistence Behavior
There is no runtime state. Protocol annotation values are compatibility and security metadata.

## Dependencies and Integration Points
It depends on generated `ClientNamenodeProtocolProtos`, `HdfsConstants`, HDFS config keys, Hadoop RPC annotations, and delegation token selection. It is used by client-side and router-side NameNode protocol translators and server-side translators.

## Risks and Edge Cases
Changing protocol name/version or security annotations can break clients or authentication. Generated protobuf service changes require translator and server-side updates. The Javadoc is placed after annotations but still documents the interface.

## Test Signals
Client protocol and method-support tests indirectly validate this interface. Security integration tests should cover Kerberos principal and delegation token selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ClientNamenodeProtocolPB.java -->
