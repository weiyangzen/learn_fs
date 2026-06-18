<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/libhdfs_events_impl.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/libhdfs_events_impl.h

## Purpose
Declares the `LibhdfsEvents` callback registry used to decouple low-level libhdfspp code from C-facing event hook storage.

## Important APIs, Types, And Functions
The class stores optional `fs_event_callback` and `file_event_callback` values and exposes setter, clearer, and dispatcher overloads.

## Control Flow
Implementation dispatches callbacks and converts exceptions in `libhdfs_events_impl.cc`.

## State And Persistence
State is per-instance optional callback data. No persistence exists.

## Dependencies And Integration Points
Included by C bindings, filesystem/filehandle, DataNode connection, and reader code that emits libhdfspp events.

## Risks
There is no locking in the class declaration, so callback mutation during event emission is unsafe unless guarded externally.

## Test Signals
Compile tests should verify both callback signatures; behavior tests should exercise dispatch through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/libhdfs_events_impl.h -->
