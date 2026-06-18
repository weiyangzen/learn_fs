# sources/distributed-fs/ceph-client/crypto/sm4_generic.c

`sm4_generic.c` registers the generic SM4 single-block cipher with the Crypto API legacy cipher interface. It is a thin wrapper over the shared SM4 routines in `sm4.c`.

The registered `crypto_alg` is `sm4_alg`, named `"sm4"` with driver `"sm4-generic"`, priority 100, `CRYPTO_ALG_TYPE_CIPHER`, 16-byte block size, 16-byte key size, and `struct sm4_ctx` transform context. Runtime callbacks are `sm4_setkey()`, `sm4_encrypt()`, and `sm4_decrypt()`.

Module init calls `crypto_register_alg()`, and exit unregisters it. Setkey obtains the transform context and delegates to `sm4_expandkey()`. Encrypt/decrypt obtain the context and call `sm4_crypt_block()` with `rkey_enc` or `rkey_dec`. State is only the expanded key schedule in each transform. Dependencies are `<crypto/algapi.h>`, `<crypto/sm4.h>`, and the library exports from `sm4.c`. Risks include legacy cipher API constraints, invalid key-length propagation, and generic table-lookup side channels. Test signals include alias allocation, setkey length rejection, ecb(sm4) vectors, and mode users in `tcrypt`.
