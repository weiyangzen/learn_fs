# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/listener.go

This file starts the HTTP endpoint used by Prometheus scraping. `endpointPromMetrics` is `/v1/metrics`. `trapClosedConnErr` normalizes nil and `net.ErrClosed` to nil. `NewMetricsHTTPListenerServer` validates the address, registers `promhttp.HandlerFor(registry.Registry, ...)` on the default HTTP mux, binds a TCP listener, and serves it in a goroutine.

State includes the global default HTTP mux registration and the listener goroutine. Integration points are the custom registry, Prometheus client library, snapshotter configuration that supplies the address, and process lifecycle. The function returns after listener creation, not after serve completion.

Risks include using the package-global `http.Handle`, which can conflict if multiple metric servers or tests register the same path; no shutdown handle is returned; listener errors after startup are only logged; and address validation only checks empty string. There are no direct tests for listener startup or handler output.
