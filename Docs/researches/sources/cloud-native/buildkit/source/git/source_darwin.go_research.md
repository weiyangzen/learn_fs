# sources/cloud-native/buildkit/source/git/source_darwin.go

## Purpose
Provides Darwin-specific process attributes for the Unix reexec wrapper used to run Git commands with BuildKit's expected umask and process-group behavior.

## Important APIs, Types, And Functions
- `reexecSysProcAttr` is a package-level `unix.SysProcAttr` with `Setpgid: true`.

## Control Flow
This file has no functions. On `unix && !linux` builds, `source_unix_nolinux.go` uses this variable when reexecing the actual Git process.

## State And Persistence
No persistent state. It only configures process spawning behavior.

## Dependencies And Integration Points
Depends on `golang.org/x/sys/unix` and is compiled only on Darwin. It integrates with `gitMain` in the non-Linux Unix helper.

## Risks And Edge Cases
Darwin lacks the FreeBSD `Pdeathsig` setting used in `source_freebsd.go`, so cancellation relies on process-group signal forwarding in the wrapper.

## Test Signals
Indirectly covered by non-Windows Git source tests when run on Darwin; no dedicated unit test targets this tiny platform shim.
