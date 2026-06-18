# sources/distributed-fs/ceph-client/arch/sh/kernel/module.c

Purpose: applies SH ELF relocations for loadable modules and connects module DWARF unwind metadata.

Important APIs and control flow: `apply_relocate_add()` iterates `Elf32_Rela` entries, resolves each symbol plus addend, and updates target locations for `R_SH_DIR32`, `R_SH_REL32`, and SHmedia immediate relocation forms. Unknown relocations print an error and return `-ENOEXEC`. `module_finalize()` calls `module_dwarf_finalize()`, and `module_arch_cleanup()` removes module unwind metadata through `module_dwarf_cleanup()`.

State, dependencies, and risks: state is modified module text/data and module-owned CIE/FDE lists. Dependencies include ELF32 relocation definitions, unaligned access helpers, module loader, and DWARF unwinder. Risks include unsupported relocation types, immediate field masking mistakes, no icache flush in this file after relocation, and module unwind parser failures blocking load. Test signals are module insertion with each relocation type, unknown relocation rejection, and module unload cleaning unwind entries.
