# sources/cloud-native/containerd/api/services/containers/v1/containers_grpc.pb.go

Generated gRPC bindings for the Containers service, built only when the `no_grpc` build tag is not set. The file adapts the protobuf contract into gRPC client interfaces, server interfaces, stream wrappers, method handlers, and `grpc.ServiceDesc`.

Important APIs are `ContainersClient`, `NewContainersClient`, unary client methods `Get`, `List`, `Create`, `Update`, `Delete`, streaming client `ListStream`, `ContainersServer`, `UnimplementedContainersServer`, `UnsafeContainersServer`, `RegisterContainersServer`, and `Containers_ServiceDesc`. `ListStream` uses `grpc.NewStream`, sends one `ListContainersRequest`, closes the send side, and returns a `Recv` wrapper over `ListContainerMessage`.

Server control flow is the standard generated pattern: unary handlers allocate request structs, decode with `dec`, call the service directly or through a `grpc.UnaryServerInterceptor`, and populate `UnaryServerInfo.FullMethod`. The stream handler receives the initial request and delegates to `srv.ListStream` with a send-only wrapper.

The file has no durable state. Runtime state is held in connections, contexts, and streams. Dependencies are `context`, `google.golang.org/grpc`, `codes/status`, and `emptypb`. Integration points are containerd daemon gRPC registration, clients using `grpc.ClientConnInterface`, interceptors for auth/namespace/metrics, and the protobuf message file.

Risks include client leaks if streaming responses are not drained/canceled, interceptor behavior changing error paths, forward-compatibility compile failures if implementations do not embed `UnimplementedContainersServer`, and divergence if edited rather than regenerated. Test signals include compile with gRPC-Go v1.32+, service registration smoke tests, interceptor coverage, unary error propagation, and `ListStream` cancellation/backpressure tests.
