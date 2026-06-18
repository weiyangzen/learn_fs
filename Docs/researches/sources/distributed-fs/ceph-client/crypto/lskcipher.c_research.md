# sources/distributed-fs/ceph-client/crypto/lskcipher.c

Purpose: implements the crypto API type for linear symmetric key ciphers (`lskcipher`) and bridges that type to skcipher scatterlist requests. It centralizes allocation, registration, reporting, alignment fallback, and simple-instance helpers.

Important APIs, types, and functions: exported APIs include `crypto_lskcipher_setkey()`, `crypto_lskcipher_encrypt()`, `crypto_lskcipher_decrypt()`, `crypto_grab_lskcipher()`, `crypto_alloc_lskcipher()`, `crypto_register_lskcipher()`, `crypto_unregister_lskcipher()`, `crypto_register_lskciphers()`, `crypto_unregister_lskciphers()`, `lskcipher_register_instance()`, and `lskcipher_alloc_instance_simple()`. Internal paths include `crypto_lskcipher_crypt_unaligned()` and `crypto_lskcipher_crypt_sg()`.

Control flow: direct callers allocate an `lskcipher`, set a key after min/max validation, and call encrypt/decrypt on linear buffers. If key, src, dst, or IV alignment violates the algorithm alignmask, the code copies through temporary aligned pages and copies IV plus state back. The SG bridge walks a skcipher request, maps continuation/final flags into `CRYPTO_LSKCIPHER_FLAG_*`, and updates the IV after walking. Registration prepares common skcipher metadata, enforces power-of-two chunksize, installs the `crypto_lskcipher_type`, and registers algorithms or instances.

State and persistence: transform state is owned by individual algorithms and optional child ciphers. The bridge stores a child `crypto_lskcipher *` in the parent skcipher context and frees it on tfm exit. No state persists outside crypto object lifetimes, except exported/imported IV/state carried by callers.

Dependencies and integration points: depends on `skcipher.h`, common crypto algorithm registration, procfs/netlink reporting, and simple-mode templates such as CBC/ECB-style modes.

Risks: alignment fallback allocates with `GFP_ATOMIC` and processes page-sized chunks; failures return `-ENOMEM`. Lengths not divisible by blocksize fail after partial chunk handling. Continuation/final flag propagation is subtle for multi-walk requests. Simple instance naming prevents nested instances unless the child was auto-ECB-wrapped.

Test signals: test aligned and unaligned keys/data/IV, SG requests with continuation and not-final flags, chunksize validation, netlink/proc reporting, simple instance creation with bare and `ecb(...)` child names, and registration rollback for arrays.
