# sources/cloud-native/moby/daemon/libnetwork/netutils/utils_freebsd.go

## Purpose
FreeBSD implementation of reserved-network inference.

## Important APIs, Types, And Functions
`InferReservedNetworks(v6 bool) []netip.Prefix` always returns an empty slice.

## Control Flow
No branching beyond returning an empty prefix list.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
Satisfies the cross-platform `netutils.InferReservedNetworks` API used by `Network.ipamAllocateVersion` when asking default IPAM to exclude host-reserved prefixes.

## Risks
On FreeBSD, automatic IPAM allocation does not avoid nameserver or route-derived prefixes through this helper. That is intentional in this file but can allow overlaps that Linux attempts to avoid.

## Test Signals
No direct tests in this subset; behavior is covered by compilation and IPAM callers on FreeBSD.
