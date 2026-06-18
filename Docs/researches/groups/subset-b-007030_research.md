# subset-b-007030 Research

Grouped code research for EOS MGM geobalancer and geotree scheduling sources. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geobalancer/GeoBalancer.hh -->
# sources/distributed-fs/eos/mgm/geobalancer/GeoBalancer.hh

## Purpose
`GeoBalancer.hh` declares the EOS MGM per-space geo-balancing worker. It exists to reduce large fill-ratio differences between geotags by selecting files from overfilled locations and scheduling converter jobs that will create a replica in another geotag. The header also defines `GeotagSize`, a small capacity/used-bytes accumulator used while deciding whether a geotag is above the configured average.

## Important APIs, Types, And Functions
`GeotagSize` stores `mSize` and `mCapacity` and exposes `usedBytes()`, `setUsedBytes()`, `capacity()`, `setCapacity()`, and `filled()`. `filled()` is the key API: it returns used divided by capacity, and the implementation asserts that capacity is nonzero at construction.

`GeoBalancer` owns an `AssistedThread`, the target space name, a fill threshold, cached maps from geotag to filesystems and filesystem to geotag, cached `GeotagSize*` values, the current average fill ratio, a last-cache-refresh timestamp, and `mTransfers`, which tracks scheduled file ids and conversion proc paths. Public APIs are the constructor, destructor, `Stop()`, and `GeoBalance(ThreadAssistant&) noexcept`. Private helpers declared here cover cache management (`populateGeotagsInfo`, `clearCachedSizes`, `fillGeotagsByAvg`, `cacheExpired`), candidate selection (`chooseFidFromGeotag`, `fileIsInDifferentLocations`, `getFileProcTransferNameAndSize`), transfer scheduling (`prepareTransfer`, `prepareTransfers`, `scheduleTransfer`), and ongoing job cleanup (`updateTransferList`).

## Control Flow
Construction starts the background `GeoBalance` thread for one MGM space. The loop waits for namespace boot, runs only on the master MGM, requires the converter engine to be running, reads the space's `geobalancer`, `geobalancer.ntx`, and `geobalancer.threshold` configuration, refreshes geotag fill caches every `CACHE_LIFE_TIME`, cleans completed transfer records, and schedules up to the configured number of converter jobs. Scheduling chooses an over-average geotag, chooses a random filesystem in that geotag, asks the namespace for an approximately random file, rejects files already spread across locations or already in transfer, then calls the converter engine.

## State And Persistence
The header exposes only in-memory state. Runtime persistence is indirect: scheduled work is handed to `ConverterEngine`, tracked by the global file-id tracker, and represented through conversion proc names. The geotag and capacity caches are intentionally temporary and are cleared/rebuilt from `FsView` snapshots. `mTransfers` is a local guard against duplicate in-flight selections and is refreshed from the converter tracker.

## Dependencies And Integration Points
The class depends on MGM namespace types, `common::FileId`, `common::FileSystem`, `common::AssistedThread`, `XrdSysPthread`, and implementation-side MGM globals such as `gOFS`, `FsView`, namespace metadata services, and `ConverterEngine`. It is created from `FsSpace` handling in `fsview/FsView.cc`, and operational config is stored as MGM space config members. It assumes the converter is enabled and that scattered placement is the default conversion policy.

## Risks And Edge Cases
`mGeotagSizes` stores owning raw pointers, so every cache rebuild must call `clearCachedSizes()` or it leaks. `GeotagSize::filled()` divides by capacity, so zero-capacity snapshots must not be admitted. The worker mutates caches and transfer state from its own thread; integration must ensure no outside thread touches those private maps. Selection is randomized and bounded by attempts, so a heavily filtered geotag can remain over average until a later cycle. File-location comparison relies on the `mFsGeotag` cache; missing fs ids can map to empty strings through `operator[]` if the metadata contains locations absent from the current cache.

## Test Signals
Useful tests should cover construction/destruction and `Stop()`, master/slave gating, disabled converter behavior, empty or missing space views, cache refresh thresholds, per-geotag capacity aggregation, threshold filtering, scheduled transfer cleanup, rejection of files in multiple geotags, rejection of proc files and zero-size/no-location files, and behavior when `ScheduleJob()` fails. Integration tests should configure `geobalancer=on`, `geobalancer.ntx`, and threshold values on an MGM space and verify only over-threshold geotags produce converter jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geobalancer/GeoBalancer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geotree/SchedulingFastTree.hh -->
# sources/distributed-fs/eos/mgm/geotree/SchedulingFastTree.hh

## Purpose
`SchedulingFastTree.hh` implements the compact, high-throughput representation used by EOS MGM geotree scheduling. Slow, mutable geotag trees are converted into these packed arrays so placement, read access, write access, draining, and gateway selection can make repeated scheduling decisions with minimal allocation and cache misses.

## Important APIs, Types, And Functions
`GeoTag2NodeIdxMap` maps hierarchical geotag strings to the closest fast-tree node using sorted child ranges and recursive binary search over geotag atoms. `FsId2NodeIdxMap<T>` maps filesystem ids to fast-tree node indexes; the `char*` specialization maps host strings for gateway lookup. Public aliases include `Fs2TreeIdxMap` and `Host2TreeIdxMap`.

Comparator and random-weight functors define scheduling policy: `PlacementPriorityComparator`, `DrainingPlacementPriorityComparator`, `ROAccessPriorityComparator`, `RWAccessPriorityComparator`, `DrainingAccessPriorityComparator`, and `GatewayPriorityComparator`, plus placement/access/gateway weight evaluators. The main template `FastTree<FsDataMemberForRand, FsAndFileDataComparerForBranchSorting, FsIdType>` stores `FastTreeNode` and `FastTreeBranch` arrays. Important methods include `selfAllocate`, `copyToBuffer`, `copyToFastTree`, `updateTree`, `updateBranch`, `sortBranchesAtNode`, `findFreeSlot`, `findFreeSlotFirstHit`, `findFreeSlotSkipSaturated`, `findFreeSlotsAll`, `decrementFreeSlot`, `disableNode`, `disableSubTree`, `checkConsistency`, and display helpers. Final typedefs instantiate placement, access, draining, and gateway trees.

## Control Flow
After `SlowTree` fills `pNodes` and `pBranches`, `updateTree()` recursively sorts every node's child branches, aggregates filesystem state upward, and aggregates file slot state upward. A placement/access operation starts at a chosen node, follows the highest-priority child branch, randomly chooses among equal-priority branches using score-derived weights, and lands on a valid leaf. When `decrFreeSlot` is true, `decrementFreeSlot()` updates leaf slot counts and walks ancestors, reordering only the modified branch with either the optimized highest-priority path or the general binary-rank/memmove path. `findFreeSlotsAll()` enumerates all valid free leaves under a subtree, optionally walking upward to a root. `findFreeSlotSkipSaturated()` explores priority levels while skipping leaves below score thresholds.

## State And Persistence
The fast tree is a mutable in-memory scheduling snapshot. Shape is fixed after build: node and branch arrays are contiguous, while file slot counters, aggregated score fields, status flags, and branch order mutate per working copy. `copyToBuffer()` supports thread-local or stack-local working copies for request handling, so scheduling can consume slots without changing the shared baseline. External metadata such as node info and id maps is referenced through pointers owned by surrounding geotree structures.

## Dependencies And Integration Points
This header depends on `SchedulingTreeCommon.hh` for state, status, comparators, and base types; on `common/utils/RandUtils.hh` for random selection; and on EOS logging. `SlowTree` and `GeoTreeEngine` are friends and populate private arrays directly. `GeoTreeEngine` uses the aliases to implement file placement, read/write replica access, draining workflows, gateway selection, disabled branches, and geotag proximity lookup.

## Risks And Edge Cases
The implementation uses raw byte allocation, pointer casting, `memcpy`, and `memmove`, so size/layout assumptions are critical. `tFastTreeIdx` is `uint16_t`; trees larger than 65535 nodes cannot be represented. `GeoTag2NodeIdxMap` truncates atoms to a small fixed tag buffer, so long geotag atoms can collide. `FsId2NodeIdxMap<T>::selfAllocate()` allocates `char[]` and later deletes through a `T*`, which is unsafe for non-char types. `findFreeSlotSkipSaturated()` declares `bool localvisited[(256)^sizeof(tFastTreeIdx)]`; `^` is bitwise XOR, not exponentiation, so the array is far smaller than the maximum tree size and can be overrun on larger trees. Many invariants are enforced only by `assert`, which may disappear in release builds.

## Test Signals
The companion test exercises construction from slow trees, placement/access round trips, closest-geotag lookup, draining placement/access, copy speed, slot decrement/repopulation, branch updates, full-tree updates, and rebuild speed. Additional high-value tests should cover saturated-node skipping on trees larger than 258 nodes, long geotag atoms, zero score weights, empty maps, disabled subtrees, capacity overflow in counters, and copy/use of every concrete typedef.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geotree/SchedulingFastTree.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geotree/SchedulingSlowTree.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geotree/SchedulingSlowTree.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geotree/SchedulingSlowTree.hh -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geotree/SchedulingSlowTree.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geotree/SchedulingTreeCommon.cc -->
# sources/distributed-fs/eos/mgm/geotree/SchedulingTreeCommon.cc

## Purpose
`SchedulingTreeCommon.cc` provides the non-template definitions for shared geotree scheduling types. Its main role is to define global debug/check settings and stream formatting for node metadata and fast-tree info arrays.

## Important APIs, Types, And Functions
The file defines `SchedTreeBase::Settings SchedTreeBase::gSettings = {0, 0}`. It implements `SchedTreeBase::TreeNodeInfo::display(std::ostream&) const`, printing node type, geotag, full geotag, filesystem id, and host. It also implements `operator<<(std::ostream&, const SchedTreeBase::FastTreeInfo&)`, iterating the metadata vector and printing index-to-node-info mappings.

## Control Flow
There is no scheduling algorithm here. Display calls format one node or iterate all `FastTreeInfo` entries. Debug/check levels are initialized before tree instances copy them through the `SchedTreeBase` constructor.

## State And Persistence
The only stored state is process-local static `gSettings`, which controls default debug and consistency-check levels for future `SchedTreeBase` instances. Stream output is transient. No scheduler tree state is persisted here.

## Dependencies And Integration Points
The file includes `SchedulingTreeCommon.hh` and `<iomanip>`, uses `EOSMGMNAMESPACE_BEGIN`, and is linked wherever non-template common geotree symbols are needed. `SchedulingTreeTest.cc` mutates `SchedTreeBase::gSettings` before constructing trees to enable consistency checks and debug behavior.

## Risks And Edge Cases
`TreeNodeInfo::display()` has manual formatting and no escaping, so host/geotag strings with delimiters or newlines would produce ambiguous logs. Global settings are mutable static state and are not synchronized; changing them while trees are being constructed in multiple threads would produce inconsistent per-instance debug/check levels. The `operator<<` implementation is safe for normal vectors but can generate large logs for large trees.

## Test Signals
Tests should cover formatted output for intermediate, filesystem, and unknown node types; vector index printing in `FastTreeInfo`; and default `gSettings` values. Integration tests can enable check/debug levels before tree construction and verify assertions/logging paths are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geotree/SchedulingTreeCommon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geotree/SchedulingTreeCommon.hh -->
# sources/distributed-fs/eos/mgm/geotree/SchedulingTreeCommon.hh

## Purpose
`SchedulingTreeCommon.hh` defines the shared data model and scheduling comparison primitives for EOS geotree slow and fast trees. It centralizes status flags, node metadata, compact node state, file slot counters, debug/check macros, and comparator helpers used by placement, access, draining, and gateway trees.

## Important APIs, Types, And Functions
`SchedTreeBase` owns global `Settings`, per-instance debug/check levels, and `tFastTreeIdx`, currently `uint16_t`. `TreeNodeInfo` describes either an intermediate geotag node or filesystem leaf with geotag, full geotag, host, hostport, proxygroup, sticky depth, fs id, and network speed class. `tStatus` defines `Drainer`, `Draining`, `Balancing`, `Available`, `Readable`, `Writable`, `Disabled`, `All`, and `None`. `TreeNodeState<T>` stores status, upload/download scores, total space, writable space, and fill ratio. `TreeNodeSlots` stores free/taken slots and aggregate score statistics. `TreeNodeStateFloat::writeCompactVersion()` converts float state to char state for fast trees.

The key static comparison helpers are `comparePlct`, `compareDrnPlct`, `compareAccessRO`, `compareAccessRW`, `compareAccessDrain`, and `compareGateway`, plus status string formatters. `FastTreeInfo` is a `std::vector<TreeNodeInfo>` storing out-of-band metadata for fast-tree nodes.

## Control Flow
The comparator helpers implement lexicographic scheduling priority. Placement first rejects disabled or non-available/non-writable nodes, requires free slots and space, applies fill-ratio cap, prefers fewer existing replicas, then prefers lower fill ratio within tolerance. Draining placement additionally requires `Drainer`. RO/RW/draining access require readable/RW or draining-compatible status and free slots. Gateway selection requires available and not disabled. These helpers are called by comparator functors in `SchedulingFastTree.hh`, which then sort branch arrays and choose random weighted branches among equal priorities.

## State And Persistence
Common state is entirely in memory. `TreeNodeInfo` is copied into slow nodes and fast-tree info arrays. `TreeNodeStateFloat` reflects live filesystem metrics before compaction; `TreeNodeStateChar` is the fast-tree state used for scheduling. `gSettings` persists for the process lifetime and seeds new `SchedTreeBase` objects.

## Dependencies And Integration Points
The header depends on STL containers/streams, `common/FileSystem.hh`, MGM namespace macros, and EOS logging. It is included by both slow and fast geotree headers and underlies `GeoTreeEngine` request scheduling, administrative tree display, and scheduling tests.

## Risks And Edge Cases
Compacting float scores and fill ratios to `char` can truncate or wrap values if callers pass values outside the expected range. `tFastTreeIdx` limits maximum nodes; exceeding it silently risks truncation if callers do not check `sGetMaxNodeCount()`. `intermediateStatusToStr()` uses `out = +"Dis"`/`+"Unv"`, which is unusual pointer-unary-plus syntax and should be reviewed for compiler behavior and readability. Placement compares `totalSpace == 0` as a headroom proxy, so upstream state computation must set this consistently. Many comparator inputs are raw pointers and assume non-null valid fast-tree nodes.

## Test Signals
Unit tests should directly exercise each comparator with disabled, unavailable, no-slot, no-space, fill-cap, replica-count, and fill-tolerance combinations. Additional tests should cover status string formatting, float-to-char compaction boundaries, `sGetMaxNodeCount()`, and `TreeNodeInfo` display. Integration coverage comes from slow-to-fast build and scheduler placement/access tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geotree/SchedulingTreeCommon.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geotree/SchedulingTreeTest.cc -->
# sources/distributed-fs/eos/mgm/geotree/SchedulingTreeTest.cc

## Purpose
`SchedulingTreeTest.cc` is a standalone test and benchmark harness for the EOS geotree scheduling structures. It validates slow-tree construction, fast-tree generation, placement/access behavior, geotag proximity lookup, gateway proxy access mapping, and performance characteristics for copy, placement, access, update, and rebuild operations.

## Important APIs, Types, And Functions
Important helpers include `PopulateSchedGroupFromFile`, `treeDepthSimilarity`, template `functionalTestFastTree`, `testAccess`, `debugDisplayPlct`, and `debugDisplayAccs`. There are three entry-style functions: the compiled `main()` demonstrates gateway access mapping on a small hand-built tree; `main2()` is another small gateway/saturation experiment; and `mainFull()` is the larger functional and burn-in test using `SchedulingTreeTest.cc.testfile`.

## Control Flow
The active `main()` constructs a slow tree with three nodes, builds a `FastGatewayAccessTree`, prints access mapping and slow-tree tables, then queries several geotags through `GeoTag2NodeIdxMap` and `findFreeSlotFirstHitBack()` to show which proxygroup can serve each geotag. `functionalTestFastTree()` copies placement and access trees into stack buffers, places a random number of replicas, enumerates access replicas, checks placement/access set equality, checks closest geotag lookup, then verifies access selection chooses a placed replica with maximal tree-depth similarity. `mainFull()` parses host/geotag data into scheduling groups, inserts randomized filesystem states, removes/reinserts each item to exercise mutation, builds all fast-tree variants, validates draining and balancing similarity maps, runs functional tests, prints display examples, and runs burn-in speed loops.

## State And Persistence
The test stores all state in process memory: generated scheduling groups, slow trees, fast trees, info vectors, id maps, geotag maps, status counters, and benchmark buffers. Input persistence is limited to the `.testfile` next to the source. Test output is written to stdout/stderr.

## Dependencies And Integration Points
The file includes `SchedulingSlowTree.hh`, EOS logging, string utilities, random utilities, table formatting, and standard containers/streams. It directly instantiates and calls the slow/fast tree APIs used by `GeoTreeEngine`, making it a useful low-level regression harness even though it is not written as a modern unit-test framework.

## Risks And Edge Cases
The active `main()` means `mainFull()` burn-in coverage is not run unless the source is modified or the symbol is invoked differently by a build rule. The tests rely heavily on `assert`, so release builds with `NDEBUG` would normally disable checks, although the file explicitly `#undef NDEBUG` before includes. Randomized data can make failures less reproducible unless RNG seeding is controlled. Fixed stack buffers use `bufferSize = 16384`, so larger trees can fail copy tests because `copyToBuffer()` returns required size. The functional test template casts copied trees to concrete `FastPlacementTree` and `FastROAccessTree` pointers, which matches current call sites but is not fully generic.

## Test Signals
Existing signals include assertion success for placement/access round trips, geotag closest-node identity, nearest-replica access, insert/remove/reinsert, fast-tree consistency, draining placement/access, and fs-id map lookup. Performance output reports placements/sec, copies/sec, repopulation/sec, access/sec, update/sec, and builds/sec. Additional desirable signals would make `mainFull()` part of automated CI, add deterministic RNG seeds, cover saturated skip with large node counts, and check failure paths for undersized buffers/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geotree/SchedulingTreeTest.cc -->
