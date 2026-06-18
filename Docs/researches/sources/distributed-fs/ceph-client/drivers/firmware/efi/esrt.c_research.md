# sources/distributed-fs/ceph-client/drivers/firmware/efi/esrt.c

Purpose: validates and reserves the EFI System Resource Table during early boot, then exposes firmware-update resource entries under `/sys/firmware/efi/esrt`.

Important APIs/types/functions: defines ESRT wire structs `efi_system_resource_table` and `efi_system_resource_entry_v1`, runtime `struct esre_entry`, top-level and per-entry sysfs attributes, `efi_esrt_init()`, `esrt_sysfs_init()`, `register_entries()`, and `esre_create_sysfs_entry()`.

Control flow: `efi_esrt_init()` requires EFI memory/config-table support, verifies the ESRT address is in an acceptable EFI memory descriptor, checks header fit, version 1, entry size capacity, a conservative count limit of 128, and full table fit in one memory-map entry. It records physical address/size and reserves boot-services data with `efi_mem_reserve()`. `device_initcall(esrt_sysfs_init)` maps the reserved table, creates the `esrt` kobject and `entries` kset, publishes top-level count/version attributes, and creates `entryN` kobjects for each resource.

State and persistence behavior: early physical address/size survive until sysfs init; the table is memremapped for sysfs reads. Per-entry kobjects remain until shutdown.

Dependencies and integration points: depends on EFI config table parsing, EFI memory descriptor lookup, memblock reservation, sysfs/kobject APIs, and userspace firmware update tools such as fwupd.

Risks and test signals: ESRT is firmware-provided and must fit in a single descriptor; bad counts or unsupported versions are rejected. Test signals include `/sys/firmware/efi/esrt/fw_resource_count`, `entries/entry*/fw_class`, correct reservation logs, and graceful `-ENOSYS` when no ESRT exists.
