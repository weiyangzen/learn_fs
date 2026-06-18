<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/set-replication-state.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/set-replication-state.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/set-replication-state.h` declares `SetReplicationState`, the shared state used by `hdfs_setrep` while applying replication changes across a recursive listing. The source was read as a complete 72-line file for this report.

## Important APIs, Types, and Functions

`SetReplicationState` stores the target `replication`, a completion handler, `request_counter`, `find_is_done`, final `hdfs::Status`, and a mutex. The constructor initializes these values for the callback fan-out in `hdfs-setrep.cc`.

## Control Flow

The struct supports the flow where `Find` discovers files, each file schedules async `SetReplication`, and the final handler runs only after listing is complete and all outstanding replication calls have returned.

## State and Persistence Behavior

State is in-memory and lasts only for one command invocation. HDFS persists the replication factor changes; this struct only coordinates callback completion.

## Dependencies and Integration Points

It integrates `<functional>`, `<mutex>`, and libhdfs++ status types with `FileSystem::Find` and `FileSystem::SetReplication` callbacks.

## Risks and Edge Cases

Counter underflow, missing locking, or invoking the final handler more than once would break command completion. Large directory trees can create many outstanding requests.

## Test Signals

Tests should cover empty trees, directory-only trees, mixed file/directory trees, first-error preservation, and asynchronous callback reordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/set-replication-state.h -->
