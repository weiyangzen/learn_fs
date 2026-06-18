# sources/cloud-native/moby/client/swarm_join_test.go

## Purpose
Tests swarm join error propagation and successful call behavior.

## APIs, Types, And Functions
The file defines `TestSwarmJoinError` and `TestSwarmJoin`, using `Client.SwarmJoin`, `SwarmJoinOptions`, mock `POST /swarm/join`, and errdefs assertions.

## Control Flow, State, And Integration
Handlers assert the HTTP method and path, then return a daemon error or success. The client should return an error in the failure case and nil error with an empty result in the success case.

## Risks And Test Signals
Signals cover endpoint contract and daemon error propagation. The file does not inspect the full request body, so detailed join option serialization relies on the shared request machinery and swarm type tests.
