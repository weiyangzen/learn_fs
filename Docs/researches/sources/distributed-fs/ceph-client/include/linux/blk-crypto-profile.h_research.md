# sources/distributed-fs/ceph-client/include/linux/blk-crypto-profile.h

## Purpose
`blk-crypto-profile.h` defines the inline-encryption capability and keyslot-management interface implemented by storage drivers and consumed by the block crypto layer. It describes what crypto modes and key types a device supports and how keys are programmed, evicted, wrapped, imported, generated, and prepared.

## Important APIs, Types, And Functions
`struct blk_crypto_ll_ops` contains driver callbacks: `keyslot_program()`, `keyslot_evict()`, `derive_sw_secret()`, `import_key()`, `generate_key()`, and `prepare_key()`. `struct blk_crypto_profile` contains public driver-initialized fields `ll_ops`, `max_dun_bytes_supported`, `key_types_supported`, `modes_supported[]`, and optional runtime-PM `dev`. Private fields track `num_slots`, a serializing `rw_semaphore lock`, lockdep class, idle slot wait queue/list/spinlock, a key-to-slot hash table, slot hash size, and per-slot state.

Lifecycle and capability functions include `blk_crypto_profile_init()`, `devm_blk_crypto_profile_init()`, `blk_crypto_profile_destroy()`, `blk_crypto_keyslot_index()`, `blk_crypto_reprogram_all_keys()`, `blk_crypto_import_key()`, `blk_crypto_generate_key()`, `blk_crypto_prepare_key()`, `blk_crypto_intersect_capabilities()`, `blk_crypto_has_capabilities()`, and `blk_crypto_update_capabilities()`.

## Control Flow And State
The profile serializes all low-level driver operations through `profile->lock`; operations may sleep and are not called while `profile->dev` is runtime-suspended. If hardware has keyslots, programming and eviction operate on unused slots. If a layered device lacks slots, eviction propagates to underlying devices. Hardware-wrapped-key callbacks convert between raw, long-term wrapped, ephemeral wrapped, and software-secret forms.

Persistent state is in the profile: supported mode bitmasks, key type bitmasks, keyslot hash state, idle LRU ordering, wait queues, and per-keyslot metadata. The header defines contracts but the actual state transitions live in block crypto implementation files.

## Dependencies And Integration Points
It includes `linux/bio.h` and `linux/blk-crypto.h`. `request_queue` references `struct blk_crypto_profile` under `CONFIG_BLK_INLINE_ENCRYPTION`, while drivers register profiles via `blk_crypto_register()` in `blkdev.h`. Filesystems and dm/stacking devices use capability intersection/update helpers to advertise only common supported modes.

## Risks And Test Signals
Risks include failing to initialize capability bitmasks, advertising wrapped-key support without all required callbacks, incorrect DUN byte limits, keyslot leaks, eviction races, runtime-PM misuse, and capability intersection bugs in stacked devices. Tests should cover profile init/destroy, slot reuse and wait paths, key reprogramming after reset, raw and hardware-wrapped key workflows, unsupported mode rejection, and runtime suspend/resume around low-level callbacks.
