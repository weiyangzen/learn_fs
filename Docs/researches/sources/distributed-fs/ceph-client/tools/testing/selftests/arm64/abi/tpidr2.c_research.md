# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/tpidr2.c

Purpose: nolibc arm64 selftest for TPIDR2 behavior across default state, read/write, scheduling, fork, and clone-with-CLONE_VM.

Important APIs/types/functions: `set_tpidr2()`/`get_tpidr2()` access system register `S3_3_C13_C0_5`; tests `default_value()`, `write_read()`, `write_sleep_read()`, `write_fork_read()`, `write_clone_read()`; raw `sys_clone()` wrapper; `main()` gates on `/proc/sys/abi/sme_default_vector_length`.

Control flow: if SME support appears present via proc sysctl, plan five tests. The fork test expects child to inherit parent TPIDR2 then change its own; the clone-VM test expects child to start with zero while parent remains unchanged. Without SME support, all tests are skipped.

State and persistence: manipulates TPIDR2 register state in current process/children and allocates an 8 MiB clone stack. No files are written.

Dependencies/integration: built statically with nolibc; depends on SME/TPIDR2 kernel ABI, wait/clone syscalls, kselftest.

Risks and test signals: process/thread semantics are subtle; wrong child exit status maps to test failure. The clone stack is not freed on parent success path, acceptable for process exit.
