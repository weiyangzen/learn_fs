<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/efi.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/efi.c

Purpose: initializes LoongArch EFI runtime/table support and primary display information.
Important APIs and types: implements `efi_fdt_pointer`, `efi_runtime_init`, `efi_poweroff_required`, `efi_init`, `init_primary_display`, and exports `sysfb_primary_display`; tracks EFI config table addresses including boot memmap, FDT, and display table.
Control flow: early EFI init maps the system table, discovers config tables, initializes runtime services if available, parses primary display/sysfb information, and records FDT pointer for later boot flow.
State and persistence: stores EFI table addresses, runtime availability, and framebuffer/display metadata for sysfb/simpledrm.
Dependencies and integration: depends on EFI core, early ioremap, memblock, ACPI/BGRT/sysfb, Loongson platform data, reboot/poweroff, and uaccess for table copying.
Risks and test signals: bad table mapping or display parsing can break boot services handoff or framebuffer. Signals include EFI boot, runtime service calls, sysfb/simpledrm display, BGRT, and kexec EFI paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/efi.c -->
