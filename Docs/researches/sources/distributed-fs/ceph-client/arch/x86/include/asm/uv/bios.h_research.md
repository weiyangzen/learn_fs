# sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/bios.h

Purpose: SGI/HPE UV BIOS runtime interface definitions, UV system table format, GAM/architecture metadata, firmware command IDs, status codes, and exported BIOS wrapper prototypes.

Important APIs/types/functions: `enum uv_bios_cmd`, `UV_BIOS_EXTRA*` commands, BIOS status constants, `struct uv_gam_parameters`, `struct uv_gam_range_entry`, `struct uv_arch_type_entry`, `struct uv_systab`, `uv_systab`, `struct uv_bios_hub_info`, `struct uv_bios_port_info`, `union partition_info_u`, `enum uv_memprotect`, UV BIOS call wrappers, `uv_bios_init()`, `get_uv_systab_phys()`, UV identity globals, `uv_get_archtype()`, `uv_get_hubless_system()`, `sgi_uv_kobj`, and `__efi_uv_runtime_lock`.

Control flow: UV initialization locates `uv_systab`, validates signature/revision, uses the EFI runtime function pointer for commands, and exposes typed wrappers for serial/partition info, frequency base, watchlists, memory protection, heap/object enumeration, geoinfo, PCI topology, and VGA target operations.

State/persistence: persistent firmware-derived state includes the UV system table pointer, architecture type, partition/coherency/region identifiers, serial number, RTC cycles, UV type, sysfs kobject, and EFI runtime lock.

Dependencies/integration: depends on EFI and RTC headers. Integrated with UV platform bring-up, MMR/GAM setup, sysfs firmware exposure, PCI topology, NMI/watchlist support, and protected memory operations.

Risks/test signals: EFI runtime calling conventions, table revision parsing, and buffer copy-in/out sizes are sensitive. Test UV boot on supported generations, missing/invalid systab handling, each BIOS wrapper return status, sysfs firmware nodes, PCI topology discovery, geoinfo parsing, and EFI runtime lock coverage.
