# sources/cloud-native/moby/daemon/pkg/registry/registry_test.go

## Purpose
Tests registry service endpoint selection and insecure-registry classification. It focuses on mirror inclusion for pulls but not pushes, default loopback insecurity, explicit insecure host/CIDR handling, and DNS lookup behavior used by registry configuration.

## Important APIs, Types, And Functions
`overrideLookupIP` temporarily replaces the package-level `lookupIP` hook and restores it with `t.Cleanup`. `TestMirrorEndpointLookup` exercises `NewService`/`newServiceConfig`, `LookupPushEndpoints`, and `LookupPullEndpoints`. `TestIsSecureIndex` drives `serviceConfig.isSecureIndex` through hostnames, ports, loopbacks, invalid DNS names, and CIDR matches.

## Control Flow
The mirror test creates a service with one mirror, resolves Docker Hub image endpoints, then asserts mirror presence differs between pull and push paths. The security test iterates table cases, builds fresh service configs, and checks the boolean result for each address.

## State And Persistence
Only package-global test state is mutated: `lookupIP` is replaced during individual tests and restored. No registry config persists beyond in-memory `serviceConfig` instances.

## Dependencies And Integration Points
The tests depend on `github.com/distribution/reference`, Moby registry service construction, and the package DNS hook. They validate behavior consumed by daemon auth, pull, push, and search code that relies on `isSecureIndex` and V2 endpoint lookup.

## Risks And Edge Cases
The table explicitly documents subtle behavior: localhost and loopback IPs are insecure by default, host-only insecure entries do not match arbitrary ports unless configured that way, and failed DNS lookup falls back to direct host matching. These rules are security-sensitive because they decide TLS verification and HTTP fallback.

## Test Signals
Failures indicate changed mirror ordering/exclusion or insecure registry matching. The DNS override makes results deterministic and catches regressions in CIDR expansion and hostname normalization.
