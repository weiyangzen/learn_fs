# sources/distributed-fs/ceph-client/drivers/acpi/acpi_memhotplug.c

## Purpose
`acpi_memhotplug.c` registers the ACPI memory-device scan handler for `PNP0C80` and, when hotplug is enabled, turns firmware memory resource notifications into Linux memory hot-add/remove operations.

## Important APIs, Types, And Functions
Key types are `struct acpi_memory_info` for merged memory ranges and `struct acpi_memory_device` for per-device state. Important functions are `acpi_memory_get_resource()`, `acpi_memory_free_device_resources()`, `acpi_memory_get_device_resources()`, `acpi_memory_check_device()`, `acpi_bind_memory_blocks()`, `acpi_unbind_memory_blocks()`, `acpi_memory_enable_device()`, `acpi_memory_remove_memory()`, `acpi_memory_device_free()`, `acpi_memory_device_add()`, `acpi_memory_device_remove()`, `acpi_memory_hotplug_init()`, and the `acpi_no_memhotplug` setup handler.

## Control Flow
Initialization registers an ACPI scan handler, with hotplug enabled unless the boot parameter `acpi_no_memhotplug` was set. Attach allocates per-device state, walks `_CRS` resources, converts memory address resources to `acpi_memory_info` entries, merges adjacent compatible ranges, checks `_STA`, registers a static memory group, and calls `__add_memory()` for each nonempty range with `MHP_NID_IS_MGID` and `MHP_MEMMAP_ON_MEMORY`. Successfully added or preexisting memory blocks are bound to the ACPI device. Detach unbinds enabled memory blocks, calls `__remove_memory()`, frees range entries, unregisters the memory group, and clears driver data.

## State And Persistence
Per-device memory range lists, enabled flags, and memory group IDs persist while the ACPI memory device is bound. The durable system effect is added or removed system memory and ACPI companion binding on `memory_block` devices.

## Dependencies And Integration Points
It depends on ACPI scan/hotplug infrastructure, `_CRS`, `_STA`, memory hotplug APIs, memory groups, NUMA node lookup, memory block walking, and ACPI device binding helpers in `internal.h`.

## Risks
There is no rollback for earlier successful `__add_memory()` calls if later ranges fail, as noted in comments. `memory_group_unregister()` can fail when some memory remains, but the free path does not surface that strongly. Firmware range correctness is critical. The no-hotplug boot mode still registers the handler but suppresses attach, which affects enumeration expectations.

## Test Signals
Tests should cover absent/disabled `_STA`, empty resources, adjacent resource merging, multiple ranges in one device, `-EEXIST` from preexisting memory, binding failures, hot-remove, `acpi_no_memhotplug`, NUMA node selection, and memory group cleanup.
