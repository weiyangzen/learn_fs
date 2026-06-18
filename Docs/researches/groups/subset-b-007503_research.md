# subset-b-007503 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeFile.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeFile.java

## Purpose

`INodeFile` is the NameNode namespace object for HDFS files. It combines inode metadata from `INodeWithAdditionalFields` with file-specific block layout, block ownership, snapshot state, under-construction state, quota accounting, content-summary accounting, and block reclamation. It implements both `INodeFileAttributes` for snapshot metadata views and `BlockCollection` for integration with block management.

## Important APIs and Types

The nested `HeaderFormat` packs preferred block size, block layout/redundancy, and storage policy into a single `long`. It distinguishes contiguous replicated files from striped erasure-coded files by a layout bit and stores either replication or EC policy id in the remaining redundancy bits. Constructors validate that any existing `BlockInfo` entries match the file block type. Important mutators include `toUnderConstruction`, `toCompleteFile`, `setFileReplication`, `setStoragePolicyID`, `addBlock`, `concatBlocks`, `removeLastBlock`, `truncateBlocksTo`, and `clearFile`. Query APIs include `getBlocks`, `getBlocks(snapshot)`, `computeFileSize`, `storagespaceConsumed`, `computeQuotaUsage`, and `computeContentSummary`.

## Control Flow, State, and Persistence

The file's durable state is the inherited inode id/name/permission/times plus `header`, `blocks`, and optional features. Snapshot behavior is mediated by `FileWithSnapshotFeature` and `FileDiffList`: `recordModification` creates or updates file diffs before live metadata changes, `getSnapshotINode` retrieves historical attributes, and `getBlocks(snapshot)` can return block arrays saved during truncate. Under-construction behavior is stored as a `FileUnderConstructionFeature`; completion checks block UC states and, for committed last blocks, validates expected locations or striped internal block count. Destruction and subtree cleanup add quota deltas, collect deleted blocks, clear ACL/features, remove snapshot diffs, and remember removed under-construction file ids.

## Dependencies and Integration Points

This class sits at the intersection of namespace, snapshots, block management, erasure coding, storage policy, ACL/XAttr storage, and visitor traversal. It uses `BlockManager` when concatenating blocks to adjust replication, `BlockStoragePolicySuite` for storage-type quota, `ErasureCodingPolicyManager` for striped layout validation, and snapshot classes such as `FileDiff`, `FileDiffList`, and `Snapshot`.

## Risks and Test Signals

Risks concentrate around packed-header compatibility, replicated versus striped branch behavior, snapshot/truncate block retention, and quota deltas when blocks exist both in current state and snapshots. Important tests should cover header encoding for replication/EC/storage policy, completing UC files with committed last blocks, concat replication updates, delete/truncate with snapshots, EC storage policy suitability, storage-space accounting for incomplete striped blocks, and block retention when snapshots reference earlier arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeFileAttributes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeFileAttributes.java

## Purpose

`INodeFileAttributes` is the read-only attribute contract for file inodes and snapshot copies. It lets snapshot and edit/image code reason about file metadata without requiring a live mutable `INodeFile`.

## Important APIs and Types

The interface exposes replication, striped/contiguous block type, EC policy id, preferred block size, packed header, local storage policy id, and `metadataEquals`. The nested `SnapshotCopy` extends `INodeAttributes.SnapshotCopy` and stores only the packed file `header` in addition to inherited permission/timestamp/ACL/XAttr snapshot fields.

## Control Flow, State, and Persistence

`SnapshotCopy` builds the same packed header as `INodeFile` through `INodeFile.HeaderFormat`, preserving file layout information for FSImage/snapshot diffs. Its methods decode from the stored header and do not track live block arrays. For non-striped files, `getErasureCodingPolicyID` returns `-1`, while the live `INodeFile` returns the replication policy id constant; callers need to tolerate that distinction.

## Dependencies and Integration Points

The contract is consumed by snapshot diff code, FSImage serialization paths, and file metadata comparisons. It depends on `PermissionStatus`, `BlockType`, `AclFeature`, `XAttrFeature`, and the `HeaderFormat` logic in `INodeFile`.

## Risks and Test Signals

The main risk is divergence between live inode header semantics and snapshot-copy header semantics. Tests should compare live and snapshot metadata equality, verify header round-trips for replicated and striped files, and ensure storage policy and ACL/XAttr references are preserved or intentionally shared as expected by snapshot code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeFileAttributes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeId.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeId.java

## Purpose

`INodeId` is the NameNode's sequential allocator for globally unique inode ids. It reserves a low range for compatibility/future use and defines the root inode id.

## Important APIs and Types

The class extends `SequentialNumber` and defines `LAST_RESERVED_ID` as `1 << 14`, `ROOT_INODE_ID` as `16385`, and `INVALID_INODE_ID` as `-1`. Its package-private constructor starts the sequence at the root id.

## Control Flow, State, and Persistence

Allocation behavior comes from `SequentialNumber`; this class only fixes constants and the starting value. The ids are persistent namespace identifiers used in FSImage, edit logs, block-collection ids, leases, and inode maps. They are intentionally not recycled.

## Dependencies and Integration Points

It integrates with all inode creation paths, `INodeMap` lookup, lease tracking by inode id, and block collection ownership. Compatibility with id `0` is noted in the class comment.

## Risks and Test Signals

Risk is low but compatibility-sensitive. Tests should verify root id stability, reserved-id boundaries, monotonic allocation across image load/save, and rejection or special handling of invalid ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeId.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeMap.java

## Purpose

`INodeMap` stores the global mapping from inode id to in-memory inode object. It is a lightweight id index used by the NameNode for fast lookups independent of path traversal.

## Important APIs and Types

`newInstance` creates a `LightWeightGSet` sized from one percent of memory and inserts the root directory. `put` indexes only `INodeWithAdditionalFields`, `remove` deletes by inode, `get` resolves an id, `getMapIterator` exposes iteration, `size` returns count, and `clear` empties the map.

## Control Flow, State, and Persistence

The map is explicitly synchronized by an external lock; methods themselves are not synchronized. Lookup constructs a temporary anonymous `INodeWithAdditionalFields` with the target id and stub behavior so `GSet` equality/hash semantics can locate the real entry. The map is memory-resident and rebuilt from namespace/image state.

## Dependencies and Integration Points

It depends on `LightWeightGSet`, `GSet`, inode equality, root `INodeDirectory`, permissions for the temporary lookup key, and `BlockStoragePolicySuite` stubs. It is used by `FSDirectory` and systems that resolve inode ids, including leases and block ownership checks.

## Risks and Test Signals

Risks include external-lock misuse, id equality regressions, and stale map entries during deletion or snapshot cleanup. Tests should cover insert/replace/remove/get behavior, root insertion, iteration during namespace scans, and lookup of missing ids without side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeReference.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeReference.java

## Purpose

`INodeReference` implements the reference objects that let one inode have multiple access paths after snapshot-aware renames. It preserves historical source names and destination paths while ensuring the underlying file or directory is reclaimed only when all snapshot and current references are gone.

## Important APIs and Types

The abstract base delegates most inode operations to `referred`. Static helpers remove references and compute the prior snapshot for cleanup. `WithCount` owns the real referred inode and tracks all `WithName` references plus the optional current-parent `DstReference`. `WithName` stores an immutable historical name and `lastSnapshotId`. `DstReference` stores `dstSnapshotId`, the latest destination snapshot before rename.

## Control Flow, State, and Persistence

A rename involving snapshots creates a `WithCount`, one or more source-side `WithName` references, and a destination-side `DstReference`. Quota/content-summary calls on `WithName` compute against the snapshot timeline rather than current cached quota. Cleanup has careful branches: `WithName.cleanSubtree` may restore quota deltas when deleting older snapshots, while `DstReference.destroyAndCollectBlocks` removes the destination link and either destroys the referred subtree or cleans content created after the prior source snapshot. `removeReference` updates reference counts and only destroys blocks when the count reaches zero.

## Dependencies and Integration Points

This class is tightly coupled to snapshot diff logic in `DirectoryWithSnapshotFeature`, `FileWithSnapshotFeature`, `FileDiffList`, `Snapshot`, and `ReclaimContext`. It also integrates with permission/ACL/XAttr delegation, quota accounting, visitor traversal, debug tree dumps, and `INodeReferenceValidation`.

## Risks and Test Signals

This is high-risk namespace code. Bugs can leak blocks, double-count quota, expose wrong snapshot paths, or delete live data. Tests should cover repeated renames across one or more snapshottable directories, rename within the same snapshottable subtree, snapshot deletion ordering, reference count changes, quota updates along source and destination ancestors, and validation failures for broken `WithCount`/`WithName`/`DstReference` links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeReference.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeReferenceValidation.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeReferenceValidation.java

## Purpose

`INodeReferenceValidation` is an optional validation harness for checking `INodeReference` graph consistency, mainly during FSImage validation or diagnostic runs.

## Important APIs and Types

Static `start` installs a singleton collector, `add` and `remove` track reference objects by class, and `end` drains validation and reports added errors. `ReferenceSet` stores references of one subclass and submits batched `Task` instances. Each `Task` calls `ref.assertReferences()` for up to `100_000` references.

## Control Flow, State, and Persistence

When validation is enabled, constructors and removal paths in `INodeReference` subclasses register or unregister objects. At `end`, the validator creates a fixed thread pool sized to available processors, periodically logs progress with a `Timer`, submits tasks for `DstReference`, `WithCount`, and `WithName`, and increments the shared error count for assertion failures. It is transient only; no namespace state is persisted.

## Dependencies and Integration Points

It depends on `FsImageValidation.Cli` helpers for output and error formatting, `FsImageValidation.Util` for counts, Java executors/futures/timer, and the `assertReferences` methods implemented by each reference subclass.

## Risks and Test Signals

Risks include memory growth when validating very large images, task partitioning behavior caused by removing from iterators while batching, and validation only running when `start` is active. Tests should cover registration/removal identity semantics, task batching, progress completion, and injected malformed reference graphs that increment the error counter rather than aborting the whole validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeReferenceValidation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeSymlink.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeSymlink.java

## Purpose

`INodeSymlink` is the namespace inode for symbolic links. It stores a symlink target and participates in namespace counts, snapshots, content summaries, and visitor traversal without owning blocks.

## Important APIs and Types

The constructor stores the target as DFS byte encoding. `recordModification` snapshots the symlink through the parent directory, `getSymlinkString` and `getSymlink` expose the target, and `computeQuotaUsage` counts one namespace entry. ACL, XAttr, and storage policy operations throw `UnsupportedOperationException`.

## Control Flow, State, and Persistence

The persistent state is inherited inode metadata plus the immutable target byte array. Snapshot recording saves a copy into the parent snapshot diff when the symlink is in the latest snapshot. Deletion from current state with no prior snapshot removes the inode and adds a namespace quota delta. Content summary increments `Content.SYMLINK`.

## Dependencies and Integration Points

It integrates with `DFSUtil` byte/string conversion, `INodeDirectory.saveChild2Snapshot`, `Snapshot`, `QuotaCounts`, `ContentSummaryComputationContext`, and namespace visitors.

## Risks and Test Signals

Risks are around unsupported feature calls and snapshot preservation of immutable target bytes. Tests should cover symlink creation, snapshot then delete, content summary counts, quota counts, dump output, and explicit rejection of ACL/XAttr/storage policy operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeSymlink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeWithAdditionalFields.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeWithAdditionalFields.java

## Purpose

`INodeWithAdditionalFields` is the common mutable base for inodes with durable ids, local names, packed permissions, modification/access times, linked-set membership, and optional feature arrays.

## Important APIs and Types

`PermissionStatusFormat` packs mode, group serial number, and user serial number into a `long`; it also reconstructs `PermissionStatus` from a string table. The class implements `LightWeightGSet.LinkedElement` via `next`, exposes getters/setters for id/name/permission/times, and manages feature arrays through `addFeature`, `removeFeature`, and `getFeature`. ACL features are interned through `AclStorage`, and XAttr features are attached directly.

## Control Flow, State, and Persistence

The packed permission format is explicitly used in-memory and on-disk, so bit layout changes are incompatible. Snapshot-aware getters delegate to `getSnapshotINode(snapshotId)` when reading historical user/group/mode/times/ACL/XAttr. Feature mutation copies the feature array on add/remove; duplicates are rejected for ACL and XAttr. Copy construction preserves parent or parent reference and clones primitive fields but shares name bytes and feature array references according to existing inode-copy semantics.

## Dependencies and Integration Points

This base supports `INodeFile`, `INodeDirectory`, `INodeSymlink`, and temporary lookup keys in `INodeMap`. It depends on `SerialNumberManager`, `LongBitFormat`, `AclStorage`, `Snapshot`, and Hadoop permission types.

## Risks and Test Signals

Risks include on-disk incompatibility from packed format changes, duplicate/missing feature errors, snapshot getters returning live state accidentally, and shared feature-array semantics during copies. Tests should cover permission packing/unpacking with string tables, ACL feature interning/removal, XAttr addition/removal, timestamp snapshot reads, and `LinkedElement` behavior in `LightWeightGSet`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeWithAdditionalFields.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodesInPath.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodesInPath.java

## Purpose

`INodesInPath` represents the resolved inode chain for a path, including unresolved tail components, snapshot path state, latest snapshot ids for mutation recording, and raw-path status.

## Important APIs and Types

Key factories are `resolve`, `fromINode`, `fromINode(rootDir, inode)`, and `fromComponents`. Structural helpers include `replace`, `append`, `getExistingINodes`, `getParentINodesInPath`, `isDescendant`, and path/inode accessors. Snapshot-specific methods distinguish `getLatestSnapshotId` for non-snapshot paths from `getPathSnapshotId` for paths inside `.snapshot`.

## Control Flow, State, and Persistence

`resolve` walks components from a starting directory, records each inode, tracks whether it has entered a snapshot path, updates latest snapshot id while traversing snapshotted directories, and applies special reference-node rules using `DstReference` snapshot ids. When encountering `.snapshot/<name>`, it resolves the snapshot root and collapses the two path components into one so path components and inode array remain one-to-one for reconstruction. The object is immutable except for cached `pathname`.

## Dependencies and Integration Points

It depends on `DFSUtil`, `HdfsConstants.DOT_SNAPSHOT_DIR`, `HdfsServerConstants`, `INodeDirectory`, `DirectoryWithSnapshotFeature`, `Snapshot`, and `INodeReference`. It is used broadly by FSDirectory operations, lease handling, snapshot creation, deletion, and mutation paths needing the correct latest snapshot id.

## Risks and Test Signals

Risks include off-by-one component collapse, incorrect latest snapshot id when traversing references, raw path flag loss during replace/append, and invalid parent validation for snapshot roots. Tests should cover missing components, `.snapshot` as final component, nonexistent snapshot names, paths under snapshot roots, rename references with dst snapshots, `fromINode` for leased files, and descendant checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodesInPath.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/IllegalReservedPathException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/IllegalReservedPathException.java

## Purpose

`IllegalReservedPathException` signals that an FSImage contains a reserved path name when upgrading from software that did not reserve those names to software that does.

## Important APIs and Types

The class is a private `IOException` subclass with constructors for message-only and message-with-cause forms.

## Control Flow, State, and Persistence

It carries no state beyond the exception message and optional cause. Its significance is in upgrade/load control flow: throwing it blocks unsafe namespace loading when reserved path invariants would be violated.

## Dependencies and Integration Points

It integrates with FSImage upgrade and reserved path validation code. Callers can handle it as an `IOException` while preserving a more specific reason for diagnostics.

## Risks and Test Signals

Risks are mostly diagnostic. Tests should cover image load or upgrade paths with illegal reserved names and ensure the specific exception and message make the offending condition clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/IllegalReservedPathException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ImageServlet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ImageServlet.java

## Purpose

`ImageServlet` is the NameNode HTTP endpoint for transferring FSImage, edit-log files, and alias map data. It supports checkpoint download by Secondary/Standby NameNodes and checkpoint upload back to active or observer NameNodes.

## Important APIs and Types

`doGet` serves latest or requested image files, finalized edit logs, or alias map bootstrap data. `doPut` receives checkpoint images. Helpers build query strings, set filename and verification headers, configure throttlers, validate requestors, and parse parameters through `GetImageParams` and `PutImageParams`. `ImageUploadRequest` orders concurrent uploads by txid and remote address.

## Control Flow, State, and Persistence

Before serving or accepting data, the servlet obtains `FSImage` from the servlet context, validates initialization, checks Kerberos/admin authorization when security is enabled, and compares storage-info strings. GET opens the target file, sets content length and stored MD5 headers, then copies bytes with configured throttling. PUT checks HA state, suppresses older or duplicate concurrent checkpoint uploads using a synchronized sorted set, rejects too-frequent ordinary image uploads based on checkpoint period and txn thresholds, streams the upload into checkpoint storage, saves the digest, renames the checkpoint image, purges old storage, and removes checkpointing state in `finally`.

## Dependencies and Integration Points

It integrates with Jetty servlets, `NameNodeHttpServer`, `FSImage`, `NNStorage`, `TransferFsImage`, `MD5FileUtils`, `NameNodeMetrics`, `HAServiceProtocol`, `InMemoryAliasMap`, `HttpServer2` admin checks, Kerberos principals for NameNode/Secondary/other HA NameNodes, and DFS image-transfer configuration keys.

## Risks and Test Signals

Risks include authorization gaps, storage-info mismatch handling, races where files disappear after headers, duplicate upload ordering, checkpoint rejection thresholds with clock skew, large-file length handling through `Util.FILE_LENGTH`, and response code distinctions for wrong HA target versus conflict. Tests should cover secure and insecure request validation, latest and txid image GET, edit-log GET, alias-map GET, PUT duplicate conflicts, recent-image rejection override, MD5/content-length headers, throttling config, and cleanup of `currentlyDownloadingCheckpoints` on errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ImageServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/InotifyFSEditLogOpTranslator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/InotifyFSEditLogOpTranslator.java

## Purpose

`InotifyFSEditLogOpTranslator` converts NameNode edit-log operations into public HDFS inotify `EventBatch` objects.

## Important APIs and Types

The static `translate(FSEditLogOp op)` switch handles create/append/close, replication changes, concat/delete, old and new rename operations, delete, mkdir, permission/owner/time updates, symlink creation, XAttr add/remove, ACL changes, and truncate. `getSize` sums block sizes for close events.

## Control Flow, State, and Persistence

The translator is stateless. For `OP_ADD`, it treats zero blocks as file creation and nonzero blocks as append. Some edit operations produce multiple events: concat emits append for target, unlink for each source, and close for target. Unsupported opcodes return `null`, meaning no inotify event is emitted. Event batches preserve the edit transaction id.

## Dependencies and Integration Points

It depends on `FSEditLogOp` subclasses, `org.apache.hadoop.hdfs.inotify.Event`, block sizes, permissions, ACL/XAttr payloads, and `ErasureCodeConstants.REPLICATION_POLICY_ID` to mark created files as erasure-coded.

## Risks and Test Signals

Risks include incomplete opcode coverage, semantic mismatch between edit-log fields and user-visible inotify events, and create-versus-append inference from block array length. Tests should feed representative edit ops, verify event ordering and txids, cover concat multi-event output, EC create flags, ACL/XAttr removed flags, and ensure unsupported operations are intentionally silent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/InotifyFSEditLogOpTranslator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/IsNameNodeActiveServlet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/IsNameNodeActiveServlet.java

## Purpose

`IsNameNodeActiveServlet` is a small load-balancer health endpoint that reports whether the NameNode in the servlet context is active.

## Important APIs and Types

It extends `org.apache.hadoop.http.IsActiveServlet` and overrides `isActive()` to fetch the `NameNode` from `NameNodeHttpServer` context and call `namenode.isActiveState()`.

## Control Flow, State, and Persistence

The servlet has no local state and no persistence. Each request follows the base servlet behavior, with this class supplying the active-state predicate.

## Dependencies and Integration Points

It integrates with the NameNode HTTP server context, HA state handling in `NameNode`, and external load balancers or monitoring systems that need active-only routing.

## Risks and Test Signals

Risks are null context or stale HA state exposure. Tests should cover active, standby/observer, and missing-context behavior through servlet tests or NameNode HTTP integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/IsNameNodeActiveServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/JournalManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/JournalManager.java

## Purpose

`JournalManager` is the abstraction for one logical edit-log storage target, such as a local file journal, shared edits, or backup-node journal.

## Important APIs and Types

The interface combines `Closeable`, `Storage.FormatConfirmable`, and `LogsPurgeable`. It defines formatting, starting and finalizing log segments, output buffer sizing, unfinalized segment recovery, upgrade/finalize/rollback/discard operations, journal ctime lookup, and close. `CorruptionException` represents gaps or corrupt edit files that make a transaction range unusable.

## Control Flow, State, and Persistence

Implementations own the persistent edit-log state. `startLogSegment` begins writing a segment at a txid and layout version; `finalizeLogSegment` marks the txid range complete; recovery resolves in-progress segments after crashes. Upgrade methods coordinate all journal stores before NameNode metadata version transitions.

## Dependencies and Integration Points

It is consumed by `FSEditLog` and `JournalSet`, and implemented by concrete journal managers such as `FileJournalManager` or quorum/shared journal managers. It uses `NamespaceInfo`, `Storage`, and `StorageInfo` to align edit logs with namespace metadata.

## Risks and Test Signals

Risks include transaction gaps, partial segment finalization, upgrade inconsistency across journals, rollback availability mismatches, and buffer sizing not applied consistently. Tests should exercise segment lifecycle, crash recovery, purge/select behavior through `LogsPurgeable`, upgrade failure rollback behavior, and corruption exception handling during edit loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/JournalManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/JournalSet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/JournalSet.java

## Purpose

`JournalSet` is the fan-out `JournalManager` used by `FSEditLog` to write, flush, finalize, recover, and read across multiple underlying journals while enforcing required and redundant resource policy.

## Important APIs and Types

`JournalAndStream` pairs a `JournalManager` with its active `EditLogOutputStream`, disabled state, and required/shared flags. `startLogSegment` returns a `JournalSetOutputStream` that writes to all active streams. `selectInputStreams` gathers candidate edit streams and `chainAndMakeRedundantStreams` groups streams with the same start txid into `RedundantEditLogInputStream`s, preferring local logs. Other APIs add/remove journals, purge old logs, recover unfinalized segments, expose edit-log manifests, and report sync times.

## Control Flow, State, and Persistence

Write-side operations are applied through `mapJournalsAndReportErrors`. Non-required journal failures abort and disable that journal; required journal failure aborts all active journals and terminates the NameNode. After errors, `NameNodeResourcePolicy` verifies that enough resources remain. `JournalSetOutputStream.write` propagates each edit op and updates `lastJournalledTxId` after asserting increasing txids. Read-side stream selection skips disabled journals, tolerates per-journal listing failures, groups redundant alternatives, and discards earlier manifest output when gaps are found.

## Dependencies and Integration Points

It integrates with `FSEditLog`, `EditLogInputStream`, `EditLogOutputStream`, `RedundantEditLogInputStream`, `FileJournalManager`, `RemoteEditLogManifest`, `NameNodeResourcePolicy`, and `ExitUtil.terminate`. The `CopyOnWriteArrayList` allows web UI or diagnostics to iterate journal streams while rare mutations occur.

## Risks and Test Signals

Risks include disabling too many journals, required journal termination behavior, inconsistent `lastJournalledTxId`, choosing in-progress over finalized logs, gaps in manifests, and unsupported interface methods accidentally called on the set instead of individual managers. Tests should cover partial write/flush failures, required journal failure exit policy, resource thresholds, redundant stream ordering/local preference, finalized versus in-progress grouping, manifest gap handling, add/remove journal behavior, and purge/recovery fan-out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/JournalSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LeaseExpiredException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LeaseExpiredException.java

## Purpose

`LeaseExpiredException` indicates that the lease used to create or write a file has expired and can no longer authorize the requested operation.

## Important APIs and Types

It is an evolving private `IOException` subclass with a single message constructor.

## Control Flow, State, and Persistence

The exception has no extra state. It participates in file create/write/append/recovery control flow by distinguishing lease expiry from generic I/O failure.

## Dependencies and Integration Points

It integrates with lease checking in NameNode write paths, `LeaseManager`, client error propagation, and retry/recovery behavior.

## Risks and Test Signals

Risks are mainly caller handling. Tests should verify expired hard-limit leases produce this exception where expected, active leases do not, and clients transition to lease recovery or fail with useful diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LeaseExpiredException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LeaseManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LeaseManager.java

## Purpose

`LeaseManager` tracks write leases for under-construction files and drives lease recovery when clients stop renewing. It also lists open files and supports snapshot creation paths that need leased inode resolution.

## Important APIs and Types

State is held in `leases` from holder string to `Lease` and `leasesById` from inode id to `Lease`. Public/package APIs add, remove, reassign, and renew leases; count leases and paths; list under-construction files; collect leased `INodesInPath`; set lease periods; and start/stop or trigger the monitor. The nested `Lease` stores holder, last update time, and inode ids. The nested `Monitor` periodically checks hard-expired leases.

## Control Flow, State, and Persistence

Lease operations are synchronized, while namespace operations require external FSNamesystem locks. The monitor sleeps for the configured recheck interval, prefilters hard-expired leases without the FS lock, then takes the global write lock and calls `checkLeases` outside safe mode. `checkLeases` copies inode ids before iteration, resolves each inode to `INodesInPath`, removes deleted or invalid entries, and invokes `FSNamesystem.internalReleaseLease` with a rotating internal lease holder. It limits lock hold time and syncs the edit log if block recovery was started. Open-file listing uses inode id as a cursor and returns a non-consistent batched view.

## Dependencies and Integration Points

It depends on `FSNamesystem`, `FSDirectory`, `INodeFile`, `INodesInPath`, `BlockInfo`, `OpenFileEntry`, `BatchedListEntries`, DFS lease configuration keys, NameNode locking modes, edit-log syncing, and DataNode block recovery initiated through `internalReleaseLease`.

## Risks and Test Signals

Risks include races with deleted files, lock-order mistakes, stale lease indexes, long write-lock holds during mass expiry, non-consistent open-file pagination, and false leases on non-UC files. Tests should cover add/renew/remove/reassign consistency across both maps, expired hard-limit recovery, deleted inode cleanup, internal lease holder rotation, max lock-hold break behavior, open-file batching/filtering, parallel leased-path collection, safe-mode monitor behavior, and edit-log sync when recovery starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LeaseManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LogsPurgeable.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LogsPurgeable.java

## Purpose

`LogsPurgeable` abstracts edit-log stores that can purge old transactions and expose input streams for replay.

## Important APIs and Types

`purgeLogsOlderThan` removes edit logs below a minimum transaction id. `selectInputStreams` returns streams starting with the segment containing `fromTxId` and continuing forward, with flags for in-progress streams and durable transaction bounding.

## Control Flow, State, and Persistence

The interface does not implement behavior; concrete journal managers define persistence semantics. The `onlyDurableTxns` parameter is important for QJM committed txids and file journals' largest written txids.

## Dependencies and Integration Points

It is extended by `JournalManager` and consumed by `JournalSet`, `FSEditLog`, checkpointers, and edit-log loading code.

## Risks and Test Signals

Risks include purging needed recovery logs, returning streams with gaps, and mishandling in-progress or non-durable tails. Tests should cover purge boundaries, stream selection from the middle of a segment, in-progress inclusion/exclusion, durable truncation, and behavior when storage is inaccessible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/LogsPurgeable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/MetaRecoveryContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/MetaRecoveryContext.java

## Purpose

`MetaRecoveryContext` holds operator-interaction state during NameNode metadata recovery, especially edit-log loading when corruption or unexpected records require a decision.

## Important APIs and Types

Force modes are `FORCE_NONE`, `FORCE_FIRST_CHOICE`, and `FORCE_ALL`. `ask` prints a prompt and reads a single-line response unless force mode chooses the first option automatically. `editLogLoaderPrompt` logs an error and offers continue, stop, quit, or always-choose-first behavior. `RequestStopException` signals a deliberate stop while preserving earlier edits.

## Control Flow, State, and Persistence

When no recovery context is supplied, `editLogLoaderPrompt` turns the condition into an `IOException`. With context, it asks the user what to do. Continue returns, stop throws `RequestStopException`, quit calls `System.exit(0)`, and always sets force to `FORCE_FIRST_CHOICE`. The only mutable state is the force mode; it is not persisted.

## Dependencies and Integration Points

It integrates with edit-log loader recovery paths, standard input/output/error, SLF4J logging, and operator-driven NameNode recovery commands.

## Risks and Test Signals

Risks include blocking on stdin in noninteractive environments, `System.exit` during tests/tools, and force mode choosing an unsafe default. Tests should cover each prompt response, null recovery behavior, force-mode auto-selection, stop exception propagation, and recovery commands that run with noninteractive flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/MetaRecoveryContext.java -->
