<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/elf.h

## Purpose
`elf.h` defines x86 UML ELF ABI details for executable loading, core dumps, relocation constants, and vDSO auxiliary vector exposure.

## Important APIs, types, and functions
Important macros include `elf_check_arch`, `ELF_CLASS`, `ELF_DATA`, `ELF_ARCH`, `ELF_PLAT_INIT`, `ELF_CORE_COPY_REGS`, `ELF_PLATFORM`, `ELF_HWCAP`, `ELF_ET_DYN_BASE`, and 64-bit `ARCH_DLINFO`/`AT_SYSINFO_EHDR`.

## Control flow
The ELF loader uses these macros to accept the correct machine type, initialize registers, set personality/platform/HWCAP aux values, and copy general registers into core-dump notes. On 64-bit it also maps the UML vDSO.

## State and persistence behavior
State is external `elf_aux_hwcap`, `elf_aux_platform`, and `um_vdso_addr`; otherwise definitions are compile-time ABI contracts.

## Dependencies and integration points
It depends on ptrace register macros, user structures, SKAS support, and `vdso/vma.c` on 64-bit.

## Risks and edge cases
Register order in core dumps must match userspace ABI. Wrong `ELF_ET_DYN_BASE` or vDSO aux data affects dynamic linker behavior.

## Test signals
Signals are running 32/64-bit UML userspace, core-dump register checks, and vDSO presence in auxv/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/elf.h -->
