# sources/distributed-fs/ceph-client/arch/sparc/kernel/traps_32.c

Purpose: handles 32-bit SPARC traps for illegal/privileged instructions, hardware traps, unaligned accesses, FPU disabled/exceptions, tag overflow, watchpoints, coprocessor traps, divide-by-zero, BUG reporting, and trap initialization.

Important APIs/types/functions: `die_if_kernel()`, `do_hw_interrupt()`, `do_illegal_instruction()`, `do_priv_instruction()`, `do_memaccess_unaligned()`, `do_fpd_trap()`, `do_fpe_trap()`, `handle_tag_overflow()`, `handle_watchpoint()`, `handle_reg_access()`, `handle_cp_disabled()`, `handle_cp_exception()`, `handle_hw_divzero()`, optional `do_BUG()`, and `trap_init()`.

Control flow: kernel-mode fatal traps print registers, walk register-window callers with bounds/alignment checks, dump nearby instructions, taint, and terminate. User traps translate to `SIGILL`, `SIGBUS`, `SIGFPE`, `SIGEMT`, or `SIGTRAP` style faults. FPU-disabled traps enable EF, lazily save/load FPU ownership on UP or per-task FPU state on SMP, and initialize first-use registers. FPU exception traps save FPU state, optionally emulate unfinished/unimplemented operations via `do_mathemu()`, otherwise decode FSR exception bits into signal codes.

State and persistence: mutates per-task FPU registers/FSR/queue/depth, `last_task_used_math` on UP, `TIF_USEDFPU` on SMP, `used_math`, active_mm in `trap_init()`, and static fake FPU buffers used to clear stray errors.

Dependencies and integration points: depends on SPARC trap/register layouts, FPU save/load helpers, math emulation, signal delivery, `init_mm`, and assembly offset constants.

Risks: lazy FPU ownership is subtle across UP/SMP. Kernel FPU exceptions are tolerated only a limited number of times. `trap_init()` includes compile-time offset checks via an undefined symbol to catch assembly/C layout drift.

Test signals: user illegal/privileged/unaligned/FPU/divzero traps, FPU first-use and context switching, math emulation for unfinished FP ops, kernel fatal trap diagnostics, BUG verbose export, and boot-time `trap_init()` offset consistency.
