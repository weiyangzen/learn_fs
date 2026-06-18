# sources/cloud-native/containerd/plugins/services/sandbox/controller_service_test.go

## Purpose
This test file validates the sandbox controller gRPC adapter without requiring real sandbox runtimes.

## Important APIs, Types, And Functions
`stubController` implements `sandbox.Controller` and records the last arguments for create, stop, wait, status, shutdown, metrics, and update. `newTestService` builds a `controllerService` with a test controller and event exchange. Test functions cover `getController`, `Create`, `Start`, `Stop`, `Wait`, `Status`, `Shutdown`, `Metrics`, and `Update`.

## Control Flow
Each test constructs a service, invokes an RPC method using a namespaced context, and asserts either gRPC status codes or captured stub state. The status tests verify that nil controller `Extra` becomes a non-nil protobuf `Any` and that non-nil extra fields are copied.

## State And Persistence
Only in-memory stub state is used. No metadata store or real runtime state is persisted.

## Dependencies And Integration Points
Tests use `exchange.NewExchange` for event publishing, `status.FromError` for gRPC code assertions, protobuf sandbox types, and `testify`.

## Risks
The tests do not assert event delivery, stop timeout option propagation, controller error status mapping for every RPC, or initialization behavior with plugin discovery. `Update` nil sandbox behavior is only checked as an error, not a specific gRPC code.

## Test Signals
These tests provide good adapter-level confidence that protobuf inputs are converted and delegated correctly, especially for create options, status fields, and update field lists.
