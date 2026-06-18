<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/signal.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/signal.h

Purpose: provides the Linux UAPI include wrapper for signal definitions, pulling in architecture-specific signal numbers and generic signal file-descriptor constants.

Important APIs, types, and functions: this header includes `asm/signal.h` and `asm/siginfo.h`; it does not define additional structs of its own in this copy.

Control flow: userspace and kernel UAPI consumers include `linux/signal.h` to obtain architecture signal numbers, sigset/sigaction-related types, and siginfo layouts through the architecture headers.

State and persistence behavior: no state is represented here. Signal dispositions, masks, and pending queues live in task structures and are defined by included ABI headers.

Dependencies and integration points: integrates with architecture UAPI signal headers, libc, syscall ABIs such as rt_sigaction/rt_sigprocmask, signalfd, ptrace, and seccomp trap delivery.

Risks and edge cases: behavior is architecture-dependent because the actual definitions come from `asm/*`. Include-order and namespace expectations matter for libc and kernel header users.

Test signals: architecture compile coverage, libc header compatibility, signal number/layout selftests, and cross-arch `siginfo_t`/sigset ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/signal.h -->
