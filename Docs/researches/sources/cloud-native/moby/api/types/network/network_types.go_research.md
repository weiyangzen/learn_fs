<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/network_types.go -->
# sources/cloud-native/moby/api/types/network/network_types.go

## Purpose
CreateRequest is the request message sent to the server for network create call.

## Important APIs, Types, And Functions
- Exported types: CreateRequest, NetworkingConfig, PruneReport.
- Constants: NetworkDefault.
- `CreateRequest` fields include Name, Driver, Scope, EnableIPv4, EnableIPv6, IPAM, Internal, Attachable, Ingress, ConfigOnly, ConfigFrom, Options, Labels.
- `NetworkingConfig` fields include EndpointsConfig.
- `PruneReport` fields include NetworksDeleted.
- Source comments highlight: CreateRequest is the request message sent to the server for network create call. NetworkingConfig represents the container's networking configuration for each of its interfaces Carries the networking configs specified in the `docker run` and `docker network connect` commands PruneReport contains the response for Engine API: POST "/networks/prune"

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- Package-level tests include `hwaddr_test.go`, `port_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/network_types.go -->
