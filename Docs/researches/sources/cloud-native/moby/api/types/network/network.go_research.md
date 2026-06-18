<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/network.go -->
# sources/cloud-native/moby/api/types/network/network.go

## Purpose
Network network swagger:model Network

## Important APIs, Types, And Functions
- Exported types: Network.
- `Network` fields include Name, ID, Created, Scope, Driver, EnableIPv4, EnableIPv6, IPAM, Internal, Attachable, Ingress, ConfigFrom, ConfigOnly, Options, and others.
- Wire JSON fields include Attachable, ConfigFrom, ConfigOnly, Created, Driver, EnableIPv4, EnableIPv6, IPAM, Id, Ingress, Internal, Labels, Name, Options, Peers, Scope.
- Source comments highlight: Network network swagger:model Network

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `time`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Carries timestamp or duration fields that must remain JSON-compatible across daemon/client boundaries.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- Package-level tests include `hwaddr_test.go`, `port_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/network.go -->
