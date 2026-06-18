# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/pci.c

## Purpose
This file is the PCIe transport driver for MT7921/MT7922/MT7920/MT7902. It owns PCI device matching, MMIO setup, register address remapping, DMA queue initialization, IRQ map setup, ASPM policy, probe/remove, PCI suspend/resume, and module metadata.

## Important APIs, Types, And Functions
The module entry is `module_pci_driver(mt7921_pci_driver)`. The core callbacks are `mt7921_pci_probe()`, `mt7921_pci_remove()`, `mt7921_pci_suspend()`, `mt7921_pci_resume()`, and `mt7921_pci_shutdown()`. Register access is wrapped by `__mt7921_reg_addr()`, `mt7921_rr()`, `mt7921_wr()`, and `mt7921_rmw()`. DMA setup is in `mt7921_dma_init()`. Unregistration cleanup is in `mt7921e_unregister_device()`.

## Control Flow
Probe enables PCI, ensures memory decoding, allocates an IRQ vector, sets a 32-bit DMA mask, optionally disables ASPM, gets mac80211 ops from firmware feature metadata, allocates mt76 device state, maps BAR0, initializes MMIO, installs mutable bus ops that remap logical register addresses, takes firmware/driver ownership, reads chip revision, resets WFSYS, masks interrupts, requests IRQ, initializes DMA rings, and calls `mt7921_register_device()`.

`mt7921_dma_init()` selects a DMA layout, with MT7902 using MCU TXQ 15, a larger shared MCU RX ring, and no MCU_WA ring. It attaches DMA, disables WPDMA, allocates data, MCU, firmware-download, and RX queues, enables NAPI, and enables DMA. Suspend cancels PM/reset/ROC work, takes driver ownership, waits for regulatory updates, turns off LED, suspends HIF, forces deep sleep, disables NAPI/workers/DMA/interrupts, and gives ownership to firmware. Resume reverses ownership, DMA/IRQ/NAPI/workers, HIF suspend, regulatory update, and LED.

## State And Persistence
State includes PCI drvdata, `dev->fw_features`, HIF ops, IRQ map, bus ops, ASPM support flag, MMIO register remap state, revision, DMA queues, IRQ tasklet, NAPI state, PM suspend flag, wakeup-source flag, and MCU response queue. Hardware state includes WFDMA rings, interrupt masks, PCI MAC interrupt enable, HIF suspend state, deep sleep, LED state, and ownership registers.

## Dependencies And Integration Points
It depends on Linux PCI, OF wakeup-source property, mt76 MMIO/DMA/PCI helpers, mt792x HIF helpers, `pci_mac.c`, `pci_mcu.c`, and common MT7921 registration/RX/TX callbacks.

## Risks
Register remap mistakes can make unsupported addresses return zero after logging, leading to failed hardware operations. MT7902 special cases must keep IRQ map and DMA layout consistent. Suspend/resume ordering is sensitive to regulatory work, DMA idle polling, IRQ tasklet shutdown, and firmware ownership. Error paths must free IRQ vectors and mt76 device without double-freeing managed BAR mappings. ASPM policy can affect stability.

## Test Signals
Probe all listed PCI IDs, verify chip revision and firmware choice, run traffic on MT7921/MT7922/MT7920/MT7902, exercise reset, suspend/resume, wakeup-source, ASPM disabled/enabled, DMA queue allocation failure paths, interrupt masks, and register debugfs reads across remapped address ranges. Check no NAPI/tasklet use after remove.
