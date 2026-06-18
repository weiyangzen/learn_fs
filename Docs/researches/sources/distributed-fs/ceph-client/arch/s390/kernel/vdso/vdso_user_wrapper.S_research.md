## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso_user_wrapper.S

Purpose: Exports user-visible vDSO entry symbols and supplies ABI-compatible stack frames for older glibc callers, plus syscall trampolines for restart and signal return.

Important symbols: `__kernel_gettimeofday`, `__kernel_clock_getres`, `__kernel_clock_gettime`, `__kernel_getcpu`, `__kernel_restart_syscall`, `__kernel_sigreturn`, and `__kernel_rt_sigreturn`.

Control flow: The `vdso_func` macro allocates a special vDSO stack frame, saves `%r14`, clears the user backchain, calls the matching `__s390_vdso_*` function with `brasl`, restores return state, and branches back. The `vdso_syscall` macro issues `svc` for trampolines and places an illegal word afterward to catch unexpected returns.

State and persistence: Manipulates only the user stack/register frame for each call. Frame layout is persistent ABI and is consumed by `stacktrace.c`.

Dependencies and integration: Depends on s390 stack-frame offsets, DWARF CFI, syscall numbers, vDSO C entry points, and user stack walking special cases.

Risks and test signals: Risks are stack-frame layout drift, broken CFI/unwind data, and trampolines returning unexpectedly. Test signals include old and current glibc vDSO calls, user stack traces through vDSO, signal return paths, and `readelf --debug-dump=frames`.
