# sources/cloud-native/moby/client/utils.go

## Purpose
Provides shared client helpers for invalid-parameter errors, ID trimming, API-version parsing, platform encoding, and context-cancelable response readers.

## APIs, Types, And Functions
Important items are `emptyIDError`, `InvalidParameter`, `trimID`, `parseAPIVersion`, `parseMajorMinor`, `encodePlatforms`, `encodePlatform`, `cancelReadCloser`, `newCancelReadCloser`, `Read`, and `Close`.

## Control Flow, State, And Integration
`trimID` rejects empty identifiers and trims `sha256:` prefixes to 64 hex characters. Platform helpers JSON-encode OCI platform slices for query/header use. `cancelReadCloser` starts a goroutine that closes the underlying reader on context cancellation and serializes reads/closes with a mutex.

## Risks And Test Signals
Risks include data races around stream close, overly aggressive ID trimming, and platform JSON compatibility. These helpers are integrated across many endpoint methods, so small regressions have broad client impact.
