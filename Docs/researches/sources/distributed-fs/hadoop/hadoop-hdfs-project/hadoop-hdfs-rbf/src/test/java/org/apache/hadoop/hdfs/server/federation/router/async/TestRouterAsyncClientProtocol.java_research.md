# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncClientProtocol.java

Purpose: compares selected async client-protocol methods with the synchronous `RouterClientProtocol` behavior.

Important APIs/types/functions: `RouterAsyncClientProtocol`, `RouterClientProtocol`, `FsServerDefaults`, `HdfsFileStatus`, `LocatedBlocks`, `AsyncUtil.syncReturn`, and the shared `RouterAsyncProtocolTestBase`. Setup instantiates async and sync protocol modules from the async and normal RPC servers.

Control flow: `testGetServerDefaults()` calls async `getServerDefaults`, materializes `FsServerDefaults`, then compares fields against the synchronous module result. `testClientProtocolRpc()` exercises common file-status/block-location style calls through the async module and compares returned metadata with synchronous router protocol results for paths created by the base fixture.

State and persistence behavior: depends on `/testdir` and any test file created in setup; no independent persistent state beyond base fixture cleanup. Integration points include Router async client protocol wrappers, synchronous protocol parity, path resolution, and async context retrieval. Risks include incomplete comparison if new fields are added to HDFS protocol objects and brittle async global state. Test signals are matching server defaults, non-null file metadata, and equal file/block information.
