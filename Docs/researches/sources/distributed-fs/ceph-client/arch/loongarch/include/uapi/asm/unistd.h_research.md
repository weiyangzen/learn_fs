<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/unistd.h

Purpose: selects generated LoongArch syscall-number headers for userspace.
Important APIs and types: includes `bitsperlong.h` and either 32-bit or 64-bit generated syscall numbers.
Control flow: compile-time inclusion by libc, seccomp tools, and kernel syscall tables.
State and persistence: syscall numbers are stable UAPI.
Dependencies and integration: generated from syscall tables and consumed by libc, audit, seccomp, strace, and kernel syscall dispatch.
Risks and test signals: wrong generated header selection breaks every syscall user. Signals include headers_install, libc builds, syscall smoke tests, and strace decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/unistd.h -->
