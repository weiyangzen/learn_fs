# sources/cloud-native/moby/client/volume_update.go

## Purpose
Implements update of cluster-scoped volume metadata using versioned swarm object semantics.

## APIs, Types, And Functions
`VolumeUpdateOptions` contains `Version` and `Spec`; `VolumeUpdateResult` is empty; `Client.VolumeUpdate` sends a `PUT` request. It uses `swarm.Version` and `volume.UpdateVolumeOptions`.

## Control Flow, State, And Integration
The method trims the volume name, sets `version` in query parameters, and sends `PUT /volumes/{name}` with the update spec. Successful calls mutate daemon or swarm volume metadata.

## Risks And Test Signals
Risks include missing optimistic-concurrency version, wrong method, and update spec drift. Integration is with swarm-aware volume drivers and daemon volume metadata storage.
