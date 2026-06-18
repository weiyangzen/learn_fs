# sources/distributed-fs/eos/mgm/geotree/SchedulingSlowTree.hh

## Purpose
`SchedulingSlowTree.hh` declares the flexible, mutable geotag tree used to assemble scheduling groups before producing compact fast trees. It models filesystem leaves under hierarchical geotag atoms and offers display, mutation, and fast-structure build APIs.

## Important APIs, Types, And Functions
`SlowTreeNode` derives from `SchedTreeBase` and is friend to `SlowTree`, `GeoTreeEngine`, and fast-structure helpers. It stores `pFather`, `pChildren`, `pLeavesCount`, `pNodeCount`, `pNodeInfo`, and `pNodeState`. Public methods are `writeFastTreeNodeTemplate`, `display`, `recursiveDisplay`, and `recursiveDisplayAccess`; protected helpers recursively destroy children and update leaf counts.

`SlowTree` owns a root node and total node count. Public APIs include constructors, `setName`, `getName`, `insert`, `remove`, `moveToNewGeoTag`, `getNodeCount`, `display`, `displayAccess`, `buildFastStrcturesSched`, `buildFastStructuresGW`, `buildFastStrcturesAccess`, and the declared `allocateAndBuildFastTreeTemplate`. The private recursive `insert` performs atom-by-atom construction.

## Control Flow
Users create a `SlowTree` per scheduling group, insert filesystem records as `TreeNodeInfo` plus `TreeNodeStateFloat`, optionally include fs-id as the final geotag level, then call a build method to emit fast trees. Display methods traverse the tree and collect table rows, while build methods flatten it into the branch/node layout used by `FastTree`. The root is initialized as an intermediate node with the group id as geotag and node count one.

## State And Persistence
The state is owned in memory by the tree. Children are raw pointers stored in `std::map<std::string, SlowTreeNode*>`; the node destructor deletes subtrees. Counts are cached to size fast structures and initialize free slots. There is no persistent storage in this header; persistence of scheduler configuration and source filesystem metadata is handled in `GeoTreeEngine`, `FsView`, and MGM config infrastructure.

## Dependencies And Integration Points
The header includes `SchedulingFastTree.hh`, `SchedulingTreeCommon.hh`, and `common/table_formatter/TableFormatterBase.hh`. It is the bridge between general EOS filesystem metadata and fast scheduling trees. `GeoTreeEngine` is a friend and can access internals for efficient refreshes and migration workflows.

## Risks And Edge Cases
The API uses raw pointers for input info/state and for tree children, so callers must pass valid objects and avoid sharing deleted nodes. `moveToNewGeoTag` only works for leaves. `pNodeCount` and `pLeavesCount` are cached invariants; incorrect update paths corrupt fast-tree sizing and scheduling slots. The header declares `allocateAndBuildFastTreeTemplate`, but no implementation is present in the researched `.cc`, so callers should not rely on it unless implemented elsewhere or removed. Include order is delicate because this header includes the fast tree while also defining classes that fast tree declares as friends.

## Test Signals
Focused tests should verify default and named construction, root naming, insertion with and without fs-id levels, duplicate insert behavior with `allowUpdate`, removal of leaves and branch collapse, display row generation, gateway access display rows, and all fast-structure build variants. Tests should also assert `getNodeCount()` against expected geotag shapes.
