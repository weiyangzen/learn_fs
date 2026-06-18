# sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpadlpar_sysfs.c

## Purpose
Exposes pSeries RPA DLPAR control through sysfs files under the PCI slots kset, allowing userspace to request slot add or remove by DRC name.

## Important APIs, Types, and Functions
Public functions are `dlpar_sysfs_init()` and `dlpar_sysfs_exit()`. Store handlers are `add_slot_store()` and `remove_slot_store()`, with simple show handlers returning `0`. The file defines `add_slot` and `remove_slot` `kobj_attribute`s in `dlpar_attr_group`.

## Control Flow
Initialization creates a `control` kobject under `pci_slots_kset` and adds the attribute group. A write to `add_slot` or `remove_slot` copies the DRC name into a fixed buffer, strips one trailing newline, and calls `dlpar_add_slot()` or `dlpar_remove_slot()`. Exit removes the group and drops the kobject.

## State and Persistence Behavior
The only local persistent state is `dlpar_kobj`. User writes trigger live topology mutations in `rpadlpar_core.c`; the sysfs file contents themselves are not persistent and reads always return `0`.

## Dependencies and Integration Points
Depends on kobject/sysfs APIs, `pci_slots_kset`, `MAX_DRC_NAME_LEN`, and the core DLPAR add/remove functions. It is the user-facing entry point for the `rpadlpar_io` module.

## Risks
Inputs with length `>= MAX_DRC_NAME_LEN` return `0` rather than an errno, which can look like a short no-op success to userspace. The handler accepts arbitrary strings and relies on core DRC lookup for validation. `dlpar_sysfs_exit()` assumes initialization succeeded and `dlpar_kobj` is valid.

## Test Signals
Validate sysfs group creation/removal, newline stripping, overlong input behavior, successful and failed add/remove writes, module unload after failed init paths, and DRC names containing spaces or unusual characters accepted by firmware.
