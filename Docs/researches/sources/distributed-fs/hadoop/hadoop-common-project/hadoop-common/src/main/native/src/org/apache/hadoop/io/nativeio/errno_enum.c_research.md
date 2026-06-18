<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/errno_enum.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/errno_enum.c

## Purpose
`errno_enum.c` maps native errno integer values to Hadoop's Java `Errno` enum for `NativeIOException`.

## Important APIs, Types, and Functions
It defines `errno_mapping_t`, static `ERRNO_MAPPINGS`, `errno_enum_init()`, `errno_enum_deinit()`, internal `errno_to_string()`, and public `errno_to_enum()`.

## Control Flow
Initialization caches global references to `java.lang.Enum` and Hadoop `Errno`, plus the static `Enum.valueOf(Class,String)` method. `errno_to_enum()` converts an errno integer to a string name, creates a Java string, and invokes `Enum.valueOf` to obtain the enum constant. Unrecognized errno values map to `"UNKNOWN"`.

## State and Persistence
Global class refs and method ID persist between init and deinit. The mapping table is static read-only data.

## Dependencies and Integration Points
It is initialized from `NativeIO.c` and used by `throw_ioe()` to construct Java `NativeIOException` with an enum errno value.

## Risks and Edge Cases
Only a subset of errno values is listed. If Java `Errno.UNKNOWN` is missing, unknown native errors will create a pending Java exception. Platform-specific errno names may not exist on all Unix variants, depending on headers and enum definitions.

## Test Signals
Tests should verify common errno values, unknown errno mapping, initialization/deinitialization idempotence, and Java enum consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/errno_enum.c -->
