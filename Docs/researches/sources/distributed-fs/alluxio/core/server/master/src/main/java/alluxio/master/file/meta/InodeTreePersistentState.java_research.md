# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeTreePersistentState.java

## Purpose
`InodeTreePersistentState` owns all durable inode-tree state and the journal replay contract. All metadata modifications are expected to flow through this class as journal entries so in-memory state, checkpoints, and standby replay stay aligned.

## Important APIs, Types, and Functions
Public APIs expose retry-cache state, root lookup, inode count and file-size histogram, pinned/replication-limited/to-be-persisted id sets, TTL buckets, `applyAndJournal()` overloads for create/delete/rename/new-block/update/set-acl entries, non-journaled access-time application, `processJournalEntry()`, checkpoint write/restore, and `getJournalEntryIterator()`. Derived checkpointed sets are `PinnedInodeFileIds`, `ReplicationLimitedFileIds`, `ToBePersistedFileIds`, `InodeCounter`, and `TtlBucketList`.

## Control Flow, State, and Persistence
`applyAndJournal()` methods apply mutations and append corresponding `JournalEntry` objects, with fatal master termination on unexpected failure. Delete is special: the delete journal entry is appended before in-memory removal to avoid replay ordering races with a concurrent create of the same name. Create writes the inode, adds the parent edge, increments counters, updates parent child count, pin/replication derived sets, TTL buckets, to-be-persisted ids, and file-size buckets for completed files. Rename removes the old child edge, changes name and parent, adds the new edge, writes the inode, and updates old/new parent timestamps and child counts.

Replay is implemented by `processJournalEntry()`, which dispatches current entries plus deprecated entries (`AsyncPersistRequest`, `CompleteFile`, `InodeLastModificationTime`, `PersistDirectory`, `SetAttribute`) into current update routines. Operation ids from `RpcContext` are attached to selected journal entries and cached after replay for retry de-duplication. Checkpoints persist and restore the inode store plus derived checkpointed structures; TTL buckets are ordered after the inode store because they resolve ids to inodes.

## Dependencies and Integration Points
This class depends on `InodeStore`, `InodeLockManager` parent update locks, journal/checkpoint utilities, proto journal entries, ACL/proto conversion, `BucketCounter`, and configuration for retry cache and file size histogram buckets. `InodeTree` delegates all durable namespace mutation to it, and the journal subsystem delegates replay/checkpointing through the `Journaled` interface.

## Risks
Many apply paths call `.get()` on optional inode lookups and assume replay/input validity; corrupt or out-of-order journals can crash the master. `applyDelete()`'s recursive deprecated branch appears to call `removeInodeAndParentEdge(inode)` for queued children using the original inode variable, which is a risk for old recursive delete replay. `resetState()` clears the inode store and some derived sets but not all visible derived structures such as TTL buckets, inode counter, to-be-persisted ids, or bucket counter in the shown code, so reset semantics need careful integration testing. Asynchronous access-time updates are deliberately ignored if the target inode is missing, but other missing inode updates are fatal.

## Test Signals
Round-trip tests should apply journal entries, checkpoint/restore, and compare inode store plus derived sets. Specific signals include delete-before-create replay ordering, rename parent child-count/timestamp updates, pin updates affecting replication min and pinned ids, replication max affecting replication-limited ids, TTL update bucket removal/reinsert, async access-time missing-inode tolerance, deprecated journal entry replay, and retry-cache operation id behavior.
