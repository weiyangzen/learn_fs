# sources/cloud-native/moby/client/volume_list_test.go

## Purpose
Tests volume list error propagation and successful list response decoding.

## APIs, Types, And Functions
`TestVolumeListError` and `TestVolumeList` exercise `Client.VolumeList`, `VolumeListOptions`, mock `GET /volumes`, and `volume.ListResponse`.

## Control Flow, State, And Integration
The mock server returns a daemon error or JSON list containing a named volume. Tests assert request method/path and decoded volume count/name.

## Risks And Test Signals
Signals cover endpoint and decode basics. Filter-specific coverage is limited, leaving shared filter helper behavior as the main guard for filtered volume lists.
