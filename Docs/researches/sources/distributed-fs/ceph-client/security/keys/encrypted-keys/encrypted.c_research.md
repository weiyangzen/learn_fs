<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/encrypted-keys/encrypted.c -->
# sources/distributed-fs/ceph-client/security/keys/encrypted-keys/encrypted.c

## Purpose
`encrypted.c` implements the Linux `encrypted` key type. It stores secret key material in kernel memory as decrypted bytes but exports/imports it as a text datablob encrypted with a derived AES-CBC key and authenticated with an HMAC derived from a trusted or user master key. The file supports `new`, `load`, and `update` commands plus `default`, `ecryptfs`, and `enc32` payload formats.

## Important APIs, Types, and Functions
The public integration point is `struct key_type key_type_encrypted`, registered by `init_encrypted()` and removed by `cleanup_encrypted()`. Key type methods are `encrypted_instantiate()`, `encrypted_update()`, `encrypted_read()`, and `encrypted_destroy()`. Parsing and validation are handled by `datablob_parse()`, `valid_master_desc()`, and `valid_ecryptfs_desc()`. Payload sizing and layout are handled by `encrypted_key_alloc()` and `__ekey_init()`. Crypto work flows through `get_derived_key()`, `init_skcipher_req()`, `derived_key_encrypt()`, `derived_key_decrypt()`, `datablob_hmac_append()`, and `datablob_hmac_verify()`.

## Control Flow
Instantiation copies the user datablob, tokenizes it, allocates a single `encrypted_key_payload` allocation sized for clear payload, text datablob, encrypted bytes, and HMAC, then either decrypts a loaded blob, decodes caller-supplied cleartext when `user_decrypted_data` permits it, or fills decrypted bytes and IV from the RNG. Read obtains the master key, derives an encryption key, encrypts the in-memory payload, appends an HMAC over the formatted datablob, formats bytes as hex, and copies the result to the keyctl caller. Update is intentionally narrow: it validates that only the master-key description changes within the same `trusted:` or `user:` family, clones the old payload and IV, publishes the new payload with RCU, and frees the old one after grace period.

## State and Persistence
All state is kernel-resident key payload state. `epayload->payload_data` holds decrypted material or an eCryptfs auth token, while `format`, `master_desc`, `datalen`, `iv`, and `encrypted_data` point inside the same allocation. The encrypted export is not stored durably by this file; userspace receives it through `read` and may later pass it to `load`. Master key semaphores are held while using trusted/user key payload pointers, and sensitive buffers are zeroed through `kfree_sensitive()` or `memzero_explicit()`.

## Dependencies and Integration Points
This file depends on the key subsystem, `trusted` and `user` key types, eCryptfs format helpers, kernel RNG, SHA-256/HMAC helpers, and the skcipher API for `cbc(aes)`. It integrates with key quotas through `key_payload_reserve()`, with RCU through `rcu_assign_keypointer()` and `call_rcu()`, and with module/key-type registration.

## Risks
The load path is format-sensitive: IV, separator byte, encrypted data, and HMAC lengths must match exactly. The datablob uses pointers into one allocation, so size and offset calculations are security critical. CBC padding is implemented through scatterlists with zero-page or throwaway padding; off-by-one errors can corrupt adjacent payload state. Debug dump helpers can expose key material if enabled. Allowing user-supplied decrypted data is gated by config/module parameter and must remain disabled unless the deployment accepts that trust boundary.

## Test Signals
Exercise `keyctl add encrypted ... new`, `load`, `read`, and `update` for `trusted:` and `user:` masters. Include bad prefixes, empty descriptions, bad eCryptfs descriptions, malformed hex, wrong HMAC, mismatched lengths, revoked master keys, missing crypto transform, quota failures, `enc32` length boundaries, and update attempts that change master type. Crypto self-tests should verify read-then-load round trips and that HMAC failures occur before decryption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/encrypted-keys/encrypted.c -->
