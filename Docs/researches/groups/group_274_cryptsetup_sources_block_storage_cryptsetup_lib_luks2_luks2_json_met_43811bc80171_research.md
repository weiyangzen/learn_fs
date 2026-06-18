# Group Research: group_274_cryptsetup_sources_block_storage_cryptsetup_lib_luks2_luks2_json_met_43811bc80171

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/block-storage/cryptsetup`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_json_metadata.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_json_metadata.c

Central LUKS2 JSON metadata implementation for cryptsetup. This file owns JSON object access helpers, schema and cross-reference validation, header read/write/rollback, backup/restore, persistent config flags, mandatory requirements, metadata dumps, segment/key-size introspection, activation/deactivation assembly, unmet-requirement enforcement, metadata repair, and generic JSON utility helpers.

Key responsibilities:
- Provides reusable JSON helpers for numbered object keys, base64 hex printing, array membership/removal, uint64-as-string conversion, object lookup for keyslots/tokens/digests/segments, and deep-copy compatibility across json-c versions.
- Validates the full LUKS2 JSON metadata object in `LUKS2_hdr_validate()`, including requirements, tokens, digests, segments, keyslots, config, keyslot area intervals, JSON size, and type-specific keyslot validation.
- Enforces numeric-string conventions for offsets/sizes/iv tweaks, uint32 bounds for integer fields, no overlap among keyslot areas, no overlap among regular data segments, contiguous segment numbering, and the rule that only the last regular segment can be dynamic.
- Validates crypt segments against digest references, sector alignment, sector-size divisibility, optional integrity subobjects, and OPAL/hw-opal segment fields.
- Validates online reencryption metadata by checking backup-final and backup-previous segments and making sure regular segments match the backup state expected by the reencryption flags.
- Reads, writes, force-writes, rolls back, frees, labels, and UUID-mutates LUKS2 headers while maintaining an in-memory rollback JSON copy.
- Backs up and restores the complete binary metadata/keyslot-area span, with read/write locks, UUID/data-offset/area-size checks, confirmation prompts, and blocking of unsupported backup requirements.
- Stores and retrieves persistent activation flags such as discard, workqueue, journal, CPU, and high-priority settings.
- Stores, preserves, filters, versions, and reports mandatory requirements such as offline reencrypt, online reencrypt v1/v2/v3, inline hardware tags, and OPAL v1/v2.
- Dumps human-readable LUKS2 header details, including config flags/requirements, segments, keyslots, tokens, and digests, plus raw JSON debug output.
- Computes metadata size, keyslots size, total header/keyslot-area footprint, data size, data offset, sector size, ciphers, integrity parameters, and volume-key size by segment or digest.
- Builds dm targets for single-segment, multisegment, reload, integrity-backed, and OPAL-backed activation paths.
- Deactivates top-level LUKS2 devices and dependent devices, handles reencryption helper dependencies and suspended helpers, drops kernel keys, removes dm-integrity helpers, and relocks OPAL ranges when needed.
- Enforces unmet mandatory requirements for operations through `LUKS2_unmet_requirements()`.
- Repairs a known historical keyslot-KDF metadata glitch by delegating keyslot repair to type-specific handlers.
- Splits combined volume keys into software crypt and OPAL user-key portions for hw-opal-crypt segments.

Important behavior:
- LUKS2 encodes 64-bit numeric values as JSON strings; this file is the main conversion and validation boundary for those values.
- Validation ordering is deliberate: digests and segments are validated before keyslot areas, while keyslot implementation validation happens after basic JSON shape checks.
- Header writes first erase unused digests, then validate all metadata, then write to disk, then refresh rollback state.
- `LUKS2_hdr_read()` first tries under a read lock and retries under a write lock only when disk-header recovery is required.
- `LUKS2_hdr_restore()` refuses backups with online reencryption or inline hardware-tag requirements, then checks existing device metadata before replacing it.
- `LUKS2_get_default_segment()` prefers a segment flagged `backup-final` during reencryption-clean/crash states, otherwise segment 0.
- Persistent config flags are permissive on read: unknown strings are ignored with a verbose message, while known strings are translated into activation flags.
- Requirement writes preserve the currently stored version string for an already-present requirement bit where possible.
- Online reencryption status is inferred from the online-reencrypt requirement and whether any segment is marked `in-reencryption`.
- Activation blocks requirements that the requested path cannot satisfy; OPAL and inline hardware tag requirements are handled specially.
- OPAL activation validates locking range size, partition offset, lock state, and optionally dm-integrity size compatibility.
- Deactivation checks UUID compatibility with metadata, deactivates dependent devices after the top-level device, and handles OPAL relocking even when metadata is unavailable by guessing range 1 or partition number.

Dependencies:
- Relies heavily on `luks2_internal.h` helpers for disk header I/O, segment helpers, digest helpers, token helpers, reencryption helpers, area sizing, and device locks.
- Uses json-c object APIs and conditional compatibility for `json_object_object_add_ex` and `json_object_deep_copy`.
- Uses cryptsetup device abstractions, logging, locking, confirmation, metadata/data devices, dm target construction, dm reload/create/remove/query, kernel key dropping, and volume-key APIs.
- Uses integrity helpers from `../integrity/integrity.h` for dm-integrity backed activation.
- Uses OPAL helpers from `luks2/hw_opal/hw_opal.h` for hardware locking range validation, unlock, lock, and exclusive locks.
- Uses UUID parsing/generation through libuuid.

Notable risks:
- The validation code is security-critical; accepting malformed offsets, sizes, overlaps, requirement flags, or segment/keyslot references could corrupt metadata or expose wrong key material.
- Many helpers assume the caller has already validated JSON shape; calling them on unvalidated metadata can return default values or dereference missing fields in ways that only work under established call order.
- Header backup/restore performs large raw reads/writes of the metadata area; size mismatches or incomplete reads/writes are treated as hard failures, but the operation remains destructive after user confirmation.
- OPAL activation/deactivation has external hardware state and lock-state dependencies; error paths try to relock when appropriate but cannot guarantee recovery if the hardware command fails.
- The file has several `FIXME` notes around integrity compatibility, multisegment activation duplication, OPAL/segment restrictions, and deactivation dependency handling, marking known design debt.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_json_metadata.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_keyslot.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_keyslot.c

Generic LUKS2 keyslot dispatcher and policy layer. It selects keyslot handlers by JSON `type`, handles slot discovery, segment/digest association, default keyslot parameter construction, open/store/wipe flows, priorities, placeholder slots for LUKS1 conversion, validation across all keyslot types, repair delegation, finding slots by type, and swapping keyslot JSON objects.

Key responsibilities:
- Registers built-in keyslot handlers: the normal `luks2` handler and, when enabled, the `reencrypt` handler.
- Finds a keyslot handler from a keyslot JSON `type`, using the active LUKS2 header from the `crypt_device`.
- Finds an empty keyslot and optionally checks that binary keyslot area space exists for the requested key length.
- Determines whether a keyslot is usable for a requested segment by comparing the keyslot digest with the segment digest.
- Counts active keyslots for a segment and detects last active keyslot state for the default segment.
- Rejects keyslot encryption ciphers that are null, CAPI formatted, integrity-tagged, wrapped-key based, or unsupported by the crypto backend.
- Builds default keyslot parameters from the active device PBKDF and configured keyslot encryption.
- Reads PBKDF parameters out of keyslot JSON into a `crypt_pbkdf_type`.
- Classifies keyslot state as invalid, inactive, unbound, active last, or active.
- Extracts binary keyslot area offset and length from keyslot JSON.
- Opens a concrete keyslot through its handler, verifies the recovered volume key against the digest, and tags the volume key with digest id.
- Opens any slot by priority, trying preferred slots before normal slots and preserving better error semantics for bad passphrases versus unusable segment membership.
- Opens old/new reencryption segment keys using keyslot contexts, including the two-order retry wrapper for old/new contexts.
- Stores regular LUKS2 keyslots by allocating or updating JSON, validating metadata, then delegating encryption/storage to the handler.
- Stores reencryption keyslot data through the `reencrypt` handler.
- Wipes keyslot area contents, invokes type-specific wipe cleanup, deletes JSON, and writes metadata.
- Gets and sets keyslot priority, omitting the JSON field for normal priority.
- Creates invalid placeholder keyslots to reserve area locations during LUKS2 to LUKS1 conversion.
- Validates all keyslots, including type-specific handler validation, exactly-one-digest association for normal `luks2` slots, reencryption requirement/keyslot consistency, and the max-one-reencryption-slot rule.
- Delegates repair of known type-specific keyslot JSON issues.
- Finds the first keyslot with a requested type and swaps two keyslot JSON objects without updating external digest/token references.

Important behavior:
- `CRYPT_ANY_SLOT` opening respects priority ordering: preferred first, then normal; ignored priority slots are skipped by that path.
- `LUKS2_keyslot_for_segment()` treats `CRYPT_ANY_SEGMENT` as always acceptable, maps `CRYPT_DEFAULT_SEGMENT` through `LUKS2_get_default_segment()`, and returns `-ENOENT` when the keyslot is valid but not usable for the segment.
- Unbound keyslots are detected when their digest has no segment references or digest lookup fails.
- Keyslot open failures only log user-visible errors for memory errors and unexpected failures; bad passphrases and no-entry cases are left quiet for callers.
- Keyslot store validates both the type-specific keyslot object and the entire LUKS2 header before writing encrypted key material.
- Wipe takes the metadata device write lock, wipes the binary keyslot area if present, then lets the handler remove digest/token references.
- Placeholder keyslots deliberately use `key_size = -1` so they cannot pass validation or accidentally be persisted as a valid header.
- `LUKS2_keyslot_swap()` only swaps JSON bodies; callers must update digests, tokens, or other references themselves.

Dependencies:
- Depends on `luks2_internal.h` for metadata access, digest lookup/assignment, token assignment, area finding, header writes, and reencryption segment helpers.
- Depends on `keyslot_context.h` for keyslot context opening during reencryption.
- Calls concrete `keyslot_handler` methods: `alloc`, `update`, `open`, `store`, `wipe`, `dump`, `validate`, and `repair`.
- Uses cryptsetup volume-key APIs for allocation, linking multiple keys, key id tagging, and safe cleanup.
- Uses device write locks and secure wipe helpers for keyslot deletion.

Notable risks:
- Handler lookup depends on the active header stored in `crypt_device`; callers passing a separate `hdr` still rely on `crypt_get_hdr(cd, CRYPT_LUKS2)` in some paths.
- Several functions assume basic metadata validation already succeeded, especially JSON fields such as `keyslots`, `type`, `digests`, and segment/digest relationships.
- Priority and error handling are intentionally subtle to avoid exposing wrong-password behavior as no-slot behavior; changes could alter user-visible unlock semantics.
- Swapping keyslot JSON without reference updates is explicitly dangerous unless the caller also fixes digest/token associations.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_keyslot.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_keyslot_luks2.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_keyslot_luks2.c

Concrete handler for normal `luks2` keyslots. It derives a keyslot encryption key from the passphrase, AF-splits/merges the volume key using the LUKS1 anti-forensic splitter, encrypts/decrypts the AF material in the binary keyslot area, manages keyslot JSON allocation/update, dumps user-visible keyslot details, validates type-specific metadata, and repairs stale KDF fields.

Key responsibilities:
- Encrypts keyslot material to storage through `crypt_storage_wrapper`, using dm-crypt when possible and disabling dm-crypt for non-root callers.
- Decrypts keyslot material from storage under a metadata-device read lock.
- Parses KDF parameters from keyslot JSON for PBKDF2, Argon2i, and Argon2id, including base64 salt decoding and strict 32-byte salt length checking.
- Stores a keyslot by deriving the keyslot encryption key, AF-splitting the supplied volume key, wrapping the derived key into a `volume_key`, and encrypting the AF material to the configured area offset.
- Opens a keyslot by deriving the same keyslot key, decrypting AF material, and AF-merging it back into the volume key buffer.
- Serializes memory-hard KDF unlocks with `crypt_serialize_lock()` when the configured memory cost exceeds 32 MiB.
- Updates keyslot JSON by setting raw-area encryption/key size, benchmarking and writing current PBKDF settings, generating a fresh salt, and setting the AF hash.
- Allocates new keyslot JSON with `type = luks2`, volume key size, LUKS1 AF object, raw area object, and a free binary area found by `LUKS2_find_area_gap()`.
- Opens, stores, updates, wipes, dumps, validates, and repairs through the exported `luks2_keyslot` handler table.
- On wipe, removes references to the deleted keyslot from digests and tokens.
- Validates that `kdf`, `af`, and `area` subobjects have the expected type-specific fields and that KDF objects contain only the required fields for their type.
- Repairs historical KDF objects by deleting fields not valid for the current PBKDF2 or Argon2 type.

Important behavior:
- Salt is regenerated whenever keyslot JSON is updated, so updating PBKDF or area encryption parameters invalidates the old passphrase-derived wrapping key until key material is stored again.
- The stored `key_size` must match the supplied volume key length when writing, preventing accidental volume-key size mutation after allocation.
- Null keyslot encryption only allows an empty passphrase on open.
- `luks2_keyslot_store()` takes the LUKS2 device write lock, writes encrypted keyslot material first, then writes metadata.
- New allocation checks the JSON still fits in the metadata area after adding the keyslot object and removes the keyslot JSON if the update fails.
- AF stripes are currently fixed through `LUKS_STRIPES` in the cryptographic operations even though the JSON stores a stripes value and validation requires it.
- The dump path prints cipher, cipher key size, PBKDF settings, salt, AF stripes/hash, and binary area offset/length.

Dependencies:
- Depends on `luks2_internal.h` for header access, area finding, JSON helpers, device locking, metadata writes, digest/token assignment, and JSON size checks.
- Depends on `utils_storage_wrappers.h` and crypt storage wrappers for encrypted keyslot area I/O.
- Uses the LUKS1 AF splitter implementation from `../luks1/af.h`.
- Uses cryptsetup PBKDF, random, base64, hash-size, safe allocation, safe free, and volume-key APIs.
- Uses metadata-device read/write locks and block storage wrapper I/O.

Notable risks:
- The code has a `FIXME` around verifying key size against AF encrypted-key size, so key-size/AF-size assumptions are partly implicit.
- Keyslot JSON update benchmarks PBKDF using current crypt device settings; errors there abort allocation/update before key material is written.
- The validation function checks required shape but does not fully verify every numeric range or cryptographic algorithm availability; later open/store paths catch unavailable hash/cipher cases.
- The secure sequencing of encrypted material write and metadata write is sensitive: a failure between them can leave stale or unusable keyslot contents, so callers rely on higher-level recovery and validation.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_keyslot_luks2.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_keyslot_reenc.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_keyslot_reenc.c

Concrete handler and helper layer for `reencrypt` keyslots, which store online reencryption resilience metadata rather than passphrase-unlocked volume keys. It allocates and validates reencryption keyslot JSON, writes reencryption metadata to the binary area, dumps resilience settings, loads protection descriptors, and supports controlled resilience-mode updates.

Key responsibilities:
- Provides a handler whose `open` always returns `-ENOENT`, because reencryption keyslots are not passphrase unlock slots.
- Builds the keyslot `area` JSON for resilience modes: `checksum`, `journal`, `none`, `datashift`, `datashift-checksum`, and `datashift-journal`.
- Allocates a reencryption keyslot with type, dummy `key_size = 1`, reencrypt mode, direction, and area metadata.
- Chooses storage area by finding a maximum gap for most resilience modes and only a minimal area for plain datashift, which does not require extra stored protection data.
- Stores reencryption data into the keyslot area using locked raw block writes.
- Wipes reencryption verification references from digests.
- Dumps mode, direction, resilience type, hash/sector size or shift size where applicable, and area offset/length.
- Validates reencryption keyslot JSON: legal mode, legal direction, key size exactly 1, checksum fields and power-of-two sector size, datashift shift-size presence and 512-byte alignment.
- Detects whether an existing reencryption keyslot needs update based on requested resilience, hash, checksum block size, and data-shift size.
- Loads primary and secondary resilience descriptors into `struct reenc_protection`, including checksum hash context initialization.
- Restricts updates so callers cannot switch to or away from datashift categories or change datashift size.
- Updates area JSON transactionally: keeps a reference to the old area, installs the new one, validates, and restores the old area if validation fails.
- Public helpers allocate, test update need, perform updates, refresh reencryption verification digest, validate hotzone capacity for secondary protection, write the header, and load resilience data.

Important behavior:
- Reencryption keyslots must have priority set to `CRYPT_SLOT_PRIORITY_IGNORE` after allocation so normal unlock attempts skip them.
- Allocation checks JSON size after inserting the keyslot and removes it if the metadata area cannot hold the new object.
- Checksum resilience records both `hash` and `sector_size`; datashift variants additionally record `shift_size` in bytes.
- Updating checksum block size without changing resilience uses a copy of the existing area with only `sector_size` changed.
- Before updating resilience metadata, the code verifies the existing reencryption digest against supplied volume keys.
- If the new secondary protection type needs storage, it computes the maximum hotzone size and refuses updates when the moved segment requires more protection space than the new type provides.
- The handler table exposes `store`, `wipe`, `dump`, and `validate`, but public allocation/update/load helpers are separate from the generic keyslot store path.

Dependencies:
- Depends on `luks2_internal.h` for header access, JSON helpers, area finding, metadata locks/writes, digest assignment, reencryption digest verification/creation, hotzone sizing, and protection cleanup.
- Uses cryptsetup block I/O helpers (`device_open_locked`, `write_lseek_blockwise`, block size/alignment helpers) for raw metadata writes.
- Uses crypt hash APIs to initialize checksum resilience state.
- Uses `crypt_params_reencrypt`, `crypt_reencrypt_mode_to_str()`, and reencryption direction/mode constants.

Notable risks:
- The validation branch for datashift-related types is structured so `datashift-checksum` is consumed by the checksum branch first; the separate datashift branch handles plain datashift and datashift-journal. This matches stored fields created by allocation but is easy to misread when extending validation.
- Reencryption resilience updates are intentionally constrained; loosening datashift category or shift-size immutability could break crash-recovery assumptions.
- Raw writes to the reencryption area depend on buffer length fitting inside the configured area and on external device locking.
- The `open` method is a sentinel; callers must not expect reencryption keyslots to produce volume keys through the normal keyslot unlock path.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_keyslot_reenc.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_luks1_convert.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_luks1_convert.c

Bidirectional LUKS1/LUKS2 conversion implementation. It constructs LUKS2 JSON metadata from a LUKS1 header, moves binary keyslot material between LUKS1 and LUKS2 area layouts, checks compatibility constraints for down-conversion, creates placeholder keyslots for inactive LUKS1 slots, and writes the target header format.

Key responsibilities:
- Converts active LUKS1 keyblocks into LUKS2 `luks2` keyslot JSON with PBKDF2 KDF, base64 salt, LUKS1 AF settings, raw encrypted area, area offset, and area size.
- Builds LUKS2 keyslots, one dynamic crypt segment, one PBKDF2 digest, empty tokens, and config objects from a LUKS1 header.
- Encodes the LUKS1 master-key digest, digest salt, keyslot salts, and iteration counts into LUKS2 JSON.
- Moves keyslot area offsets in JSON when converting LUKS1 to LUKS2, because LUKS2 stores two metadata areas before binary keyslot areas.
- Moves binary keyslot material on disk between LUKS1 offset 4 KiB and LUKS2 offset 32 KiB layouts with page-aligned buffers and blockwise I/O.
- Checks whether the mapped LUKS device is active before destructive conversion.
- Detects LUKSMETA foreign metadata after the LUKS1 area and refuses conversion when present.
- Converts LUKS1 to LUKS2 by checking keyslot offset, cipher compatibility, keyslot cipher compatibility, available space, JSON validity, active-device state, binary keyslot move, and LUKS2 header write.
- Checks whether each LUKS2 keyslot can be represented as LUKS1: type `luks2`, PBKDF2, digest hash match, AF stripes/hash match, matching data/keyslot cipher and key size, and compatible binary area length.
- Converts LUKS2 to LUKS1 only for single-segment, no-token, single-PBKDF2-digest, 512-byte-sector, LUKS1-compatible metadata.
- Rejects down-conversion when keyslots are invalid, unbound, above the LUKS1 slot limit, or not LUKS1 compatible.
- Allocates placeholder LUKS2 keyslots for inactive LUKS1 slots so each LUKS1 keyblock gets a distinct key material offset.
- Reconstructs the LUKS1 binary header fields: keyblock active state, stripes, key material offsets, PBKDF iteration counts/salts, cipher name/mode, hash, key size, digest fields, payload offset, UUID, magic, and version.
- Wipes the old LUKS2 binary header area before writing the new LUKS1 header.

Important behavior:
- LUKS1 to LUKS2 assumes the LUKS1 keyslot material starts at `LUKS_ALIGN_KEYSLOTS / SECTOR_SIZE`; other layouts are refused.
- LUKS1 to LUKS2 requires enough space for the shifted keyslot area. It attempts fallocate when the current max size is too small.
- The generated LUKS2 header is fixed to 16 KiB metadata area, seqid 1, version 2, sha256 header checksum, fresh salts, and the existing LUKS UUID.
- Conversion validates the future LUKS2 metadata before moving binary keyslot material to avoid destructive changes when JSON would later fail.
- LUKS2 to LUKS1 refuses wrapped-key ciphers, multiple segments, tokens, non-512-byte default segment sector size, and non-PBKDF2 digest layouts.
- Inactive LUKS2 slots are temporarily represented by invalid placeholder keyslots only to reserve unique binary areas for the LUKS1 header calculation.
- Down-conversion subtracts the LUKS2 keyslot shift from stored keyslot material offsets to recover LUKS1-relative offsets.
- LUKS2 to LUKS1 moves binary keyslots from 32 KiB back to 4 KiB, zeros the old LUKS2 header prefix, then calls `LUKS_write_phdr()`.

Dependencies:
- Depends on `luks2_internal.h` for LUKS2 JSON/header helpers, validation, size calculations, keyslot area lookup, keyslot placeholder allocation, token count, volume-key size, cipher lookup, and header write/free.
- Depends on LUKS1 structures and helpers from `../luks1/luks.h` and AF sizing from `../luks1/af.h`.
- Uses cryptsetup device size, data offset, cipher checking, hash checking, dm active lookup, metadata-device I/O, wipe, sync, and allocation helpers.
- Uses base64 encoding/decoding for LUKS1 salts and digests stored in LUKS2 JSON.

Notable risks:
- Both conversion directions move live keyslot material on disk; failures during movement or after partial writes can leave the device requiring recovery from backup.
- The code intentionally refuses many valid LUKS2 features because LUKS1 cannot represent them; callers must surface those compatibility failures clearly.
- Placeholder keyslots are deliberately invalid and must not be written as a final LUKS2 header.
- LUKSMETA detection treats a matching magic after the LUKS1 area as a hard blocker because the conversion shift would overwrite or invalidate foreign metadata.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_luks1_convert.c -->