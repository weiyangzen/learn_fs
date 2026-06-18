# sources/distributed-fs/ceph-client/block/blk-crypto-fallback.c

## Purpose
`blk-crypto-fallback.c` implements software crypto API fallback for blk-crypto when a block device does not natively support a raw-key inline-encryption configuration. It makes encrypted I/O appear like normal bios below the fallback boundary: write bios are encrypted into bounce-page bios before submission, and read bios are decrypted in place after completion.

## Important APIs, Types, and Functions
The exported/internal entry points are `blk_crypto_fallback_bio_prep()`, `blk_crypto_fallback_start_using_mode()`, and `blk_crypto_fallback_evict_key()`. `struct bio_fallback_crypt_ctx` stores a copy of the crypto context, the original iterator, and either read-decrypt work metadata or saved end_io/private fields. The fallback device is modeled as a `struct blk_crypto_profile` with `blk_crypto_fallback_ll_ops`, `blk_crypto_num_keyslots`, and per-slot `crypto_sync_skcipher` transforms.

Key helpers include `blk_crypto_fallback_init()`, `blk_crypto_fallback_keyslot_program()`, `blk_crypto_fallback_evict_keyslot()`, `blk_crypto_alloc_enc_bio()`, `__blk_crypto_fallback_encrypt_bio()`, `blk_crypto_fallback_encrypt_bio()`, `__blk_crypto_fallback_decrypt_bio()`, `blk_crypto_fallback_decrypt_endio()`, and `blk_crypto_dun_to_iv()`.

## Control Flow
Upper layers are expected to call `blk_crypto_start_using_key()`, which eventually calls `blk_crypto_fallback_start_using_mode()` for unsupported raw-key hardware configurations. That routine lazily initializes fallback global state, preallocates transforms for every fallback keyslot for the requested mode, and publishes readiness with release/acquire ordering through `tfms_inited[]`.

At submission time, `blk_crypto_fallback_bio_prep()` validates mode initialization and profile support. For writes, it obtains a fallback keyslot, encrypts each data unit from source pages into allocated bounce pages, builds one or more encrypted bios, and submits those bios. Completion frees bounce pages, propagates status to the source bio, and completes the original bio after all encrypted child bios finish. For reads, it saves the caller's `bi_private` and `bi_end_io`, stores a fallback context in the bio, clears the normal crypto context, and installs `blk_crypto_fallback_decrypt_endio()`. On successful read completion, that end_io queues work on `blk_crypto_wq`; the work item obtains a keyslot, decrypts the original submission range in place, frees the fallback context, sets status, and completes the restored bio.

## State and Persistence
State is global and in-memory only: transform arrays, fallback keyslots, fallback profile, bounce page mempool, fallback context mempool, encryption bioset, high-priority workqueue, random `blank_key`, and mode initialization flags. Per-bio state captures the crypt context and original iterator so decrypt/encrypt covers the submission range even if later splitting changes `bi_iter`.

## Dependencies and Integration Points
This file depends on the Linux crypto skcipher API, mempools, biosets, blk-cgroup bio association cloning, blk-crypto keyslot management, and the block bio submission/completion model. It integrates with `blk-crypto.c` as the fallback called by `__blk_crypto_submit_bio()`.

## Risks
The main risks are deadlocks from allocating transforms or memory in I/O paths, incorrect DUN advancement, alignment errors against data-unit size, completion accounting for multiple encrypted child bios, use-after-free in saved end_io/private restoration, and leaking sensitive key material. The design mitigates these with preallocation, mempools, keyslot profile reuse, explicit zero/blank-key eviction, and queueing decrypt work out of atomic completion context.

## Test Signals
Tests should cover raw-key fallback enablement, missing crypto algorithm returning `-ENOPKG`, write bounce bio splitting beyond `BIO_MAX_VECS`, read decrypt after bio splitting, unaligned bio rejection, child bio error propagation, key eviction, mode readiness races, and memory-pressure scenarios that exercise mempools without direct reclaim deadlock.
