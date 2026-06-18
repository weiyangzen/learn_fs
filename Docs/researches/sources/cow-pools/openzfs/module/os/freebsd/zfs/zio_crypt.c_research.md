# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zio_crypt.c

Read completely: 1813 lines.

This is the FreeBSD/OpenCrypto implementation of ZFS encryption parameter handling, authenticated encryption, wrapping/unwrapping dataset keys, block pointer salt/IV/MAC encoding, and authentication checksums for encrypted datasets.

Key responsibilities:
- Defines the supported encryption table for AES-CCM and AES-GCM key sizes, along with `inherit`, `on`, and `off` pseudo-values.
- Creates, unwraps, wraps, rotates, and destroys `zio_crypt_key_t` state, including master key data, HMAC key data, current HKDF-derived encryption key, salt, key GUID, and FreeBSD crypto sessions.
- Enforces salt rotation after `zfs_key_max_salt_uses` to bound IV/key reuse risk.
- Generates random IVs for normal encrypted writes and deterministic HMAC-derived salt/IV pairs for encrypted dedup.
- Encodes/decodes salt, IV, and MAC fields into block pointers and ZIL headers with explicit byte-swap handling.
- Computes HMACs for objset, dnode, indirect-block, and unencrypted authenticated metadata.
- Builds FreeBSD `zfs_uio_t`/`struct uio` layouts for normal data, ZIL blocks, and dnode blocks, then invokes `freebsd_crypt_uio()`.

Important implementation details:
- The top comment is essential design documentation for on-disk encryption: IV storage in DVA[2]/`blk_fill`, salt in DVA[2], MAC in the upper checksum words, object HMACs, ZIL plaintext/AAD exceptions, dnode bonus-buffer encryption, objset portable/local MACs, and dedup-derived IV/salt.
- `zio_crypt_key_init()` generates key GUID, master key, HMAC key, salt, derives `zk_current_keydata` through HKDF-SHA512, initializes `zk_current_key`, and opens an OpenCrypto session. The unwrap path rebuilds the same state from encrypted key material and generates a fresh salt.
- `zio_do_crypt_uio_opencrypto()` maps OpenCrypto errors to `EIO` on encryption and `ECKSUM` on decryption/authentication failure.
- FreeBSD OpenCrypto uses one in/out buffer, so key wrapping and data encryption copy plaintext/ciphertext into the target buffer and arrange AAD before encrypted iovecs.
- `zio_crypt_bp_zero_nonportable_blkprop()` defines which block pointer properties participate in portable MACs and preserves compatibility with version 0 crypt keys.
- ZIL handling encrypts sensitive record payloads but leaves the chain header and write/clone block pointers as AAD.
- Dnode handling leaves the core dnode and block pointers plaintext/AAD, encrypting only encrypted bonus buffers.
- `zio_do_crypt_data()` selects either the current cached key/session or a temporary HKDF-derived key when decrypting blocks with an older salt.

Dependencies and interactions:
- Depends on DMU, dnode, objset, ZIL, ABD, SHA2/HMAC, HKDF, FreeBSD OpenCrypto glue, and ZFS block pointer macros.
- Called by the ZIO encryption pipeline to transform ABDs and linear buffers.
- Objset/dnode authentication must match raw send/receive portability rules, so this file is tightly coupled to on-disk format compatibility.

Reliability/security notes:
- Cryptographic correctness depends on never reusing salt/IV pairs for non-dedup writes and on preserving exact AAD/MAC field normalization across byte orders.
- Several paths intentionally support legacy key version 0 for read-only import or rewrap scenarios.
- Error cleanup zeroes temporary key material and frees uio/auth buffers. The `zio_crypt_key_init()` HMAC `ck_data` assignment differs from the unwrap path and is worth verifying against the corresponding struct definition/upstream when auditing this copy.
