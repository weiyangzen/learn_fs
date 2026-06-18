<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/winmacro.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/winmacro.h

Purpose: Supplies SPARC32 assembly macros for saving/restoring register windows, trap-frame fields, user window spill bookkeeping, and current-task lookup.

Important APIs and control flow: `STORE_WINDOW`/`LOAD_WINDOW` move locals and ins between registers and memory offsets from `ptrace.h`. `LOAD_PT_*` and `STORE_PT_*` transfer selected `pt_regs` fields around trap return paths. `SAVE_BOLIXED_USER_STACK` records a user stack pointer and stores a register window in thread-info save slots. `LOAD_CURRENT` loads the current task pointer from `current_set`; on SMP it includes `.cpuid_patch` alternatives for SUN4D and LEON CPU-id mechanisms.

State, dependencies, and risks: state touched includes saved register-window arrays, trap frames, `%y`, PSR/PC/NPC fields, thread-info window counters, and per-CPU `current_set`. Dependencies include `asm/ptrace.h`, thread-info offsets, ASI definitions for Viking temporary registers, and boot-time CPU patching. Risks are offset drift, stack alignment assumptions, register clobber mistakes, and CPU-id patch errors on SMP. Test signals are trap/return stress, signal delivery, register-window overflow/underflow tests, SMP boot on sun4m/sun4d/LEON, and user-stack spill recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/winmacro.h -->
