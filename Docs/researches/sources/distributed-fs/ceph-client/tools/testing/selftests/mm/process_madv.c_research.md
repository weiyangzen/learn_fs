# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/process_madv.c

Purpose: validates `process_madvise(2)` behavior for self-targeted non-contiguous ranges, remote `MADV_COLLAPSE`, exited pidfds, bad pidfds, invalid vector lengths, and invalid flags.

Important APIs and functions: `sys_process_madvise()` wraps `__NR_process_madvise`; the fixture tracks `PIDFD_SELF`, child PID, and remote pidfd. Tests use `mmap()`, `pidfd_open`, pipes for child address handoff, `MADV_DONTNEED`, and `MADV_COLLAPSE`.

Control flow and state: each harness test allocates or forks as needed; parent teardown kills live children and closes pidfds. The remote collapse test forks a child that faults a hugepage-sized region and pauses while the parent advises it.

Dependencies and risks: depends on pidfd support, process_madvise permissions, PMD-size discovery, and `vm_util.h`. Success is exact byte counts or expected `ESRCH`, `EBADF`, and `EINVAL`. Remote collapse validates return semantics, not final hugepage state.
