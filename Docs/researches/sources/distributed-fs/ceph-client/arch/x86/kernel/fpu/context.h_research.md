# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/context.h

## Purpose
Defines inline helpers for tracking whether a task's FPU register state is currently valid in CPU registers.

## Important APIs, Types, And Functions
`__cpu_invalidate_fpregs_state()` clears the per-CPU owner. `__fpu_invalidate_fpregs_state()` invalidates a task by setting `last_cpu=-1`. `fpregs_state_valid()` checks owner and CPU. `fpregs_activate()`/`fpregs_deactivate()` update ownership and trace. `fpregs_restore_userregs()` restores current user registers when needed.

## Control Flow
Lazy restore paths check whether current's `struct fpu` owns the CPU registers. If not, `restore_fpregs_from_fpstate()` loads all user FPU state except parts handled eagerly or specially, marks the FPU active, records `last_cpu`, and clears `TIF_NEED_FPU_LOAD`.

## State, Persistence, And Dependencies
State is `fpu_fpregs_owner_ctx`, `fpu->last_cpu`, and current thread flags. It depends on xstate restore helpers, PKRU/XFD rules, scheduler current task state, and FPU tracepoints.

## Integration Points
Included by FPU core, signal, and regset paths to coordinate lazy FPU state with context switches, ptrace, signal return, and kernel FPU sections.

## Risks
Any code that modifies FPU registers or task fpstate must invalidate ownership correctly; otherwise stale registers can overwrite modified memory state or leak between tasks.

## Test Signals
Context switch, ptrace modification, signal restore, and kernel FPU use should force reloads only when needed and never run user tasks with stale register state.
