# sources/cloud-native/containerd/integration/client/client_unix.go

## Purpose
This non-Windows file defines default integration-test daemon paths and address.

## Important APIs, Types, and Functions
Constants define `defaultRoot`, `defaultState`, and `defaultAddress` under `/var/lib/containerd-test` and `/run/containerd-test`.

## Control Flow
No executable flow.

## State and Persistence
The integration suite uses these paths for daemon root, state, and socket unless overridden.

## Dependencies and Integration Points
Consumed by `client.go` and `client_test.go`.

## Risks
Tests remove `defaultRoot`; path isolation is critical to avoid deleting real data. Requires privileges to access `/var/lib` and `/run`.

## Test Signals
Harness build/runtime configuration for Unix integration tests.
