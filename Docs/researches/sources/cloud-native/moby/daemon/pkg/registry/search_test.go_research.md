# sources/cloud-native/moby/daemon/pkg/registry/search_test.go

## Purpose
Exercises registry search behavior, including authenticated test registry requests, filter validation, result filtering, error classification, and index-info generation from service configuration.

## Important APIs, Types, And Functions
`spawnTestRegistrySession` constructs an authenticated V1 client and endpoint for mock registry search. `debugTransport` logs HTTP requests/responses. Test cases call `searchRepositories`, `Service.Search`, `NewService`, `newServiceConfig`, and `newIndexInfo`.

## Control Flow
`TestSearchRepositories` verifies a mock registry returns the expected query and star count. `TestSearchErrors` checks invalid filters and upstream 500 handling. `TestSearch` iterates successful filter combinations for empty/no-filter/automated/official/stars cases. `TestNewIndexInfo` checks default, mirror, and custom insecure registry configurations across hostnames and IP ranges.

## State And Persistence
Tests use `httptest.Server`, transient registry service instances, and the DNS override from `registry_test.go`. The fake auth token is stored inside the `authTransport` created for the test client.

## Dependencies And Integration Points
Depends on Docker registry API types, daemon filter parser, containerd errdefs classification, and registry test mock handlers. It guards the search path exposed through the daemon API.

## Risks And Edge Cases
The tests encode that `is-automated=true` returns no results even if upstream reports automated builds, and that `IsAutomated` is reset to false in returned entries. They also lock in loopback IPv6 behavior and mirror URL normalization.

## Test Signals
Passing tests confirm client-side filter semantics, invalid argument versus unknown error typing, authenticated search setup, and secure/insecure index derivation.
