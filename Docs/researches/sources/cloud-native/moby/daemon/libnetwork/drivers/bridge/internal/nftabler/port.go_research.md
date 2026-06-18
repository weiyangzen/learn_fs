<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/port.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/port.go

## Purpose
Programs nftables rules for published ports: forwarding accepts, DNAT, hairpin masquerade, and loopback-bound host-port protection.

## Important APIs, Types, And Functions
`AddPorts`, `DelPorts`, and `modPorts` manage lifecycle. `splitByContainerFam` separates IPv4/IPv6 bindings. `setPerPortRules` coordinates modifiers. `setPerPortForwarding`, `setPerPortDNAT`, `setPerPortHairpinMasq`, and `filterPortMappedOnLoopback` emit rule objects.

## Control Flow
Internal networks skip all port rules. On add, any old-backend cleaner first deletes equivalent old rules. Bindings are grouped by container address family and applied to valid family tables. Unprotected networks skip forwarding accept rules because final ingress accepts all. DNAT skips zero host ports and cross-family mappings handled by docker-proxy. Hairpin masquerade only applies when hairpin is enabled.

## State And Persistence
State is nftables table rules in network-specific chains and shared NAT/raw chains. Duplicate per-container forwarding and hairpin rules are marked with `IgnoreExist` semantics where needed.

## Dependencies And Integration Points
Uses internal `nftables`, `types.PortBinding`, `net.JoinHostPort`, logging, and the parent network config. Called from bridge port mapping and live-restore replay.

## Risks And Edge Cases
Multiple host ports for one container port can create duplicate rules; current behavior relies on idempotent add/delete rather than refcounting. IPv6 link-local sources are skipped for DNAT. WSL2 loopback accept is IPv4-only.

## Test Signals
Nftabler golden tests validate rule output; bridge port mapping tests validate that expected firewall port bindings are passed to the firewaller abstraction.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/nftabler/port.go -->
