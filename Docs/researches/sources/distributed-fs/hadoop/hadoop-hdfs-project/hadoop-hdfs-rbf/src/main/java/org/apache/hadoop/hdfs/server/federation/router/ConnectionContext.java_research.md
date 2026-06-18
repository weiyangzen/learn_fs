# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionContext.java

Purpose: wraps a Namenode RPC proxy and tracks concurrent use, recent activity, and closure for a `ConnectionPool`.

Important APIs and state: stores `ProxyAndInfo<?>`, active thread count, closed flag, last active timestamp, active-window constant of 30 seconds, and max concurrency per connection from configuration. `isActive`, `isActiveRecently`, `isClosed`, `isUsable`, `isIdle`, `getClient`, `release`, and `close` are synchronized. `getClient` reserves the connection by incrementing thread count.

Control flow: a caller obtains the proxy through `getClient` and must call `release`. `close(false)` logs if closing with active handlers but still closes to avoid leaks after removal from a pool; `RPC.stopProxy` shuts down the underlying proxy.

Dependencies and integration points: used by `ConnectionPool` and `ConnectionManager`, wraps Hadoop RPC proxies created by `ConnectionPool.newConnection`.

Risks: missing `release` leaks active count and reduces usability. `isActiveRecently` starts true until 30 seconds after construction because `lastActiveTs` defaults to 0 only if monotonic time is below window early in process; normally it becomes false after uptime exceeds the window. Forced close can interrupt active callers.

Test signals: concurrency limit, reserve/release count, idle/active/recent flags, close behavior with active users, and proxy shutdown.
