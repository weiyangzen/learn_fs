# sources/distributed-fs/seaweedfs/weed/filer/mount_peer_registry_test.go

## Purpose

`mount_peer_registry_test.go` validates the in-memory mount peer registry's TTL, renewal, listing, sweep, and capacity semantics using an injectable clock.

## Important APIs, Types, and Functions

The tests use `newMountPeerRegistryWithClock`, `Register`, `List`, `Len`, `Sweep`, `maxMountPeerRegistryTTL`, and `maxMountPeerRegistryEntries`. `testClock` is a small helper retained for future tests.

## Control Flow

Tests register peers, advance a mutable clock, and assert list contents or registry length. They verify renewal extends expiry and updates rack, `List` filters but does not delete expired entries, `Sweep` deletes expired entries and counts them, negative TTL defaults to 60 seconds, huge TTLs are capped, empty address is ignored, and a full registry rejects a new address but accepts renewal.

## State and Persistence Behavior

State is local to each test registry. The injected clock makes TTL behavior deterministic without sleeping.

## Dependencies and Integration Points

The test file depends on Go `testing`, sorting for stable list assertions, and the registry API. It validates behavior expected by mount registration RPCs.

## Risks and Edge Cases

Filling 10,000 entries is acceptable but relatively heavier than other unit tests. The tests do not cover concurrent access or data-center fields beyond empty strings.

## Test Signals

Important signals are deterministic expiry, Len retaining expired entries until Sweep, TTL cap/default behavior, and capacity behavior preserving existing renewals.
