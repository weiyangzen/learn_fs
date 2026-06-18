# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/eeprom.c

## Purpose
This file loads, validates, defaults, and interprets MT7996-family EEPROM/efuse data. It chooses default EEPROM binaries by chip variant/FEM, reads efuse or external EEPROM blocks through MCU, parses per-band stream/path capabilities, applies efuse chip-config caps, sets MAC address, and exposes power/radar capability helpers.

## Important APIs, Types, And Functions
Public functions are `mt7996_eeprom_init()`, `mt7996_eeprom_parse_hw_cap()`, `mt7996_eeprom_get_target_power()`, `mt7996_eeprom_get_power_delta()`, and `mt7996_eeprom_has_background_radar()`. Important internals include `mt7996_check_eeprom()`, `mt7996_eeprom_name()`, `mt7996_eeprom_parse_stream()`, `mt7996_eeprom_variant_valid()`, `mt7996_eeprom_check_or_use_default()`, `mt7996_eeprom_load()`, `mt7996_eeprom_parse_efuse_hw_cap()`, and `mt7996_eeprom_parse_band_config()`.

## Control Flow
Initialization loads EEPROM data via `mt76_eeprom_init()`. Valid flash data is accepted; otherwise data is zeroed and loaded from external EEPROM or efuse block reads. Efuse free-block count can force default use when data is insufficient. The first block is checked for chip ID validity before reading remaining blocks. After loading, default firmware data is requested and either used as fallback or as a variant validation reference. Hardware capability parsing reads path/RX path/NSS fields per band, optionally clamps them by MCU chip-config capability, normalizes invalid values to max, detects aux RX, sets antenna mask, chainmask and chain shifts, and parses band selection. Init then copies the primary MAC address and applies mt76 EEPROM override.

## State And Persistence
State includes `dev->mt76.eeprom.data`, `dev->eeprom_mode`, variant fields `dev->var.type/fem`, `dev->has_eht`, `dev->wtbl_size_group`, per-phy antenna and chain masks, `phy->has_aux_rx`, `dev->chainmask`, `dev->chainshift[]`, and `dev->mphy.macaddr`. EEPROM content persists for device lifetime and drives channel/power/capability setup.

## Dependencies And Integration Points
It depends on Linux firmware loading, mt76 EEPROM initialization/override, MT7996 MCU efuse/eeprom/chip-config commands, chip/variant helpers, per-band PHY objects, channel group helpers, and default EEPROM binary names from `mt7996.h`.

## Risks
Wrong default binary selection can advertise invalid chains or FEM layout. Variant validation only ensures live EEPROM does not exceed default stream/path/NSS and FEM matches expected mode; subtle calibration mismatches still depend on firmware data quality. Efuse free-block heuristic can force defaults. Chainshift accumulation across bands must match present phys. Power delta sign handling affects regulatory TX power.

## Test Signals
Flash EEPROM, external EEPROM, efuse, and default-bin fallback boots; all supported chip IDs and variant/FEM combinations; per-band 2/5/6 GHz capability exposure; MAC override; target power/delta queries; background radar capability decisions; and invalid EEPROM fallback validate this file.
