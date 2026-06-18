# sources/cloud-native/moby/client/volume_prune_test.go

## Purpose
Tests volume prune success and error variants, including errdefs classification and decoded prune reports.

## APIs, Types, And Functions
`TestVolumePrune` uses table-driven mock responses for `Client.VolumePrune`, `VolumePruneOptions`, mock `POST /volumes/prune`, and `volume.PruneReport`.

## Control Flow, State, And Integration
Test cases configure status codes and JSON bodies, assert the request method/path, and compare deleted volume names plus reclaimed space. State is local to each table case.

## Risks And Test Signals
Signals are valuable because prune is destructive. The test checks response mapping but does not execute real daemon volume reference accounting.
