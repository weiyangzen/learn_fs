<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ccm.c -->
# sources/distributed-fs/ceph-client/crypto/ccm.c

## Purpose

`ccm.c` implements Counter with CBC-MAC AEAD templates: `ccm`, `ccm_base`, the IPsec `rfc4309` wrapper, and the `cbcmac` shash template used by CCM. It composes CTR-mode encryption with CBC-MAC authentication.

## Important APIs, Types, and Flow

`crypto_ccm_setkey()` sets the same key on child CTR skcipher and CBC-MAC ahash. `crypto_ccm_setauthsize()` accepts even tag sizes from 4 through 16. `crypto_ccm_auth()` formats the B0 block and associated-data length encoding, hashes AAD and plaintext with block padding, and returns a 16-byte MAC. `crypto_ccm_init_crypt()` validates `L'` in `iv[0]`, zeros the counter field, and constructs scatterlists that prepend the tag block before data for CTR processing.

Encryption computes CBC-MAC over plaintext, CTR-encrypts tag plus payload, then copies the requested tag length to the end of the destination. Decryption saves the incoming tag, CTR-decrypts tag plus ciphertext, recomputes CBC-MAC over plaintext, and compares tags. `crypto_ccm_create_common()` validates that the MAC is `cbcmac(...)`, the cipher is `ctr(...)`, both use the same underlying cipher, and CTR has 16-byte IV/block conventions.

`rfc4309` stores a three-byte nonce suffix in the key, builds a CCM child IV from nonce plus eight-byte packet IV, and moves the leading AAD bytes into child AAD. The `cbcmac` template wraps a single-block cipher as a block-only shash.

## State, Dependencies, and Integration

Tfm state stores child ahash/skcipher or child AEAD plus RFC4309 nonce. Request state stores formatted blocks, auth tag buffers, scatterlists, and embedded child requests. Dependencies include scatterwalk, internal AEAD/hash/skcipher/cipher APIs, and Crypto API templates.

## Risks and Test Signals

Risks include CCM length encoding overflow, AAD formatting, partial tag handling, IV mutation, RFC4309 AAD length restrictions, and async callback correctness. Test signals are NIST/RFC CCM vectors, RFC4309 vectors, invalid auth sizes, invalid IV `L'`, tag mismatch returning `-EBADMSG`, in-place/out-of-place operation, and template creation rejection for mismatched children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ccm.c -->
