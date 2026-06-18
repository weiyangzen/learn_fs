<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/new_delete.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/new_delete.h

## Purpose
Defines `MEMCHECKED_CLASS`, a debug-only allocation macro that overwrites object or array memory on delete to help expose use-after-free bugs.

## Important APIs, Types, And Functions
`mem_struct` stores array allocation size. In non-`NDEBUG` builds, `MEMCHECKED_CLASS(clazz)` injects custom scalar and array new/delete operators; release builds expand to nothing.

## Control Flow
Scalar delete zeros `sizeof(clazz)` bytes before freeing. Array new stores size in a prepended header, and array delete recovers the header, zeros the payload, and frees the original allocation.

## State And Persistence
No runtime state is kept beyond per-allocation headers for arrays in debug builds.

## Dependencies And Integration Points
Used by classes such as `IoServiceImpl`, `DataNodeConnection`, and `FileHandleImpl` for debug memory hygiene.

## Risks
Custom allocation operators must remain correctly paired. Scalar delete assumes the object allocation size equals `sizeof(clazz)`, which is true for normal scalar objects but can be risky with inheritance if deleting through a base without a virtual destructor. The macro uses C allocation routines and bypasses standard new-handler behavior.

## Test Signals
Debug ASAN/unit tests should allocate and delete scalar and array instances of memchecked classes and check for allocator mismatches or crashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/new_delete.h -->
