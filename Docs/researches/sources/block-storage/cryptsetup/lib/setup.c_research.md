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
