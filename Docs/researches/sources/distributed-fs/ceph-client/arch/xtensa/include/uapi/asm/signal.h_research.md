<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/signal.h

Purpose: defines Xtensa UAPI signal numbers, signal-set layout, action/restorer ABI, realtime bounds, stack sizes, and `stack_t`. Important constants include `_NSIG`, `_NSIG_BPW`, `_NSIG_WORDS`, traditional signal numbers 1-31, `SIGRTMIN`, `SIGRTMAX`, `SA_RESTORER`, `MINSIGSTKSZ`, and `SIGSTKSZ`.

Control flow is in generic signal/syscall code and architecture signal frame code. Persistent state includes user signal masks, sigaction tables, altstack state, and signal frames. Dependencies include `linux/types.h`, generic signal defs, and `__kernel_size_t`. Integration points are libc, `sigaction`, `rt_sigprocmask`, signal delivery/return, strace, and debuggers. Risks are ABI incompatibility with libc, signal number mismatches, insufficient signal stack size for extended registers, and restorer handling. Test signals include signal selftests, realtime signals, altstack/nested handlers, libc compatibility, and headers_install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/signal.h -->
