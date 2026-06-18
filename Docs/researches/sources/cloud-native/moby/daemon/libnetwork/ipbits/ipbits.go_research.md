# sources/cloud-native/moby/daemon/libnetwork/ipbits/ipbits.go

## Purpose
Implements numeric and bitfield helpers for `netip.Addr`, supporting both IPv4 and IPv6.

## Important APIs, Types, And Functions
- `Add(ip, x, shift)` returns `ip + (x << shift)`.
- `SubnetsBetween(a1, a2, sz)` returns how many `sz`-sized subnets fit between two addresses, capped by `uint128.Uint64`.
- `subAddr` subtracts one address from another using `uint128`.
- `Field(ip, u, v)` extracts a bitfield where bit 0 is the most significant bit.

## Control Flow
IPv4 paths use big-endian uint32 operations. IPv6 paths convert addresses to `uint128`. `SubnetsBetween` validates address family/order, masks both endpoints to prefix size, subtracts, then right-shifts by host-bit count.

## State And Persistence
Pure functions, no state.

## Dependencies And Integration Points
Depends on internal `uint128`. Used by default IPAM dynamic pool allocation to measure gaps between prefixes and by other address math paths.

## Risks
`Add` wraps on overflow. `Field` documents undefined behavior for invalid ranges. `SubnetsBetween` returns zero for invalid/mismatched inputs, which callers must distinguish from a valid no-gap result if needed.

## Test Signals
`ipbits_test.go` covers IPv4/IPv6 addition, bitfield extraction, subnet distances, and benchmarks allocation-free address addition.
