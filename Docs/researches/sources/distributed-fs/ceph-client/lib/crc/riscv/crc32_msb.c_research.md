# sources/distributed-fs/ceph-client/lib/crc/riscv/crc32_msb.c

## Purpose
This file instantiates the RISC-V CLMUL template for non-reflected/most-significant-bit-first 32-bit CRC32.

## Important APIs, Types, and Functions
It sets `crc_t` to `u32`, `LSB_CRC` to `0`, includes `crc-clmul-template.h`, and defines `crc32_msb_clmul()`.

## Control Flow
The wrapper calls `crc_clmul()` with the supplied constants. The shared template manages byte-order loads with big-endian interpretation for MSB-first CRCs.

## State and Persistence
No persistent state is present.

## Dependencies and Integration Points
It backs `crc32_be_arch()` in the RISC-V CRC32 header.

## Risks and Test Signals
Risks include byte-order mistakes and MSB-first partial-byte update errors. Test signals include CRC32 BE KUnit cases and comparison against `crc32_be_base()`.
