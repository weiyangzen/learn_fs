<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_code.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_code.c

## Purpose
`erasure_code.c` is a thin Hadoop wrapper over dynamically loaded ISA-L erasure-code functions. It decouples the rest of the native erasure-code implementation from direct ISA-L linkage.

## Important APIs, Types, and Functions
It implements `h_ec_init_tables()`, `h_ec_encode_data()`, and `h_ec_encode_data_update()`. Each function delegates to the corresponding function pointer in global `isaLoader`.

## Control Flow
There is no algorithmic flow in this file. Callers must ensure `load_erasurecode_lib()` has initialized `isaLoader` before calling these wrappers.

## State and Persistence
The only state touched is external global `isaLoader`, owned by `isal_load.c`. No per-call state is retained.

## Dependencies and Integration Points
It depends on `isal_load.h` and `erasure_code.h`. `erasure_coder.c` uses these wrappers when building parity or recovery outputs.

## Risks and Edge Cases
If `isaLoader` is null or a symbol pointer is missing, calls will crash. There is no local argument validation for dimensions, buffers, or table sizes.

## Test Signals
Tests should load ISA-L successfully before encode/decode calls and verify failure behavior when the library is missing is caught at `loadLibrary`, not at wrapper invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_code.c -->
