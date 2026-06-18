<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_code.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_code.h

## Purpose
`erasure_code.h` declares ISA-L-compatible erasure-code table generation and encoding interfaces used by Hadoop's native RS implementation.

## Important APIs, Types, and Functions
The public functions are `h_ec_init_tables()`, `h_ec_encode_data()`, and `h_ec_encode_data_update()`. They operate on GF(2^8) coefficient tables, source pointer arrays, and coding-output pointer arrays.

## Control Flow
The header documents expected call order: generate tables with `h_ec_init_tables()` from coding coefficients, then pass those tables to full or incremental encoding routines.

## State and Persistence
No state is declared. The caller owns coefficient arrays, generated `gftbls`, source buffers, and output buffers.

## Dependencies and Integration Points
It is consumed by `erasure_coder.c` and backed by `erasure_code.c` delegation into dynamically loaded ISA-L functions.

## Risks and Edge Cases
The API assumes callers provide table storage of `32 * k * rows` bytes and valid source/output pointer arrays. Incorrect dimensions or missing ISA-L initialization can cause memory corruption or crashes.

## Test Signals
Known-answer RS parity tests, decode/recovery tests, table-size checks, and address-sanitized invalid-dimension tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_code.h -->
