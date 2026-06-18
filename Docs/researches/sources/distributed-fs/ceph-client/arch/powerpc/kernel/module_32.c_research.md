
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/module_32.c

Purpose: 32-bit PowerPC module loader backend for sizing PLT trampoline sections, applying ELF RELA relocations, and creating ftrace trampolines for out-of-range calls.

Important APIs/types/functions: `module_frob_arch_sections`; `get_plt_size`; `count_relocs`; `relacmp`; `do_plt_call`; `apply_relocate_add`; `module_trampoline_target`; `module_finalize_ftrace`; module fields `core_plt_section`, `init_plt_section`, `tramp`, and `tramp_regs`.

Control flow: before allocation, relocation sections are sorted by symbol/addend and scanned for unique `R_PPC_REL24` entries, adding PLT space for core/init sections and ftrace callers. During relocation, absolute 32-bit and 16-bit HI/HA/LO writes are patched, REL24 branches are checked for +/-32 MiB range, and out-of-range calls allocate or reuse a four-instruction PLT entry (`lis/addi/mtctr/bctr`) before patching the branch displacement. REL32 writes a 32-bit relative value. Ftrace finalization reserves PLT entries for `ftrace_caller` and optionally `ftrace_regs_caller`.

State and persistence: mutates module sections, PLT entries, and ftrace architecture fields. Sorted relocation arrays are also modified in memory during sizing.

Dependencies and integration: depends on generic module loader section callbacks, PowerPC text patching, `struct ppc_plt_entry`, dynamic ftrace, and module core/init memory boundary helpers.

Risks: PLT sizing depends on sorted relocation identity and must match later allocation; range checks must be exact for REL24; 16-bit patching aligns down to a full instruction; ftrace trampoline decoding assumes exact PLT instruction patterns.

Test signals: load modules with near and far calls, init/core section calls, unknown relocation rejection, ftrace and ftrace-with-regs enabled, and `module_trampoline_target` on generated PLT entries.
