# sources/cloud-native/moby/integration/system/version_test.go

## Purpose
Tests server version API component metadata and rejection of clients older than the daemon's minimum supported API version.

## Important APIs, Types, And Functions
- `TestVersion` calls `ServerVersion`, finds the `Engine` component, and compares detail fields with top-level version and environment daemon info.
- `TestAPIClientVersionOldNotSupported` decrements the daemon minimum API minor version and expects a precise too-old-client error.

## Control Flow
Both tests use the shared daemon. The first scans `version.Components` for `Engine`; the second constructs a client with an intentionally unsupported API version and calls `ServerVersion`.

## State And Persistence
Read-only metadata checks; no daemon state changes.

## Dependencies And Integration Points
Integrates client API version negotiation, server version serialization, component metadata, and request client construction.

## Risks And Edge Cases
The old-client test assumes semantic `major.minor` parsing and minor version decrement remain valid. Error text is exact and can be brittle.

## Test Signals
Passing means Engine component details include API version, minimum API version, OS, and experimental flag matching daemon info, and unsupported clients receive the expected upgrade error.
