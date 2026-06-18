# sources/cloud-native/moby/client/volume_update_test.go

## Purpose
Tests volume update daemon errors and successful request construction.

## APIs, Types, And Functions
`TestVolumeUpdateError` and `TestVolumeUpdate` exercise `Client.VolumeUpdate`, `VolumeUpdateOptions`, `swarm.Version`, and mock `PUT /volumes/test1`.

## Control Flow, State, And Integration
Mock handlers assert method, path, and version query encoding, then return server failure or success. The tests verify error classification and nil success behavior.

## Risks And Test Signals
Signals cover the versioned update endpoint contract. Request-body field coverage is limited, so schema drift in update options would need additional tests.
