# sources/cloud-native/moby/client/swarm_update.go

## Purpose
Implements swarm cluster updates with versioned concurrency and optional token/unlock-key rotation flags.

## APIs, Types, And Functions
`SwarmUpdateOptions` embeds `swarm.Spec` and contains `RotateWorkerToken`, `RotateManagerToken`, `RotateManagerUnlockKey`, and `Version`. `SwarmUpdateResult` is empty; `Client.SwarmUpdate` posts to `/swarm/update`.

## Control Flow, State, And Integration
The method encodes version and rotation booleans into query values, posts the swarm spec, and returns daemon errors. Successful calls mutate cluster-level Raft configuration, token state, and potentially unlock-key material.

## Risks And Test Signals
Risks include missing version values, inverted rotation flags, and daemon API drift around swarm spec serialization. Integration is with manager control-plane state and security token rotation workflows.
