# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/registry_test.go

## Purpose
Tests host capability bitmask matching and localhost detection.

## Important APIs, Types, And Functions
`TestHasCapability` targets `HostCapabilities.Has`. `TestMatchLocalhost` targets `MatchLocalhost`.

## Control Flow
Capability tests verify single and combined required capability masks. Localhost tests cover empty host, IPv4 loopback ranges, invalid IPv4, host:port, DNS names, localhost, bracketed IPv6, bare `::1`, and malformed port cases.

## State And Persistence
No state; pure unit tests.

## Dependencies And Integration Points
The tested helpers affect default resolver plain-HTTP behavior and host filtering for pull/resolve/push/referrers.

## Risks And Edge Cases
The tests document intentional non-matches for invalid or ambiguous addresses, reducing the chance that insecure HTTP is enabled for non-local registries.

## Test Signals
Direct unit coverage for small but security-relevant registry helper behavior.
