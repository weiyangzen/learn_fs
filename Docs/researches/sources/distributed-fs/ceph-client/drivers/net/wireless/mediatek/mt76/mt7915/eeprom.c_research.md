# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/eeprom.c

Purpose: EEPROM/efuse/default-bin loading and capability/power parsing for MT7915-family devices.

Important APIs: `mt7915_eeprom_init`, `mt7915_eeprom_parse_hw_cap`, `mt7915_eeprom_get_target_power`, `mt7915_eeprom_get_power_delta`, `mt7915_eeprom_has_background_radar`, and `mt7915_sku_group_len`.

Control flow: initialization attempts `mt76_eeprom_init`; flash mode is accepted directly, otherwise the driver checks efuse free blocks and reads EEPROM blocks through MCU. Invalid/missing EEPROM falls back to chip/adie/dbdc-specific default firmware bin. Precal data is optionally loaded from MTD or nvmem if EEPROM flags request it. Hardware capability parsing sets band support, 5/6 GHz choice, chainmask, antenna mask, DBDC chain shifts, and MAC address. Power helpers compute per-channel target power and rate delta by band/chip/adie/TSSI state.

State and persistence: EEPROM bytes live in `mt76.eeprom.data`; `dev->flash_mode`, `dev->cal`, `chainmask`, `chainshift`, band capabilities, and MAC address are derived state. `enable_6ghz` module parameter can force 6 GHz instead of 5 GHz for dual-capable hardware and mutates the buffered EEPROM band field.

Dependencies and integration: depends on Linux firmware loader, mt76 EEPROM/MTD/nvmem helpers, mt7915 MCU EEPROM access, `eeprom.h` offsets, chip/adie predicates, and txpower initialization in `init.c`.

Risks: bad EEPROM fallback can mask board data problems. Free-block heuristic for efuse sufficiency is hardware-specific. 6 GHz selection forces flash/buffer mode and can affect regulatory exposure. Power offsets differ by chip generation and TSSI state.

Test signals: flash EEPROM, efuse-only, invalid EEPROM fallback, default bins for 7915/7916/7981/7986/adie variants, precal MTD/nvmem presence and absence, DBDC chain masks, 6 GHz module parameter, and per-band txpower results.
