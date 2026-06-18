<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/index.go -->
## sources/cloud-native/buildkit/solver/index.go

Purpose: maintains an in-memory synchronous index of active solver edges so equivalent cache keys share work and merged edges can be discovered.

Important APIs and types: `edgeIndex`, `indexItem`, `newEdgeIndex`, `LoadOrStore`, `Release`, `releaseEdge`, `releaseLink`, `enforceLinked`, `enforceIndexID`, `getAllMatches`, and `isIgnoreCache`.

Control flow: `LoadOrStore` computes all matching IDs for a `CacheKey`; if an existing edge should win, it links the new key and returns the old edge. Otherwise it assigns an identity or matching ID, links dependencies, records the edge, and back-references it for release. Dependency matching intersects candidate IDs across input indexes and selectors. Release clears edge owners and recursively removes link-only items no longer referenced.

State and dependencies: state is fully in-memory under `mu`: ID-to-item map and edge-to-ID backrefs. `CacheKey.indexIDs` is mutated to cache index identities. Dependencies are BuildKit cache key/link types and `identity.NewID`.

Integration points: scheduler and solver state create edges through this index to deduplicate concurrent or repeated graph work.

Risks and test signals: correctness depends on recursive link cleanup and `IgnoreCache` asymmetry. `index_test.go` covers simple, multi-level, three-level, selector, dependency mutation, and release cleanup scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/index.go -->
