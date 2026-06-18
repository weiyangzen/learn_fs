# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/MountTableResolver.java

Purpose: `MountTableResolver` implements path-to-subcluster resolution over State Store mount table records. It maps global federation paths to `PathLocation` objects and serves the hot Router RPC path.

Important APIs and state: constructors accept configuration plus optional `Router` or `StateStoreService`, configure optional Guava `locationCache`, register as an external State Store cache, and initialize default nameservice fallback. Mutable state includes an initialized/disabled flag, `TreeMap<String, MountTable>` path tree, cache hit/miss counters, default nameservice settings, and a read/write lock. Public APIs add/remove/refresh entries, load cache, clear, resolve paths, list mount points/mounts, and expose test knobs.

Control flow: `loadCache` refreshes the store cache, fetches all entries from `/`, calls `refreshEntries`, and publishes location-cache counters to `StateStoreMetrics`. `refreshEntries` atomically diffs new entries against the tree, removes stale entries leaf-first, adds/updates changed entries, and invalidates affected cache entries. `getDestinationForPath` verifies initialization, normalizes trash paths, consults or populates the path cache, and rewrites trash results back to the original path. `lookupLocation` finds the deepest mount and builds remote paths or falls back to the default namespace.

Dependencies and integration points: State Store `MountTableStore`, router config keys, `RouterAdmin` path normalization, `FileSystem` trash path conventions, `StateStoreMetrics`, and `RemoteLocation`/`PathLocation` data types.

Risks: this base resolver rejects multi-destination mount entries; callers need `MultipleDestinationMountTableResolver` for that. Cache invalidation is path-sensitive and must cover descendants and default-location entries. `verifyMountTable` fails when disabled or not initialized. Trash processing depends on current remote user. Default namespace fallback can hide missing mount coverage if enabled.

Test signals: mount add/remove/update invalidation, deepest mount matching, trash path processing, default namespace enabled/disabled, cache metrics, concurrent reads/writes, and multi-destination rejection.
