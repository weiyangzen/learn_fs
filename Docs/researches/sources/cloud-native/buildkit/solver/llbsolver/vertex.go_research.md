# sources/cloud-native/buildkit/solver/llbsolver/vertex.go

Purpose: loads protobuf LLB definitions into solver vertices, applies load options, validates capabilities/entitlements, evaluates source policy, normalizes platforms, and recomputes digests after policy/proxy mutations.

Important APIs/types/functions: `vertex`, `LoadOpt`, `WithValidateCaps`, `WithCacheSources`, `WithLinuxResourcesMetadata`, `NormalizeRuntimePlatforms`, `ValidateEntitlements`, `detectPrunedCacheID`, `Load`, `loadWithProxyNetwork`, `vertexOptions`, `newVertex`, `recomputeDigests`, `op`, `loadLLB`, `llbOpName`, and `fileOpName`.

Control flow: `loadLLB` unmarshals each definition op, records source ops, attaches metadata, optionally computes per-op proxy-network flags, evaluates source policies concurrently, recomputes digests recursively after mutations, strips the synthetic last vertex, and recursively materializes reachable vertices through a cache. `newVertex` applies load options, computes a display name, and resolves input edges. Entitlement validation checks exec host network, insecure security, and CDI device requests, including aliasing, auto-allow devices, and forbidden device reporting.

State/persistence: no durable state. It mutates in-memory protobuf ops during platform normalization, policy conversion, device filtering, proxy marking, and digest recomputation.

Dependencies/integration: solver vertex interfaces, protobuf LLB definitions, source policy evaluator, BuildKit API caps, entitlements, CDI manager, linux resources metadata, platform normalization, and op validation.

Risks: digest recomputation must include proxy-network marker and all mutated input digests to avoid stale cache keys. Synthetic last vertex assumptions are strict. Entitlement/device rewriting mutates requested device lists and must remain auditable.

Test signals: no direct tests in this subset, but vertex loading is exercised by most solve tests. Names for source/exec/file/build/merge/diff/passthrough ops affect progress UI and diagnostics.
