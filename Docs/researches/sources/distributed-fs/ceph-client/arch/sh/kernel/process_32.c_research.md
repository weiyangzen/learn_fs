# sources/distributed-fs/ceph-client/arch/sh/kernel/process_32.c

Purpose: implements 32-bit SH process register display, user/thread startup, clone setup, context switching, and wait-channel lookup.

Important APIs and control flow: `show_regs()` prints PC/PR/SR/SP, MMU TEA, GPRs, MAC/GBR registers, trace, and decoded code. `start_thread()` initializes user PC/SP/SR/PR and frees old xstate. `flush_thread()` clears ptrace hardware breakpoints and lazy FPU state. `copy_thread()` builds kernel-thread or user-child `pt_regs`, handles DSP copy, TLS in GBR, child return value zero, and fork return trampolines. `__switch_to()` saves previous lazy FPU, restores banked kernel thread-info register, optionally prefetches/restores hot FPU state, and updates stack canary on non-SMP. `__get_wchan()` reports saved PC or frame-pointer-derived scheduler caller.

State, dependencies, and risks: state includes thread registers, ptrace breakpoint array, DSP/FPU state, banked r7, and per-task stack canary. Dependencies include entry trampolines, FPU/DSP helpers, frame-pointer layout, MMU context, and SH switch assembly. Risks include register layout coupling with `entry-common.S`, clone TLS ABI in GBR, and FPU lazy restore heuristics. Test signals are fork/clone/kernel_thread, exec user register setup, ptrace hardware breakpoint cleanup, and context-switch FPU preservation.
