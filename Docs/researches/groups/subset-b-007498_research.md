# Research: subset-b-007498

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLogOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLogOp.java

## Purpose

`FSEditLogOp` is the edit-log record model for HDFS NameNode namespace mutations. It defines the abstract base operation, one nested payload class for each persistent edit opcode, binary serialization/deserialization, XML import/export support for offline tooling, transaction ID/RPC retry-cache metadata, and three reader implementations for different edit-log layout eras. Together with `FSEditLogOpCodes`, this file is the durable contract between active NameNodes, standby NameNodes, JournalNodes, offline edits tools, and future software versions reading older edits.

The file is intentionally broad because it centralizes the on-disk schema for namespace operations: file create/close/append/block updates, permissions and owner changes, quota changes, rename/delete/mkdir/symlink/truncate, leases, delegation tokens, log segment markers, snapshots, cache directives and pools, ACLs, xattrs, storage policies, rolling-upgrade markers, and erasure-coding policy operations.

## Important APIs, Types, and Functions

The outer `FSEditLogOp` stores `opCode`, `txid`, `rpcClientId`, and `rpcCallId`. `getTransactionId`, `setTransactionId`, `hasRpcIds`, `getClientId`, and `getCallId` expose durable transaction/retry-cache metadata. `reset()` restores common fields and delegates to `resetSubFields()` so cached op instances can be reused safely.

`OpInstanceCache` keeps a thread-local `EnumMap<FSEditLogOpCodes,FSEditLogOp>` and instantiates nested operation classes by reflection from `FSEditLogOpCodes.getOpClass()`. This reduces allocation in hot edit-log read/write paths but makes complete field reset critical. `disableCache()` forces new instances, useful for callers that cannot tolerate object reuse.

Each nested operation implements `readFields(DataInputStream,int)`, `writeFields(DataOutputStream)` or the log-version-aware overload, `toXml(ContentHandler)`, and `fromXml(Stanza)`. Important operation families include:

- `AddCloseOp`, `AddOp`, `CloseOp`, `AppendOp`, `AddBlockOp`, and `UpdateBlocksOp` for file creation, close, append, and block-list mutation. `BlockListUpdatingOp` exposes path, blocks, and whether replay should complete the last block.
- `SetReplicationOp`, `SetPermissionsOp`, `SetOwnerOp`, `SetQuotaOp`, `SetQuotaByStorageTypeOp`, `TimesOp`, and `SetStoragePolicyOp` for metadata-only updates.
- `ConcatDeleteOp`, `RenameOldOp`, `RenameOp`, `DeleteOp`, `MkdirOp`, `SymlinkOp`, `TruncateOp`, and `ReassignLeaseOp` for namespace shape and lease changes.
- Token/key operations: `GetDelegationTokenOp`, `RenewDelegationTokenOp`, `CancelDelegationTokenOp`, and `UpdateMasterKeyOp`.
- Segment operations: `StartLogSegmentOp`, `EndLogSegmentOp`, and `InvalidOp`.
- Snapshot operations: `CreateSnapshotOp`, `DeleteSnapshotOp`, `RenameSnapshotOp`, `AllowSnapshotOp`, and `DisallowSnapshotOp`.
- Cache operations: `AddCacheDirectiveInfoOp`, `ModifyCacheDirectiveInfoOp`, `RemoveCacheDirectiveInfoOp`, `AddCachePoolOp`, `ModifyCachePoolOp`, and `RemoveCachePoolOp`.
- ACL/xattr operations: `SetAclOp`, `SetXAttrOp`, and `RemoveXAttrOp`.
- Erasure-coding operations: `AddErasureCodingPolicyOp`, `EnableErasureCodingPolicyOp`, `DisableErasureCodingPolicyOp`, and `RemoveErasureCodingPolicyOp`.
- `RollingUpgradeStartOp` and `RollingUpgradeFinalizeOp` persist rolling-upgrade lifecycle timestamps.

`AclEditLogUtil` packs ACL entries into a compact integer bit layout for binary edit logs. XAttrs and several newer structures use protobuf-delimited records through `XAttrEditLogProto`, `AclEditLogProto`, and `FSImageSerialization` helpers. XML helpers at the bottom convert blocks, delegation tokens, delegation keys, permission status, ACL entries, and xattrs for offline edit viewers and XML round trips.

`Writer.writeOp()` writes modern length-prefixed records: opcode byte, placeholder length, txid, op body, backfilled length, and CRC32 checksum. `Reader.create()` selects `LengthPrefixedReader`, `ChecksummedReader`, or `LegacyReader` from the log layout version. `Reader.readOp(skipBrokenEdits)` can scan forward one byte at a time in recovery mode after decode failures. `Reader.scanOp()` supports fast txid scanning where possible.

## Control Flow

On write, callers obtain a typed op from `OpInstanceCache`, populate fields with fluent setters, assign txid/RPC IDs in the surrounding edit-log layer, and call `Writer.writeOp(op, logVersion)`. `Writer` serializes a frame around `op.writeFields(...)`, computes CRC32 over the opcode/length/txid/body bytes, and appends the checksum.

On read, `Reader.create()` chooses the reader format. `LengthPrefixedReader.decodeOpFrame()` sets a stream limit, reads opcode and length, rejects oversized or undersized frames before allocating op payloads, reads txid, recomputes checksum over the complete frame excluding the checksum field, and returns the txid. `decodeOp()` then resets to the frame start, resolves the opcode to a cached op instance, assigns txid, skips length and txid fields, reads the op-specific payload, and skips the already-validated checksum. Older readers either validate checksum without a length prefix or fully decode legacy records, including layouts without stored txids.

`OP_INVALID` is the terminator. `verifyTerminator()` requires remaining bytes to be all `0x00` or `0xff`; this avoids silently treating a stray invalid byte as a clean end-of-log in the middle of useful data.

The op payload read/write methods are heavily version-gated by `NameNodeLayoutVersion.supports(...)`. Older layouts read numeric values as strings, omit inode IDs, omit retry-cache IDs, omit xattrs/ACLs/storage policies/erasure-coding fields, or use deprecated quota ops. Newer layouts write compact binary numeric values, protobuf sections, and additional fields. This version branching is part of the persistence contract and is the main reason fields are not factored into independent serializers.

## State and Persistence Behavior

The durable state is the ordered sequence of edit-log frames. Each record's byte opcode comes from `FSEditLogOpCodes`, txid establishes replay order, and payload fields are operation-specific namespace deltas. Some operations also persist RPC client/call IDs when the layout supports `EDITLOG_SUPPORT_RETRYCACHE`; replay can use them to preserve at-most-once semantics for retried client requests.

Several write methods defensively copy mutable block arrays (`deepCopy`, `setBlocks`, `setLastBlock`, `setTruncateBlock`) so later namespace mutations do not corrupt queued edit records. Maximum counts (`MAX_BLOCKS`, `MAX_CONCAT_SRC`) protect read paths from malformed data causing unbounded allocation. The length-prefixed reader's `maxOpSize` limit is another safety barrier for NameNode and JournalNode startup.

The XML path is a second persistence/interchange format for offline tools rather than the primary NameNode recovery format. It must still preserve txid and op payloads well enough for offline edit viewing and tests that construct edits from XML.

## Dependencies and Integration Points

This class depends on HDFS protocol and namespace types: `Block`, `CacheDirectiveInfo`, `CachePoolInfo`, `ErasureCodingPolicy`, `ECSchema`, `StorageType`, `FsPermission`, `PermissionStatus`, `AclEntry`, `XAttr`, delegation-token classes, `ClientProtocol` annotations in comments, layout feature gates, and `FSImageSerialization`. It uses Hadoop IO wrappers (`ArrayWritable`, `BytesWritable`, `Writable`, `DataOutputBuffer`), protobuf helpers (`PBHelperClient`), SAX/XML utilities, and CRC32 via `DataChecksum`.

Major consumers include `FSEditLog` and journal output streams for writing, `FSEditLogLoader` and `EditLogInputStream` for replay, JournalNode scan/cache paths such as `JournaledEditsCache`, NameNode bootstrap/upgrade code that copies or scans edit streams, and offline edits viewer classes under `org.apache.hadoop.hdfs.tools.offlineEditsViewer`.

`FSEditLogOpCodes` is tightly coupled: every active opcode with an op class must instantiate correctly in `OpInstanceCache`, and every binary/XML serializer must stay in sync with the assigned byte code.

## Risks

Durable compatibility is the core risk. Changing opcode byte values, reordering fields, removing version gates, or writing fields under the wrong layout feature can make existing clusters unable to replay edits. Missing `resetSubFields()` coverage in any cached op can leak data between records. Adding a new op requires coordinated changes in `FSEditLogOpCodes`, the nested op class, binary and XML read/write paths, replay in `FSEditLogLoader`, offline edits viewer handling, and inotify translation if relevant.

Resource exhaustion is another risk. Any variable-length read must keep bounds checks similar to `MAX_BLOCKS`, `MAX_CONCAT_SRC`, length-prefixed `maxOpSize`, and protobuf parser assumptions. Checksum or terminator verification changes can either reject valid old logs or silently accept corruption. Retry-cache metadata must be written only when supported by the layout; otherwise old readers can misalign.

XML conversion has separate drift risk because it is hand-maintained alongside binary serialization. Fields such as erasure-coding extra options, ACL entries, xattr values, and snapshot mtimes need round-trip tests when changed.

## Test Signals

Relevant local tests and usage signals include `TestEditsDoubleBuffer` for writing representative ops through edit buffers, `TestFileJournalManager` for reading edit streams and last-op behavior, `TestOfflineEditsViewer` for opcode coverage and XML/offline rendering, `TestDFSInotifyEventInputStream` for the expected opcode count and inotify translation coverage, `TestFileAppendRestart` for `OP_ADD`, `OP_APPEND`, `OP_ADD_BLOCK`, `OP_UPDATE_BLOCKS`, and `OP_CLOSE` sequences across restart, and `DFSTestUtil` helpers that generate erasure-coding policy edit records. `TestEditLogRace` exercises concurrent edit-log/saveNamespace behavior with concrete `FSEditLogOp` instances. Good additional validation for edits changes is a create/append/delete/rename/checkpoint/restart cycle plus offline edits viewer parsing of the generated logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLogOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLogOpCodes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLogOpCodes.java

## Purpose

`FSEditLogOpCodes` is the stable byte-code registry for HDFS edit-log records. Each enum constant maps a one-byte value from the edits file to the nested `FSEditLogOp` subclass that knows how to read, write, and render that operation. The enum is part of the on-disk wire format: byte values are historical compatibility commitments, not local implementation details.

## Important APIs, Types, and Functions

Each enum value stores `opCode` and optionally `opClass`. `getOpCode()` returns the durable byte value. `getOpClass()` returns the `FSEditLogOp` nested class used by `FSEditLogOp.OpInstanceCache` to create reusable operation instances.

The enum covers current and legacy operations from `OP_ADD` byte `0` through erasure-coding operations at bytes `49` to `52`, plus `OP_INVALID` at byte `-1`. Deprecated or obsolete entries remain present, including datanode add/remove and namespace quota variants, because old edit logs may still contain them or tooling may need to recognize them.

The static `VALUES` array is built once from the maximum non-negative byte code. `fromByte(byte opCode)` returns the enum for non-negative values inside the array, `OP_INVALID` for `-1`, and `null` for unknown bytes. This is the fast path used by edit-log readers for every record.

## Control Flow

During `FSEditLogOp.Reader.decodeOp()`, a byte is read from the stream and passed to `fromByte`. If the result is `OP_INVALID`, the reader verifies the log terminator. If the result has no op class or is `null`, the reader throws an invalid-opcode error. Otherwise `OpInstanceCache.get(opCode)` uses `getOpClass()` to instantiate or retrieve the matching `FSEditLogOp` subclass and then delegates payload decoding to that class.

During writes, `FSEditLogOp.Writer.writeOp()` asks the operation object for `op.opCode.getOpCode()` and writes that byte as the first byte of the frame. The opcode therefore controls both dispatch and durable compatibility.

## State and Persistence Behavior

The enum itself has no mutable runtime state after static initialization, but it defines the persistent edit-log namespace. `OP_INVALID` is not a normal operation; it is the terminator marker recognized by readers. The comment notes that valid opcodes are currently in the `0..127` range. Negative values other than `-1` are rejected by `fromByte`.

Because `VALUES` is indexed by byte code, sparse missing values would produce `null` entries. Existing code handles `null` by treating it as invalid. Adding a new opcode should append a new unused byte and map it to an operation class; changing existing byte assignments would corrupt compatibility with all previously written edit logs.

## Dependencies and Integration Points

The enum imports all nested `FSEditLogOp` classes and is used by `FSEditLogOp.OpInstanceCache`, edit-log readers/writers, offline edit viewers, inotify translation, and tests that assert opcode counts. It integrates with `FSEditLogLoader` indirectly because loader switch/dispatch behavior depends on the same op identities after decoding.

## Risks

The main risk is compatibility drift. Reassigning byte values, deleting obsolete constants, or changing an op class mapping can make old logs unreadable or make readers instantiate the wrong payload parser. Adding a constant without updating `FSEditLogOp`, replay logic, offline edits viewer expectations, and inotify handling can produce invalid-opcode failures or unsupported operation gaps.

There is also a guardrail risk around `VALUES`: the table is sized by maximum non-negative opcode, so non-contiguous codes are allowed but unknown holes return `null`. Code that assumes every value below `VALUES.length` is non-null would be incorrect.

## Test Signals

`TestDFSInotifyEventInputStream` asserts the total enum length, which is a useful signal when adding an opcode because inotify translator coverage may need adjustment. `TestOfflineEditsViewer` iterates `FSEditLogOpCodes.values()` and maintains a skipped-op set for unsupported/deprecated operations, so opcode additions commonly require viewer-test updates. Edit-log replay and journal tests such as `TestFileJournalManager`, `TestEditsDoubleBuffer`, and restart tests provide indirect validation that byte-to-class mapping still works.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLogOpCodes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSImage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSImage.java

## Purpose

`FSImage` orchestrates NameNode namespace persistence: formatting storage, recovering storage directories, loading the latest fsimage and edit logs at startup, handling upgrade/rollback/import flows, saving checkpoints, rolling edit logs for checkpointing, renaming and purging image files, and exposing transaction/checkpoint metadata. It is the high-level coordinator around `NNStorage`, `FSEditLog`, `FSImageFormat`, `FSImageFormatProtobuf`, and retention management.

The class is private/evolving NameNode infrastructure. It does not encode every inode itself; instead it chooses files, prepares streams and contexts, delegates actual image load/save to format loaders/savers, and maintains consistency between image directories, edit directories, md5 files, VERSION files, and transaction-id markers.

## Important APIs, Types, and Functions

Construction creates `NNStorage` from image and edits URIs, configures failed-storage restoration, creates a `FSEditLog`, initializes `NNStorageRetentionManager`, and configures protobuf parallel image loading.

Formatting and startup APIs include `format(FSNamesystem,String,boolean)`, `confirmFormat(...)`, `recoverTransitionRead(...)`, `recoverStorageDirs(...)`, `checkUpgrade(...)`, `doUpgrade(...)`, `doRollback(...)`, `doImportCheckpoint(...)`, `finalizeUpgrade(...)`, `hasRollbackFSImage()`, and `initEditLog(StartupOption)`.

Load APIs include private `loadFSImage(FSNamesystem,StartupOption,MetaRecoveryContext)`, `loadFSImageFile(...)`, `loadFSImage(File,...)`, `loadEdits(...)`, `reloadFromImageFile(...)`, `rollingRollback(...)`, and `setLastAppliedTxId(...)`.

Save and checkpoint APIs include `saveNamespace(...)` overloads, `saveFSImageInAllDirs(...)`, `saveFSImage(...)`, `saveLegacyOIVImage(...)`, `save(...)`, `rollEditLog(...)`, `startCheckpoint(...)`, `endCheckpoint(...)`, `saveDigestAndRenameCheckpointImage(...)`, `renameCheckpoint(...)`, `deleteCancelledCheckpoint(...)`, and `purgeOldStorage(...)`.

State accessors expose storage identity and progress: `getEditLog`, `getStorage`, `getLayoutVersion`, `getNamespaceID`, `getClusterID`, `getBlockPoolID`, `getLastAppliedTxId`, `getLastAppliedOrWrittenTxId`, `getCorrectLastAppliedOrWrittenTxId`, `updateLastAppliedTxIdFromWritten`, `getMostRecentCheckpointTxId`, and `getMostRecentNameNodeFileTxId`.

Important fields are `storage`, `editLog`, `lastAppliedTxId`, `archivalManager`, `newDirs`, `currentlyCheckpointing`, `isUpgradeFinalized`, `exitAfterSave`, and throttled edit-log loading telemetry.

## Control Flow

`recoverTransitionRead` is the main startup path. It validates configured image/edit directories, calls `recoverStorageDirs` to analyze and recover each storage directory, rejects unformatted or incompatible layouts unless the startup option permits transition work, handles metadata-version queries, prepares newly formatted HA dirs, then dispatches upgrade/import/regular paths. Regular startup calls `loadFSImage`.

`loadFSImage` inspects storage directories for latest `IMAGE` or `IMAGE_ROLLBACK` files, initializes the edit log according to HA/startup mode, selects edit streams from the checkpoint txid forward, applies max-op-size limits, tries candidate image files until one loads, and then either replays edits with `loadEdits` or performs rolling-upgrade rollback. Successful load sets the edit log's next txid to `lastAppliedTxId + 1` and returns whether startup should save a fresh namespace because storage inspection or stale checkpoint policy requested it.

`loadEdits` constructs an `FSEditLogLoader` beginning at the current `lastAppliedTxId`, iterates selected `EditLogInputStream`s, loads expected txids, updates `lastAppliedTxId` even if an error occurs after partial application, optionally advances to a stream's last txid in recovery mode, and always closes all edit streams.

`saveNamespace` ends the current log segment if open, determines the checkpoint txid as the max of applied and written txids, prevents concurrent checkpoint work for the same txid via `currentlyCheckpointing`, saves fsimages into all image dirs, updates storage versions when not in rolling upgrade, restarts the edit log segment at `imageTxId + 1`, writes the transaction-id marker, updates name-dir metrics, and terminates the process if the saver detected possible image corruption.

`saveFSImageInAllDirs` creates a `SaveNamespaceContext`, launches one `FSImageSaver` thread per image directory, waits for them, reports failed directories, rejects all-dir failure or cancellation, renames `IMAGE_NEW` files into their final `NameNodeFile` type, purges old checkpoints/edit logs unless the saved image is marked suspect, and marks the context complete.

Upgrade and rollback paths load existing state, prepare or roll back directory layouts with `NNUpgradeUtil`, coordinate shared edit logs for HA, save an upgraded image where appropriate, and mark `isUpgradeFinalized`.

## State and Persistence Behavior

`lastAppliedTxId` is the in-memory record of the latest transaction loaded from an image or applied from edits. `getLastAppliedOrWrittenTxId` and `getCorrectLastAppliedOrWrittenTxId` include the edit log's last-written txid so checkpoint saves include edits already written by an active NameNode.

Image persistence writes temporary `fsimage_N.ckpt`/`IMAGE_NEW` style files first, writes or renames associated `.md5` files, then renames into final `fsimage_N` or rollback-image names. This staged flow is central to crash recovery: storage inspection can distinguish complete images, checkpoint-in-progress files, and rollback images.

`NNStorage` owns VERSION files, storage directory locking, namespace IDs, cluster IDs, block-pool IDs, cTime/layout version, storage type filtering, removed-storage reporting, and transaction-id marker files. `FSImage` coordinates when those properties are read/written. Newly added HA image dirs may be partially formatted and later receive a VERSION file in `initNewDirs()` after a checkpoint image has been saved.

`FSImageCompression.createCompression(conf)` is used when saving protobuf images and legacy OIV images. Loads verify md5 digests either from sidecar `.md5` files or deprecated VERSION properties depending on layout features.

## Dependencies and Integration Points

`FSImage` integrates with `FSNamesystem` for namespace state, locks, HA mode, rolling-upgrade state, and save contexts; `NameNode` startup progress and static helpers; `FSEditLog` for journal initialization, segment rolling, edit stream selection, shared-log upgrade/rollback, and txid tracking; `NNStorage` and `StorageDirectory` for disk layout; `FSImageStorageInspector` for selecting latest images; `FSEditLogLoader` for replay; `FSImageFormat`/`FSImageFormatProtobuf` for actual image serialization; `NNStorageRetentionManager` for purging; `MD5FileUtils` for digest sidecars; and `SecondaryNameNode`/checkpoint protocol classes for remote checkpoint flows.

It is called from `NameNode` formatting, startup, rollback, import, bootstrap, admin `saveNamespace`, and checkpoint RPC paths. HA edit-log tailing and consistent-read tests depend on `getLastAppliedTxId` and related accessors.

## Risks

This class sits on several crash-consistency and HA boundaries. Risks include losing edits if `lastAppliedTxId`, edit-log next txid, or transaction-id marker writes get out of sync; accepting a stale or corrupt image if md5 and storage inspection checks are weakened; deleting needed edits/images during purge after a failed save; mishandling newly added HA directories; and racing concurrent checkpoints without `currentlyCheckpointing`.

Save failure handling is subtle: partial image directory failures should remove bad dirs but continue if at least one image dir succeeds; all-dir failure must fail loudly; cancellation must delete temporary checkpoints; and `exitAfterSave` deliberately terminates after saving an image with detected corruption. Rolling rollback is also high-risk because it discards edit segments after a chosen txid, renames rollback images, and purges newer checkpoints.

Changes to startup option handling must account for regular, import, upgrade, upgrade-only, metadata-version, HA standby, and rolling-upgrade rollback modes. Symlink assumptions in image loading are documented: persisted paths should not trigger intermediate symlink resolution.

## Test Signals

`TestSaveNamespace` directly targets saveNamespace failure, cancellation, restore, and checkpoint-threshold behavior. `TestEditLogRace` covers edit-log/saveNamespace races and restart consistency. `TestRollingUpgrade` and `TestRollingUpgradeDowngrade` exercise rollback fsimage detection and rolling-upgrade image lifecycle. HA tests such as `TestEditLogTailer`, `HATestUtil`, and `TestConsistentReadsObserver` validate `lastAppliedTxId` and edit replay on standbys. `TestFileJournalManager` and restart-oriented tests validate edit stream selection/replay after checkpointing. Admin tests under `hdfs/tools` cover `-saveNamespace` behavior in HA and non-HA modes. Any FSImage change should be validated with a MiniDFSCluster format/start/operate/saveNamespace/restart cycle and, for persistence changes, with md5 sidecar and storage-directory fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSImage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSImageCompression.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSImageCompression.java

## Purpose

`FSImageCompression` is a small container around optional fsimage compression. It decides whether an fsimage should be compressed from configuration or from an on-disk image header, records the chosen Hadoop `CompressionCodec`, writes the compression header, and wraps input/output streams so the rest of fsimage serialization can read or write uncompressed bytes regardless of the stored representation.

## Important APIs, Types, and Functions

The only state is `imageCodec`, which is `null` for no compression and a `CompressionCodec` instance when compression is enabled. `getImageCodec()` exposes it for callers/tests. `createNoopCompression()` returns the uncompressed variant.

`createCompression(Configuration)` reads `dfs.image.compress` (`DFS_IMAGE_COMPRESS_KEY`) and, when enabled, reads the configured codec class name from `DFS_IMAGE_COMPRESSION_CODEC_KEY` with Hadoop's default. `createCompression(Configuration,String)` resolves the class name through `CompressionCodecFactory.getCodecByClassName` and throws an `IOException` if the codec is unavailable.

`readCompressionHeader(Configuration,DataInput)` reads a boolean stored in the image. If false, it returns no-op compression. If true, it reads a codec class name via `Text.readString` and resolves that codec.

`unwrapInputStream(InputStream)` returns a `DataInputStream` over either `imageCodec.createInputStream(is)` or a `BufferedInputStream`. `writeHeaderAndWrapStream(OutputStream)` writes the boolean and optional codec class name to an unbuffered output stream, then returns a `DataOutputStream` over either the codec output stream or a `BufferedOutputStream`. `toString()` reports either the codec canonical name or `no compression`.

## Control Flow

During save, fsimage code calls `FSImageCompression.createCompression(conf)`. The saver passes the resulting object to the image format writer, which calls `writeHeaderAndWrapStream` before writing the image body. The header is always uncompressed and precedes the compressed body. When compression is enabled, the codec class canonical name is persisted so readers can select the same codec. When disabled, the returned body stream is still buffered.

During load, image format code reads early image metadata and calls `readCompressionHeader(conf,in)`. The boolean determines whether a codec class name follows. Then `unwrapInputStream` produces a stream yielding the uncompressed image payload for downstream deserialization.

## State and Persistence Behavior

The persistent compression metadata is minimal: one boolean followed, when true, by a codec class name encoded with Hadoop `Text`. The compressed data itself starts immediately after that header. This design makes compression self-describing per image file but still dependent on the reader's classpath and Hadoop codec configuration.

A no-op compression object is represented by `imageCodec == null`; there is no separate enum or flag after construction. Stream buffering differs by mode: uncompressed paths add Java buffering here, while compressed paths rely on the codec stream returned by `CompressionCodec`.

One subtle implementation detail is that `writeHeaderAndWrapStream` creates a `DataOutputStream dos` for the header, writes the header through it, and then wraps the original `OutputStream` for the body. This works because the header stream is not separately buffered, but callers must pass an unbuffered output stream as documented.

## Dependencies and Integration Points

The class depends on `Configuration`, `DFSConfigKeys`, `CompressionCodec`, `CompressionCodecFactory`, and Hadoop `Text`. It is used by `FSImage.saveFSImage` through `FSImageFormatProtobuf.Saver`, by `saveLegacyOIVImage`, and by fsimage format loaders/savers that own the concrete image wire format. It is not used for edit logs.

## Risks

The main operational risk is codec availability. A NameNode can write an image with a codec that a later NameNode process cannot resolve, causing load failure. Configuration changes must therefore be coordinated with installed codecs. Header compatibility is also important: changing the boolean/string order would make existing compressed images unreadable.

Because this class wraps streams, premature closing/flushing behavior is important in callers. The body stream returned by `writeHeaderAndWrapStream` must be closed or flushed by the saver so codec trailers and buffered bytes reach disk. Passing an already buffered or transformed stream can violate the method's assumption and make header/body ordering harder to reason about.

## Test Signals

Fsimage save/load restart tests indirectly cover compression when run with `dfs.image.compress=true` and a codec available in the test classpath. `TestSaveNamespace` and MiniDFSCluster restart/checkpoint tests are the strongest integration signals because they force image write, md5 sidecar creation, reload, and edit replay. Additional focused validation should exercise no-op compression, a configured supported codec, an unsupported codec class producing `IOException`, and reading a compressed image after changing unrelated fsimage settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSImageCompression.java -->
