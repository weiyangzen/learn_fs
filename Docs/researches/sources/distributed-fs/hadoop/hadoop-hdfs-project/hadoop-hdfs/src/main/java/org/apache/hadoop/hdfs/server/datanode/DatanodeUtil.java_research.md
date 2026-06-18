# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DatanodeUtil.java

Purpose: `DatanodeUtil` centralizes small DataNode filesystem helpers for block metadata naming, temporary unlink files, block directory hashing, recursive empty-directory checks, disk-error wrapping, and metadata stream access.

Important APIs: `createFileWithExistsCheck` atomically guards creation of temporary files through `FileIoProvider`; `getMetaName` builds `blk_generation.meta` names; `getUnlinkTmpFile` appends `.unlinked`; `dirNoFilesRecursive` verifies a directory tree has no files; `idToBlockDirSuffix` and `idToBlockDir` map block IDs to the two-level `subdirN/subdirM` finalized layout; `getAllSubDirNameForDataSetLock` enumerates all 32x32 subdirectories; `getMetaDataInputStream` extracts the `FileInputStream` wrapped by dataset metadata input.

Control flow and state: the class is stateless except constants. The block-directory mapping uses bits 16-20 and 8-12 of the block ID with mask `0x1F`, matching DataNode finalized directory sharding. Creation failures from the provider are wrapped with the `DISK_ERROR` prefix so `getCauseIfDiskError` can recover the original cause.

Dependencies and integration points: it depends on `Block`, `ExtendedBlock`, `FsDatasetSpi`, `FsVolumeSpi`, `LengthInputStream`, `DataStorage`, and `FileIoProvider`. `LocalReplica` uses its metadata names, unlink tmp files, and ID-to-directory parsing; dataset locking code can use the subdirectory enumeration.

Risks: `getMetaDataInputStream` casts the wrapped stream to `FileInputStream`, so provided or non-local dataset implementations must match that assumption or avoid this helper. `dirNoFilesRecursive` treats directories as ignorable only if recursively empty; list failures become IOExceptions.

Test signals: cover block ID to subdirectory mapping at boundary values, existing temp file rejection, disk-error prefix cause extraction, recursive directory traversal with files and empty subdirs, metadata name formatting, and dataset metadata stream null/non-`FileInputStream` behavior.
