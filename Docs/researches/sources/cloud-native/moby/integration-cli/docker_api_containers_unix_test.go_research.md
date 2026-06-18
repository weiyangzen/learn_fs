# sources/cloud-native/moby/integration-cli/docker_api_containers_unix_test.go

## Purpose
Unix helper for mount setup inside container API integration tests.

## Important APIs and Types
Defines `mountWrapper(t, device, target, mType, options) error`.

## Control Flow, State, and Persistence
The helper shells out to the platform mount command to create test bind/shared mount setups. It marks the test failed or returns errors through assertions depending on call sites.

## Dependencies, Integration Points, Risks, and Test Signals
Used by mount propagation test cases in `docker_api_containers_test.go`. Depends on Unix mount privileges and host filesystem capabilities. Risks include requiring privileged CI, leaving mounts behind if cleanup elsewhere fails, and platform-specific option support. Successful mount propagation tests validate it.
