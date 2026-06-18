# sources/cloud-native/moby/daemon/libnetwork/ipams/windowsipam/windowsipam.go

## Purpose
Provides the built-in Windows IPAM driver. It behaves like a minimal/null-style IPAM for Windows local networks while returning explicit requested pools when supplied.

## Important APIs, Types, And Functions
- Build-tagged for Windows only.
- `DefaultIPAM` is `"windows"`.
- Default address spaces are `LocalDefault` and `GlobalDefault`; default pool is `0.0.0.0/0`.
- `Register` registers the driver.
- `RequestPool` rejects subpools and IPv6, parses an explicit pool if supplied, otherwise returns default pool.
- `RequestAddress` parses the pool ID as CIDR and returns the preferred address with the pool mask, or nil if no preferred address is supplied.
- Release methods are no-ops with logging; `IsBuiltIn` returns true.

## Control Flow
Pool requests are simple: validate unsupported features, choose default or parsed pool, and return pool string as pool ID. Address requests require pool ID to parse as CIDR, then echo preferred IP when present.

## State And Persistence
Stateless; Windows HNS or higher layers own actual network/address state.

## Dependencies And Integration Points
Uses `ipamapi`, libnetwork `types`, `net/netip`, and logging. Registered from `ipams/drivers.go` only on Windows builds.

## Risks
No overlap or allocation tracking is performed. IPv6 and subpools are explicitly unsupported. The comment mentions allocating `0.0.0.0/32` by default, but implementation returns nil for no preferred address.

## Test Signals
`windowsipam_test.go` validates default and explicit pool responses, unsupported subpool/IPv6 errors, preferred address echoing, options tolerance, and no-op releases on Windows builds.
