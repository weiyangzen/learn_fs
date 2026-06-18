<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crash_dump.h -->
# sources/distributed-fs/ceph-client/include/linux/crash_dump.h

## Purpose

`crash_dump.h` declares second-kernel vmcore access, ELF core header state, old-memory copying, vmcore callbacks, device dump registration, and helpers that identify whether the running kernel is a kdump kernel. The source was read as a complete 192-line file.

## Important APIs, Types, and Functions

Global addresses include `elfcorehdr_addr`, `elfcorehdr_size`, and `dm_crypt_keys_addr`, with sentinel values `ELFCORE_ADDR_MAX` and `ELFCORE_ADDR_ERR`. Crash-dump APIs include `elfcorehdr_alloc()`, `elfcorehdr_free()`, `elfcorehdr_read()`, `elfcorehdr_read_notes()`, `elfcorehdr_fill_device_ram_ptload_elf64()`, `remap_oldmem_pfn_range()`, `copy_oldmem_page()`, `copy_oldmem_page_encrypted()`, `vmcore_cleanup()`, architecture ELF checks, `is_kdump_kernel()`, `is_vmcore_usable()`, and `vmcore_unusable()`. `struct vmcore_cb` lets drivers validate PFNs or contribute device RAM ranges. `struct vmcore_range` plus `vmcore_alloc_add_range()` and `vmcore_free_ranges()` manage ranges. `struct vmcoredd_data` supports device-specific dumps via `vmcore_add_device_dump()`. `read_from_oldmem()` backs proc vmcore reads.

## Control Flow

The kdump kernel receives an ELF core header address, validates usability, exposes `/proc/vmcore`, and maps/copies pages from old memory on read. Registered callbacks can reject non-RAM PFNs or add device-managed RAM ranges. Device dump callbacks append driver-specific data to the vmcore.

## State and Persistence Behavior

The key persistent state for the kdump kernel is the ELF core header address/size and optional dm-crypt key address. Vmcore callbacks and range lists are runtime state. `vmcore_unusable()` preserves the fact this is a kdump kernel while preventing vmcore use.

## Dependencies and Integration Points

It depends on kexec, procfs, ELF, page tables, and UAPI vmcore definitions. It integrates with `/proc/vmcore`, memory hotplug/device memory drivers, encrypted memory reads, vmcore device dumps, architecture ELF checks, and old-memory remapping.

## Risks and Edge Cases

Sentinel address handling is critical because `-1ULL` and `-2ULL` have different meanings. Old memory reads must avoid non-RAM or ballooned/device memory pages unless callbacks allow them. Device dump callbacks must provide bounded data. Encrypted reads must choose the correct old-memory copy helper.

## Test Signals

Signals include kdump vmcore read tests, invalid elfcore header sentinel tests, vmcore callback register/unregister coverage, device dump collection tests, encrypted old-memory read tests, vmcore range allocation/free leak tests, and `CONFIG_PROC_VMCORE` disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crash_dump.h -->
