# sources/cloud-native/moby/daemon/pkg/registry/search_session.go

## Purpose
Implements the V1 registry authentication transport used by legacy search. It injects basic auth or cached token auth, preserves cancellation compatibility, and installs cookie support on the HTTP client.

## Important APIs, Types, And Functions
`authTransport` wraps an `http.RoundTripper` with `authConfig`, token cache, and a `modReq` map from original to cloned requests. `newAuthTransport`, `cloneRequest`, `onEOFReader`, `(*authTransport).RoundTrip`, `CancelRequest`, and `authorizeClient` are the key functions.

## Control Flow
`RoundTrip` bypasses auth changes for redirected untrusted locations, clones the request, records the clone for cancellation, sets Basic auth when always enabled, otherwise uses Basic auth only when `X-Docker-Token: true` requests a token or sends cached token auth. Response `X-Docker-Token` values update the cache, and the response body wrapper removes the request mapping on EOF or close. `authorizeClient` pings standalone HTTPS registries to decide always-basic mode, wraps the client transport, and installs a cookie jar.

## State And Persistence
Token cache and in-flight request mappings are in-memory on the transport. `authorizeClient` mutates the passed `http.Client` by replacing `Transport` and `Jar`.

## Dependencies And Integration Points
Depends on registry auth config, V1 endpoint ping, Go cookie jars, and redirect trust logic from `search_endpoint_v1.go`. It is used by `searchUnfiltered` and test registry sessions.

## Risks And Edge Cases
`token` is read and written without the mutex used for `modReq`, so concurrent requests could race if the same transport is shared broadly. `CancelRequest` depends on the wrapped transport exposing the legacy method. Always-basic auth requires non-nil auth config and is limited to standalone HTTPS registries.

## Test Signals
`search_test.go` uses this transport to seed a fake token and verify authenticated search. Redirect behavior is covered in the V1 endpoint tests.
