# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AclFeature.java

Purpose: inode feature storing the explicit ACL entries that cannot be represented directly in `FsPermission` bits.

Important APIs/types/functions: holds final `int[] entries` encoded by `AclEntryStatusFormat`. `getEntriesSize()` and `getEntryAt()` expose packed entries. `equals()`/`hashCode()` are array-content based for deduplication. Implements `ReferenceCountMap.ReferenceCounter` with synchronized `getRefCount()`, `incrementAndGetRefCount()`, and `decrementAndGetRefCount()`. `EMPTY_ENTRY_LIST` provides a shared empty immutable ACL entry list constant.

Control flow: `AclStorage.createAclFeature()` builds instances; `INode` attaches/removes them; `AclStorage.UNIQUE_ACL_FEATURES` interns them by equality and manages reference counts.

State and persistence behavior: packed int array is persisted as part of inode features. Reference count is in-memory only and supports deduplicating identical ACL features across inodes.

Dependencies and integration points: implements `INode.Feature`; used by NameNode namespace, fsimage serialization, snapshots, and ACL modification APIs.

Risks: `entries` array is stored directly without defensive copy, so caller mutation would break immutability assumptions and reference-map hashing. Reference count methods are synchronized but broader lifecycle correctness depends on all attach/remove paths using `AclStorage`.

Test signals: `TestFSImageWithAcl`, `TestAclWithSnapshot`, and NameNode ACL tests exercise ACL persistence and feature sharing behavior.
