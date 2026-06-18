<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/types_test.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/types_test.h

## Purpose
Defines typed Google Tests for x-platform signed size type compatibility.

## Important APIs, Types, And Functions
`XPlatformTypesTest<T>` is the typed fixture. Registered tests are `SSizeTMinusOne`, `SSizeTCanHoldInts`, and on 64-bit systems `SSizeTCanHoldLongInts`, all using `std::numeric_limits`.

## Control Flow
The header registers typed test patterns; `types_test.cc` instantiates them for `ssize_t`.

## State And Persistence
No mutable state and no persistence.

## Dependencies And Integration Points
Depends on gtest and standard limits. It validates the public x-platform type contract consumed by filesystem and syscall wrappers.

## Risks
Architecture detection uses preprocessor checks for `_WIN64`, `__x86_64__`, and `__ppc64__`; other 64-bit architectures may skip the long-int capacity test.

## Test Signals
Passing tests confirm the signed size type can represent sentinel negative values and expected positive ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/types_test.h -->
