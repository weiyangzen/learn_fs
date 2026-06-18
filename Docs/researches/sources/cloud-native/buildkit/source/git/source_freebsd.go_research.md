# sources/cloud-native/buildkit/source/git/source_freebsd.go

## Purpose
Provides FreeBSD-specific process attributes for the Unix Git reexec wrapper.

## Important APIs, Types, And Functions
- `reexecSysProcAttr` sets `Setpgid: true` and `Pdeathsig: unix.SIGTERM`.

## Control Flow
The non-Linux Unix wrapper imports this variable, attaches it to the child Git command, and then forwards process-group signals on cancellation.

## State And Persistence
No persisted data. The file affects runtime process lifecycle only.

## Dependencies And Integration Points
Depends on `golang.org/x/sys/unix` and integrates with `source_unix_nolinux.go`.

## Risks And Edge Cases
Correctness depends on FreeBSD honoring `Pdeathsig` and process-group signaling as expected; platform drift can leave Git children alive after BuildKit cancellation.

## Test Signals
Covered indirectly by Git source tests on FreeBSD; there is no file-local test.
