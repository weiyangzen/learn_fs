# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/init.c

Purpose: this file implements shared MT76x0 hardware bring-up, MAC/BBP initialization, WLAN power control, MAC stop, txpower initialization, and mac80211 registration support for both USB and PCIe variants.

Important functions: `mt76x0_chip_onoff` toggles WLAN function state and optional reset; `mt76x0_mac_stop` drains TX/RX queues and disables MAC engines; `mt76x0_init_hardware` performs common post-firmware hardware setup; `mt76x0_register_device` initializes mt76/mac80211 registration and debugfs. Internal helpers include `mt76x0_set_wlan_state`, `mt76x0_reset_csr_bbp`, `mt76x0_init_bbp`, `mt76x0_init_mac_registers`, and `mt76x0_init_txpower`.

Control flow: common init waits for WPDMA/MAC readiness, resets CSR/BBP, enables MCU queue selection, writes common MAC tables, waits for TX/RX idle, initializes BBP and DCOC values, snapshots the RX filter, clears shared keys and WCIDs, loads EEPROM, and initializes PHY. Registration then initializes mt76x02 device data, configures MAC address lists, registers with mac80211, adjusts VHT LDPC on 5 GHz, computes per-channel original/max power, and adds debugfs.

State and persistence behavior: it programs hardware registers, clears security/WCID tables, stores `dev->mt76.rxfilter`, initializes supported-band channel power fields, and schedules no work itself except through PHY init. It does not persist configuration to EEPROM.

Dependencies and integration: it relies on mt76 core MMIO/MCU accessors, `mt76x02` MAC/PHY helpers, `eeprom.c`, static tables from `initvals.h`/`initvals_init.h`, and PHY initialization from `phy.c`. Bus-specific probe paths call this after their firmware and DMA setup.

Risks: register sequencing is timing-sensitive. `mt76x0_set_wlan_state` deliberately does not disable WLAN clock because probe can otherwise fail. MAC stop loops can time out and only warn, leaving possible DMA/MAC residue. The init path assumes firmware is already running and hardware is responsive.

Test signals: probe/resume should pass WPDMA/MAC wait checks, no PLL/XTAL error should log, MAC stop should not warn about TX/RX failure, EEPROM/PHY init should complete, and registered bands should expose sane channel power values. Regression tests should cover USB and PCIe because register access mechanisms differ downstream.
