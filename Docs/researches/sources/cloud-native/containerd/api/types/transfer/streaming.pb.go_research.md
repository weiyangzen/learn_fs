<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/streaming.pb.go -->
# sources/cloud-native/containerd/api/types/transfer/streaming.pb.go

Purpose: generated bindings for the binary stream control protocol used by transfer import/export and callback streams.

Important APIs/types/functions: `Data` carries raw bytes. `WindowUpdate` carries flow-control credit. `ReadStream` identifies client-to-server data streams. `WriteStream` identifies server-to-client data streams. Each has standard generated methods/getters.

Control flow: generated code only; stream flow control and data movement are implemented by transfer stream creator/proxy code.

State/persistence: stream data is transient; no durable state in the message itself. Window updates represent in-flight flow-control state.

Dependencies/integration: package `transfer`; used with import/export and registry auth/log streaming.

Risks: flow-control bugs can deadlock or over-buffer transfers. Raw byte streams need cancellation/error propagation. Stream IDs must be unique and scoped to an operation.

Test signals: streaming tests should cover backpressure, large payloads, EOF/cancel/error behavior, concurrent streams, and media type propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/streaming.pb.go -->
