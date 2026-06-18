# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionPool.java

Purpose: maintains multiple RPC proxy connections for one user/token set, Namenode address, and protocol so the Router can multiplex requests across sockets.

Important APIs and state: stores configuration, `ConnectionPoolId`, target address, UGI, protocol, copy-on-write volatile connection list, round-robin client index, socket index for multi-socket mode, min/max sizes, min active ratio, last active time, multi-socket flag, and `PoolAlignmentContext`. `PROTO_MAP` maps public protocols to protobuf protocol and translator classes. Methods get/add/remove/close connections, count active/idle/recent connections, render JSON, and create new RPC connections.

Control flow: constructor creates minimum connections. `getConnection` first returns any usable connection; if none, it returns a round-robin connection even if busy so the manager can decide whether to grow the pool. `addConnection` and `removeConnections` replace the volatile list with a new copy. `newConnection` configures protobuf RPC engine, retry policy, socket, SASL if needed, optional `FederationConnectionId`, translator client, and token service, then wraps it in `ConnectionContext`.

Dependencies and integration points: Hadoop IPC/RPC, protobuf translators, `ClientProtocol`, `NamenodeProtocol`, refresh/get-user-mapping protocols, UGI/tokens, retry config, and alignment context.

Risks: `newProtoClient` can return null after logging, producing a `ConnectionContext` with a null client if not guarded by caller. Copy-on-write list avoids iterator locking but callers can observe stale snapshots. Unsupported protocols throw `IllegalStateException`. Multi-socket identity depends on incrementing socket index.

Test signals: protocol mapping, min connection creation, round-robin fallback, copy-on-write add/remove, only idle removals, multi-socket connection IDs, security-enabled SASL path, and JSON/debug counters.
