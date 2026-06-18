# sources/cloud-native/moby/daemon/server/router/swarm/cluster_routes.go

## Purpose
`cluster_routes.go` implements most swarm API handlers: cluster lifecycle, services, nodes, tasks, secrets, configs, and legacy response shaping.

## Important APIs, Types, And Functions
Handlers include `initCluster`, `joinCluster`, `leaveCluster`, `inspectCluster`, `updateCluster`, `unlockCluster`, `getUnlockKey`, service CRUD/log handlers, node CRUD, task list/get/logs, secret CRUD, and config CRUD. `serviceWithLegacy` supports deprecated `ServiceSpec.Networks`; `backFillLegacyNetwork` injects old fields.

## Control Flow
Handlers decode JSON or filters, parse object versions and booleans, apply API-version stripping, and call backend methods. Service create/update carry registry auth headers and choose `queryRegistry` for API <1.30. Service update parses `registryAuthFrom` and rollback flags. Secret/config templating is rejected before API 1.37. Logs delegate to `swarmLogs`.

## State And Persistence
All persistent swarm state changes are delegated to the backend: Raft cluster membership/configuration, service specs, node specs, secrets, configs, and unlock keys.

## Dependencies And Integration Points
Depends on API swarm/registry types, filters, version helpers, compat wrappers, backend log selectors, and `swarmbackend` options.

## Risks
Version compatibility is dense. Missing version stripping can let old clients set unsupported fields. Version query parsing must reject malformed object versions to avoid unsafe updates. Legacy network backfill is required for pre-1.25 clients.

## Test Signals
`helpers_test.go` covers some version-stripping behavior. Swarm integration tests cover route-level semantics and backend interactions.
