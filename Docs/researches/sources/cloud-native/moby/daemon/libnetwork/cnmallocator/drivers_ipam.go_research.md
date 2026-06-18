<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_ipam.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_ipam.go

## Purpose
Initializes IPAM drivers for the Swarm CNM allocator, including optional swarm default address pool configuration.

## Important APIs, Types, And Functions
`initIPAMDrivers(r ipamapi.Registerer, netConfig *networkallocator.Config)` parses `DefaultAddrPool` prefixes into `ipamutils.NetworkToSplit`, logs configured defaults, and calls `ipams.Register`.

## Control Flow
If a network allocator config is present, each default pool string is parsed with `netip.ParsePrefix`; invalid prefixes fail allocator initialization. The parsed base and subnet size are collected and passed to libnetwork IPAM registration.

## State And Persistence
No local persistence. It configures the IPAM registry with in-memory driver instances and default address-pool inputs used by later pool allocation.

## Dependencies And Integration Points
Connects SwarmKit `networkallocator.Config` to libnetwork IPAM registration and default pool splitting.

## Risks And Edge Cases
The logging string leaves a trailing comma and only logs when pools are present. Invalid prefixes fail fast. Passing `nil` plugin getter means only built-in IPAMs are registered here; remote IPAM plugins are registered later by `NewAllocator`.

## Test Signals
Allocator tests that allocate empty-config networks and custom pool configs exercise this path indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_ipam.go -->
