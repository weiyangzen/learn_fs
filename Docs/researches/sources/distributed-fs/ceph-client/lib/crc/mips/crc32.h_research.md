# sources/distributed-fs/ceph-client/lib/crc/mips/crc32.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/mips/crc32.h` dispatches CRC32 and CRC32C to optional MIPSr6 CRC instructions, with assembler compatibility for toolchains lacking CRC mnemonic support.

## Important APIs, Types, and Functions

Important macros are `_ASM_SET_CRC`, `_ASM_UNSET_CRC`, `__CRC32`, `_CRC32_crc32*`, `_CRC32_crc32c*`, `CRC32`, and `CRC32C`. It defines static key `have_crc32` and inline wrappers `crc32_le_arch`, `crc32c_arch`, `crc32_mod_init_arch`, and `crc32_optimizations_arch`. Big-endian CRC32 uses generic.

## Control Flow

If the static key is disabled, wrappers call generic base functions. With hardware support, 64-bit builds process 64-bit chunks first, then 32/16/8 tails; 32-bit builds process 32-bit chunks, then smaller tails. Inline assembly emits CRC opcodes either through assembler macros or explicit instruction encodings. Init enables the static key when `MIPS_CRC32` is present.

## State and Persistence Behavior

The only persistent state is the runtime static key. CRC accumulators are local.

## Dependencies and Integration Points

Dependencies include MIPS CPU feature detection, MIPS register/opcode assembler helpers, unaligned little-endian loads, generic CRC base functions, and inclusion by `crc32-main.c`.

## Risks and Edge Cases

Toolchain-support fallbacks must encode the exact CRC opcodes. 32-bit and 64-bit chunk paths must advance pointers consistently. Hardware support is LE CRC32/CRC32C only; BE remains generic.

## Test Signals

Signals include builds with and without `TOOLCHAIN_SUPPORTS_CRC`, 32-bit and 64-bit MIPS configs, hardware/generic vector equivalence, unaligned buffers, tails, and feature flag reporting.

## Read Coverage

Source read size: 162 lines, 4068 bytes.
