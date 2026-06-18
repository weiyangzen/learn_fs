# sources/cloud-native/moby/integration/internal/network/network.go

Purpose: shared wrappers for network create, inspect, and remove operations in integration tests.

Important APIs and helpers: `createNetwork`, `Create`, `CreateNoError`, `Inspect`, `InspectNoError`, and `RemoveNoError`.

Control flow: `createNetwork` builds `client.NetworkCreateOptions`, applies option functions, calls `NetworkCreate`, and returns the network ID. `Create` exposes the error-returning form. `CreateNoError`, `InspectNoError`, and `RemoveNoError` wrap client calls with test assertions.

State and persistence: creates and removes daemon network objects and reads network inspect state. The helper itself persists no state.

Dependencies and integration: depends on Moby API client network methods, network create/inspect option types, and gotest assertions.

Risks: assertion wrappers are unsuitable for tests that need to inspect expected errors. `Create` returns ID only, not the full create response warnings.

Test signals: helper-only; centralizes network setup and teardown for integration tests.
