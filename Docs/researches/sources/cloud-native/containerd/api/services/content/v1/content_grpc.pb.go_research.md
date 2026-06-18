# sources/cloud-native/containerd/api/services/content/v1/content_grpc.pb.go

Generated gRPC bindings for the Content service behind the `!no_grpc` build tag. It exposes typed clients, servers, stream wrappers, unary handlers, stream handlers, and `Content_ServiceDesc`.

Important APIs are `ContentClient`, `NewContentClient`, unary methods `Info`, `Update`, `Delete`, `Status`, `ListStatuses`, `Abort`, server-streaming `List` and `Read`, bidirectional `Write`, `ContentServer`, `UnimplementedContentServer`, `UnsafeContentServer`, `RegisterContentServer`, and stream interfaces for list/read/write.

Control flow follows gRPC generated conventions. Unary client methods call `cc.Invoke`; `List` and `Read` create streams, send one request, close send, then expose `Recv`. `Write` creates a bidirectional stream and leaves send/receive sequencing to the caller. Server handlers decode unary requests or receive stream initial requests, wrap streams with typed `Send`/`Recv` helpers, and call interceptors for unary methods.

The file has no persistence. Runtime state is in contexts, `grpc.ClientStream`/`ServerStream`, and service implementations. Dependencies include `context`, gRPC, `codes/status`, and `emptypb`. Integration points include the containerd API server, content-store implementation, interceptors for namespace/auth/observability, and generated protobuf messages.

Risks include deadlocks or leaks if bidirectional `Write` callers do not coordinate send/receive/close, unbounded memory if list/read consumers do not drain, interceptor coverage gaps for streaming methods, and compile breakage when servers omit `UnimplementedContentServer`. Test signals should include unary dispatch, stream cancellation, write half-close behavior, registration metadata, and parity with ttrpc and proto definitions.
