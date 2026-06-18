<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/cancel_tracker.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/cancel_tracker.cc

## Purpose
Implements `CancelTracker`, the shared cancellation flag used by asynchronous continuation pipelines and file read operations.

## Important APIs, Types, And Functions
The implementation provides the constructor, `CancelTracker::New()`, `is_canceled()`, and `set_canceled()`.

## Control Flow
Users create a shared tracker, pass it into asynchronous pipelines or readers, and call `set_canceled()` when the owning operation should stop. Pipelines poll `is_canceled()` between stages and convert cancellation into `Status::Canceled()`.

## State And Persistence
The only state is an `std::atomic_bool canceled_`, initialized false and flipped true permanently for a tracker instance. It is in-memory and safe for concurrent polling.

## Dependencies And Integration Points
Used by `continuation::Pipeline`, `FileHandleImpl`, and block readers to coordinate logical cancellation with socket close/cancel behavior.

## Risks
Cancellation is cooperative except where callers also close sockets. Long-running stages that do not check the flag will continue until their callback boundary.

## Test Signals
Tests should verify initial false state, one-way true transition, visibility across threads, and pipeline/file-read completion with `Status::Canceled()` after cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/cancel_tracker.cc -->
