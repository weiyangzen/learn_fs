# Research: sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/canonical_test.go

## sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/canonical_test.go

Purpose: unit tests for conversion from lifecycle XML to canonical lifecycle engine rules.

Important tests: `TestLifecycleToCanonical_TopLevelPrefix`, `_FilterPrefix`, `_FilterTagAndSize`, and `_SingleTagFilter` cover filter flattening. `TestLifecycleToCanonical_MultipleActions` ensures expiration, noncurrent expiration, and abort-MPU actions all populate one canonical rule. `TestLifecycleToCanonical_ExpirationDate` and `_ExpiredObjectDeleteMarker` cover alternate expiration fields. `_DisabledRulePreserved` keeps status unchanged. `_NilSafe` and `_EmptyRules` cover edge cases. `parseLifecycle` uses the public `Parse` entrypoint.

State and dependencies: pure XML strings, reflection for tag-map equality, and time parsing. Integration points are lifecycle XML handlers and downstream rule compilation. Risks covered include dropping actions when multiple are present and misrepresenting filters. Test signal is broad for currently mapped canonical fields; transition mapping remains outside these assertions.
