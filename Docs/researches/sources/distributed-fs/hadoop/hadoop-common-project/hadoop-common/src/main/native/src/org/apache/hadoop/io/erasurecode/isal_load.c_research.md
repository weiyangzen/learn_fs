<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/isal_load.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/isal_load.c

## Purpose
`isal_load.c` dynamically loads the Intel ISA-L library and resolves the GF and erasure-code symbols needed by Hadoop native erasure coding.

## Important APIs, Types, and Functions
It defines global `IsaLibLoader *isaLoader`, internal `load_functions()`, public `load_erasurecode_lib()`, and `build_support_erasurecode()`. Resolved symbols include `gf_mul`, `gf_inv`, `gf_gen_rs_matrix`, `gf_gen_cauchy1_matrix`, `gf_invert_matrix`, `gf_vect_mul`, `ec_init_tables`, `ec_encode_data`, and `ec_encode_data_update`.

## Control Flow
`load_erasurecode_lib()` is idempotent if `isaLoader` already exists. Otherwise it allocates the loader, opens `HADOOP_ISAL_LIBRARY`, clears loader errors, resolves all required functions, discovers the actual library path with `dladdr` or Windows APIs, and stores a duplicated library name. Errors are returned through the caller-provided string buffer.

## State and Persistence
The loader, dynamic library handle, function pointers, and library name persist process-wide. The code never frees or unloads the ISA-L library.

## Dependencies and Integration Points
It depends on Hadoop platform config, `dlopen`/`LoadLibrary`, and `isal_load.h`. `jni_common.c` calls it from Java `ErasureCodeNative.loadLibrary()`.

## Risks and Edge Cases
If allocation succeeds but `dlopen` fails, `isaLoader` remains allocated with missing symbols; subsequent calls return early because `isaLoader != NULL`, potentially leaving a permanently broken loader. `calloc` is not checked before `memset`. The function call `load_functions(isaLoader->libec)` passes an argument to a no-argument function in the visible source, which is a compile-time mismatch in strict C. Windows filename handling uses an unallocated `filename` pointer.

## Test Signals
Tests should cover missing ISA-L library, missing individual symbols, repeat load after failure, successful library-name reporting, and encode/decode only after successful load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/isal_load.c -->
