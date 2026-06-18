# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/LocalReplica.java

Purpose: `LocalReplica` is the abstract base for replicas backed by local block and metadata files. It implements file path derivation, stream access, hard-link breaking, pinning, generation-stamp metadata rename, truncation, copy, delete, and directory fsync behavior.

Important APIs: `getBlockFile`, `getMetaFile`, `getDir`, `parseBaseDir`, `breakHardLinksIfNeeded`, data/metadata stream methods, delete/existence/length methods, `renameMeta`, `renameData`, `updateWithReplica`, pinning accessors, `bumpReplicaGS`, `truncateBlock`, `compareWith`, `copyMetadata`, `copyBlockdata`, static `truncateBlock`, and `fsyncDirectory`.

Control flow: directory state stores an interned base directory plus a `hasSubdirs` flag. If the provided directory matches the sharded block-ID layout, `getDir` recomputes the leaf via `DatanodeUtil.idToBlockDir`; otherwise it uses the base directly. Hard-link breaking copies a block/meta file to an `.unlinked` temp file, verifies length, and atomically replaces the original. Truncation rewrites both block file length and final checksum metadata after recomputing the last chunk checksum.

State and persistence: object state includes block identity inherited from `ReplicaInfo`, `baseDir`, and `hasSubdirs`. Persistent state is the block data file, metadata file, sticky-bit pinning, directory entries, and generation-stamped metadata filename. `internedBaseDirs` reduces duplicate `File` object memory across replicas.

Dependencies and integration points: it uses `FileIoProvider`, `DatanodeUtil`, `DataStorage`, `BlockMetadataHeader`, `DataChecksum`, `NativeIO`, `FsVolumeSpi`, `ScanInfo`, `LocalFileSystem`, `FsPermission`, and `StorageLocation`. `FinalizedReplica` and `LocalReplicaInPipeline` inherit this local-file contract.

Risks: `getMetadataOutputStream` directly creates `FileOutputStream`, bypassing `FileIoProvider` instrumentation. `parseBaseDir` relies on subdirectory names starting with the block subdir prefix. Hard-link breaking must clean temp files on failure or upgrades can leave restart artifacts. `truncateBlock` must handle zero-length and checksum geometry carefully; new length greater than old length is rejected.

Test signals: cover sharded/non-sharded directory parsing, base-dir interning, block/meta path generation, hard-link break replacement and cleanup, NativeIO/share-delete and open-and-seek paths, sticky-bit pinning, generation stamp rename rollback, truncation checksum updates, copy operations through provider, and fsync directory error wrapping.
