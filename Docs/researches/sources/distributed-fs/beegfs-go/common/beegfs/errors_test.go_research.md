# sources/distributed-fs/beegfs-go/common/beegfs/errors_test.go

## Purpose
This Go test verifies `OpsErr` interoperability with standard Go error matching.

## Important Tests
`TestErrMappings` checks that `OpsErr_PATHNOTEXISTS` matches `syscall.ENOENT`, `fs.ErrNotExist`, and `os.ErrNotExist`; `OpsErr_INUSE` matches `syscall.EBUSY`; `OpsErr_WOULDBLOCK` and `OpsErr_AGAIN` match EAGAIN/EWOULDBLOCK; reverse matching from `os.ErrNotExist` to `OpsErr_PATHNOTEXISTS` is false; and unrelated permission matching is false.

## Dependencies and Integration
The test uses Go `errors`, `io/fs`, `os`, `syscall`, and `stretchr/testify/assert`.

## Signals and Gaps
The suite confirms the most important sentinel behavior. It does not exhaustively verify every `opsToSys` mapping or string output for all codes.
