<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/network.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/network.go

## Purpose
Creates per-network nftables chains, verdict-map entries, NAT rules, ICC rules, direct ingress policy, and cleanup modifiers for bridge networks.

## Important APIs, Types, And Functions
`network` stores config, parent `Nftabler`, and reverse modifiers. `Nftabler.NewNetwork` invokes optional old-backend cleanup and configures IPv4/IPv6 tables. `configure` builds chains/maps/rules. `DelNetworkLevelRules` applies reverse modifiers. Helpers derive chain names and parse firewall marks with `nftFwMark`.

## Control Flow
For each valid family, `configure` creates ingress/egress filter chains and postrouting chains, inserts verdict-map elements keyed by bridge interface, adds conntrack rules, then branches for internal or external networks. Internal networks drop non-bridge ingress/egress and enforce ICC. External networks add optional fwmark accept, ICC, outgoing accept, final ingress accept/drop for unprotected/default, ICMP in routed mode, SNAT/MASQUERADE for outgoing NAT, and hairpin host masquerade.

## State And Persistence
State is nftables table state plus reverse modifiers retained in memory for cleanup. Firewalld reload does not delete nftables rules, so `ReapplyNetworkLevelRules` logs that it is not implemented.

## Dependencies And Integration Points
Uses internal `nftables`, OpenTelemetry spans, logging, and `firewaller`. Called by bridge network creation and backend live-restore.

## Risks And Edge Cases
In-memory reverse modifiers are unavailable after daemon restart, so persistent cleanup relies on table deletion or reconstructive cleaners. Rule grouping controls order; mistakes can expose unpublished ports or block established traffic. Firewall mark mask syntax differs from iptables and is converted to nft expressions.

## Test Signals
`nftabler_test.go` golden matrix validates generated table content and cleanup for IPv4/IPv6, internal, ICC, masquerade, SNAT, routed/unprotected, hairpin, localhost binding, and WSL2 options.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/network.go -->
