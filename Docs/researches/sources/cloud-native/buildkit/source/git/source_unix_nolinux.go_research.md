# sources/cloud-native/buildkit/source/git/source_unix_nolinux.go

## Purpose
Implements the non-Linux Unix strategy for running Git with a standard umask by reexecing BuildKit itself as a small wrapper process.

## Important APIs, Types, And Functions
- `gitCmd` names the reexec entrypoint.
- `init` registers `gitMain` with `reexec`.
- `gitMain` sets umask, starts the real Git command, forwards signals, mirrors exit status, and exits.
- `runWithStandardUmask` rewrites the command path/args to invoke the reexec wrapper and applies cancellation signaling.

## Control Flow
Callers invoke `runWithStandardUmask`; it starts `reexec.Self()` with `umask-git` plus original args. The wrapper sets `Umask(0022)`, starts Git with OS-specific `reexecSysProcAttr`, forwards incoming signals to the child or child process group, waits, and exits with the child status where possible. Cancellation sends SIGTERM to the process group and escalates to SIGKILL after 10 seconds.

## State And Persistence
No persisted state. It affects per-process umask and process-group lifecycle.

## Dependencies And Integration Points
Depends on `github.com/moby/sys/reexec`, `os/signal`, `syscall`, and `x/sys/unix`. It uses `reexecSysProcAttr` supplied by Darwin/FreeBSD platform files.

## Risks And Edge Cases
Exit status translation depends on platform `WaitStatus` type. Signal forwarding treats SIGKILL like a forwarded signal even though SIGKILL cannot be caught by the wrapper. Detached grandchildren may survive if not in the process group.

## Test Signals
Indirectly covered by the Git source tests on supported non-Linux Unix platforms; `source_unix_test.go` creates a hostile umask baseline to expose regressions.
