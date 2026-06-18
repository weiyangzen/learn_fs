<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/signal.h

Purpose: Defines PowerPC signal numbers, signal-set layout, signal action structs, altstack type, stack sizes, and 32-bit debug-sigreturn operations.

Important APIs/types/functions: `_NSIG`, `_NSIG_BPW`, `sigset_t`, signal numbers, `SA_RESTORER`, `MINSIGSTKSZ`, `SIGSTKSZ`, userspace `old_sigaction`, `sigaction`, `stack_t`, 32-bit `struct sig_dbg_op`, and `SIG_DBG_*` constants.

Control flow: Kernel and libc use these constants and structures for signal install, delivery, alternate stacks, and 32-bit debug signal return behavior.

State and persistence: Signal masks/actions and altstack settings persist per task in kernel state; structures define the userspace ABI view.

Dependencies and integration points: Depends on Linux types and generic signal definitions. Integrated by signal syscalls, libc, debuggers, and signal frame code.

Risks: Signal numbers, stack sizes, and structure layout are ABI. ppc64 has larger minimum stack due to larger context state.

Test signals: Signal syscall tests, realtime signal mask tests, altstack sizing tests, 32-bit debug signal return tests, and libc ABI checks.

Source read size: 119 lines, 2595 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/signal.h -->
