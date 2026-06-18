# sources/distributed-fs/ceph-client/lib/crypto/arm/blake2b.h

## Purpose
This ARM arch header selects the NEON BLAKE2b compression implementation when available and SIMD use is allowed.

## Important APIs, Types, and Functions
It defines static key `have_neon`, declares `blake2b_compress_neon()`, overrides `blake2b_compress()`, and defines `blake2b_mod_init_arch()`.

## Control Flow
`blake2b_compress()` falls back to `blake2b_compress_generic()` if NEON is unavailable or SIMD cannot be used. Otherwise it processes input in chunks capped at `SZ_4K / BLAKE2B_BLOCK_SIZE` inside `scoped_ksimd()` sections, updating data pointer and block count. Init enables the static key when `elf_hwcap` has `HWCAP_NEON`.

## State and Persistence
Persistent state is the static key and caller-owned BLAKE2b context. No other state persists.

## Dependencies and Integration Points
It depends on ARM NEON/SIMD helpers and is included by generic `blake2b.c` via arch include path when selected.

## Risks and Test Signals
Risks include SIMD use in preempt/irq contexts, chunking mistakes, and static-key feature detection. Test signals are BLAKE2b vectors with NEON enabled/disabled and context-sensitive SIMD tests.
