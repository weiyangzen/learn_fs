# sources/distributed-fs/ceph-client/arch/x86/crypto/aegis128-aesni-glue.c

## Purpose
C glue registering the AES-NI/SSE4.1 AEGIS-128 AEAD implementation with the kernel crypto API. It handles scatterlists, FPU ownership, key/authsize validation, tag placement, and module lifecycle.

## Important APIs, Types, And Functions
Defines `struct aegis_block`, `struct aegis_state`, and `struct aegis_ctx`, declares the assembly routines, and registers `crypto_aegis128_aesni_alg`. Key functions are `crypto_aegis128_aesni_setkey()`, `crypto_aegis128_aesni_setauthsize()`, `crypto_aegis128_aesni_encrypt()`, `crypto_aegis128_aesni_decrypt()`, `crypto_aegis128_aesni_crypt()`, `crypto_aegis128_aesni_process_ad()`, and `crypto_aegis128_aesni_process_crypt()`.

## Control Flow And State
Setkey stores a 16-byte key in aligned context. Encrypt/decrypt set up a skcipher walk, enter kernel FPU context, initialize assembly state, absorb AD from scatterlists with zero-padded final AD block, process full blocks and tails, finalize the tag, and leave FPU context around `skcipher_walk_done()` calls. Encryption writes the produced tag after ciphertext. Decryption preloads the transmitted tag, finalizes by XORing computed tag into it, and returns `-EBADMSG` when any authenticated byte differs from zero.

## Dependencies And Integration
Depends on crypto AEAD/skcipher internals, scatterwalk helpers, module registration, CPU feature checks for AES/SSE4.1/SSE xfeatures, and the assembly symbols from `aegis128-aesni-asm.S`.

## Risks And Test Signals
Risks include scatterlist boundary buffering, FPU begin/end imbalance, authsize limits, context alignment, tag comparison length, and cryptlen underflow if callers violate AEAD decrypt contract. Signals include `tcrypt`/crypto manager selftests, random scatterlist layouts, all auth sizes 8-16, empty AD/plaintext cases, CPU feature gating, and module unload/reload.
