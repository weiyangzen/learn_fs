<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/metrics/plugin_unix.go -->
# sources/cloud-native/moby/daemon/internal/metrics/plugin_unix.go

Purpose: enables metrics collector plugins on Unix by exposing the daemon metrics endpoint on a Unix socket and notifying plugin lifecycle hooks.

Important APIs and types: `Plugin`, `metricsPluginAdapter`, `makePluginAdapter`, `RegisterPlugin`, `CleanupPlugin`, package variable `listener`, and helper `listen`.

Control flow: `RegisterPlugin` creates the Unix listener, registers a runtime option that bind-mounts the metrics socket into plugins, and registers a handler that looks up a metrics plugin and calls `StartMetrics`. `CleanupPlugin` concurrently calls `StopMetrics` for all managed metrics plugins and closes the listener. `listen` serves `/metrics` with `gometrics.Handler`.

State and persistence: creates/removes a Unix socket path and stores a package-level listener. Plugin state lives outside this package.

Dependencies and integration: integrates daemon plugin store, Docker plugin client calls, OCI spec mount mutation, HTTP server, and go-metrics.

Risks: package-level listener means only one active socket is expected. Cleanup logs plugin stop failures but continues. The metrics socket is bind-mounted read-only, but plugins can scrape sensitive daemon metrics.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/metrics/plugin_unix.go -->
