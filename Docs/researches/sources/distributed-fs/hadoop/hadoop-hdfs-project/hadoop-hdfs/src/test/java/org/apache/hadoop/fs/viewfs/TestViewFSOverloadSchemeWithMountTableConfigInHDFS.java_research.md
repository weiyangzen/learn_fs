# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFSOverloadSchemeWithMountTableConfigInHDFS.java

## Purpose

This subclass verifies that `ViewFileSystemOverloadScheme` can load mount-table configuration from versioned XML files stored in HDFS rather than only from in-memory `Configuration` keys. It extends the broader HDFS-scheme overload test suite and changes only mount-link persistence.

## Important APIs, types, and functions

Important APIs are `Constants.CONFIG_VIEWFS_MOUNTTABLE_PATH`, `ViewFileSystemOverloadScheme.ChildFsGetter`, `ViewFsTestSetup.addMountLinksToFile`, `FileSystem.createNewFile`, and the inherited `addMountLinks` contract from `TestViewFileSystemOverloadSchemeWithHdfsScheme`.

## Control flow, state, and persistence

`setUp` calls the parent setup, derives an HDFS `/MountTable/` directory from `fs.defaultFS`, configures it as the mount-table path, creates old and new version files `mount-table.30.xml` and `mount-table.31.xml`, then overrides `addMountLinks` to write the mount links into the newer file. Runtime state is the HDFS mount-table directory; the overload scheme should choose the highest version.

## Dependencies and integration points

The test covers ViewFS mount-table loading from HDFS, versioned mount-table file selection, `ChildFsGetter` target initialization, and inherited overload-scheme operations for local, HDFS, fallback, Nfly, and cache behavior.

## Risks and test signals

Risks include selecting the wrong mount-table version, failing to initialize the child HDFS used to read mount tables, or diverging between file-backed and configuration-backed link parsing. Passing inherited tests through this subclass signals that file-backed mount links are behaviorally equivalent.
