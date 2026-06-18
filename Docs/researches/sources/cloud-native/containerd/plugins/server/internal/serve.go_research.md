# sources/cloud-native/containerd/plugins/server/internal/serve.go

## Purpose
Provides shared asynchronous serving behavior for HTTP, gRPC, and TTRPC listeners.

## Important APIs, Types, And Functions
`Serve` logs the address, starts `serveFunc` in a goroutine, closes the listener on exit, and treats expected closed-server errors as non-fatal.

## Control Flow
The function captures listener address, logs, launches a goroutine, defers listener close, invokes the supplied serve function, and logs fatal only for unexpected errors not matching net/http/ttrpc closed conditions.

## State And Persistence
No persistence. Owns listener lifecycle after called.

## Dependencies And Integration Points
Used by debug, metrics, gRPC, and TTRPC server plugins. Depends on `net`, `http`, `ttrpc`, and logging.

## Risks
Unexpected serve errors call `Fatal`, terminating the daemon. Server start functions return after goroutine launch, so later bind/serve failures are asynchronous.

## Test Signals
No direct tests.
