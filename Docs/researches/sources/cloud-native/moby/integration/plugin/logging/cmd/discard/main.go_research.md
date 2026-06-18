# sources/cloud-native/moby/integration/plugin/logging/cmd/discard/main.go

## Purpose
Entry point for the discard logging plugin fixture. It exposes the handlers from `driver.go` over Docker's expected plugin Unix socket.

## Important APIs, Types, And Functions
`main` listens on `/run/docker/plugins/plugin.sock`, creates an HTTP mux, calls `handle(mux)`, constructs `http.Server` with `ReadHeaderTimeout`, and serves forever.

## Control Flow
Startup either panics on socket listen failure or blocks serving log driver endpoints.

## State And Persistence Behavior
No state beyond the driver state registered by `handle`.

## Dependencies And Integration Points
Depends on Unix sockets and the companion driver implementation. Used by plugin fixture build helpers in logging tests.

## Risks
Linux/Unix-socket specific. No graceful shutdown handling is implemented because test plugin lifecycle is managed by the daemon/plugin fixture.

## Test Signals
Indirectly verified by logging read tests that enable the built plugin and use it as a log driver.
