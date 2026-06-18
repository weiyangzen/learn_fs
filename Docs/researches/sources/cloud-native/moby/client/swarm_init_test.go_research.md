# sources/cloud-native/moby/client/swarm_init_test.go

## Purpose
Tests swarm initialization error propagation and successful node-ID decoding.

## APIs, Types, And Functions
The tests are `TestSwarmInitError` and `TestSwarmInit`. They call `Client.SwarmInit`, provide `SwarmInitOptions`, use mock `POST /swarm/init`, and check errdefs classification and response content.

## Control Flow, State, And Integration
Handlers assert method and path, return either a server error or JSON-encoded node ID, and the client result is compared. Test state is isolated to the mock HTTP exchange.

## Risks And Test Signals
Signals cover basic endpoint contract and response decoding. More complex init request validation remains a daemon-side concern rather than a client unit test.
