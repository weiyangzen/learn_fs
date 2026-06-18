# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/match_helpers_test.go

Purpose: focused tests for low-level match helpers and edge cases that broader match tests might obscure.

Important coverage: `prefixMatches` allows empty prefixes, accepts exact prefixes, rejects non-matching or shorter paths. `filterAllows` tests no-filter fast path, strict size greater-than and less-than boundaries, zero-size filter disabled behavior, required tag presence, multi-tag AND behavior, and size+tag conjunction. Additional match cases cover nil/wrong event shapes, delay mismatch, no tag-sensitive predicate actions, unknown buckets, nil-event prefix-only `MatchPath`, event-provided filter gates, bucket scoping, AbortMPU requiring MPU init, and expired delete marker requiring marker+latest.

Control flow/state: uses compiled snapshots from helper builders so internal indexes are realistic. No persistent state.

Dependencies/integration: imports lifecycle rules, action keys, and testify. It documents router expectations for the event-driven matching surface.

Risks/gaps: tests directly use package internals, which is desirable for helper contracts but can require updates when implementation is intentionally refactored.

Test signals: excellent boundary coverage for filter semantics; catches off-by-one size filter changes, cross-bucket leakage, and shape-gate regressions.
