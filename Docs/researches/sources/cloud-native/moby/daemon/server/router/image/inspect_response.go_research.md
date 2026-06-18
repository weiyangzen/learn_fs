# sources/cloud-native/moby/daemon/server/router/image/inspect_response.go

## Purpose
`inspect_response.go` centralizes legacy image config fields that must be injected into inspect responses for older API versions.

## Important APIs, Types, And Functions
`legacyConfigFields` maps version buckets (`v1.49` and `v1.50-v1.51`) to field/default-value maps used by `compat.Wrap`.

## Control Flow
`getImagesByName` selects a map based on API version and adds it as extra `Config` fields. Actual configured fields override legacy defaults during wrapping/JSON serialization.

## State And Persistence
No state is persisted; the maps are package-level constants for response shaping.

## Dependencies And Integration Points
Used by image inspect response compatibility code and tested by `inspect_response_test.go`.

## Risks
Wrong default values or version bucket selection can change JSON wire shape and break clients expecting pre-omitempty fields.

## Test Signals
The inspect response test serializes representative responses and verifies exact JSON for each legacy bucket.
