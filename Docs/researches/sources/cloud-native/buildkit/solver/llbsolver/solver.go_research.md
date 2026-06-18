# sources/cloud-native/buildkit/solver/llbsolver/solver.go

Purpose: top-level BuildKit LLB solver orchestration: constructs solver/bridge state, resolves worker ops, runs frontend/definition solves, records history, applies processors, exports results/cache, and exposes status.

Important APIs/types/functions: `ExporterRequest`, `RemoteCacheExporter`, `ResolveWorkerFunc`, `Opt`, `Solver`, `Processor`, `New`, `Close`, `resolver`, `bridge`, `Bridge`, `Solve`, `leaseManager`, `Status`, `defaultResolver`, `allWorkers`, `inBuilderContext`, and `notifyStarted`.

Control flow: `New` validates provenance env reserved keys, initializes metrics, provenance store, system sampler, and the underlying solver with a worker-backed resolve function. `Solve` normalizes gateway dockerfile requests, creates a job, starts usage sampling, sets entitlements/proxy/source policy/compatibility/session values, builds a provenance bridge, optionally registers a gateway forwarder, records history, solves via forwarder or bridge, captures frontend opts, evaluates all refs, attaches provenance, runs post-processors, converts refs to cache refs, creates a lease, augments session exporters, runs exporters, then finalizes image exporters and cache exporters in parallel.

State/persistence: stores long-lived solver dependencies, provenance store, metrics, and resource sampler. Per-solve state includes job values, leases, history records, result refs, descriptor refs, and releasers. History and cache/exporters persist outside this file.

Dependencies/integration: worker controller, BuildKit solver core, gateway forwarder, frontends, cache import/export, exporters, verifier, result conversion, entitlements, source policy, leases, progress, history, metrics, and processors such as provenance/SBOM.

Risks: cleanup ordering is critical for refs, descriptor refs, leases, gateway registration, and history finalization. Export finalization and cache export run concurrently and share content created by exporters. Provenance env reserved keys prevent users from overriding builtins.

Test signals: no direct tests in this subset; this is integration-heavy and validated by solve/export/status suites elsewhere.
