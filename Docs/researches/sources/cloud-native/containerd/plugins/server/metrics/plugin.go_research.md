# sources/cloud-native/containerd/plugins/server/metrics/plugin.go

## Purpose
Registers the optional HTTP metrics endpoint server.

## Important APIs, Types, And Functions
`config` stores the address. `server.Start` listens on TCP and serves `/v1/metrics`. `Close` closes the HTTP server.

## Control Flow
Startup skips without an address, builds an HTTP mux with `metrics.Handler`, and returns a server. Start opens a TCP listener, constructs `http.Server` with a long read-header timeout, and delegates serving to `internal.Serve`.

## State And Persistence
No persistence. Owns an HTTP server and TCP listener.

## Dependencies And Integration Points
Uses `docker/go-metrics` handler and shared server internal serving logic. Exposes metrics registered by GC, gRPC, and other packages.

## Risks
Metrics endpoint exposure depends on configured address. Read header timeout is intentionally long, so deployments should bind to trusted interfaces.

## Test Signals
No direct tests.
