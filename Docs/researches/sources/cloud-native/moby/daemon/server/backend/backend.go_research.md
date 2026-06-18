# sources/cloud-native/moby/daemon/server/backend/backend.go

## Purpose
Defines shared backend data structures used between API routers and daemon implementations for containers, logs, stats, image commit, plugins, and networks.

## Important APIs, Types, And Functions
Key structs include `ContainerCreateConfig`, `ContainerRmConfig`, `ContainerAttachConfig`, `PartialLogMetaData`, `LogMessage`, `LogAttr`, `LogSelector`, `ContainerStatsConfig`, `ContainerInspectOptions`, `ContainerListOptions`, `ContainerLogsOptions`, `ContainerStopOptions`, `ExecStartConfig`, `CreateImageConfig`, `CommitConfig`, plugin configs, and `NetworkListConfig`.

## Control Flow
This file contains type definitions only. Control flow is supplied by routers and daemon backend methods consuming these structs.

## State And Persistence
The structs carry request options, streams, log payloads, and configuration between layers. They do not persist state themselves, but some fields such as `LogMessage.Line` warn that backing bytes may be reused after logging.

## Dependencies And Integration Points
Imports Docker API container/network types, distribution references, daemon filters, OCI platform specs, and Go `io`/`time`. It is a central contract for container router, daemon lifecycle code, image commit, logs, stats, and plugin handlers.

## Risks And Edge Cases
Because this package is a cross-layer contract, field semantics must remain compatible with API version shims. `ContainerStopOptions.Timeout` uses nil versus `-1` versus `0` semantics that handlers must preserve.

## Test Signals
No direct tests; compile-time interface use and router/daemon tests validate these shapes.
