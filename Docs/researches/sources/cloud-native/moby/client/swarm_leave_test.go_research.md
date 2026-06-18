# sources/cloud-native/moby/client/swarm_leave_test.go

## Purpose
Tests swarm leave error handling and force query encoding.

## APIs, Types, And Functions
`TestSwarmLeaveError` and `TestSwarmLeave` exercise `Client.SwarmLeave`, `SwarmLeaveOptions`, mock `POST /swarm/leave`, and errdefs assertions.

## Control Flow, State, And Integration
The success test asserts the request method, path, and force query value when `Force` is true. The error test returns a daemon failure and expects an unknown errdefs classification.

## Risks And Test Signals
Signals catch query encoding and endpoint regressions. The test models client behavior only; daemon cleanup correctness is covered elsewhere.
