# sources/cloud-native/containerd/api/services/events/v1/doc.go

Package-level file for the `events` API package. It documents that the package defines event publishing and subscription services, imports containerd API `types`, and provides a deprecated alias `Envelope = types.Envelope`.

The only API is the type alias `Envelope`, retained for compatibility while directing users to `types.Envelope`. There is no function control flow, persistence, or mutable state.

Dependencies are `github.com/containerd/containerd/api/types`. Integration points include older callers that imported `events.Envelope`, generated event protobuf files that use `types.Envelope`, and migration paths to the canonical type.

Risks are compatibility-related: removing the alias would break downstream consumers, while continued use can hide the preferred package boundary. Test signals include compilation of legacy imports and static/deprecation checks encouraging `types.Envelope`.
