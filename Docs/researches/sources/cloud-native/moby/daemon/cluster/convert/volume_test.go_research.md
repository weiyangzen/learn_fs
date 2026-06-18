# sources/cloud-native/moby/daemon/cluster/convert/volume_test.go

## Purpose
Tests cluster volume conversion helpers for topology, capacity, availability, access modes, and create request mapping.

## Important APIs, Types, And Functions
Targets `topologyFromGRPC`, `capacityRangeFromGRPC`, `volumeAvailabilityFromGRPC`, `accessModeFromGRPC`, and `VolumeCreateToGRPC`.

## Control Flow
Tests verify nil and populated topology, nil/zero/nonzero capacity, availability enum mapping, block and mount access mode conversion, and a full create request with driver opts, labels, group, access mode, secrets, topology, and capacity.

## State And Persistence
No persistent state.

## Dependencies And Integration Points
Directly covers `volume.go`, protecting API-to-swarmkit conversion for cluster volumes.

## Risks And Test Signals
The suite does not cover `VolumeFromGRPC` end-to-end or publish status. Failures point to swarm volume API compatibility regressions.
