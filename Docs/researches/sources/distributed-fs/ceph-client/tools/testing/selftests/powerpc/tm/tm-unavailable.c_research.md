# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-unavailable.c

Purpose: verifies FP, VEC, and VSX unavailable exceptions inside transactions do not corrupt checkpointed FP/VEC register state across all MSR.FP/MSR.VEC pre-touch combinations.

Important APIs/types/functions: `struct Flags`, `expecting_failure()`, `is_failure()`, `tm_una_ping()`, `tm_una_pong()`, `test_fp_vec()`, and `tm_unavailable_test()`.

Control flow: a background pong thread yields on one CPU. For each unavailable exception type, the test runs ping cases with FP/VEC pre-touched or not. Inline assembly primes vs0/vs32 expected values, optionally enables FP/VEC, begins a transaction, executes the target unavailable instruction, captures CR and vector values, and validates expected failure cause plus register integrity.

State and persistence behavior: global `flags` carries selected case and accumulated result. Threads are CPU-affined; FP/VEC/VSX register state is local to the test thread.

Dependencies and integration points: requires real HTM, pthreads, ppc64, VSX, and no optimization assumptions (`-O0`) per Makefile.

Risks and test signals: retries tolerate reschedule/KVM aborts. Failure prints unexpected cause or corrupted FP/VEC values and exits nonzero; timeout is extended to 220 seconds.
