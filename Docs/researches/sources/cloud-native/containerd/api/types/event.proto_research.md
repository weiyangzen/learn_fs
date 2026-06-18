<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/event.proto -->
# sources/cloud-native/containerd/api/types/event.proto

## Purpose
Canonical proto definition of `Envelope`, the common event wrapper for containerd APIs.

## Important APIs and Types
`Envelope` has custom option `(containerd.types.fieldpath) = true`, plus `timestamp`, `namespace`, `topic`, and opaque `event` payload fields.

## Control Flow
Schema only. Event creation, forwarding, filtering, and subscription are implemented elsewhere.

## State and Persistence
Carries event state for transmission or storage. It preserves event time, namespace scope, topic routing key, and typed payload.

## Dependencies and Integration Points
Imports protobuf `Any`, `Timestamp`, and containerd `types/fieldpath.proto`. Used by event services and publisher/subscriber integrations.

## Risks
Opaque payloads and forwarded namespace/timestamp data require authorization and decoding care. The custom option must stay registered for code that relies on fieldpath metadata.

## Test Signals
Generated descriptor tests should confirm the fieldpath option, and integration tests should verify topic/namespace preservation through event forwarding.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/event.proto -->
