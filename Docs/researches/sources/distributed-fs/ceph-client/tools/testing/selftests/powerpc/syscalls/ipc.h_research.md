# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/syscalls/ipc.h

Purpose: declarative list of IPC syscall numbers used twice by `ipc_unmuxed.c` to generate and run tests.

Important APIs/types/functions: conditionally invokes `DO_TEST(name, __NR_name)` for SysV semaphore, message queue, and shared memory calls when each syscall number is defined.

Control flow: no standalone flow; including file behavior is defined by the current `DO_TEST` macro.

State and persistence behavior: none.

Dependencies and integration points: included by `ipc_unmuxed.c` first to generate functions and again to execute them.

Risks and test signals: if built with old headers defining none of the syscalls, the caller skips rather than falsely passing.
