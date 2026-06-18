# sources/cloud-native/moby/client/service_update_test.go

## Purpose
Tests service update error propagation, connection failure handling, request method/path, query encoding, and response warning decoding.

## APIs, Types, And Functions
The tests are `TestServiceUpdateError`, `TestServiceUpdateConnectionError`, and `TestServiceUpdate`. They exercise `Client.ServiceUpdate`, `ServiceUpdateOptions`, `swarm.Version`, `swarm.ServiceSpec`, and mock `POST /services/service_id/update`.

## Control Flow, State, And Integration
The tests configure server responses, assert `version`, `registryAuthFrom`, and rollback-related request behavior where applicable, and decode returned warnings. State is test-local but mirrors the daemon update endpoint.

## Risks And Test Signals
Signals include transport failure classification, daemon error mapping, and warning preservation. The file is a contract test for API clients that rely on versioned service updates.
