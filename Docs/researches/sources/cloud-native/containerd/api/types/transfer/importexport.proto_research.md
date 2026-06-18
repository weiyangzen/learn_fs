<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/importexport.proto -->
# sources/cloud-native/containerd/api/types/transfer/importexport.proto

Purpose: source schema for transfer import/export tar streams.

Important APIs/types/functions: `ImageImportStream` declares a client-to-server raw tar stream with media type and force-compress. `ImageExportStream` declares server-to-client raw tar stream and export filters/options.

Control flow: schema-only; stream direction is documented and implemented by transfer streaming.

State/persistence: stream messages are transient, while content/image records are created or read by the transfer operation.

Dependencies/integration: imports platform types and pairs with `streaming.proto`.

Risks: missing stream validation can deadlock transfers. Media type and platform option combinations must be checked by implementation.

Test signals: bidirectional stream tests, cancellation/error propagation, and archive content validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/importexport.proto -->
