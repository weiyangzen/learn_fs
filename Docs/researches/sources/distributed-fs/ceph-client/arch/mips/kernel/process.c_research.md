# sources/distributed-fs/ceph-client/arch/mips/kernel/process.c

## Purpose
Implements MIPS process/thread lifecycle support: starting user threads, copying task state, saving live CPU extension state, stack unwinding, blocked-task wait-channel reporting, user stack layout, SMP backtrace triggering, FP mode prctl support, and register dump helpers.

## Important APIs, Types, and Functions
- `start_thread()`, `exit_thread()`, `arch_dup_task_struct()`, and `copy_thread()` implement exec, exit cleanup, fork duplication, and kernel/user child register setup.
- `struct mips_frame_info`, instruction classifiers, `get_frame_info()`, `frame_info_init()`, `thread_saved_pc()`, `unwind_stack_by_address()`, `unwind_stack()`, and `__get_wchan()` implement schedule-prologue analysis and stack unwinding.
- `mips_stack_top()` and `arch_align_stack()` calculate user stack placement/randomization constraints.
- `arch_trigger_cpumask_backtrace()` sends asynchronous SMP backtrace IPIs.
- `mips_get_process_fp_mode()` and `mips_set_process_fp_mode()` implement MIPS FP mode reporting/switching.
- `mips_dump_regs32()` and `mips_dump_regs64()` format pt_regs for ptrace/core regsets.

## Control Flow
Exec through `start_thread()` drops kernel/FPU/MSA privileges, clears math state, initializes DSP, and sets PC/SP. Fork goes through `arch_dup_task_struct()` to save live FPU/MSA/DSP state before copying `task_struct`, then `copy_thread()` builds child pt_regs at the top of the kernel stack. Kernel threads get `ret_from_kernel_thread` and function arguments in saved registers; user clones inherit pt_regs, return zero in the child, optionally use a new user SP and TLS, and start at `ret_from_fork`. At init, `frame_info_init()` analyzes `__schedule`/`schedule` prologue so blocked task PCs can be recovered. Unwinding uses kallsyms function sizes and decoded stack-frame/RA-save instructions. FP mode changes validate support, update every thread's TIF flags, then schedule work on CPUs that may be running the process so old FPU modes are flushed.

## State and Persistence
State lives in `task_struct.thread`, `thread_info`, pt_regs on kernel stacks, TIF flags, and per-CPU call-single data for backtraces. `schedule_mfi` caches decoded scheduler frame info after boot. No disk persistence exists.

## Dependencies and Integration Points
Depends on low-level entry assembly (`ret_from_fork`, `ret_from_kernel_thread`), FPU/MSA/DSP helpers, delay-slot emulation cleanup, CPU feature flags, kallsyms, IRQ stacks, NMI backtrace framework, scheduler/task stack layout, MIPS ABI descriptors, VDSO sizing, GIC user page mapping, and ptrace regset dump consumers.

## Risks
Instruction decoding for stack unwinding is architecture-revision sensitive, especially microMIPS and Loongson encodings. Incorrect clone register setup can corrupt user ABI returns or kernel-thread startup. Live FPU/MSA/DSP state must be saved before task duplication to avoid stale child state. FP mode switching is process-wide and has races unless every potentially running CPU context-switches. User stack top calculation must leave space for delay-slot emulation, VDSO, GIC page, randomization, and cache coloring.

## Test Signals
Fork/clone/exec tests should validate child return values, TLS, and kernel-thread startup. Backtrace and `/proc/<pid>/wchan` should work through scheduler frames. `prctl(PR_SET_FP_MODE)` should accept/reject modes according to CPU and ABI and preserve FP results across threads. NMI backtrace should warn rather than corrupt state if a previous IPI is still busy. Core dumps/ptrace should show zeroed k0/k1 and correct register contents.
