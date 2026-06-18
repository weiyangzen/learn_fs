<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_glue.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_glue.c

## Purpose
Implements the ACPI-to-PCI glue for ACPI PCI hotplug. It discovers ACPI hotplug slots under PCI bridges, installs ACPI notification contexts, registers user-visible hotplug slots when appropriate, rescans/removes PCI devices on ACPI events, and manages bridge/slot lifetimes.

## Important APIs, Types, and Functions
Important exported or externally used functions are `acpiphp_enumerate_slots()`, `acpiphp_remove_slots()`, `acpiphp_check_host_bridge()`, `acpiphp_enable_slot()`, `acpiphp_disable_slot()`, and status helpers. Internal core functions include context reference helpers, `free_bridge()`, `acpiphp_add_context()`, `cleanup_bridge()`, `enable_slot()`, `disable_slot()`, `get_slot_status()`, `trim_stale_devices()`, `acpiphp_check_bridge()`, `hotplug_event()`, and `acpiphp_hotplug_notify()`.

## Control Flow
Enumeration starts from a PCI bus ACPI companion, allocates an `acpiphp_bridge`, pins the PCI bus/device, installs a root or bridge hotplug context, adds the bridge to `bridge_list`, and walks one ACPI level to add contexts for function objects with `_ADR`. Each function is grouped into a physical slot by device number; ejectable or dock slots not owned by native hotplug are registered with the hotplug core.

ACPI notifications grab context and bridge refs, take `pci_lock_rescan_remove()`, and handle bus check, device check, or eject request. Bridge checks iterate slots: if the slot is present, stale devices are trimmed and the slot is enabled; otherwise it is disabled. Enabling rescans the slot, scans bridges in two passes, assigns resources, sanitizes devices lacking resources, configures PCIe settings, connects ACPI config-space regions, and adds devices. Disabling removes all PCI functions for the slot and trims ACPI devices, then eject executes `_EJ0` when present.

## State and Persistence
State is kept in `bridge_list`, each bridge's kref/refcounted contexts, slots, function lists, slot flags, and ACPI device hotplug contexts. References pin PCI buses and bridge devices across notifications and module unload. No disk persistence exists.

## Dependencies and Integration Points
Depends on ACPI scan/hotplug context locks, PCI core scanning/removal/resource assignment, runtime PM for bridges, dock support, native hotplug detection, and `acpiphp_core.c` slot registration.

## Risks and Edge Cases
Lifetime is complex: ACPI notifications may race with bridge removal, so `is_going_away`, context locks, krefs, and PCI rescan locks are critical. Native hotplug bridges are mostly left to native drivers, but ACPI still scans non-hotplug bridges below them. Firmware `_STA` can be absent or misleading, so fallback vendor-ID reads are used. Resource assignment failures remove devices during sanitize. Eject is synchronized with `acpi_scan_lock` to avoid ACPI scan races.

## Test Signals
Boot enumeration on root and downstream bridges, ACPI bus/device/eject notifications, dock/undock, native-hotplug coexistence, stale device removal, resource exhaustion leading to sanitize removal, bridge removal during notification, and status reads after `_STA` changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_glue.c -->
