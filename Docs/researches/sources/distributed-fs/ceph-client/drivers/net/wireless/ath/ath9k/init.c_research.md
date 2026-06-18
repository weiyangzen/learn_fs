<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/init.c

Purpose: Initializes and tears down the ath9k softc and module, binding Atheros 802.11n hardware to mac80211 across PCI/AHB buses. It owns module parameters, DMI MSI quirks, register access serialization, EEPROM/NVMEM/OF calibration loading, descriptor DMA allocation, hardware capability publication, mac80211 registration, debug/LED/rfkill startup, and staged deinitialization.

Important APIs and functions: Public entry points are `ath_descdma_setup()`, `ath9k_init_device()`, and `ath9k_deinit_device()`. Internal helpers include `ath9k_ioread32()`, `ath9k_iowrite32()`, `ath9k_reg_rmw()`, `ath9k_reg_notifier()`, `ath9k_init_softc()`, `ath9k_set_hw_capab()`, `ath9k_init_txpower_limits()`, `ath9k_of_init()`, `ath9k_nvmem_request_eeprom()`, and module hooks `ath9k_init()`/`ath9k_exit()`.

Control flow: Module init registers PCI, then AHB, then applies DMI quirks. Device init allocates `struct ath_hw`, wires ath common ops and power-save ops, parses platform/OF/NVMEM calibration, initializes locks, tasklets, timers, work items, channel contexts, hardware, TX queues, BT coexistence, channels/rates, crypto, P2P/offchannel state, and ASPM. `ath9k_init_device()` then sets mac80211 capabilities, regulatory hooks, TX/RX DMA, TX power, LEDs, registers `ieee80211_hw`, debugfs, regulatory hints, LEDs, and rfkill polling. Error paths unwind RX, registration, queues, hardware, EEPROM, and allocated SKBs.

State and persistence: Mutates module globals such as `ath9k_use_msi`, `ath9k_modparam_nohwcrypt`, `ath9k_btcoex_enable`, and `is_ath9k_unloaded`; runtime softc state such as `sc->sc_ah`, locks, timers, `cur_chan`, `tx99_power`, beacon slots, antenna diversity, spectral config, and mac80211 capabilities; and hardware/NVMEM/firmware calibration pointers. Persistent inputs are EEPROM, NVMEM calibration cells, firmware EEPROM blobs, OF MAC address, DMI quirks, and PCI subsystem driver data.

Dependencies and integration points: Depends on Linux DMA, firmware, NVMEM, OF, DMI, relay/debug, cfg80211/mac80211, ath common regulatory/rate/crypto helpers, PCI/AHB bus registration, RX/TX setup, BTCOEX, P2P, WOW, LED, rfkill, and DFS detector infrastructure. Register ops become `common->ops` and are consumed by low-level `ath9k_hw_*` code.

Risks: Register serialization is chipset-sensitive; missing `sc_serial_rw` protection can corrupt PCI register FIFO accesses. DMA descriptor allocation must avoid 4 KiB split transactions on older hardware. Firmware/NVMEM calibration length and byte-swap flags determine radio correctness. Capability flags exposed to mac80211 must match hardware features. Error unwinds must not double release devres-managed memory or leak firmware blobs. DMI/MSI and PCOEM quirks are hardware-specific.

Test signals: Probe/remove with PCI and AHB builds, OF no-eeprom firmware path, NVMEM calibration path, invalid calibration sizes, DMI MSI systems, PCOEM subsystem quirks, TX/RX DMA allocation failures, regulatory changes updating TX power/DFS detector, mac80211 registration failure unwinds, LED/rfkill/debugfs lifecycle, and module unload setting `is_ath9k_unloaded`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/init.c -->
