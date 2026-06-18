# sources/cloud-native/moby/daemon/server/router/volume/backend.go

## Purpose
`backend.go` defines local volume and swarm cluster-volume backend contracts for the volume router.

## Important APIs, Types, And Functions
`Backend` covers local volume `List`, `Get`, `Create`, `Remove`, and `Prune`. `ClusterBackend` covers cluster volume `GetVolume`, `GetVolumes`, `CreateVolume`, `RemoveVolume`, `UpdateVolume`, and `IsManager`.

## Control Flow
Routes try local volume operations first for normal volumes and use the cluster backend for API 1.42+ cluster volume features when the node is a manager.

## State And Persistence
Implementations persist local volume metadata/data and swarm cluster-volume specs.

## Dependencies And Integration Points
Depends on API volume types, daemon filters, `volumebackend` option structs, and volume service options.

## Risks
Local and cluster volumes can duplicate names; the router defines precedence rather than preventing all duplication.

## Test Signals
`volume_routes_test.go` uses fake implementations of both interfaces to test routing decisions.
