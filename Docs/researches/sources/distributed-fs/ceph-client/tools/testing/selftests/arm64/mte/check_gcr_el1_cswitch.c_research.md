<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_gcr_el1_cswitch.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_gcr_el1_cswitch.c

Purpose: stress test that GCR_EL1-related tag control state is restored correctly across context switches, forks, and threads.

Important APIs and functions: `execute_thread` chooses a random tag mask and sync/async TCF mode, repeatedly calls `prctl(PR_SET_TAGGED_ADDR_CTRL)` and compares `PR_GET_TAGGED_ADDR_CTRL`. `execute_test` starts five threads. `mte_gcr_fork_test` forks 1024 children, each running threaded checks.

Control flow: main runs MTE setup, plans one test, evaluates `mte_gcr_fork_test`, restores setup, and returns based on failure count.

State and persistence: no files; heavy process/thread state. Each thread has random desired tagged address control bits.

Dependencies and integration: depends on pthreads, MTE prctl ABI, shared MTE setup, and kselftest.

Risks: very high fork/thread count can be expensive. `pthread_join` writes a pointer return value into `int thread_data[]`, which is not portable and can truncate on 64-bit systems; current returned constants are small but the type mismatch is risky.

Test signals: one kselftest result; failure prints mismatched `prctl_set`/`prctl_get` values or `prctl` errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_gcr_el1_cswitch.c -->
