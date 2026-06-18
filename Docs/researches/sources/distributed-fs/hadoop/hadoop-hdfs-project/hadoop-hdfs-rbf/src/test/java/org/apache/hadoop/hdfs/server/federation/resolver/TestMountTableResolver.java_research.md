# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestMountTableResolver.java

## Purpose
`TestMountTableResolver` is the main unit test for single-destination `MountTableResolver` behavior. It verifies path normalization, longest-prefix destination resolution, mount listing, entry removal/update, default nameservice fallback, cache behavior, and scalability.

## Important APIs, Types, and Functions
The tests use `MountTableResolver.addEntry()`, `removeEntry()`, `refreshEntries()`, `getDestinationForPath()`, `getMountPoint()`, `getMountPoints()`, `getMounts()`, `getCacheSize()`, `getLocCacheAccess()`, `getLocCacheMiss()`, and `MountTable.newInstance()`. Config keys include `FEDERATION_MOUNT_TABLE_MAX_CACHE_SIZE`, `FEDERATION_MOUNT_TABLE_CACHE_ENABLE`, and `DFS_ROUTER_DEFAULT_NAMESERVICE`.

## Control Flow
`setupMountTable()` creates a resolver with max cache size 10, default namespace `0`, root mapping, nested `/user` and `/usr/bin` mappings, read-only `/readonly`, and multi-destination `/multi`. Destination tests assert suffix rewriting for files/folders and consecutive slash normalization. Default namespace tests remove root and check fallback, then disable fallback and expect an IOException for root. Listing tests verify virtual child names and records below paths. Removal tests distinguish real subtree, virtual node, and leaf removal. Refresh/update tests replace entries and assert old cache/data invalidation. Scalability adds 100,000 flat entries, 1,000 deep entries, and 100,000 deep/wide entries. Cache tests cover disabled local cache, cache size cap, location cache update after refresh, child invalidation after adding a more specific mount, and hit/miss counters.

## State and Persistence
All resolver state is in memory: mount tree, default namespace flags, local location cache, and cache counters. There is no state-store backing in this unit test.

## Dependencies and Integration Points
The test integrates `MountTable` records, `PathLocation`, `RemoteLocation`, router config keys, and `GenericTestUtils` exception assertions. It guards behavior used by router path resolution before RPC fan-out.

## Risks and Test Signals
The scalability test is intentionally heavy and can be runtime-sensitive. `testMuiltipleDestinations` documents that this resolver rejects multi-destination mounts; those belong to `MultipleDestinationMountTableResolver`. Passing tests signal correct trie semantics, normalized paths, cache invalidation, read-only metadata retention, and safe fallback/default namespace behavior.
