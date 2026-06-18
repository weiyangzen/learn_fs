<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/bridge_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/bridge_linux.go

## Purpose
Linux bridge network driver implementation. It creates bridge networks and veth endpoints, configures IPv4/IPv6 gateway behavior, programs firewall/NAT/port mappings, persists bridge state, and integrates with libnetwork driver APIs.

## Important APIs, Types, And Functions
Key types are `Configuration`, `networkConfiguration`, `bridgeEndpoint`, `bridgeNetwork`, `driver`, and `gwMode`. Registration and setup functions include `Register`, `newDriver`, `newFirewaller`, `parseNetworkOptions`, `processIPAM`, `Validate`, `Conflicts`, `CreateNetwork`, `createNetwork`, and `DeleteNetwork`. Endpoint and connectivity APIs include `CreateEndpoint`, `createVeth`, `Join`, `Leave`, `DeleteEndpoint`, `EndpointOperInfo`, `ProgramExternalConnectivity`, `ReleaseIPv6`, `trimPortBindings`, `clearConntrackEntries`, `handleFirewalldReload`, and legacy `link` handling.

## Control Flow
Driver registration optionally runs in a RootlessKit netns, initializes firewaller backend, restores store state, and registers reload callbacks. Network creation parses labels/options, validates subnets/gateway modes, checks conflicts under a config lock, creates or reuses a bridge interface, queues setup steps for devices, MTU, sysctls, IPv4/IPv6, forwarding, bridge netfilter, firewall network, and device up, then persists config. Endpoint creation creates host/container veth names, tries to place the peer in the container netns, sets MTU, enslaves host veth to the bridge, enables hairpin when proxy is disabled, sets MAC/IP data, adds endpoint firewall rules, brings the link up, and stores endpoint state. External connectivity computes gateway roles, trims stale bindings, maps ports, clears conntrack, and stores operational bindings.

## State And Persistence
In-memory driver state maps network IDs to `bridgeNetwork` objects and endpoint maps. Persistent state is stored through `datastore.Store` for network configurations and endpoints. Kernel/network state includes bridge devices, veth links, sysctls, forwarding, firewall rules, conntrack entries, firewalld zone membership, and portmapper allocations.

## Dependencies And Integration Points
Integrates with libnetwork `driverapi`, datastore, bridge firewaller implementations (`iptabler` or `nftabler`), iptables/firewalld, netlink/netns, RootlessKit, portmapper registry, network labels, IPAM data, OpenTelemetry tracing, and OSL namespace setup.

## Risks And Edge Cases
This file has high privilege and cleanup risk: partial failures must unwind kernel links, firewall rules, port bindings, and store records. Lock ordering across `driver.mu`, `configNetwork`, and per-network locks matters. Existing user-created bridges are not deleted. Firewalld reload reapplication must avoid races with network deletion and port updates. Rootless netns fallback and failed container-netns placement create host-netns peer behavior that callers must handle.

## Test Signals
Bridge driver tests should cover network option parsing, IPv6 CIDR validation, conflict detection, bridge creation/reuse/delete, endpoint create/delete, port mapping, routed/NAT gateway modes, firewalld reload, conntrack cleanup, live-restore persistence, and rootless behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/bridge_linux.go -->
