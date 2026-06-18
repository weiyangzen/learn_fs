# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockPoolManager.java

## Purpose
`TestBlockPoolManager` validates how `BlockPoolManager` interprets NameNode and nameservice configuration, creates or refreshes `BPOfferService` instances, filters internal nameservices, and expands a nameservice through DNS resolution.

## Important APIs, Types, and Functions
- A test subclass of `BlockPoolManager` overrides `createBPOS` to return Mockito `BPOfferService` objects and log create, refresh, and stop events.
- Mock `BPServiceActor` instances expose NN IDs and socket addresses.
- `refreshNamenodes(Configuration)` is the primary behavior under test.
- `addNN` writes `dfs.namenode.rpc-address.<ns>` keys via `DFSUtil.addKeySuffixes`.
- `addDNSSettings` enables nameservice resolution and selects `MockDomainNameResolver`.

## Control Flow and Behavior
Each test builds a `Configuration` and invokes `refreshNamenodes`. `testSimpleSingleNS` uses `fs.defaultFS` and expects one creation. `testFederationRefresh` starts with two nameservices, removes one, then adds it back and checks that the retained BPOS is refreshed and the removed one is stopped. `testInternalNameService` verifies that `dfs.internal.nameservices` restricts creation to the internal service. `testNameServiceNeedToBeResolved` configures one nameservice with a mock domain and asserts that it expands into two actor endpoints with generated NN IDs.

## State and Persistence
The test stores state in a `StringBuilder` log and in `BlockPoolManager`'s in-memory map from nameservice ID to `BPOfferService`. No filesystem persistence is involved.

## Dependencies and Integration Points
The file depends on `DFSConfigKeys`, `DFSUtil`, `MockDomainNameResolver`, Mockito, and DataNode block-pool management classes. It is a unit-level configuration parser and lifecycle test rather than a MiniDFSCluster integration test.

## Risks and Edge Cases
Risks covered include accidental recreation instead of refresh, failure to stop removed block pools, ignoring the internal nameservice filter, and bad NN IDs or addresses when DNS resolution expands one logical nameservice into multiple physical endpoints.

## Test Signals
Signals are exact log sequences for create/refresh/stop, `getBpByNameserviceId` membership, actor counts, generated NN IDs, and resolved `InetSocketAddress` values.
