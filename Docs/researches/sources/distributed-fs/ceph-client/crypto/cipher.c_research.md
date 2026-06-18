<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cipher.c -->
# sources/distributed-fs/ceph-client/crypto/cipher.c

## Purpose

`cipher.c` implements internal single-block cipher helper APIs: setkey with alignment handling, one-block encrypt/decrypt wrappers, and cloning of simple cipher transforms.

## Important APIs, Types, and Flow

`crypto_cipher_setkey()` validates key length against the algorithm's `cia_min_keysize` and `cia_max_keysize`. If the key pointer violates the transform alignmask, `setkey_unaligned()` allocates an aligned temporary buffer with `GFP_ATOMIC`, copies the key, invokes the algorithm setkey, and frees the temporary with `kfree_sensitive()`.

`cipher_crypt_one()` selects the algorithm encrypt or decrypt function. If source or destination is unaligned, it copies one block to an aligned stack buffer, runs the primitive in place, then copies to destination. Otherwise it calls the primitive directly. `crypto_cipher_encrypt_one()` and `crypto_cipher_decrypt_one()` export this behavior in the `CRYPTO_INTERNAL` namespace. `crypto_clone_cipher()` clones transforms for algorithms without `cra_init`, preserving flags and module references.

## State, Dependencies, and Integration

State is the underlying `crypto_tfm` and algorithm context. The file depends on internal cipher headers, allocation APIs, and `internal.h`. It is consumed by templates such as CMAC and CBC-MAC that need one-block cipher operations.

## Risks and Test Signals

Risks include alignment buffer sizing, stack buffer bounds for maximum block size, clone behavior for algorithms with initialization, and namespace-only consumers. Test signals include unaligned key/input/output cases, invalid key lengths, clone lifecycle tests, and template tests that exercise `crypto_cipher_encrypt_one()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cipher.c -->
