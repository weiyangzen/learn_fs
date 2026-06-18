# sources/distributed-fs/eos/mgm/geotree/SchedulingSlowTree.cc

## Purpose
`SchedulingSlowTree.cc` implements the mutable geotag tree declared in `SchedulingSlowTree.hh` and the conversion from slow trees to fast scheduling structures. It is the build/update side of the geotree scheduler: filesystem metadata is inserted in an easy-to-modify tree, then flattened into compact fast trees for high-volume placement and access operations.

## Important APIs, Types, And Functions
Important node functions are `SlowTreeNode::display`, `recursiveDisplay`, and `recursiveDisplayAccess`. Important tree functions are `SlowTree::insert` overloads, `remove`, `moveToNewGeoTag`, `display`, `displayAccess`, `buildFastStrcturesSched`, `buildFastStructuresGW`, and `buildFastStrcturesAccess`. The build functions populate `FastPlacementTree`, `FastROAccessTree`, `FastRWAccessTree`, `FastDrainingPlacementTree`, `FastDrainingAccessTree`, `FastGatewayAccessTree`, `FastTreeInfo`, `Fs2TreeIdxMap`, `Host2TreeIdxMap`, and `GeoTag2NodeIdxMap`.

## Control Flow
Insertion splits a geotag path on `::`, creates intermediate nodes as needed, appends an optional filesystem-id leaf level, writes file-system metadata/state at the final node, and updates leaf/node counters along the affected ancestors. Removal walks the same atom path, deletes the matching leaf or collapsible branch, subtracts leaf/node counts upward, and deletes the detached subtree. `moveToNewGeoTag()` copies a leaf's info/state, removes it, and reinserts under the new geotag.

Fast-structure building first calls `pRootNode.update()`, then creates a breadth-first node layout. It copies node state into the primary placement or gateway fast tree, writes father and child branch indexes, initializes free/taken slot counters, fills `FastTreeInfo`, and builds an fs-id or host lookup map. Scheduling build then clones the placement tree into RO/RW/draining trees and adjusts initial free-slot state before `updateTree()`. Both scheduling and gateway builders create a second breadth-first layout for `GeoTag2NodeIdxMap`, recording each node's tag, fast-tree index, first child, and child count.

## State And Persistence
The slow tree owns heap-allocated child nodes through `pChildren`; node destruction recursively deletes children. Per-node state includes parent pointers, children maps, leaf counts, node counts, `TreeNodeInfo`, and `TreeNodeStateFloat`. The generated fast structures are separate in-memory snapshots whose external info/id maps are filled by these build routines. No file-backed persistence occurs here.

## Dependencies And Integration Points
The file depends on `SchedulingSlowTree.hh`, `SchedulingFastTree.hh`, `SchedulingTreeCommon.hh`, EOS logging, and table formatter color data for display. `GeoTreeEngine` uses this code while refreshing scheduling groups and proxy/gateway structures from MGM filesystem state. The output maps are consumed by request-time scheduling and administrative display paths.

## Risks And Edge Cases
The build routines require caller-allocated fast trees to be large enough; some undersized cases return false, while zero-sized `geo2node`, `fs2idx`, or `host2idx` maps are self-allocated. Because `std::map` orders children lexicographically, fast-tree branch and geotag-map searches depend on that deterministic ordering. Several sanity checks are `assert`s and may be compiled out. `remove()` erases a child from its parent before subtracting counts by walking from the detached node; this relies on parent pointers remaining valid until deletion. Gateway host strings are copied with fixed `Host2TreeIdxMap` length. The function name `buildFastStrcturesSched` is misspelled but forms an API used by callers.

## Test Signals
Test signals include successful insert/remove/reinsert cycles, moving leaves between geotags, correct leaf/node counts after branch collapse, scheduling build failure on undersized buffers, correct fs-id and geotag lookup maps, gateway host map creation, access build disabling nodes without proxy groups, and `checkConsistency()` on every produced fast tree. The existing test calls insert/remove for every generated filesystem and then builds all scheduling fast-tree variants.
