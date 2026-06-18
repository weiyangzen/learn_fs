# File Research: sources/block-storage/stratisd/src/engine/strat_engine/names.rs

## Purpose

`names.rs` centralizes Stratis naming conventions for kernel key descriptions and device-mapper names/UUIDs. It ensures generated names fit DM name and UUID buffer limits and remain versioned.

## Key Constants

- `FORMAT_VERSION = 1`
- Stratis key descriptions use prefix `stratis-1-key-`.
- Volume-key descriptions use prefix `stratis-1-vk-`.

## Key Description Handling

`KeyDescription` extensions:

- `from_system_key_desc()` recognizes Stratis-owned system key descriptions, strips the prefix, rejects empty descriptions, and validates the application key description.
- `to_system_string()` adds the Stratis key prefix for kernel keyring registration.

`VolumeKeyKeyDescription::to_system_string()` formats a pool volume-key description from its UUID.

## Device-Mapper Name Formatting

- `format_crypt_name(dev_uuid)`
  - `stratis-1-private-<dev_uuid>-crypt`
- `format_crypt_backstore_name(pool_uuid)`
  - `stratis-1-private-<pool_uuid>-crypt`
- `format_flex_ids(pool_uuid, role)`
  - private flex device names and UUIDs.
- `format_thin_ids(pool_uuid, role)`
  - thin filesystem names and UUIDs.
- `format_thinpool_ids(pool_uuid, role)`
  - private thinpool names and UUIDs.
- `format_backstore_ids(pool_uuid, role)`
  - physical/cache-layer names and UUIDs.

## Role Enums

- `FlexRole`
  - `MetadataVolume`, `ThinData`, `ThinMeta`, `ThinMetaSpare`
- `ThinRole`
  - `Filesystem(FilesystemUuid)`
- `ThinPoolRole`
  - `Pool`
- `CacheRole`
  - `Cache`, `CacheSub`, `MetaSub`, `OriginSub`

## Behavior Details

The formatting functions build a single string and use it both as the DM name and UUID when appropriate. Each function documents length arithmetic showing the maximum allowed displayed `FORMAT_VERSION` length before `DmNameBuf` or `DmUuidBuf` construction could fail.

## Tests

The key-description test checks:

- Empty Stratis-prefixed key descriptions are ignored.
- Non-prefixed descriptions are ignored.
- Valid prefixed descriptions are parsed.
- Application descriptions may themselves contain the Stratis prefix text after the leading system prefix is stripped.
