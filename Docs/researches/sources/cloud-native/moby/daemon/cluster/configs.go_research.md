# sources/cloud-native/moby/daemon/cluster/configs.go

## Purpose
Implements swarm config object CRUD and listing for manager nodes.

## Important APIs, Types, And Functions
Defines methods `GetConfig`, `GetConfigs`, `CreateConfig`, `RemoveConfig`, and `UpdateConfig` on `Cluster`.

## Control Flow
Each operation runs inside `lockedManagerAction`, obtains a swarmkit control client, converts API types with `convert.ConfigFromGRPC` or `ConfigSpecToGRPC`, and calls the corresponding swarmkit RPC. List builds filters with `newListConfigsFilters` and uses the large receive limit.

## State And Persistence
Config data is persisted in swarmkit's raft store, not locally in this file. The methods read or mutate cluster state through RPCs.

## Dependencies And Integration Points
Depends on swarm backend option types, swarmkit API requests, conversion helpers, and manager availability checks from `cluster.go`.

## Risks And Test Signals
Update relies on caller-provided version index for optimistic concurrency. Remove first resolves name/ID with `getConfig`. No tests in this subset; API/integration tests should verify manager-only errors, filters, conversion, and version conflicts.
