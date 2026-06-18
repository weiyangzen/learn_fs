<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/aes-ce-core.S -->
# sources/distributed-fs/ceph-client/arch/arm/crypto/aes-ce-core.S

## Purpose
ARMv8 Crypto Extensions assembly core for AES block modes on 32-bit ARM: ECB, CBC, CTS-CBC, CTR, XTS, key substitution, and inverse mix-columns helper.

## Important APIs/types/functions
- Exported entry points: `ce_aes_ecb_encrypt/decrypt`, `ce_aes_cbc_encrypt/decrypt`, `ce_aes_cbc_cts_encrypt/decrypt`, `ce_aes_ctr_encrypt`, `ce_aes_xts_encrypt/decrypt`, `ce_aes_sub`, and `ce_aes_invert`.
- Internal helpers: `aes_encrypt`, `aes_decrypt`, `aes_encrypt_4x`, `aes_decrypt_4x`, and `ce_aes_xts_init`.
- Uses AES instructions (`aese`, `aesmc`, `aesd`, `aesimc`) and NEON vector registers for parallel blocks.

## Control flow
Mode entry points loop over full blocks, prefer 4-block parallel paths where possible, then handle remaining blocks and tails. CBC encrypt chains each ciphertext block through the IV; CBC decrypt can parallelize decrypt then XOR previous ciphertext. CTR constructs counter blocks, handles counter carry, and supports a tail-keystream path. XTS initializes tweak from the second key and IV, updates tweaks per block, and handles ciphertext stealing.

## State and persistence behavior
No global state. State is passed in key schedules, IV/tweak/counter buffers, input/output pointers, block counts, and vector registers. IV/counter buffers are updated by the assembly routines for chaining modes.

## Dependencies and integration points
Called from `aes-ce-glue.c` inside `kernel_neon_begin/end`. Requires CPU AES extension availability and correct key schedule layout from `struct crypto_aes_ctx`.

## Risks and edge cases
Assembly ABI must exactly match C prototypes. Tail and ciphertext-stealing paths are high risk for off-by-one and overlap errors. Counter carry and XTS tweak multiplication must match CryptoAPI test vectors. NEON/AES register use must remain inside protected SIMD sections.

## Test signals
Run CryptoAPI AES test vectors for ECB, CBC, CTS-CBC, CTR, XTS with 128/192/256-bit keys, unaligned scatterlists, in-place and out-of-place buffers, partial tails, and counter carry cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/aes-ce-core.S -->
