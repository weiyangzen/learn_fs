# sources/cloud-native/moby/client/service_list_test.go

## Purpose
Tests service list error propagation and successful decoding from the daemon mock endpoint.

## APIs, Types, And Functions
The file defines `TestServiceListError` and `TestServiceList`. It uses `Client.ServiceList`, `ServiceListOptions`, `swarm.Service`, mock HTTP status responses, and gotest assertions.

## Control Flow, State, And Integration
The error test returns a server failure from `GET /services` and expects an unknown errdefs classification. The success test writes a JSON array with one service and compares the decoded ID. Test state is limited to the mock response body and request assertions.

## Risks And Test Signals
Signals include method/path correctness, daemon error mapping, and JSON array decoding. Missing coverage around filters and `Status` means query-building regressions there would need additional tests.
