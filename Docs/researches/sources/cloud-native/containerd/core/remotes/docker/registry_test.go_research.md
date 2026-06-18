<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/registry_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/registry_test.go

## Purpose
Tests registry capability bitmasks and localhost host matching.

## Important APIs, Types, And Functions
- `TestHasCapability` validates `HostCapabilities.Has` for individual and combined capability masks.
- `TestMatchLocalhost` validates `MatchLocalhost` across IPv4, IPv6, hostnames, ports, malformed values, and non-local hosts.

## Control Flow
The tests are table-driven, directly invoking bitmask and matching helpers.

## State And Persistence
No state is persisted.

## Dependencies And Integration Points
Protects behavior consumed by host filtering in resolver/fetcher/pusher/referrers and default plain-HTTP decisions in resolver construction.

## Risks And Edge Cases
The test explicitly ensures invalid loopback-looking IPs do not panic and malformed host:port values do not match.

## Test Signals
Focused unit coverage for the registry trust/capability primitives.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/registry_test.go -->
