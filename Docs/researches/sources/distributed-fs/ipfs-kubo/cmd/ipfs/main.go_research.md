# sources/distributed-fs/ipfs-kubo/cmd/ipfs/main.go

## Purpose
This is the `ipfs` binary entrypoint.

## Important APIs, Types, And Functions
`main` calls `kubo.Start(kubo.BuildDefaultEnv)` and exits with the returned code.

## Control Flow
All CLI parsing, execution, and cleanup are delegated to `cmd/ipfs/kubo/start.go`.

## State And Persistence Behavior
It only sets the process exit code.

## Dependencies And Integration Points
It integrates the compiled binary with the Kubo CLI package.

## Risks And Test Signals
Risks are minimal; failures come from delegated startup. Signal is the binary invoking Kubo startup and returning correct exit codes.
