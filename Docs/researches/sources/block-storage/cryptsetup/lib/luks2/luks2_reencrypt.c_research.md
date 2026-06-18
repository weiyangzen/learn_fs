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
