# sources/cloud-native/moby/client/volume_create_test.go

## Purpose
Tests volume create error propagation and successful response decoding.

## APIs, Types, And Functions
The tests are `TestVolumeCreateError` and `TestVolumeCreate`, using `Client.VolumeCreate`, `VolumeCreateOptions`, mock `POST /volumes/create`, and `volume.Volume`.

## Control Flow, State, And Integration
Mock handlers assert method/path, return a daemon error or JSON volume object, and the client result is compared by volume name. State is mock-server scoped.

## Risks And Test Signals
Signals cover endpoint contract and result decoding. The tests do not inspect full request bodies, so option serialization has only indirect coverage.
