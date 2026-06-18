<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/peer_info.go -->
# sources/cloud-native/moby/api/types/network/peer_info.go

## Purpose
PeerInfo represents one peer of an overlay network.

## Important APIs, Types, And Functions
- Exported types: PeerInfo.
- `PeerInfo` fields include Name, IP.
- Wire JSON fields include IP, Name.
- Source comments highlight: PeerInfo represents one peer of an overlay network.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
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
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/peer_info.go -->
