<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/endpoint.go -->
# sources/cloud-native/moby/api/types/network/endpoint.go

## Purpose
EndpointSettings stores the network endpoint details

## Important APIs, Types, And Functions
- Exported types: EndpointSettings, EndpointIPAMConfig.
- Exported functions/methods: Copy, Copy.
- `EndpointSettings` fields include IPAMConfig, Links, Aliases, DriverOpts, GwPriority, NetworkID, EndpointID, Gateway, IPAddress, MacAddress, IPPrefixLen, IPv6Gateway, GlobalIPv6Address, GlobalIPv6PrefixLen, and others.
- `EndpointIPAMConfig` fields include IPv4Address, IPv6Address, LinkLocalIPs.
- Wire JSON fields include IPv4Address, IPv6Address, LinkLocalIPs.
- Source comments highlight: EndpointSettings stores the network endpoint details EndpointIPAMConfig represents IPAM configurations for the endpoint

## Control Flow
- Runtime behavior is limited to helper methods such as validators, stringers, comparison functions, sort methods, or error adapters.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `maps`, `net/netip`, `slices`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Uses `net/netip` typed IP/prefix values, preserving validated address semantics instead of raw strings.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- Address parsing and JSON behavior depend on `netip` semantics; invalid or legacy textual addresses need explicit handling upstream.

## Test Signals
- Package-level tests include `hwaddr_test.go`, `port_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/endpoint.go -->
