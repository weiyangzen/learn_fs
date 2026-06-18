# sources/cloud-native/containerd/plugins/server/debug/plugin.go

## Purpose
Registers the optional debug HTTP server exposing the internal pprof handler.

## Important APIs, Types, And Functions
`config` stores address/UID/GID. `server.Start` opens a Unix/local or TCP listener and serves the configured HTTP server. `Close` closes the HTTP server.

## Control Flow
Startup skips if no address is configured, looks up the `pprof` HTTP handler, returns a server wrapper, and logs/skips if pprof is not found. Start chooses local listener for local addresses or TCP for others and delegates serving to `internal.Serve`.

## State And Persistence
No persistence. It owns a listener and HTTP server lifecycle.

## Dependencies And Integration Points
Depends on HTTP handler plugins, internal pprof registration, `pkg/sys.GetLocalListener`, and shared server `internal.Serve`.

## Risks
Debug endpoints can expose sensitive process information; configuration must bind appropriately. Missing pprof handler skips the server.

## Test Signals
No direct tests in this subset.
