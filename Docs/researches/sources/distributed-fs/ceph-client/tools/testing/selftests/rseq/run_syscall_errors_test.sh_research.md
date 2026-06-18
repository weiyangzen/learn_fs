# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/run_syscall_errors_test.sh

Purpose: `run_syscall_errors_test.sh` executes the syscall error validation binary in an environment where glibc does not pre-register rseq.

Important APIs, types, and functions: it sets `GLIBC_TUNABLES="${GLIBC_TUNABLES:-}:glibc.pthread.rseq=0"` and runs `./syscall_errors_test`.

Control flow: straight-line shell wrapper. The child program owns the validation logic and exit status.

State and persistence: no files are written. Only child environment state is adjusted.

Dependencies and integration points: depends on `syscall_errors_test` being built and on the glibc tunable being available. It integrates the C syscall validation into kselftest runners.

Risks and test signals: if libc already owns rseq despite the tunable, expected EBUSY/EINVAL sequences may differ. The test signal is a zero exit status from `syscall_errors_test`.
