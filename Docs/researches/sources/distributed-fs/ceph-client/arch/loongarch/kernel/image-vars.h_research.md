<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/image-vars.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/image-vars.h

Purpose: maps kernel image symbols for the EFI stub and compressed/relocatable image interfaces.
Important APIs and types: declares symbol aliases for image size, file size, and entry/load addresses used by EFI or relocation code.
Control flow: included by low-level image/header code at build time; no runtime logic.
State and persistence: symbols become part of linked image metadata.
Dependencies and integration: tied to linker script symbols, `head.S`, EFI stub, and boot loaders.
Risks and test signals: wrong symbol exposure breaks boot image headers. Signals include EFI boot, objdump/readelf image checks, and relocatable boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/image-vars.h -->
