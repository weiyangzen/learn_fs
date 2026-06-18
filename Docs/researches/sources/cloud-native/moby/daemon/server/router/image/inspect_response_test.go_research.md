# sources/cloud-native/moby/daemon/server/router/image/inspect_response_test.go

## Purpose
This test validates image inspect response compatibility for legacy `Config` fields.

## Important APIs, Types, And Functions
`TestInspectResponse` builds `image.InspectResponse` values with optional OCI image config, wraps them with `compat.Wrap`, and asserts the serialized `Config` JSON.

## Control Flow
Cases cover nil config, no legacy config, API `< v1.50`, and API `v1.50-v1.51`. The test verifies real configured fields override defaults while missing legacy fields are injected.

## State And Persistence
No state is persisted. The test verifies JSON serialization behavior.

## Dependencies And Integration Points
Depends on Docker image-spec config types, OCI image config, API image types, and daemon `compat`. It protects `legacyConfigFields` and `getImagesByName`.

## Risks
Changing `omitempty` compatibility can break clients that deserialize old fields unconditionally.

## Test Signals
Exact JSON comparison provides strong signal for legacy field presence and ordering-insensitive object semantics through raw JSON extraction.
