# sources/distributed-fs/ceph-client/include/linux/efi.h

Purpose: central in-kernel UEFI contract header. It defines EFI status values, GUID construction, table descriptors, memory descriptor types and attributes, runtime service function pointer ABI, system/config table layouts, capsule update structures, efivar operations, EFI device path records, secure boot helpers, TPM/random-seed/memreserve table records, and global EFI state exposed through `extern struct efi`.

Important APIs/types/functions: `efi_guid_t`, `efi_memory_desc_t`, `efi_runtime_services_t`, `efi_system_table_t`, `efi_config_table_t`, `efi_memory_map`, `efivar_operations`, `efivars`, `efi_get_secureboot_mode()`, `efi_enabled()`, `efi_rt_services_supported()`, `efi_call_virt_pointer()`, `for_each_efi_memory_desc*`, `efi_memdesc_ptr()`, efivar get/set/query helpers, capsule helpers, memreserve and MOK variable table helpers.

Control flow: architecture boot code populates `efi`, parses config tables via `efi_config_parse_tables()`, installs the memory map, optionally enters virtual mode, and routes later runtime service calls through locked/arch-wrapped helpers. Efivar users call wrapper APIs rather than firmware pointers directly. Capsule and secure boot helpers layer policy around variable/runtime operations.

State/persistence: persistent state lives in firmware variables, capsule payload/reset state, EFI memory maps, config table addresses, reserved memory tables, and secure boot/MOK data. Kernel state is mostly global and boot initialized (`efi.flags`, `efi.memmap`, table pointers, runtime_supported_mask).

Dependencies/integration: depends on architecture `asm/efi`-style call setup, `mm_struct`, kobjects/sysfs, pstore, reboot, uuid/guid, memblock/page/PFN helpers, EFI capsule loader, TPM log, Xen EFI handling, and firmware-specific runtime ABI details.

Risks/test signals: high risk around mixed 32/64-bit pointer layouts, GUID alignment, descriptor-size iteration, firmware return status mapping, runtime lock/IRQ/flag discipline, nonblocking variable store writes, and secure boot variable interpretation. Test with EFI boot/memmap parsing, efivarfs read/write/query, capsule update paths, secure boot modes, kexec/reboot, Xen EFI config tables, and malformed descriptor/table fixtures.
