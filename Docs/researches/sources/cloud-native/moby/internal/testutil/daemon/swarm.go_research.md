# sources/cloud-native/moby/internal/testutil/daemon/swarm.go

## Purpose
Provides Swarm cluster lifecycle and management helpers for integration-test daemons.

## Important APIs, Types, And Functions
- Constants define default test Swarm port/listen address and start args with or without iptables.
- `StartNode`, `StartNodeWithBusybox`, `RestartNode`, `StartAndSwarmInit`, and `StartAndSwarmJoin` compose daemon startup with Swarm initialization/join.
- `SwarmListenAddr`, `NodeID`, `SwarmInitWithError`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmInfo`, `SwarmUnlock`, `GetSwarm`, `UpdateSwarm`, `RotateTokens`, `JoinTokens`, and `startArgs` wrap Swarm APIs.
- `SpecConstructor` mutates `swarm.Spec` for update helpers.

## Control Flow
Startup helpers start daemons with Swarm-friendly arguments, load busybox where needed, initialize or join clusters using default listen addresses/ports and configured pools. API helpers create clients, fill missing request fields, submit Swarm operations, assert or return errors, and refresh cached daemon info after init/join.

## State And Persistence
Creates and mutates Swarm raft state, node membership, join tokens, Swarm specs, cached node info, and daemon runtime state. Start args disable iptables unless `WithSwarmIptables(true)` is set.

## Dependencies And Integration Points
Integrates daemon lifecycle helpers with Moby Swarm APIs, client options, Swarm request/response types, and busybox image loading.

## Risks And Edge Cases
Default listen address is `0.0.0.0`, while advertised address is only set when customized. Cached `NodeID` is valid only after successful init/join. Swarm tests requiring iptables must opt in. Join token selection depends on manager flag.

## Test Signals
Signals include successful daemon startup as Swarm node, initialized/joined clusters, inspectable Swarm info, token rotation, swarm spec updates, and node IDs available from cached info.
