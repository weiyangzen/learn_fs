# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/StateStoreDFSCluster.java

## Purpose
`StateStoreDFSCluster` extends `MiniRouterDFSCluster` with state-store-backed router resolver configuration and helpers for creating membership and mount-table fixtures. It is the main integration-test cluster for Router Based Federation tests that exercise state-store behavior.

## Important APIs, Types, and Functions
Constructors choose HA mode, numbers of nameservices and NameNodes, heartbeat/cache intervals, and optional file resolver class. Fixture methods include `createTestRegistration(StateStoreService)`, `createTestMountTable(StateStoreService)`, `generateMockMountTable()`, and `getRouterClientConf()`.

## Control Flow
Construction delegates to `MiniRouterDFSCluster`, creates a state-store test configuration, sets `FEDERATION_NAMENODE_RESOLVER_CLIENT_CLASS` to `MembershipNamenodeResolver`, sets `FEDERATION_FILE_RESOLVER_CLIENT_CLASS` to the requested file resolver, and adds those overrides to routers. Registration fixtures iterate the mini-cluster NameNode contexts and synchronize synthetic `MembershipState` records. Mount table fixtures create one direct federated path per nameservice plus a root mount to the first nameservice, then refresh caches.

## State and Persistence
The cluster state is inherited from `MiniRouterDFSCluster`; this class writes membership and mount-table records into the provided `StateStoreService` using `synchronizeRecords()`. It does not maintain a separate durable store beyond the configured test driver.

## Dependencies and Integration Points
It depends on federation state-store test utilities, `MembershipNamenodeResolver`, `MountTableResolver`, `MountTable`, `MembershipState`, `DFSTestUtil`, and HDFS HA client configuration keys. `getRouterClientConf()` integrates with Hadoop HA client failover by advertising all router RPC ports under a synthetic nameservice `fed`.

## Risks and Test Signals
The fixture assumes nameservice ordering is stable, especially for the root mount to index 0. A typo in the constructor parameter name is harmless but visible. Tests using this class signal state-store integration by successfully loading router resolver caches, resolving generated federated paths, and failing over client RPCs across routers.
