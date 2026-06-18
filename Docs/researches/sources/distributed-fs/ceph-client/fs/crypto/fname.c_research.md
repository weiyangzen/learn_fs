# sources/distributed-fs/ceph-client/fs/crypto/fname.c

Purpose: implements fscrypt filename encryption/decryption, encrypted filename sizing and buffers, no-key name presentation and lookup, name matching, SipHash dirhash calculation, and encrypted dentry revalidation.

Important APIs/types/functions: `struct fscrypt_nokey_name` encodes dirhash, up to 149 ciphertext bytes, and optional SHA-256 for long ciphertext names, then base64url encodes to stay within `NAME_MAX`. `fscrypt_fname_encrypt()` pads and encrypts plaintext filenames. `fname_decrypt()` decrypts and trims NUL padding. `fscrypt_fname_encrypted_size()` computes padded encrypted size. `fscrypt_fname_disk_to_usr()` decrypts when the key is available or emits a no-key encoded name. `fscrypt_setup_filename()` prepares lookup/create disk names from user names. `fscrypt_match_name()` compares full disk names or long no-key hashes. `fscrypt_fname_siphash()` calculates keyed plaintext dirhashes. `fscrypt_d_revalidate()` invalidates no-key dentries after keys appear.

Control flow: create/lookup calls `fscrypt_setup_filename()`. With a key, plaintext is padded to at least 16 bytes and policy padding, encrypted with IV index 0, and used as the disk name. Without a key, lookup decodes the presented no-key name and either reconstructs the full ciphertext or stores prefix/hash data for matching. Directory listing calls `fscrypt_fname_disk_to_usr()` to present decrypted or encoded names.

State and persistence: transient buffers in `fscrypt_name` and `fscrypt_str`; persistent ciphertext names live in the filesystem directory entries. Dentries may be flagged `DCACHE_NOKEY_NAME`.

Dependencies/integration: fscrypt keysetup, skcipher crypto, SHA-256, base64url, SipHash, VFS dentry validation, and filesystem directory lookup code.

Risks: no-key names must be unambiguous, legal path components, and no longer than `NAME_MAX`. Short ciphertext below the minimum indicates corruption (`-EUCLEAN`). RCU revalidation must return `-ECHILD` because key lookup can sleep. Padding policy changes affect on-disk compatibility.

Test signals: filename round trips for lengths around 1, 16, padding boundaries, and `NAME_MAX`; listing without keys; lookup/delete by no-key names; long-name SHA-256 matching; dirhash/minor hash propagation; key-added dentry invalidation; dot/dotdot handling; and malformed base64/no-key names.
