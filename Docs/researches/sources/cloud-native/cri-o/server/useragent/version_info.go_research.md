# sources/cloud-native/cri-o/server/useragent/version_info.go

## Purpose
Utility for formatting validated product/version tokens into a User-Agent header suffix.

## Important APIs, Types, And Functions
`VersionInfo` stores `Name` and `Version`. `(*VersionInfo).isValid()` rejects spaces, tabs, carriage returns, newlines, and `/` in either field. `AppendVersions(base string, versions ...VersionInfo)` appends valid `name/version` tokens to an optional base string.

## Control Flow
With no versions, returns `base` unchanged. With versions, initializes an output slice with base when non-empty, skips invalid entries, and joins tokens with spaces.

## State And Persistence
Pure string transformation; no state or persistence.

## Dependencies And Integration Points
Used by `useragent.Get` and can be reused by other CRI-O HTTP clients needing RFC-friendly product tokens.

## Risks And Test Signals
Validation is intentionally narrow and does not reject empty name/version strings, non-ASCII, or other HTTP token separators. Tests cover base append behavior and newline invalidation.
