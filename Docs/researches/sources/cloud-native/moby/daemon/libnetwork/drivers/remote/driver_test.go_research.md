# sources/cloud-native/moby/daemon/libnetwork/drivers/remote/driver_test.go

Purpose: Tests remote network driver plugin integration using HTTP test servers and temporary plugin specs.

Important APIs and functions: `handle` registers plugin RPC handlers. `setupPlugin` creates a plugin spec and activation endpoint. `testEndpoint` implements `InterfaceInfo`/`JoinInfo` assertions. Capability tests cover empty, extra, and invalid capabilities. `TestRemoteDriver` exercises capability negotiation, `GwAllocCheck`, network create/delete, endpoint create/delete, join/leave, operational info, and discovery. `TestDriverError` checks plugin `Err` propagation. `TestMissingValues` allows empty interface response fields. `TestRollback` verifies `DeleteEndpoint` is called when applying returned interface state fails.

Control flow: tests use real plugin HTTP client calls against `httptest.Server`, so they validate JSON encoding and plugin path construction.

State and persistence: writes temporary plugin spec files under the Docker plugin spec directory and cleans them up; plugin state is local test variables.

Dependencies and integration points: exercises `remote/driver.go`, plugin discovery, API wire structs, errdefs-compatible endpoint behavior, and route/gateway parsing.

Risks: uses global plugin spec path, so isolation depends on cleanup and permissions. External connectivity behavior is not deeply covered.

Test signals: strong regression coverage for remote plugin RPC adapter behavior and rollback paths.
