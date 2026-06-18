# sources/distributed-fs/ceph-client/lib/crc/riscv/crc-clmul-consts.h

## Purpose
This generated header supplies RISC-V scalar carryless-multiply constants for CRC-16/T10DIF, CRC-32 IEEE, CRC-32C, CRC-64 ECMA, and CRC-64 NVMe. It is data-only support for the Zbc-based template in `crc-clmul-template.h`.

## Important APIs, Types, and Functions
The central type is `struct crc_clmul_consts` with two fold-across-two-longs constants and two Barrett reduction constants. It defines `crc16_msb_0x8bb7_consts`, `crc32_msb_0x04c11db7_consts`, `crc32_lsb_0xedb88320_consts`, `crc32_lsb_0x82f63b78_consts`, and, under `CONFIG_64BIT`, `crc64_msb_0x42f0e1eba9ea3693_consts` and `crc64_lsb_0x9a6c9329ac4bc9b5_consts`.

## Control Flow
There is no executable flow. Including CRC headers pass the relevant constant object into `crc*_clmul()` functions. The values differ for 32-bit and 64-bit RISC-V where the long-width fold distances and Barrett constants differ.

## State and Persistence
The constants are static immutable data marked `__maybe_unused` so the compiler can discard variants unused by a given translation unit. No runtime state exists.

## Dependencies and Integration Points
It depends on Linux types/macros and on the generator script contract documented in the header comment. It is included by `crc-clmul.h` and indirectly by RISC-V CRC arch headers.

## Risks and Test Signals
Manual edits would be risky because the constants encode polynomial arithmetic. Test signals include generator reproducibility, 32-bit versus 64-bit build coverage, and randomized CRC KUnit comparisons for all CRC variants that reference the table.
