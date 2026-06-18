# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSEditLogOp.java

## Purpose

`FSEditLogOp` is the edit-log record model for HDFS NameNode namespace mutations. It defines the abstract base operation, one nested payload class for each persistent edit opcode, binary serialization/deserialization, XML import/export support for offline tooling, transaction ID/RPC retry-cache metadata, and three reader implementations for different edit-log layout eras. Together with `FSEditLogOpCodes`, this file is the durable contract between active NameNodes, standby NameNodes, JournalNodes, offline edits tools, and future software versions reading older edits.

The file is intentionally broad because it centralizes the on-disk schema for namespace operations: file create/close/append/block updates, permissions and owner changes, quota changes, rename/delete/mkdir/symlink/truncate, leases, delegation tokens, log segment markers, snapshots, cache directives and pools, ACLs, xattrs, storage policies, rolling-upgrade markers, and erasure-coding policy operations.

## Important APIs, Types, and Functions

The outer `FSEditLogOp` stores `opCode`, `txid`, `rpcClientId`, and `rpcCallId`. `getTransactionId`, `setTransactionId`, `hasRpcIds`, `getClientId`, and `getCallId` expose durable transaction/retry-cache metadata. `reset()` restores common fields and delegates to `resetSubFields()` so cached op instances can be reused safely.

`OpInstanceCache` keeps a thread-local `EnumMap<FSEditLogOpCodes,FSEditLogOp>` and instantiates nested operation classes by reflection from `FSEditLogOpCodes.getOpClass()`. This reduces allocation in hot edit-log read/write paths but makes complete field reset critical. `disableCache()` forces new instances, useful for callers that cannot tolerate object reuse.

Each nested operation implements `readFields(DataInputStream,int)`, `writeFields(DataOutputStream)` or the log-version-aware overload, `toXml(ContentHandler)`, and `fromXml(Stanza)`. Important operation families include file/block operations (`AddOp`, `CloseOp`, `AppendOp`, `AddBlockOp`, `UpdateBlocksOp`, `TruncateOp`), metadata updates (`SetReplicationOp`, `SetPermissionsOp`, `SetOwnerOp`, `SetQuotaOp`, `SetQuotaByStorageTypeOp`, `TimesOp`, `SetStoragePolicyOp`), namespace shape changes (`ConcatDeleteOp`, `RenameOldOp`, `RenameOp`, `DeleteOp`, `MkdirOp`, `SymlinkOp`), leases, delegation token/key ops, segment markers, snapshot ops, cache directive/pool ops, ACL/xattr ops, rolling-upgrade ops, and erasure-coding policy ops.

`Writer.writeOp()` writes modern length-prefixed records: opcode byte, placeholder length, txid, op body, backfilled length, and CRC32 checksum. `Reader.create()` selects `LengthPrefixedReader`, `ChecksummedReader`, or `LegacyReader` from the log layout version. `Reader.readOp(skipBrokenEdits)` can scan forward one byte at a time in recovery mode after decode failures. `Reader.scanOp()` supports fast txid scanning where possible.

## Control Flow

On write, callers obtain a typed op from `OpInstanceCache`, populate fields with fluent setters, assign txid/RPC IDs in the surrounding edit-log layer, and call `Writer.writeOp(op, logVersion)`. `Writer` serializes a frame around `op.writeFields(...)`, computes CRC32 over the opcode/length/txid/body bytes, and appends the checksum.

On read, `Reader.create()` chooses the reader format. `LengthPrefixedReader.decodeOpFrame()` sets a stream limit, reads opcode and length, rejects oversized or undersized frames before allocating op payloads, reads txid, recomputes checksum over the complete frame excluding the checksum field, and returns the txid. `decodeOp()` then resets to the frame start, resolves the opcode to a cached op instance, assigns txid, skips length and txid fields, reads the op-specific payload, and skips the already-validated checksum. Older readers either validate checksum without a length prefix or fully decode legacy records, including layouts without stored txids.

`OP_INVALID` is the terminator. `verifyTerminator()` requires remaining bytes to be all `0x00` or `0xff`; this avoids silently treating a stray invalid byte as a clean end-of-log in the middle of useful data.

The op payload read/write methods are heavily version-gated by `NameNodeLayoutVersion.supports(...)`. Older layouts read numeric values as strings, omit inode IDs, omit retry-cache IDs, omit xattrs/ACLs/storage policies/erasure-coding fields, or use deprecated quota ops. Newer layouts write compact binary numeric values, protobuf sections, and additional fields.

## State and Persistence Behavior

The durable state is the ordered sequence of edit-log frames. Each record's byte opcode comes from `FSEditLogOpCodes`, txid establishes replay order, and payload fields are operation-specific namespace deltas. Some operations also persist RPC client/call IDs when the layout supports `EDITLOG_SUPPORT_RETRYCACHE`; replay can use them to preserve at-most-once semantics for retried client requests.

Several write methods defensively copy mutable block arrays so later namespace mutations do not corrupt queued edit records. Maximum counts (`MAX_BLOCKS`, `MAX_CONCAT_SRC`) protect read paths from malformed data causing unbounded allocation. The length-prefixed reader's `maxOpSize` limit is another safety barrier for NameNode and JournalNode startup.

The XML path is a second persistence/interchange format for offline tools rather than the primary NameNode recovery format. It must still preserve txid and op payloads well enough for offline edit viewing and tests that construct edits from XML.

## Dependencies and Integration Points

This class depends on HDFS protocol and namespace types: `Block`, cache directive/pool types, erasure-coding types, `StorageType`, permissions, ACLs, xattrs, delegation-token classes, layout feature gates, and `FSImageSerialization`. It uses Hadoop IO wrappers, protobuf helpers, SAX/XML utilities, and CRC32 via `DataChecksum`.

Major consumers include `FSEditLog` and journal output streams for writing, `FSEditLogLoader` and `EditLogInputStream` for replay, JournalNode scan/cache paths, NameNode bootstrap/upgrade code that copies or scans edit streams, and offline edits viewer classes.

## Risks

Durable compatibility is the core risk. Changing opcode byte values, reordering fields, removing version gates, or writing fields under the wrong layout feature can make existing clusters unable to replay edits. Missing `resetSubFields()` coverage in any cached op can leak data between records. Adding a new op requires coordinated changes in `FSEditLogOpCodes`, the nested op class, binary and XML read/write paths, replay in `FSEditLogLoader`, offline edits viewer handling, and inotify translation if relevant.

Resource exhaustion is another risk. Any variable-length read must keep bounds checks similar to `MAX_BLOCKS`, `MAX_CONCAT_SRC`, length-prefixed `maxOpSize`, and protobuf parser assumptions. Checksum or terminator verification changes can either reject valid old logs or silently accept corruption. Retry-cache metadata must be written only when supported by the layout; otherwise old readers can misalign.

## Test Signals

Relevant local tests and usage signals include `TestEditsDoubleBuffer` for writing representative ops through edit buffers, `TestFileJournalManager` for reading edit streams and last-op behavior, `TestOfflineEditsViewer` for opcode coverage and XML/offline rendering, `TestDFSInotifyEventInputStream` for the expected opcode count and inotify translation coverage, `TestFileAppendRestart` for append/block op sequences across restart, `DFSTestUtil` erasure-coding policy edit helpers, and `TestEditLogRace` for concurrent edit-log/saveNamespace behavior.
