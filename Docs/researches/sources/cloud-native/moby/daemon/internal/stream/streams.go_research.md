# sources/cloud-native/moby/daemon/internal/stream/streams.go

## Purpose
Defines the daemon stream `Config` abstraction that groups stdin, stdout, stderr, and containerd `DirectIO` copying for container processes.

## Important APIs, Types, And Functions
`Config` owns unbuffered stdout/stderr broadcasters, stdin pipe ends, a `cio.DirectIO`, a wait group, and a closed flag. `NewConfig`, `Stdout`, `Stderr`, `Stdin`, `StdinPipe`, `StdoutPipe`, and `StderrPipe` expose stream endpoints. `NewInputPipes` creates an `io.Pipe`; `NewNopInputPipe` discards input. `CloseStreams`, `CopyToPipe`, and `Wait` manage shutdown and DirectIO copying.

## Control Flow
Output pipes create a `bytespipe.BytesPipe` and add it to the broadcaster. `CopyToPipe` starts goroutines from containerd stdout/stderr into broadcasters and stdin into containerd stdin. Errors after `CloseStreams` are suppressed; other copy/close failures are logged. `Wait` waits for output copy goroutines or cancels/closes DirectIO on context timeout.

## State And Persistence
Stream state is in memory. `closed` gates logging after teardown. The object mutates pipe fields and DirectIO references but does not checkpoint daemon state.

## Dependencies And Integration Points
Integrates containerd `cio.DirectIO`, `bytespipe`, `unbuffered`, and `pools.Copy`. It is the substrate used by attach and container runtime wiring.

## Risks And Test Signals
Blocking stdout/stderr consumers can stall broadcaster writes. Stdin copy is started with a raw goroutine rather than the wait group, so `Wait` mainly tracks output streams. Tests in this subset validate attach cancellation and broadcaster behavior indirectly.
