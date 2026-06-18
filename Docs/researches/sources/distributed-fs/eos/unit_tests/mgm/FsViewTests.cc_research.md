# sources/distributed-fs/eos/unit_tests/mgm/FsViewTests.cc

## Purpose
Tests MGM filesystem view support classes: geo-tree iteration, FsView reset cleanup, filesystem UUID mapping, filesystem config parsing/joining/relocation, balancer stats, and random vector iterator selection.

## Important APIs, types, and functions
Coverage includes `GeoTree`, `FsView::Reset`, `FsNode::sNumInstances`, `FilesystemUuidMapper`, `ConfigParsing::parseFilesystemConfig`, config join/relocate helpers, `FsBalancerStats::UpdateInfo`, `FsView::GetUnbalancedGroups`, and `FsBalancer::GetRandomIter`.

## Control flow
Tests populate trees and maps, assert duplicate rejection and iterator boundary behavior, directly inject `FsNode` pointers into `mNodeView` to verify reset deletes nodes, parse realistic filesystem config strings, relocate filesystem queue/path entries, and build synthetic balancing groups to validate unbalanced group counts under threshold changes.

## State and persistence
State is local test data plus static `InstanceName` and `FsNode::sNumInstances`. Config parsing outputs are transient but model persisted MGM configuration entries.

## Dependencies and integration points
Depends on Google Test/Mock, FsView, balancer classes included under `IN_TEST_HARNESS`, filesystem UUID mapper, config parsing, and string utilities.

## Risks and test signals
The reset leak regression is a strong lifecycle signal. Risks include direct access to internals, manual deletion of synthetic groups, and random iterator tests that cannot guarantee full distribution. Additional tests should cover concurrent FsView reset and malformed config strings.
