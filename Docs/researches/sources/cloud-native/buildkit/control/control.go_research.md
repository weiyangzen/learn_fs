# Research: sources/cloud-native/buildkit/control/control.go

Purpose: implements the BuildKit control gRPC service, bridging daemon subsystems to client APIs for solve, status, sessions, disk usage, prune, workers, info, history, trace export, content reads, and gateway forwarding.

Important APIs and flow: `Opt` injects session manager, worker controller, frontends, cache manager/resolvers, entitlements, trace collector, meter provider, history/cache/content stores, lease manager, history config, proxy network, GC callback, graceful stop, and provenance env. `NewController` creates a gateway forwarder, history queue, LLB solver, throttled GC/release callbacks, and optional trace forwarder. `Register` registers control, gateway, trace, and read-only content services. RPCs include `DiskUsage`, `Prune`, `Export`, history listen/update, legacy solve request translation, `Solve`, `Status`, `Session`, `ListWorkers`, and `Info`.

State and persistence: owns long-lived solver, history queue over Bolt DB, cache store, worker controller, trace forwarder, and content-store fallback namespace. It triggers GC and cache metadata release, mutates history records, and streams session connections.

Dependencies and integration: integrates gRPC APIs, LLB solver, workers, exporters, remote cache import/export, attestations/SBOM/provenance processors, entitlements, sessions, history, cache stores, tracing, content services, and BuildKit versioning.

Risks and test signals: solve is high-risk because it validates compatibility, deduplicates cache exports, configures exporters/processors, applies entitlements/source policy/proxy network, and handles sessions. `control_test.go` covers duplicate cache option handling and ignore-error parsing; broad behavior depends on integration tests.
