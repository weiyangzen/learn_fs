<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/eeprom.h

Purpose: MT76x2-specific EEPROM type declarations and capability predicates.

Important APIs/types/functions: `enum mt76x2_cal_channel_group`, `struct mt76x2_tx_power_info`, `struct mt76x2_temp_comp`, prototypes for power/RX/temp helpers, and inline predicates `mt76x2_has_ext_lna()`, `mt76x2_temp_tx_alc_enabled()`, and `mt76x2_tssi_enabled()`.

Control flow: declarative header; PHY and init code call these helpers to decide power-control and gain paths.

State and persistence: no local state; structs carry decoded runtime views of EEPROM/eFUSE calibration.

Dependencies/integration: includes shared `mt76x02_eeprom.h`; used by mt76x2 EEPROM, init, MCU, and PHY code.

Risks: predicates encode mutually exclusive temp ALC vs TSSI behavior; wrong NIC_CONF bit interpretation changes calibration mode. Test signals include EEPROM bit combinations for external LNA, temp ALC, and TSSI; channel group coverage; and compile checks for all mt76x2 objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/eeprom.h -->
