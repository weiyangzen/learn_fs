# sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/memfd_test.c

Purpose: comprehensive memfd syscall/sealing/noexec/sysctl/sharing selftest, with optional hugetlbfs mode.

Important APIs/types/functions: wraps memfd creation, seal get/add, read/write/mmap/ftruncate/fallocate/chmod checks, `/proc/self/fd` reopening, `/proc/sys/vm/memfd_noexec`, `clone()` with `CLONE_NEWPID` and shared file-table flags, SysV semaphores for nested PID namespace synchronization, and constants `MFD_EXEC`, `MFD_NOEXEC_SEAL`, `F_SEAL_EXEC`, `F_SEAL_FUTURE_WRITE`, and `F_WX_SEALS`.

Control flow: helper assertions abort on unexpected behavior. `test_create()` validates name/flag constraints. Basic and seal tests verify `F_SEAL_SEAL`, write, future-write, shrink, grow, resize, and read-only mapping behavior. Exec/noexec tests validate file mode and chmod restrictions. Sysctl tests run inside PID namespaces to verify `memfd_noexec` values 0/1/2, inheritance, and child-lowering/no-raising rules. Sharing tests verify seals are shared through dup, mmap constraints, separate `/proc/self/fd` opens, forked children, and repeated under a shared file table.

State and persistence: mutates `/proc/sys/vm/memfd_noexec` inside PID namespaces, creates memfds, maps memory, and uses process/global state only. In hugetlbfs mode, memfd size and name prefix change and write paths skip unsupported operations.

Dependencies and integration points: memfd syscall, sealing support, PID namespaces for sysctl tests, `/proc`, hugetlb pages when requested, and kselftest wrappers.

Risks: abort-based style gives coarse failure localization. Root or namespace permissions may be needed for sysctl/PID namespace behavior. Some checks depend on current memfd noexec policy semantics.

Test signals: prints section banners and finishes with `memfd: DONE`; any failed assertion aborts.
