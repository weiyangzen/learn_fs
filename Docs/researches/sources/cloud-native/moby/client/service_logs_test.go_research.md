# sources/cloud-native/moby/client/service_logs_test.go

## Purpose
Tests service log request construction, option encoding, response streaming, and error propagation.

## APIs, Types, And Functions
The tests are `TestServiceLogsError` and `TestServiceLogs`. They exercise `Client.ServiceLogs`, `ServiceLogsOptions`, mock `GET /services/service_id/logs`, and the returned read closer.

## Control Flow, State, And Integration
The error case returns a daemon failure and expects an errdefs unknown error. The success case checks request method, path, and query values for stdout/stderr, follow, timestamps, details, since, and tail, then reads the response body from the returned stream.

## Risks And Test Signals
Signals cover query compatibility and streaming response lifetime. Remaining risks include context-cancel behavior and `tail=all` suppression, which are primarily covered by implementation review rather than these tests.
