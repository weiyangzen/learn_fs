# sources/cloud-native/cri-o/server/useragent/useragent.go

## Purpose
Builds the HTTP User-Agent string CRI-O uses to identify itself.

## Important APIs, Types, And Functions
`Get()` calls `internal/version.Get(false)`, normalizes the CRI-O version to the simplest `X.Y.Z` semver substring when present, and delegates formatting to `AppendVersions`. `versionRegex` captures the first three-component version string.

## Control Flow
Version lookup errors are wrapped. The generated User-Agent includes `cri-o`, `go`, `os`, and `arch` product/version tokens.

## State And Persistence
No persistence. Reads process build/runtime metadata via CRI-O version helpers and Go runtime constants.

## Dependencies And Integration Points
Used by outbound HTTP clients or registries that need CRI-O identity headers. Integrates with `version_info.go`.

## Risks And Test Signals
Regex normalization drops build suffixes and pre-release metadata, which is intentional for header compatibility but loses detail. Tests assert the returned string contains expected product tokens, not exact version formatting.
