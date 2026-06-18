# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/ptrace.c

Purpose: tests arm64 ptrace ABI register sets for TLS/TPIDR values and hardware debug resource reporting.

Important APIs/types/functions: `have_sme()` checks `HWCAP2_SME`; `test_tpidr()` exercises `PTRACE_GETREGSET`/`SETREGSET` with `NT_ARM_TLS` for TPIDR and optional TPIDR2; `test_hw_debug()` reads `NT_ARM_HW_WATCH` and `NT_ARM_HW_BREAK`; `do_child()` requests tracing and stops; `do_parent()` waits, confirms stop signal, runs tests, and kills child.

Control flow: parent forks child. Child does `PTRACE_TRACEME` and raises SIGSTOP. Parent waits for the expected stop, then performs register-set tests on the stopped child and finally kills it. Main plans `EXPECTED_TESTS` and reports counts.

State and persistence: parent/child process state only; no files.

Dependencies/integration: ptrace, wait/signal APIs, arm64 regset constants, auxv, and kselftest.

Risks and test signals: if child exits unexpectedly, the test fails. TPIDR2 expectations vary with SME support: with SME it should round-trip, without SME it may read zero. Hardware debug arch field must be nonzero.
