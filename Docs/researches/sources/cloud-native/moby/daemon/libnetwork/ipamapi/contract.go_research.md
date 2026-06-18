# sources/cloud-native/moby/daemon/libnetwork/ipamapi/contract.go

## Purpose
Defines libnetwork's IP Address Management contract for built-in and remote IPAM drivers, including registration, pool/address allocation, capabilities, request/response structures, and canonical errors.

## Important APIs, Types, And Functions
- `Registerer` lets drivers register by name with optional capabilities.
- `Ipam` is the driver interface: default address spaces, pool request/release, address request/release, and `IsBuiltIn`.
- `PoolStatuser` extends `Ipam` with `PoolStatus`.
- `PoolRequest` carries address space, pool, subpool, options, excluded prefixes, and IPv6 selection.
- `AllocatedPool` returns opaque pool ID, allocated prefix, and driver metadata.
- `Capability` expresses MAC-address and request-replay requirements.
- Error variables standardize invalid pool, overlap, exhaustion, duplicate IP, and out-of-range responses.

## Control Flow
This is contract-only code. Driver packages implement the interface and return these errors. The controller and network creation paths call the interface through registry lookups.

## State And Persistence
No state is stored. The opaque `PoolID` returned by drivers is persisted by higher libnetwork objects and later passed back to the same driver.

## Dependencies And Integration Points
Imports network API types for `SubnetStatus`, standard `net`/`netip`, and libnetwork `types` error classifiers. It is central to default, null, windows, and remote IPAM packages in this subset.

## Risks
`PoolRequest.Exclude` is documented as sorted, but enforcement is driver-specific. `PoolID` opacity is important; consumers parsing it would couple to one driver. Error identity matters because tests use `errors.Is` and callers may branch on classifications.

## Test Signals
Tests throughout `ipams/defaultipam`, `ipams/null`, `ipams/windowsipam`, `ipams/remote`, and `libnetwork_internal_test.go` exercise this contract.
