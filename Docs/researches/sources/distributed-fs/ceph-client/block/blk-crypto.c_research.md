# sources/distributed-fs/ceph-client/block/blk-crypto.c

## Purpose
`blk-crypto.c` implements the core blk-crypto bio context, encryption mode table, request crypto preparation, key validation, capability checks, key lifecycle operations, fallback selection, and crypto ioctls. It is the central glue between filesystem encryption users, request construction, device crypto profiles, and software fallback.

## Important APIs, Types, and Functions
Important functions include `bio_crypt_set_ctx()`, `__bio_crypt_free_ctx()`, `__bio_crypt_clone()`, `bio_crypt_dun_increment()`, `__bio_crypt_advance()`, `bio_crypt_dun_is_contiguous()`, `bio_crypt_rq_ctx_compatible()`, `bio_crypt_ctx_mergeable()`, `__blk_crypto_rq_get_keyslot()`, `__blk_crypto_rq_put_keyslot()`, `__blk_crypto_free_request()`, `__blk_crypto_submit_bio()`, `__blk_crypto_rq_bio_prep()`, `blk_crypto_init_key()`, `blk_crypto_config_supported_natively()`, `blk_crypto_config_supported()`, `blk_crypto_start_using_key()`, `blk_crypto_evict_key()`, and `blk_crypto_ioctl()`.

## Control Flow
Subsystem init creates a mempool-backed `bio_crypt_ctx` cache and validates every mode's key size, security strength, and IV size. Upper layers initialize keys with `blk_crypto_init_key()`, attach key and DUN to bios with `bio_crypt_set_ctx()`, and call `blk_crypto_start_using_key()` before data-path use when fallback might be needed. Submission checks call `__blk_crypto_submit_bio()` for encrypted bios. If the queue supports the config natively, the bio continues. If not, raw-key bios can be consumed by fallback; wrapped-key bios or disabled fallback produce errors.

Request setup copies the bio crypt context into `rq->crypt_ctx`; dispatch gets a profile keyslot through `blk_crypto_get_keyslot()`, and request cleanup releases keyslot/context. Mergeability uses key pointer equality and DUN continuity to avoid combining incompatible encrypted regions.

The ioctl path requires a queue crypto profile and supports importing raw keys into long-term wrapped keys, generating wrapped keys, and preparing long-term wrapped keys into ephemeral keys. It validates reserved fields and buffer sizes, copies user buffers, calls profile operations, copies results back, and zeroes temporary key buffers.

## State and Persistence
State is per-bio `bio_crypt_ctx`, per-request copied crypt context and keyslot pointer, the static `blk_crypto_modes[]` table, and the crypt context mempool. Keys are caller-owned; this file stores pointers and requires callers to evict before freeing. There is no disk persistence, but ioctl operations produce hardware-wrapped key material for userspace.

## Dependencies and Integration Points
Dependencies include blk-crypto profiles, fallback, block device queues, mempools, usercopy, module parameters, and fscrypt-style upper layers. `submit_bio_noacct()` and blk-mq request code rely on these helpers for validation and request preparation.

## Risks
Risks include DUN arithmetic overflow, incorrect data-unit-size shifts, accepting malformed key sizes or DUN widths, failing to pre-start fallback transforms, leaking temporary key material, and key pointer lifetime violations. Mempool allocation assumptions are explicit: callers using `bio_crypt_set_ctx()` must pass reclaim-capable GFP flags.

## Test Signals
Tests should cover mode table validation, key initialization for raw and wrapped keys, invalid key sizes/DUN sizes/data unit sizes, DUN increment and contiguity, clone/free paths, native vs fallback support decisions, fallback-disabled failures, request keyslot get/put balance, ioctls with reserved fields and too-small output buffers, and temporary key zeroing paths.
