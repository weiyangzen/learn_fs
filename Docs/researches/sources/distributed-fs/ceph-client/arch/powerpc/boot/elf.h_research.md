# sources/distributed-fs/ceph-client/arch/powerpc/boot/elf.h

Purpose: defines the minimal ELF32/ELF64 data structures and constants consumed by the boot wrapper's ELF parser.

Important APIs/types/functions: types `elf32_hdr`, `elf64_hdr`, `elf32_phdr`, `elf64_phdr`, `elf_info`; macros `_PPC_BOOT_ELF_H_`, `PT_NULL`, `PT_LOAD`, `PT_DYNAMIC`, `PT_INTERP`, `PT_NOTE`, `PT_SHLIB`, `PT_PHDR`, `PT_TLS`, `PT_LOOS`, `PT_HIOS`, `PT_LOPROC`, `PT_HIPROC`, `PT_GNU_EH_FRAME`, `PT_GNU_STACK`, `ET_NONE`, `ET_REL`, `ET_EXEC`, and 38 more. Source size is 158 lines / 4046 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
