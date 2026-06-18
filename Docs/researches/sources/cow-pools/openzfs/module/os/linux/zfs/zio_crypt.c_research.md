# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zio_crypt.c

## Purpose
Implements OpenZFS block encryption and authentication mechanics for Linux/OpenZFS, including key initialization/wrapping, HKDF-derived data keys, IV/salt/MAC encoding in block pointers and ZIL headers, AEAD encrypt/decrypt execution, HMAC-based authentication for non-encrypted metadata, indirect MAC checksums, and special layouts for ZIL and dnode blocks.

## Main APIs and Data
- `zio_crypt_table[]` maps ZFS encryption function IDs to ICP mechanism names, crypt type, key length, and user-visible algorithm names.
- `zio_crypt_key_init()`, `zio_crypt_key_destroy()`, `zio_crypt_key_wrap()`, `zio_crypt_key_unwrap()` manage dataset crypto keys and wrapping-key AEAD.
- `zio_crypt_key_get_salt()` and `zio_crypt_key_change_salt()` rotate salts after `zfs_key_max_salt_uses`, defaulting to 400,000,000 uses.
- `zio_do_crypt_data()` and `zio_do_crypt_abd()` are the primary block encryption/decryption entry points.
- `zio_crypt_encode_params_bp()`, `zio_crypt_decode_params_bp()`, `zio_crypt_encode_mac_bp()`, `zio_crypt_decode_mac_bp()`, `zio_crypt_encode_mac_zil()`, and `zio_crypt_decode_mac_zil()` serialize cryptographic metadata into on-disk structures.
- `zio_crypt_do_objset_hmacs()` computes portable and local objset MACs.
- `zio_crypt_do_indirect_mac_checksum()` and `_abd()` compute or verify indirect-block SHA512 checksums over child MAC/auth metadata.

## Control Flow
Key initialization generates a key GUID, master key, HMAC key, and initial salt, derives the current encryption key via HKDF-SHA512, and opportunistically creates ICP context templates. Key unwrap performs AEAD decryption of stored master/HMAC key material using wrapping-key AAD containing GUID, crypt algorithm, and key version, then derives a fresh current data key.

Block encryption chooses the key by comparing the block salt to the cached current salt. Matching salts use `zk_current_key`; older salts derive a temporary key from the master key. For simple blocks, `zio_crypt_init_uios_normal()` creates plaintext/ciphertext UIOs. For ZIL and dnode blocks, custom parsers split encrypted payload from plaintext authenticated data. `zio_do_crypt_uio()` then dispatches AES-CCM or AES-GCM through ICP. Large normal blocks may use QAT acceleration, falling back to software on failure.

Authentication is layered. Level-0 encrypted blocks store AEAD MACs in checksum words. Authenticated-but-not-encrypted metadata uses HMAC-SHA512. Indirect blocks carry SHA512 digests of child MAC/portable blk_prop data. Objsets maintain separate portable and local MAC roots so raw sends can preserve portable authentication while local user-accounting data remains host-local.

## Integration Points
This file sits below DMU/ZIO logic and is consumed by block I/O, raw send/receive, dataset encryption, ZIL, dnode, objset, and scrub/claim paths. It depends on SPL/ICP crypto APIs, HKDF, SHA2, ABD buffer borrowing, DMU object type rules, block pointer encoding macros, and optional QAT acceleration.

## Invariants and Edge Cases
- AES-GCM/CCM IV uniqueness is enforced by salt rotation plus random 96-bit IVs for non-dedup blocks.
- Dedup derives salt and IV from HMAC(plaintext), intentionally exposing equality only where dedup already does.
- Byte-order handling is explicit because blkptrs and objsets may be byteswapped below this layer.
- ZIL leaves `zil_chain_t` and write/clone block pointers plaintext but authenticates them as AAD.
- Dnode blocks leave core dnode fields and block pointers plaintext, encrypting only encrypted bonus buffers.
- Version 0 compatibility affects authenticated blk_prop padding and nonportable masking.
- Notable review point: `zio_crypt_key_init()` assigns `zk_hmac_key.ck_data` differently from unwrap path, using `&key->zk_hmac_key` instead of `key->zk_hmac_keydata`; this is security-sensitive and should be checked against upstream intent.

## Risks and Testing Signals
Primary risks are cryptographic metadata drift, endian/portable-field mismatches, ZIL/dnode parser mistakes, salt rotation races, and fallback differences between QAT and software crypto. Coverage should include encrypted dataset read/write, raw send/receive, dedup encryption, ZIL replay/claim, dnode bonus encryption, objset MAC verification, cross-endian import, key rewrap/unwrap, and negative MAC corruption tests.
