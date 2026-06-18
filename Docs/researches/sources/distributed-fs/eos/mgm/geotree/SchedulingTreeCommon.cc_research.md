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
