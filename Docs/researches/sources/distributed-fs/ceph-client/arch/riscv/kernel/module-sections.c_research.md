# sources/distributed-fs/ceph-client/arch/riscv/kernel/module-sections.c

Purpose: Prepares module GOT and PLT sections needed when RISC-V module relocations cannot directly reach their targets.

Important APIs/types/functions: Implements `module_emit_got_entry()`, `module_emit_plt_entry()`, relocation sorting/dedup helpers, `rela_needs_plt_got_entry()`, and `module_frob_arch_sections()`.

Control flow: Before final relocation, module sections are scanned and sorted to count unique GOT/PLT needs. The module loader reserves architecture section storage, then relocation handlers emit or reuse GOT/PLT entries for out-of-range calls or GOT references.

State and persistence: Mutates module architecture metadata and allocated GOT/PLT sections that persist with the loaded module.

Dependencies and integration points: Used by `module.c` relocation handlers under `CONFIG_MODULE_SECTIONS`, depends on ELF Rela entries, module loader section allocation, and RISC-V relocation semantics.

Risks and test signals: Dedup or size-count errors can overflow reserved sections or duplicate entries. Test modules with far calls, GOT references, many relocations, duplicate relocations, and module unload/reload.
