<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/firewaller/firewaller.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/firewaller/firewaller.go

## Purpose
Defines the bridge driver's firewall abstraction used by both iptables and nftables implementations.

## Important APIs, Types, And Functions
`IPVersion` identifies IPv4 or IPv6. `Config` contains top-level daemon settings such as enabled families, hairpin mode, direct routing, and WSL2 mirrored networking. `NetworkConfig` carries bridge-scoped policy: interface name, internal flag, ICC, masquerade, trusted host interfaces, fwmark allowance, and family configs. `NetworkConfigFam` carries host SNAT address, prefix, routed mode, and unprotected mode. Interfaces `Firewaller`, `Network`, and `FirewallCleaner` define lifecycle, endpoint, port, link, and cleanup operations.

## Control Flow
The bridge driver selects a concrete `Firewaller`, creates one `Network` per bridge, then calls network methods as endpoints, port mappings, legacy links, and reload/cleanup events occur.

## State And Persistence
The interface itself stores no state. It makes explicit which firewall state is network-level, endpoint-level, port-level, and link-level, and it documents cleaner behavior for deleting rules left by a previous backend during live-restore.

## Dependencies And Integration Points
Depends on `types.PortBinding`, `types.TransportPort`, `context`, and `netip`. Implemented by `iptabler`, `nftabler`, and the test `StubFirewaller`; consumed by the bridge driver, port mapping, IP forwarding, and store restore logic.

## Risks And Edge Cases
Semantics must remain consistent across backends. `DelNetworkLevelRules` intentionally excludes per-port/per-link cleanup, so driver call ordering is important. `AllowDirectRouting`, `Unprotected`, and `Routed` have security-sensitive meanings and must map cleanly to backend rules.

## Test Signals
Stub-backed bridge tests verify call ordering and object lifetimes; iptabler/nftabler golden tests verify equivalent rule output across policy combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/firewaller/firewaller.go -->
