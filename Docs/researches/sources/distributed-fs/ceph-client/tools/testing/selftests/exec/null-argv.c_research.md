# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/null-argv.c

## Purpose
Regression test ensuring exec calls with null or empty argv are converted by the kernel into a single empty `argv[0]` rather than exposing `argc == 0`.

## Important APIs, Types, And Functions
Uses `fork`, `waitpid`, `execve`, kselftest helpers, and macro `FORK(exec)`. `check_result()` validates child exit status.

## Control Flow
When invoked with `argv[0]` already empty, it verifies `argc == 1` and exits success. Otherwise it prints a five-test plan and forks children to re-exec itself with `str`, `NULL`, and `{ NULL }` argv combinations, with null and inherited environments. Parent expects all children to exit 0.

## State And Persistence
No persistent state. Uses process recursion through `execve`.

## Dependencies And Integration Points
Standalone exec selftest built by the exec Makefile.

## Risks
Old kernels exposing `argc == 0` fail early. The test assumes the current executable path in `argv[0]` is usable for re-exec.

## Test Signals
Five pass results indicate all null/empty argv forms became `argc == 1` with empty `argv[0]`.
