# sources/cloud-native/containerd/api/services/events/v1/events_grpc.pb.go

Generated gRPC bindings for the Events service under `!no_grpc`. It exposes unary publish/forward calls and a server-streaming subscribe call.

Important APIs are `EventsClient`, `NewEventsClient`, `Events_SubscribeClient`, `EventsServer`, `Events_SubscribeServer`, `UnimplementedEventsServer`, `UnsafeEventsServer`, `RegisterEventsServer`, handlers for `Publish`, `Forward`, and `Subscribe`, and `Events_ServiceDesc`. Subscribe returns `types.Envelope` messages through a typed `Recv` client.

Control flow follows generated gRPC patterns. Unary calls use `cc.Invoke` and server handlers support unary interceptors. `Subscribe` creates a stream, sends one `SubscribeRequest`, closes the send side, then receives envelopes. The server stream handler receives the initial request and delegates to `srv.Subscribe` with a send wrapper.

No persistence is implemented. Runtime state is in gRPC streams, contexts, and the event service. Dependencies are `context`, containerd `api/types`, gRPC, `codes/status`, and `emptypb`. Integration points include containerd event service registration, subscribers, interceptors, namespace/auth handling, and protobuf messages.

Risks include subscriber stream leaks, backpressure blocking event dispatch, missing namespace filters exposing cross-namespace events, forward compatibility compile issues without embedding `UnimplementedEventsServer`, and streaming methods bypassing unary interceptors. Test signals should include publish/forward unary behavior, subscribe stream cancellation, namespace filtering, interceptor coverage, and service descriptor registration.
