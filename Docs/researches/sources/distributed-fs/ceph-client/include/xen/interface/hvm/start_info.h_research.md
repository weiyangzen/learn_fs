# sources/distributed-fs/ceph-client/include/xen/interface/hvm/start_info.h

Purpose: defines the x86 HVM/PVH start-of-day memory layout passed to guests, including modules, command line, ACPI RSDP, and optional memory map.

Important APIs/types/functions: `XEN_HVM_START_MAGIC_VALUE`, `XEN_HVM_MEMMAP_TYPE_*`, `struct hvm_start_info`, `struct hvm_modlist_entry`, and `struct hvm_memmap_table_entry`.

Control flow: the domain builder places the start info structure in guest physical memory and passes its address in the boot register convention. The guest validates `magic`, checks `version`, reads modules and command line if their physical addresses are nonzero, and for version 1+ reads memory map entries when `memmap_entries` is nonzero.

State and persistence: start info is immutable boot data. Address fields with value zero mean absent. Xen on x86 attempts to place data below 4 GiB.

Dependencies and integration points: used by PVH/HVM guest entry code, boot loaders, ACPI discovery, initrd/module loading, and memory-map initialization. It ties to `XENFEAT_linux_rsdp_unrestricted` for Linux RSDP placement behavior.

Risks: layout is defined by the ASCII diagram and represented by C structs; padding changes would break boot. Version 0 guests must not read version 1 fields. All addresses and sizes are 64-bit little-endian values.

Test signals: PVH/HVM boot tests with no modules, multiple modules, absent/present RSDP, version 0 and 1 structures, and memory maps containing RAM, reserved, ACPI, NVS, unusable, disabled, and PMEM entries.
