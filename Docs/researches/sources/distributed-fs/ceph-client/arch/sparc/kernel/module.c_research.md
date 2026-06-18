# sources/distributed-fs/ceph-client/arch/sparc/kernel/module.c

Purpose: Implements SPARC module loader architecture hooks for ELF symbol cleanup, relocation application, sun4v patch sections, and Spitfire I-cache handling.

Important APIs/types/functions: `module_frob_arch_sections()` finds the symbol table and converts undefined `STT_REGISTER` symbols to absolute so generic module loading ignores SPARC register pseudo-symbols. `apply_relocate_add()` handles SPARC relocations such as `R_SPARC_DISP32`, `R_SPARC_32`, `R_SPARC_UA32`, `R_SPARC_WDISP30`, `R_SPARC_WDISP22`, `R_SPARC_LO10`, `R_SPARC_HI22`, and on SPARC64 `R_SPARC_64`, `R_SPARC_UA64`, `R_SPARC_WDISP19`, and `R_SPARC_OLO10`. `do_patch_sections()` and `module_finalize()` patch `.sun4v_1insn_patch` and `.sun4v_2insn_patch` on hypervisor TLB systems.

Control flow: During module load, section frobbing normalizes register symbols before generic resolution. Relocation processing iterates each `Elf_Rela`, computes symbol plus addend, patches bytes or instruction fields, and aborts on unsupported relocation types. Finalization applies sun4v instruction substitutions and, on Spitfire, flushes register windows and invalidates I-cache tags.

State and persistence: It mutates module text/data in memory and may modify module patch sections. It does not keep module-private state after load. The relocated code persists until module unload.

Dependencies and integration points: It depends on Linux module loader/ELF structures, SPARC relocation encodings, sun4v patch helpers, `tlb_type`, Spitfire cache routines, and exported module loader hooks.

Risks and test signals: Relocation bitfield mistakes produce invalid branches or addresses. The SPARC64 BUG_ON enforces module locations under 4 GB for patched sites. Tests include loading modules with branches/calls/64-bit data/OLO10 relocations, modules containing sun4v patch sections, old SPARC register symbols, unsupported relocation rejection, and Spitfire cache coherency.
