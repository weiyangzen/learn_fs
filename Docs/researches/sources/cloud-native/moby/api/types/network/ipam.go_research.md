<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/ipam.go -->
# sources/cloud-native/moby/api/types/network/ipam.go

## Purpose
IPAM represents IP Address Management

## Important APIs, Types, And Functions
- Exported types: IPAM, IPAMConfig, SubnetStatuses.
- `IPAM` fields include Driver, Options, Config.
- `IPAMConfig` fields include Subnet, IPRange, Gateway, AuxAddress.
- Wire JSON fields include AuxiliaryAddresses, Gateway, IPRange, Subnet.
- Source comments highlight: IPAM represents IP Address Management IPAMConfig represents IPAM configurations

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `net/netip`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Uses `net/netip` typed IP/prefix values, preserving validated address semantics instead of raw strings.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- Address parsing and JSON behavior depend on `netip` semantics; invalid or legacy textual addresses need explicit handling upstream.

## Test Signals
- Package-level tests include `hwaddr_test.go`, `port_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/ipam.go -->
