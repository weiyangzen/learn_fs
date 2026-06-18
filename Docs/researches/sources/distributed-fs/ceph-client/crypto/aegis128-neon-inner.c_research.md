# sources/distributed-fs/ceph-client/crypto/aegis128-neon-inner.c

Purpose: provides the freestanding ARM/ARM64 NEON inner implementation of AEGIS-128, including AES-round acceleration, software AES fallback on ARM64 without AES instructions, chunk encryption/decryption, and tag generation/verification.

Important APIs, types, and functions: defines `struct aegis128_state`, `aegis128_load_state_neon()`, `aegis128_save_state_neon()`, `aegis_aes_round()`, `aegis128_update_neon()`, `preload_sbox()`, and exported NEON functions declared in `aegis-neon.h`.

Control flow and behavior: state is loaded into five `uint8x16_t` vectors. `aegis_aes_round()` uses paired AES instructions when available; ARM64 fallback emulates ShiftRows/SubBytes/MixColumns using table lookups and the AES S-box. Encryption computes keystream `s1 ^ (s2 & s3) ^ s4`, updates with plaintext, and writes ciphertext; decryption derives plaintext before update. Short final chunks use a permutation table to avoid out-of-bounds vector accesses.

State and persistence: state exists only in caller-provided memory, converted to/from vector registers. `aegis128_have_aes_insn` controls the fast AES instruction path. Temporary buffers for short chunks and tag verification are stack-local.

Dependencies and integration points: compiled with special kbuild flags from `crypto/Makefile`, includes ARM/ARM64 NEON headers, uses `crypto_aes_sbox`, and is invoked only through `aegis128-neon.c` under `scoped_ksimd()`.

Risks and correctness concerns: freestanding vector code is compiler- and architecture-sensitive. The GCC ARM64 fallback pins vector registers and preloads S-box tables; flag drift can corrupt ABI assumptions. Short-chunk permutation logic is high risk for off-by-one and stale vector writes. Verification returns a vector-derived mismatch value, so callers must treat any nonzero as failure.

Test signals: ARM32 and ARM64 builds with GCC and Clang, CPUs with and without AES instructions, known-answer tests for all chunk lengths 0-31 and multi-block lengths, unaligned buffers, KASAN where possible, and generic-vs-NEON differential tests.
