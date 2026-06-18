# sources/cloud-native/moby/client/swarm_get_unlock_key.go

## Purpose
Implements retrieval of the swarm manager unlock key from the daemon.

## APIs, Types, And Functions
`SwarmGetUnlockKeyResult` wraps `swarm.UnlockKeyResponse`; `Client.SwarmGetUnlockKey` performs `GET /swarm/unlockkey`, decodes JSON, and closes the response reader.

## Control Flow, State, And Integration
The method sends a simple GET request without query parameters, decodes the unlock-key payload into swarm API types, and returns it. It does not persist local state, but it exposes sensitive cluster unlock material from daemon state.

## Risks And Test Signals
Risk centers on error handling and safe treatment of sensitive data by callers. Integration is with swarm autolock functionality and manager recovery workflows.
