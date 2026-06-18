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
