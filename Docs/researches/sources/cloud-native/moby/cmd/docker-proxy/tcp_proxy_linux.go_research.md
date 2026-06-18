# sources/cloud-native/moby/cmd/docker-proxy/tcp_proxy_linux.go

## Purpose
Implements TCP forwarding for docker-proxy.

## APIs, Types, And Functions
`TCPProxy` stores frontend and backend TCP addresses. `NewTCPProxy`, `clientLoop`, `Run`, and `Close` implement the shared `Proxy` interface.

## Control Flow, State, And Integration
`Run` accepts TCP connections and starts a client goroutine per connection. `clientLoop` dials the backend and starts two `io.Copy` brokers, using `CloseRead` and `CloseWrite` to support half-close semantics before closing both ends.

## Risks And Test Signals
Risks include stalled goroutines, improper half-close behavior, backend dial failures, and listener close races. Integration is with Docker host-port publishing and TCP socket behavior.
