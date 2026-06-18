# sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/server.go

Purpose: Provides the debug HTTP mux for the snapshotter daemon.

Important API: `debugServerMux` returns a new `http.ServeMux` with expvar and pprof handlers registered at `/debug/vars`, `/debug/pprof/`, `/debug/pprof/cmdline`, `/debug/pprof/profile`, `/debug/pprof/symbol`, and `/debug/pprof/trace`.

Control flow: The mux is constructed on demand and passed to `http.Serve` from `main.go` when `DebugAddress` is configured.

State and persistence: No persistent state. Handlers expose process runtime state from expvar and pprof.

Dependencies and integration: Uses standard library `expvar`, `net/http`, and `net/http/pprof`. Integrated by the daemon's debug listener on a local socket.

Risks: Debug endpoints expose profiling and process details; binding should remain restricted to the configured local/debug socket. No authentication is added here.

Test signals: No direct tests; behavior is simple standard library wiring.
