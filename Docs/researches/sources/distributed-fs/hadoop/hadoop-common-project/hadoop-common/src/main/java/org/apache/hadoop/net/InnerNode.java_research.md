<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/InnerNode.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/InnerNode.java

## Purpose
`InnerNode` defines the mutable interior-node contract for Hadoop network topology trees. Interior nodes represent racks, switches, or higher-level topology components and contain children.

## Important APIs and Types
The interface extends `Node`. It declares nested `Factory<N extends InnerNode>`, `add`, `getLoc`, `getChildren`, `getNumOfChildren`, `getNumOfLeaves`, `remove`, and `getLeaf`.

## Control Flow
Implementations must add and remove nodes in subtrees, resolve path-like locations, expose children, count leaves, and return the indexed leaf while optionally excluding a node or subtree.

## State and Persistence
State is implementation-defined but expected to be an in-memory tree. No persistence is implied.

## Dependencies and Integration Points
`InnerNodeImpl` implements this interface, and Hadoop network topology/block placement code traverses it to choose replica locations and count fault domains.

## Risks and Test Signals
The `getLeaf` contract depends on stable child ordering and correct exclusion accounting. Tests for implementations should cover adding/removing leaves and inner nodes, path lookup, leaf counts, excluded leaf and subtree behavior, and factory construction from paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/InnerNode.java -->
