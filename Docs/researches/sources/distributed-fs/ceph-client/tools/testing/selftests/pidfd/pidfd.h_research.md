# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd.h

Purpose: shared pidfd test header providing fallback constants, pidfs ioctl definitions, `struct pidfd_info`, syscall wrappers, child creation, wait helpers, and EINTR-safe I/O helpers.

Important APIs/types: defines fallback `FD_PIDFS_ROOT`, `P_PIDFD`, clone flags, pidfd syscall numbers, `PIDFD_NONBLOCK`, `PIDFD_THREAD`, self pidfd constants, `PIDFD_GET_*_NAMESPACE`, `PIDFD_GET_INFO`, `PIDFD_INFO_*`, coredump flags, and `struct pidfd_info`. Helpers include `sys_waitid()`, `wait_for_pid()`, `sys_pidfd_open()`, `sys_pidfd_send_signal()`, `sys_pidfd_getfd()`, `sys_memfd_create()`, `create_child()`, `read_nointr()`, `write_nointr()`, and `sys_execveat()`.

Control flow/integration: test files include this header to avoid dependence on newest system headers. `create_child()` uses `clone3()` with `CLONE_PIDFD` and optional flags, returning the child pid while storing the pidfd. `wait_for_pid()` loops on EINTR and reports non-exited children through kselftest messages.

State and persistence: no persistent state. Helpers create processes/fds or perform syscalls on caller request.

Dependencies/integration: depends on kselftest, clone3 selftest definitions, Linux syscall ABI, and pidfs ioctl ABI.

Risks: fallback constants must stay synchronized with kernel UAPI. Tests compiled against older libc headers rely heavily on these definitions; mismatches can cause false failures.

Test signals: helper failures usually surface as kselftest assertion failures or diagnostic messages in callers.
