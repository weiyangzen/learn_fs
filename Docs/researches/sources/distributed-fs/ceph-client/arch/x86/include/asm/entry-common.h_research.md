
# sources/distributed-fs/ceph-client/arch/x86/include/asm/entry-common.h

Purpose: x86 hooks for generic syscall/interrupt entry and exit handling.

Important APIs and control flow: `arch_enter_from_user_mode()` performs `CONFIG_DEBUG_ENTRY` checks on EFLAGS, SMAP/XenPV AC state, user mode, thread stack, and regs location. `arch_exit_work()` fires user-return notifiers, updates the IO bitmap, and loads FPU state when needed. `arch_exit_to_user_mode_prepare()` asserts FPU consistency, handles pending work, updates FRED RSP0, clears compat status bits, and optionally issues IBPB before user return. `arch_exit_to_user_mode()` clears AMD divider state.

State, dependencies, and risks: state includes task thread flags/status, TSS IO bitmap, FPU registers, FRED state, and per-CPU branch prediction barrier flag. Dependencies include nospec branch mitigation, IO bitmap, FPU API, user-return notifier, and debug entry code. Risks include returning to user mode with stale compat flags, FPU state inconsistency, missing IBPB, or incorrect stack/regs assumptions. Test signals are syscall selftests, ptrace compat restart tests, FPU lazy-load tests, and entry debug assertions.
