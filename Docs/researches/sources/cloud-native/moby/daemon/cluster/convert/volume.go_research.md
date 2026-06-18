# sources/cloud-native/moby/daemon/cluster/convert/volume.go

## Purpose
Converts swarmkit cluster volume specs/status into Docker volume API types and Docker volume create requests into swarmkit volume specs.

## Important APIs, Types, And Functions
Exports `VolumeFromGRPC` and `VolumeCreateToGRPC`. Internal helpers include `volumeSpecToGRPC`, `volumeInfoFromGRPC`, `volumePublishStatusFromGRPC`, `accessModeFromGRPC`, `volumeSecretsFromGRPC`, `topologyRequirementFromGRPC`, `topologyFromGRPC`, `capacityRangeFromGRPC`, and `volumeAvailabilityFromGRPC`.

## Control Flow
Inbound conversion maps cluster spec fields, publish status, volume info, metadata, driver, labels, name, options, and global scope. Outbound conversion maps access scope/sharing/type, secrets, topology requirements, capacity range, availability, annotations, and driver/options. Nil cluster specs create a minimal swarmkit spec.

## State And Persistence
No local state. It defines conversion for cluster volume objects persisted by swarmkit and shown through Docker volume APIs.

## Dependencies And Integration Points
Used by swarm volume create/list/inspect flows and executor volume attachments. Depends on Docker API volume types and swarmkit volume enums.

## Risks And Test Signals
Default/unknown inbound availability maps to `drain`, a conservative fallback. `VolumeCreateToGRPC` assumes non-nil request for name/labels/driver after optional cluster spec handling. Tests cover topology, capacity, availability, access modes, and create conversion.
