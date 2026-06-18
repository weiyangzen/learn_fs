# sources/cloud-native/moby/client/service_remove_test.go

## Purpose
Verifies service removal behavior for daemon failures, not-found errors, and successful deletion.

## APIs, Types, And Functions
The file defines `TestServiceRemoveError`, `TestServiceRemoveNotFoundError`, and `TestServiceRemove`. It uses `Client.ServiceRemove`, `ServiceRemoveOptions`, mock `DELETE /services/service_id`, and errdefs assertions.

## Control Flow, State, And Integration
Mock handlers assert the request method and path, then return server error, 404, or success. The tests validate classification of daemon errors and that a successful delete returns nil error and an empty result.

## Risks And Test Signals
The test signal protects the removal endpoint contract. It does not deeply test ID validation, but it catches path, method, and error mapping regressions that would break swarm service cleanup callers.
