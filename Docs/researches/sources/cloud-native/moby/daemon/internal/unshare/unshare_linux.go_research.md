# sources/cloud-native/moby/daemon/internal/unshare/unshare_linux.go

## Purpose
Runs functions in a new goroutine locked to an OS thread whose Linux execution state has been unshared, while protecting the Go startup thread from namespace mutation.

## Important APIs, Types, And Functions
`init` locks the startup thread with `runtime.LockOSThread` to avoid `/proc/self` reflecting a mutated startup-thread namespace. `reversibleSetnsFlags` maps namespace flags that can be saved/restored with `setns`. `Go(flags, setupfn, fn)` locks a new goroutine to its thread, optionally saves namespace fds, calls `unix.Unshare`, runs setup, signals readiness, runs `fn`, and restores reversible namespaces when possible.

## Control Flow
`Go` determines whether all requested flags are reversible. For reversible flags it opens `/proc/self/task/<tid>/ns/<name>` fds and defers `Setns` restoration. If unshare or setup fails, the error is sent on `started` and `fn` is skipped. For irreversible state, the thread may be allowed to terminate after the goroutine returns.

## State And Persistence
Mutates per-thread kernel namespace and execution state. The caller observes only setup errors; `fn` runs asynchronously after readiness.

## Dependencies And Integration Points
Used by daemon code that needs isolated namespace operations without poisoning process-global `/proc/self` consumers such as mountinfo.

## Risks And Test Signals
The startup-thread lock has global runtime implications. Pdeathsig subprocesses may see early signals if the unshared thread exits. No tests are included here, so comments document much of the safety contract.
