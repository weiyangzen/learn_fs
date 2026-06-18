<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/gcm.c -->
# sources/distributed-fs/ceph-client/crypto/gcm.c

Purpose: Implements AEAD templates for Galois/Counter Mode and IPsec-specific GCM wrappers: `gcm`, `gcm_base`, `rfc4106`, and `rfc4543`.

Important APIs/types/functions: `struct crypto_gcm_ctx` owns a CTR skcipher child and prepared GHASH key. `crypto_gcm_setkey()` keys CTR, encrypts the zero block to derive GHASH H, and prepares the GF(2^128) key. `crypto_gcm_encrypt()` and `crypto_gcm_decrypt()` build synthetic scatterlists that prepend the encrypted counter block, run CTR, compute GHASH over AAD/ciphertext/lengths, append or verify tags. `crypto_rfc4106_*()` adapts GCM for ESP with a salt stored in the last four key bytes and IV/AAD reshaping. `crypto_rfc4543_*()` adapts GMAC/authentication-only ESP mode. Template create functions validate child IV size, blocksize, names, priorities, and request sizes.

Control flow: Template registration happens in `crypto_gcm_module_init()`. Instantiation grabs a CTR or AEAD child, validates it is stream-like with 12-byte GCM IV where required, and registers an AEAD instance. Runtime setkey propagates request flags and configures child keys. Encryption initializes `J0`, encrypts the counter block plus plaintext, hashes AAD and ciphertext, XORs GHASH with the encrypted counter block, and writes the auth tag. Decryption hashes ciphertext first, decrypts data, and compares the expected tag with `crypto_memneq()`.

State and persistence behavior: Per-tfm state stores child crypto handles, the 4-byte IPsec salt for RFC wrappers, and GHASH precomputation. Per-request state stores aligned IVs, authentication tags, temporary scatterlists, and child requests. There is no durable persistence, but child transform lifetime and request memory alignment are critical.

Dependencies and integration points: Uses `crypto/internal/aead.h`, skcipher spawns, `gf128hash` GHASH helpers, scatterwalk utilities, `crypto/gcm.h` authsize/assoclen validators, and the template registry. It is a core provider for IPsec, storage, and other AEAD users requesting GCM by name.

Risks: IV and AAD layout is security-critical, especially RFC4106/RFC4543 salt and assoclen handling. Scatterlist forwarding/chaining errors can hash or encrypt the wrong bytes. Authentication tag comparison must remain constant-time. Counter/IV reuse is not prevented here and must be enforced by callers/protocols. Async completion paths must call the final tag operation exactly once.

Test signals: Crypto manager GCM vectors, RFC4106 and RFC4543 ESP vectors, in-place and out-of-place scatterlist tests, async child completion tests, invalid authsize/assoclen rejection, bad-tag `-EBADMSG` behavior, and module alias/template instantiation by `gcm(aes)`, `gcm_base(ctr(aes),ghash)`, `rfc4106(gcm(aes))`, and `rfc4543(gcm(aes))`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/gcm.c -->
