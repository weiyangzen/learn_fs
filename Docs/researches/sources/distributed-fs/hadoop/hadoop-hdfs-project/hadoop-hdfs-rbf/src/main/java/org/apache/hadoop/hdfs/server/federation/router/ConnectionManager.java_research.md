# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionManager.java

Purpose: owns all Router-to-Namenode connection pools, asynchronous connection creation, and periodic cleanup.

Important APIs and state: configuration controls pool max size, minimum active ratio, creator queue size, pool cleanup period, and connection cleanup period. State includes a map of `ConnectionPoolId` to `ConnectionPool`, read/write lock, bounded creator queue, `ConnectionCreator` thread, cleanup executor, `RouterStateIdContext`, and running flag. Public methods start/close the manager, get a connection, expose pool/connection counts, and render JSON.

Control flow: `getConnection` rejects calls when stopped, looks up or creates a pool under locks, advances the pool alignment context with client state ID, asks the pool for a connection, and queues async pool growth if the chosen connection is null or unusable. `CleanupTask` periodically removes stale pools or asks `cleanup(pool)` to close idle excess connections. `ConnectionCreator` takes pools from the queue and creates a new connection only if below max size and recent active ratio justifies growth.

Dependencies and integration points: `ConnectionPool`, `ConnectionPoolId`, `RouterStateIdContext`, `PoolAlignmentContext`, UGI, and Router RPC clients.

Risks: `running` is not volatile but typically controlled by lifecycle thread. Queue dedup uses `contains(pool)` on object identity and may race. Cleanup closes pools under read lock and removes under write lock later. If all connections are busy, `getConnection` can return a busy connection rather than null, relying on per-connection concurrency checks.

Test signals: lazy pool creation, stopped-manager behavior, async creator queue saturation, pool cleanup timing, connection cleanup active-ratio logic, JSON counters, and close shutting down all pools/threads.
