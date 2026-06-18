# sources/cloud-native/cri-o/test/checkseccomp/checkseccomp.go

## Purpose
Host capability probe for seccomp support used by tests.

## Important APIs, Types, And Functions
`main()` uses `unix.Prctl` with `PR_GET_SECCOMP` and `PR_SET_SECCOMP`/`SECCOMP_MODE_FILTER`.

## Control Flow
The helper first checks whether `PR_GET_SECCOMP` avoids `EINVAL`, then checks whether attempting filter mode fails with `EINVAL`. If both kernel capabilities appear present, exits 0; otherwise exits 1.

## State And Persistence
No persistence. The `PR_SET_SECCOMP` call is passed a nil filter pointer and is used as a capability probe.

## Dependencies And Integration Points
Referenced by integration helpers as `CHECKSECCOMP_BINARY`.

## Risks And Test Signals
Seccomp probing is kernel and permission sensitive. The code intentionally treats `EINVAL` as lack of support; other errors can still lead to success depending on the first check.
