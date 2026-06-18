# sources/distributed-fs/ceph-client/lib/crypto/arm64/aes.h

## Purpose
This header is the ARM64 AES integration layer. It handles feature detection, key expansion, single-block dispatch, exported internal mode symbols, and optional CBC-MAC acceleration.

## Important APIs, Types, And Functions
It defines `struct aes_block`, static keys `have_neon` and `have_aes`, declarations for scalar, CE, and mode assembly symbols, `aes_expandkey_arm64`, `aes_preparekey_arch`, exported `ce_aes_expandkey`, `aes_encrypt_arch`, `aes_decrypt_arch`, `aes_cbcmac_blocks_arch`, and `aes_mod_init_arch`.

## Control Flow
Key expansion uses generic C when AES CE is unavailable or SIMD cannot be used; otherwise it uses `__aes_ce_sub` for key schedule S-box operations and `__aes_ce_invert` for inverse round keys. Single-block encrypt/decrypt choose CE inside `scoped_ksimd()` when possible and scalar otherwise. CBC-MAC chooses CE or NEON mode update under ASIMD. Init enables ASIMD and AES static keys through named CPU features.

## State And Persistence
Persistent state is limited to static keys. Expanded keys are stored in caller-owned AES key structures. `ce_aes_expandkey` mutates `struct crypto_aes_ctx` and is exported for remaining arch crypto users.

## Dependencies And Integration Points
It depends on ASIMD/SIMD helpers, unaligned access helpers, cpufeature APIs, generic AES key expansion/check helpers, and exported internal crypto symbols for mode code. It bridges lib/crypto and legacy arch/arm64 crypto users.

## Risks And Edge Cases
The expanded key format must stay compatible across scalar, CE, NEON modes, and exported users. `ce_aes_expandkey` is temporary but externally visible. SIMD usability checks are required for key expansion too because `__aes_ce_sub` uses vector crypto instructions.

## Test Signals
AES key expansion tests for all key sizes, encrypt/decrypt KATs, module symbol users such as CCM/XTS/CBC, fallback with AES feature disabled, and CBC-MAC tests validate this header.
