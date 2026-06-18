<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util_c.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util_c.h

## Purpose
Declares the C ABI wrapper for shutting down the protobuf library from C or mixed-language consumers.

## Important APIs, Types, And Functions
`ShutdownProtobufLibrary_C()` is declared inside `extern "C"` when compiled as C++.

## Control Flow
The implementation in `util.cc` calls `google::protobuf::ShutdownProtobufLibrary()`.

## State And Persistence
Calling the function mutates protobuf process-global state; the header itself stores no state.

## Dependencies And Integration Points
Used by C-facing libraries or tests that need an unmangled shutdown hook.

## Risks
The function should only be called when no protobuf messages/descriptors are still in use. Repeated or premature calls can break later protobuf operations in the same process.

## Test Signals
C and C++ link tests should verify symbol visibility; integration tests should call it only at process teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util_c.h -->
