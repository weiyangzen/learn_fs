# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/ConnectionPoolId.java

Purpose: identity key for a Router connection pool, combining Namenode address, UGI, UGI token IDs, and protocol.

Important APIs and state: constructor caches `ugi.toString()` because it is expensive. `hashCode`, `equals`, `compareTo`, and `toString` include sorted token identifier byte arrays. `getUgi` is visible for testing.

Control flow and persistence: immutable identity object. Token IDs are recomputed on each hash/equality/compare call from current UGI tokens, while the UGI string is cached.

Dependencies and integration points: keys the `ConnectionManager` pool map and JSON output.

Risks: because token IDs are read dynamically, mutating UGI tokens after insertion can change hash/equality behavior and break map lookup. `equals` compares token list string forms while `hashCode` appends the list object; both use sorted contents but rely on consistent conversion.

Test signals: equality/hash/compare with same user/address/protocol, differing tokens, token order independence, and mutation risk if UGI tokens change after construction.
