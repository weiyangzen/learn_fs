# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_fdinfo_test.c

Purpose: validates `/proc/self/fdinfo/<pidfd>` `Pid:` and `NSpid:` reporting for live children in nested/sibling PID namespaces and for dead processes.

Important APIs/types/functions: `struct error` tracks pass/fail/skip/error states; `clone_newns()` creates children with `CLONE_PIDFD | CLONE_NEWPID | CLONE_NEWNS` and optional `CLONE_NEWUSER`; `verify_fdinfo()` reads fdinfo lines and compares expected strings; `child_fdinfo_nspid_test()` remounts procfs and checks a sibling pidfd resolves to `NSpid:\t0`.

Control flow: `test_pidfd_fdinfo_nspid()` creates child A in a new PID/mount namespace, then child B in a sibling namespace with A's pidfd. Parent verifies A and B fdinfo show host pid and namespace pid 1; B verifies sibling pidfd NSpid is 0. Both children are joined and results reported. `test_pidfd_dead_fdinfo()` creates a child, waits for it to exit, then verifies `Pid:` and `NSpid:` become `-1` before closing the pidfd.

State and persistence: creates namespace children, maps stacks with `mmap()`, remounts procfs inside children, and reads procfs fdinfo. No persistent files.

Dependencies/integration: requires PID/user/mount namespaces, procfs, clone pidfd support, and kselftest output helpers.

Risks: exact fdinfo formatting is part of the tested ABI; formatting changes are failures. Restricted unshare/clone policies will block tests. Error handling uses custom states and fatal exits for infrastructure errors.

Test signals: two planned kselftest results: sibling namespace NSpid behavior and dead process fdinfo behavior.
