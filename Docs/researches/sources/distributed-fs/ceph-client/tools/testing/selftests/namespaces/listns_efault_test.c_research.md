## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/listns_efault_test.c

**Purpose:** Fault-injection and concurrency coverage for the `listns` syscall. It verifies invalid user buffers return the right errors and that namespace cleanup during iteration does not deadlock or corrupt active-reference handling.

**Important APIs and flow:** Tests construct `struct ns_id_req`, call `sys_listns()`, and build invalid buffers with `mmap()` followed by `munmap()` of the second page. Iterator children loop in `listns()` against a partially invalid buffer while the parent creates mount-namespace children with `create_child(..., CLONE_NEWNS)`, mounts tmpfs under `/tmp/test_mnt*`, then signals them to exit. Variants cover one-u64 partial fault, full invalid pointer `0xdeadbeef`, NULL buffer, late page-boundary fault after several writes, and mount-namespace-only cleanup.

**State, dependencies, integration:** State lives in child processes, mount namespaces, tmpfs mounts, pidfds, and the kernel namespace tree. It depends on `../pidfd/pidfd.h`, `wrappers.h`, mount permissions, and helper I/O wrappers. It integrates with `listns` copy-to-user error paths and RCU cleanup behavior.

**Risks and test signals:** The file intentionally races cleanup and faults, so environment limits on mount namespaces can cause child setup failures. The comments expect complete invalid buffers to return `EFAULT`; the partial-boundary comment mentions `EINVAL`, so kernel behavior must be checked against implementation. Passing tests primarily signal no hangs, correct `EFAULT` for invalid buffers, and safe cleanup when namespaces are destroyed during iteration.
