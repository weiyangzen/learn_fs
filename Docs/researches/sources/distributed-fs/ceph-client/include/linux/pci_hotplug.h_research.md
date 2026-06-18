<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci_hotplug.h -->
# sources/distributed-fs/ceph-client/include/linux/pci_hotplug.h

## Purpose
`include/linux/pci_hotplug.h` defines the public interface between PCI hotplug controller drivers and the PCI hotplug core. It describes the callback table a hotplug controller provides for slot operations, the `struct hotplug_slot` object registered with the core, registration/initialization/add/delete/destroy/deregister helpers, and ACPI/native-ownership helpers used by PCIe hotplug and SHPC paths.

## Important APIs, Types, and Functions
`struct hotplug_slot_ops` is the central contract. Its callbacks cover user or core requests to enable or disable a slot, set the attention LED, run hardware tests, query power/attention/latch/adapter status, and optionally reset a slot. The `reset_slot()` callback receives a `bool probe` argument so code can ask whether reset is supported before doing it.

`struct hotplug_slot` carries the callback table plus core-owned linkage to `struct pci_slot`, module owner, and module name. `hotplug_slot_name()` resolves the underlying `pci_slot` kobject name through `pci_slot_name()`.

Registration APIs are `__pci_hp_register()`, `__pci_hp_initialize()`, `pci_hp_add()`, `pci_hp_del()`, `pci_hp_destroy()`, and `pci_hp_deregister()`. Public macros `pci_hp_register()` and `pci_hp_initialize()` inject `THIS_MODULE` and `KBUILD_MODNAME`, avoiding extra include chaining for callers.

ACPI/native helpers include `pciehp_is_native()`, `acpi_get_hp_hw_control_from_firmware()`, `shpchp_is_native()`, `acpi_pci_check_ejectable()`, `acpi_pci_detect_ejectable()`, and `hotplug_is_native()`. Without ACPI, inline stubs treat PCIe hotplug and SHPC as native and firmware-control requests as successful.

## Control Flow
A hotplug controller allocates/fills `struct hotplug_slot`, supplies `hotplug_slot_ops`, then initializes/registers it against a parent PCI bus and slot number. The PCI hotplug core calls the ops in response to sysfs requests, controller events, or slot-management flows. Removal paths delete and destroy the slot object, then deregister the hotplug slot so the core stops exposing and invoking it.

`hotplug_is_native()` combines cached bridge state (`bridge->is_pciehp`) with ACPI ownership queries. It returns true when a PCIe hotplug bridge is OS-native or when SHPC ownership is native.

## State and Persistence Behavior
The header stores no state itself, but it defines ownership boundaries. The hotplug driver owns the callback implementation and lifetime of the `hotplug_slot` object until registration hands core-owned fields to the hotplug core. The core owns `pci_slot`, module metadata, and user-visible slot name. Persistent user-visible behavior is surfaced through slot sysfs attributes backed by these callbacks.

## Dependencies and Integration Points
This header depends on `struct pci_bus`, `struct pci_slot`, `struct pci_dev`, `struct module`, and `u8`/`u32` kernel types provided through surrounding PCI includes. With `CONFIG_ACPI`, it includes `linux/acpi.h` and integrates with ACPI slot ejectability and firmware ownership negotiation. Runtime users include PCIe hotplug (`pciehp`), SHPC hotplug, ACPI hotplug glue, and generic PCI slot reset code.

## Risks
Callback return semantics and slot lifetime are the main risks. A driver must not free a hotplug slot while sysfs or the hotplug core can still call its ops. `reset_slot()` must distinguish probe mode from actual reset to avoid disruptive bus resets during capability checks. Native ownership must be respected; controlling firmware-owned hotplug hardware can race platform firmware and produce duplicate or missing hotplug events. Status callbacks must tolerate hardware removal and transient presence/latch states.

## Test Signals
Test with `CONFIG_HOTPLUG_PCI`, `CONFIG_HOTPLUG_PCI_PCIE`, SHPC, and ACPI combinations. Exercise slot registration and deregistration, sysfs enable/disable/status paths, LED and latch status callbacks, reset probe versus reset execution, ACPI firmware-owned versus OS-native bridges, surprise removal, repeated add/remove cycles, and module unload while slots are registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci_hotplug.h -->
