# sources/cloud-native/moby/client/swarm_unlock.go

## Purpose
Implements unlocking an autolocked swarm manager by submitting the unlock key to the daemon.

## APIs, Types, And Functions
`SwarmUnlockOptions` embeds `swarm.UnlockRequest`; `SwarmUnlockResult` is empty; `Client.SwarmUnlock` posts to `/swarm/unlock`.

## Control Flow, State, And Integration
The method serializes the unlock request, posts it to the daemon, and returns any daemon error. It stores no local state, while successful calls unlock persisted manager state and encrypted Raft material.

## Risks And Test Signals
Risks include improper propagation of sensitive unlock keys and weak error classification for rejected keys. Integration is with swarm autolock and manager recovery paths.
