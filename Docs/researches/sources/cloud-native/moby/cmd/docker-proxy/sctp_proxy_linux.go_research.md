# sources/cloud-native/moby/cmd/docker-proxy/sctp_proxy_linux.go

## Purpose
Implements SCTP forwarding for docker-proxy.

## APIs, Types, And Functions
`SCTPProxy` stores frontend listener and backend address. `NewSCTPProxy`, `clientLoop`, `Run`, and `Close` implement the `Proxy` interface using `github.com/ishidawataru/sctp`.

## Control Flow, State, And Integration
`Run` accepts SCTP clients and starts `clientLoop` goroutines. Each client loop dials the backend, wraps SCTP connections to preserve send/receive info, then runs bidirectional `io.Copy` brokers until either side finishes or the proxy closes.

## Risks And Test Signals
Risks include SCTP kernel/module availability, connection close semantics, goroutine cleanup, and error handling when backend dial fails. Integration is with published SCTP ports and the shared docker-proxy lifecycle.
