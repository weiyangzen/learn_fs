<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync.proto -->
# sources/cloud-native/buildkit/session/filesync/filesync.proto

Purpose: protobuf contract for BuildKit session file synchronization.

Important APIs, types, and functions: package `moby.filesync.v1`, Go package `github.com/moby/buildkit/session/filesync`. Imports fsutil wire packet proto. Service `FileSync` has bidirectional streaming RPCs `DiffCopy` and `TarStream` over `fsutil.types.Packet`. Service `FileSend` has bidirectional `DiffCopy` over `BytesMessage`. `BytesMessage` contains `bytes data = 1`.

Control flow and state: schema only. Runtime behavior is implemented in generated gRPC stubs and handwritten filesync/diffcopy code.

Dependencies and integration: ties BuildKit sessions to fsutil's streaming diff protocol and local exporter byte streams.

Risks and test signals: `TarStream` exists in schema and provider method but is not listed in `supportedProtocols`, so callers currently negotiate diffcopy only. Test via generated-code compilation and filesync integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync.proto -->
