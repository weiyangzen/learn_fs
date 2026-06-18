# sources/cloud-native/moby/daemon/cluster/convert/secret.go

## Purpose
Converts swarmkit secret objects, specs, and file references to Docker API swarm secret types.

## Important APIs, Types, And Functions
Exports `SecretFromGRPC`, `SecretSpecToGRPC`, and `SecretReferencesFromGRPC`.

## Control Flow
`SecretFromGRPC` copies ID, annotations, data, driver, templating driver, version, and timestamps. `SecretSpecToGRPC` maps annotations, data, driver, and optional templating. Reference conversion copies ID/name and file target fields.

## State And Persistence
No local state. Secret data is persisted in swarmkit and passed through by these converters.

## Dependencies And Integration Points
Used by swarm secret APIs and service/container conversion. Depends on driver helpers from `service.go` and gogo timestamps.

## Risks And Test Signals
The exported reference converter only handles file targets. No tests in this subset directly target secret conversion; service/executor paths indirectly depend on it.
