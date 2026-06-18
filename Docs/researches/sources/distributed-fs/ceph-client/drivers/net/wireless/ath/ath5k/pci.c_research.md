# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/pci.c

## Purpose
`pci.c` is the PCI bus binding for ath5k. It declares supported PCI IDs, implements PCI EEPROM and MAC address access for ath bus ops, sets up PCI device resources and DMA constraints, allocates the mac80211 hardware object, calls core ath5k initialization, and tears everything down on remove. It also handles small suspend/resume LED and PCI config fixups.

## Important APIs and Control Flow
`ath5k_pci_id_table[]` matches AR5210/5211/5212 and compatible PCI/PCIe devices. `ath5k_pci_read_cachesize()` reads PCI cache line size with a fallback to `L1_CACHE_BYTES >> 2`. `ath5k_pci_eeprom_read()` performs hardware-version-specific EEPROM reads: AR5210 enables `AR5K_PCICFG_EEAE` and reads from mapped EEPROM address space, while newer chips program `AR5K_EEPROM_BASE` and trigger `AR5K_EEPROM_CMD_READ`, polling status until done or timeout. `ath5k_pci_eeprom_read_mac()` validates and copies the MAC from EEPROM words 0x1d..0x1f.

`ath5k_pci_probe()` disables PCIe L0s, enables the device, requires 32-bit DMA, fixes cache line and latency timer, enables bus mastering, disables retry timeout register 0x41, reserves and maps BAR0, allocates `ieee80211_hw`, populates `struct ath5k_hw`, and calls `ath5k_init_ah()` with `ath_pci_bus_ops`. Error paths unwind in reverse order. `ath5k_pci_remove()` calls `ath5k_deinit_ah()`, unmaps/release/disables PCI, and frees the mac80211 object.

## State, Dependencies, and Integration
State includes PCI driver data (`ieee80211_hw`), `ah->pdev`, `ah->dev`, `ah->irq`, `ah->devid`, and `ah->iobase`. Dependencies include Linux PCI, DMA mask, mac80211 allocation, ath common bus ops, register helpers, EEPROM layout macros, and core `base.c` init/deinit. `module_pci_driver()` wires this into the kernel PCI driver model.

## Risks and Test Signals
Risks include BAR mapping failures, unsupported DMA mask, EEPROM read timeout, bad MAC validation, incomplete error unwinding, and resume losing PCI retry-timeout configuration. Test signals include probe/remove under fault injection, valid MAC assignment, successful EEPROM checksum parsing through the bus ops, lspci ID coverage, suspend/resume with LEDs restored, and no resource leaks after repeated bind/unbind.
