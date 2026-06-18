<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBatchedListDirectories.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBatchedListDirectories.java

Purpose: Tests the experimental batched listing APIs for files, directories, located statuses, repeated paths, missing paths, relative paths, limits, and access-control failures.

Important APIs, types, and functions: `DistributedFileSystem.batchedListStatusIterator`, `batchedListLocatedStatusIterator`, `PartialListing<FileStatus>`, `PartialListing<LocatedFileStatus>`, `RemoteIterator`, `CommonPathCapabilities.FS_EXPERIMENTAL_BATCH_LISTING`, `DFS_LIST_LIMIT`, `DFS_NAMENODE_BATCHED_LISTING_LIMIT`, `FsPermission`, and `UserGroupInformation.doAs`.

Control flow: `beforeClass` starts a one-DataNode cluster with small listing limits and calls `loadData`. The fixture creates two first-level directories, three subdirectories under each, five files per subdirectory, an empty directory, a standalone data file, and a no-permission directory containing a file. Helpers convert `PartialListing` iterators into lists while preserving per-source listed paths. Tests cover empty input, empty directories, files, missing paths, mixtures of missing and valid paths, relative working-directory behavior, capability declaration, batches of many file paths, batches of directory paths, too many source paths, repeated paths, located status block metadata, and listing as a non-owner user.

State and persistence behavior: Static lists `SUBDIR_PATHS` and `FILE_PATHS` mirror the fixture tree for expected ordering and path assertions. The cluster is static for the test class and shut down once. Permission state is persisted in HDFS inode metadata by setting the inaccessible directory to mode `0000`.

Dependencies and integration points: Integrates the HDFS batched listing implementation with `FileSystem` path qualification, NameNode list batching, partial exception reporting, located block lookup, path capabilities, and Hadoop security/permission checks.

Risks: The expected ordering relies on fixture insertion/listing order and on `LinkedHashMap` grouping. Some missing-path behavior is lazy: exceptions are raised by `PartialListing.get()`, so callers must not assume iterator construction alone validates every path. Static mutable fixture lists would be problematic if the setup were rerun in the same JVM without class isolation.

Test signals: Success means batch iterators preserve path grouping and duplicate inputs, return correct file counts and qualified paths, surface `FileNotFoundException` and `AccessControlException` at the expected time, respect configured path limits, expose block locations for located listing, and advertise the experimental capability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBatchedListDirectories.java -->
