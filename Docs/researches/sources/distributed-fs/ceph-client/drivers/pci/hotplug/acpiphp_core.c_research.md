<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_core.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_core.c

## Purpose
Implements the generic hotplug-slot interface for ACPI PCI hotplug. It registers slots with the PCI hotplug core, exposes enable/disable/status/attention operations, and provides a global registration point for platform-specific attention LED handlers.

## Important APIs, Types, and Functions
Exports `acpiphp_register_attention()`, `acpiphp_unregister_attention()`, `acpiphp_register_hotplug_slot()`, and `acpiphp_unregister_hotplug_slot()`. Static hotplug ops include `enable_slot()`, `disable_slot()`, `set_attention_status()`, `get_power_status()`, `get_attention_status()`, `get_latch_status()`, and `get_adapter_status()`. `acpiphp_init()` logs module status and honors `acpiphp_disabled`.

## Control Flow
Slot registration allocates `struct slot`, assigns `acpi_hotplug_slot_ops`, links it to the `acpiphp_slot`, names it by `_SUN`, and calls `pci_hp_register()`. Hotplug-core enable/disable callbacks delegate to glue functions `acpiphp_enable_slot()` and `acpiphp_disable_slot()`. Status callbacks translate ACPI glue state into generic hotplug values. Attention callbacks call the registered provider under a module reference.

## State and Persistence
Global state consists of `acpiphp_disabled` and one `attention_info` pointer. Per-slot state is allocated for each registered hotplug slot and freed on unregister. The generic hotplug core exposes these slots through sysfs.

## Dependencies and Integration Points
Depends on PCI hotplug core, ACPI PCI glue functions, module reference counting, and optional platform extensions such as Ampere/IBM attention providers.

## Risks and Edge Cases
Only one attention provider can be registered. If `try_module_get()` fails, the provider pointer is cleared. Slot registration may fail with `-EBUSY` when a native driver already registered the slot; glue can still track the slot internally without sysfs exposure. Power/latch/adapter status are derived from ACPI glue state and may be heuristic when firmware `_STA` is unreliable.

## Test Signals
Register/unregister slots, enable/disable via sysfs, read power/latch/adapter status, test attention callback provider install/removal, verify `disable=1` prevents glue enumeration, and test slot-name collisions returning `-EBUSY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_core.c -->
