# sources/distributed-fs/ceph-client/lib/crc/riscv/crc-clmul.h

## Purpose
This header declares the RISC-V Zbc carryless-multiply CRC entry points and exposes the generated constant objects to arch selectors.

## Important APIs, Types, and Functions
It declares `crc16_msb_clmul()`, `crc32_msb_clmul()`, `crc32_lsb_clmul()`, and, under `CONFIG_64BIT`, `crc64_msb_clmul()` and `crc64_lsb_clmul()`. Each accepts an initial CRC, buffer pointer, length, and `struct crc_clmul_consts *`.

## Control Flow
There is no control flow beyond include guards. Callers choose which function and constant set to use based on CRC variant and CPU feature detection.

## State and Persistence
The header defines no state. It links translation units together through declarations.

## Dependencies and Integration Points
It depends on `linux/types.h` and `crc-clmul-consts.h`. It is the shared interface between RISC-V arch selector headers and the C files that instantiate `crc-clmul-template.h`.

## Risks and Test Signals
Risks are ABI/signature mismatches between declarations and generated functions, and accidentally exposing 64-bit CRC functions on 32-bit builds. Test signals include allmodconfig-style compile coverage and link checks for CRC32/T10DIF/CRC64 modules.
