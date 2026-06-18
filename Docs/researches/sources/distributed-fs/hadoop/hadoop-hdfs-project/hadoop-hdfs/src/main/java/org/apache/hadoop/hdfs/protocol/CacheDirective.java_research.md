# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirective.java

Purpose: Represents a NameNode cache directive: a path to cache, replication factor, owning cache pool, expiry time, computed cache statistics, and intrusive-list membership in the pool.

Important APIs and types: Constructors accept `CacheDirectiveInfo` or explicit id/path/replication/expiry. Getters expose id, path, replication, pool, expiry time, and formatted expiry. `toInfo()`, `toStats()`, and `toEntry()` convert internal state to protocol objects. Statistics methods reset or add bytes/files needed/cached and propagate deltas to the owning `CachePool`. Intrusive collection methods `insertInternal`, `setPrev`, `setNext`, `removeInternal`, `getPrev`, `getNext`, and `isInList` maintain list links.

Control flow: Construction validates positive id and replication and non-null path. `toInfo()` always emits an absolute expiration. `toStats()` computes `hasExpired` from current wall-clock time. Add-stat methods increment directive counters and immediately update pool counters. Intrusive insertion records the pool from the list, and removal clears pool and links.

State and persistence behavior: Persistent NameNode in-memory state includes immutable id/path/replication/expiry, mutable pool pointer, mutable stats, and intrusive prev/next links. Cache directive persistence to fsimage/edit logs is handled elsewhere through info objects; this class converts to protocol records for that process.

Dependencies and integration points: Depends on `CacheDirectiveInfo`, `CacheDirectiveStats`, `CacheDirectiveEntry`, `CachePool`, Hadoop `Path`, `DFSUtil.dateToIso8601String`, `IntrusiveCollection`, and `Preconditions`. It integrates with NameNode cache manager and cache pool directive lists.

Risks: Stats updates assume `pool` is non-null; calling add methods before insertion or after removal would fail. Equality/hashCode are id-only, so id uniqueness is required. Wall-clock expiry checks are time-sensitive. Intrusive list assertions may be disabled at runtime, reducing misuse detection.

Test signals: Tests should cover construction validation, conversion to info/stats/entry, expiry status before/after expiry, stat propagation to `CachePool`, reset behavior, intrusive insert/remove/link navigation, id-based equality, and operations attempted outside a pool list.
