<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/exporter_test.go -->
## sources/cloud-native/buildkit/solver/exporter_test.go

Purpose: validates deterministic cache record ranking used by cache export selection.

Important APIs and types: `TestCompareCacheRecord` constructs records with equal, newer, older timestamps and different priorities, includes nil entries, then sorts with `compareCacheRecord`.

Control flow: the expected order is newest first, then lower priority for equal timestamps, then older records, with nil records last.

State and dependencies: test-only; depends on `slices`, `testing`, and `time`.

Integration points: protects `getBestResult` and the first record selected by `exporter.ExportTo` when multiple cache records are available.

Risks and test signals: useful but narrow. It does not exercise backlink recursion, remote resolution, compression variants, dependency validation, or target `Add` behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/exporter_test.go -->
