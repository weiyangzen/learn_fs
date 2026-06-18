<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/cancel_tracker.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/cancel_tracker.h

## Purpose
Declares `CancelTracker` and the `CancelHandle` alias used to share cancellation state across asynchronous HDFS operations.

## Important APIs, Types, And Functions
`CancelTracker` derives from `enable_shared_from_this`, has `New()`, `set_canceled()`, and `is_canceled()`. `CancelHandle` is `std::shared_ptr<CancelTracker>`.

## Control Flow
Owners allocate a tracker and hand shared pointers to continuations, readers, or file handles. Consumers poll the flag before scheduling the next action.

## State And Persistence
State is an atomic cancellation bit. There is no reset API and no external persistence.

## Dependencies And Integration Points
This header is included by continuation and file-handle code and forms the cancellation contract for async operations.

## Risks
The class exposes no reason or generation counter, so reusing a canceled handle for a new operation will immediately cancel it. `enable_shared_from_this` is unused here but implies shared ownership assumptions.

## Test Signals
Compile and concurrency tests should confirm the shared handle can be passed through async code and cancellation is observed without data races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/cancel_tracker.h -->
