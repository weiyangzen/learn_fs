# sources/cloud-native/moby/client/swarm_update_test.go

## Purpose
Tests swarm update error handling and successful endpoint invocation.

## APIs, Types, And Functions
`TestSwarmUpdateError` and `TestSwarmUpdate` exercise `Client.SwarmUpdate`, `SwarmUpdateOptions`, mock `POST /swarm/update`, and errdefs classification.

## Control Flow, State, And Integration
The mock server validates request method and path, then returns failure or success. The tests assert that daemon failures surface and successful updates return nil errors.

## Risks And Test Signals
The file protects the endpoint contract but gives limited coverage to query parameters for version and rotation flags. Those fields remain the main client-side risk surface.
