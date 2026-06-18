# Group Research: group_273_cryptsetup_sources_block_storage_cryptsetup_lib_luks1_keymanage_c_so_77d526d7e627

Scope checked against `Docs/research_subset_a.md`; all listed files are under `sources/block-storage/cryptsetup`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks1/keymanage.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks1/keymanage.c

Implements LUKS1 header/keyslot lifecycle: header generation, read/write, backup/restore, repair, keyslot creation/open/delete, activation, wiping, and PBKDF reporting.

Core behavior:
- Calculates keyslot offsets and lengths from `luks_phdr.keyblock[]`, `AF_split_sectors()`, `SECTOR_SIZE`, and fixed `LUKS_STRIPES`.
- Validates device/header geometry: key material must fit after the binary header, before payload for attached headers, without overlapping other keyslots.
- Reads on-disk big-endian LUKS1 headers and converts integer fields to CPU endian; writes by converting back to network byte order.
- Generates new headers with magic/version/cipher/hash/UUID, keyslot layout, random master-key digest salt, and PBKDF2 digest over the volume key.
- Backs up/restores the header plus keyslot area, with restore checks for payload offset/key size compatibility and user confirmation.
- Repairs known legacy/broken header cases: uppercase hash names, `ecb-*` mode strings, damaged inactive keyslot offsets/stripes/salts, and partition-signature damage in keyslot metadata.

Keyslot operations:
- `LUKS_set_key()` derives a wrapping key from passphrase via PBKDF2, AF-splits the volume key, encrypts AF material to the keyslot area, marks the slot enabled, and writes the header.
- `LUKS_open_key_with_hdr()` tries a requested slot or all slots, decrypts AF material, merges it back to a volume key, verifies the master-key digest, and returns the opened slot index.
- `LUKS_del_key()` disables a slot, wipes key material with `CRYPT_WIPE_SPECIAL`, clears salt/iterations, and writes the updated header.
- Slot state is reported as inactive, active, active-last, or invalid from `active` magic values.

Important invariants:
- LUKS1 supports exactly 8 keyslots and assumes `LUKS_STRIPES == 4000`.
- Digest and keyslot PBKDF are PBKDF2-based.
- On-disk integer fields are big-endian.
- Keyslot area starts at or after `LUKS_ALIGN_KEYSLOTS` except legacy unaligned headers, where direct I/O is disabled.
- Null cipher activation only accepts an empty passphrase.

External dependencies:
- Uses cryptsetup internals for device I/O, locking-adjacent device helpers, PBKDF, random, AF split/merge, dm-crypt target assembly, secure allocation/free, wiping, logging, and confirmation prompts.
- Uses `uuid_parse`, `uuid_generate`, `uuid_unparse`.

Failure/security notes:
- Many validation failures map to `-EINVAL`; wrong passphrases map to `-EPERM`; inactive slots to `-ENOENT`.
- Header restore and wipe paths can destroy access to data, so restore requires confirmation and wipe carefully bounds header/keyslot areas.
- Sensitive buffers are allocated with safe allocators and zeroed/freed on exit paths.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks1/keymanage.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks1/luks.h -->
# File Research: sources/block-storage/cryptsetup/lib/luks1/luks.h

Defines the LUKS1 on-disk header ABI and declares the LUKS1 management API implemented primarily by `keymanage.c`.

Key definitions:
- Fixed string sizes for cipher name, cipher mode, hash spec, UUID, salts, and digest.
- `LUKS_NUMKEYS` is 8; `LUKS_STRIPES` is 4000.
- Keyslot active markers include old and current constants; current enabled marker is `0x00AC71F3`, disabled marker is `0x0000DEAD`.
- Header magic is `{'L','U','K','S',0xba,0xbe}` and version is handled by code as version 1.
- `LUKS_ALIGN_KEYSLOTS` is 4096 bytes; `LUKS_MAX_KEYSLOT_SIZE` is 16 MiB for wipe safety.

Main structure:
- `struct luks_phdr` is the packed conceptual LUKS1 metadata layout: magic/version, cipher/hash fields, payload offset, master key size, master-key digest/salt/iterations, UUID, 8 keyblock entries, and padding to sector alignment.
- Each keyblock stores active state, PBKDF iteration count, salt, key material offset, and AF stripe count.
- Comment states integer values are stored in network byte order on disk.

Declared API:
- Header generation/read/write/backup/restore/UUID update.
- Keyslot set/open/delete/wipe/info/count/area/PBKDF helpers.
- Volume-key verification and LUKS1 activation.

Role in the subsystem:
- This header is the compatibility boundary for LUKS1 code and for conversion paths referenced by LUKS2 headers.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks1/luks.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/hw_opal/hw_opal.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/hw_opal/hw_opal.c

Implements cryptsetup’s Linux OPAL self-encrypting drive support behind `HAVE_HW_OPAL`, with `-ENOTSUP` stubs when OPAL support is unavailable at build time.

Core behavior:
- Wraps Linux `sed-opal` ioctls with debug logging, OPAL method-status translation, and compatibility definitions for newer Single User Mode ioctl structures if kernel headers lack them.
- Supports OPAL discovery, status, geometry, ownership, locking SP activation, user activation, password setup, locking range setup, lock/unlock, save-for-resume behavior, PSID factory reset, and locking-range reset.
- Detects and configures Single User Mode (SUM), including runtime kernel ioctl support probing and fallback behavior for non-conforming drives.
- Maintains OPAL-specific exclusive locks using cryptsetup write locks keyed by block device major/minor.

Setup flow:
- `opal_setup_ranges()` opens the device, checks SUM and existing OPAL state, activates the locking SP or reuses an active one, creates/enables the range user, sets the user password from a `volume_key`, configures range start/length, locks the range, verifies attributes and lock state, and returns the LUKS2 OPAL requirement version.
- SUM setup attempts preferred RangeStartLengthPolicy behavior, then retries without range policy, then disables SUM if the device behaves incorrectly.
- Reusing an active locking SP wipes the existing target range first via SUM erase or secure erase.

Lock/unlock flow:
- `opal_lock()` and `opal_unlock()` call a shared helper using `IOC_OPAL_LOCK_UNLOCK`.
- Unlock requires a volume key; lock does not.
- Unlock attempts `IOC_OPAL_SAVE` with `OPAL_SAVE_FOR_LOCK` for suspend/resume support. Lock attempts `IOC_OPAL_SAVE` without the flag to clear cached kernel credentials.

Validation and discovery:
- `opal_range_check_attributes_and_get_lock_state()` verifies OPAL range offset/length, RLE/WLE, and optional expected lock state, returning current read/write lock state.
- `opal_geometry()` returns OPAL logical block size, alignment granularity, and lowest aligned LBA.
- `crypt_status_hw_encryption()` uses OPAL level-0 discovery when possible, otherwise falls back to supported/SUM status probes.

Failure/security notes:
- OPAL method status is distinguished from negative errno-style ioctl failures.
- Sensitive OPAL keys are stored in `crypt_safe_alloc` buffers where practical and zeroed before return in direct stack cases.
- Factory reset intentionally does not take the OPAL serialization lock because it destroys the whole OPAL block device.
- Non-SUM and SUM paths differ in authority rules: in SUM, user credentials control RLE/WLE and lock/unlock for the range.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/hw_opal/hw_opal.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/hw_opal/hw_opal.h -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/hw_opal/hw_opal.h

Declares the OPAL utility API used by LUKS2 hardware encryption paths.

Exported operations:
- `opal_setup_ranges()` configures an OPAL locking range and reports the required LUKS2 OPAL requirement version.
- `opal_lock()` and `opal_unlock()` lock/unlock a segment.
- `opal_supported()` and `opal_geometry()` query device capability and geometry.
- `opal_factory_reset()` performs PSID revert of the full OPAL device.
- `opal_reset_segment()` erases/resets a specific locking range.
- `opal_range_check_attributes_and_get_lock_state()` validates range geometry and returns lock state.
- `opal_exclusive_lock()` / `opal_exclusive_unlock()` serialize OPAL operations with cryptsetup locking.

Role:
- Keeps OPAL support isolated behind a small interface so LUKS2 segment/key management can call hardware encryption functions without depending directly on Linux ioctl details.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/hw_opal/hw_opal.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2.h -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2.h

Defines the LUKS2 on-disk binary header, in-memory header, sizing limits, object limits, and public internal API surface for LUKS2 metadata operations.

Key constants:
- Primary magic is `LUKS\xba\xbe`; secondary magic is `SKUL\xba\xbe`.
- Max object counts are 32 for keyslots, tokens, and segments; digest max is 8.
- Default metadata/header sizing: 16 KiB minimum header, 16 MiB default header area, 128 MiB max keyslots area, 4 MiB max metadata offset.
- Secondary header scan offsets are enumerated up to `LUKS2_HDR_OFFSET_MAX`.
- Defines special segment/digest IDs such as `CRYPT_ANY_SEGMENT`, `CRYPT_DEFAULT_SEGMENT`, and `CRYPT_ANY_DIGEST`.

On-disk structures:
- `struct luks2_hdr_disk` is packed and contains magic, version, header size, sequence ID, label, checksum algorithm, per-header salt, UUID, subsystem, header offset, checksum, padding to 4096 bytes, then JSON area.
- Checksum is calculated with the checksum field zeroed over the binary header plus the full JSON area.
- `struct luks2_hdr` stores in-memory metadata, salts for both copies, JSON object pointers, rollback object, and tracked on-disk JSON end offset.

API coverage:
- Header read/write/rollback/dump/backup/restore/labels/UUID/free and size helpers.
- Keyslot open/store/wipe/priority/swap/area/PBKDF helpers.
- Segment creation/query helpers, including OPAL and OPAL+dm-crypt segments.
- Token assignment, creation, status, keyring helpers, and passphrase/key unlock.
- Digest creation, assignment, lookup, and verification.
- Activation/deactivation, header generation, storage parameter calculation, wipe, conversion between LUKS1/LUKS2, OPAL key splitting, requirements, and reencryption support.

Role:
- Central declaration point for LUKS2 metadata layout and operations shared by JSON formatting, disk metadata I/O, digest/keyslot/token handling, reencryption, activation, and OPAL support.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_digest.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_digest.c

Implements generic LUKS2 digest management over JSON metadata. Digest-specific algorithms are dispatched through `digest_handler`; currently the handler table contains PBKDF2.

Core behavior:
- Locates digest handlers by JSON `"type"`.
- Finds free digest IDs under `LUKS2_DIGEST_MAX`.
- Creates digest JSON entries through handler `store()`.
- Finds digest IDs associated with keyslots or segments by scanning digest `"keyslots"` and `"segments"` arrays.
- Verifies a volume key by digest, keyslot, segment, or any matching digest.
- Optionally checks expected key size from digest/segment/keyslot metadata after cryptographic verification.

Assignment behavior:
- `LUKS2_digest_assign()` adds/removes keyslot IDs from one digest or all digests.
- `LUKS2_digest_segment_assign()` adds/removes segment IDs from one digest or all digests, with support for default segment and all segments.
- Empty digests with no segments and no keyslots can be erased by `LUKS2_digests_erase_unused()`.

Keyring helpers:
- Builds key descriptions in the form `cryptsetup:<uuid>-d<digest>`.
- Can attach segment-derived descriptions to volume keys and load digest-described keys into the kernel keyring.

Important invariants:
- Digest JSON objects must expose `"type"`, `"keyslots"`, and `"segments"` fields for generic assignment/removal.
- Segment and keyslot IDs are stored as decimal strings in arrays.
- Verification returns the digest ID on success or negative errno-style values on failure.

Role:
- Connects LUKS2 JSON references between volume-key digests, keyslots, and segments, while leaving algorithm-specific digest storage/verification to handlers.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_digest.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_digest_pbkdf2.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_digest_pbkdf2.c

Implements the PBKDF2 digest handler used by LUKS2 and compatible with LUKS1-style master-key digest concepts.

Stored JSON fields:
- `"type": "pbkdf2"`
- `"keyslots"` and `"segments"` arrays
- `"hash"`
- `"iterations"`
- Base64 `"salt"`
- Base64 `"digest"`

Verification:
- Reads hash, iterations, salt, and digest from digest JSON.
- Base64-decodes salt and digest.
- Validates salt length is 32 bytes.
- Accepts digest length of legacy 20 bytes or the hash output size, bounded by a local 64-byte check buffer.
- Runs PBKDF2 over the supplied volume key and compares with constant-time backend comparison.
- Returns `0` for match, `-EPERM` for mismatch, and `-EINVAL` for malformed metadata or PBKDF failure.

Storage:
- Inherits PBKDF hash from the crypt device PBKDF settings, defaulting to `DEFAULT_LUKS1_HASH`.
- Uses 125 ms target PBKDF2 benchmark unless benchmarking is disabled, in which case it uses the backend minimum iteration count.
- Generates random digest salt, computes PBKDF2 digest using the HMAC size for the selected hash, base64-encodes salt/digest, and inserts or updates the digest JSON object.

Dump:
- Prints hash, iterations, salt, and digest in decoded hex form through `hexprint_base64()`.

Role:
- Supplies the concrete digest algorithm implementation consumed by `luks2_digest.c`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_digest_pbkdf2.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_disk_metadata.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_disk_metadata.c

Implements low-level LUKS2 binary header and JSON metadata read/write, checksum calculation, sequence handling, validation, and recovery between primary and secondary headers.

Read path:
- Reads the 4096-byte binary header at a given offset, validates magic/version/header size/header offset before reading JSON.
- Reads the full JSON area, checks checksum over binary header with zeroed checksum plus full JSON area, then clears the in-memory checksum field.
- Parses JSON with json-c while tracking the parsed byte offset.
- Validates JSON area starts with `{`, has a trailing NUL after parsed data, and contains only zero bytes in unused space.
- Validates the resulting LUKS2 JSON object and attempts known metadata repair before failing.

Write path:
- Serializes JSON in compact on-disk form.
- Ensures JSON fits inside the configured JSON area with room for trailing NUL.
- Writes binary header without checksum, writes JSON area, calculates checksum, then rewrites binary header with checksum.
- `LUKS2_disk_hdr_write()` checks device size, takes a write lock, increments sequence ID, writes primary then secondary copies, tracks JSON end offset, and unlocks.

Recovery/selection:
- Reads primary at offset 0.
- Reads secondary at `hdr_size` from primary when possible, otherwise scans known secondary offsets.
- If both headers are valid, the lower sequence ID copy is considered obsolete.
- If one copy is valid and the other invalid, optional recovery rewrites the bad copy with regenerated salt after optional blkid signature safety checks.
- Refuses auto-recovery when metadata locking is disabled in normal probe mode.

Concurrency:
- `LUKS2_device_write_lock()` acquires device write lock and checks the on-disk sequence ID matches the in-memory header on the first lock, unless reencryption is in progress.
- Detects concurrent metadata update attempts and aborts.

Other helpers:
- `LUKS2_hdr_version_unlocked()` reads only magic/version from a device or backup file without full metadata locking.
- Foreign-signature detection uses blkid and filters out crypto_LUKS signatures before allowing auto-recovery.

Important invariants:
- LUKS2 has two metadata copies with separate salts and shared sequence semantics.
- Header checksum algorithm comes from the header field and is used over the full JSON area, not just live JSON bytes.
- The secondary header offset must match the header size.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_disk_metadata.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_internal.h -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_internal.h

Declares private LUKS2 internals shared across implementation files.

Main areas:
- Disk metadata read/write and write-lock helpers.
- JSON object accessors for keyslots, tokens, digests, segments, and top-level segment collections.
- JSON scalar helpers, object-copy/add/delete helpers, compact on-disk JSON serialization, and debug dumping.
- JSON validation/repair entry points for headers, tokens, and keyslots.
- JSON array lookup/removal helpers.

Plugin-style handler interfaces:
- `keyslot_handler` declares alloc/update/open/store/wipe/dump/validate/repair operations for keyslot implementations.
- `digest_handler` declares verify/store/dump operations for digest implementations.
- Token handler internals wrap public/deprecated token handler versions while preserving prefix layout compatibility.

Reencryption support:
- Defines `struct reenc_protection`, supporting checksum, journal, and datashift protection variants.
- Declares reencryption keyslot allocate/update/load/store/digest helpers and reencryption segment/digest lookup functions.

Segment/keyslot/digest internals:
- Declares JSON segment getters for offsets, sizes, ciphers, sector sizes, OPAL IDs/key sizes, backup flags, and reencryption flags.
- Declares JSON segment creation for linear, crypt, OPAL, and OPAL+crypt segments.
- Declares area gap search, keyslot dump, segment assembly into dm targets, segment flags, default segment lookup, volume-key size lookup, and digest verification helpers.

Role:
- This is the private coordination header for LUKS2 modular implementation files; it exposes internal contracts but not the on-disk ABI itself, which lives in `luks2.h`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_json_format.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_json_format.c

Implements LUKS2 JSON metadata formatting, keyslot-area allocation helpers, header generation, wipe behavior, and storage-size parameter calculation.

Area allocation:
- Keyslot material size is currently `keylength * 4000` rounded to 4096, mirroring AF split sizing.
- Keyslot areas live after both metadata copies: minimum offset is `2 * hdr->hdr_size`.
- Maximum usable metadata/keyslot area is `LUKS2_hdr_and_areas_size(hdr)`.
- `LUKS2_find_area_gap()` finds the first aligned gap large enough for a keyslot.
- `LUKS2_find_area_max_gap()` finds the largest free gap, adding a sentinel at the current max offset.
- Both functions scan all possible LUKS2 keyslots, sort existing allocated areas by offset, and avoid overlap.

Sizing validation:
- `LUKS2_check_metadata_area_size()` accepts only supported metadata sizes matching known secondary-header offsets.
- `LUKS2_check_keyslots_area_size()` rejects misaligned or too-large keyslot areas.

Header generation:
- `LUKS2_generate_hdr()` initializes header version, sequence ID, checksum algorithm, salts, UUID, top-level JSON objects (`keyslots`, `tokens`, `segments`, `digests`, `config`), creates a PBKDF2 digest, assigns it to segment 0, and creates the initial segment.
- Supports three segment modes: normal dm-crypt, OPAL-only, and OPAL+dm-crypt.
- Stores `json_size` and `keyslots_size` in config.
- Warns when the keyslot area is so small that available keyslot count is limited.

Wipe behavior:
- `LUKS2_wipe_header_areas()` validates metadata, bounds the zero wipe to metadata/keyslot maxima and device size, wipes metadata area with zeroes, ensures actual header/keyslot area exists, then wipes keyslot area with random data if configured.

Storage parameter calculation:
- `LUKS2_hdr_get_storage_params()` derives metadata size, keyslots size, and data offset from crypt device settings and alignment constraints.
- Metadata defaults to 16 KiB when unspecified.
- Keyslots size is inferred from explicit data offset when possible, capped at 128 MiB, 4 KiB aligned, and reduced if the metadata device is too small.
- Data offset has priority; otherwise it is aligned after two metadata areas plus keyslots area.

Role:
- This file builds the initial logical LUKS2 JSON layout and decides where variable-sized keyslot areas fit inside the metadata/keyslots region.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_json_format.c -->