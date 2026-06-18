# sources/distributed-fs/ceph-client/tools/testing/selftests/kcmp/kcmp_test.c

`kcmp_test.c` smoke-tests `kcmp(2)` resource comparisons between a parent and child process, including the epoll target-fd comparison mode.

Important APIs are `syscall(__NR_kcmp)`, `KCMP_FILE`, `KCMP_FILES`, `KCMP_VM`, `KCMP_FS`, `KCMP_SIGHAND`, `KCMP_IO`, `KCMP_SYSVSEM`, `KCMP_EPOLL_TFD`, `struct kcmp_epoll_slot`, `pipe()`, `epoll_create1()`, `epoll_ctl()`, `dup2()`, `fork()`, and kselftest counters. `sys_kcmp()` is the local syscall wrapper.

The parent creates `kcmp-test-file`, a pipe, an epoll instance, and a duplicated fd number 64, then forks. The child opens the same path independently, prints sample comparison values, and runs three planned checks: same file fd compares equal, a process compared with itself has the same VM, and `KCMP_EPOLL_TFD` finds the duplicated pipe fd in the epoll set. The parent waits for the child.

State consists of inherited file descriptors, epoll interest entries, process resources, and the temporary file. Dependencies are the `kcmp` syscall, epoll, fork, and ptrace/security policy that permits comparison. A notable risk is that the parent does not propagate child failure status as its own exit code. The strongest signal is the child emitting three PASS results and exiting successfully.
