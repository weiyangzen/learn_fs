<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/progress.pb.go -->
# sources/cloud-native/containerd/api/types/transfer/progress.pb.go

Purpose: generated binding for transfer progress events.

Important APIs/types/functions: `Progress` includes event, name, parent names, current progress, total, and optional content descriptor.

Control flow: generated methods only; event ordering and aggregation happen in transfer implementations.

State/persistence: progress messages are transient telemetry, not authoritative content state. Descriptor field can identify content blobs associated with progress.

Dependencies/integration: imports `types/descriptor.proto`; used by transfer service streams or callbacks.

Risks: progress/total can be unknown or non-monotonic depending on source. Parent relationships are string-based and require consumer interpretation.

Test signals: progress stream tests should cover event ordering, descriptor mapping, unknown totals, cancellation, and parent aggregation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/progress.pb.go -->
