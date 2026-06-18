# File Research: sources/block-storage/cryptsetup/lib/tcrypt/tcrypt.c

## Purpose

`tcrypt.c` implements TrueCrypt-compatible and VeraCrypt-compatible volume handling for libcryptsetup. It reads and decrypts TCRYPT/VeraCrypt headers, tries supported PBKDF/cipher combinations, derives mapping keys, activates chained dm-crypt mappings, reconstructs active mappings, deactivates TCRYPT subdevice chains, computes data/IV offsets, exports the volume key, and dumps header information.

## KDF And Cipher Tables

- `tcrypt_kdf[]` enumerates supported PBKDF2 variants: TrueCrypt RIPEMD160/SHA512/Whirlpool/SHA1 legacy modes and VeraCrypt SHA512/Whirlpool/SHA256/BLAKE2s-256/RIPEMD160/Stribog512 modes.
- VeraCrypt entries include PIM constants/multipliers. When a PIM is supplied, TrueCrypt KDFs are skipped and iteration counts are derived from the VeraCrypt formula.
- `struct tcrypt_alg` describes one cipher component: backend name, key size, IV/tweak size, offsets inside the TCRYPT key pool, and extra key material.
- `struct tcrypt_algs` describes a whole cipher chain: legacy flag, chain count, total chain key size, public cipher-chain name, dm mode, and up to three component ciphers.
- `tcrypt_cipher[]` covers XTS chains, LRW chains, and legacy CBC/TCW/CBCI chains, including AES, Serpent, Twofish, Camellia, Kuznyechik, CAST5, 3DES, and Blowfish variants. Unsupported kernel LRW Blowfish combinations are left commented out.

## Header Decryption And Validation

- `TCRYPT_read_phdr()` reads the 512-byte physical header from the selected offset:
  - system header at `TCRYPT_HDR_SYSTEM_OFFSET`, optionally on the base disk for partitions;
  - hidden header at current or old hidden offsets;
  - backup hidden or normal backup offsets;
  - normal header at offset zero.
- `TCRYPT_init_hdr()` builds the password/keyfile pool, enforces TrueCrypt/VeraCrypt passphrase size rules, folds keyfile CRC output into the pool, combines passphrase bytes, tries allowed KDFs, decrypts the header under each allowed cipher chain, then normalizes the decrypted header.
- `TCRYPT_decrypt_hdr()` iterates cipher-chain candidates, filters by requested cipher and legacy/VeraCrypt flags, decrypts a working copy, and accepts `TRUE` or VeraCrypt `VERA` magic.
- `TCRYPT_decrypt_hdr_one()` handles single component decryptions. It strips the mode suffix, prepares IVs/tweak keys, removes CBC whitening where needed, special-cases little-endian Blowfish CBC, initializes backend ciphers, and decrypts the 448-byte encrypted header area.
- `TCRYPT_decrypt_cbci()` implements outer CBC for chained ciphers directly with ECB backend ciphers because the backend does not provide this composite mode.
- `TCRYPT_hdr_from_disk()` verifies header CRC and key CRC, converts big-endian fields to CPU endianness, fills default `mk_offset` and sector size if absent, and records the selected hash, cipher, mode, and key size in `crypt_params_tcrypt`.
- Sensitive buffers such as derived keys, IVs, keyfile data, CRC state, and temporary decrypted headers are zeroed before release.

## Keyfile And Password Pool Logic

- `TCRYPT_pool_keyfile()` reads up to `TCRYPT_KEYFILE_LEN` bytes from each keyfile, computes rolling CRC32 bytes, and adds those bytes into the key pool modulo either the TrueCrypt 64-byte or VeraCrypt 128-byte pool length.
- VeraCrypt mode may use a 128-byte keyfile pool when passphrase size exceeds the TrueCrypt limit.
- If keyfiles are supplied, the passphrase pool length is promoted to the maximum pool size; passphrase bytes are added to the existing keyfile-derived pool.

## Activation And Active Mapping Recovery

- `TCRYPT_activate()` validates the loaded header, rejects unsupported sector sizes and legacy `-tcrypt` kernel modes, resolves required dm-crypt feature flags, computes mapping size from normal/hidden/system header fields, adjusts offsets, and creates one dm-crypt target per cipher-chain component.
- Chained cipher activation creates private intermediate mappings named `<name>_2`, `<name>_1`, etc., and the final public mapping named `name`. Each layer uses `TCRYPT_copy_key()` to extract the component key material from the header master-key pool.
- System encryption offset handling is intentionally heuristic: it distinguishes partition devices, partition images, whole-device mappings, and missing partition information, logging fallback choices when it cannot determine the original partition offset.
- Activation checks kernel support for `plain64` or `tcw` compatible mapping if dm creation fails.
- `TCRYPT_init_by_name()` reconstructs TCRYPT parameters from an active dm-crypt chain. It parses the first target cipher/mode, walks expected subdevices with `TCRYPT_status_one()`, rebuilds the cipher chain string and total key size, verifies it against `tcrypt_cipher[]`, and fills params/header fields.
- `TCRYPT_status_one()` validates subdevice UUID relation, appends component cipher names, accumulates key size, updates `mk_offset`, and follows the data-device pointer down the chain.

## Deactivation

- `TCRYPT_deactivate()` removes the public mapping, then removes up to two private chained subdevices using `TCRYPT_remove_one()`.
- `is_tcrypt_subdev()` verifies subdevice UUIDs against the base UUID. It supports both current `SUBDEV-` UUID naming and older direct UUID-prefix behavior for compatibility.

## Offsets, Keys, And Dumping

- `TCRYPT_get_data_offset()` computes the dm data offset. It accounts for unloaded active-device contexts, system headers, XTS legacy version behavior, hidden volumes, old hidden offsets, and device-size-dependent hidden-volume placement.
- `TCRYPT_get_iv_offset()` returns XTS data offset, zero for LRW, or `mk_offset` for CBC-like modes.
- `TCRYPT_get_volume_key()` reconstructs an exported concatenated volume key by copying each cipher component key in chain order into a safe allocation.
- `TCRYPT_dump()` prints header type, version, required driver version, flags, sector size, master-key offset, volume sizes, PBKDF hash, cipher chain, cipher mode, and master-key bit length.

## Dependencies

This file depends on libcryptsetup public/internal types, crypto backend cipher/PBKDF/CRC helpers, safe allocation/memzero helpers, device open/read helpers, dm target creation/removal/query helpers, active device UUID conventions, and partition/device-offset utilities.
