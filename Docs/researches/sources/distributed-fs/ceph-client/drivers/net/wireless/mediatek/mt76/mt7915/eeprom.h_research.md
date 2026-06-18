# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/eeprom.h

Purpose: EEPROM offset map, calibration sizes, band/SKU enums, and inline helpers for MT7915-family EEPROM interpretation.

Important definitions: `enum mt7915_eeprom_field`, calibration flags and sizes, Wi-Fi configuration bit masks, rate delta masks, `enum mt7915_adie_sku`, band selection enums, `enum mt7915_sku_rate_group`, `mt7915_get_channel_group_5g`, `mt7915_get_channel_group_6g`, `mt7915_tssi_enabled`, `mt7915_get_cal_group_size`, and `mt7915_get_cal_dpd_size`.

Control flow: inline helpers map channel numbers to EEPROM power groups, inspect EEPROM config bits for TSSI enablement, and select group/DPD precal sizes by chip, band, and adie generation.

State and persistence: this header documents the persistent EEPROM layout. Callers read `dev->mt76.eeprom.data` and chip/adie state to derive calibration sizes, target-power indices, band capabilities, and TSSI behavior.

Dependencies and integration: included by EEPROM, init, debugfs, and power code. Depends on `mt7915.h`, Linux bitfield helpers, and chip/adie helper functions provided elsewhere.

Risks: offsets are hardware ABI. A wrong offset or group-size constant can make EEPROM reads corrupt capability/power interpretation or allocate the wrong precal buffer size. 6 GHz fields only appear in v2 layout, so callers must guard old hardware.

Test signals: unit-style validation of channel group mapping boundaries, EEPROM fixture parsing for all supported chips/adies, TSSI bit behavior for DBDC and non-DBDC, precal size selection, and build coverage for all includers.
