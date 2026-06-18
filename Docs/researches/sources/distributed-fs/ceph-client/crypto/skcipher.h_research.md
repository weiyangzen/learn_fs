# sources/distributed-fs/ceph-client/crypto/skcipher.h

`skcipher.h` is a local internal header that connects the generic skcipher frontend with lskcipher scatterlist adapter helpers and shared algorithm validation.

It declares `crypto_lskcipher_encrypt_sg()`, `crypto_lskcipher_decrypt_sg()`, `crypto_init_lskcipher_ops_sg()`, and `skcipher_prepare_alg_common()`. It includes `<crypto/internal/skcipher.h>` and local `"internal.h"`, with the `_LOCAL_CRYPTO_SKCIPHER_H` include guard.

There is no runtime control flow or owned state. Its integration role is compile-time: `skcipher.c` uses these declarations to dispatch lskcipher-backed skcipher transforms and to share common `skcipher_alg_common` validation. The main risk is local ABI drift: if prototypes or implied request-layout expectations change without matching implementations, lskcipher-backed algorithms can fail at build time or at runtime. Test signals are successful builds plus runtime coverage of lskcipher-backed encrypt/decrypt, import/export, and request-size handling.
