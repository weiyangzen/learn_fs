# sources/distributed-fs/ceph-client/include/linux/dmar.h

## Purpose
This header declares Intel DMAR/VT-d table, device-scope, interrupt-remapping, and MSI fault-handling interfaces. It models ACPI DMAR hardware units, their PCI scopes, hotplug notifications, and interrupt remapping table entries.

## Important APIs, types, and functions
Important types are `struct dmar_dev_scope`, `struct dmar_drhd_unit`, `struct dmar_pci_path`, `struct dmar_pci_notify_info`, and `struct irte`. Global state includes `dmar_tbl`, `dmar_global_lock`, and `dmar_drhd_units` when DMAR table support is enabled. Iteration helpers include `for_each_drhd_unit`, `for_each_active_drhd_unit`, `for_each_iommu`, `for_each_active_iommu`, `for_each_dev_scope`, and `for_each_active_dev_scope`.

The API declares table and scope lifecycle functions (`dmar_table_init()`, `dmar_dev_scope_init()`, `dmar_alloc_dev_scope()`, `dmar_free_dev_scope()`, `dmar_insert_dev_scope()`, `dmar_remove_dev_scope()`), device notification hooks (`dmar_device_add()`, `dmar_device_remove()`, `dmar_register_bus_notifier()`), IOMMU detection/init hooks, DMAR parser callbacks for RMRR/ATSR/SATC, hotplug hooks, IRQ remapping hotplug, platform opt-in checks, and DMAR MSI/fault functions such as `dmar_set_interrupt()`, `dmar_fault()`, `dmar_alloc_hwirq()`, and `dmar_free_hwirq()`.

## Control flow, state, and persistence
DMAR state is persistent global kernel state sourced from ACPI tables and maintained in RCU-protected lists. `dmar_rcu_check()` allows safe list dereference when the global rwsem is held or during boot. Device scopes carry RCU pointers to devices plus bus/devfn identifiers. `struct irte` is a packed hardware-format entry with shared, remapped, and posted interrupt views; `dmar_copy_shared_irte()` copies only fields common to both modes.

## Dependencies and integration points
It integrates with ACPI DMAR parsing, Intel IOMMU, PCI hotplug, IRQ remapping, MSI message programming, RCU lists, rwsems, and boot-time system state. If `CONFIG_DMAR_TABLE`, `CONFIG_INTEL_IOMMU`, or `CONFIG_IRQ_REMAP` are disabled, many APIs compile to no-op or `-ENODEV` stubs.

## Risks and test signals
Risks include unsafe iteration without the DMAR lock/RCU guarantees, incorrect interrupt remapping bit layout, stale RCU device scopes on hotplug, and configuration stubs masking missing functionality. Tests should cover ACPI table parse failures, device scope add/remove, hotplug insertion/removal, platform opt-in flags, interrupt remapping in remapped and posted modes, and disabled-config stub behavior.
