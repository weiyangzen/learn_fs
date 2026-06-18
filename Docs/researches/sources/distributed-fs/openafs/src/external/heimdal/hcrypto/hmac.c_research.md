# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/hmac.c

Purpose: implements HMAC over the hcrypto EVP digest API, including reusable `HMAC_CTX` state and a one-shot convenience wrapper.

Important APIs/types/functions: `HMAC_CTX_init`, `HMAC_CTX_cleanup`, `HMAC_size`, `HMAC_Init_ex`, `HMAC_Update`, `HMAC_Final`, and `HMAC`. Context fields include selected digest, optional engine, inner digest context, digest-sized buffer, and allocated inner/outer pads.

Control flow: initialization clears the context. `HMAC_Init_ex` updates the digest selection, allocates a digest-sized work buffer, hashes overlong keys down to digest size, allocates block-sized ipad/opad buffers, XORs the key into 0x36/0x5c pads, creates the nested EVP context if needed, and starts the inner digest with ipad. `HMAC_Update` feeds message data. `HMAC_Final` finalizes the inner digest into `buf`, starts a new digest over opad plus inner digest, and returns the outer digest. The one-shot wrapper performs init, update, final, and cleanup on a stack context.

State and persistence: reusable contexts persist allocated pads, a digest work buffer, and an EVP digest context until cleanup. Cleanup zeroes buffers before free and destroys the EVP context.

Dependencies and integration points: depends on `hmac.h`, `evp.h`, and provider digest descriptors. Used by `pkcs5.c` and `validate.c`, and by callers needing OpenSSL-compatible `HMAC()`.

Risks and test signals: `HMAC_Init_ex` does not check malloc or `EVP_MD_CTX_create` failures before use, cleanup zero lengths use `key_length` for pads even though pads are block-sized in two spots, and engine storage is disabled under `#if 0`. Tests should cover RFC-style HMAC vectors, overlong keys, repeated reuse with different digests/keys, cleanup under partially initialized contexts, and allocation-failure hardening if relevant.
