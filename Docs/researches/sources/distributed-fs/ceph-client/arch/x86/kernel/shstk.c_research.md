# sources/distributed-fs/ceph-client/arch/x86/kernel/shstk.c

## Purpose
`shstk.c` implements Intel CET user shadow-stack support: allocation, enable/disable policy, signal shadow-stack records, clone/vfork behavior, the `map_shadow_stack` syscall, and `ARCH_SHSTK_*` `arch_prctl` operations.

## Important APIs, Types, And Functions
Key functions include `reset_thread_features()`, `shstk_alloc_thread_stack()`, `shstk_pop()`, `shstk_push()`, `setup_signal_shadow_stack()`, `restore_signal_shadow_stack()`, `shstk_free()`, `shstk_prctl()`, `shstk_update_last_frame()`, and `shstk_is_enabled()`. Internal state is `thread.features`, `thread.features_locked`, `struct thread_shstk`, restore tokens, signal data markers, and CET MSRs `MSR_IA32_PL3_SSP`/`MSR_IA32_U_CET`.

## Control Flow
`shstk_setup()` rejects unsupported CPUs and IA32 syscalls, allocates a `VM_SHADOW_STACK` mapping sized from `RLIMIT_STACK`, writes the PL3 SSP to the top, enables CET, and records base/size. Clone allocates a separate stack for `CLONE_VM`, leaves non-`CLONE_VM` to copied state, and clears tracking for `CLONE_VFORK`. Signal delivery pushes a marked restore token and restorer address; sigreturn validates the token's VMA with mmap sequence retry before restoring SSP. Disable clears CET MSRs, frees tracked mappings, and clears SHSTK/WRSS bits.

## State, Persistence, Dependencies, Integration
Persistent state lives in task thread features and shadow-stack VMA mappings with guard-page assumptions. It depends on FPU register locking for MSRs, `vm_mmap_shadow_stack()`, `write_user_shstk_64()`, mmap locks, clone/exit paths, and `X86_FEATURE_USER_SHSTK`. Signal setup in `signal_64.c` calls the delivery/restore hooks.

## Risks And Test Signals
Token validation, VMA races, feature locking, `CLONE_VFORK`, and failed fork cleanup are security-sensitive. Test prctl enable/disable/lock/status, WRSS permission rules, `map_shadow_stack` flags/overflow, nested signals, invalid tokens/restorers, clone/vfork/fork/exec/exit, ptrace unlock for CRIU, and 32-bit syscall rejection.
