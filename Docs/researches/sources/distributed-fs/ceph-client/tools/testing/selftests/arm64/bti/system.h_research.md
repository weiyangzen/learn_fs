# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/system.h

Purpose: freestanding type and syscall declarations for BTI tests.

Important APIs/types/functions: defines `size_t` and `ssize_t` from kernel types; includes errno/compiler/hwcap/ptrace/unistd UAPI; declares `syscall()`, `exit()`, and `write()`.

Control flow: no direct flow.

State and persistence: none.

Dependencies/integration: common header for BTI C files.

Risks and test signals: bypassing libc means all required types/constants must come from compatible kernel headers.
