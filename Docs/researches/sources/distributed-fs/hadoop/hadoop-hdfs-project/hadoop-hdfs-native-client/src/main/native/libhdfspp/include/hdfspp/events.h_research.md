# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/events.h

## Purpose
This header defines stable public event names and callback response types for libhdfs++ filesystem and file instrumentation.

## Important APIs, Control Flow, and State
Stable event constants include NameNode connect/read/write, DataNode connect/read/write, failover, empty endpoint, and pre-RPC retry events. `event_response` represents callback outcomes: OK, caught `std::exception`, caught unknown exception, or testing-only injected `Status`. Factory methods create responses and preserve exception text/status. `fs_event_callback` and `file_event_callback` are `std::function` types returning `event_response`.

## Dependencies and Integration Points
`FileSystem::SetFsEventCallback`, `FileHandle::SetFileEventCallback`, and C monitor APIs in `hdfs_ext.h` use these concepts. Internal RPC and reader code emits events.

## Risks and Test Signals
Callback exceptions must not escape worker threads. Stable event-name compatibility matters for monitoring consumers, while private events may appear. Tests should cover callback success, thrown standard and non-standard exceptions, test error injection, failover event values, and C/C++ monitor bridging.
