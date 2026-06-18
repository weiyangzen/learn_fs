# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_connect.c

## Purpose
Connection manager for `fuse_dfs`, caching libhdfs filesystem handles by OS user and Kerberos ticket cache while expiring idle or stale connections.

## Important APIs, Types, And Functions
Public functions are `fuseConnectInit`, `fuseConnectAsThreadUid`, `fuseConnectTest`, `hdfsConnGetFs`, and `hdfsConnRelease`. Internals include `struct hdfsConn`, red-black tree `gConnTree`, `discoverAuthConf`, `findKerbTicketCachePath`, `fuseNewConnect`, `fuseConnect`, `hdfsConnExpiry`, and the timer thread.

## Control Flow
Initialization reads Hadoop config keys for auth, timer, and connection timeout, stores NameNode URI/port, initializes the tree mutex, and starts the expiry thread. Each FUSE operation asks for a connection as the calling UID, resolves username and optionally ticket cache path, reuses or creates a libhdfs builder-backed connection, increments refcount, and later releases it. The timer periodically condemns Kerberos connections whose ticket cache mtime changed and frees idle expired entries.

## State, Persistence, And Dependencies
Global process state includes URI, port, auth mode, timeout settings, red-black tree, mutex, and timer thread. Each connection holds username, optional ticket path/mtime, hdfsFS, refcount, condemned flag, and expiration count. It depends on libhdfs builder APIs, FUSE context UID/PID, `/proc/<pid>/environ`, Kerberos cache files, pthreads, monotonic clock, and `util/tree.h`.

## Integration Points
All operation callbacks use this module through `fuseConnectAsThreadUid` and `hdfsConnGetFs`. `dfs_init` calls `fuseConnectInit` and optional `fuseConnectTest`.

## Risks
Connection tree operations rely on correct mutex discipline. Kerberos support assumes file ticket caches and `/proc` environment readability. `hdfsConnCompare` returns a raw `strcmp` expression only under Kerberos; null kpath assumptions must hold. The expiry thread never exits cleanly. Errors are often mapped to `-EIO`, reducing diagnosability at the FUSE layer.

## Test Signals
Signals include successful initial connection, reuse across operations, expiration after timeout, refresh after Kerberos ticket update, and no leaked or double-freed connections under concurrent FUSE traffic.
