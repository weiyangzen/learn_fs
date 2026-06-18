# sources/distributed-fs/ceph-client/net/ceph/crypto.c

## Purpose
Implements libceph cryptographic key handling, Ceph keyring integration, AES-CBC and AES256-KRB5 encryption/decryption wrappers, HMAC support, and registration of the kernel `ceph` key type.

## Important APIs, Types, and Functions
Public APIs are `ceph_crypto_key_prepare()`, `ceph_crypto_key_clone()`, `ceph_crypto_key_decode()`, `ceph_crypto_key_unarmor()`, `ceph_crypto_key_destroy()`, `ceph_crypt()`, `ceph_crypt_data_offset()`, `ceph_crypt_buflen()`, `ceph_hmac_sha256()`, `ceph_crypto_init()`, and `ceph_crypto_shutdown()`. Internal helpers include `set_aes_tfm()`, `set_krb5_tfms()`, `setup_sgtable()`, `teardown_sgtable()`, `ceph_aes_crypt()`, `ceph_krb5_encrypt()`, `ceph_krb5_decrypt()`, and key-type callbacks `ceph_key_preparse()`, `ceph_key_free_preparse()`, `ceph_key_destroy()`.

## Control Flow
Key preparation dispatches by type: none is a no-op, AES allocates `cbc(aes)` and sets the key, AES256KRB5 prepares HMAC state and per-usage AEAD transforms. Key decode reads type, creation timestamp, length, validates `CEPH_MAX_KEY_LEN`, copies key bytes, and zeroes the source. Unarmor base64-decodes a string then decodes a key from the binary payload.

`ceph_crypt()` dispatches encryption/decryption. AES applies PKCS#7-like padding on encrypt, builds an sg table over kmalloc or vmalloc buffers, runs synchronous skcipher CBC with a fixed Ceph IV, and strips padding on decrypt. KRB5 encryption/decryption builds sg tables and calls crypto KRB5 helpers, accounting for a confounder offset and HMAC length. HMAC-SHA256 returns zeros for none/AES and computes real HMAC for AES256KRB5. Module crypto init registers the `ceph` key type; shutdown unregisters it.

## State and Persistence
`struct ceph_crypto_key` owns key bytes and prepared transform pointers. The global `key_type_ceph` is registered during libceph init. Key material is freed with `kfree_sensitive()` and HMAC state is explicitly zeroed. No persistent storage is written.

## Dependencies and Integration Points
Depends on the kernel crypto API, KRB5 crypto helpers, scatterlist helpers, keyring API, Ceph armor/decode helpers, and libceph auth paths. CephX relies on usage-slot ordering when preparing keys.

## Risks
AES uses a fixed IV for protocol compatibility, so callers must understand the security model. `setup_sgtable()` handles vmalloc and linear buffers but returns `-EINVAL` for zero length. AES decrypt validates only padding shape. KRB5 transform preparation has a fixed transform array size; too many usages return `-EINVAL`. Key decode mutates input by zeroing decoded key bytes, so callers must not expect immutable input buffers.

## Test Signals
Decode and unarmor valid/invalid keys, enforce maximum key length, prepare AES and AES256KRB5 keys, encrypt/decrypt round trips over kmalloc and vmalloc buffers, padding edge cases at block boundaries, malformed padding rejection, KRB5 usage-slot bounds, keyring add/request/destroy lifecycle, failure injection for crypto allocation, and secret-zeroing checks.
