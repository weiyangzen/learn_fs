# sources/distributed-fs/ceph/src/client/FSCrypt.h

## Purpose
`FSCrypt.h` declares Linux-only fscrypt constants, helper functions, policy/context encoding, key store objects, encryption/decryption classes, and the `FSCrypt` facade used by `Client` and `Inode`.

## Important APIs, Types, and Functions
Constants define nonce size, HKDF contexts, 4 KiB block geometry, alignment, and maximum IO size. Inline helpers compute block starts, block numbers, offsets, alignment, and hex output. `ceph_fscrypt_key_identifier`, `FSCryptKey`, `FSCryptPolicy`, and `FSCryptContext` model key IDs and encoded policy/context metadata. `FSCryptDenc` is the abstract cipher base; `FSCryptFNameDenc` and `FSCryptFDataDenc` specialize name/symlink and data encryption. `FSCryptKeyHandler`, `FSCryptKeyStore`, and `FSCryptKeyValidator` manage master keys and epoch validity. `FSCrypt` initializes contexts and returns denc instances.

## Control Flow
Callers decode inode auth into an `FSCryptContext`, resolve a master key through `FSCryptKeyStore`, create the proper denc type, derive filename or data keys, then transform names or buffers. Policy encode/decode wraps a versioned envelope around fscrypt v2 fields plus context nonce.

## State and Persistence Behavior
Policy/context bytes are serializable into inode metadata. Key material and decrypted inode lists are memory-only and guarded by locks. `fscrypt_file` effective-size handling is on `Inode`, not in this header, but the data denc enforces block-aligned encrypted storage semantics.

## Dependencies and Integration Points
It depends on `fscrypt_uapi.h`, OpenSSL headers, Ceph mutexes and bufferlist, and Linux build guards. `Client.h` exposes fscrypt public APIs only on Linux and embeds an `FSCrypt` instance.

## Risks and Edge Cases
The declarations expose raw OpenSSL pointers and require destructor cleanup. Policy support is intentionally narrow: v2, AES-256-XTS contents, AES-256-CTS filenames. Callers must account for block alignment and missing keys. `FSCryptDecryptedInodes::open_inodes` is declared but not actively managed in visible code.

## Test Signals
Compile on Linux and non-Linux, policy encode/decode compatibility, key spec validation, denc setup for supported/unsupported ciphers, alignment helper boundary cases, and encrypted read/write max IO sizing.
