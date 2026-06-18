<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/signal.h

Purpose: Defines x86 signal numbers, signal action layout, signal stack type, signal stack sizes, and the x86 `SA_RESTORER` flag.

Important APIs/types/functions: `NSIG`, `sigset_t`, `SIG*` constants, `SIGRTMIN`, `SIGRTMAX`, `SA_RESTORER`, `MINSIGSTKSZ`, `SIGSTKSZ`, i386 and x86_64 userspace `struct sigaction`, and `stack_t`.

Control flow: Userspace registers signal handlers with `sigaction`; kernel signal delivery uses the ABI layout and optional restorer pointer, and alternate signal stack syscalls use `stack_t`.

State and persistence behavior: Signal dispositions and blocked masks persist per task; alternate stacks persist per thread. The header defines the serialized ABI only.

Dependencies and integration points: Depends on Linux UAPI types/compiler and generic signal defs. Integrates with libc, signal syscalls, rt signals, sigreturn trampolines, alternate stacks, ptrace, and i386 compatibility.

Risks and test signals: Risks include mismatched `struct sigaction` between i386 and x86_64, restorer handling bugs, and too-small stack assumptions for modern xstate. Test signal delivery, SA_RESTORER, alternate stacks, real-time signals, i386 compat, and libc header compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/signal.h -->
