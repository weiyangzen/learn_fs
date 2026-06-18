<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/default_gateway_windows.go -->
# sources/cloud-native/moby/daemon/libnetwork/default_gateway_windows.go

## Purpose
Windows default gateway support using the built-in `nat` network and endpoint options that disable ICC and DNS.

## Important APIs, Types, And Functions
Defines `libnGWNetwork = "nat"`. `getPlatformOption` returns `CreateOptionGeneric` with Windows driver `DisableICC` and `DisableDNS`. `createGWNetwork` delegates to `NetworkByName("nat")`.

## Control Flow
Common gateway setup uses the existing Windows NAT network rather than creating a new bridge network.

## State And Persistence
No new network is created; gateway endpoints attach to the existing NAT network.

## Dependencies And Integration Points
Depends on Windows libnetwork driver labels, generic endpoint options, and a preexisting NAT network.

## Risks And Edge Cases
If `nat` does not exist, gateway setup fails. Behavior differs from Linux because DNS and ICC are explicitly disabled on the endpoint.

## Test Signals
Windows networking tests should verify default gateway endpoint attachment to NAT and correct DNS/ICC option propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/default_gateway_windows.go -->
