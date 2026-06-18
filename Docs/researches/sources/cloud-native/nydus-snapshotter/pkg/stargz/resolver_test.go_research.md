# sources/cloud-native/nydus-snapshotter/pkg/stargz/resolver_test.go

## Purpose
Tests stargz resolver range-reading and TOC discovery with a mock transport resolver.

## Important APIs, Types, And Functions
`TestResolver_resolve`, `MockResolver.Resolve`, and `mockRoundTripper.RoundTrip`.

## Control Flow
The test creates a resolver with mock URL/transport, builds a keychain from base64 credentials, resolves a stargz blob, reads the last 47-byte footer, parses the TOC offset, reads the TOC gzip range, opens it as a tar stream, and asserts the first entry is `stargz.index.json`.

## State And Persistence
Reads fixture files `testdata/stargzfooter.bin` and `testdata/stargztoc.bin`. No writes.

## Dependencies And Integration Points
Exercises `parseFooter`, `Resolver.resolve`, range handling, auth keychain setup, and stargz TOC extraction expectations.

## Risks And Edge Cases
The mock returns success for unspecified requests, so negative HTTP status and malformed header cases are not covered. The fixture sizes encode one known stargz layout.

## Test Signals
Direct positive-path coverage for remote stargz TOC resolution and partial range reads.
