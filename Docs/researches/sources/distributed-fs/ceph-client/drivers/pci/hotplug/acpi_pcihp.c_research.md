<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpi_pcihp.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpi_pcihp.c

## Purpose
Provides common ACPI helper functions for PCI hotplug drivers. It arbitrates OS control of SHPC hotplug through ACPI `_OSC`/`OSHP`, and detects whether ACPI namespace objects represent ejectable PCI slots.

## Important APIs, Types, and Functions
Exports `acpi_get_hp_hw_control_from_firmware()`, `acpi_pci_check_ejectable()`, and `acpi_pci_detect_ejectable()`. Internal helpers are `acpi_run_oshp()`, `pcihp_is_ejectable()`, and the namespace walk callback `check_hotplug()`.

## Control Flow
For firmware control, the helper locates the ACPI PCI root for the host bridge. If `_OSC` was used, it trusts `native_shpc_hotplug`; otherwise it searches from the hotplug controller or parent bridge handles upward and evaluates `OSHP` until success or the root bridge is reached. For ejectability, it checks for `_ADR` plus `_EJ0` or a true `_RMV`, and ensures the object's parent matches the PCI bus bridge handle.

## State and Persistence
Only module parameter `debug_acpi` persists while loaded. All other behavior is query-based against firmware state.

## Dependencies and Integration Points
Depends on ACPI core, PCI ACPI root lookup, host bridge lookup, PCI hotplug, and namespace walking. It is compiled into `pci_hotplug` when ACPI is enabled and is used by ACPI hotplug and SHPC/native arbitration paths.

## Risks and Edge Cases
The OSHP search up the ACPI hierarchy is explicitly called suspect relative to the PCI Firmware Specification. Firmware may omit `_OSC`, `OSHP`, `_EJ0`, or `_RMV`, making detection heuristic. `acpi_get_name()` allocated buffers must be freed on all paths, which this file does.

## Test Signals
Test systems with `_OSC` granting and denying SHPC control, systems requiring `OSHP`, ejectable slots with `_EJ0`, removable slots with `_RMV`, non-ejectable PCI devices, and ACPI-disabled platforms where root lookup returns no ACPI root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpi_pcihp.c -->
