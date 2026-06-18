# sources/cloud-native/moby/daemon/libnetwork/ipams/null/null.go

## Purpose
Implements a built-in null IPAM driver that satisfies the IPAM contract without reserving specific pools or addresses.

## Important APIs, Types, And Functions
- `DriverName` is `"null"`; default address space is `"null"`.
- Default pools are `0.0.0.0/0` and `::/0` with corresponding pool IDs.
- `allocator` implements `ipamapi.Ipam`.
- `RequestPool` accepts only the default address space and no explicit pool/subpool, then returns the v4 or v6 default pool.
- `RequestAddress` returns nil address/data for valid default pool IDs.
- `ReleasePool` is always successful; `ReleaseAddress` validates pool ID.
- `Register` registers the driver name.

## Control Flow
The driver rejects address spaces other than `"null"` and rejects specific pool/subpool requests because it does not manage real ranges. Address requests do not allocate and always return nil for recognized pools.

## State And Persistence
Stateless; no pool or address usage is stored.

## Dependencies And Integration Points
Uses `ipamapi` and libnetwork `types` errors. It can be selected by networks that do not need Docker-managed IPAM.

## Risks
Because it returns nil addresses, callers must be prepared for no allocated address. It only validates pool IDs on address operations, so pool releases are no-ops for any string.

## Test Signals
`null_test.go` verifies v4/v6 default pool return, rejection of unknown address space and explicit pools/subpools, nil address results for valid pools, and errors for unknown pool IDs.
