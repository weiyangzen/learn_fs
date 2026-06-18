<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/pmdk_load.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/pmdk_load.h

## Purpose
`pmdk_load.h` declares the PMDK dynamic loader structure, function pointer types, symbol-loading macro, and load entry point.

## Important APIs, Types, and Functions
`PmdkLibLoader` stores the library handle, library name, and pointers to required libpmem functions. `PMDK_LOAD_DYNAMIC_SYMBOL` resolves a symbol from `pmdkLoader->libec`. Public API is `load_pmdk_lib()`, and external global `pmdkLoader` is declared.

## Control Flow
The macro returns an error string from the calling loader function when a required symbol cannot be found. The header itself has compile-time Unix branches for libpmem typedefs.

## State and Persistence
It declares `pmdkLoader`, which points to process-wide loader state after initialization.

## Dependencies and Integration Points
It is included by PMDK loader implementation and `NativeIO.c` PMDK operations.

## Risks and Edge Cases
The loader struct field name `libec` is inherited from erasure-code style naming and can obscure that it stores libpmem. Symbol typedefs are only defined under `UNIX`, limiting portability unless guarded by build configuration.

## Test Signals
Builds with and without `HADOOP_PMDK_LIBRARY`, missing-symbol tests, and PMDK map/unmap JNI tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/pmdk_load.h -->
