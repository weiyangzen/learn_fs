# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/Node.java

Purpose: defines the minimal contract for entries in Hadoop's network topology tree. Leaves usually represent data nodes, while inner-node implementations represent data centers, racks, or node groups.

Important APIs/types/functions: `getNetworkLocation`, `setNetworkLocation`, `getName`, `getParent`, `setParent`, `getLevel`, and `setLevel`.

Control flow: this is an interface only. Tree mutations are driven by `InnerNode`/`NetworkTopology` implementations, which set parent and level while adding or removing nodes.

State and persistence: no state directly. Implementations are mutable, so callers must treat network location, parent, and level as topology-managed fields once inserted.

Dependencies and integration: implemented by `NodeBase` and inner-node classes. Used pervasively in topology distance, scope, sorting, and rack membership code.

Risks: because setters are public, external mutation can invalidate `NetworkTopology` invariants, cached map keys, and parent/level-based distance calculations.

Test signals: indirectly covered by `NodeBase`, `NetworkTopology`, and nodegroup tests.
