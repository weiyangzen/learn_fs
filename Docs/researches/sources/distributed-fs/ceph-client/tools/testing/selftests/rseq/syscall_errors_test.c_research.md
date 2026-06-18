# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/syscall_errors_test.c

Purpose: `syscall_errors_test.c` verifies expected `errno` behavior for invalid and duplicate `rseq` syscall operations.

Important APIs, types, and functions: it defines `sys_rseq()` and `main()`. It uses `rseq_get_abi()`, `rseq_available()`, `RSEQ_SIG`, `RSEQ_ABI_FLAG_UNREGISTER`, and direct `syscall(__NR_rseq, ...)`.

Control flow: `main()` skips to error if the syscall is unavailable, then exercises invalid registration flags, unaligned ABI address, invalid size, optionally invalid address on most 64-bit builds, successful registration, double registration, unregister with wrong signature, successful unregister, and double unregister. Each step captures `errno`, prints a diagnostic, and fails if the observed errno differs from the expected value.

State and persistence: state is the current thread's registration status and local errno snapshots. No persistent files are written.

Dependencies and integration points: depends on glibc `strerrorname_np()`, syscall availability, and the local rseq ABI allocation from `rseq.c`. `run_syscall_errors_test.sh` disables glibc rseq ownership before invoking it.

Risks and test signals: architecture-specific address-space behavior is handled by skipping the EFAULT invalid-address test on 32-bit userspace and s390 alternate address-space cases. A zero exit means all expected syscall errors matched.
