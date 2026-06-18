<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/set-exec.c -->
# sources/distributed-fs/ceph-client/samples/check-exec/set-exec.c

## Purpose
`set-exec.c` is a wrapper that sets check-exec-related securebits before executing another command. It is used to demonstrate file-execution restrictions and denial of interactive interpretation.

## Important APIs, Types, And Functions
`main()` uses `prctl(PR_GET_SECUREBITS)`, `prctl(PR_SET_SECUREBITS)`, `SECBIT_EXEC_RESTRICT_FILE`, `SECBIT_EXEC_RESTRICT_FILE_LOCKED`, `SECBIT_EXEC_DENY_INTERACTIVE`, `SECBIT_EXEC_DENY_INTERACTIVE_LOCKED`, and `execvpe()`.

## Control Flow
The program parses `-f` and/or `-i`, ORs the requested securebits and lock bits into the current mask, requires a following command, sets securebits if changed, and then executes the command with the original environment.

## State And Persistence
Securebits become persistent process credentials state and are inherited by the executed command. The wrapper process is replaced by `execvpe()` on success.

## Dependencies And Integration Points
It depends on kernel support for the check-exec securebits and generated UAPI headers. It integrates with `inc` and the sample scripts by launching them under policy.

## Risks And Edge Cases
Locked securebits cannot be undone by the child. Kernels without support return an error and the wrapper prints a hint. The wrapper requires at least one policy flag and a command.

## Test Signals
Running `set-exec -fi -- ./inc ...` should execute the command with both policies set; unsupported kernels should fail at `PR_SET_SECUREBITS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/set-exec.c -->
