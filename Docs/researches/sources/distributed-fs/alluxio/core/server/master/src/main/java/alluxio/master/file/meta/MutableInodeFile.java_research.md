# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/MutableInodeFile.java

## Purpose
`MutableInodeFile` is the mutable metadata representation for files in the file master. It tracks block ids, block container id, block size, length, completion/cacheability, persistence job metadata, replication settings, and temporary UFS persistence path.

## Important APIs, Types, and Functions
Important APIs include file-specific getters, `getBlockIdByIndex()`, `getNewBlockId()`, setters for block size/ids/cacheable/completed/length/persist job/replication/temp UFS path, `reset()`, `updateFromEntry(UpdateInodeFileEntry)`, static `fromJournalEntry()`, static `create()`, `toJournalEntry()`, `toJournalEntry(String)`, `toProto()`, and `fromProto()`. File inodes reject default ACL get/set with `UnsupportedOperationException`.

## Control Flow, State, and Persistence
The constructor derives the inode id from `BlockId.createBlockId(blockContainerId, maxSequenceNumber)`, while actual data block ids are generated from the same container id and the current block count. `create()` validates max replication is infinity or at least min, copies file options and common options, initializes owner/group/mode/ACL, persistence state, persistence wait time, xattrs, optional fingerprint, and optional complete-file block ids/length/completed status. `updateFromEntry()` applies file-specific journal updates, including replacing block lists when `setBlocks` is present. Journal/proto serialization includes block ids, block size, completion, length, replication, persistence job, temp UFS path, ACL, medium types, xattrs, and common fields.

## Dependencies and Integration Points
`InodeTree.createPath()` creates file inodes and allocates block containers. `InodeTreePersistentState.applyNewBlock()` calls `getNewBlockId()` and writes the inode back. File metadata feeds block deletion registration on delete, client `FileInfo`, file size histogram buckets, pinned and replication-limited id sets, and persistence queues.

## Risks
`getNewBlockId()` mutates `mBlocks` as a side effect, so callers must journal/write the inode through `InodeTreePersistentState` immediately. `setLength()` does not validate non-negative length. `generateClientFileInfo()` intentionally does not compute in-Alluxio percentage, so callers need block-master data for locality/completion. Default ACL methods throw, which can surprise generic ACL code if default entries are applied to files.

## Test Signals
Tests should cover block id sequence generation, invalid block index errors, replication max/min validation, create context mapping for persisted/not-persisted and complete-file cases, update entry application, journal/proto round trips, default ACL exceptions, file size histogram updates when completed length changes, and block deletion registration after file delete.
