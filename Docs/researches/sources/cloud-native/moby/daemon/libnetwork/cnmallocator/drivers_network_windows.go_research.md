<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_network_windows.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_network_windows.go

## Purpose
Defines Windows CNM allocator driver availability and predefined networks.

## Important APIs, Types, And Functions
`globalDrivers` still exposes overlay allocation through `ovmanager.Register`. `localDrivers` lists Windows drivers `internal`, `l2bridge`, and `nat`. `PredefinedNetworks` returns the predefined `nat` network.

## Control Flow
The same allocator logic uses these platform-specific maps at build time on Windows.

## State And Persistence
No persistence; the data is static.

## Dependencies And Integration Points
Connects SwarmKit allocation policy to Windows libnetwork driver names.

## Risks And Edge Cases
Linux-focused allocator tests are skipped because expected driver names differ. Validation depends on this list staying aligned with Windows driver registration.

## Test Signals
Windows-specific allocator/provider tests should validate `nat`, `internal`, and `l2bridge` behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_network_windows.go -->
