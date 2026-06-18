# sources/cloud-native/moby/daemon/pkg/registry/search_endpoint_v1_test.go

## Purpose
Tests V1 endpoint construction, ping semantics, URL parsing, insecure fallback behavior, and redirect header safety for legacy registry search.

## Important APIs, Types, And Functions
Tests call `newV1Endpoint`, `newV1EndpointFromStr`, `(*v1Endpoint).ping`, `trustedLocation`, and `addRequiredHeadersToRedirectedRequests`. Helpers such as `makeIndex`, `makeHTTPSIndex`, and `makePublicIndex` come from registry test fixtures.

## Control Flow
The suite validates default/public standalone ping values, expands URL forms with or without `/v1`, rejects `/v2`, confirms invalid secure endpoints produce certificate or insecure-registry hints, accepts a 401 basic-auth ping as a valid registry, and checks header copying across redirect pairs.

## State And Persistence
All state is in `httptest` servers and local request objects. There is no persisted registry configuration.

## Dependencies And Integration Points
Uses Go HTTP request construction, `httptest`, Docker registry test server helpers, and `gotest.tools`. These tests guard behavior consumed by `search.go` and `search_session.go`.

## Risks And Edge Cases
The redirect tests ensure `Authorization` is stripped for untrusted or non-HTTPS redirects but retained for trusted Docker HTTPS hosts. The endpoint tests encode legacy expectations for URLs that may look malformed but were historically accepted.

## Test Signals
Failures indicate regressions in V1 search compatibility, insecure registry guidance, Docker Hub special-casing, or credential leakage prevention during redirects.
