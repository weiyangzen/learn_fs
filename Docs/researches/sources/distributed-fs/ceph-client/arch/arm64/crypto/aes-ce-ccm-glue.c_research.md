# sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-ce-ccm-glue.c

## Purpose
This C glue registers and implements the kernel crypto API AEAD algorithm `ccm(aes)` backed by ARMv8 AES Crypto Extensions.

## APIs, Types, And Functions
Important functions are `ccm_setkey`, `ccm_setauthsize`, `ccm_init_mac`, `ce_aes_ccm_auth_data`, `ccm_calculate_auth_mac`, `ccm_encrypt`, and `ccm_decrypt`. It declares assembly entry points `ce_aes_ccm_encrypt` and `ce_aes_ccm_decrypt`. The exported algorithm is `ccm_aes_alg` with driver name `ccm-aes-ce`, priority 300, AES block IV size, max auth size 16, and crypto API callbacks.

## Control Flow, State, And Persistence
Setkey expands AES keys into `crypto_aes_ctx`. Encryption validates CCM `L`, initializes B0/MAC state, preserves the original IV, walks AEAD scatterlists, enters `scoped_ksimd`, authenticates AAD, invokes assembly for data, and appends the auth tag. Decryption mirrors this flow, subtracts authsize from cryptlen, decrypts, reads the stored tag, and returns `-EBADMSG` on `crypto_memneq`. Persistent state is only the per-transform AES context.

## Dependencies And Integration
It depends on crypto AEAD/skcipher internals, scatterwalk, AES helpers, `ce_aes_expandkey`, `ce_aes_mac_update`, and `asm/simd.h`. Module init checks `cpu_have_named_feature(AES)` before `crypto_register_aead`.

## Risks And Test Signals
Risks include CCM length-field overflow, AAD length-tag handling, scatterlist/tail handling, and SIMD context misuse. Tests are crypto manager AES-CCM vectors, non-contiguous scatterlists, invalid auth sizes, short final blocks, bad-tag detection, and CPU feature-gated module loading.
