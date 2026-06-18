# `sources/distributed-fs/ceph-client/drivers/md/dm-crypt.c`

## Purpose

`dm-crypt.c` implements the `crypt` device-mapper target, providing transparent encryption and decryption over a linear backing block-device range. It maps bios to the configured backing device, encrypts writes into cloned output bios, decrypts reads after lower-device completion, supports multiple IV schemes, supports optional authenticated/integrity metadata, handles key loading from hex strings or kernel keyrings, and exposes suspend-time key update/wipe messages.

## Important APIs, Types, and Functions

The core state is `struct crypt_config`: backing `dm_dev`, start sector, cipher/IV configuration, key material, integrity tag parameters, crypto transform arrays, request/page/tag mempools, bioset, IO and crypto workqueues, write-submission kthread, and flags such as `DM_CRYPT_KEY_VALID`, `DM_CRYPT_NO_READ_WORKQUEUE`, and `DM_CRYPT_WRITE_INLINE`. `struct dm_crypt_io` is per-bio state, carrying the base bio, integrity metadata, conversion context, pending counters, saved iterators, error state, and write-ordering tree node. `struct convert_context` tracks multi-sector crypto progress and async restart completion.

`crypt_ctr()` parses `<cipher> <key> <iv_offset> <dev_path> <start> [features]`, allocates all persistent resources, selects workqueue policy, handles zoned-device constraints, configures integrity, and registers per-IO data size. `crypt_map()` is the runtime entry point: it bypasses flush/discard, splits oversized bios where safe, validates sector alignment, allocates per-bio integrity metadata, and queues reads or writes. `crypt_convert()`, `crypt_convert_block_skcipher()`, and `crypt_convert_block_aead()` drive per-sector crypto through the Linux crypto API. Completion and scheduling are split across `crypt_endio()`, `kcryptd_queue_crypt()`, `kcryptd_crypt_read_convert()`, `kcryptd_crypt_write_convert()`, `kcryptd_async_done()`, and the `dmcrypt_write()` kthread.

The IV framework is represented by `struct crypt_iv_operations` and implementations for `plain`, `plain64`, `plain64be`, `essiv`, `benbi`, `null`, `lmk`, `tcw`, `random`, `eboiv`, and `elephant`. Constructor helpers `crypt_ctr_cipher_new()`, `crypt_ctr_cipher_old()`, `crypt_ctr_ivmode()`, `crypt_ctr_auth_cipher()`, and `crypt_ctr_optional()` translate device-mapper table syntax into crypto API transforms and feature flags. Key helpers include `crypt_set_key()`, `crypt_set_keyring_key()`, `crypt_setkey()`, and `crypt_wipe_key()`.

## Control Flow

On table load, optional features are parsed before cipher allocation because integrity and sector-size choices affect transform setup. The constructor allocates crypto transforms, initializes IV handling, decodes or fetches the key, creates request/page/tag mempools, opens the backing device, configures integrity profiles if requested, creates IO and crypto queues, and starts the write-submission thread.

For reads, `crypt_map()` clones and submits the original bio to the backing device through `kcryptd_io_read()`. Lower-device completion calls `crypt_endio()`, which queues decryption. Decryption runs in a safe context, possibly asynchronously through the crypto API, and completes the original bio when all pending sectors have finished. For AEAD read failures, `crypt_dec_pending()` performs a second read into a private buffer for recheck before logging an integrity audit failure.

For writes, `crypt_map()` queues encryption first. `kcryptd_crypt_write_convert()` allocates an output bio, encrypts sector-sized chunks into it, and then submits it directly, through a workqueue, or through `dmcrypt_write()` depending on workqueue flags and ordering requirements. A red-black tree sorted by original sector preserves write-submission ordering for the write thread. Flush and discard are remapped directly because no data conversion is needed.

## State and Persistence Behavior

Persistent on-disk state is the ciphertext and, when configured, lower-device integrity tuples containing AEAD tags or stored IVs. In-memory state includes key bytes, IV private data, transform handles, per-client page budget counters, mempools, and pending IO counters. Key material is treated as sensitive: constructor key strings are zeroed after use, `crypt_wipe_key()` clears validity, overwrites key material, wipes IV private state, and uses `kfree_sensitive()`/`memzero_explicit()` on teardown. `postsuspend`, `preresume`, and `resume` gate key replacement: `crypt_message()` accepts `key set` and `key wipe` only while suspended, and `crypt_preresume()` refuses resume without a valid key.

## Dependencies and Integration Points

The target integrates with device mapper through `struct target_type crypt_target`, providing `.ctr`, `.dtr`, `.map`, `.status`, `.postsuspend`, `.preresume`, `.resume`, `.message`, `.iterate_devices`, `.io_hints`, and optional zoned `.report_zones`. It depends heavily on the kernel crypto API (`skcipher`, `aead`, `authenc`, `ahash`, AES helpers), block integrity APIs, keyrings (`user`, `logon`, `encrypted`, `trusted` when enabled), mempools, biosets, workqueues, kthreads, red-black trees, and `dm-audit`. It advertises `DM_TARGET_ZONED_HM` and `DM_TARGET_ATOMIC_WRITES`, requests zone-append emulation when needed, and tightens queue limits to its encryption sector size and bio-vector constraints.

## Risks and Edge Cases

Correctness depends on strict alignment between bio sectors, configured encryption sector size, lower-device logical block size, and integrity interval size. The async crypto paths are sensitive to pending-count balance, request lifetime, and restart completions. AEAD mode must keep sector number, IV, tag offset, and integrity metadata synchronized, otherwise reads fail with protection errors. Zoned devices require inline write completion and no write workqueue to preserve ordering. Memory pressure is a major risk, mitigated by per-client page budgets and mempools, but the allocation paths are complex. Legacy IV modes (`lmk`, `tcw`, `elephant`) include compatibility-only algorithms with additional key material and sector-size restrictions. A notable implementation signal is the very dense resource unwinding in `crypt_ctr()`/`crypt_dtr()`, which should be regression-tested around every constructor failure point.

## Test Signals

Useful tests include table creation for old and `capi:` cipher syntax, all IV modes, keyring and hex keys, suspended `key set`/`key wipe`, integrity `none` and `aead`, non-512 sector sizes, discard/flush bypass, bio splitting limits, AEAD bad-tag logging, zoned device write ordering, atomic writes, and failure injection for mempool/workqueue/crypto allocation paths. Runtime tests should verify data survives remounts and table reloads, status output round-trips table syntax, IMA status omits secret key bytes, and no pending-page counter leaks remain after teardown.
