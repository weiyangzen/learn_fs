<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/isal_load.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/isal_load.h

## Purpose
`isal_load.h` declares the ISA-L dynamic loader structure, symbol typedefs, loading macros, and public loader functions.

## Important APIs, Types, and Functions
`IsaLibLoader` stores the loaded library handle, library name, GF function pointers, and erasure-code function pointers. `EC_LOAD_DYNAMIC_SYMBOL` abstracts `dlsym`/`GetProcAddress`. Public functions are `build_support_erasurecode()` and `load_erasurecode_lib()`.

## Control Flow
The header's macros return an error string from the caller when a symbol cannot be resolved. Platform branches define compatible function pointer calling conventions.

## State and Persistence
It declares external global `isaLoader`, which persists after initialization in `isal_load.c`.

## Dependencies and Integration Points
It is included by wrapper files (`gf_util.c`, `erasure_code.c`, `jni_common.c`) and binds them to dynamic ISA-L symbols without direct library linkage.

## Risks and Edge Cases
The symbol-loading macro relies on a local `isaLoader` global and a caller returning `const char *`; misuse in other function shapes would be unsafe. Build support is controlled by `HADOOP_ISAL_LIBRARY`, so compile-time and runtime availability can diverge.

## Test Signals
Cross-platform compile tests, symbol-resolution failure tests, and Java load-library behavior validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/isal_load.h -->
