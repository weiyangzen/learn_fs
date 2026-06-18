<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/InnerNodeImpl.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/InnerNodeImpl.java

## Purpose
`InnerNodeImpl` is the default in-memory implementation of `InnerNode`, representing non-leaf network topology nodes such as racks or switches.

## Important APIs and Types
It extends `NodeBase` and implements `InnerNode`. Important members are ordered `children`, lookup `childrenMap`, `numOfLeaves`, static `FACTORY`, constructors, `isRack`, `isAncestor`, `isParent`, `getNextAncestorName`, `add`, `remove`, `getLoc`, and `getLeaf`.

## Control Flow
`add` verifies the new node is a descendant. If this node is the direct parent, it sets parent/level and inserts or replaces the child. Otherwise it finds or creates the next inner ancestor and delegates. `remove` mirrors this traversal, pruning empty intermediate parents and decrementing leaf counts. `getLoc` recursively follows path segments. `getLeaf` walks ordered children, adjusting indices for an excluded leaf or subtree.

## State and Persistence
The topology tree is mutable in memory. Child ordering is preserved in `children`; fast lookup is mirrored in `childrenMap`; leaf counts are manually maintained.

## Dependencies and Integration Points
Network topology management uses this tree to store data nodes and select leaves for placement. It relies on `NodeBase` path, level, parent, and separator conventions.

## Risks and Test Signals
`getLeaf` casts children to `InnerNodeImpl` in non-rack mode, so mixed custom inner implementations can fail. Replacing a direct child returns false and does not update `numOfLeaves`, which is intentional for replacement. Tests should cover path-derived parent creation, duplicate replacement, subtree pruning, leaf count correctness, rack detection, exclusion by leaf/subtree, invalid ancestor errors, and path lookup edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/InnerNodeImpl.java -->
