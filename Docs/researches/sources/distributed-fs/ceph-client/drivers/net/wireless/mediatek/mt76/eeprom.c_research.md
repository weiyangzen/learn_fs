# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/eeprom.c

## Purpose
Shared mt76 EEPROM, device-tree calibration, MAC-address override, and per-rate/per-path transmit-power-limit support. It abstracts board data from inline DT properties, MTD partitions, nvmem cells, and power-limit child nodes so individual mt76 chipset drivers can initialize EEPROM buffers and compute regulatory/board power caps without duplicating parsing logic.

## Important APIs, Types, And Functions
- `enum mt76_sku_type` classifies plain rate limits, path backoff limits, and beamforming backoff-offset tables.
- `mt76_get_of_data_from_mtd()` reads board EEPROM bytes from a DT `mediatek,mtd-eeprom` phandle plus offset, handles MTD bitflips as success, optional big-endian word conversion, and records testmode MTD metadata when enabled.
- `mt76_get_of_data_from_nvmem()` reads an `eeprom`-style nvmem cell and copies exactly the requested length.
- `mt76_eeprom_init()` allocates `dev->eeprom.data`, sets `dev->eeprom.size`, and returns whether OF/MTD/nvmem data was found.
- `mt76_eeprom_override()` fills `phy->macaddr` from DT, accepts probe deferral, and generates a random address when the result is invalid.
- `mt76_find_power_limits_node()` chooses a `power-limits` child by country (`dev->alpha2`) or DFS region (`dev->region`), with an unqualified fallback node.
- `mt76_find_channel_node()` selects a channel-range child node from a `channels` array.
- `mt76_get_rate_power_limits()` initializes `struct mt76_power_limits` and applies `rates-*`, `paths-*`, RU, MCS, and beamforming arrays from DT.

## Control Flow
EEPROM initialization starts with allocation in `mt76_eeprom_init()`, then `mt76_get_of_eeprom()` tries inline `mediatek,eeprom-data`, MTD, and nvmem in order. Power-limit calculation finds the region/country-specific node, descends into `txpower-2g`, `txpower-5g`, or `txpower-6g`, selects the channel range, reads optional `txs-delta`, then applies array limits to each destination table. `mt76_apply_multi_array_limit()` walks compressed multi-entry arrays whose first byte is a repeat count and calls `mt76_apply_array_limit()` for each logical row.

## State And Persistence
Persistent board data lives in `dev->eeprom.data`, `dev->eeprom.size`, and optionally `dev->test_mtd` for nl80211 testmode. Runtime power-limit output is written into caller-owned `struct mt76_power_limits`; the only lasting side effect in power-limit lookup is OF node refcounting. MAC-address state is stored in `phy->macaddr`, with random generation on invalid input.

## Dependencies And Integration Points
This file depends on Linux OF, MTD, nvmem, etherdevice helpers, mac80211 channel structures, `mt76.h`, and `mt76_connac.h` for chip-family helpers such as `is_mt799x()`. Chip drivers call the exported functions during probe, channel/power setup, and debug/testmode paths. It integrates with device-tree bindings for EEPROM storage and region-specific power tables.

## Risks
The MTD path can fail from missing labels, short reads, or malformed phandle/offset arrays. OF node refcounts are subtle because matching children are returned to callers. Power tables silently fall back to target power when nodes or arrays are missing, which is safe but can hide DT mistakes. The compressed multi-array parser depends on array lengths matching driver expectations; malformed lengths truncate processing. Random MAC fallback is operationally useful but can surprise systems expecting stable identity.

## Test Signals
Probe should succeed with inline EEPROM, MTD EEPROM, nvmem EEPROM, and no OF EEPROM. Test dmesg for MTD read failures, invalid-MAC randomization, and bitflip handling. Validate regulatory power through `iw phy`, channel max power, and chipset-specific debugfs/testmode outputs. DT power-limit changes should alter computed limits for representative 2 GHz, 5 GHz, and 6 GHz channels, including country/regdomain fallback behavior.
