# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pnv-pci.h

Purpose: This header exposes PowerNV PCI and PCI hotplug interfaces backed by OPAL, including slot ID encoding, device-tree retrieval, slot presence/power state, MSI EOI helpers, and PowerNV hotplug slot state.

Important APIs/types/functions: `PCI_SLOT_ID_PREFIX`, `PCI_SLOT_ID`, and `PCI_PHB_SLOT_ID` encode OPAL slot identifiers. Declarations include `pnv_pci_get_slot_id`, `pnv_pci_get_device_tree`, presence and power state getters, `pnv_pci_set_power_state`, `pnv_opal_pci_msi_eoi`, and `is_pnv_opal_msi`. `struct pnv_php_slot` wraps `struct hotplug_slot` and records OPAL ID, name, flags such as `PNV_PHP_FLAG_BROKEN_PDC`, kref, slot state, IRQ, workqueue, device nodes, PCI objects, attention/power state, FDT/change-set state, parent/children, and list links.

Control flow: PowerNV PCI code identifies slots from device-tree nodes, queries OPAL for presence and power, retrieves slot device-tree fragments, applies OF changesets for hotplug, and powers slots through OPAL with asynchronous messages. MSI handling checks whether an IRQ chip is PowerNV OPAL MSI and sends EOI through OPAL.

State and persistence: Hotplug slot structures persist across registration, population, offline, and removal states. They own krefs, OF changeset state, dynamic FDT buffers, child lists, and links into broader hotplug management. Power state and attention state mirror platform state.

Dependencies and integration points: It depends on Linux PCI, PCI hotplug, IRQ, Open Firmware, and `asm/opal-api.h`. It integrates PHB/slot management with OPAL firmware, dynamic device tree updates, workqueues, PCI device/bus objects, and the IRQ/MSI subsystem.

Risks and test signals: OPAL slot IDs must be encoded consistently or power operations can target the wrong PHB/device. Dynamic OF changesets and FDT buffers need correct lifetime handling. Hotplug transitions must be serialized across workqueue, IRQ, and kref paths. Tests should cover physical slot presence/power operations, hotplug add/remove, broken PDC handling, MSI EOI behavior, and error paths from OPAL calls.
