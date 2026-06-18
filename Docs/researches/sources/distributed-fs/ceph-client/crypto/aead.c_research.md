# sources/distributed-fs/ceph-client/crypto/aead.c

Purpose: provides the generic AEAD crypto API front end: key setup, authsize validation, encrypt/decrypt dispatch, allocation, spawn grabbing, algorithm and template instance registration, proc reporting, and netlink reporting.

Important APIs, types, and functions: exported calls include `crypto_aead_setkey()`, `crypto_aead_setauthsize()`, `crypto_aead_encrypt()`, `crypto_aead_decrypt()`, `crypto_grab_aead()`, `crypto_alloc_aead()`, `crypto_alloc_sync_aead()`, `crypto_has_aead()`, `crypto_register_aead()`, `crypto_unregister_aead()`, batch helpers, and `aead_register_instance()`.

Control flow and behavior: `crypto_aead_setkey()` handles key alignment by copying to an aligned temporary buffer when required, propagates algorithm setkey errors, and manages `CRYPTO_TFM_NEED_KEY`. Encryption/decryption reject unkeyed transforms; decryption also verifies `cryptlen >= authsize`. Transform initialization defaults authsize to `maxauthsize`, sets request size, and installs an exit hook when needed. Registration validates authsize/iv/chunksize bounds and stamps the crypto type.

State and persistence: per-transform state is held by `struct crypto_aead`, including flags, authsize, request size, and algorithm-private context. The file has no persistent storage; registered algorithms persist in the global crypto registry until unregistered.

Dependencies and integration points: depends on `crypto/internal/aead.h`, generic `crypto_alloc_tfm()` and `crypto_register_alg()`, procfs, netlink cryptouser reporting, and template/spawn infrastructure from `algapi.c`. AEAD implementations such as GCM, CCM, ChaCha20-Poly1305, and AEGIS register through this layer.

Risks and correctness concerns: authsize zero is allowed only for algorithms with zero maximum auth size. Unaligned key handling uses `GFP_ATOMIC`, so large or frequent setkey calls can fail under pressure. Registration bounds prevent huge IV/auth/chunk sizes from breaking stack/request assumptions. Forgetting to set `NEED_KEY` on errors can permit unkeyed operations.

Test signals: test unaligned key pointers, invalid auth sizes, decrypt-shorter-than-tag rejection, sync allocation rejecting large request sizes, proc/netlink output, instance registration with missing `free`, and AEAD known-answer tests through both direct kernel API and AF_ALG.
