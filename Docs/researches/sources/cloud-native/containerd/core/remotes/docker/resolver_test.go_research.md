<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/resolver_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/resolver_test.go

## Purpose
Provides broad integration and unit tests for Docker resolver behavior, including auth schemes, host fallback, proxy namespace handling, sanitized URLs, retry policy, and digest resolution fallback rules.

## Important APIs, Types, And Functions
- Basic integration tests: `TestHTTPResolver`, `TestHTTPSResolver`, `TestBasicResolver`, `runBasicTest`, and `runNotFoundTest`.
- Auth tests: anonymous bearer tokens, basic-auth token requests, refresh token flows, POST password grant, direct basic auth, bad/missing/wrong credentials.
- Host/fallback tests: host failure fallback, TLS failure fallback, `NewHTTPFallback`, timeout fallback, and port-error helper checks.
- Proxy and query tests: `TestResolveProxy`, `TestResolveProxyFallback`, `TestAddQuery`, and `TestRequestSanitize`.
- Retry tests: `TestIsTransientTransportErr` and `TestDoWithTransportRetries`.
- Digest fallback tests: `TestResolveTransientManifestError`, `TestResolve404ManifestFallback`, and `TestResolverErrorStatusCodeOnFetch`.
- Fixtures: `testContent`, `testManifest`, `refreshTokenServer`, `namespaceRouter`, and local TLS/basic/token server helpers.

## Control Flow
The file builds miniature registries with `httptest` and exercises actual `NewResolver`, `Resolve`, `Fetcher`, `Fetch`, and `FetchByDigest` calls. Auth tests deliberately return `WWW-Authenticate` challenges and token endpoints. Fallback tests configure multiple `RegistryHost` entries or fallback transports. Retry tests isolate `request.doWithTransportRetries` with fake round trippers.

## State And Persistence
State is local to tests: in-memory manifests/blobs, local HTTP/TLS servers, refresh token server fields, and call counters. No real registry or content store is used.

## Dependencies And Integration Points
Touches most of the Docker remotes package: registry host config, authorizer, resolver, fetcher, request retry logic, error wrapping, HTTP fallback, and namespace proxy query generation.

## Risks And Edge Cases
The tests document important invariants: headers must be cloned for parallel use; 5xx on `/manifests/` must not fall back to `/blobs/`; 404 may fall back for legacy compatibility; URL logging must redact secrets; context cancellation must interrupt transport retry backoff.

## Test Signals
This is the primary resolver regression suite and gives strong coverage for network/auth behaviors. It relies on local test servers rather than external registries, making failures deterministic.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/resolver_test.go -->
