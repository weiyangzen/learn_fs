<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/ghash-ce-core.S -->
# sources/distributed-fs/ceph-client/arch/arm/crypto/ghash-ce-core.S

## Purpose
ARM PMULL/NEON assembly core for GHASH and fused AES-GCM encrypt/decrypt/finalization operations.

## Important APIs/types/functions
- Exported functions: `pmull_ghash_update_p64`, `pmull_gcm_encrypt`, `pmull_gcm_decrypt`, `pmull_gcm_enc_final`, and `pmull_gcm_dec_final`.
- Internal helpers: PMULL GHASH aggregation, AES encrypt helpers, final tag generation/verification, and byte-permutation table `.Lpermute`.

## Control flow
GHASH update multiplies input blocks into the running digest using precomputed hash powers. GCM encrypt/decrypt routines interleave AES counter-mode keystream generation with GHASH accumulation over ciphertext. Final routines process tail bytes, fold lengths into GHASH, encrypt `J0`, produce or compare tags, and return authentication status for decrypt.

## State and persistence behavior
No global state. Digest, hash key powers, AES round keys, IV/counter, source/destination pointers, and tag buffers are caller-provided. Digest and output buffers are mutated.

## Dependencies and integration points
Called by `ghash-ce-glue.c` inside NEON sections. Requires PMULL and NEON hardware capability, key layout from ARM AES library, and GHASH reflection/precomputation in C.

## Risks and edge cases
Authentication correctness depends on exact GHASH endian/reflection convention. Tail handling and final tag comparison are security-critical. Assembly ABI and PMULL availability must match runtime feature checks.

## Test signals
Run AES-GCM and RFC4106 vectors with varied AAD/plaintext lengths, tails, tag sizes, invalid tags, in-place buffers, and scatterlist splits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/ghash-ce-core.S -->
