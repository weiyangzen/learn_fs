<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/index_test.go -->
## sources/cloud-native/buildkit/solver/index_test.go

Purpose: exercises edge index matching and cleanup across root and dependency-linked cache keys.

Important APIs and types: helper `checkEmpty` asserts both internal maps are empty. Tests create `edge` placeholders and cache keys using `NewCacheKey`, `testCacheKeyWithDeps`, and selectors.

Control flow: `TestIndexSimple` checks root-key collision and release cleanup. `TestIndexMultiLevelSimple` verifies dependency equivalence, selector changes, alternate dependency sets, merged key behavior, and that a later edge remains after the original is released. `TestIndexThreeLevels` verifies nested dependencies and low-level dependency mutation still match through linked IDs.

State and dependencies: test-only state is an in-memory `edgeIndex`. It depends on test helpers defined elsewhere in the solver package.

Integration points: gives confidence that scheduler deduplication can merge equivalent active graph edges without leaking index entries after job release.

Risks and test signals: solid coverage for index graph behavior, but no race test here; synchronization is covered by mutex use and broader scheduler tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/index_test.go -->
