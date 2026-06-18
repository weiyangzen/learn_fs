# sources/cloud-native/containerd/core/events/events.go

Purpose: core event model and publish/forward/subscribe interfaces.

Important APIs/types: `Envelope` holds timestamp, namespace, topic, and typeurl-encoded event payload. `Envelope.Field` implements filter access for namespace, topic, and nested event fields when the decoded event implements `Field([]string)`. `Publisher`, `Forwarder`, and `Subscriber` define event bus contracts.

Control flow and state: `Field` is read-only and decodes the `typeurl.Any` payload on demand for `event.*` lookups.

Dependencies and integration: typeurl for typed event encoding and containerd filter adaptors via the `Field` convention.

Risks: timestamp is intentionally not filterable here. Decode errors or event types lacking a field adaptor make `event.*` absent. Repeated field matching can repeatedly unmarshal payloads.

Test signals: exchange filter tests exercise `Envelope.Field` indirectly for topics and event fields.
