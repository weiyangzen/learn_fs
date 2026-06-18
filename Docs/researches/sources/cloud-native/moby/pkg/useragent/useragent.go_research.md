# sources/cloud-native/moby/pkg/useragent/useragent.go

Purpose: compose product/version tokens into a User-Agent string.

APIs and flow: `VersionInfo` holds name/version. `isValid` rejects empty fields and whitespace, newline, carriage-return, tab, or slash. `AppendVersions` preserves a non-empty base and appends valid `name/version` tokens separated by spaces.

State and dependencies: pure string processing using stdlib `strings`; no persistence.

Integration points: useful for HTTP clients that need additive component version metadata.

Risks and tests: invalid entries are silently skipped, so missing user-agent fragments may hide bad input. Tests cover empty fields and nominal append behavior, but not stop-character rejection.
