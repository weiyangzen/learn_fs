# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-exec.c

Purpose: verifies that a suspended transaction does not survive `exec()`, and that post-exec TM startup is not reported as nested.

Important APIs/types/functions: `test_exec()` starts/suspends a transaction and calls `execl()` on its own path with `--child`; `after_exec()` starts a fresh transaction and checks `failure_is_nesting()`.

Control flow: parent mode skips if HTM is unavailable/synthetic, enters suspended TM, then replaces itself with the same binary. Child mode repeats a TM begin/suspend sequence and fails if the failure code indicates nesting from a stale pre-exec transaction.

State and persistence behavior: `path` stores `argv[0]`; process image replacement is the key state transition. No file state is changed.

Dependencies and integration points: uses `tm.h` failure-code helpers and kselftest harness only in parent mode.

Risks and test signals: `execl()` failure is a test failure. The child path returns directly rather than through `test_harness()`, which is intentional for exec mode.
