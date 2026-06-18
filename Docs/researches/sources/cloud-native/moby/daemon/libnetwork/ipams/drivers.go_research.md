# sources/cloud-native/moby/daemon/libnetwork/ipams/drivers.go

## Purpose
Registers all IPAM drivers that libnetwork should know about: default, Windows, null, and remote plugin drivers.

## Important APIs, Types, And Functions
- `Register(r, pg, lAddrPools, gAddrPools)` sequentially calls `defaultipam.Register`, `windowsipam.Register`, `null.Register`, and `remote.Register`.

## Control Flow
Registration stops at the first error. The default driver receives configured local/global pools; Windows registration is a no-op on non-Windows builds; remote registration also installs plugin activation handling.

## State And Persistence
No direct state, but it populates the libnetwork IPAM registry passed through `ipamapi.Registerer`.

## Dependencies And Integration Points
Imports all IPAM driver packages, `ipamutils` for configured address pools, and `plugingetter` for managed plugin discovery. Called during controller initialization.

## Risks
Ordering matters: built-ins are registered before remote plugin handlers. A default registration failure prevents null or remote drivers from registering. Remote registration behavior changes depending on whether a plugin getter is available.

## Test Signals
Driver registration is indirectly covered by libnetwork controller tests and specific driver tests; this file has no direct test in the subset.
