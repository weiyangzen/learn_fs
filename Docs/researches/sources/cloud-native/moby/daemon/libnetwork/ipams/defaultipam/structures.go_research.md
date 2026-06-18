# sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/structures.go

## Purpose
Defines default IPAM internal data structures for pool identity, pool data, subnet keys, and merged prefix iteration.

## Important APIs, Types, And Functions
- `PoolID` combines an address space with a `SubnetKey`.
- `PoolData` holds allocated addresses, child subpools, and auto-release marker.
- `SubnetKey` stores master and child prefixes and exposes `Is6`.
- `PoolIDFromString` parses `addressSpace/ip/bits` or `addressSpace/ip/bits/child/bits`.
- `(*PoolID).String` serializes the opaque ID used by the driver.
- `(*PoolData).String` prints child count for debugging.
- `mergeIter` merges two sorted prefix slices without allocating a combined slice.

## Control Flow
Pool ID parsing splits on `/`, expects 3 or 5 parts, and reconstructs CIDR strings for `netip.ParsePrefix`. `mergeIter` tracks indexes into allocated and reserved slices and selects the next item according to a caller-supplied comparator.

## State And Persistence
`PoolID.String` output is persisted by libnetwork as the driver's opaque pool ID. `PoolData` is in-memory allocator state. `mergeIter` is transient during dynamic allocation.

## Dependencies And Integration Points
Depends on `addrset` for per-pool address tracking and libnetwork `types` for invalid parameter errors. Used by `allocator.go` and `address_space.go`.

## Risks
Pool ID parsing assumes address spaces do not contain `/`. IPv6 prefixes contain colons but still split correctly on slash. Consumers outside the driver should not parse this ID despite its readable form. `mergeIter` assumes both input slices are sorted.

## Test Signals
`allocator_test.go` tests pool ID round-tripping and benchmarks conversions. `structures_test.go` verifies merge iteration order when allocated and reserved contain equal prefixes.
