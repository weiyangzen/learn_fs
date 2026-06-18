<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug_pci.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug_pci.c

## Purpose
Provides the PCI configuration-space operations used by the CompactPCI hotplug core. It reads and writes the CompactPCI Hot Swap capability, controls attention LEDs, detects insertion/extraction bits, and configures or removes PCI devices for a CPCI slot.

## Important APIs, Types, and Functions
Exports `cpci_get_attention_status()`, `cpci_set_attention_status()`, `cpci_get_hs_csr()`, `cpci_check_and_clear_ins()`, `cpci_check_ext()`, `cpci_clear_ext()`, `cpci_led_on()`, `cpci_led_off()`, `cpci_configure_slot()`, and `cpci_unconfigure_slot()`.

## Control Flow
HS CSR helpers find `PCI_CAP_ID_CHSWP` on the slot devfn and read/write the capability status/control word. Insert and extract bits are write-one-to-clear where appropriate. Configure locks PCI rescan/removal, finds or scans the slot device, adds bridge children through `pci_hp_add_bridge()`, assigns unassigned bridge resources, and adds devices. Unconfigure locks rescan/removal, removes all functions in the slot, drops the cached slot device reference, and clears `slot->dev`.

## State and Persistence
Persistent runtime state is mostly in the caller's `struct slot`: cached `pci_dev`, adapter/latch status managed by the core, and bus/devfn. Hardware state is the HS CSR in PCI config space.

## Dependencies and Integration Points
Depends on PCI config-space access, PCI hotplug bridge helpers, resource assignment, and global PCI rescan/remove locking. It is called by `cpci_hotplug_core.c` on ENUM events and sysfs disable.

## Risks and Edge Cases
Most HS CSR helpers return success-like zero when the capability is missing or config reads fail, so callers can miss hardware failures. `cpci_configure_slot()` scans all functions only when the cached device is absent. Resource assignment operates at the parent bridge and may affect more than the slot. Cached `pci_dev` refs must be released exactly once on unconfigure/release.

## Test Signals
Test cards with and without Hot Swap capability, INS/EXT bit clear behavior, LED on/off, bridge insertion, resource assignment failures, multifunction slots, unconfigure after surprise removal, and repeated configure/unconfigure cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug_pci.c -->
