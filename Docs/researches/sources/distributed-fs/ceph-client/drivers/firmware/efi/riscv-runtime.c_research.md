
# sources/distributed-fs/ceph-client/drivers/firmware/efi/riscv-runtime.c

Purpose: enables RISC-V EFI runtime services by remapping the EFI memory map, creating runtime page-table mappings, applying EFI memory attributes, wiring runtime service wrappers, and switching address spaces around EFI calls.

Important APIs/types/functions: internal `efi_virtmap_init()` and `riscv_enable_runtime_services()` perform setup. Exports `arch_efi_call_virt_setup()` and `arch_efi_call_virt_teardown()` for runtime wrappers. `riscv_dmi_init()` initializes DMI early.

Control flow: early init verifies EFI boot, unmaps the early memory map, remaps it late, registers soft-reserved EFI memory resources, exits if runtime services are disabled or paravirtualized, allocates and initializes `efi_mm`, maps all runtime descriptors unless any has `virt_addr == U64_MAX`, applies memattr permissions, calls `efi_native_runtime_setup()`, and sets `EFI_RUNTIME_SERVICES`. Runtime call setup syncs kernel mappings, disables preemption, switches to `efi_mm`; teardown switches back and enables preemption.

State and persistence behavior: `efi_mm` persists as the EFI runtime address space. Soft-reserved resources are inserted into `iomem_resource`. EFI flags record runtime availability.

Dependencies and integration points: depends on EFI memmap/memattr code, RISC-V page-table mapping helpers, scheduler MM switching, resource tree, DMI setup, and generic runtime wrappers.

Risks and test signals: missing virtual addresses disable runtime services, mapping failures leave services unavailable, and address-space switching must restore preemption/MM state reliably. Test signals include RISC-V EFI boot, runtime variable reads/writes, soft-reserve resources, memattr permission application, runtime-disabled command line, paravirt runtime mode, and DMI data availability.
