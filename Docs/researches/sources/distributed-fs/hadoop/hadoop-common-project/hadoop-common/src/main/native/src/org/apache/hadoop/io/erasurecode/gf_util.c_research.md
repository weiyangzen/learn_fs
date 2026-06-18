<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/gf_util.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/gf_util.c

## Purpose
`gf_util.c` wraps ISA-L Galois-field utility functions behind Hadoop-prefixed functions.

## Important APIs, Types, and Functions
It implements `h_gf_mul()`, `h_gf_inv()`, `h_gf_gen_rs_matrix()`, `h_gf_gen_cauchy_matrix()`, `h_gf_invert_matrix()`, and `h_gf_vect_mul()`. All delegate directly to function pointers on global `isaLoader`.

## Control Flow
There is no local algorithmic control flow. Calls synchronously invoke the dynamically loaded ISA-L symbol.

## State and Persistence
No state is owned here. It reads the external `isaLoader` global.

## Dependencies and Integration Points
`erasure_coder.c` uses these wrappers to build Cauchy matrices, invert decode matrices, and multiply GF coefficients.

## Risks and Edge Cases
Missing library initialization or unresolved symbols cause null-function-pointer crashes. Caller-provided buffers and matrix dimensions are not validated here.

## Test Signals
Unit tests should verify GF multiply/inverse known values, Cauchy matrix generation, matrix inversion, vector multiply alignment behavior, and missing-library initialization errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/gf_util.c -->
