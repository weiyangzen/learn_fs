# sources/cloud-native/containerd/api/services/events/v1/events.proto

Protocol definition for containerd's event publishing, forwarding, and subscription service.

The `Events` service exposes unary `Publish` and `Forward` plus server-streaming `Subscribe`. `PublishRequest` carries a topic and an `Any` event payload; the service is expected to wrap it in a timestamped envelope with namespace from context. `ForwardRequest` carries an already packaged `containerd.types.Envelope`. `SubscribeRequest` carries filter strings and can receive all namespaces unless the caller filters by namespace.

Control flow is declarative. Implementations publish new events, forward existing envelopes without retimestamping/re-namespacing, and stream matching envelopes to subscribers until completion or cancellation.

Persistence is not specified; event retention/buffering is implementation-dependent. Dependencies are protobuf `Any`/`Empty` and containerd `types/event.proto`. Integration points include namespace context handling, event broker, consumers watching task/image/content changes, generated Go bindings, and gRPC/ttrpc stream transports.

Risks include namespace leakage when subscribers omit namespace filters, malformed filter expressions, large or unknown `Any` payloads, subscriber backpressure, and timestamp correctness for forwarded events. Test signals should include publish wrapping, forward preservation, namespace filtering, multi-filter behavior, stream cancellation/backpressure, and payload type compatibility.
