# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/MockNamenode.java

## Purpose
`MockNamenode` is a test fixture that exposes a Mockito-backed `NamenodeProtocols` implementation through real Hadoop RPC and HTTP endpoints. Router federation tests use it to register lightweight NameNodes with routers without starting full `NameNode` processes.

## Important APIs, Types, and Functions
The public surface includes constructors taking a nameservice id and optional `Configuration`, endpoint accessors `getRPCPort()` and `getHTTPPort()`, `getMock()` for extending the Mockito object, HA helpers `transitionToActive()` and `transitionToStandby()`, lifecycle `stop()`, feature installers `addFileSystemMock()` and `addDatanodeMock()`, and static `registerSubclusters(...)`. Internally it wires `ClientNamenodeProtocolPB`, `NamenodeProtocolPB`, `DatanodeProtocolPB`, and `HAServiceProtocolPB` translators into one `RPC.Server`, and starts an `HttpServer2`.

## Control Flow
Construction initializes namespace identity, creates the Mockito `NamenodeProtocols`, stubs `versionRequest()` and `getServiceStatus()`, then starts RPC and HTTP servers on ephemeral ports. `addFileSystemMock()` installs Mockito answers backed by a `ConcurrentSkipListMap<String,String>` that models path type, handles listing, file info, create, block location, complete, add block, mkdirs, server defaults, and content summary. `addDatanodeMock()` returns the fixture's datanode list and synthetic storage reports. `registerSubclusters()` builds `NamenodeStatusReport` records for each mock NameNode and pushes them into each router's `MembershipNamenodeResolver`.

## State and Persistence
State is in-memory only: `nsId`, `haState`, `dns`, server handles, and the file-system map captured by `addFileSystemMock()`. There is no durable persistence. Registration writes to router resolver/state-store layers through `MembershipNamenodeResolver`, but this fixture itself only owns transient ports and mock behavior.

## Dependencies and Integration Points
The class depends heavily on Mockito, Hadoop IPC/protobuf protocol translators, `HttpServer2`, HDFS protocol records, HA service protocol types, and router membership APIs. It integrates with router registration tests and mock-cluster tests that need real RPC addresses and block tokens carrying a nameservice-specific block pool id.

## Risks and Test Signals
Risks include incomplete HDFS semantics: directory parent creation skips root, file lengths are fixed at 100, block locations are synthetic, and the filesystem map does not enforce all NameNode invariants. RPC/HTTP lifecycle leaks would affect test stability if `stop()` is not called. Strong test signals are endpoint startup, registration of available/unavailable subclusters, and expected failures for missing files through `FileNotFoundException`.
