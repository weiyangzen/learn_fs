# sources/distributed-fs/ceph-client/arch/mips/include/asm/processor.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/processor.h

### Purpose
`processor.h` defines the MIPS processor and per-thread execution-state contract: task address limits, stack placement, FPU/MSA/DSP/watch/COP2 saved state, thread initialization, stack/register helpers, return-address handling, prefetch C intrinsics, and FP-mode prctl hooks.

### Important APIs, Types, And Functions
Key macros include `TASK_SIZE`, `TASK_SIZE32`, `TASK_SIZE64`, `STACK_TOP_MAX`, `TASK_UNMAPPED_BASE`, `VDSO_RANDOMIZE_SIZE`, `NUM_FPU_REGS`, `FPU_REG_WIDTH`, `FPR_IDX`, `INIT_THREAD`, `task_pt_regs`, `KSTK_EIP`, `KSTK_ESP`, `return_address`, `ARCH_HAS_PREFETCH`, `GET_FP_MODE`, and `SET_FP_MODE`. Key types include `union fpureg`, `struct mips_fpu_struct`, `struct mips_dsp_state`, `union mips_watch_reg_state`, Octeon COP2/CVMSEG state, and `struct thread_struct`. Externs include `arch_dup_task_struct`, `mips_stack_top`, `start_thread`, `__get_wchan`, `mips_get_process_fp_mode`, `mips_set_process_fp_mode`, and `show_registers`.

### Control Flow
Scheduler and fork/exec paths initialize and copy `thread_struct`; exception and ptrace paths read saved task registers through `task_pt_regs`; FP-mode prctls dispatch through the defined getter/setter; optional prefetch macros compile to GCC builtins when supported.

### State, Persistence, Dependencies, And Integration
State is per-task CPU context, FPU/MSA/DSP/watch registers, Octeon COP2 state, bad address/error/trap metadata, and ABI pointers. Dependencies include CPU/cache/thread headers, `mipsregs`, `dsemul`, `prefetch`, VDSO processor definitions, and task/thread flags. Integration is central to scheduler context switching, signal/ptrace, coredumps, FPU emulation, prctl, and VDSO stack layout.

### Risks
`struct thread_struct` layout is coupled to assembly offsets. Address-limit constants are ABI-visible and affect mmap, stack, and VDSO placement. Endianness-sensitive FPR indexing and optional MSA width must match save/restore code. Octeon COP2 alignment is strict.

### Test Signals
Cross-build 32/64-bit, O32/N32/N64, MSA, DSP, Octeon, and FP-affinity configs. Run fork/exec, signal, ptrace, coredump, FP/MSA/DSP context-switch, prctl FP-mode, and stack unwinding tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/processor.h -->
