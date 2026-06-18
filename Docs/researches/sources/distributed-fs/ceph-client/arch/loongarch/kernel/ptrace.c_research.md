## sources/distributed-fs/ceph-client/arch/loongarch/kernel/ptrace.c

### Purpose
`ptrace.c` implements LoongArch ptrace and core-dump register access. It exposes GPR, FPR, CPUCFG, LSX, LASX, LBT, hardware breakpoint, and hardware watchpoint regsets; supports legacy `PTRACE_PEEKUSR`/`POKEUSR`; and implements ptrace single-step using hardware breakpoints.

### Important APIs, Types, And Functions
The file defines `ptrace_disable`, `task_user_regset_view`, `arch_ptrace`, `regs_query_register_offset`, `user_enable_single_step`, and `user_disable_single_step`. Regset handlers include `gpr_get/set`, `fpr_get/set`, `cfg_get/set`, `simd_get/set`, `lbt_get/set`, and `hw_break_get/set`. Hardware breakpoint helpers wrap perf breakpoints through `register_user_hw_breakpoint`, `modify_user_hw_breakpoint`, and architecture encode/decode helpers.

### Control Flow
Regset reads save live FPU state as needed, then copy data into `membuf`; writes initialize FP context when needed and copy user data into thread state. SIMD reads pad unavailable upper lanes with all ones based on whether FP, LSX, or LASX context is live. Hardware breakpoint regset writes ignore resource-info input, then apply address, mask, and control triplets, creating disabled perf breakpoint events lazily. Single-step sets or reuses instruction breakpoint slot 0 at current `csr_era`, records the address, and sets `TIF_SINGLESTEP`.

### State, Persistence, And Dependencies
Ptrace-visible state persists in `pt_regs`, `thread.fpu`, `thread.lbt`, `thread.hbp_break/watch`, thread flags `TIF_LOAD_WATCH` and `TIF_SINGLESTEP`, and per-task perf breakpoint events. The code depends on stable ELF note types, user regset ABI sizes, LoongArch CPUCFG, FPU/SIMD layout, perf hardware breakpoint support, and security/no-spec indexing helpers.

### Integration Points
Generic ptrace and core dump code use the regset view. `traps.c` handles watchpoint and single-step traps. `process.c` copies hardware breakpoints on fork and clears them on flush. Debuggers such as gdb consume the note types and legacy user offsets.

### Risks
The regset layout is ABI-sensitive. `ptrace_hbptriggered` has two loops using the same index variable and the watch loop overwrites the break-loop result, so signal errno identification should be reviewed carefully. Single-step reuses breakpoint slot 0, which can interact with user-programmed hardware breakpoints. Kernel address rejection differs between 32-bit and 64-bit address ranges and must match user/kernel split.

### Test Signals
Run gdb/ptrace tests for GPR/FPR/CPUCFG/LSX/LASX/LBT get/set, core dump note validation, legacy peek/poke offsets, hardware breakpoint/watchpoint programming, single-step over normal and LL/SC-like sequences, and detach cleanup. Include invalid regset sizes, out-of-range breakpoint indices, and kernel-space breakpoint addresses.
