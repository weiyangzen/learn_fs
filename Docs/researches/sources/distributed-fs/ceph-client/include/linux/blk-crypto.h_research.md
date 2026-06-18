# sources/distributed-fs/ceph-client/include/linux/blk-crypto.h

## Purpose
`blk-crypto.h` defines the block-layer inline encryption key and bio context API. It lets upper layers attach encryption metadata to bios and lets the block layer decide whether to submit directly to inline hardware or fall back to software crypto.

## Important APIs, Types, And Functions
`enum blk_crypto_mode_num` defines supported modes: invalid, AES-256-XTS, AES-128-CBC-ESSIV, Adiantum, SM4-XTS, and max. `enum blk_crypto_key_type` defines bitflag key types: raw and hardware-wrapped. Size constants are `BLK_CRYPTO_MAX_RAW_KEY_SIZE`, `BLK_CRYPTO_MAX_HW_WRAPPED_KEY_SIZE`, `BLK_CRYPTO_MAX_ANY_KEY_SIZE`, `BLK_CRYPTO_SW_SECRET_SIZE`, `BLK_CRYPTO_MAX_IV_SIZE`, and `BLK_CRYPTO_DUN_ARRAY_SIZE`.

`struct blk_crypto_config` stores mode, data unit size, DUN width, and key type. `struct blk_crypto_key` stores immutable config, log2 data unit size, key size, and key bytes. `struct bio_crypt_ctx` stores a key pointer and starting DUN array. With `CONFIG_BLK_INLINE_ENCRYPTION`, helper APIs include `bio_has_crypt_ctx()`, `bio_crypt_ctx()`, `bio_crypt_set_ctx()`, `bio_crypt_dun_is_contiguous()`, `blk_crypto_init_key()`, `blk_crypto_start_using_key()`, `blk_crypto_evict_key()`, `blk_crypto_config_supported_natively()`, `blk_crypto_config_supported()`, and `blk_crypto_derive_sw_secret()`. `blk_crypto_submit_bio()` wraps `__blk_crypto_submit_bio()` and falls through to `submit_bio()` when appropriate. `bio_crypt_clone()` clones crypt contexts through `__bio_crypt_clone()`.

## Control Flow And State
When inline encryption is enabled, a bio with `bi_crypt_context` carries a key and DUN. `blk_crypto_submit_bio()` checks whether a crypto context exists and whether `__blk_crypto_submit_bio()` handled fallback setup; direct submission proceeds when there is no crypto context or when native hardware support is available. Clone flow copies encryption context only if the source bio has one. Without `CONFIG_BLK_INLINE_ENCRYPTION`, context accessors return false/NULL, keeping call sites buildable but featureless.

State is shared by immutable keys, per-bio crypto contexts, and device profiles/keyslots declared elsewhere. The key lifetime contract is explicit: keys must outlive all bios using them and eviction from all devices.

## Dependencies And Integration Points
The header includes `linux/minmax.h`, `linux/types.h`, `uapi/linux/blk-crypto.h`, `linux/blk_types.h`, and `linux/blkdev.h`. It integrates with `struct bio`, `struct block_device`, request queues, block crypto profiles, filesystems with encrypted data, dm targets, and hardware inline encryption drivers.

## Risks And Test Signals
Risks include freeing keys too early, DUN discontinuity across splits/merges, unsupported crypto configurations, fallback bio allocation failures, hardware-wrapped key misuse, and config-disabled call sites assuming contexts exist. Test signals should include encrypted read/write submission, bio splitting/cloning, DUN contiguity checks, unsupported hardware fallback, memory allocation failure in clone/fallback paths, and eviction after I/O completion.
