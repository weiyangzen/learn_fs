# sources/distributed-fs/ceph-client/crypto/essiv.c

## Purpose
`essiv.c` implements the `essiv(cipher,hash)` template for skcipher and dm-crypt-specific authenc AEAD uses. ESSIV derives an IV encryption key by hashing the data-encryption key and uses a block cipher to encrypt each request IV before passing it to the wrapped cipher.

## Important APIs, Types, And Functions
- `struct essiv_instance_ctx` stores either a skcipher or AEAD spawn plus selected ESSIV cipher and hash driver names.
- `struct essiv_tfm_ctx` stores the spawned child skcipher/AEAD, ESSIV block cipher, hash transform, and AEAD IV buffer offset.
- `essiv_skcipher_setkey()` sets the child key, hashes the key, and sets the ESSIV cipher key to the hash digest.
- `essiv_aead_setkey()` handles authenc key format, sets child AEAD key, hashes encryption key then authentication key into the ESSIV salt, and sets the ESSIV cipher key.
- `essiv_skcipher_crypt()` encrypts `req->iv` in place with the ESSIV cipher and forwards encrypt/decrypt to the child skcipher.
- `essiv_aead_crypt()` encrypts the IV and patches the dm-crypt AAD layout before forwarding to the child AEAD.
- `parse_cipher_name()` extracts the inner block cipher name from the child algorithm name.
- `essiv_supported_algorithms()` checks hash digest size fits the cipher key size, IV size equals cipher block size, and hash is unkeyed.
- `essiv_create()` supports both lskcipher/skcipher and authenc AEAD instantiation, validates children, fills instance metadata, and registers the instance.

## Control Flow
Template creation parses `essiv(inner,hash)` attributes, determines whether an lskcipher or AEAD instance is requested, spawns the inner algorithm, derives the underlying block cipher name from the inner algorithm's `cra_name`, looks up the hash, validates compatibility, records the hash driver name, and registers either a skcipher or AEAD instance.

At runtime, setkey configures both the child transform and ESSIV cipher. A skcipher request simply encrypts the IV and delegates. An AEAD request computes `ssize = assoclen - ivsize`, encrypts the IV, and either writes the IV into the destination AAD area for in-place/decrypt or constructs a temporary scatterlist that inserts the encrypted IV between the sector-number AAD and payload for out-of-place encryption. Temporary assoc copies are freed in completion or immediate-error paths.

## State And Persistence
Transform state persists child transform, ESSIV cipher, hash transform, and AEAD request layout offset. Per-request AEAD state may allocate a temporary `assoc` buffer for fragmented AAD; it is freed after completion. The encrypted IV mutates `req->iv` in place.

## Dependencies And Integration Points
The file depends on crypto authenc key extraction, skcipher/AEAD/hash/cipher internal APIs, scatterwalk, and dm-crypt/fscrypt ESSIV conventions. It imports `CRYPTO_INTERNAL` namespace and registers the `essiv` template. Testmgr includes `essiv(cbc(aes),sha256)` and `essiv(authenc(hmac(sha256),cbc(aes)),sha256)` vectors.

## Risks And Edge Cases
ESSIV is tightly coupled to child naming and dm-crypt AEAD AAD layout. `parse_cipher_name()` uses parenthesis parsing, so unusual algorithm names can fail. AEAD support is intentionally limited to `authenc(...)`. Hash digest size must exactly be a valid key size for the IV cipher, and IV size must equal block size. Out-of-place AEAD encryption must handle multi-entry AAD scatterlists; allocation uses `GFP_ATOMIC`, so memory pressure can fail requests.

## Test Signals
`testmgr.h` contains skcipher and AEAD ESSIV vectors, and `testmgr.c` maps both algorithm forms. Additional tests should cover unsupported hash/cipher combinations, keyed hash rejection, non-authenc AEAD rejection, fragmented AAD scatterlists, in-place versus out-of-place encryption, decrypt IV handling, and setkey failure propagation.
