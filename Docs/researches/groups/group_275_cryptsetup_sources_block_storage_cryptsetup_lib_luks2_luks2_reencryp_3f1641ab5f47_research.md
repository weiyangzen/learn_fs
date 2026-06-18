# Group Research: group_275_cryptsetup_sources_block_storage_cryptsetup_lib_luks2_luks2_reencryp_3f1641ab5f47

Scope confirmed against `Docs/research_subset_a.md`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_reencrypt.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_reencrypt.c

This is the main LUKS2 reencryption implementation. It owns initialization, resume, crash recovery, online device-mapper stack management, hotzone processing, metadata transitions, and public API entry points for `crypt_reencrypt_*`.

Core state is kept in `struct luks2_reencrypt`: current window `offset/progress/length`, total `device_size`, online/fixed-length mode, reencryption direction/mode, dm device names, protection metadata, reencryption keyslot, backup/hot/post JSON segment objects, old/new digests, volume keys, aligned reencryption buffer, old/new `crypt_storage_wrapper`s, hotzone device, and the reencryption metadata lock.

Important metadata model:
- Reencryption uses special segment flags: `backup-previous`, `backup-final`, `backup-moved-segment`, and `in-reencryption`.
- Old/new backup segments provide the before/after crypt or linear segment definitions.
- The reencryption keyslot stores resilience data and mode/direction/protection parameters.
- `LUKS2_keyslot_reencrypt_digest_create()` binds a digest over keys plus serialized metadata so reencryption metadata tampering can be detected.

Major flows:
- Initialization validates mode, direction, sector sizes, data size, cipher, keyslots, resilience parameters, DAX exclusion, and data-shift constraints.
- It creates backup segments, allocates the reencryption keyslot, unlocks required old/new volume keys, creates/verifies the reencryption digest, optionally moves the first segment for data-shift modes, then commits the online reencryption requirement flag.
- Resume/load verifies the reencryption digest, obtains the reencryption lock, reloads metadata under lock, opens keys if needed, checks active dm mapping compatibility, computes offsets/hotzone size, initializes storage wrappers, and stores the context on the crypt device.
- `crypt_reencrypt_run()` creates the online helper stack if needed, then loops over hotzones until `progress >= device_size` or the progress callback requests stop.
- Each hotzone computes temporary “hot” and “post” segments, commits hot metadata/protection data, reads old data, decrypts, encrypts/writes with the new layout, syncs when required, then commits post metadata.
- Crash recovery reloads the crashed context, reconstructs the current hotzone, restores data using checksum/journal/datashift resilience, assigns post segments, advances context, and commits metadata.

Resilience handling:
- `none`: no per-hotzone rollback metadata, limited rollback ability.
- `checksum`: stores hashes for blocks in the reencryption keyslot; recovery compares new hotzone data against saved hashes to identify sectors needing old-data recovery.
- `journal`: stores old plaintext-equivalent hotzone payload encrypted in the reencryption keyslot area.
- `datashift`: reserves/moves data so old data can be reread from shifted locations.
- `datashift-checksum` and `datashift-journal` support moved-first-segment cases, especially decrypt-with-datashift.

Online reencryption device stack:
- Creates a private hotzone dm-linear device over the data device.
- Creates an overlay device from the original mapping.
- Redirects the public mapping through the overlay.
- Reloads overlay tables to expose hotzone segments during a chunk.
- Uses careful suspend/resume ordering: overlay before hotzone, then resume overlay.
- On fatal suspended-hotzone errors, replaces hotzone with `dm-error` to prevent queued I/O from corrupting data.

Key dependencies:
- LUKS2 JSON helpers, digest/keyslot APIs, segment APIs, storage wrappers, device locking, dm helpers, keyring upload/drop, device size/access helpers, wipe helpers, and translation macro `_()`.
- The file has compile-time fallback stubs when `USE_LUKS2_REENCRYPTION` is disabled.

Public/internal API surface in this file includes:
- `crypt_reencrypt_init_by_passphrase`, `crypt_reencrypt_init_by_keyring`, `crypt_reencrypt_init_by_keyslot_context`
- `crypt_reencrypt_run`, `crypt_reencrypt`
- `LUKS2_reencrypt_digest_new/old`, `LUKS2_reencrypt_segment_new/old`, `LUKS2_reencrypt_vks_count`
- `LUKS2_reencrypt_lock`, `LUKS2_reencrypt_unlock`, `LUKS2_reencrypt_lock_by_dm_uuid`
- `LUKS2_reencrypt_check_device_size`, `LUKS2_reencrypt_data_offset`
- `LUKS2_reencrypt_locked_recovery_by_vks`, `LUKS2_reencrypt_get_params`

Notable correctness constraints:
- Hotzone size and fixed device size must align to the computed alignment.
- Reencryption length is capped by protection area, hard max, memory soft limit, requested max, and topology alignment.
- Digest verification must pass before reencryption context load.
- The first metadata write during init is intentionally the online-reencryption requirement flag.
- Recovery refuses invalid segment layouts and missing required old/new keys.
- DAX devices are explicitly unsupported.
- Direct I/O is required for online reencryption.

Risk areas:
- The file contains several `FIXME`/`TODO` comments around segment modeling, locking, function naming, old/new segment equivalence detection, and more specific errors.
- Device-mapper transitions are complex and rely on exact suspend/resume ordering.
- `REENC_PROTECTION_NONE` intentionally cannot roll back metadata progress in the same way as protected modes.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_reencrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_reencrypt_digest.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_reencrypt_digest.c

This file builds and verifies the reencryption metadata digest. Its purpose is to authenticate the reencryption keyslot parameters plus backup segment definitions plus relevant volume keys.

Serialization model:
- Small typed serializer `struct jtype` supports strings, 64-bit numeric strings, 64-bit segment sizes including `"dynamic"`, and JSON ints stored as big-endian 32-bit.
- Segment serialization covers `linear` fields `type/offset/size`.
- Crypt segment serialization covers `type/offset/size/iv_tweak/encryption/sector_size`.
- Backup segment serialization requires `backup-previous` and `backup-final`; `backup-moved-segment` is optional.
- Reencrypt keyslot serialization includes `mode`, `direction`, area `type`, `offset`, `size`, plus resilience-specific fields such as `hash`, `sector_size`, and `shift_size`.

Digest data assembly:
- Starts with a version marker: bytes `0x76` and `0x30 + version`.
- Appends old volume key bytes when an old digest exists.
- Appends new volume key bytes when the new digest exists and differs from old.
- Appends serialized reencryption keyslot metadata.
- Appends serialized backup segments.

Main functions:
- `LUKS2_keyslot_reencrypt_digest_create()` assembles verification data, creates a PBKDF2 digest, clears any old assignment from the reencryption keyslot, and assigns the new digest to that keyslot.
- `LUKS2_reencrypt_digest_verify()` rebuilds the same verification data and verifies it against the reencryption keyslot digest. It logs missing digest and invalid metadata cases.

Important constraints:
- Required volume keys must already be unlocked and accessible by digest id.
- Serialization fails closed on missing fields, wrong JSON types, unknown segment types, overlong strings, or missing backup segments.
- The digest check deliberately does not check key size because the reencryption keyslot stores a bogus `key_size=1`.

Dependencies:
- LUKS2 segment/digest/keyslot helpers from `luks2_internal.h`
- volume key helpers
- JSON-C
- endian conversion helpers
- safe allocation/free helpers

This file is tightly coupled to the metadata schema in `luks2_reencrypt.c`; changes to reencryption segment or keyslot JSON fields must preserve this serialization contract or update digest versioning.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_reencrypt_digest.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_segment.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_segment.c

This file implements internal LUKS2 JSON segment access, creation, flag handling, lookup, and comparison helpers.

Main responsibilities:
- Read segment fields: `offset`, `type`, `iv_tweak`, `size`, cipher `encryption`, `sector_size`, OPAL segment id/key size/size.
- Handle flags arrays, including backup detection via flags prefixed by `backup-`.
- Create `linear`, `crypt`, `hw-opal`, and `hw-opal-crypt` segment JSON objects.
- Add crypt fields: `iv_tweak`, `encryption`, `sector_size`, optional integrity object, optional `in-reencryption` flag.
- Find first/last segment by type, first unused id, segment by flag, and segment currently flagged `in-reencryption`.
- Set the whole `segments` object on a header, optionally committing it.
- Assign/remove segment flags and remove empty flag arrays.
- Compare key segment characteristics for compatibility.

Important functions:
- `json_segments_get_minimal_offset()` returns the smallest non-backup segment offset.
- `json_segment_is_backup()` treats any flag with prefix `backup-` as a backup segment.
- `json_segments_count()` counts only non-backup segments.
- `json_segment_create_crypt()` and `json_segment_create_linear()` are used heavily by reencryption.
- `LUKS2_get_segment_id_by_flag()` and `LUKS2_get_segment_by_flag()` are central to finding reencryption backup segments.
- `LUKS2_segments_dynamic_size()` detects non-backup segments with `"size": "dynamic"`.

OPAL support:
- `hw-opal` and `hw-opal-crypt` segment types carry `opal_segment_number`, `opal_key_size`, and `opal_segment_size`.
- Helper predicates distinguish OPAL-only, OPAL-crypt, and any OPAL segment.

Notable behavior:
- Missing cipher field defaults to `"null"` with a FIXME noting pseudo-null cipher handling should happen elsewhere.
- Invalid or missing sector size defaults to 512-byte sector size.
- Segment ids are string keys in JSON and are converted with `atoi()`.
- `LUKS2_segment_first_unused_id()` returns the current object length, so it assumes dense/append-style segment ids.

Dependencies:
- `luks2_internal.h`
- JSON-C
- LUKS2 array helpers
- crypt JSON uint helpers

This file is a foundational utility for LUKS2 metadata manipulation and is especially important for reencryption because backup segments are intentionally present in metadata but excluded from normal active segment counting.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_segment.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_token.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_token.c

This file implements LUKS2 token handler registration, built-in/external token loading, token JSON creation/removal, token status, assignment to keyslots, and unlock flows.

Token handler model:
- `token_handlers` is a fixed-size array of internal handler slots.
- The built-in keyring token is registered by default with open/free/validate/dump callbacks.
- Additional built-in-like names are blocked by the reserved `LUKS2_BUILTIN_TOKEN_PREFIX`.
- External token support is conditional on `USE_EXTERNAL_TOKENS`.

External token loading:
- External token path defaults to `EXTERNAL_LUKS2_TOKENS_PATH` and can be changed to an absolute path.
- Names must be non-empty, max `LUKS2_TOKEN_NAME_MAX`, and only alnum, `-`, or `_`.
- Loader builds `libcryptsetup-token-<name>.so`, uses `dlopen`, resolves ABI symbols, validates required callbacks, records ABI version, and stores the dlhandle.
- `crypt_token_unload_external_all()` unloads v2 external handlers and frees copied names.

Token metadata operations:
- `LUKS2_token_create()` creates, replaces, or removes a token JSON object at a given token id or first free slot.
- It parses JSON, validates against LUKS2 schema, validates handler-specific constraints when a handler exists, rejects missing built-in handlers, checks header JSON size, and optionally commits.
- `LUKS2_token_status()` reports inactive, internal/external known, or internal/external unknown.
- `LUKS2_token_json_get()` returns serialized token JSON.
- `LUKS2_token_dump()` delegates pretty-printing to the token handler.

Unlock flow:
- `LUKS2_token_unlock_key()` unlocks a volume key using a specific token or any usable token.
- Token usability checks assigned keyslots, requested segment, minimum keyslot priority, and whether a keyslot assignment is required.
- A token handler returns a passphrase/key buffer, then `LUKS2_keyslot_open_by_token()` attempts assigned keyslots in priority order.
- For `CRYPT_ANY_TOKEN`, token attempts are ordered by priority: prefer first, then normal.
- Return priority is carefully preserved: `-ENOENT` unusable, `-EPERM` provided material did not unlock, `-EAGAIN` hardware unavailable/not ready, `-ENOANO` wrong/missing PIN. Other errors short-circuit.
- Tokens returning `-ENOANO` are blocked from later priority loops.

Passphrase extraction:
- `LUKS2_token_unlock_passphrase()` opens a token without requiring assigned keyslots and copies the returned buffer into a crypt safe allocation for caller use.

Assignment operations:
- `LUKS2_token_assign()` assigns/unassigns one keyslot, all keyslots, one token, or all tokens.
- `LUKS2_token_is_assigned()` checks a token’s `keyslots` array.
- `LUKS2_token_assignment_copy()` copies token assignments from one keyslot to another.

Safety behavior:
- Token buffers are freed through handler `buffer_free` when available; otherwise they are zeroed and freed.
- External token positive returns, `-EINVAL`, and `-EPERM` are normalized to `-ENOENT` in `translate_errno()` for non-built-in handlers.
- External loading is disabled cleanly when unsupported or explicitly disabled.

Dependencies:
- JSON-C
- dynamic loader APIs when enabled
- keyslot priority/open helpers
- LUKS2 token JSON/schema helpers
- built-in keyring token callbacks from `luks2_token_keyring.c`
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_token.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_token_keyring.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_token_keyring.c

This file implements the built-in LUKS2 kernel keyring token handler.

Main behavior:
- `keyring_open()` loads the LUKS2 header, gets the token JSON, reads `key_description`, and calls `crypt_keyring_get_user_key()` to retrieve key material from the kernel keyring.
- `-ENOTSUP` from keyring access maps to `-ENOENT`; other negative failures map to `-EPERM`.
- `keyring_validate()` parses token JSON and requires exactly three fields, including non-empty string `key_description`.
- `keyring_dump()` prints the key description.
- `LUKS2_token_keyring_json()` formats a token JSON string with type `LUKS2_TOKEN_KEYRING`, empty `keyslots`, and the given key description.
- `LUKS2_token_keyring_get()` extracts `key_description` into `crypt_token_params_luks2_keyring`.
- `keyring_buffer_free()` releases retrieved material with `crypt_safe_free()`.

Important assumptions:
- `LUKS2_token_keyring_get()` asserts the token type is the keyring token.
- Validation only checks the description is a string and non-empty; a TODO notes possible future format validation.

Dependencies:
- `luks2_internal.h`
- JSON-C
- kernel keyring helper `crypt_keyring_get_user_key`
- safe free helper
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks2/luks2_token_keyring.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/meson.build -->
# File Research: sources/block-storage/cryptsetup/lib/meson.build

This Meson build file defines the cryptsetup library build.

Main build structure:
- Enters `crypto_backend` subdirectory.
- Defines `libutils_io` static library from `utils_io.c`.
- Sets the symbol version script path `libcryptsetup.sym`.
- Defines `libcryptsetup_deps`: crypto backend library, uuid, devmapper, argon2, json-c, blkid, and dl.
- Defines `libcryptsetup_sources`, including the LUKS2 files in this group:
  - `luks2/luks2_reencrypt.c`
  - `luks2/luks2_reencrypt_digest.c`
  - `luks2/luks2_segment.c`
  - `luks2/luks2_token.c`
  - `luks2/luks2_token_keyring.c`
- Builds either a static `cryptsetup` library when `enable_static` is set or a shared `cryptsetup` library with versioning and linker version script.
- Links both library variants with crypto backend and `libutils_io`.
- Defines helper file lists for tools and ssh token builds.
- Installs `libcryptsetup.h`.
- Generates pkg-config metadata for `libcryptsetup`.

This file is the integration point that ensures the reencryption, segment, token, and random support sources are compiled into the core library.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/nls.h -->
# File Research: sources/block-storage/cryptsetup/lib/nls.h

This header centralizes native language support macros.

Behavior:
- Defines default `LOCALEDIR` as `/usr/share/locale` if not provided.
- Includes `<locale.h>` when `HAVE_LOCALE_H` is set; otherwise stubs `setlocale`.
- When `ENABLE_NLS` is set, includes `<libintl.h>` and maps:
  - `_()` to `gettext()`
  - `N_()` to `gettext_noop()` if available, otherwise identity
- When NLS is disabled, stubs `bindtextdomain()` and `textdomain()`, maps `_()` and `N_()` to identity, and defines `ngettext()` as a singular/plural conditional.

This header is why source files such as `luks2_reencrypt.c` and `random.c` can use `_()` around user-visible log messages without conditional localization logic in each file.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/nls.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/random.c -->
# File Research: sources/block-storage/cryptsetup/lib/random.c

This file implements cryptsetup RNG access through kernel random devices and the crypto backend in FIPS mode.

Global state:
- `random_initialised`
- `urandom_fd` for `/dev/urandom`
- `random_fd` for `/dev/random`

Initialization:
- `crypt_random_init()` opens `/dev/urandom` read-only close-on-exec and `/dev/random` read-only nonblocking close-on-exec.
- Both descriptors are mandatory.
- On failure it closes any opened descriptors and returns `-ENOSYS`.
- Logs when running in FIPS mode.

Random data paths:
- `_get_urandom()` reads until the requested length is filled, retrying on `EINTR`; other read errors return `-EINVAL`.
- `_get_random()` waits with `select()` on `/dev/random`, prints entropy/progress warnings after a timeout, reads in 8-byte chunks, handles `EINTR` and nonblocking `EAGAIN/EWOULDBLOCK`, and fills the full buffer.
- `crypt_random_get()` chooses source by quality:
  - `CRYPT_RND_NORMAL`: `/dev/urandom`
  - `CRYPT_RND_SALT`: backend RNG in FIPS mode, otherwise `/dev/urandom`
  - `CRYPT_RND_KEY`: backend RNG in FIPS mode, otherwise default or context-selected `/dev/random` or `/dev/urandom`
- Unknown quality logs an error and returns `-EINVAL`.

Cleanup and defaults:
- `crypt_random_exit()` closes both descriptors and resets initialization.
- `crypt_random_default_key_rng()` maps build-time `DEFAULT_RNG` to `CRYPT_RNG_RANDOM` or `CRYPT_RNG_URANDOM`; any other value aborts.

Important details:
- `/dev/random` progress messages are user-visible and localized with `_()`.
- The file assumes `crypt_random_init()` has opened descriptors before `crypt_random_get()` is called.
- In FIPS mode, salt/key randomness delegates to `crypt_backend_rng()` with prediction resistance flag `1`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/random.c -->