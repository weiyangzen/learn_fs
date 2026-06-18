# sources/cloud-native/moby/client/swarm_join.go

## Purpose
Implements joining an existing swarm with a daemon-side join request.

## APIs, Types, And Functions
`SwarmJoinOptions` embeds `swarm.JoinRequest`; `SwarmJoinResult` is an empty result wrapper; `Client.SwarmJoin` posts the join request to the daemon.

## Control Flow, State, And Integration
The method sends `POST /swarm/join` with the requested advertise address, remote addresses, listen address, and join token embedded in the API type. The daemon persists membership and node identity if successful; the client stores nothing.

## Risks And Test Signals
Risks include request serialization drift and failure to surface daemon errors for invalid tokens or unreachable managers. Integration is with swarm node bootstrap and cluster membership state.
