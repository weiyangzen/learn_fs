# sources/distributed-fs/ceph-client/drivers/acpi/ioapic.c

Purpose: `ioapic.c` manages ACPI-described IOAPIC/IOxAPIC/IOSAPIC devices added through PCI root hotplug after boot. Boot IOAPICs are registered from MADT elsewhere; this file discovers additional ACPI devices, reserves resources, registers IOAPICs, and removes them on root teardown.

Important APIs, types, and functions: `struct acpi_pci_ioapic` records the root handle, device handle, GSI base, resource, optional PCI device, and list entry. Public functions are `acpi_ioapic_add()`, `pci_ioapic_remove()`, and `acpi_ioapic_remove()`. Internal helpers include `setup_res()`, `acpi_is_ioapic()`, and `handle_ioapic_add()`.

Control flow: `acpi_ioapic_add()` walks ACPI devices under a root. Each candidate must have `_GSB` and HID `ACPI0009` or `ACPI000A`. The add handler skips already-tracked handles, evaluates `_GSB`, allocates state, skips hardware already registered, optionally enables and claims PCI BAR0, walks `_CRS` for a memory resource, inserts it into `iomem_resource`, selects PCI resource or `_CRS`, and calls `acpi_register_ioapic()`. Removal first releases PCI resources in `pci_ioapic_remove()`, then `acpi_ioapic_remove()` unregisters IOAPICs, releases inserted resources, removes list entries, and frees state.

State and persistence: tracked hotplug IOAPICs live in the global `ioapic_list` protected by `ioapic_list_lock`. The driver also owns inserted iomem resources and PCI device references for tracked entries.

Dependencies and integration: integrates ACPI namespace/resource evaluation, PCI device acquisition and resource management, global iomem resource insertion, and architecture ACPI IOAPIC registration callbacks.

Risks: error unwinding spans PCI enable/request, `_CRS` insertion, and IOAPIC registration. Duplicate detection is by ACPI handle and `acpi_ioapic_registered()`; mismatched firmware handles or GSI bases can cause skipped or duplicated registration. Remove ordering matters because IRQ users can keep IOAPICs busy, causing `-EBUSY`.

Test signals: test hot-add under PCI root, duplicate add, PCI BAR and pure `_CRS` resources, prefetch/disabled resource filtering, registration failure unwind, root removal with busy IOAPIC, and resource release after PCI disable.
