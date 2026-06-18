# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/check-exec-tests.sh

## Purpose
KTAP shell suite for check-exec securebits/sample interpreter behavior. It verifies how executable-file restriction and denied interactive commands affect direct script execution, indirect interpreter execution, stdin, pipes, and `-c` arguments.

## Important APIs, Types, And Functions
Uses generated `inc`, `set-exec`, `script-exec.inc`, and `script-noexec.inc`. Helper functions are `exec_direct()`, `exec_indirect()`, `exec_stdin_reg()`, `exec_stdin_pipe()`, `exec_argument()`, `exec_interactive()`, and `ktap_test()`.

## Control Flow
It prints a KTAP plan of 28. It first tests default behavior, then runs the same execution shapes under `set-exec -f`, `set-exec -i`, and `set-exec -fi`, checking both exit status and expected output `1` for allowed cases.

## State And Persistence
No persistent state. It changes securebits only in subprocesses spawned through `set-exec`.

## Dependencies And Integration Points
Requires bash, KTAP helpers, libcap-built `set-exec`, sample `inc` interpreter, and kernel support for exec restriction securebits.

## Risks
Direct non-executable scripts return shell-specific `126`, and stderr is redirected away. The test assumes current directory in `PATH` for direct env execution.

## Test Signals
KTAP pass/fail lines identify allowed versus denied execution mode under each securebit combination, with exit status and output validation.
