# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/FederationConnectionId.java

Purpose: extends Hadoop IPC `Client.ConnectionId` with a socket index so a Router can create multiple distinct physical sockets for the same user/protocol/address.

Important APIs and state: constructor delegates normal connection identity fields to the superclass and stores `index`. `hashCode` appends superclass hash and index; `equals` first requires superclass equality, then requires matching index for another `FederationConnectionId`.

Control flow and persistence: immutable identity object. Used only when multi-socket connection pooling is enabled in `ConnectionPool.newConnection`.

Dependencies and integration points: Hadoop IPC client, retry policy, UGI, configuration, and connection pool socket index.

Risks: equality with a plain superclass `ConnectionId` returns false after superclass equality because the object is not a `FederationConnectionId`, intentionally preventing socket coalescing. Index reuse would collapse sockets.

Test signals: equality/hash differences for different indexes, equality with identical base fields and index, and non-equality against plain `ConnectionId`.
