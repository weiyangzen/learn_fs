# sources/cloud-native/moby/daemon/internal/usergroup/lookup_unix_test.go

## Purpose
Tests negative user and group lookup paths on Unix.

## Important APIs, Types, And Functions
`TestLookupUserAndGroupThatDoesNotExist` calls `LookupUser`, `LookupUID`, `LookupGroup`, and `LookupGID` with fake names or `-1` IDs and asserts errors.

## Control Flow
The test expects named lookups to fall through to `getent` and return specific "unable to find entry" messages for passwd and group databases. Numeric negative lookups only assert a non-empty error.

## State And Persistence
Read-only; no accounts are created or removed.

## Dependencies And Integration Points
Requires a `getent` command on the test host. It validates the fallback error mapping used by daemon user namespace lookup.

## Risks And Test Signals
Exact error strings depend on this package's translation of getent exit status 2; systems without getent may produce different errors. The test does not cover successful NSS-only fallback.
