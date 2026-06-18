# sources/cloud-native/moby/daemon/libnetwork/cluster/provider.go

## Purpose
Defines the libnetwork-facing interface for swarm/cluster providers and event types emitted by cluster control.

## Important APIs, Types, And Functions
Constants define `EventSocketChange`, `EventNodeReady`, `EventNodeLeave`, and `EventNetworkKeysAvailable`. `ConfigEventType` is a `uint8`. `Provider` exposes manager/agent role checks, local/listen/advertise/datapath/remote addresses, event listening, network attach/detach/update, and detachment waiting.

## Control Flow
The file only declares contracts. Implementations provide event channels and operations; libnetwork consumers call these methods during agent setup and swarm network attachment.

## State And Persistence
No state is stored here. Implementations may persist or mutate swarm/network state.

## Dependencies And Integration Points
Imports Docker API network types and `context`. `agent.go` uses address getters and remote lists to initialize NetworkDB and join peers.

## Risks And Test Signals
Interface changes affect cluster provider implementations and tests across the daemon. No direct tests are included in this subset.
