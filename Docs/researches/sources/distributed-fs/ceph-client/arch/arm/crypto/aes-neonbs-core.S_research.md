<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/aes-neonbs-core.S -->
# sources/distributed-fs/ceph-client/arch/arm/crypto/aes-neonbs-core.S

## Purpose
NEON bit-sliced AES assembly core for 32-bit ARM, processing eight AES blocks in parallel for ECB, CBC decrypt, CTR, and XTS.

## Important APIs/types/functions
- Exported entry points: `aesbs_convert_key`, `aesbs_ecb_encrypt/decrypt`, `aesbs_cbc_decrypt`, `aesbs_ctr_encrypt`, `aesbs_xts_encrypt/decrypt`.
- Internal helpers: `aesbs_encrypt8`, `aesbs_decrypt8`, `__xts_prepare8`, permutation tables, ShiftRows/MixColumns/S-box macro sequences.

## Control flow
`aesbs_convert_key()` transforms conventional round keys into bit-sliced layout. ECB and CTR process groups of eight blocks, with permutations between byte layout and bit-sliced vectors. CBC decrypt decrypts parallel blocks then XORs with prior ciphertext/IV. CTR generates counter vectors and handles tails. XTS prepares eight tweak values, applies encrypt/decrypt, and updates tweak order for ciphertext stealing.

## State and persistence behavior
No global state. State is in vector registers, key schedule memory, IV/counter/tweak buffers, and input/output pointers. IV/counter/tweak buffers are mutated for chaining modes.

## Dependencies and integration points
Called from `aes-neonbs-glue.c` under `kernel_neon_begin/end`. Requires NEON availability and key layout produced by `aesbs_convert_key()`.

## Risks and edge cases
Eight-block granularity requires fallback or special handling for small/tail buffers. Assembly/C ABI mismatches, scatterlist stride mistakes, or tweak reordering bugs break only specific sizes. Constant-time bit-sliced logic reduces table-timing exposure but still depends on correct SIMD context management.

## Test signals
CryptoAPI vectors for ECB/CBC/CTR/XTS across key sizes, messages below/equal/above eight blocks, unaligned buffers, in-place buffers, and ciphertext stealing are required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/aes-neonbs-core.S -->
