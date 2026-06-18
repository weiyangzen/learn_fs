<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/pci.c

Purpose: Implements ath9k PCI bus binding, device ID/subsystem quirk matching, bus operations, PCI probe/remove, optional MSI, ASPM handling, EEPROM reads, suspend/resume PM, and PCI driver registration.

Important APIs and functions: Exposes `ath_pci_init()` and `ath_pci_exit()` to module init/exit. Static pieces include the large `ath_pci_id_table[]`, `ath_pci_read_cachesize()`, `ath_pci_eeprom_read()`, `ath_pci_aspm_init()`, `ath_pci_bus_ops`, `ath_pci_probe()`, `ath_pci_remove()`, `ath_pci_suspend()`, and `ath_pci_resume()`.

Control flow: Probe enables the PCI device with pcim, sets 32-bit coherent DMA, repairs cache line size and latency timer, enables bus mastering, disables PCI retry timeout, maps BAR0, fills channel-context ops, allocates `ieee80211_hw`, stores softc device/memory/driver-data, optionally enables MSI, requests IRQ with shared INTx or MSI flags, calls `ath9k_init_device()`, records MSI state, and logs hardware name/mem/IRQ. Failure unwinds IRQ and hardware allocation. Remove marks unplugged unless module unload is active, deinitializes ath9k, frees IRQ, and frees mac80211 hw. Suspend bypasses full PCI suspend for WOW, otherwise stops BTCOEX, disables hardware, cancels sleep timer, and forces full sleep. Resume reapplies retry-timeout workaround, ASPM init, and clears reset-power-on.

State and persistence: Uses PCI config space, BAR mappings, IRQ registration, `pci_drvdata`, `sc->driver_data`, `sc->irq`, `sc->mem`, `ah->msi_enabled`, `ah->msi_reg`, `ah->aspm_enabled`, `ah->config.aspm_l1_fix`, `AH_UNPLUGGED`, and PCI subsystem quirk flags. PCI config changes persist until device reset/resume reinitialization.

Dependencies and integration points: Integrates with Linux PCI/PM/MSI APIs, mac80211 hardware allocation, ath9k core init/deinit, `ath_isr()`, PCI EEPROM register access, ASPM capability helpers, DMI-driven `ath9k_use_msi`, and PCOEM driver-data handling in `init.c`.

Risks: The device table encodes many subsystem-specific workarounds; ordering matters because more-specific entries must match before generic IDs. MSI is enabled before `ath9k_init_device()` but `sc->sc_ah->msi_enabled` is set after init, so interrupt setup timing depends on when interrupts are enabled. PCI config retry-timeout and cacheline fixes are hardware stability workarounds. ASPM disable for BTCOEX must update both endpoint and parent link. Remove/unplug distinction affects later register access.

Test signals: Probe/remove for generic and subsystem IDs, MSI and INTx IRQ paths, request_irq failure, BAR map failure, ath9k init failure unwind, PCI EEPROM read timeout/success, ASPM enabled/disabled with BTCOEX and AR9285/AR9462, suspend/resume with and without WOW, hot-unplug setting `AH_UNPLUGGED`, and module PCI registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/pci.c -->
