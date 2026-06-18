# sources/distributed-fs/ceph-client/lib/crc/loongarch/crc32.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/loongarch/crc32.h` dispatches CRC32 and CRC32C to LoongArch hardware CRC instructions when available, otherwise falling back to generic tables.

## Important APIs, Types, and Functions

It defines inline assembly macros `_CRC32`, `CRC32`, and `CRC32C`, static key `have_crc32`, and inline functions `crc32_le_arch`, `crc32c_arch`, `crc32_mod_init_arch`, and `crc32_optimizations_arch`. Big-endian CRC32 aliases to generic.

## Control Flow

Each wrapper checks `have_crc32`; if false, it calls the generic base function. If true, it processes unaligned little-endian chunks in 64-bit, 32-bit, 16-bit, and 8-bit widths with `get_unaligned_le*()` and LoongArch `crc` or `crcc` instructions. Init enables the static key when `cpu_has_crc32`.

## State and Persistence Behavior

Runtime feature state is a read-only-after-init static key. No per-call state persists beyond the returned CRC.

## Dependencies and Integration Points

Dependencies include LoongArch CPU feature macros, unaligned access helpers, generic CRC32 base functions, and inclusion from `crc32-main.c`.

## Risks and Edge Cases

Hardware instructions are little-endian CRC32/CRC32C only; BE falls back. Inline assembly clobbers memory and must match instruction operand order. Feature detection must not enable instructions on unsupported CPUs.

## Test Signals

Signals include hardware/generic equivalence for CRC32 and CRC32C, unaligned buffers, all tail widths, no-feature fallback, and `crc32_optimizations()` flags.

## Read Coverage

Source read size: 115 lines, 2335 bytes.
