# sources/cloud-native/moby/daemon/pkg/registry/search_endpoint_v1.go

## Purpose
Provides the legacy V1 registry endpoint abstraction used only by search. It normalizes endpoint URLs, configures TLS and transport headers, pings endpoints, handles insecure fallback, and preserves redirect header behavior.

## Important APIs, Types, And Functions
`v1PingResult` records registry standalone status. `v1Endpoint` stores the client, URL, and secure flag. `newV1Endpoint`, `trimV1Address`, `newV1EndpointFromStr`, `(*v1Endpoint).String`, `(*v1Endpoint).ping`, `httpClient`, `trustedLocation`, and `addRequiredHeadersToRedirectedRequests` form the endpoint implementation.

## Control Flow
`newV1Endpoint` builds TLS config from `IndexInfo`, constructs an endpoint, skips ping for Docker Hub's known endpoint, then tries HTTPS `_ping`. Secure registries fail with an explicit insecure-registry hint on HTTPS error; insecure registries fall back to HTTP and require a successful ping. `ping` reads standalone status from `X-Docker-Registry-Standalone` or JSON body and defaults to standalone when absent. Redirect handling copies all headers except authorization unless both original and redirect targets are trusted HTTPS Docker domains.

## State And Persistence
No persistent state is stored beyond the endpoint object and its HTTP client. `newV1Endpoint` mutates the endpoint URL scheme during HTTPS/HTTP probing.

## Dependencies And Integration Points
Uses TLS config helpers from the registry package, Docker distribution transport modifiers, Docker API registry metadata, and Go HTTP redirect hooks. It feeds `searchUnfiltered` and `authorizeClient`.

## Risks And Edge Cases
This code intentionally permits HTTP fallback only for insecure registries. Redirect authorization retention is narrow but security-sensitive. `_ping` accepts 401 as a reachable registry through HTTP client behavior and assumes sane defaults on malformed JSON. Address trimming rejects explicit `/v2` endpoints because search is V1-only.

## Test Signals
`search_endpoint_v1_test.go` covers endpoint string normalization, secure/insecure fallback errors, V2 rejection, 401 validation, trusted-location classification, and redirect header propagation with and without authorization.
