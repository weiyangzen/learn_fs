# sources/distributed-fs/ceph-client/arch/sparc/include/asm/ptrace.h

Purpose: Architecture ptrace/register helper header for both sparc64 and sparc32, exposing syscall markers, user-mode tests, instruction/stack pointers, register snapshots, profiling PC lookup, and register offset accessors.

Important APIs/types/functions: types `global_reg_snapshot`, `global_pmu_snapshot`; functions/helpers `pt_regs_trap_type`, `pt_regs_is_syscall`, `pt_regs_clear_syscall`, `is_syscall_success`, `regs_return_value`, `profile_pc`, `regs_query_register_offset`, `regs_get_kernel_stack_nth`, `regs_get_register`, `kernel_stack_pointer`; macros/constants `__SPARC_PTRACE_H`, `arch_ptrace_stop_needed`, `arch_ptrace_stop`, `current_pt_regs`, `force_successful_syscall_return`, `user_mode`, `instruction_pointer`, `instruction_pointer_set`, `user_stack_pointer`, `profile_pc`, `MAX_REG_OFFSET`, `STACK_BIAS`, `GR_SNAP_TSTATE`, `GR_SNAP_TPC`, `GR_SNAP_TNPC`, `GR_SNAP_O7`, `GR_SNAP_I7`, `GR_SNAP_RPC`, plus 2 more.

Control flow: The file is driven by preprocessor gates such as `__SPARC_PTRACE_H`, `defined(__sparc__) && defined(__arch64__)`, `__ASSEMBLER__`, `CONFIG_SMP`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into SMP, syscall/ptrace paths rather than through standalone functions.

State and persistence behavior: State is `pt_regs`, `thread_info` window-save counters, sparc64 global CPU snapshots, and syscall carry/noerror bits.

Dependencies and integration points: Includes/dependencies: `uapi/asm/ptrace.h`, `linux/compiler.h`, `linux/threads.h`, `asm/switch_to.h`. Integration points include SMP, syscall/ptrace; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, configuration-specific build gaps, ABI compatibility breaks. Test signals: PTRACE register access, syscall tracing/rollback, stack unwinding, SMP profiling, and user-window synchronization on ptrace stop should be tested.
