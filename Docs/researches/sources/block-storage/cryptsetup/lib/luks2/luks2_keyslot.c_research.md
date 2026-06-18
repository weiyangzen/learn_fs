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
