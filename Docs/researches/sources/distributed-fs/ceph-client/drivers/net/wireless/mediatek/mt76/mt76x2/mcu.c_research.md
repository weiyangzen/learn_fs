<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mcu.c

Purpose: MT76x2 common MCU command helpers for channel switching, CR loading, gain initialization, and TSSI compensation.

Important APIs/types/functions: `mt76x2_mcu_set_channel()`, `mt76x2_mcu_load_cr()`, `mt76x2_mcu_init_gain()`, and `mt76x2_mcu_tssi_comp()`.

Control flow: channel switch sends `CMD_SWITCH_CHANNEL_OP` twice: first without extension channel, then after a short delay with `0xe0 + bw_index`. CR load sends NIC configuration-derived mode data. Gain init can set a force bit in the channel word. TSSI compensation wraps calibration data in `CMD_CALIBRATION_OP`.

State and persistence: updates firmware/MCU channel, BBP/RF CR state, gain tables, and TSSI calibration state.

Dependencies/integration: shared mt76 MCU send path, mt76x2 EEPROM config bits, mt76x2 PCI/USB PHY channel setup and calibration.

Risks: two-step channel switch ordering, bandwidth index encoding, EEPROM config packing, and calibration command timeout. Test signals include 20/40/80 MHz channel switches, scans vs normal channel changes, forced gain init, TSSI-enabled devices, and MCU timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mcu.c -->
