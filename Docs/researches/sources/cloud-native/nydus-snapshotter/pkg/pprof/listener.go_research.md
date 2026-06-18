# Research: sources/cloud-native/nydus-snapshotter/pkg/pprof/listener.go

This file starts a lightweight pprof HTTP listener. `NewPprofHTTPListener` validates the address, registers selected pprof handlers on the default HTTP mux (`threadcreate`, `goroutine`, `allocs`, `block`, `mutex`, and `heap`), opens a TCP listener, and serves it in a goroutine.

State includes global HTTP mux registrations and a background server goroutine. Integration points are snapshotter diagnostics configuration, Go's standard pprof package, process networking, and logging. The function returns no listener or shutdown function, so lifecycle is tied to process lifetime.

Risks include use of global `http.Handle`, duplicate handler registration if called multiple times, no endpoint for the pprof index/profile/cmdline handlers, no authentication, no graceful shutdown, and address exposure depending on configuration. There are no direct tests in this subset.
