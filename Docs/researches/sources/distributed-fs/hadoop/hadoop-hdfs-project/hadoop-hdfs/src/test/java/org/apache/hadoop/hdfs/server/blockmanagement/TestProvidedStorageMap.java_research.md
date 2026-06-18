# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestProvidedStorageMap.java

## Purpose
`TestProvidedStorageMap` validates how `ProvidedStorageMap` exposes HDFS PROVIDED storage to multiple DataNodes. It checks that all DataNodes presenting the configured provided storage UUID resolve to the same shared `DatanodeStorageInfo`, while regular DISK storage still follows normal DataNode-local registration.

## Important APIs, types, and functions
The test configures `DFS_PROVIDER_STORAGEUUID`, `DFS_NAMENODE_PROVIDED_ENABLED`, and `DFS_PROVIDED_ALIASMAP_CLASS` with `TestProvidedImpl.TestFileRegionBlockAliasMap`. It uses mocked `BlockManager` and `RwLock`, `DatanodeDescriptor`, `DatanodeStorage`, `DatanodeStorageInfo`, `StorageType.PROVIDED`, and `StorageType.DISK`. The central methods are `ProvidedStorageMap.getProvidedStorageInfo()` and `ProvidedStorageMap.getStorage(...)`.

## Control flow
`setup` prepares the provided UUID, alias map class, block pool ID, and mocks. `testProvidedStorageMap` creates the map and captures its singleton provided storage info. It creates a DataNode, then asks for a PROVIDED storage and a DISK storage while the mocked namesystem lock reports a global write lock. The provided lookup returns the map singleton; the disk lookup is null until a disk `DatanodeStorageInfo` is injected into the descriptor. A second DataNode with the same provided storage UUID also receives the same singleton, and its descriptor is updated to contain that provided storage.

## State and persistence behavior
The tested state is the in-memory association between DataNode descriptors and storage infos. PROVIDED storage is intentionally global per configured UUID and block pool, not a separate per-DataNode storage object. DISK storage remains descriptor-local. The test does not validate alias map persistence or block report contents, only mapping identity and registration side effects.

## Dependencies and integration points
This test sits at the BlockManager storage registration boundary. It depends on the provided-storage feature flags, alias map abstraction, NameNode locking contract, and `DFSTestUtil.getDatanodeDescriptor`. It does not start a cluster.

## Risks and test signals
The important signal is Java object identity: `dns1Provided == providedMapStorage`, `dns2Provided == providedMapStorage`, and injected disk storage identity is preserved. Regressions would duplicate provided storage per DataNode, fail to attach it to the descriptor, or treat unregistered disk storage as implicitly valid. The test does not cover disabled provided storage or wrong UUID behavior.
