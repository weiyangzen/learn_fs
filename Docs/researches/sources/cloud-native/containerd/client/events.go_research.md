<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/events.go -->
# sources/cloud-native/containerd/client/events.go

Purpose: gRPC-backed event publish/forward/subscribe adapter.

Important APIs/types/functions: `EventService` combines publisher, forwarder, subscriber. `NewEventServiceFromClient` returns `eventRemote`. Methods `Publish`, `Forward`, and `Subscribe` marshal typeurl events and protobuf envelopes.

Control flow: publish/forward are single RPCs with native error conversion. Subscribe opens a stream, returns event and error channels, and starts a goroutine receiving envelopes until stream error or context cancellation. It suppresses `context.Canceled` as an error but reports other context errors.

State/persistence: events are transient; envelopes carry timestamp, namespace, topic, and `Any` payload. Goroutine/channel lifecycle is the main local state.

Dependencies/integration: events gRPC API, API `Envelope`, typeurl, protobuf timestamp conversion, core events interfaces.

Risks: returned event channel is not closed in the goroutine, only error channel is closed; consumers must follow documented error-channel termination. Initial subscribe RPC errors are sent without errgrpc conversion. Backpressure on `evq` can block receiver goroutine.

Test signals: publish/forward marshal failures, native error conversion, subscribe initial error, stream EOF/error, context cancel/deadline, channel behavior, and slow consumer backpressure.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/events.go -->
