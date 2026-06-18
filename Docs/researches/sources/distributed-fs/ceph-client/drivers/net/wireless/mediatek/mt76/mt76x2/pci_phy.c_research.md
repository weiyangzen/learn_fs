<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_phy.c

Purpose: MT76x2 PCI PHY channel setup and periodic calibration. It handles TSSI initialization, per-channel calibrations, antenna programming, channel/bandwidth programming, RX gain/power setup, temperature/TSSI compensation, and radio start.

Important APIs/types/functions: `mt76x2_phy_set_channel()`, `mt76x2_phy_set_antenna()`, `mt76x2_phy_calibrate()`, `mt76x2_phy_start()`, and internal TSSI/channel/temp compensation helpers.

Control flow: channel setup computes bandwidth and extension-channel indexes for 20/40/80 MHz, reads RX gain, programs TX power registers/delay/power, sets band/bandwidth/ext CCA, sends MCU channel and gain commands, programs antenna and LDPC, runs initial RC/RXDCOC and channel calibrations when not scanning, initializes AGC, sets default temp compensation, and schedules calibration work. Periodic calibration runs channel calibration if pending, TSSI/temp compensation, channel gain update, then reschedules. Radio start sends radio-on and loads CRs.

State and persistence: calibration flags, TSSI/temp/agc/rx gain state, channel definition, BBP/RF/TX power registers, antenna chain state, EDCCA state, and delayed calibration work.

Dependencies/integration: mt76x2 EEPROM/MCU/MAC/common PHY helpers, mac80211 DFS channel state, mt76 register access, EDCCA, and workqueues.

Risks: calibration must be skipped on silent DFS channels, scan path avoids disruptive calibration, bandwidth index math, external PA/TSSI/temp ALC interactions, and antenna register consistency. Test signals include 20/40/80 MHz channels, DFS unavailable channels, scan channel changes, TSSI/temp-enabled EEPROMs, single/dual antenna modes, and calibration work under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_phy.c -->
