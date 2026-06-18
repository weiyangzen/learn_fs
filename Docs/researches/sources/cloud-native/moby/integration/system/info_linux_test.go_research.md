# sources/cloud-native/moby/integration/system/info_linux_test.go

## Purpose
Linux-only coverage for `/info` API compatibility fields around binary commit metadata and deprecated bridge nftables fields.

## Important APIs, Types, And Functions
- `TestInfoBinaryCommits` defines local `legacyCommit`/`legacyInfo` structs and compares current `/info` with `/v1.48/info`.
- `TestInfoLegacyFields` unmarshals `/v1.49/info` and `/v1.50/info` into a map and checks presence or absence of `BridgeNfIp6tables` and `BridgeNfIptables`.

## Control Flow
The tests issue raw JSON requests, read bodies, unmarshal into local structs/maps, and assert version-specific field values.

## State And Persistence
Read-only daemon metadata; no persistent state is changed.

## Dependencies And Integration Points
Touches API version negotiation, `/info` serialization, binary commit metadata for containerd/runc/init, and legacy field removal behavior.

## Risks And Edge Cases
The file is excluded on Windows. Assertions depend on binary commit IDs being known and not `N/A`. Legacy compatibility boundaries are version-specific and will need updating if API deprecation policy changes.

## Test Signals
Current API should expose commit IDs but empty `Expected` fields; API v1.48 should mirror `Expected` to `ID`; v1.49 should include bridge nftables booleans while v1.50 should omit them.
