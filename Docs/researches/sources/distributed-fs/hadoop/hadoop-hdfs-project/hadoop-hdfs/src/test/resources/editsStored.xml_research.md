# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/editsStored.xml

## Purpose

`editsStored.xml` is a stored HDFS edit-log XML fixture. The complete 1604-line XML was read. It captures a canonical serialized edit stream used by NameNode edit-log loader/offline edits tests to ensure that HDFS can parse, replay, and preserve compatibility for many operation encodings across filesystem, cache, ACL, xattr, erasure-coding, delegation-token, and rolling-upgrade features.

## Important APIs, Types, and Functions

The file is data rather than Java code, but it directly exercises edit-log record types consumed by HDFS offline edits processors and NameNode edit replay. Important serialized types include `<RECORD>`, `<OPCODE>`, `<DATA>`, `<TXID>`, `<BLOCK>`, `<PERMISSION_STATUS>`, `<DELEGATION_KEY>`, `<XATTR>`, erasure-coding policy payloads, cache pool/directive records, client identity fields (`RPC_CLIENTID`, `RPC_CALLID`), and lease-recovery records. The operation set includes `OP_START_LOG_SEGMENT`, `OP_UPDATE_MASTER_KEY`, `OP_ADD`, `OP_CLOSE`, `OP_APPEND`, `OP_ALLOCATE_BLOCK_ID`, `OP_SET_GENSTAMP_V2`, `OP_ADD_BLOCK`, `OP_UPDATE_BLOCKS`, `OP_SET_STORAGE_POLICY`, `OP_RENAME_OLD`, `OP_DELETE`, `OP_MKDIR`, snapshot operations, `OP_SET_REPLICATION`, permission/owner/time/quota changes, `OP_RENAME`, `OP_CONCAT_DELETE`, `OP_TRUNCATE`, `OP_SYMLINK`, `OP_REASSIGN_LEASE`, cache operations, ACL/xattr operations, erasure-coding policy operations, `OP_ROLLING_UPGRADE_START`, `OP_ROLLING_UPGRADE_FINALIZE`, and `OP_END_LOG_SEGMENT`.

## Control Flow

The stream begins with transaction 1 starting a log segment, then updates delegation master keys. Transactions 4-18 create, close, append, update block lists, set a storage policy, rename/delete a file, and create a directory. Transactions 19-24 cover allow/disallow snapshot, create, rename, and delete snapshot. Transactions 25-33 mutate a recreated `/file_create` through close, replication, permissions, owner, times, quotas, storage-type quota, and rename. Transactions 34-67 build concat target/source files with explicit block ID/generation-stamp allocation and then concatenate/delete sources. Transactions 68-86 cover truncation, symlink creation, and hard lease recovery with block generation-stamp bump and lease reassignment. Transactions 87-96 cover cache pool/directive and ACL/xattr mutation. Transactions 97-118 add, enable, disable, and remove erasure-coding policies, set an EC xattr on `/ec`, and create both replicated and striped files. Transactions 119-121 cover rolling upgrade start/finalize and log-segment end.

## State and Persistence Behavior

The fixture is entirely about persisted NameNode edit state. It encodes transaction ordering, inode IDs, paths, replication, mtimes/atimes, block IDs, block lengths, generation stamps, permissions, ACL entries, xattrs, quotas, cache pool metadata, cache directive IDs, EC policy lifecycle, striped block IDs, client RPC idempotency metadata, and rolling-upgrade timestamps. It also preserves special values such as empty client IDs, `RPC_CALLID=-2` for internal block updates, and negative striped block IDs.

## Dependencies and Integration Points

The fixture integrates with XML offline edits parsing, binary-to-XML round-trip tests, edit-log replay in FSImage/NameNode startup paths, delegation-token key parsing, cache manager state, snapshot manager state, ACL and xattr feature serialization, erasure-coding policy manager state, and rolling-upgrade metadata. The path names are intentionally broad enough to trigger code paths in namespace, block manager, cache manager, and EC policy logic.

## Risks and Edge Cases

Risks covered include edit-loader drift when new fields are added, incorrect defaulting of legacy fields, transaction order sensitivity, losing RPC idempotency identifiers, mishandling empty block updates, preserving ACL/xattr binary encodings, parsing negative striped block IDs, and compatibility regressions for old rename, truncate, symlink, cache, and rolling-upgrade opcodes. Because this is a golden fixture, small textual changes can invalidate round-trip expectations.

## Test Signals

Useful signals are successful XML parsing, every `TXID` replaying in order from 1 through 121, exact opcode recognition, stable offline-edits XML output, correct namespace reconstruction of files/directories/snapshots/cache entries/EC state, and no unknown-field or compatibility errors during edit-log loader tests.
