# Group Research: group_276_cryptsetup_sources_block_storage_cryptsetup_lib_setup_c_sources_bloc_74fb0d543dd1

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/setup.c -->
# File Research: sources/block-storage/cryptsetup/lib/setup.c

## Purpose

`setup.c` is the central libcryptsetup API implementation and dispatch layer. It owns the public `struct crypt_device` context, routes operations by crypt type, coordinates metadata loading/formatting, activates and reloads device-mapper targets, handles keyslot/token/keyring operations, and exposes getters/status/reporting helpers for PLAIN, LUKS1, LUKS2, LOOPAES, VERITY, TCRYPT, INTEGRITY, BITLK, and FVAULT2.

## Core Structures And State

- `struct crypt_device` stores the active type string, data and metadata `struct device` handles, optional in-memory volume key, RNG/PBKDF settings, compatibility flags, keyring-link settings, LUKS2 storage sizing hints, memory-hard PBKDF serialization state, and a large union of per-format metadata.
- The per-format union keeps native headers and derived runtime fields: LUKS1 header plus cipher spec, LUKS2 header plus cached cipher buffers/keyslot cipher/reencryption handle, PLAIN/LOOPAES params, VERITY root hash/FEC state, TCRYPT params/header, INTEGRITY journal keys and flags, BITLK metadata, FVAULT2 metadata, or anonymous active-device fields.
- Global process-scope settings include debug/log callbacks, metadata locking enablement, cached kernel keyring support, and whether volume keys may be passed to dm-crypt through kernel keyrings.

## Initialization, Loading, And Context Recovery

- `crypt_init()` allocates a zeroed context, allocates the initial device handle, initializes the dm backend, and chooses the default RNG.
- `init_crypto()` initializes RNG and crypto backends once, logging backend and kernel details.
- `crypt_set_data_device()` and `_crypt_set_data_device()` split detached metadata/data device handling, preserve the original metadata device, verify data device size, and apply LUKS2 sector size to the data device.
- `crypt_load()` is the main metadata loader. It resets transient anonymous state and dispatches to `_crypt_load_luks`, `_crypt_load_verity`, `_crypt_load_tcrypt`, `_crypt_load_integrity`, `_crypt_load_bitlk`, or `_crypt_load_fvault2`.
- `_crypt_load_luks()` probes LUKS version, initializes PBKDF defaults, loads LUKS1 or LUKS2 metadata, updates cipher specs/hash settings, and can run repair-mode loads.
- `crypt_init_by_name_and_header()` reconstructs a context from an active dm mapping. It reads dm UUID/type, initializes from data or detached header device, and dispatches to active-target parsers for crypt/linear, verity, or integrity targets.
- `_init_by_name_crypt()` reconstructs PLAIN, LOOPAES, LUKS, TCRYPT, BITLK, and FVAULT2 state from dm-crypt/linear targets, including dependency lookup for LUKS2 detached-header cases and special dm-integrity-under-dm-crypt handling.

## Formatting Paths

- `_crypt_format()` implements public `crypt_format()` dispatch. It initializes crypto, checks that the context is unformatted, and calls the type-specific formatter.
- `_crypt_format_plain()` validates cipher/mode/key size/sector size and initializes a headerless PLAIN context.
- `_crypt_format_luks1()` validates metadata/data devices, zoned/DAX constraints, data alignment, PBKDF/hash settings, detached data devices, cipher availability, header generation, header area wipe, and LUKS1 header write.
- `_crypt_format_luks2()` handles LUKS2 software encryption formatting, including detached data devices, sector-size autodetection, integrity parameter validation, metadata/keyslot/data offset sizing, header generation, optional inline hardware tags requirement, labels/subsystem, header wipe/write, and optional dm-integrity formatting.
- `crypt_format_luks2_opal()` formats LUKS2 with OPAL hardware encryption. It validates admin/user keys, OPAL geometry and alignment, computes locking range size/offset, creates LUKS2 metadata with OPAL segment fields, sets OPAL requirement flags, programs OPAL ranges under an exclusive OPAL lock, handles optional software encryption and integrity, writes metadata, and attempts OPAL range reset plus metadata cleanup on failure.
- `_crypt_format_verity()` validates block sizes and hash/FEC offsets, computes data size and root hash, checks data/hash/FEC overlap, optionally creates the hash/FEC areas, generates UUID, and writes the verity superblock unless headerless mode is requested.
- `_crypt_format_integrity()` wipes the initial sectors, validates UUID/key-size constraints, records journal and integrity settings, derives/generates integrity keys, and calls `INTEGRITY_format()`.
- `crypt_format_inline()` supports inline integrity for standalone INTEGRITY and LUKS2, requiring compatible device inline DIF/NOP fields and matching sector/tag sizes.

## Device Activation, Reload, Resize, Suspend, And Deactivation

- `PLAIN_activate()` builds a dm-crypt target for headerless PLAIN mappings and delegates to `create_or_reload_device()`.
- `_activate_by_volume_key()` dispatches activation to the proper backend: PLAIN, LUKS1, LUKS2, VERITY, TCRYPT, INTEGRITY, BITLK, or FVAULT2.
- `crypt_activate_by_keyslot_context()` is the main activation/checking entry point. It validates flags, obtains keys through a `crypt_keyslot_context`, handles LOOPAES passphrase parsing, LUKS2 reencryption multi-key cases, TCRYPT header-derived activation, BITLK/FVAULT2/VERITY/INTEGRITY keys, key verification, OPAL key splitting, kernel keyring uploads, optional user keyring linking, and rollback/unlink on failure.
- `_activate_luks2_by_volume_key()` routes LUKS2 activation through reencryption recovery/activation if reencryption metadata is active, otherwise through normal `LUKS2_activate()`.
- `create_or_reload_device()` and `create_or_reload_device_with_integrity()` centralize dm target creation versus refresh reload, enforce active-name collision checks, adjust sizes against backing devices, and handle stacked dm-integrity subdevices.
- `_reload_device()` and `_reload_device_with_integrity()` compare requested and existing dm tables before refresh, preserve read-only flags, support keyring/direct-key transitions for LUKS2, and use careful suspend/resume ordering for crypt-over-integrity reloads.
- `crypt_compare_dm_devices()` validates dm target equivalence across type UUIDs, cipher specs, volume keys/key descriptions, integrity settings, offsets, sector sizes, tag sizes, segment count, and backing devices.
- `crypt_resize()` supports resizing crypt and integrity targets, rejects unsupported types and LUKS2 static/integrity-protected layouts, resizes loop backing devices when applicable, recalculates dm-integrity sizes through kernel reload, verifies sector/logical-block alignment, and refreshes the dm table.
- `crypt_suspend()` verifies LUKS UUID/type, rejects mismatched OPAL-only headers, suspends the crypt target with key wipe where possible, optionally suspends the underlying integrity device, drops uploaded kernel keys, and locks OPAL ranges.
- `crypt_resume_by_keyslot_context()` obtains and verifies a LUKS volume key, then resumes LUKS1 or LUKS2. LUKS2 resume handles OPAL unlocking, custom keyring links, integrity subdevice resume, and key reinstatement.
- `crypt_deactivate_by_name()` supports normal, force, deferred, and deferred-cancel deactivation. It rejects deferred OPAL deactivation, detects holders unless forced/deferred, delegates LUKS2 deactivation when possible, uses TCRYPT chain deactivation for TCRYPT, otherwise removes the dm device.

## Keyslot, Token, Keyring, And Volume Key Handling

- Keyslot APIs wrap context creation and dispatch into `crypt_keyslot_add_by_keyslot_context()`, `crypt_keyslot_change_by_passphrase()`, `crypt_keyslot_destroy()`, and LUKS-specific helpers.
- LUKS1 keyslot operations use `LUKS_set_key`, `LUKS_del_key`, and volume-key verification; LUKS2 operations additionally manage digest assignment, token assignment copy, keyslot swap, unbound/no-segment volume keys, new digest creation, and rollback on failure.
- `crypt_volume_key_get_by_keyslot_context()` retrieves LUKS keys, PLAIN hashed keys, VERITY root hash, TCRYPT reconstructed key material, BITLK keys, or FVAULT2 keys, with buffer sizing and fallback to an in-memory context key.
- `crypt_volume_key_verify()` checks supplied volume keys against LUKS1 or LUKS2 segment digests.
- Token APIs are LUKS2-only: JSON get/set, status/max, keyring token get/set, keyslot assignment/unassignment, and assignment checks.
- Kernel keyring support is cached by `kernel_keyring_support()`. `crypt_use_keyring_for_vk()` enables keyring use only for PLAIN/LUKS2 when supported and avoids old dm-crypt keyring bugs.
- Keyring helpers upload volume keys to the thread keyring, read user/logon keys by description/name, unlink uploaded keys, and optionally link activated volume keys into a caller-specified keyring.

## Reporting And Getters

- `crypt_status()` reports active/busy/inactive/invalid from dm status.
- `crypt_dump()` dispatches to LUKS1, LUKS2, VERITY, TCRYPT, INTEGRITY, BITLK, or FVAULT2 dump routines; `crypt_dump_json()` is LUKS2-only.
- Getter APIs expose cipher spec/name/mode, integrity name/key/tag size, sector size, UUID, data and metadata device names, volume key sizes, old reencryption key size, OPAL key size/type/SUM support, keyslot encryption/PBKDF/priority/area, metadata sizes, data/IV offsets, active device offsets/flags, verity info/repair count, integrity info, labels, subsystem, type, and type defaults.
- `crypt_convert()` converts LUKS1/LUKS2 in either direction, rolls back in-memory LUKS2 metadata on failure, frees old type state, and reloads the requested type.
- `crypt_free()` tears down dm/backend state, frees format-specific allocations, devices, PBKDF/user key strings, volume keys, and wipes the context because some union members can contain key material.
- The destructor `libcryptsetup_exit()` unloads external tokens and shuts down crypto/random backends.

## Notable Invariants And Error Handling

- Most public operations validate initialized type and supported requirements via `onlyLUKS*()` helpers; LUKS2 operations check OPAL, inline-HW-tags, or online-reencryption requirements as appropriate.
- Detached header handling consistently treats `metadata_device ?: device` as metadata and `device` as ciphertext data.
- Formatting and activation paths reject zoned header devices, unsupported sector sizes, unaligned data sizes, header/data overlap, active device collisions, and unsupported type/flag combinations.
- Failure paths generally free generated headers/keys, reset type state, drop uploaded keyring keys, unlink custom keyring keys, remove partially-created dm-integrity subdevices, reset OPAL ranges when possible, and roll back LUKS2 in-memory metadata after failed metadata mutations.

## Dependencies

This file orchestrates almost every libcryptsetup subsystem: LUKS1, LUKS2, LOOPAES, VERITY, TCRYPT, INTEGRITY, BITLK, FVAULT2, dm target helpers, device helpers, locking, keyslot contexts, keyrings, crypto backend/PBKDF/RNG, OPAL support, and gettext/logging utilities.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/setup.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/tcrypt/tcrypt.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/tcrypt/tcrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/tcrypt/tcrypt.h -->
# File Research: sources/block-storage/cryptsetup/lib/tcrypt/tcrypt.h

## Purpose

`tcrypt.h` declares the internal TCRYPT/VeraCrypt header layout, constants, forward declarations, and function interface used by `setup.c` and `tcrypt.c`.

## Constants

- Header sizing:
  - `TCRYPT_HDR_SALT_LEN` is 64 bytes.
  - `TCRYPT_HDR_IV_LEN` is 16 bytes.
  - `TCRYPT_HDR_LEN` is 448 encrypted-header bytes.
  - `TCRYPT_HDR_KEY_LEN` is 192 bytes of derived header key material.
  - `TCRYPT_HDR_MAGIC_LEN` is 4 bytes.
- Magic values:
  - `TCRYPT_HDR_MAGIC` is `"TRUE"`.
  - `VCRYPT_HDR_MAGIC` is `"VERA"`.
- Header offsets:
  - old hidden header offset: `-1536`;
  - current hidden header offset: `65536`;
  - hidden backup offset: `-65536`;
  - normal backup offset: `-131072`;
  - system header offset: `31744`.
- Key material:
  - `TCRYPT_LRW_IKEY_LEN` is 16 bytes.
  - TrueCrypt keyfile/passphrase pool length is 64 bytes.
  - VeraCrypt pool length is 128 bytes.
  - keyfile read cap is 1 MiB.
- Header flags define system and nonsystem volume bits.

## Header Layout

- `struct tcrypt_phdr` is packed and exactly 512 bytes in practice: 64-byte salt followed by a 448-byte encrypted/plain union.
- The decrypted header view contains:
  - 4-byte magic;
  - TCRYPT and required-driver versions;
  - CRC32 of key area;
  - reserved timestamp fields;
  - hidden volume size and visible volume size;
  - master-key offset and size;
  - flags and sector size;
  - reserved bytes;
  - header CRC32;
  - 256-byte encrypted-volume key pool.
- Multi-byte on-disk fields are stored big-endian and converted by `TCRYPT_hdr_from_disk()` in `tcrypt.c`.

## Interface

The header exposes internal TCRYPT operations:

- `TCRYPT_read_phdr()` reads and decrypts a TCRYPT/VeraCrypt header using `crypt_params_tcrypt`.
- `TCRYPT_init_by_name()` reconstructs TCRYPT parameters/header state from an active dm mapping.
- `TCRYPT_activate()` creates the required dm-crypt mapping chain.
- `TCRYPT_deactivate()` removes the public mapping and private subdevices.
- `TCRYPT_get_data_offset()` and `TCRYPT_get_iv_offset()` compute dm offsets for normal, hidden, legacy, and system layouts.
- `TCRYPT_get_volume_key()` exports reconstructed volume key material.
- `TCRYPT_dump()` prints decoded TCRYPT/VeraCrypt metadata.

## Dependencies

The file forward-declares `crypt_device`, `crypt_params_tcrypt`, `dm_target`, `volume_key`, and `device`, keeping the TCRYPT interface internal and avoiding heavy includes beyond `<stdint.h>`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/tcrypt/tcrypt.h -->