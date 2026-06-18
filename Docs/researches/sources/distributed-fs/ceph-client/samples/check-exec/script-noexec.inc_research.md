<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/script-noexec.inc -->
# sources/distributed-fs/ceph-client/samples/check-exec/script-noexec.inc

## Purpose
`script-noexec.inc` is a minimal inc script intended to represent a non-executable or restricted script case in check-exec testing.

## Important APIs, Types, And Functions
It has the same `/usr/bin/env inc` shebang and single `+` command as the executable variant.

## Control Flow
If interpreted by `inc`, it increments the default counter and prints `1`; under restrictive file-exec policy it is expected to be denied when file permissions or policy mark it as not executable.

## State And Persistence
Only the interpreter's transient counter is used.

## Dependencies And Integration Points
It depends on external file mode or test harness setup to distinguish it from `script-exec.inc`. It integrates with the kernel check-exec examples.

## Risks And Edge Cases
The source contents alone do not enforce non-executable behavior; tests must set file permissions or invoke the right policy. If made executable, it behaves like `script-exec.inc`.

## Test Signals
Allowed interpretation prints `1`; restrictive file-exec tests should reject it when permissions/policy indicate non-executable input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/script-noexec.inc -->
