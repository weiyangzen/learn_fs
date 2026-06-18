# sources/distributed-fs/ceph-client/drivers/ufs/core/ufshcd-crypto.c

## Purpose

`ufshcd-crypto.c` connects UFS inline encryption hardware to the block layer blk-crypto profile and programs UFS crypto keyslots.

## Important APIs, Types, and Functions

Public functions are `ufshcd_crypto_enable()`, `ufshcd_hba_init_crypto_capabilities()`, `ufshcd_init_crypto()`, and `ufshcd_crypto_register()`. Internal functions include `ufshcd_program_key()`, `ufshcd_crypto_keyslot_program()`, `ufshcd_crypto_keyslot_evict()`, and `ufshcd_find_blk_crypto_mode()`. The supported algorithm table maps blk AES-256-XTS to UFS AES-XTS 256.

## Control Flow

Capability init exits if custom crypto profiles are used, host/device capability bits are absent, or allocation/profile initialization fails. Otherwise it reads `REG_UFS_CCAP`, derives config-array base, allocates and caches crypto capability entries, initializes a blk crypto profile with slots, DUN size, raw key support, and supported modes. Keyslot programming chooses a matching UFS crypto capability by algorithm/key size/data-unit mask, fills a config entry, writes registers with CFGE cleared first and set last, then zeroizes the temporary config. Enable reprograms all blk-crypto keys after reset and returns whether standard `CRYPTO_GENERAL_ENABLE` should be set.

## State and Persistence Behavior

State lives in `hba->crypto_capabilities`, `crypto_cfg_register`, `crypto_cap_array`, and `crypto_profile`. Key material is written to hardware keyslots and explicitly zeroized from stack config buffers after programming. Keyslots are cleared during crypto init and eviction.

## Dependencies and Integration Points

It depends on blk-crypto, UFSHCI crypto registers, UFS host hold/release, devm allocation, and request queue registration. It is used by request preparation helpers in `ufshcd-crypto.h`.

## Risks and Test Signals

Risks include unsupported crypto modes, data-unit mask interpretation, broken hardware enable quirks, reset losing keys, key material lifetime in registers/PRDT, and capability count/register offset errors. Test signals include capability discovery, AES-256-XTS keyslot program/evict, reset reprogramming, queue registration, custom profile bypass, and builds without crypto support.
