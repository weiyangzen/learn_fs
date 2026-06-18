# sources/cloud-native/cri-o/internal/runtimehandlerhooks/gomaxprocs_hooks_linux.go

Purpose: injects `GOMAXPROCS` into selected container OCI specs to improve Go workload behavior for burstable and best-effort pods without CPU limits.

Important APIs/types/functions: `GomaxprocsHooks`, `PreCreate`, no-op `PreStart`/`PreStop`/`PostStop`, `calculateGOMAXPROCS`, and `injectGOMAXPROCS`.

Control flow: `PreCreate` skips when the sandbox has the skip annotation, when the cgroup parent is not burstable/besteffort, or when CPU quota is set. It reads CPU shares, calculates a doubled rounded-up CPU request with a fallback floor, and adds `GOMAXPROCS` unless already present.

State and persistence behavior: mutates only the OCI spec generator's process environment.

Dependencies and integration points: integrates with sandbox annotations/cgroup parent, OCI generator, CRI-O annotation constants, and `HooksRetriever` when `MinInjectedGOMAXPROCS` is configured.

Risks: cgroup-parent string matching is heuristic. Injecting can override future runtime/container defaults if skip conditions are wrong. CPU shares of zero still result in at least the fallback/one.

Test signals: unit tests cover env injection/skipping and CPU-share-to-GOMAXPROCS calculations across best-effort, fractional, and large CPU requests.
