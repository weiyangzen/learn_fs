# sources/distributed-fs/ceph-client/include/crypto/akcipher.h

Purpose: public key cipher API for algorithms such as RSA under the kernel crypto framework.

Important APIs/types/functions: `struct akcipher_request`, `struct crypto_akcipher`, `struct akcipher_alg`, `crypto_alloc_akcipher`, tfm/alg casts, request allocation/free/callback/crypt setters, `crypto_akcipher_maxsize`, async `crypto_akcipher_encrypt/decrypt`, sync encrypt/decrypt helpers, and public/private key setters.

Control flow: callers allocate a tfm, set public or private key, allocate and configure a request with source/destination SGs and lengths, then invoke encrypt/decrypt. Inline dispatch calls the algorithm callback. Sync helpers wrap this for virtual buffers.

State and persistence: tfm holds algorithm context and request size. Requests carry transient SGs and lengths; `dst_len` is updated with actual or required output length.

Dependencies and integration points: built on core crypto async requests and scatterlists. Integrated with key handling and public-key users such as signature/encryption code.

Risks: `crypto_akcipher_maxsize()` assumes a successful prior key set; otherwise callbacks may dereference missing key state. Callers must honor updated `dst_len` on insufficient output buffers.

Test signals: RSA KATs, too-small destination tests, key decode error tests, async callback tests, sync wrapper tests, and request zeroization checks.
