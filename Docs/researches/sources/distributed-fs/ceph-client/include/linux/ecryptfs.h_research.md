# sources/distributed-fs/ceph-client/include/linux/ecryptfs.h

## Purpose
This header defines eCryptfs shared kernel/user authentication token structures, version constants, feature bits, cipher identifiers, key sizes, and passphrase/private-key token layouts.

## Important APIs, types, and functions
Version constants include major/minor and supported file version. Feature bits advertise passphrase, pubkey, plaintext passthrough, policy, xattr, multikey, devmisc, HMAC, filename encryption, and GCM support. Size constants define password, salt, signature, key, encrypted key, and PKI-name limits. Cipher constants mirror RFC2440 values.

Structures include `struct ecryptfs_session_key`, `struct ecryptfs_password`, `enum ecryptfs_token_types`, `struct ecryptfs_private_key`, and packed `struct ecryptfs_auth_tok`. Session-key flags indicate whether user space should decrypt/encrypt and whether decrypted/encrypted key data is present. Password tokens carry hash parameters, session-key encryption key, hex signature, and salt. Private-key tokens carry key size, signature, PKI type, and flexible data.

## Control flow, state, and persistence
There is no code, but the structs are persistent ABI data exchanged between kernel and user space and stored or referenced in keyrings/auth flows. The packed auth token layout is especially ABI-sensitive.

## Dependencies and integration points
It integrates with eCryptfs mount helpers, key management, sysfs feature reporting, cryptographic token parsing, and encrypted filesystem metadata handling.

## Risks and test signals
Risks include ABI layout changes, exposing decrypted key material, buffer-size mistakes around hex signatures and salts, and accepting unsupported cipher/version combinations. Tests should cover struct size/layout compatibility, passphrase and private-key token parsing, feature-bit reporting, key length bounds, and secure zeroing in implementation code that handles these structures.
