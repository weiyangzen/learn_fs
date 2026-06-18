# sources/distributed-fs/ceph-client/arch/x86/kernel/signal_64.c

## Purpose
`signal_64.c` implements native x86-64 and x32 realtime signal setup and sigreturn. It restores 64-bit register/FPU context, handles compatibility SS restore rules, integrates CET shadow stacks, and preserves native/x32 siginfo layouts.

## Important APIs, Types, And Functions
Important functions are `x64_setup_rt_frame()`, native `rt_sigreturn`, `x32_setup_rt_frame()`, `x32_rt_sigreturn`, `copy_siginfo_to_user32()`, and `sigaction_compat_abi()`. Internals include `force_valid_ss()`, `restore_sigcontext()`, `__unsafe_setup_sigcontext()`, `frame_uc_flags()`, and `x32_copy_siginfo_to_user()`.

## Control Flow
Setup requires `SA_RESTORER`, obtains a frame, writes ucontext/sigcontext/sigmask/optional siginfo, installs a shadow-stack signal record when enabled, and sets handler args in `di/si/dx`. Sigreturn validates the frame, restores mask/altstack/general registers/FPU, restores shadow-stack state, and returns restored `ax`. x32 uses compat siginfo and special SIGCHLD time handling.

## State, Persistence, Dependencies, Integration
State includes pt_regs, ucontext flags (`UC_FP_XSTATE`, `UC_SIGCONTEXT_SS`, `UC_STRICT_RESTORE_SS`), FPU state, sigmask, altstack, and CET tokens. It depends on `signal.c`, FPU helpers, `shstk.c`, user access, x32/compat types, and descriptor validation.

## Risks And Test Signals
SS restore behavior is compatibility-sensitive for DOSEMU/CRIU. `SA_RESTORER` and shadow-stack restorer alignment are mandatory contracts. Test native 64-bit and x32 handlers, missing restorers, strict/non-strict SS restore, bad SS values, shadow-stack sigreturn, x32 SIGCHLD info, bad frames, and compat sigaction tagging.
