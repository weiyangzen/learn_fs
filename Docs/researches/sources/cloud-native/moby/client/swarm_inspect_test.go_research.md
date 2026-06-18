# sources/cloud-native/moby/client/swarm_inspect_test.go

## Purpose
Tests swarm inspection for daemon error handling and successful typed decoding.

## APIs, Types, And Functions
`TestSwarmInspectError` and `TestSwarmInspect` exercise `Client.SwarmInspect`, `SwarmInspectOptions`, mock `GET /swarm`, `swarm.Swarm`, and errdefs assertions.

## Control Flow, State, And Integration
The mock server verifies method and path, then returns a failure or a JSON object with a swarm ID. The client result is compared to ensure response decoding preserves the ID.

## Risks And Test Signals
Signals protect the basic inspect API contract. The test does not cover all swarm fields, so schema field regressions outside ID would need broader fixture coverage.
