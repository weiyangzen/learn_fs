# File Research: sources/block-storage/linux-dm/drivers/md/dm-crypt.c

## Role
Implements the `crypt` device-mapper target: a transparent block encryption/decryption layer that maps a logical range to an underlying block device while transforming bio data with Linux Crypto API skcipher or AEAD algorithms.

## Main Structures
- `struct crypt_config` stores the target-wide device, offset, cipher transforms, key material, IV generator, workqueues, write-ordering thread, mempools, bioset, integrity settings, sector size, and feature flags.
- `struct dm_crypt_io` is per-bio state containing the original bio, optional integrity metadata buffer, pending counters, async crypto context, error state, sector, and write-tree node.
- `struct convert_context` tracks multi-sector crypto conversion progress across input/output bios and async crypto restarts.
- `struct crypt_iv_operations` abstracts IV mode lifecycle and generation/postprocessing.

## Target Interface
- Constructor syntax is `<cipher> [<key>|:<key_size>:<user|logon|encrypted|trusted>:<key_description>] <iv_offset> <dev_path> <start> [<#opts> <opts>...]`.
- `crypt_ctr()` parses optional features first, configures cipher/IV/key state, validates offsets, opens the backing device, creates request/page/tag mempools, allocates workqueues, and starts the ordered write submission thread.
- `crypt_map()` bypasses flush and discard directly to the lower device, validates sector alignment and size against the internal encryption sector size, allocates integrity metadata when needed, and submits reads or writes into the crypto pipeline.
- `crypt_status()` emits table, info, and IMA status. Table status can emit either the hex key or a keyring descriptor.
- `crypt_message()` supports suspended-only key operations: `key set <key>` and `key wipe`.
- `crypt_preresume()` rejects resume if no valid key is installed.

## Crypto and IV Modes
- Supports legacy cipher syntax (`cipher[:keycount]-mode-iv:ivopts`) and new Crypto API syntax (`capi:cipher_api_spec-iv:ivopts`).
- IV generators include `plain`, `plain64`, `plain64be`, `essiv`, `benbi`, `null`, `lmk`, `tcw`, `random`, `eboiv`, and `elephant`.
- Compatibility modes implement Loop-AES LMK, old TrueCrypt TCW whitening, BitLocker EBOIV, and BitLocker Elephant diffuser behavior.
- `essiv` is represented through the Crypto API transform string, while this file supplies the plain sector-number IV input.
- Multi-key modes distribute sectors over `tfms_count`, with LMK using 64 transforms and key splitting.

## Data Path
- Writes allocate a new clone bio with freshly allocated pages, encrypt from the original bio into that clone, then submit the encrypted clone to the lower device.
- Reads clone and submit the original bio layout to the lower device first; successful completion queues in-place decryption into the original bio.
- `crypt_convert()` walks one encryption sector at a time, allocates/reuses crypto requests, handles synchronous and asynchronous Crypto API completion, and maps errors to block status.
- `kcryptd_async_done()` handles Crypto API callbacks, post-IV transforms, AEAD authentication failures, request cleanup, and final read/write completion.
- Separate `io_queue`, `crypt_queue`, and `dmcrypt_write` thread keep IO submission, CPU crypto work, and ordered write dispatch from blocking each other.
- Zoned devices force no write workqueue and inline write completion to preserve write ordering; zone append is emulated to avoid IV mismatch.

## Integrity Support
- Optional `integrity:<tag_size>:aead` enables AEAD authenticated encryption over sector number, IV, data, and tag.
- Optional `integrity:<tag_size>:none` provides per-sector on-disk metadata space, including random IV storage when needed.
- Requires the lower device integrity profile `DM-DIF-EXT-TAG` with matching tuple/tag size and interval size.
- AEAD failures log rate-limited integrity errors and audit events and surface as `BLK_STS_PROTECTION`.

## Key Handling
- Hex keys are decoded into `cc->key`, installed into all transforms, then the supplied key string is wiped in-place.
- Keyring descriptors may reference `logon`, `user`, `encrypted`, or `trusted` keys when configured; key descriptors with whitespace are rejected because DM table status does not escape them.
- HMAC-based `authenc(...)` AEAD keys are repacked into the Crypto API `crypto_authenc_key_param` format.
- `crypt_wipe_key()` clears key validity, randomizes key material into transforms, wipes IV-private material, clears stored keyring state, and zeroes the in-memory key.

## Important Invariants
- Bios must be aligned and sized to `sector_size`; `iv_offset` must also align to that sector size.
- Request memory layout is carefully aligned as crypto request, private `dm_crypt_request`, IV, original IV, original sector, and tag offset.
- Buffer page allocation is serialized on fallback to avoid mempool deadlock when multiple large bios need the whole pool.
- Page usage is capped per dm-crypt client from a global low-memory page budget.
- Flush and discard bypass crypto because they carry no transformable data; discard ordering is left to callers via flush.
- Inline write mode waits for all async crypto completions before submitting writes that require ordering.

## Filesystem/Storage Relevance
`dm-crypt` is the main Linux block encryption target used beneath filesystems and above raw disks, partitions, LVM, RAID, or other DM targets. Its sector sizing, integrity tag handling, discard policy, and zoned-device behavior directly affect filesystem correctness, performance, and recoverability.

## Notable Risks
- Key, IV, integrity, and async completion paths are tightly coupled; ordering mistakes can create silent corruption or authentication failures.
- Legacy compatibility modes intentionally preserve older, weaker on-disk formats and should be understood as compatibility paths.
- Memory pressure behavior is complex because crypto requests, clone bios, pages, and integrity tags all have independent pools and fallback paths.
