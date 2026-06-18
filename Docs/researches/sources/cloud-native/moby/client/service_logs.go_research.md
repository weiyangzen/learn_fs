# sources/cloud-native/moby/client/service_logs.go

## Purpose
Implements streaming log retrieval for swarm services, returning an `io.ReadCloser` that closes automatically when the supplied context is canceled.

## APIs, Types, And Functions
`ServiceLogsOptions` includes stdout/stderr selection, `Since`, `Until`, timestamps, follow, tail, and details flags. `ServiceLogsResult` is an `io.ReadCloser`; `Client.ServiceLogs` validates IDs, builds query parameters, and wraps the response body in `newCancelReadCloser`.

## Control Flow, State, And Integration
The function trims the service ID, translates boolean options into `1` query values, parses `Since` with `timestamp.GetTimestamp`, suppresses `tail` for empty or `all`, then sends `GET /services/{id}/logs`. The stream is live daemon state and remains caller-owned until closed or context cancellation fires.

## Risks And Test Signals
Risks include stream leaks, invalid timestamp handling, mismatched service-log query semantics, and inconsistent behavior with task/container logs. Integration points are the swarm logs endpoint and Docker's multiplexed log stream conventions.
