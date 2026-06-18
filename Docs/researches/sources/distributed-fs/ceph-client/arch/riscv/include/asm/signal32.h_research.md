<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/signal32.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/signal32.h

Purpose: Declares 32-bit compatibility signal-frame setup and restore hooks for RV64 compat tasks.

Important APIs/types/functions: Declares `compat_setup_rt_frame()` and `compat_sys_rt_sigreturn()` under compat support.

Control flow: Signal delivery code calls setup to build a 32-bit frame; sigreturn validates/restores it into kernel register state.

State and persistence: State is user-visible compat signal frame content and restored `pt_regs`/FPU/vector context.

Dependencies and integration points: Integrates with compat syscalls, signal.c, uapi sigcontext/ucontext, and ptrace register layout.

Risks: ABI mistakes break 32-bit processes or allow malformed signal frames to restore unsafe state.

Test signals: RV64 compat signal selftests, sigreturn fuzzing, ptrace/signal interaction, and altstack tests.

Source read size: 18 lines, 358 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/signal32.h -->
