# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/resolver_test.go

## Purpose
Integration-style tests for Docker resolver authentication, host fallback, proxy namespace support, and fetch correctness.

## Important APIs, Types, And Functions
Tests include `TestHTTPResolver`, `TestHTTPSResolver`, auth-token variants, refresh token tests, fallback tests, proxy tests, and helpers `runBasicTest`, `testFetch`, `testocimanifest`, `withTokenServer`, `tlsServer`, and `refreshTokenServer`.

## Control Flow
The suite builds local registries with manifests/configs/layers, resolves an image tag, creates fetchers, verifies manifest children, and fetches each child by descriptor and by digest. Auth tests wrap registries with Basic or Bearer challenge flows and token endpoints. Fallback tests supply multiple hosts where the first fails or has the wrong TLS mode. Proxy tests verify namespace query routing.

## State And Persistence
Uses `httptest` HTTP/TLS servers and in-memory content structs. No durable state.

## Dependencies And Integration Points
Exercises resolver, authorizer, fetcher, registry host configuration, schema media type handling, and reference parsing as a coordinated system.

## Risks And Edge Cases
The tests are broad but still use simplified registry handlers. They do not cover every status-code path, manifest size rejection, or pusher behavior.

## Test Signals
This is the strongest signal that resolver/auth/fetch integration works across common registry modes and fallback scenarios.
