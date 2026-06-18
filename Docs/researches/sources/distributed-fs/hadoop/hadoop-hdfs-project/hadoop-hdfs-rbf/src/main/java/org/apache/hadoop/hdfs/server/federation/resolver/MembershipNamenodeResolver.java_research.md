# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/MembershipNamenodeResolver.java

Purpose: `MembershipNamenodeResolver` implements `ActiveNamenodeResolver` and `StateStoreCache` using State Store membership and disabled-nameservice records.

Important APIs and state: it holds lazy `MembershipStore` and `DisabledNameserviceStore` handles, a router ID for heartbeat registration, and two concurrent caches: nameservice plus observer-first flag to Namenode contexts, and block pool ID to contexts. `loadCache` refreshes underlying stores then clears both caches. `registerNamenode` converts `NamenodeStatusReport` into `MembershipState` and optional `MembershipStats`, then sends a heartbeat. `getNamespaces` filters disabled namespace IDs.

Control flow: lookup methods first check caches, query membership records on miss, filter expired/unavailable depending on parameters, sort by `NamenodePriorityComparator`, optionally move/shuffle observers ahead, mark disabled namespaces, and cache results. `updateNameNodeState` finds the matching membership record by nameservice/RPC address and writes an active/unavailable state update, invalidating affected caches. `rotateCache` demotes an inaccessible Namenode unless an active target is present.

Dependencies and integration points: State Store stores/protocols, `MembershipState`, `MembershipStats`, resolver comparator/state enum, and Router heartbeat services. Metrics and Router RPC paths depend on its priority results.

Risks: implementation sometimes returns `null` for no eligible Namenodes. `cacheNS` stores the mutable `result` list rather than the unmodifiable wrapper, and `rotateCache` casts cached lists to mutable lists. Observer shuffling is deliberate nondeterminism. Cache invalidation for block pool is broad because namespace-to-block-pool lookup is costly.

Test signals: cache refresh invalidation, active/unavailable updates, observer-first shuffling, disabled namespace filtering, heartbeat stats mapping, null/empty result handling, and rotate-cache behavior when active entries exist.
