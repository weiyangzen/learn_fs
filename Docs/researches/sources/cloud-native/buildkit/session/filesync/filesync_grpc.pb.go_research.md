<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync_grpc.pb.go -->
# sources/cloud-native/buildkit/session/filesync/filesync_grpc.pb.go

Purpose: generated gRPC client/server bindings for FileSync and FileSend streaming services.

Important APIs, types, and functions: defines `FileSyncClient` streams for `DiffCopy` and `TarStream`, `FileSyncServer` interfaces, stream wrapper types, `RegisterFileSyncServer`, plus `FileSendClient`, `FileSendServer`, and `RegisterFileSendServer` for `BytesMessage` diffcopy.

Control flow and state: stream clients create bidirectional gRPC streams and expose typed send/recv wrappers. Server descriptors route incoming streams to registered implementations.

Dependencies and integration: used by `filesync.go` providers and callers. It depends on fsutil packet generated types and gRPC.

Risks and test signals: service paths and stream message types are compatibility-sensitive. Test through end-to-end session file transfer and generated-code regeneration.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync_grpc.pb.go -->
