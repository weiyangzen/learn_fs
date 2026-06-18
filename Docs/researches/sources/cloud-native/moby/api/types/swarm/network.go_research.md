<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/network.go -->
# sources/cloud-native/moby/api/types/swarm/network.go

## Purpose
Defines swarm network and endpoint specifications including virtual IPs, published ports, attachment
configuration, IPAM, and CSI-style labels.

## Important APIs, Types, And Functions
- Exported types: Endpoint, EndpointSpec, ResolutionMode, PortConfig, PortConfigPublishMode, EndpointVirtualIP, Network, NetworkSpec, NetworkAttachmentConfig, NetworkAttachment, IPAMOptions, IPAMConfig.
- Exported functions/methods: Compare.
- Constants: ResolutionModeVIP, ResolutionModeDNSRR, PortConfigPublishModeIngress, PortConfigPublishModeHost.
- `Endpoint` fields include Spec, Ports, VirtualIPs.
- `EndpointSpec` fields include Mode, Ports.
- `PortConfig` fields include Name, Protocol, TargetPort, PublishedPort, PublishMode.
- `EndpointVirtualIP` fields include NetworkID, Addr.
- `Network` fields include ID, Spec, DriverState, IPAMOptions.
- Wire JSON fields include Addr, Gateway, Range, Subnet.
- Source comments highlight: Endpoint represents an endpoint. EndpointSpec represents the spec of an endpoint. ResolutionMode represents a resolution mode.
- `PortConfig.Compare` provides deterministic sort order over protocol, target, published port, mode, and name.

## Control Flow
- Runtime behavior is limited to helper methods such as validators, stringers, comparison functions, sort methods, or error adapters.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `cmp`, `net/netip`, `github.com/moby/moby/api/types/network`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Uses `net/netip` typed IP/prefix values, preserving validated address semantics instead of raw strings.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- Address parsing and JSON behavior depend on `netip` semantics; invalid or legacy textual addresses need explicit handling upstream.

## Test Signals
- Adjacent test file `sources/cloud-native/moby/api/types/swarm/network_test.go` exercises related behavior.
- Package-level tests include `network_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/network.go -->
