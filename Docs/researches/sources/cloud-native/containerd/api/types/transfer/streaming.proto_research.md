<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/streaming.proto -->
# sources/cloud-native/containerd/api/types/transfer/streaming.proto

Purpose: source schema for transfer binary stream messages and stream descriptors.

Important APIs/types/functions: `Data`, `WindowUpdate`, `ReadStream`, and `WriteStream` model bytes, flow-control credits, and named stream endpoints with media type.

Control flow: schema comments define stream direction; actual protocol control is in transfer implementation.

State/persistence: transient stream protocol state only.

Dependencies/integration: used by image import/export stream messages and transfer proxy stream creation.

Risks: signed `int32` window updates need validation against negative or overflow behavior. Media type is not constrained by schema.

Test signals: generated binding consistency plus stream protocol tests for flow-control correctness and cancellation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/streaming.proto -->
