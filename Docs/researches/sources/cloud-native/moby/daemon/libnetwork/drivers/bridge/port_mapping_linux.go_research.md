<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/port_mapping_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/port_mapping_linux.go

## Purpose
Coordinates bridge published-port allocation, port mapper calls, firewall programming, docker-proxy startup, operational state storage, and cleanup.

## Important APIs, Types, And Functions
`addPortMappings` normalizes requested bindings and groups same-port allocations. `mapPorts` calls registered port mappers, applies firewall rules, and starts proxies. `sortAndNormPBs`, `needSamePort`, `configurePortBindingIPv4`, and `configurePortBindingIPv6` derive per-family requests. `releasePorts`, `unmapPBs`, `reapplyPerPortIptables`, `collectFirewallPorts`, `toNATBinding`, and `toFwdBinding` handle cleanup/replay/conversion.

## Control Flow
Requests are normalized by endpoint addresses, default host IP, gateway mode, and existing port-binding state. Bindings that differ only by host IP are grouped so they receive the same host port. Mapping reserves/binds ports through the selected mapper, adds firewall rules from mapped NAT/forwarding data, starts docker-proxy when enabled and supported, and registers defers to undo every step on failure.

## State And Persistence
Endpoint `portMapping` stores operational mappings, stop-proxy callbacks, sockets, mapper names, NAT/forwarding metadata, and selected host ports. Persistent restore uses saved mappings with collapsed ranges to re-reserve previous ports.

## Dependencies And Integration Points
Uses `drvregistry.PortMappers`, `portmapperapi`, `portallocator`, `portmapper.StartProxy`, `netutils.IsV6Listenable`, firewaller network methods, and bridge endpoint/network state. Integrates NAT and routed port mappers plus rootlesskit clients.

## Risks And Edge Cases
Cross-family host IPv6 to container IPv4 requires docker-proxy. Routed mode disables NAT and ignores specific host ports. Default host IP selection, IPv4-mapped addresses, host port ranges, busy ports, loopback bindings, and proxy socket filter detachment all affect behavior. Cleanup must stop proxies, unmap ports, and remove firewall rules without leaking state.

## Test Signals
`port_mapping_linux_test.go` covers default mappings, explicit/ranged/busy ports, IPv4-mapped addresses, IPv6-to-IPv4 proxy behavior, routed mode, rootless clients, same-port grouping, release errors, and stub firewaller calls.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/port_mapping_linux.go -->
