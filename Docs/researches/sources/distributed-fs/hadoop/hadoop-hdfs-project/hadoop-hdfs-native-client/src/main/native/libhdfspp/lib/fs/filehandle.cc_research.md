<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filehandle.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filehandle.cc

## Purpose
Implements `FileHandleImpl`, the object coordinating reads from one HDFS file, including synchronous reads, positioned reads, DataNode selection, block-reader creation, cancellation, read statistics, and file event callbacks.

## Important APIs, Types, And Functions
Key methods are async and sync `PositionRead`, `Read`, `Seek`, `AsyncPreadSome`, `CancelOperations`, `SetFileEventCallback`, `get_event_handlers`, `get_bytes_read`, `clear_bytes_read`, `CreateBlockReader`, and `CreateDataNodeConnection`. `FileHandle::ShouldExclude` decides whether a failed read should mark a DataNode bad.

## Control Flow
Positioned reads check cancellation, wrap completion to update bad-node tracking and byte counters, and call `AsyncPreadSome`. The synchronous overload bridges async completion through `std::promise`/`future`. Sequential `Read` uses the current offset and advances it on success. `Seek` computes a new offset from beginning/current/end and validates bounds. `AsyncPreadSome` validates EOF/offset/client name, finds the containing located block, picks the first non-excluded DataNode, computes block-relative offset and bounded read size, creates a DataNode connection and block reader, connects, emits events, and starts `AsyncReadBlock`.

## State And Persistence
The handle stores cluster name, path, shared `IoService`, random client name, immutable `FileInfo` with located blocks, shared bad-node tracker, current sequential offset, cancel tracker, `ReaderGroup`, event handlers, and atomic bytes-read counter. State is in-memory per open file; HDFS file data remains remote.

## Dependencies And Integration Points
Depends on block reader, DataNode connection, continuation cancellation, events, logging, generated namenode protobufs, x-platform types, and bad-node tracking. It is wrapped by the C API and created by `FileSystem::Open`.

## Risks
The class comment says most operations are not thread-safe except `PositionRead`, but `offset_` and event handler replacement are unsynchronized. The sync read path blocks until async completion, requiring active `IoService` workers. `AsyncPreadSome` captures iterators/references into `file_info_`; this is safe only because `file_info_` is shared immutable and the lambda owns the shared handle context indirectly through captured objects. It chooses the first available DataNode without locality/rack ranking. Cancellation relies on both a flag and reader socket cancellation.

## Test Signals
Tests should read zero bytes at EOF, reject offsets past EOF, read across block boundaries via repeated calls, seek from all origins, run concurrent positioned reads, simulate DataNode failure and bad-node exclusion, cancel slow reads, verify event callbacks and simulated errors, validate bytes-read statistics, and ensure sync reads complete with active worker threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filehandle.cc -->
