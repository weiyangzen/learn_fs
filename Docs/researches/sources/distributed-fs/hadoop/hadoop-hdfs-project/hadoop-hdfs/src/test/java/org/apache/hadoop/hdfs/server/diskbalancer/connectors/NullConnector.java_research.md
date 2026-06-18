# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/NullConnector.java

## Purpose
`NullConnector` is a minimal in-memory `ClusterConnector` implementation for DiskBalancer tests. It lets tests assemble a synthetic cluster by directly adding `DiskBalancerDataNode` instances without reading from NameNode RPCs, JSON, or other persistent sources.

## Important APIs, Types, and Functions
- `NullConnector implements ClusterConnector`.
- `private final List<DiskBalancerDataNode> nodes = new LinkedList<>()` stores the mutable in-memory cluster.
- `getNodes()` returns the backing list directly.
- `getConnectorInfo()` returns a fixed human-readable description identifying no persistence.
- `addNode(DiskBalancerDataNode node)` appends a node to the backing list.

## Control Flow and Behavior
There is no initialization or external discovery. Test code creates the connector, calls `addNode` for each synthetic node, and consumers call `getNodes` to read the same list. Returning the backing list means callers can observe all additions and can also mutate the connector state indirectly.

## State and Persistence
All state is process-local and in memory. There is no serialization, snapshotting, validation, synchronization, or defensive copying. The connector lifetime and data lifetime are the same Java object lifetime.

## Dependencies and Integration Points
The class depends only on DiskBalancer's `ClusterConnector` interface and `DiskBalancerDataNode` model type plus standard Java `List`/`LinkedList`. It integrates with `DiskBalancerCluster` or planner tests that need a connector-shaped source of nodes.

## Risks and Edge Cases
- `getNodes()` exposes the mutable list; callers can clear, reorder, or add invalid/null nodes.
- `addNode` accepts null and duplicates unless callers prevent them.
- `LinkedList` plus no synchronization makes this unsuitable for concurrent mutation.
- Because it is test-only, lack of persistence and validation is intentional but should not be copied into production connectors.

## Test Signals
Useful tests would confirm nodes added via `addNode` are returned by `getNodes`, that connector info is stable, and that DiskBalancer components can consume the connector without external cluster dependencies. Existing coverage is likely indirect through DiskBalancer data-model and planner tests.
