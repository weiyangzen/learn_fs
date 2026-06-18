# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/syscalls/ipc_unmuxed.c

Purpose: verifies that powerpc exposes direct/unmuxed SysV IPC syscall numbers rather than returning ENOSYS.

Important APIs/types/functions: macro-generated `test_<name>()` functions call `syscall(_num, -1, 0, 0, 0, 0, 0)` and treat `errno == ENOSYS` as failure. `ipc_unmuxed()` runs all generated cases.

Control flow: the file includes `ipc.h` once to emit static test functions and once to execute them while counting tests. If no syscall numbers were available at build time, it skips.

State and persistence behavior: no persistent IPC objects are intentionally created because invalid arguments are supplied.

Dependencies and integration points: depends on kernel headers defining `__NR_*` and kselftest `FAIL_IF/SKIP_IF`.

Risks and test signals: this only checks syscall implementation presence, not semantic correctness. Unexpected errno values other than ENOSYS are accepted as proof the syscall exists.
