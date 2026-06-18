# sources/cloud-native/moby/client/volume_list.go

## Purpose
Implements Docker volume listing with optional filters.

## APIs, Types, And Functions
`VolumeListOptions` contains `Filters`; `VolumeListResult` wraps `volume.ListResponse`; `Client.VolumeList` performs the request and decode.

## Control Flow, State, And Integration
The method applies filters to URL values, sends `GET /volumes`, decodes the list response, and closes the response body. It reads daemon volume store state without mutating it.

## Risks And Test Signals
Risks include filter query encoding, schema drift in warnings or volume entries, and nil list fields. Integration is with CLI volume listing, pruning decisions, and driver metadata display.
