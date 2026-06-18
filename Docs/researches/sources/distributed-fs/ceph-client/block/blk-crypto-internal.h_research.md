# sources/distributed-fs/ceph-client/block/blk-crypto-internal.h

## Purpose
`blk-crypto-internal.h` is the private block-layer header that connects blk-crypto core, keyslot profile management, sysfs, request preparation, fallback support, and request/bio merge logic. It supplies conditional inline stubs when `CONFIG_BLK_INLINE_ENCRYPTION` or fallback support is disabled.

## Important APIs, Types, and Functions
The central private type is `struct blk_crypto_mode`, which records the sysfs name, crypto API cipher string, raw key size, security strength, and IV size for each encryption mode. The header declares `blk_crypto_modes[]`, `bio_crypt_dun_increment()`, `bio_crypt_rq_ctx_compatible()`, `bio_crypt_ctx_mergeable()`, `blk_crypto_get_keyslot()`, `blk_crypto_put_keyslot()`, `__blk_crypto_evict_key()`, `__blk_crypto_cfg_supported()`, `blk_crypto_ioctl()`, request keyslot functions, bio crypt context advance/free functions, and fallback functions.

Inline helpers include merge checks (`bio_crypt_ctx_back_mergeable()`, `bio_crypt_ctx_front_mergeable()`, `bio_crypt_ctx_merge_rq()`), request defaults (`blk_crypto_rq_set_defaults()`), request state predicates, `blk_crypto_supported()`, `bio_crypt_advance()`, `bio_crypt_free_ctx()`, `bio_crypt_do_front_merge()`, `blk_crypto_rq_get_keyslot()`, `blk_crypto_rq_put_keyslot()`, `blk_crypto_free_request()`, and `blk_crypto_rq_bio_prep()`.

## Control Flow
Request construction code uses the inlines to copy bio crypto context into requests, get or release hardware keyslots only when the request is encrypted, and maintain DUN continuity during front merges. Merge code uses the compatibility helpers to reject merging encrypted bios or requests with incompatible keys or non-contiguous data unit numbers. Submission code calls `blk_crypto_supported()` to require native support in `submit_bio_noacct()` and calls fallback preparation through the exported fallback hook when configured.

## State and Persistence
The header owns no runtime storage, but it defines the expectations for `request->crypt_ctx`, `request->crypt_keyslot`, `bio->bi_crypt_context`, and `blk_crypto_key` mode metadata. Its disabled-configuration stubs are significant state behavior: they make non-encryption builds compile while returning false support, no-op cleanup, and `-ENOTTY` for crypto ioctls.

## Dependencies and Integration Points
It includes `linux/bio.h` and `linux/blk-mq.h` and is included by crypto core, sysfs, profile, fallback, and request preparation paths. It bridges public blk-crypto APIs, private block request internals, and compile-time feature flags.

## Risks
Because these are hot-path inline helpers, a semantic mismatch between enabled and disabled stubs can create subtle bugs. Mergeability depends on DUN continuity and key pointer identity; relaxing it incorrectly would corrupt encrypted data. Request cleanup assumes keyslots are put before crypt contexts are freed. Stubs must preserve existing non-encryption behavior and reject ioctls/support queries predictably.

## Test Signals
Relevant tests are build coverage for all combinations of inline encryption and fallback config, encrypted request merge tests, front/back merge DUN tests, disabled-config ioctl behavior, keyslot get/put balancing, and request cleanup assertions that `crypt_keyslot` is not leaked.
