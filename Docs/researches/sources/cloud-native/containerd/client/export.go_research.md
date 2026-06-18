<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/export.go -->
# sources/cloud-native/containerd/client/export.go

Purpose: high-level wrapper for exporting images/content as an OCI tar archive, optionally Docker manifest compatible.

Important APIs/types/functions: `Client.Export(ctx, w, opts...)` delegates to `archive.Export` with the client content store.

Control flow: single delegation; archive options drive selection and formatting.

State/persistence: reads from the content store and writes to the provided `io.Writer`; no client metadata mutation.

Dependencies/integration: core images archive exporter and content store accessor.

Risks: writer errors and content-store missing blobs propagate from archive exporter. Large exports depend on caller-provided writer backpressure.

Test signals: archive format tests, writer error propagation, platform option behavior in archive exporter, and missing content errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/export.go -->
