<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/port_summary.go -->
# sources/cloud-native/moby/api/types/container/port_summary.go

## Purpose
PortSummary Describes a port-mapping between the container and the host.

## Important APIs, Types, And Functions
- Exported types: PortSummary.
- `PortSummary` fields include IP, PrivatePort, PublicPort, Type.
- Wire JSON fields include IP, PrivatePort, PublicPort, Type.
- Source comments highlight: PortSummary Describes a port-mapping between the container and the host.

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
- Package-level tests include `config_test.go`, `health_test.go`, `hostconfig_test.go`, `hostconfig_unix_test.go`, `state_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/port_summary.go -->
