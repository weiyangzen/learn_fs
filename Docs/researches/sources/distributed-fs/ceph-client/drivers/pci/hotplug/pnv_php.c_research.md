# sources/distributed-fs/ceph-client/drivers/pci/hotplug/pnv_php.c

## Purpose
Implements PowerPC PowerNV PCI hotplug. It registers firmware-described hotplug slots, controls slot power via OPAL, imports/removes device-tree fragments for newly powered slots, scans/removes PCI devices, manages nested hotplug slot registration, and handles surprise hotplug interrupts.

## Important APIs, Types, and Functions
Important state is `struct pnv_php_slot` from platform headers and local `struct pnv_php_event`. Exported APIs are `pnv_php_find_slot()` and `pnv_php_set_slot_power_state()`. Major helpers include `pnv_php_add_devtree()`, `pnv_php_rmv_devtree()`, `pnv_php_enable()`, `pnv_php_disable_slot()`, `pnv_php_activate_slot()`, `pnv_php_register_slot()`, `pnv_php_enable_irq()`, `pnv_php_interrupt()`, `pnv_php_event_handler()`, `pnv_php_register()`, and `pnv_php_unregister()`.

## Control Flow
Module init walks PowerNV PHB compatible nodes and registers pluggable/reset-by-firmware slots. Allocation records slot id, PCI bus, bridge device, workqueue, kref, and hotplug ops. Enabling checks firmware presence and power, optionally asks OPAL to power on the slot, imports a fresh FDT blob through `pnv_pci_get_device_tree()`, applies an OF changeset, adds PCI device-node data, scans devices, and recursively registers child slots. Disabling turns off downstream IRQs, removes PCI devices, unregisters child slots, powers the slot off, and removes dynamic device-tree state. Surprise interrupts read/clear PCIe Slot Status, determine add/remove from DLL active or OPAL presence, optionally freezes a removed EEH PE, then queues work to enable or disable the slot.

## State and Persistence Behavior
Global slot topology is a locked tree rooted at `pnv_php_slot_list`, with krefs for parent/child ownership. Per-slot state includes OPAL id, device node, PCI bus/bridge, current populated/registered/offline state, dynamic FDT/change-set pointers, attention state, power-state-check flag, IRQ number, and broken-PDC flag. Power state and slot activation persist in OPAL firmware; device-tree changes persist in the live OF tree until removal.

## Dependencies and Integration Points
Depends on OPAL PCI calls, PowerNV PCI helpers, OF/FDT changesets, PCI hotplug core, PCI scanning/removal, MSI/MSI-X/INTx interrupt APIs, EEH PE freeze/thaw helpers, and PCIe capability registers. It integrates with platform firmware properties such as `ibm,slot-pluggable`, `ibm,reset-by-firmware`, `ibm,slot-surprise-pluggable`, `ibm,slot-label`, and `ibm,slot-broken-pdc`.

## Risks
Device-tree changeset ordering and cleanup are delicate because child nodes are attached in reverse and may come from one allocated FDT block. Interrupt resources must be disabled for downstream slots before removal or stale MSI/MSI-X state can block further events. OPAL slot activation may fail due to frozen PHBs, requiring reset retry logic. EEH freeze/thaw paths affect error recovery. Parent/child kref and list management must remain balanced across registration failure, nested unregister, and module exit.

## Test Signals
Use PowerNV systems with IODA2/IODA3/OpenCAPI slots: boot-time registration, manual enable/disable, OPAL power failures, FDT import/removal, nested slots, surprise add/remove interrupts with DLLSC and PDC, broken-PDC slots, MSI-X/MSI/INTx fallback, EEH frozen PE recovery, PHB reset retry, module unload, and repeated hotplug while child slots exist.
