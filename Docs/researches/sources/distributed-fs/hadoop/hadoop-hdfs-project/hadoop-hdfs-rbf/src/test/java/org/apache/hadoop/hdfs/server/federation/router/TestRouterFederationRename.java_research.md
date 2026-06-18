# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterFederationRename.java

## Purpose

`TestRouterFederationRename.java` provides the main positive and negative tests for Router Federation Rename, especially cross-namespace directory rename through the router. It extends `TestRouterFederationRenameBase` and covers success, unsupported file rename shape, pre-existing destinations, missing sources, mount-point restrictions, multi-destination source restrictions, and scheduler counter accounting. The source was read as a complete 350-line JUnit 5 test.

## Important APIs, Types, and Functions

Important types include `MiniRouterDFSCluster`, `RouterContext`, `DFSClient`, `ClientProtocol`, `RouterFederationRename`, `RemoteLocation`, `FileContext`, and Mockito spies. `MockGroupsMapping` implements `GroupMappingServiceProvider` and returns a deterministic group based on user name. Key methods are `testRenameDir`, `testSuccessfulRbfRename`, `testRbfRenameFile`, `testRbfRenameWhenDstAlreadyExists`, `testRbfRenameWhenSrcNotExists`, `testRbfRenameOfMountPoint`, `testRbfRenameWithMultiDestination`, and `testCounter`.

## Control Flow

Class-level setup starts the base federated mini-cluster. Each test calls `setup`, chooses a router, and uses nameservice-specific federated paths. The positive directory test creates a source directory with a file, invokes both `rename` and `rename2`, and checks the source is gone while the destination contains the child file. Negative tests call the router's `ClientProtocol` and expect `RemoteException` messages for file-to-directory rename, existing destination, missing source, mount-point rename, and multi-destination source. `testCounter` directly constructs a spy `RouterFederationRename`, starts a watcher thread on `RouterRpcServer.getSchedulerJobCount`, triggers `routerFedRename`, and verifies count increment/decrement plus maximum observed scheduler count.

## State and Persistence Behavior

Persistent test state is held in the MiniRouterDFSCluster namenode filesystems, router resolver mock locations, DistCp scheduler journal configured by the base class, and router metrics counters. Per-test source/destination paths are cleaned with `FileContext.delete`. `MockGroupsMapping` affects permission/group lookup for the cluster.

## Dependencies and Integration Points

The tests integrate DFS client protocol rename variants, router federation rename orchestration, DistCp procedure scheduling, caller context, router metrics, mock location resolution, and cross-namespace file movement. They depend on the base class's router rename options, journal URI, bandwidth/map settings, and datanode heartbeat tuning.

## Risks and Edge Cases

Message-fragment assertions make error text a compatibility surface. The scheduler counter test uses a 1 ms polling watcher and a timeout; slow environments could expose race conditions. The tests focus on directory rename; file rename support is intentionally expected to fail when the destination is a directory. Multi-destination source handling must stay strict because the implementation assumes exactly one remote source and one remote destination.

## Test Signals

Signals include successful `rename`/`rename2` across namespaces, stable source/destination existence checks, expected `RemoteException` messages, Mockito verification of `countIncrement` and `countDecrement`, and cleanup checks against the underlying namenode filesystems.
