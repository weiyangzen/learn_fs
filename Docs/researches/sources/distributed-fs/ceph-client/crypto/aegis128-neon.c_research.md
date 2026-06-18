# sources/distributed-fs/ceph-client/crypto/aegis128-neon.c

Purpose: is the ARM/ARM64 SIMD wrapper layer for AEGIS-128. It detects runtime AES/NEON availability and safely enters kernel SIMD context before calling freestanding NEON inner routines.

Important APIs, types, and functions: exports `aegis128_have_aes_insn`, `crypto_aegis128_have_simd()`, `crypto_aegis128_init_simd()`, `crypto_aegis128_update_simd()`, `crypto_aegis128_encrypt_chunk_simd()`, `crypto_aegis128_decrypt_chunk_simd()`, and `crypto_aegis128_final_simd()`.

Control flow and behavior: `crypto_aegis128_have_simd()` returns true on ARM CPUs with AES feature and on ARM64 even without AES instructions because the inner file has an ARM64 table fallback; it sets `aegis128_have_aes_insn` only when hardware AES exists. Each operation wraps the raw NEON call in `scoped_ksimd()` so vector register use is permitted in kernel context.

State and persistence: the global `aegis128_have_aes_insn` is read-only after init and controls inner fallback behavior. No transform/request state is stored here; state buffers are supplied by `aegis128-core.c`.

Dependencies and integration points: depends on architecture CPU feature helpers, `asm/simd.h`, `aegis.h`, and `aegis-neon.h`. It is included in the `aegis128` composite object only for ARM/ARM64 SIMD builds.

Risks and correctness concerns: SIMD use outside valid kernel SIMD context can corrupt user or kernel vector state, so wrapper coverage must remain complete. Runtime feature detection must match the inner implementation’s assumptions. ARM64 fallback availability means SIMD registration can happen without AES instructions, which must remain intentional.

Test signals: boot/module tests on ARM with AES, ARM without AES, ARM64 with and without AES, preemption-heavy crypto workloads, crypto self-tests forcing SIMD driver selection, and comparison with generic `aegis128-generic`.
