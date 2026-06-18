# sources/distributed-fs/beegfs-go/common/registry/capability_test.go

Purpose: validates feature support checks for `ComponentRegistry`, including nested subfeature trees.

Important tests are `TestRequireFeatureSupportMatrix`, `TestRequireFeature`, and `TestRequireFeatures`. They construct in-memory registries with plain features, nested child/grandchild features, and unused features.

Control flow is table-driven. Single-feature tests call `RequireFeature(feature, sub...)` and assert success or `ErrUnsupportedFeature`. Multi-feature tests pass maps of required `flex.Feature` trees to `RequireFeatures` and verify recursive matching behavior.

State behavior is limited to immutable test registry maps. Persistence and remote RPC retrieval are outside this file.

Dependencies include `testing`, `testify/assert`, and protobuf `flex`. Integration point is the public feature validation API consumed by registry cache and callers.

Risks: tests do not verify clone isolation from `NewComponentRegistry` or `GetCapabilities`, build-info formatting, nil build-info fallback, malformed `GetCapabilities` responses, or gRPC error translation. One test name has a typo (`supported nexted`) but behavior is clear.

Test signals: good coverage of the recursive feature matrix and sentinel wrapping for unsupported features.
