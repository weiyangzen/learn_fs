# sources/distributed-fs/ceph-client/crypto/aegis-neon.h

Purpose: declares the low-level NEON implementation entry points for AEGIS-128 state initialization, update, chunk encryption/decryption, and final tag generation/verification.

Important APIs, types, and functions: prototypes are `crypto_aegis128_init_neon()`, `crypto_aegis128_update_neon()`, `crypto_aegis128_encrypt_chunk_neon()`, `crypto_aegis128_decrypt_chunk_neon()`, and `crypto_aegis128_final_neon()`. All operate on opaque state/tag buffers to keep the NEON inner file decoupled from the generic `struct aegis_state` definition.

Control flow and behavior: callers in `aegis128-neon.c` enter kernel SIMD context, then call these raw NEON helpers. The final helper uses `authsize == 0` as tag-generation mode and nonzero authsize as verification mode.

State and persistence: the header owns no state. It defines ABI expectations for an 80-byte AEGIS state buffer, 16-byte key/IV inputs, chunk pointers, length parameters, and tag buffers shared between generic and NEON code.

Dependencies and integration points: included by `aegis128-neon.c` and `aegis128-neon-inner.c`; indirectly tied to kbuild flags enabling ARM/ARM64 NEON/AES intrinsics. It is compiled only when SIMD support is selected.

Risks and correctness concerns: prototypes must match the freestanding NEON object exactly. Because state is `void *`, layout mismatches are not type-checked. Tag verification return semantics must remain synchronized with the generic SIMD wrapper.

Test signals: ARM and ARM64 build coverage with `CONFIG_CRYPTO_AEGIS128_SIMD`, module load, KASAN/UBSAN where applicable, and AEGIS known-answer tests comparing generic and NEON outputs for full and partial chunks.
