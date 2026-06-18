# sources/distributed-fs/ceph-client/drivers/firmware/efi/arm-runtime.c

Purpose: enables EFI runtime services on ARM and ARM64 after early memory setup by remapping EFI runtime regions into a dedicated `efi_mm` page table and installing native runtime service pointers.

Important APIs/types/functions: core functions are `efi_virtmap_init()`, `arm_enable_runtime_services()`, `efi_virtmap_load()`, `efi_virtmap_unload()`, and `arm_dmi_init()`. Optional ptdump support registers `efi_page_tables`.

Control flow: `early_initcall(arm_enable_runtime_services)` checks EFI boot status, unmaps the early memory map, remaps it late, installs soft-reserved resource entries for EFI specific-purpose memory, honors `efi=noruntime`/runtime-disabled state, and skips setup if paravirtual runtime services are already active. Otherwise it builds page-table mappings for every `EFI_MEMORY_RUNTIME` descriptor with valid virtual addresses, applies EFI memory-attribute permissions, calls `efi_native_runtime_setup()`, and sets `EFI_RUNTIME_SERVICES`. `efi_virtmap_load/unload()` switch page tables around runtime calls with preemption disabled.

State and persistence behavior: `efi_mm` page tables persist for runtime calls. Soft-reserved resources are inserted in `iomem_resource`. Runtime availability is reflected in `efi.flags`.

Dependencies and integration points: depends on EFI memory map infrastructure, architecture page-table helpers, `efi_memattr_apply_permissions()`, native runtime wrappers, memblock/iomem resources, and DMI setup for ARM platforms.

Risks and test signals: missing runtime virtual addresses, failed mappings, or invalid memory attributes disable runtime services. Page-table switching must be balanced and non-preemptible. Test signals include EFI runtime variables/time access on ARM/ARM64, `efi_page_tables` debugfs output when enabled, and DMI availability before DMI ID init.
