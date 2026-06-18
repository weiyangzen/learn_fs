# sources/distributed-fs/ceph-client/lib/crc/riscv/crc32.h

## Purpose
This arch header connects the generic CRC32 library to RISC-V Zbc implementations for CRC32 little-endian, CRC32 big-endian, and CRC32C.

## Important APIs, Types, and Functions
It defines `crc32_le_arch()`, `crc32_be_arch()`, `crc32c_arch()`, and `crc32_optimizations_arch()`. Accelerated calls use `crc32_lsb_clmul()` for IEEE reflected and Castagnoli reflected CRCs and `crc32_msb_clmul()` for big-endian CRC32.

## Control Flow
Each checksum hook gates on `riscv_has_extension_likely(RISCV_ISA_EXT_ZBC)`. Positive checks use the matching CLMUL function and constants; otherwise the hook calls the base/generic CRC implementation. `crc32_optimizations_arch()` returns the bitmask of all three optimizations when Zbc is available.

## State and Persistence
No local persistent state exists. CPU feature state is external.

## Dependencies and Integration Points
It depends on RISC-V hwcap helpers and the shared `crc-clmul.h` interface. It is included by the generic CRC32 implementation to override weak/base hooks.

## Risks and Test Signals
Risks include wrong reflected/non-reflected constant selection, incorrect optimization reporting, and runtime feature gating mismatches on alternatives. Test signals include KUnit CRC32/CRC32C tests, `/proc/crypto` or module optimization reporting if exposed, and cross-checks on Zbc and non-Zbc systems.
