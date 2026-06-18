# sources/cloud-native/moby/client/volume_inspect_test.go

## Purpose
Tests volume inspect daemon errors, not-found handling, empty ID validation, and successful decode.

## APIs, Types, And Functions
The tests include `TestVolumeInspectError`, `TestVolumeInspectNotFound`, `TestVolumeInspectWithEmptyID`, and `TestVolumeInspect`. They use `Client.VolumeInspect`, `volume.Volume`, and errdefs assertions.

## Control Flow, State, And Integration
Mock handlers assert `GET /volumes/volume_id`, return status codes or a JSON volume, and the client validates decoded name fields. Empty ID validation occurs before HTTP.

## Risks And Test Signals
Signals protect validation, path construction, error classification, and response decoding. Broader driver-specific fields are not exhaustively tested.
