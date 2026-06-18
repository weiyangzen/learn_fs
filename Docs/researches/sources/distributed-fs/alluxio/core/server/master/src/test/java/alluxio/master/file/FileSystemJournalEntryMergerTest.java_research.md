<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemJournalEntryMergerTest.java -->
## sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemJournalEntryMergerTest.java

**Purpose:** Verifies `FileSystemJournalEntryMerger` compacts related file-system journal entries while preserving non-mergeable records and special directory fingerprint updates.

**Important APIs/types/functions:** Uses `FileSystemJournalEntryMerger.add`, `getMergedJournalEntries`, `clear`, and journal protobuf entries: `InodeFileEntry`, `UpdateInodeEntry`, `UpdateInodeFileEntry`, `InodeDirectoryEntry`, `UpdateInodeDirectoryEntry`, and `AddMountPointEntry`.

**Control flow:** The main test adds file creations, inode updates, file-length updates, directory creation/update/name update, and a mount point entry. It then asserts merged output order and merged fields: file 1 has updated length but original name/path, file 2 has updated name, independent update for id 3 remains, directory id 1 has updated name and loaded flag, and mount point remains. It clears the merger and verifies empty output. The fingerprint test verifies a directory creation plus normal directory updates can merge, but an `UpdateInode` with `ufsFingerprint` remains a separate entry.

**State and persistence behavior:** Tests only in-memory journal-entry merging, but this directly affects journal persistence volume and metadata-sync journal flushing. It confirms that compaction does not lose UFS fingerprint updates that cannot be folded into directory creation entries.

**Dependencies and integration points:** Depends on `BlockId.createBlockId`, `PersistenceState`, Alluxio URI construction, and journal protobuf builders. It integrates with metadata sync and filesystem master contexts that use `FileSystemMergeJournalContext`.

**Risks:** Assertions are position-based, so any intended output ordering change will require test updates. The unused `AlluxioURI uri` local suggests historical context but no active behavior.

**Test signals:** Expected merged list sizes and fields, retained mount entry, separate fingerprint update entry, and empty list after `clear`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/FileSystemJournalEntryMergerTest.java -->
