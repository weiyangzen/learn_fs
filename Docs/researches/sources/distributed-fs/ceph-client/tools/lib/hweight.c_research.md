## sources/distributed-fs/ceph-client/tools/lib/hweight.c

Purpose: Provides software Hamming-weight/popcount implementations for 8-, 16-, 32-, and 64-bit values.

Important APIs/functions: `__sw_hweight8()`, `__sw_hweight16()`, `__sw_hweight32()`, and `__sw_hweight64()`.

Control flow: Each function applies standard SWAR bit-count reductions. Fast-multiplier builds use multiply-by-byte-sum constants for 32/64-bit cases; otherwise they use staged additions. 64-bit behavior splits into two 32-bit halves on 32-bit `BITS_PER_LONG`.

State/persistence: Stateless.

Dependencies/integration: Uses Linux bitops, asm types, `BITS_PER_LONG`, and optional `CONFIG_ARCH_HAS_FAST_MULTIPLIER`.

Risks: Correctness depends on unsigned arithmetic widths and constants matching word size. Build configuration determines implementation path. The 64-bit function has no explicit fallback outside 32/64-bit `BITS_PER_LONG`.

Test signals: Compare against compiler builtin popcount for all 8-bit values, representative 16/32/64-bit patterns, all-zero/all-one values, alternating bits, and both fast/non-fast configurations.
