<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/bad_datanode_tracker.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/bad_datanode_tracker.h

## Purpose
Declares the DataNode exclusion interfaces used during block reads.

## Important APIs, Types, And Functions
`ExclusionSet` wraps a fixed `std::set<std::string>` of excluded UUIDs. `BadDataNodeTracker` tracks failed DataNodes with timeout-based eviction and exposes `AddBadNode`, `IsBadNode`, and test clock shifting.

## Control Flow
File read logic supplies either a caller-provided `NodeExclusionRule` or the shared bad-node tracker to DataNode selection.

## State And Persistence
`BadDataNodeTracker` owns a timestamp map and mutex; `ExclusionSet` owns an immutable set. Neither persists to disk.

## Dependencies And Integration Points
Depends on public options and `NodeExclusionRule` declarations from `hdfspp/hdfspp.h`. Integrated with `FileHandleImpl::AsyncPreadSome`.

## Risks
The timeout is fixed at construction, so option changes do not affect existing trackers. Test-only clock shifting is part of the public class surface.

## Test Signals
Tests should cover both dynamic tracker and fixed set behavior through direct calls and through file read DataNode selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/bad_datanode_tracker.h -->
