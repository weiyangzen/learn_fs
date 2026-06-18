# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/pci.c

## Purpose
This file implements the MT7925E PCIe bus driver. It matches PCI IDs, wraps register access through MT7925 remap windows, initializes WFDMA rings and interrupts, wires mt76 driver/HIF operations, registers the mac80211 device, and handles suspend/resume/remove/shutdown.

## Important APIs, Types, And Functions
The public module entry is `module_pci_driver(mt7925_pci_driver)`. Key helpers are `mt7925_pci_probe()`, `mt7925_pci_remove()`, `mt7925_pci_suspend()`, `_mt7925_pci_resume()`, `mt7925_dma_init()`, and `mt7925e_unregister_device()`. Register remapping is implemented by `__mt7925_reg_addr()`, `mt7925_reg_map_l1()`, `mt7925_reg_map_l2()`, `mt7925_reg_remap_restore()`, and bus-op wrappers `mt7925_rr()/wr()/rmw()`.

## Control Flow
Probe enables the PCI device, maps BAR0, enables bus mastering and IRQ vectors, sets a 32-bit DMA mask, optionally disables ASPM, clones mac80211 ops based on firmware features, allocates `mt792x_dev`, installs remapped bus ops, takes driver ownership from firmware, reads chip revision, resets WFSYS, requests IRQ, initializes DMA queues, then calls `mt7925_register_device()`. DMA setup disables WFDMA, creates data/MCU/FWDL TX rings, event/data RX rings, initializes NAPI, and enables DMA. Suspend aborts ROC, waits for regulatory updates to finish, enables deep sleep and HIF suspend, waits for idle, disables NAPI/DMA/interrupts, then gives ownership to firmware. Resume reacquires driver ownership, conditionally reinitializes WPDMA, reenables interrupts/DMA/NAPI, resumes HIF, restores deep-sleep policy, and reapplies regulatory state.

## State And Persistence
Persistent driver state includes `dev->backup_l1/l2` remap registers, ASPM support, `hif_idle`, `hif_resumed`, PM suspended state, IRQ masks, NAPI state, queued MCU response SKBs, DMA queues, and firmware/regulatory flags. Suspend persists country information and deep-sleep preference but tears down active host DMA/interrupt state until resume.

## Dependencies And Integration Points
The file integrates Linux PCI PM, mt76 MMIO/DMA/NAPI, connac PM ownership, MT7925 MCU/MAC routines, regulatory update code, and the shared `mt792x_dma`/reset helpers. Its `mt76_driver_ops` bind PCI TX preparation, RX parsing, station events, and survey update callbacks to the rest of the driver.

## Risks
Register remapping is fragile: the L1/L2 backup/restore sequence must bracket indirect accesses without leaving the HIF window pointing at the wrong range. Suspend/resume has several timeout paths where NAPI, deep sleep, HIF suspend, and ownership state must be restored correctly. DMA initialization and reset depend on exact ring IDs and interrupt masks. ASPM and ownership polling timing can expose platform-specific failures.

## Test Signals
PCI probe/remove, firmware load, association traffic, module unload, ASPM on/off, suspend/resume/freeze/thaw/poweroff/restore, regulatory update during suspend, IRQ/NAPI activity, WPDMA reset, and firmware reset recovery are the primary validation signals. Timeout paths should trigger `mt792x_reset()` without leaking IRQs, NAPI, or queues.
