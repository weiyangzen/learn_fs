<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/port.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/port.go

## Purpose
Programs per-port iptables rules for published ports, DNAT, hairpin masquerade, direct forwarding, loopback protection, and legacy cleanup.

## Important APIs, Types, And Functions
`AddPorts`, `DelPorts`, and `modPorts` iterate port bindings. `setPerPortIptables` dispatches family and security decisions. `setPerPortNAT` creates DNAT and hairpin MASQUERADE. `setPerPortForwarding` opens published container ports. `filterPortMappedOnLoopback` protects loopback-bound host ports. `dropLegacyFilterDirectAccess` removes older direct-access rules. `rawRulesDisabled` honors `DOCKER_INSECURE_NO_IPTABLES_RAW`.

## Control Flow
Each binding is skipped if its family/backend is disabled or the network is internal. Loopback filtering and legacy direct-access cleanup run first. Cross-family IPv6-host to IPv4-container mappings are left to docker-proxy. NAT rules are added only for nonzero host ports, and forwarding ACCEPT rules are added unless the family config is unprotected.

## State And Persistence
State is iptables nat/filter/raw rules keyed by host IP/port, container IP/port, protocol, and bridge name. The bridge endpoint stores operational mappings; on restore the driver replays `AddPorts`.

## Dependencies And Integration Points
Uses `types.PortBinding`, `iptables`, `os.Getenv`, and containerd logging. Called from bridge port mapping and cleaner paths.

## Risks And Edge Cases
Raw-rule opt-out weakens loopback and direct-routing protections. IPv6 link-local sources are excluded from DNAT. Duplicate host mappings and hairpin mode must avoid duplicate or missing rules. Legacy direct-access cleanup is upgrade-sensitive.

## Test Signals
Golden iptabler tests cover per-port rule output; bridge port mapping tests validate firewall calls through the stub firewaller.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/internal/iptabler/port.go -->
