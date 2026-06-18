<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/default_gateway_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/default_gateway_linux.go

## Purpose
Linux implementation for creating the `docker_gwbridge` default gateway network.

## Important APIs, Types, And Functions
Defines `libnGWNetwork`, `getPlatformOption` returning nil, and `Controller.createGWNetwork`, which calls `NewNetwork` with bridge options `BridgeName=docker_gwbridge`, `EnableICC=false`, `EnableIPMasquerade=true`, IPv4 enabled, and IPv6 disabled.

## Control Flow
When common gateway code cannot find the gateway network, it enters this function and creates a bridge-backed network with tracing baggage identifying the trigger.

## State And Persistence
Creates a normal libnetwork bridge network persisted by controller network storage and realized by the bridge driver.

## Dependencies And Integration Points
Depends on bridge driver labels, controller `NewNetwork`, and OpenTelemetry baggage utilities.

## Risks And Edge Cases
Hardcoded IPv6 disabled means default gateway service is IPv4-only here. Bridge creation failures propagate to sandbox default gateway setup.

## Test Signals
Linux sandbox tests and daemon startup/live-restore behavior around `docker_gwbridge` exercise this path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/default_gateway_linux.go -->
