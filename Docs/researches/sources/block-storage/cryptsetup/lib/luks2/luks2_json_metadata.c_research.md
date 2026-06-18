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
