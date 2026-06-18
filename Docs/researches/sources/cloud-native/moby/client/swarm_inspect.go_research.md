# sources/cloud-native/moby/client/swarm_inspect.go

## Purpose
Implements swarm cluster inspection through the Docker API client.

## APIs, Types, And Functions
`SwarmInspectOptions` is currently empty; `SwarmInspectResult` wraps `swarm.Swarm`; `Client.SwarmInspect` requests and decodes the current swarm object.

## Control Flow, State, And Integration
The method sends `GET /swarm`, decodes the response into `swarm.Swarm`, closes the reader, and returns the typed result. It reads daemon cluster state but does not mutate client state.

## Risks And Test Signals
Risks are endpoint drift, JSON decode failures as swarm fields evolve, and callers assuming fields are always present. Integration is with swarm manager metadata, Raft configuration, and node join-token state exposed by the daemon.
