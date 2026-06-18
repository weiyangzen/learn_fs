# sources/distributed-fs/ceph-client/lib/crc/riscv/crc-clmul-template.h

## Purpose
This header is a C template that generates RISC-V Zbc scalar carryless-multiply CRC implementations for a caller-selected CRC width and bit order. Including files define `crc_t` and `LSB_CRC`, then get inline helpers plus the `crc_clmul()` engine.

## Important APIs, Types, and Functions
Key helpers are inline wrappers around `clmul`, `clmulh`, and `clmulr`, `crc_load_long()`, `crc_clmul_prep()`, `crc_clmul_long()`, `crc_clmul_update_long()`, `crc_clmul_update_partial()`, and `crc_clmul()`. It consumes `struct crc_clmul_consts` from `crc-clmul-consts.h`.

## Control Flow
`crc_clmul()` first aligns the buffer to `sizeof(unsigned long)` using partial-byte updates. Large buffers use a two-long folding loop that carries two polynomial accumulators, folds with precomputed constants, and consumes two longs per iteration. Remaining full longs are reduced one at a time, and any tail bytes are handled by `crc_clmul_update_partial()`. Final reductions use Barrett arithmetic specialized for reflected and non-reflected CRCs.

## State and Persistence
All state is local to the checksum call: the input pointer, length, current CRC value, temporary message polynomial, and fold accumulators. There is no global state, locking, or persistence.

## Dependencies and Integration Points
It depends on RISC-V inline assembly with `.option arch,+zbc`, Linux byte-order helpers, `BITS_PER_LONG`, and `BUILD_BUG_ON`. It is instantiated by the RISC-V CRC wrapper C files for 16-, 32-, and 64-bit CRCs.

## Risks and Test Signals
Risks include subtle polynomial bit-order mistakes, wrong tail handling when `len < sizeof(crc_t)`, alignment pointer arithmetic on `const void *`, and compiler/assembler support for Zbc inline asm. Test signals are random alignment and length vectors, zero-length calls, 32-bit RISC-V builds, 64-bit CRC builds, interrupt-context KUnit coverage, and comparison to generic table/bit implementations.
