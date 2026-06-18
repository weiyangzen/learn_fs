## sources/cloud-native/buildkit/session/upload/upload_grpc.pb.go

Purpose: generated gRPC client/server bindings for the upload service.

Important APIs/types/functions: `UploadClient` exposes `Pull`; `NewUploadClient` wraps a `grpc.ClientConnInterface`; `UploadServer` requires `Pull`; `UnimplementedUploadServer` provides forward-compatible default behavior; `RegisterUploadServer` registers the service; `_Upload_Pull_Handler` adapts server streams; `Upload_ServiceDesc` declares the stream.

Control flow: client `Pull` creates a new stream with the static method name and returns a typed bidirectional stream. Server handler wraps the raw `grpc.ServerStream` and calls `srv.(UploadServer).Pull`.

State and persistence: no persistent state.

Dependencies and integration points: used by `upload.New` and `uploadprovider.Uploader.Register`. Depends on gRPC-Go v1.64.0 or newer.

Risks and test signals: generated code must stay in sync with `upload.proto`. The bidirectional type accepts client sends even if current provider ignores them; future protocol additions should preserve compatibility.
