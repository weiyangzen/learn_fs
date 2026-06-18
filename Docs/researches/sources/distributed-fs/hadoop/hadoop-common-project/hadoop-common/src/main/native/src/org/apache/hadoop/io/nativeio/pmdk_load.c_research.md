<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/pmdk_load.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/pmdk_load.c

## Purpose
`pmdk_load.c` dynamically loads libpmem/PMDK symbols used by NativeIO persistent-memory support.

## Important APIs, Types, and Functions
It defines global `PmdkLibLoader *pmdkLoader` and `int pmdkLoaded`, internal `load_functions()`, and public `load_pmdk_lib()`. Resolved symbols are `pmem_map_file`, `pmem_unmap`, `pmem_is_pmem`, `pmem_drain`, `pmem_memcpy_nodrain`, and `pmem_msync`.

## Control Flow
`load_pmdk_lib()` clears the error buffer, returns early when already loaded, allocates the loader if necessary, opens `HADOOP_PMDK_LIBRARY`, resolves required functions, discovers the actual library path with `dladdr`, stores a duplicated library name, and marks `pmdkLoaded`.

## State and Persistence
The loader, library handle, function pointers, library name, and loaded flag persist process-wide. The file never unloads libpmem.

## Dependencies and Integration Points
It is used by `NativeIO.c` when `HADOOP_PMDK_LIBRARY` is compiled in, enabling PMDK map/copy/sync JNI methods.

## Risks and Edge Cases
If `dlopen` fails after allocating `pmdkLoader`, later calls can retry because `pmdkLoaded` remains unset, but the partially allocated loader remains. Allocation is not checked. `pmdkLoaded` is not synchronized, so concurrent initialization could race. Windows branches reference `GetModuleFileName` despite the header primarily defining Unix symbol types.

## Test Signals
Tests should cover PMDK absent/present states, missing symbols, repeated load calls, concurrent initialization, and NativeIO PMDK method behavior after load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/pmdk_load.c -->
