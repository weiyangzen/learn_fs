# sources/cloud-native/moby/client/service_inspect_test.go

## Purpose
Verifies the service inspect client contract for daemon errors, not-found errors, invalid input, and successful response decoding.

## APIs, Types, And Functions
The tests are `TestServiceInspectError`, `TestServiceInspectServiceNotFound`, `TestServiceInspectWithEmptyID`, and `TestServiceInspect`. They use mock HTTP handlers, `cerrdefs.IsNotFound`, `InvalidParameter`, `swarm.Service`, and assert helpers.

## Control Flow, State, And Integration
Mock clients expect `GET /services/service_id`, return status codes or a JSON service object, and assert the client returns the matching service ID. The empty-ID case checks local validation before a daemon call. All state is contained in the mock server and decoded response object.

## Risks And Test Signals
The tests catch path regressions, wrong method selection, failure to classify 404 responses, lost invalid-parameter validation, and JSON decode breaks. They are a unit-level signal for swarm service inspect consumers.
