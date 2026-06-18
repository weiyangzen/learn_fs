# sources/distributed-fs/ipfs-kubo/core/corehttp/logs.go

## Purpose
Adds a `/logs` HTTP endpoint that streams live go-log output to connected clients.

## Important APIs, Types, and Functions
The only entry point is `LogOption`, which registers an HTTP handler using `logging.NewPipeReader`, `bufio.Reader`, response writes, and optional flushing.

## Control Flow and State
On each request, the handler creates a log pipe reader, starts a cancellation goroutine watching request cancellation, node shutdown, or reader completion, then streams newline-delimited log messages to the response until read/write fails. It closes the pipe reader to unblock reads when the client disconnects.

## Dependencies and Integration Points
Depends on `go-log/v2`, `core.IpfsNode.Context`, and the core HTTP serve option interface. It integrates with API HTTP serving and exposes process log state to remote API clients.

## Risks and Test Signals
Risks include long-lived goroutines on stalled clients, writing an HTTP error after partial streaming, leaking log readers, and exposing sensitive logs if the API endpoint is reachable broadly. Test signals should cover client cancellation, node shutdown, flushing behavior, and authorization/binding assumptions at the HTTP API layer.
