<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/gf_util.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/gf_util.h

## Purpose
`gf_util.h` declares Hadoop-prefixed wrappers for ISA-L GF(2^8) utility routines used in erasure coding.

## Important APIs, Types, and Functions
The declared APIs cover scalar multiply/inverse, Reed-Solomon and Cauchy matrix generation, matrix inversion, and vector multiply using a precomputed GF table.

## Control Flow
The header documents call expectations: matrix generators fill coefficient arrays, inversion returns nonzero on singular input, and vector multiply expects precomputed constants and aligned buffers.

## State and Persistence
No state is declared. Callers own all arrays and buffers.

## Dependencies and Integration Points
It provides the matrix and GF contract used by `erasure_coder.c`, backed by `gf_util.c` and `isal_load.c`.

## Risks and Edge Cases
The vector multiply contract requires length and buffers aligned to 32 bytes, which the wrappers do not enforce. Cauchy matrix generation is chosen for invertibility, but invalid dimensions still risk downstream errors.

## Test Signals
Known GF arithmetic, matrix invertibility, 32-byte alignment behavior, and RS recovery tests validate this API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/gf_util.h -->
