# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/eeprom.h

Purpose: EEPROM layout definitions, calibration block sizing, band/channel grouping helpers, and external-PA detection for MT7615-family devices.

Important APIs/macros: defines DCOC/TXDPD calibration offsets and full EEPROM size; `enum mt7615_eeprom_field` for chip ID, MAC, NIC/WiFi config, calibration flags, target power, rate power, and per-chip maximum offsets; rate-power and NIC config bit masks; `enum mt7615_eeprom_band`; `enum mt7615_channel_group`; `mt7615_get_channel_group()`; and `mt7615_ext_pa_enabled()`.

Control flow: inline helpers map 5 GHz channels into Japan/UNII groups for target-power lookup and infer external PA/TSSI state from EEPROM NIC config bits. The rest of the file is declarative.

State and persistence: describes persistent EEPROM/OTP fields used by `eeprom.c`, `init.c`, and `mcu.c`. Calibration payloads beyond base EEPROM are appended in the allocated EEPROM buffer for DCOC and TX DPD replay.

Dependencies and integration: includes `mt7615.h` for device type and mt76 EEPROM storage. Channel grouping feeds target-power index selection; external-PA logic affects target chain count and power source selection.

Risks: offsets are chip-specific and close together; mistakes can read wrong power/calibration data. `mt7615_ext_pa_enabled()` interprets cleared TSSI bits as external PA enabled, so inverted logic must be preserved. Channel group boundaries determine regulatory power behavior on 5 GHz channels.

Test signals: power index helpers returning expected offsets for 2 GHz and 5 GHz channels; calibration buffer size sufficient for all DCOC/TXDPD entries; external-PA platforms selecting external PA target-power bytes.
