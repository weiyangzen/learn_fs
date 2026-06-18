# sources/cloud-native/containerd/internal/pprof/plugin.go

## Purpose
Registers containerd's pprof and expvar HTTP handler plugin.

## Important APIs, Types, And Functions
`init` registers a plugin of type `plugins.HTTPHandler` with ID `pprof`. `newHandler` returns an `http.Server` with `/debug/vars` and standard `/debug/pprof` endpoints.

## Control Flow
Plugin initialization constructs a serve mux and returns it to the plugin system. The server sets `ReadHeaderTimeout` to five minutes.

## State And Persistence
Registers global plugin metadata at init. Runtime state is the HTTP server and handlers.

## Dependencies And Integration Points
Uses expvar, net/http/pprof, containerd plugin registry, and plugin type constants.

## Risks
Exposes profiling and expvar data wherever the containerd HTTP handler plugin is served, so endpoint access control is important outside this file.

## Test Signals
No direct tests in this subset. Plugin registration is covered by containerd plugin initialization integration.
