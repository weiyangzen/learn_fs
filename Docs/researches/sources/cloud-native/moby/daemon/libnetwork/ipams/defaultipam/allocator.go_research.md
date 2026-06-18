# sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/allocator.go

## Purpose
Implements Docker's built-in default IPAM driver. It exposes the `ipamapi.Ipam` and `PoolStatuser` contracts over four address spaces: local/global and IPv4/IPv6.

## Important APIs, Types, And Functions
- `DriverName`, `localAddressSpace`, and `globalAddressSpace` define driver identity and default address spaces.
- `Register` creates an allocator and registers it with `RequiresRequestReplay`.
- `Allocator` owns `local4`, `local6`, `global4`, and `global6` `addrSpace` instances.
- `NewAllocator` splits configured pools by IP family and initializes address spaces.
- `splitByIPFamily` validates canonical pool definitions and normalizes IPv4-mapped addresses.
- `RequestPool` parses static/dynamic pool requests, handles unspecified prefixes as dynamic size requests, validates subpools, and returns driver-specific pool IDs.
- `ReleasePool`, `RequestAddress`, `ReleaseAddress`, `PoolStatus`, and `IsBuiltIn` implement the driver API.
- `newPoolData` reserves network/subnet-router-anycast and IPv4 broadcast addresses, with RFC 3021 /31 exceptions.
- `getAddress` maps `addrset` errors into IPAM errors and supports preferred, subpool, serial, and any-address allocation.

## Control Flow
`RequestPool` requires an address space, selects v4/v6 address space, parses pool and subpool strings, treats unspecified pool addresses as dynamic requests with preferred prefix length, and delegates to `addrSpace`. `RequestAddress` parses the opaque default pool ID, converts optional preferred IP to `netip`, then delegates. `ReleaseAddress` and `ReleasePool` reverse those paths.

## State And Persistence
Allocator state is in-memory in the four `addrSpace` objects. Persistence is achieved by libnetwork replaying pool/address requests because the driver registers `RequiresRequestReplay`.

## Dependencies And Integration Points
Depends on `addrset`, `ipamapi`, `ipamutils`, libnetwork `types`, network API `SubnetStatus`, `netiputil`, and containerd logging. It is the default driver registered by `ipams/drivers.go` and used by network creation tests in `libnetwork_internal_test.go`.

## Risks
Opaque pool IDs are parseable only by this driver and encode address space plus pool/subpool. Compatibility code accepts child subnets larger than parents by collapsing them to parent behavior for pre-v24 networks. Incorrect address-space selection can cross IPv4/IPv6 or local/global state. Concurrency safety relies on `addrSpace` locks.

## Test Signals
`allocator_test.go` covers ID parsing/stringification, overlap detection, subpool behavior, dynamic predefined pools, address request/release, serial allocation, unusual /31 subnets, random deallocation, duplicate prevention, and parallel predefined pool allocation.
