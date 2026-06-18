<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/aes-neonbs-glue.c -->
# sources/distributed-fs/ceph-client/arch/arm/crypto/aes-neonbs-glue.c

## Purpose
C CryptoAPI glue for the NEON bit-sliced AES implementation, registering ECB, CBC, CTR, and XTS skcipher providers.

## Important APIs/types/functions
- Contexts: `struct aesbs_ctx`, `struct aesbs_cbc_ctx`, and `struct aesbs_xts_ctx`.
- Key setup: `aesbs_setkey()`, `aesbs_cbc_setkey()`, `aesbs_xts_setkey()`.
- Request handlers: `__ecb_crypt()`, `cbc_encrypt()`, `cbc_decrypt()`, `ctr_encrypt()`, `__xts_crypt()`, `xts_encrypt()`, `xts_decrypt()`.
- Registered drivers: `ecb-aes-neonbs`, `cbc-aes-neonbs`, `ctr-aes-neonbs`, and `xts-aes-neonbs`.

## Control flow
Key setup expands normal AES keys then converts encryption keys into bit-sliced form. ECB/CBC decrypt/CTR/XTS walk scatterlists and call assembly for block batches. CBC encryption uses the scalar AES fallback because encryption is inherently serial. CTR pads sub-block tails into a stack buffer. XTS encrypts the tweak with the fallback key, processes full blocks via bit-sliced assembly, then handles ciphertext stealing with scalar fallback on a two-block stack buffer.

## State and persistence behavior
Per-tfm state stores bit-sliced round keys, scalar fallback keys, and XTS tweak key. Request state is in scatterwalks, IV buffers, and stack buffers. Module registration persists until unload.

## Dependencies and integration points
Depends on HWCAP_NEON runtime check, CryptoAPI skcipher, AES library fallback routines, XTS helpers, scatterwalk, and `aes-neonbs-core.S`.

## Risks and edge cases
The source as read contains a duplicate `kernel_neon_begin()` in `ctr_encrypt()` without a matching second end, which is a serious SIMD nesting risk if active. CBC encryption fallback is table/scalar dependent and may not share bit-sliced side-channel properties. Tail and XTS stealing paths use stack bounce buffers and scatterwalk copies that need overlap testing.

## Test signals
Run CryptoAPI AES vectors with NEON present/absent, all key sizes, batch and non-batch message lengths, CTR partial blocks, XTS tails, and in-place scatterlists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/aes-neonbs-glue.c -->
