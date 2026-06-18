<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/status.go -->
# sources/cloud-native/moby/api/types/network/status.go

## Purpose
Status provides runtime information about the network such as the number of allocated IPs.

## Important APIs, Types, And Functions
- Exported types: Status.
- `Status` fields include IPAM.
- Wire JSON fields include IPAM.
- Source comments highlight: Status provides runtime information about the network such as the number of allocated IPs.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- Package-level tests include `hwaddr_test.go`, `port_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/status.go -->
