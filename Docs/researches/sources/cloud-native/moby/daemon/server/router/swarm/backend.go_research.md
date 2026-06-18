# sources/cloud-native/moby/daemon/server/router/swarm/backend.go

## Purpose
`backend.go` defines the swarm router backend contract for cluster, service, node, task, secret, config, and log operations.

## Important APIs, Types, And Functions
`Backend` includes swarm init/join/leave/inspect/update/unlock methods; service list/get/create/update/remove/logs; node list/get/update/remove; task list/get; secret CRUD; and config CRUD.

## Control Flow
Swarm route handlers parse HTTP request bodies/query values into API types and option structs, then call these methods.

## State And Persistence
Implementations persist swarm cluster state in the manager/control plane and retrieve task/service logs.

## Dependencies And Integration Points
Depends on API swarm types, server log selectors/options, and `swarmbackend` option structs.

## Risks
The interface is broad and version-sensitive. Route compatibility shims must align with backend expectations for older API clients.

## Test Signals
Compilation against swarm manager implementations and swarm API integration tests validate the contract.
