# sources/cloud-native/moby/daemon/cluster/convert/service_test.go

## Purpose
Exercises service and task conversion edge cases that are user-visible in Docker swarm APIs.

## Important APIs, Types, And Functions
Tests `ServiceFromGRPC`, `ServiceSpecToGRPC`, `taskSpecFromGRPC`, isolation conversion, credential spec conversion, config reference conversion, and volume mount subpath conversion.

## Control Flow
Cases cover container runtime inbound/outbound, plugin generic runtime inbound/outbound, unsupported custom runtime, isolation mapping both directions, credential spec exclusivity and oneof mapping, unsupported network attachment service creation, runtime/spec mismatch, inbound network attachment task specs, config file/runtime targets both directions, invalid config target combinations, and `VolumeOptions.Subpath`.

## State And Persistence
No persistent state; all objects are in-memory API structs.

## Dependencies And Integration Points
This is the main regression suite for `service.go` and parts of `container.go`.

## Risks And Test Signals
The tests intentionally focus on tricky compatibility surfaces rather than all fields. Failures indicate API/raft conversion drift likely to affect service create/update/inspect behavior.
