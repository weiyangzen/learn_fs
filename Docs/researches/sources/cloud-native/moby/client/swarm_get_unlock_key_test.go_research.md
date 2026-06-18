# sources/cloud-native/moby/client/swarm_get_unlock_key_test.go

## Purpose
Tests unlock-key retrieval for server errors and successful JSON decoding.

## APIs, Types, And Functions
The file defines `TestSwarmGetUnlockKeyError` and `TestSwarmGetUnlockKey`, using `Client.SwarmGetUnlockKey`, `swarm.UnlockKeyResponse`, mock `GET /swarm/unlockkey`, and errdefs assertions.

## Control Flow, State, And Integration
Mock handlers assert method and path, then return either an error status or an unlock-key response body. The success test checks the decoded unlock key value.

## Risks And Test Signals
Signals protect endpoint path, HTTP method, error mapping, and JSON shape. The test does not validate secrecy handling, which remains caller and logging policy responsibility.
