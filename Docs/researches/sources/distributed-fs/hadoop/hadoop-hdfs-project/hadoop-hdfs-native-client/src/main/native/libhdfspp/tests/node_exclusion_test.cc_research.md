# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/node_exclusion_test.cc

## Purpose

This unit test validates bad datanode tracking and static exclusion sets.

## Important APIs, types, and functions

Tests exercise `BadDataNodeTracker::AddBadNode()`, `IsBadNode()`, `TEST_set_clock_shift()`, and `ExclusionSet::IsBadNode()`.

## Control flow, state, and persistence

`AddBadNode` verifies newly added datanode IDs are marked bad and unrelated IDs are not. `RemoveOnTimeout` adds a node, shifts the test clock far forward, and expects lookup to expire the node. `ExcludeSet` verifies empty and populated immutable exclusion sets. State is in-memory tracker maps/sets only.

## Dependencies and integration points

The file depends on `fs/filesystem.h`, `fs/bad_datanode_tracker.h`, gmock, protobuf shutdown, and standard sets through production headers. It supports file-handle retry behavior by validating the bad-node filter used during block reads.

## Risks and test signals

The timeout test depends on a test-only clock shift hook. These tests catch stale exclusion retention and incorrect set membership. They do not cover concurrent access or integration with actual block read retry paths; `bad_datanode_test.cc` covers some of that.
