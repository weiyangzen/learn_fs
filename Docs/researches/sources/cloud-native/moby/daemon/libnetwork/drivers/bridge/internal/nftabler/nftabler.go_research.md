<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/nftabler.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/nftabler.go

## Purpose
Initializes the nftables backend's per-family Docker bridge tables and base chains.

## Important APIs, Types, And Functions
Constants name the `docker-bridges` table, base chains, NAT chain, raw chain, verdict maps, and rule groups. `Nftabler` stores config, optional cleaner, and IPv4/IPv6 tables. `NewNftabler`, `Close`, and `init` manage table creation and resources.

## Control Flow
For each enabled family, `init` creates a table, filter FORWARD base chain with ingress/egress verdict maps, NAT POSTROUTING base chain with ingress/egress maps, shared NAT chain, NAT PREROUTING and OUTPUT chains that jump for local destinations, raw PREROUTING chain, and optional WSL2 loopback rule. IPv6 table apply failures are logged and tolerated.

## State And Persistence
State is host nftables table state. The object holds table handles that must be closed, but `Close` does not delete firewall rules. The table is intended to be backend-owned and cleaned by table deletion when needed.

## Dependencies And Integration Points
Uses internal `nftables`, `firewaller`, and logging. It is selected by bridge driver firewall configuration and returns per-network objects implemented in `network.go`.

## Risks And Edge Cases
Base chain priorities and verdict-map dispatch are central to packet path correctness. Hairpin mode changes OUTPUT loopback exceptions. IPv6 failure tolerance can leave IPv6 bridge networking unavailable while daemon startup succeeds.

## Test Signals
Nftabler golden tests validate table initialization and cleaned state for enabled/disabled families and hairpin/WSL2 combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/nftabler.go -->
