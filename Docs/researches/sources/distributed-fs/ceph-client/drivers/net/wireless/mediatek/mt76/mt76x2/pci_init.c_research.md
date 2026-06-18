<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_init.c

Purpose: MT76x2 PCI/MMIO hardware initialization, reset, power-on, resume, stop, cleanup, and device registration.

Important APIs/types/functions: `mt76x2_mac_reset()`, `mt76x2_resume_device()`, `mt76x2_stop_hardware()`, `mt76x2_cleanup()`, `mt76x2_register_device()`, plus PBF/RF power/XTAL helpers.

Control flow: init disables DMA, enables WLAN, powers RF, loads EEPROM, resets MAC/hardware tables, saves RX filter, initializes DMA, marks initialized, starts MAC, initializes MCU firmware, then stops MAC until mac80211 start. MAC reset waits for MAC, configures WPDMA/PBF/default registers/XTAL/RF bypass/MCU clock, programs MAC address and beacon config, and on hard reset clears WCID/drop/key/status tables. Register initializes calibration work, common device caps, hardware, address list, mac80211 registration, debugfs, and channel power.

State and persistence: hardware power/RF/MAC/PBF/WCID/key/register state, DMA queues, initialized/running bits, calibration/watchdog/mac work, firmware state, and debugfs/mac80211 registration.

Dependencies/integration: mt76x2 EEPROM/MCU/MAC/PHY, shared mt76x02 DMA/MAC/beacon/debugfs, mt76 registration, Linux delay APIs.

Risks: hardware reset ordering, hard vs soft reset table clearing, RF power magic values, firmware initialization after MAC start, and failure cleanup after mac80211 registration. Test signals include cold probe, resume, channel start, module unload, MAC reset timeout, EEPROM failure, DMA init failure, and debugfs/channel-power availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_init.c -->
