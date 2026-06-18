<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/bad_datanode_tracker.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/bad_datanode_tracker.cc

## Purpose
Implements DataNode exclusion rules used by file reads to avoid recently failed DataNodes and user-specified excluded nodes.

## Important APIs, Types, And Functions
`BadDataNodeTracker` implements `AddBadNode`, `IsBadNode`, `TimeoutExpired`, and `TEST_set_clock_shift`. `ExclusionSet` implements `IsBadNode` over a fixed set. `NodeExclusionRule` has an out-of-line virtual destructor.

## Control Flow
When reads fail with statuses worth excluding, `FileHandleImpl` calls `AddBadNode`. Future `AsyncPreadSome` calls ask `IsBadNode`; if the timestamp has expired, the node is erased and allowed again, otherwise it is skipped. `ExclusionSet` directly checks set membership.

## State And Persistence
`BadDataNodeTracker` stores a mutex-protected map from DataNode UUID to steady-clock insertion time, timeout duration from `Options`, and a test clock shift. State is per tracker and not persisted.

## Dependencies And Integration Points
Used by `FileHandleImpl` DataNode selection. Timeout defaults come from `Options::host_exclusion_duration`; rule interface comes from public `hdfspp.h`.

## Risks
The map is cleaned lazily only when a specific node is queried. `TEST_set_clock_shift` is not synchronized. Exclusion is by UUID, so callers must pass consistent identifiers.

## Test Signals
Tests should mark nodes bad, verify immediate exclusion, shift/advance time to expire entries, test concurrent add/check, and validate `ExclusionSet` with known UUID sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/bad_datanode_tracker.cc -->
