<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/signal.h

Source read size: 84 lines, 1795 bytes.

Purpose: defines PA-RISC signal numbers, signal action flags, stack sizes, and signal set types. Important APIs/types: `SIG*` numbers, `SIGRTMIN`, `SIGRTMAX`, `SA_*`, `MINSIGSTKSZ`, `SIGSTKSZ`, `_NSIG`, `_NSIG_WORDS`, `old_sigset_t`, `sigset_t`, and `stack_t`. Control flow: signal syscalls and libc use these constants to install handlers, block masks, and alt stacks. State and persistence: signal masks and altstack settings persist per task; constants are permanent ABI. Dependencies and integration points: generic signal definitions, `sigcontext.h`, `ucontext.h`, and PA-RISC signal entry/return code. Risks: PA-RISC signal numbering differs from some architectures; changing it breaks all userspace signal handling. Test signals: POSIX signal tests, realtime signal queueing, sigaltstack, mask manipulation, and compat signal ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/signal.h -->
