# sources/cloud-native/moby/daemon/libnetwork/ipamutils/utils.go

## Purpose
Provides default IPAM address-pool definitions and helper methods for splitting base networks into smaller allocatable prefixes.

## Important APIs, Types, And Functions
- `NetworkToSplit` combines a base `netip.Prefix` and target subnet size.
- `FirstPrefix` returns the first subnet derived from the base and size.
- `Overlaps` checks whether a prefix overlaps the base.
- `GetGlobalScopeDefaultNetworks` and `GetLocalScopeDefaultNetworks` return shallow clones of default pool slices.

## Control Flow
No complex flow. Defaults include Docker's local IPv4 private ranges and global `10.0.0.0/8` split into /24 pools.

## State And Persistence
Default slice variables are package-level. Getter functions clone the slice header but not the pointed-to `NetworkToSplit` structs, so callers modifying struct fields through pointers can mutate shared defaults.

## Dependencies And Integration Points
Used by default IPAM registration and tests. `NetworkToSplit` values are also accepted as user-configured default address pools.

## Risks
The shallow clone behavior is a mutation risk. Default pool definitions are IPv4-only here unless callers provide IPv6 pools. Validation of canonical form happens in default IPAM, not these helpers.

## Test Signals
Covered indirectly by default IPAM tests that consume defaults and custom `NetworkToSplit` lists.
