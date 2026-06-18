# File Research: sources/block-storage/stratisd/src/engine/strat_engine/crypt/consts.rs

Read status: complete, 43 lines.

## Purpose

`consts.rs` defines shared crypt/LUKS2 token constants, default metadata sizing constants, and Clevis-related constants.

## Token JSON Keys

- `TOKEN_TYPE_KEY`
- `TOKEN_KEYSLOTS_KEY`
- `STRATIS_TOKEN_DEVNAME_KEY`
- `STRATIS_TOKEN_POOL_UUID_KEY`
- `STRATIS_TOKEN_DEV_UUID_KEY`
- `STRATIS_TOKEN_POOLNAME_KEY`

## Token IDs

- `STRATIS_TOKEN_ID = 0`
- `LUKS2_TOKEN_ID = 1`
- `CLEVIS_LUKS_TOKEN_ID = 2`

These fixed IDs are used heavily by legacy v1 crypt handling.

## Token Types

- `LUKS2_TOKEN_TYPE = "luks2-keyring"`
- `STRATIS_TOKEN_TYPE = "stratis"`
- `CLEVIS_TOKEN_TYPE = "clevis"`

## Crypt Sizing Constants

- `STRATIS_MEK_SIZE`: 512-bit media encryption key size.
- `LUKS2_SECTOR_SIZE`: 4096 bytes.
- `DEFAULT_CRYPT_METADATA_SIZE_V1`: 16 KiB.
- `DEFAULT_CRYPT_METADATA_SIZE_V2`: 64 KiB.
- `DEFAULT_CRYPT_KEYSLOTS_SIZE`: 16352 KiB.
- `DEFAULT_CRYPT_DATA_OFFSET_V2`: 34816 sectors.

## Clevis Constants

- `CLEVIS_TANG_TRUST_URL`: Stratis-specific JSON key allowing Tang URL trust.
- `CLEVIS_TOKEN_NAME`: null-terminated `clevis`.
- `CLEVIS_RECURSION_LIMIT`: 20.
