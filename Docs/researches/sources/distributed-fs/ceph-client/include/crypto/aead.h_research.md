# sources/distributed-fs/ceph-client/include/crypto/aead.h

Purpose: authenticated encryption with associated data API for `CRYPTO_ALG_TYPE_AEAD` algorithms.

Important APIs/types/functions: `struct aead_request`, `struct aead_alg`, `struct crypto_aead`, `struct crypto_sync_aead`, `SYNC_AEAD_REQUEST_ON_STACK`, allocation/free helpers, getters for IV/auth/block/align sizes and flags, `crypto_aead_setkey`, `crypto_aead_setauthsize`, `crypto_aead_encrypt`, `crypto_aead_decrypt`, request allocation/free, `aead_request_set_callback`, `aead_request_set_crypt`, and `aead_request_set_ad`.

Control flow: callers allocate a tfm, set key and authentication tag size, allocate/configure a request with SG source/destination, IV, crypt length, and associated-data length, then call encrypt/decrypt. Decrypt returns `-EBADMSG` for authentication failure.

State and persistence: tfm stores auth size and request context size. Requests store transient SG pointers, IV, lengths, callbacks, and per-request context. Algorithm definitions persist callback tables and capability sizes.

Dependencies and integration points: built on `linux/crypto.h` and async crypto requests; used by GCM, CCM, authenc, IPsec AEAD wrappers, and synchronous wrapper users.

Risks: source/destination layout must be `AAD || text || tag` as documented. Destination must reserve tag growth on encryption and include tag on decryption. IPsec RFC variants require an IV copy in associated data. Authentication errors must not be collapsed into generic I/O success.

Test signals: AEAD known-answer tests, in-place/out-of-place SG tests, bad-tag `-EBADMSG` tests, authsize validation, sync wrapper stack-size checks, and IPsec RFC quirk coverage.
