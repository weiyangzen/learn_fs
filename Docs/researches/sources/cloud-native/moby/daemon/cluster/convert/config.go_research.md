# sources/cloud-native/moby/daemon/cluster/convert/config.go

## Purpose
Converts swarmkit config objects and references between gRPC/raft-store representation and Docker API types.

## Important APIs, Types, And Functions
Exports `ConfigFromGRPC`, `ConfigSpecToGRPC`, and `ConfigReferencesFromGRPC`.

## Control Flow
`ConfigFromGRPC` copies ID, annotations, data, templating driver, version, and timestamps. `ConfigSpecToGRPC` builds swarmkit annotations, data, and optional templating driver. `ConfigReferencesFromGRPC` converts IDs/names and file targets when present.

## State And Persistence
No state. It translates objects persisted by swarmkit.

## Dependencies And Integration Points
Used by cluster config CRUD and service/container conversion. Depends on gogo timestamp conversion and shared `annotationsFromGRPC`.

## Risks And Test Signals
`ConfigReferencesFromGRPC` ignores non-file targets in this exported helper, while `container.go` has fuller runtime target handling. Tests in service conversion cover config references indirectly.
