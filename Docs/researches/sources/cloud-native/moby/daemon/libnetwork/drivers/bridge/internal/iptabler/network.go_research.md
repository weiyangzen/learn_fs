<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/network.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/network.go

## Purpose
Implements per-bridge network-level iptables rules for internal, NAT, routed, unprotected, ICC, masquerade, SNAT, conntrack, and default-forward policy behavior.

## Important APIs, Types, And Functions
`network` holds `firewaller.NetworkConfig`, parent `Iptabler`, and cleanup functions. `NewNetwork`, `ReapplyNetworkLevelRules`, `DelNetworkLevelRules`, `configure`, and `setupIPTables` manage lifecycle. Helpers include `setICMP`, `addNATJumpRules`, `deleteLegacyFilterRules`, `setDefaultForwardRule`, `setupNonInternalNetworkRules`, `setIcc`, `removeIPChains`, `setupInternalNetworkRules`, and `iptablesFwMark`.

## Control Flow
Creating a network configures each enabled valid family. Internal networks get ingress/egress DROP rules plus ICC handling. External networks get SNAT/MASQUERADE rules when configured, hairpin host masquerade, ICC rules, optional ICMP for routed mode, outgoing ACCEPT rules, default incoming DROP/ACCEPT in `DOCKER`, conntrack established ACCEPT, and jumps from Docker bridge/CT chains. Each successful step registers a reverse cleanup function.

## State And Persistence
State is host iptables state plus in-memory cleanup closures. Cleanups are lost on daemon restart, so store restore and cleaner paths reconstruct removal based on persisted network config.

## Dependencies And Integration Points
Uses `firewaller`, `iptables`, containerd logging, and numeric parsing for firewall marks. Called by `Iptabler.NewNetwork`, cleaner, and reload paths.

## Risks And Edge Cases
Ordering matters: per-port ACCEPT rules must precede default DROP. Upgrade cleanup deletes legacy FORWARD rules from old releases. Firewall mark parsing accepts Go-style numeric syntax and converts to decimal for iptables. Internal network IPv4/IPv6 rule forms differ.

## Test Signals
`network_test.go` verifies setup/deletion and NAT/SNAT combinations; `iptabler_test.go` golden files validate full network rule output across policy combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/network.go -->
