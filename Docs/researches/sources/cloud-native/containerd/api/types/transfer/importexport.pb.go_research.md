<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/importexport.pb.go -->
# sources/cloud-native/containerd/api/types/transfer/importexport.pb.go

Purpose: generated bindings for tar-stream import/export endpoints in transfer operations.

Important APIs/types/functions: `ImageImportStream` carries stream ID, media type, and force-compress flag. `ImageExportStream` carries stream ID, media type, platform list, all-platforms flag, skip Docker compatibility manifest flag, and skip non-distributable flag.

Control flow: generated protobuf methods only.

State/persistence: messages identify binary streams managed by the transfer streaming protocol; exported/imported content persists in content/image stores outside this message.

Dependencies/integration: imports platform proto types; paired with `streaming.proto` stream control messages and transfer service.

Risks: stream IDs must match active binary streams. Platform/all-platforms flags can conflict semantically and must be resolved by implementation. `ForceCompress` and non-distributable filtering affect reproducibility and distribution legality.

Test signals: import/export tests should cover stream lifecycle, media type handling, compression, platform filters, compatibility manifest generation, and non-distributable exclusion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/importexport.pb.go -->
