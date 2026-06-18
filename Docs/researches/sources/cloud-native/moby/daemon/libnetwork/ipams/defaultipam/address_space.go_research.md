# sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/address_space.go

## Purpose
Implements the per-address-space allocator backing default IPAM. It tracks allocated master pools, child subpools, address usage within pools, predefined dynamic pools, and pool status.

## Important APIs, Types, And Functions
- `addrSpace` contains ordered `allocated` prefixes, `subnets` map to `PoolData`, `predefined` split pools, and a mutex.
- `newAddrSpace` sorts predefined pools and removes longer overlapping entries.
- `allocateSubnet` and `allocateSubnetL` handle static master/subpool allocation and overlap checks.
- `allocatePredefinedPool` dynamically chooses the first available predefined subnet considering current allocations and reserved prefixes.
- `releaseSubnet` and `deallocate` remove pools/subpools and honor `autoRelease`.
- `requestAddress` and `releaseAddress` allocate/release addresses inside a pool or subpool.
- `allocationStatus` reports in-use and available counts with 128-bit arithmetic and uint64 saturation.

## Control Flow
All mutating and status operations lock `mu`. Static master pool allocation rejects overlaps; subpool allocation intentionally preserves historical behavior where parent overlap checks are weaker. Dynamic allocation merges current allocations with reserved prefixes, walks sorted predefined networks, handles full and partial overlaps, and inserts the selected subnet at the iterator's allocation index.

## State And Persistence
State is in-memory and lost when the allocator is rebuilt, but default IPAM advertises request replay so libnetwork can rebuild state on daemon restart. `PoolData` tracks reserved addresses and child subpools; `autoRelease` determines whether a parent is removed when the last child goes away.

## Dependencies And Integration Points
Uses `addrset` for address allocation, `netiputil` and `ipbits` for prefix ordering and arithmetic, `uint128` for counts, and `ipamapi` errors. Called by `Allocator` request/release methods.

## Risks
The dynamic allocator is subtle: it assumes sorted inputs and carefully handles duplicate/overlapping allocated and reserved prefixes. Historical subpool overlap behavior is deliberately inconsistent for compatibility. Any missed mutex path could duplicate pools or addresses under parallel network creation.

## Test Signals
`address_space_test.go` heavily covers predefined deduplication, dynamic allocation with many overlap shapes, requested subnet sizes, reserved exclusions, release/reallocation, and static ordering. `allocator_test.go` and `parallel_test.go` further stress address allocation and concurrency.
