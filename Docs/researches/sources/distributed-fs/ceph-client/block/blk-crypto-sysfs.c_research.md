# sources/distributed-fs/ceph-client/block/blk-crypto-sysfs.c

## Purpose
`blk-crypto-sysfs.c` exposes inline-encryption capabilities through `/sys/block/$disk/queue/crypto/`. It creates a `crypto` kobject under a disk queue and publishes supported key types, DUN width, number of keyslots, and per-mode data-unit-size masks.

## Important APIs, Types, and Functions
`struct blk_crypto_kobj` embeds a kobject and points to the queue's `blk_crypto_profile`. `struct blk_crypto_attr` wraps a sysfs attribute and profile-aware show callback. Exported functions are `blk_crypto_sysfs_register()` and `blk_crypto_sysfs_unregister()`. Static show callbacks include `hw_wrapped_keys_show()`, `raw_keys_show()`, `max_dun_bits_show()`, `num_keyslots_show()`, and `blk_crypto_mode_show()`.

## Control Flow
At boot, `blk_crypto_sysfs_init()` initializes one attribute per encryption mode from `blk_crypto_modes[]`, skipping mode zero because `BLK_ENCRYPTION_MODE_INVALID` is expected to be zero. When a disk queue is registered, `blk_crypto_sysfs_register()` checks `q->crypto_profile`; if present, it allocates a wrapper object, points it at the profile, and calls `kobject_init_and_add()` under the queue kobject as `crypto`. Attribute visibility filters hide raw or hardware-wrapped key files if the key type is unsupported and hide mode files if the corresponding mode mask is zero. Unregistering simply puts the stored kobject.

## State and Persistence
The sysfs kobject is transient queue-registration state stored in `q->crypto_kobject`. Attribute values are read directly from the profile and are not persisted. Mode attributes are initialized once at subsystem init into static arrays.

## Dependencies and Integration Points
This file depends on `blk-crypto-internal.h`, `blk_crypto_modes[]`, queue sysfs registration, and profile capability fields. Userspace filesystems and tooling use this tree to decide whether direct inline encryption is available and what configurations are legal.

## Risks
Risks include stale profile pointers if unregister ordering is wrong, exposing unsupported capabilities due to visibility errors, and mode array indexing bugs. The use of `kobject_put()` on registration failure and unregister is essential because the release handler frees the wrapper object.

## Test Signals
Tests should verify sysfs presence only for queues with crypto profiles, visibility of `raw_keys` and `hw_wrapped_keys`, `max_dun_bits` calculation, `num_keyslots`, mode file names matching `blk_crypto_modes[]`, absence of invalid mode zero, and clean register/unregister under disk teardown.
