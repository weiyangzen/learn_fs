# sources/distributed-fs/ceph-client/block/blk-crypto-profile.c

## Purpose
`blk-crypto-profile.c` implements generic inline-encryption device profiles and keyslot management. Storage drivers expose capabilities and hardware operations through `struct blk_crypto_profile`; the block layer uses this file to allocate, program, reuse, evict, and reprogram keyslots independent of device-specific details.

## Important APIs, Types, and Functions
The key private type is `struct blk_crypto_keyslot`, containing a reference count, idle LRU node, hash node, key pointer, and backpointer to the profile. Public APIs include `blk_crypto_profile_init()`, `devm_blk_crypto_profile_init()`, `blk_crypto_keyslot_index()`, `blk_crypto_get_keyslot()`, `blk_crypto_put_keyslot()`, `__blk_crypto_cfg_supported()`, `__blk_crypto_evict_key()`, `blk_crypto_reprogram_all_keys()`, `blk_crypto_profile_destroy()`, `blk_crypto_register()`, hardware-wrapped-key helpers (`blk_crypto_derive_sw_secret()`, `blk_crypto_import_key()`, `blk_crypto_generate_key()`, `blk_crypto_prepare_key()`), and capability helpers (`blk_crypto_intersect_capabilities()`, `blk_crypto_has_capabilities()`, `blk_crypto_update_capabilities()`).

## Control Flow
Drivers initialize a profile, fill low-level operations and capability bitmaps, and register it on a queue. If keyslots exist, initialization builds an idle slot list and hash table. For I/O, `blk_crypto_get_keyslot()` first tries a read-locked lookup for an already programmed key. If not found, it enters hardware access with runtime PM and write lock, waits for an idle slot if none are free, programs the key with `ll_ops.keyslot_program`, updates the key hash, sets refs to one, and removes the slot from the idle LRU. Completion calls `blk_crypto_put_keyslot()`, which returns a slot to the idle list and wakes waiters when refs drop to zero.

Eviction removes a key from profile management and calls driver `keyslot_evict` when needed. Hardware reset recovery calls `blk_crypto_reprogram_all_keys()` to reprogram every slot that still has a key pointer. Hardware-wrapped-key ioctls in `blk-crypto.c` call this file's import/generate/prepare/derive helpers, each protected by the same hardware enter/exit sequence.

## State and Persistence
Persistent runtime state is in `struct blk_crypto_profile`: lockdep key, rwsem, optional device for runtime PM, slots array, idle list/spinlock/waitqueue, key hash table, capability bitmaps, max DUN size, key type support, and low-level ops. Key identity is pointer-based; the block layer expects callers not to free keys until eviction and I/O quiescence rules are satisfied.

## Dependencies and Integration Points
This file integrates with request queues, runtime PM, blk-integrity, low-level storage drivers, device-managed resources, hardware-wrapped-key ioctls, and layered-device capability propagation. `blk_crypto_register()` refuses hardware inline encryption when queue integrity is enabled.

## Risks
Risk concentrates around key lifetime, slot refcounting, hardware programming while the device is suspended, and lock ordering between runtime PM and `profile->lock`. The code deliberately resumes the device before taking the profile write lock because resume paths can re-enter key reprogramming. Eviction unlinks keys even on hardware errors because callers may free keys immediately; this avoids stale key pointers but requires warnings to catch driver failures.

## Test Signals
Tests should exercise no-slot profiles, single-slot hash sizing, slot reuse, idle-slot waiting, concurrent get/put/evict, runtime PM reprogramming, wrapped-key unsupported paths, integrity conflict disabling, layered capability intersection/update, and reset recovery through `blk_crypto_reprogram_all_keys()`.
