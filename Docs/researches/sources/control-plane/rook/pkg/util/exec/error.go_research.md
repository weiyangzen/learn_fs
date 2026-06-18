# sources/control-plane/rook/pkg/util/exec/error.go

## Purpose
`exec/error.go` defines Ceph CLI error wrapping and exit-status extraction for exec failures.

## Important APIs, Types, and Functions
`CephCLIError` stores an underlying error and command output; its `Error()` returns the output text. `ExitStatus(err)` recognizes `*os/exec.ExitError`, `k8s.io/client-go/util/exec.CodeExitError`, nested `CephCLIError`, and `syscall.Errno`.

## Control Flow, State, and Persistence
The logic is pure. `CephCLIError` recursively delegates status extraction to its wrapped `err`.

## Dependencies and Integration Points
It depends on Go `os/exec`, `syscall`, and Kubernetes client-go exec errors. Ceph command wrappers can preserve output while still allowing callers to branch on exit code.

## Risks
`CephCLIError` fields are unexported, so only package-local constructors or literals can create rich values. `Error()` hides the underlying error. `ExitStatus()` returns zero with `false` for unknown errors, which callers must check carefully.

## Test Signals
`error_test.go` covers unknown errors, `ExitError`, nested `CephCLIError`, and `CephCLIError` with unknown wrapped errors.
