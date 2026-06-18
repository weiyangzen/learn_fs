# sources/control-plane/rook/pkg/util/exec/error_test.go

## Purpose
This file tests exit status extraction in the exec package.

## Important APIs, Types, and Functions
`TestExitStatus()` passes unknown errors, a synthetic `*exec.ExitError`, and `CephCLIError` wrappers to `ExitStatus()`.

## Control Flow, State, and Persistence
The test is table-driven and pure. The synthetic `os.ProcessState` returns status zero in this setup.

## Dependencies and Integration Points
It depends on Go `errors`, `os`, `os/exec`, and testing. It protects command-error handling used by Ceph wrappers.

## Risks
It does not cover `kexec.CodeExitError` or `syscall.Errno`, both supported by `ExitStatus()`. Synthetic `ProcessState` limits realism for nonzero exit codes.

## Test Signals
Signals include recursive status extraction through `CephCLIError` and false for unsupported error types.
