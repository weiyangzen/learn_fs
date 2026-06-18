# sources/cloud-native/moby/daemon/libnetwork/network_windows_test.go

## Purpose
Windows unit tests for endpoint-to-resolver external DNS configuration.

## Important APIs, Types, And Functions
`TestAddEpToResolver` builds synthetic HNS endpoints and resolvers, calls `addEpToResolverImpl`, validates resolver `ipToExtDNS` maps, then calls `deleteEpFromResolverImpl` and verifies cleanup.

## Control Flow
Table cases cover IPv4, limiting external DNS servers to three, disabled internal DNS, missing matching resolver, multiple resolvers/endpoints, and IPv6. Each case creates resolvers with requested listen addresses and checks only the expected resolver is modified.

## State And Persistence
All state is in-memory: fake `hcsshim.HNSEndpoint` values and resolver objects. Resolver external DNS maps are mutated and then cleared.

## Dependencies And Integration Points
Depends on hcsshim types, resolver internals, `netip`, `go-cmp`, and `gotest.tools`. Protects Windows DNS forwarding behavior in `network_windows.go`.

## Risks
The test does not call real HNS APIs or exercise compartment startup; it isolates pure selection/mapping logic.

## Test Signals
Strong signal for correct endpoint matching, self-resolver filtering, per-source ext DNS mapping, map cleanup, IPv6 handling, and resolver-index isolation.
