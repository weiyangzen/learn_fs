# sources/cloud-native/containerd/api/services/diff/v1/diff_grpc.pb.go

Generated gRPC bindings for the Diff service, built under `!no_grpc`. It exposes unary client/server adapters for `Apply` and `Diff` plus service registration metadata.

Important APIs are `DiffClient`, `NewDiffClient`, `DiffServer`, `UnimplementedDiffServer`, `UnsafeDiffServer`, `RegisterDiffServer`, internal unary handlers, and `Diff_ServiceDesc`. Client methods call `cc.Invoke` with full method names `/containerd.services.diff.v1.Diff/Apply` and `/Diff`.

Control flow is generated unary dispatch. Server handlers allocate request structs, decode them, call the implementation directly or through a `grpc.UnaryServerInterceptor`, and pass `UnaryServerInfo` with method names. No streaming paths exist, and `Diff_ServiceDesc.Streams` is empty.

No durable state is kept. Runtime state is limited to gRPC contexts and connections. Dependencies are `context`, gRPC, and `codes/status`. Integration points include containerd's API server, diff implementation registration, interceptors, and protobuf messages in `diff.pb.go`.

Risks include missing `UnimplementedDiffServer` embedding causing forward-compatibility compile issues, interceptor behavior hiding service errors, and stale generated code after proto edits. Test signals include compile with gRPC-Go v1.32+, service registration, unary request/response round trips, interceptor coverage, and parity with ttrpc bindings.
