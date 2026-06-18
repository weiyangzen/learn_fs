# sources/cloud-native/moby/daemon/libnetwork/netutils/utils_windows.go

## Purpose
Windows implementation of reserved-network inference.

## Important APIs, Types, And Functions
`InferReservedNetworks(v6 bool) []netip.Prefix` always returns an empty slice.

## Control Flow
The function unconditionally returns an empty prefix list.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
Satisfies the same API used by network IPAM allocation. Windows-specific IPAM and HNS behavior live elsewhere.

## Risks
Windows automatic IPAM does not get Linux-style host route or resolver exclusions from this helper.

## Test Signals
No direct tests in this subset; coverage is build and integration oriented.
