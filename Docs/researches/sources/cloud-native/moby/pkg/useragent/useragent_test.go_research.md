# sources/cloud-native/moby/pkg/useragent/useragent_test.go

Purpose: unit tests for user-agent version validation and formatting.

APIs and flow: `TestVersionInfo` checks valid name/version and empty field rejection. `TestAppendVersions` verifies base plus three version tokens format as space-separated `product/version` entries.

State and dependencies: pure in-memory tests with stdlib testing only.

Integration points: protects the public formatting contract used by HTTP callers.

Risks and signals: tests do not cover whitespace or slash stop characters, empty base behavior, or skipped invalid entries in `AppendVersions`.
