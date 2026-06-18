# sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/signal.go

## Purpose
This non-WASM utility handles OS interrupts for the CLI and daemon.

## Important APIs, Types, And Functions
`IntrHandler` stores a closing channel and wait group. `NewIntrHandler`, `Close`, and `Handle` manage signal listeners. `SetupInterruptHandler` returns an `io.Closer` plus a derived context canceled on first SIGHUP/SIGINT/SIGTERM and force-exits on subsequent signals.

## Control Flow
`Handle` registers signals, starts a goroutine counting received signals, and invokes a callback. The default callback cancels context on first signal and exits with `-1` on later signals.

## State And Persistence Behavior
It mutates process signal notification state and derived context cancellation. No files are written.

## Dependencies And Integration Points
It integrates `cmd/ipfs/kubo/start.go` startup and daemon graceful shutdown behavior with `os/signal` and `syscall`.

## Risks And Test Signals
Risks include repeated `Close` panic due to closing an already closed channel, hard exit on second signal bypassing defers, and no WASM build. Signals are first Ctrl-C triggering graceful shutdown text and second Ctrl-C terminating.
