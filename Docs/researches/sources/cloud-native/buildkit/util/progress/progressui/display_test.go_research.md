<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/display_test.go -->
# sources/cloud-native/buildkit/util/progress/progressui/display_test.go

Purpose: table-driven unit tests for `mergeIntervals`, the time-interval normalization helper used by progress grouping and job duration display.

Important APIs and types: local helpers `mkinterval` and `mkOpenInterval` build `interval` values with concrete `time.Time` pointers. `TestMergeIntervals` exercises the unexported `mergeIntervals` function.

Control flow: each case passes a slice of intervals and asserts exact equality against the expected merged slice. Cases cover empty input, single intervals, nil-start filtering, duplicate/equal intervals, disjoint ranges, subsumed ranges, partial overlap chains, adjacent boundaries, open intervals, and a mixed complex case.

State and persistence: test-only in-memory data; no filesystem or environment state.

Dependencies and integration: uses `testing`, `time`, and `testify/require`. It directly validates the helper used by `vertexGroup.refresh`, `trace.displayInfo`, and text completion duration calculation.

Risks: tests do not exercise terminal rendering, progress-group aliasing, warning/log buffering, or rate limiting. They do protect a core invariant: open intervals consume later overlapping intervals and nil starts are omitted.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/display_test.go -->
