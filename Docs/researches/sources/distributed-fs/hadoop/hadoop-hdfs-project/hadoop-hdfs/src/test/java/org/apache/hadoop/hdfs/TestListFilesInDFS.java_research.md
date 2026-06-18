# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestListFilesInDFS.java

## Purpose
Runs the generic `TestListFiles` suite against HDFS through `DistributedFileSystem`.

## APIs and Control Flow
`testSetUp` sets the inherited test paths to `/tmp/TestListFilesInDFS`, creates a `MiniDFSCluster`, initializes inherited `fs`, and deletes any old test directory. `testShutdown` closes `fs` and shuts down the cluster. `getTestDir` returns `/main_` for inherited tests.

## State, Dependencies, Integration
State is inherited from `TestListFiles` fixtures and HDFS namespace entries created by that suite. Dependencies are `MiniDFSCluster`, `Path`, and the superclass test contract. It integrates the common file-listing contract with HDFS.

## Risks and Test Signals
Signals are inherited tests from `TestListFiles`, not explicit methods in this file. Risks are limited local visibility into exact assertions, and static inherited fields requiring proper cleanup between suites.
