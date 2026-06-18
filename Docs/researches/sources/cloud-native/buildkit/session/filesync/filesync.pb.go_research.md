<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync.pb.go -->
# sources/cloud-native/buildkit/session/filesync/filesync.pb.go

Purpose: generated protobuf message and descriptor definitions for filesync's `BytesMessage`.

Important APIs, types, and functions: defines `BytesMessage` with `Data []byte`, standard protobuf methods/getters, raw descriptor state, and file initialization for `filesync.proto`.

Control flow and state: descriptor state is initialized once; message state is per stream message.

Dependencies and integration: generated from `filesync.proto`, imports fsutil wire proto descriptors because services stream fsutil packets. Used by FileSend streaming and `streamWriterCloser`.

Risks and test signals: generated file should not be edited manually. Message size and chunking behavior are handled in handwritten stream code. Test through filesync stream round trips.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/filesync.pb.go -->
