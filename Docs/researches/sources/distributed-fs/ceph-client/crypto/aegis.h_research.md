# sources/distributed-fs/ceph-client/crypto/aegis.h

Purpose: provides common AEGIS definitions shared by generic and SIMD implementations: block layout, alignment checks, SIMD wrapper prototypes, and a software AES round helper used by the generic AEGIS state update.

Important APIs, types, and functions: defines `AEGIS_BLOCK_SIZE`, `union aegis_block`, forward `struct aegis_state`, `aegis128_have_aes_insn`, `AEGIS_ALIGNED()`, SIMD wrapper declarations, `crypto_aegis_block_xor()`, `crypto_aegis_block_and()`, and `crypto_aegis_aesenc()`.

Control flow and behavior: generic code uses the inline XOR/AND/AESENC helpers for state transitions and block operations. SIMD-capable code uses the declared wrapper functions when runtime SIMD is usable. The AESENC helper implements SubBytes/ShiftRows/MixColumns/table lookup plus key XOR using `aes_enc_tab`.

State and persistence: no independent storage is defined beyond the global `aegis128_have_aes_insn` declaration. `union aegis_block` standardizes in-memory state and tag representation as 16 bytes with little-endian 32/64-bit views.

Dependencies and integration points: depends on `crypto/aes.h` tables, Linux bitops/types, and ARM/ARM64 SIMD implementations. Included by `aegis128-core.c` and `aegis128-neon.c`.

Risks and correctness concerns: the inline software AES round must match the AES round semantics used by AEGIS; endian conversion and byte indexes are correctness-critical. Alignment macros affect fast paths, and `union aegis_block` layout must remain 16 bytes. Prototype drift would break SIMD builds.

Test signals: compile with and without SIMD, compare generic and SIMD known-answer results, run unaligned input/output cases, and validate big/little-endian behavior through crypto self-tests on supported architectures.
