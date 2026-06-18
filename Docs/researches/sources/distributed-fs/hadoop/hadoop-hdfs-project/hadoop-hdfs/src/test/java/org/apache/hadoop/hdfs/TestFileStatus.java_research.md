# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileStatus.java

## Purpose
JUnit coverage for HDFS `FileStatus`, `HdfsFileStatus`, `FileContext.listStatus`, `FileSystem.listStatus`, and list iterators. It validates file, directory, nonexistent-path, qualification, content-summary length, listing order, and erasure-coding status for non-EC paths.

## APIs and Control Flow
`@BeforeAll testSetUp` builds a `MiniDFSCluster`, sets `DFS_LIST_LIMIT` to 2 to force batched listings, initializes `FileSystem`, `FileContext`, `DFSClient`, and creates `filestatus.dat`. `testGetFileInfo` checks root, null return for missing `DFSClient.getFileInfo`, child counts, and non-absolute path rejection. `testGetFileStatusOnFile`, `testListStatusOnFile`, `testGetFileStatusOnNonExistantFileDir`, and `testGetFileStatusOnDir` exercise direct status calls, one-file listing, missing-path exception messages, and increasingly populated directory iteration, including deletion while iterating.

## State, Dependencies, Integration
State is cluster-local namespace metadata and file blocks. It depends on `DFSTestUtil`, `ContractTestUtils`, `GenericTestUtils`, `FSNamesystem`, and both old and newer status iterator APIs. It integrates client-side `DFSClient` semantics with public `FileSystem` and `FileContext` behavior.

## Risks and Test Signals
Strong signals are exact assertions on block size, replication, lengths, qualified paths, EC flags, iterator ordering, and `FileNotFoundException` behavior. Risk areas are brittle exception text, ordering assumptions from HDFS directory listing, and races around deleting a parent while a batched iterator is active.
