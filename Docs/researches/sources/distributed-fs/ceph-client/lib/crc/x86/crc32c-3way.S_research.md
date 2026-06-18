# sources/distributed-fs/ceph-client/lib/crc/x86/crc32c-3way.S

## Purpose
This x86_64 assembly file computes CRC32C for long buffers by running three parallel scalar CRC32 streams and combining them with PCLMULQDQ.

## Important APIs, Types, and Functions
It defines `SYM_FUNC_START(crc32c_x86_3way)`, constants such as `SMALL_SIZE`, and the `K_table` of PCLMUL combination constants.

## Control Flow
The function routes buffers below `SMALL_SIZE` to a simple scalar CRC32 path. Larger buffers are aligned to 8 bytes, split into three equal lanes of qwords, processed with unrolled `crc32q` streams, then combined using two PCLMUL multiplications and an XOR with the third lane. It repeats for full and partial blocks, then finishes remaining qword/dword/word/byte tails with scalar CRC32 instructions.

## State and Persistence
All mutable state is in registers. `K_table` is immutable read-only data.

## Dependencies and Integration Points
It depends on x86_64, SSE/PCLMUL availability, and is called by `crc32c_arch()` only inside a kernel FPU section when long-buffer conditions are met.

## Risks and Test Signals
Risks include lane-length arithmetic, table indexing by chunk size, alignment prologue bugs, and PCLMUL state assumptions. Long-buffer CRC32C KUnit tests and comparisons across the scalar/PCLMUL threshold validate it.
