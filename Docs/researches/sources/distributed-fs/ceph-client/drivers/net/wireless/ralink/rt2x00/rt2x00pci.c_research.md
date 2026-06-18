# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00pci.c

## Purpose
`rt2x00pci.c` is the generic PCI/PCIe bus glue for rt2x00 PCI drivers. It handles PCI enablement, BAR mapping, DMA mask setup, `ieee80211_hw` allocation, rt2x00 device initialization, and remove/suspend/resume forwarding to rt2x00lib.

## Important APIs, Types, And Functions
The exported APIs are `rt2x00pci_probe()`, `rt2x00pci_remove()`, and `rt2x00pci_pm_ops`. Private helpers `rt2x00pci_alloc_reg()` and `rt2x00pci_free_reg()` map BAR0 and allocate EEPROM/RF shadow arrays sized by `struct rt2x00_ops`.

## Control Flow
Probe enables the PCI function, requests regions, enables bus mastering and optionally MWI, requires a 32-bit DMA mask, allocates mac80211 hardware with private `struct rt2x00_dev`, sets driver data, initializes the rt2x00 device fields, detects PCI versus PCIe interface type, maps/register-allocates local storage, stores the PCI device id into `chip.rt` for early efuse users, and calls `rt2x00lib_probe_dev()`. Every failure label unwinds the resources acquired so far. Remove calls `rt2x00lib_remove_dev()`, frees mapped/shadow register storage, frees mac80211 hardware, clears MWI, disables the device, and releases regions. PM callbacks retrieve `rt2x00_dev` from driver data and call `rt2x00lib_suspend()` or `rt2x00lib_resume()`.

## State And Persistence
The file owns the bus-level lifetime of `rt2x00dev->csr.base`, `rt2x00dev->eeprom`, `rt2x00dev->rf`, `rt2x00dev->irq`, `rt2x00dev->dev`, `rt2x00dev->hw`, and `rt2x00dev->name`. EEPROM and RF arrays are kernel shadow storage, not persistent writes to device EEPROM unless other code explicitly writes through rt2x00 helpers.

## Dependencies And Integration Points
It integrates Linux PCI APIs, DMA mask configuration, mac80211 `ieee80211_alloc_hw()`, rt2x00 core probing, and chip-specific `struct rt2x00_ops`. Chip drivers such as `rt61pci.c` provide the PCI id table and invoke this generic probe from their bus-specific `probe` callback.

## Risks
The probe path assumes BAR0 is the CSR region and that devices support 32-bit DMA. Resource unwind ordering is important because rt2x00lib may register mac80211 state and start work before remove. `pci_release_regions()` is called after `pci_disable_device()` in remove, while probe unwind releases regions before disable; both are common but worth preserving intentionally. Early `chip.rt` initialization is needed by some chip-specific paths before full EEPROM parsing.

## Test Signals
Expected signals are clean probe/remove for all supported PCI IDs, valid BAR mapping, successful 32-bit DMA setup, mac80211 registration through rt2x00lib, suspend/resume callbacks on PCI power events, and no leaks or use-after-free reports when probe fails at each staged label.
