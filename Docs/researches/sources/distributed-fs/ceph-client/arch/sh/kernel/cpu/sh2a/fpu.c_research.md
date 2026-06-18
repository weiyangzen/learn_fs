<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/fpu.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/fpu.c

Purpose: saves/restores SH-2A FPU state and emulates denormal arithmetic traps.

Important APIs/types/functions: `save_fpu()`, `restore_fpu()`, denormal float/double helpers, `ieee_fpe_handler()`, `BUILD_TRAP_HANDLER(fpu_error)`.

Control flow: trap handler un-lazies FPU state, decodes the faulting or delay-slot instruction, emulates denormal fcnvsd/fmul/fadd/fsub when possible, clears FPSCR cause/flag bits, restores FPU, or sends SIGFPE.

State and persistence: per-task hardfpu registers/fpscr/fpul are persistent scheduler state; hardware FPU enable is transient.

Dependencies/integration: depends on trap framework, task xstate, instruction encodings, branch-delay PC rules, and FPU control helpers.

Risks: manual IEEE emulation has precision FIXME notes and fragile instruction decoding for delay slots.

Test signals: test denormal single/double multiply/add/sub, branch-delay FPU traps, context switch, and SIGFPE fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/fpu.c -->
