# sources/distributed-fs/ceph-client/arch/mips/include/asm/module.h

Purpose: MIPS module-loader architecture definitions, including module-specific exception tables and ELF relocation type aliases.

Important APIs/types/functions: `struct mod_arch_specific` stores data-bus-error exception table list/ranges and pending `mips_hi16` relocations. Defines `Elf64_Mips_Rel` and `Elf64_Mips_Rela` with MIPS64 packed relocation fields. For `CONFIG_32BIT` or `CONFIG_64BIT`, aliases generic `Elf_*`, `Elf_Mips_Rel`, `Elf_Mips_Rela`, `ELF_R_TYPE`, `ELF_R_SYM`, `ELF_MIPS_R_SYM`, and `ELF_MIPS_R_TYPE`. Declares or stubs `search_module_dbetables()`.

Control flow, state, and persistence: State is attached to loaded modules for relocation and exception lookup. The DBE table lookup returns matching exception entries for fault recovery.

Dependencies and integration: Depends on Linux ELF types, module code, and MIPS exception tables. Integrates with module relocation, fault handling, and data bus error recovery.

Risks and test signals: MIPS64 relocation packing differs from generic ELF64; incorrect aliases break module loading. Test 32/64-bit module builds, HI16/LO16 relocation sequences, DBE exception table lookup, and module unload cleanup.
