<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/efi-header.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/efi-header.S

Purpose: defines the PE/COFF EFI header emitted for EFI-stub bootable LoongArch kernels.
Important APIs and types: assembly macros lay out DOS, PE, optional header, section table, machine type, image base, subsystem, and relocation/header fields.
Control flow: included by `head.S` when `CONFIG_EFI_STUB` is enabled; firmware reads the header before jumping to the kernel entry.
State and persistence: header bytes persist in the kernel image and are part of the boot protocol.
Dependencies and integration: tied to EFI stub, linker symbols, image size symbols, and firmware loaders.
Risks and test signals: incorrect offsets or machine values prevent EFI boot. Signals include EFI boot on firmware, PE header inspection, secure boot tooling, and relocatable kernel tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/efi-header.S -->
