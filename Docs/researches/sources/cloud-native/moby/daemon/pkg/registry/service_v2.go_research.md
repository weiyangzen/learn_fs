# sources/cloud-native/moby/daemon/pkg/registry/service_v2.go

## Purpose
Builds ordered V2 registry endpoints for pulls, pushes, authentication, and registry communication. It handles Docker Hub defaults, mirrors, TLS config, and HTTP fallback for explicitly insecure registries.

## Important APIs, Types, And Functions
`(*Service).lookupV2Endpoints` returns `[]APIEndpoint` from a hostname and `includeMirrors` flag. It uses `DefaultNamespace`, `IndexHostname`, `DefaultV2Registry`, `newTLSConfig`, `isSecureIndex`, and `tlsconfig.ServerDefault`.

## Control Flow
For Docker Hub hostnames, pull lookup optionally prepends configured mirrors, normalizing schemes to HTTPS when absent and loading TLS config for each mirror, then appends the default V2 registry. For non-Hub hosts, it creates an HTTPS endpoint and, when TLS config has `InsecureSkipVerify`, appends an HTTP endpoint.

## State And Persistence
No state is modified. The caller must hold `s.mu` when accessing `s.config`, and public service methods do so.

## Dependencies And Integration Points
Called by registry auth, image pull/push, and service endpoint lookup. Mirrors interact with daemon configuration and certificate directories through `newTLSConfig`.

## Risks And Edge Cases
Mirror TLS config is recalculated on each call rather than memoized. Insecure registries receive an HTTP fallback endpoint, so accurate `isSecureIndex` classification is critical. Context cancellation is checked inside the mirror loop before potentially expensive TLS loading.

## Test Signals
`registry_test.go` verifies mirrors appear for pulls but not pushes. `search_test.go` and reload tests indirectly validate secure/insecure config feeding endpoint construction.
