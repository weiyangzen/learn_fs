<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_eeprom.c

Purpose: shared EEPROM/eFUSE access helpers for mt76x02 devices. It reads 16-byte eFUSE blocks, copies EEPROM ranges, derives hardware band capabilities, checks external PA flags, and extracts RSSI/LNA calibration values.

Important APIs/types/functions: `mt76x02_get_efuse_data()`, `mt76x02_eeprom_copy()`, `mt76x02_eeprom_parse_hw_cap()`, `mt76x02_ext_pa_enabled()`, `mt76x02_get_rx_gain()`, and `mt76x02_get_lna_gain()`.

Control flow: eFUSE reads program address/mode/kick bits, poll for completion, treat all-ones AOUT as blank, and copy four data registers into the caller buffer. Capability parsing interprets board type from `NIC_CONF_0`. RX gain extraction reads shared LNA/RSSI offsets and falls back between 5 GHz groups if EEPROM fields are invalid.

State and persistence: reads from device eFUSE and `dev->mt76.eeprom.data`; it updates band capability flags in `mphy.cap` but does not persist changes externally.

Dependencies/integration: Linux unaligned helpers, mt76 register access, `mt76x02_eeprom.h`, mt76x2 and mt76x0 EEPROM loaders/PHY calibration.

Risks: byte/word offset errors, invalid field fallback, eFUSE timeout, and board capability misclassification. Test signals include blank eFUSE, valid EEPROM override, 2G-only/5G-only boards, external PA configurations, and RSSI calibration sanity across channel groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_eeprom.c -->
