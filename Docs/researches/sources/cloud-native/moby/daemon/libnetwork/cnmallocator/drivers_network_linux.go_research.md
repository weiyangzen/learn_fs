<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_network_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_network_linux.go

## Purpose
Defines Linux CNM allocator driver availability: global overlay allocation plus local built-in drivers that can be referenced from Swarm-scoped networks without manager-side driver allocation.

## Important APIs, Types, And Functions
`globalDrivers` registers `overlay` through `ovmanager.Register`. `localDrivers` lists `bridge`, `host`, `ipvlan`, and `macvlan`. `PredefinedNetworks` returns predefined `bridge` and `host` network data.

## Control Flow
`NewAllocator` iterates `globalDrivers` and uses `localDrivers` through `resolveDriver`/`IsBuiltInDriver`.

## State And Persistence
No persistence; this file provides platform-specific static driver maps.

## Dependencies And Integration Points
Integrates bridge, host, ipvlan, macvlan, overlay manager, and SwarmKit predefined network data on Linux.

## Risks And Edge Cases
Driver names are compile-time platform policy. Adding a Linux driver requires updating this list if it should be valid for swarm allocator validation or node-local handling.

## Test Signals
Provider validation, generic allocator tests, and network allocation tests depend on these driver names.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_network_linux.go -->
