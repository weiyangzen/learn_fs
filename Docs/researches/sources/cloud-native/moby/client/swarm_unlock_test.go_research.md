# sources/cloud-native/moby/client/swarm_unlock_test.go

## Purpose
Tests swarm unlock endpoint method/path and daemon error propagation.

## APIs, Types, And Functions
The tests are `TestSwarmUnlockError` and `TestSwarmUnlock`, using `Client.SwarmUnlock`, `SwarmUnlockOptions`, mock `POST /swarm/unlock`, and errdefs assertions.

## Control Flow, State, And Integration
The mock server checks method and path, returns either a server error or success, and the test asserts the client error result. Sensitive key contents are not inspected in this unit.

## Risks And Test Signals
Signals protect the basic unlock client contract. Remaining risk is body serialization and secret logging policy, which requires broader review outside this focused endpoint test.
