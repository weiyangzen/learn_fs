# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/blockdev/mod.rs

This module is the shared block-device interface layer for the backstore. It declares the v1 and v2 blockdev submodules and defines common types/traits used by `BlockDevMgr`, `DataTier`, `CacheTier`, and both backstore versions.

`StratSectorSizes` stores base block-size information and optional crypt-layer block-size information. Its `Display` implementation emits both base and crypt values, using `None` for unencrypted/no crypt cases. v1 blockdevs can populate both fields because encryption is per physical blockdev; v2 normally has only base sizes because encryption is above the assembled cap device.

`InternalBlockDev` is the central internal trait for backstore-owned physical devices. It exposes identity (`bda`, `uuid`, `device`, `physical_path`, metadata version), physical/logical size accounting (`total_size`, `available`, `metadata_size`, `max_stratis_metadata_size`, `in_use`), allocation (`alloc`), detected growth (`calc_new_size`), pool-level metadata persistence (`load_state`, `save_state`), lifecycle teardown, and destructive disowning.

The trait documents an important device-number distinction: `device()` must be the device number used to construct cap-device dm tables. For unencrypted devices this is physical; for v1 encrypted devices it is the unlocked logical LUKS device. The trait also establishes destructive semantics for `disown()`: encrypted devices must destroy keyslots and wipe the LUKS2 header, while unencrypted devices wipe Stratis metadata so blkid/stratisd no longer recognize ownership.

This file contains no tests or implementations beyond formatting; its role is to keep the manager/tier code generic over v1 and v2 block-device implementations.
