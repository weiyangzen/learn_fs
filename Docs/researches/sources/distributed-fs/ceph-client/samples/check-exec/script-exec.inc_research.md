<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/script-exec.inc -->
# sources/distributed-fs/ceph-client/samples/check-exec/script-exec.inc

## Purpose
`script-exec.inc` is a minimal executable script for the `inc` interpreter that increments the default counter once.

## Important APIs, Types, And Functions
It uses the shebang `#!/usr/bin/env inc` and a single `+` command.

## Control Flow
Execution invokes `inc`, which starts its counter at zero, processes `+`, increments to one, and prints `1`.

## State And Persistence
State is limited to the transient interpreter counter.

## Dependencies And Integration Points
It depends on `inc` in `PATH` and is used to exercise allowed executable-file interpretation under check-exec policy.

## Risks And Edge Cases
If the file lacks execute permission or file execution is restricted, the interpreter's `AT_EXECVE_CHECK` path can reject it.

## Test Signals
Executing the script under allowed policy should print `1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/script-exec.inc -->
