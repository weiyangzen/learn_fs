# sources/cloud-native/moby/daemon/prune.go

## Purpose
Implements daemon-side pruning for stopped containers and unused networks. It enforces one prune operation at a time and returns API prune reports with deleted objects and reclaimed space where available.

## Important APIs, Types, And Functions
`ContainerPrune`, `localNetworkPrune`, `clusterNetworkPrune`, `NetworkPrune`, `getUntilFromPruneFilters`, and `matchLabels` are key functions. `containersAcceptedFilters` allows `label`, `label!`, and `until`; `errPruneRunning` is a conflict error. `networkIsInUse` recognizes swarm network-in-use errors.

## Control Flow
Container prune validates filters, parses `until`, lists containers, skips running/newer/label-mismatched containers, fetches layer size for reporting, removes containers, and emits a prune event. Network prune builds a network filter, prunes swarm manager networks first when possible, prunes local networks by walking libnetwork networks, skips config-only/non-pruneable/in-use networks, and emits a network prune event if not canceled.

## State And Persistence
`daemon.pruneRunning` is an atomic guard shared by container and network prune. Successful prune mutates daemon state by removing containers/networks and logs events. Cancellation returns partial reports without rolling back completed removals.

## Dependencies And Integration Points
Depends on daemon container stores, image layer-size service, libnetwork, swarm cluster manager, filter parsing, timestamp parsing, and event logging. API handlers call these through backend interfaces.

## Risks And Edge Cases
Container size lookup failures are logged only because size is informational. Cluster network prune ignores specific "network ID is in use" errors but logs other removal failures. Context cancellation is cooperative and can return partially completed reports. The single prune guard serializes unrelated prune categories.

## Test Signals
No direct file-local tests are listed, but API prune routes, network filtering, and daemon integration tests exercise this behavior. Event logs and returned prune reports are the primary signals.
