# sources/cloud-native/containerd/core/content/proxy/content_store.go

Purpose: client-side proxy implementing `content.Store` over containerd content gRPC or ttrpc APIs.

Important APIs: `NewContentStore` accepts `contentapi.ContentClient`, `grpc.ClientConnInterface`, `contentapi.TTRPCContentClient`, or `*ttrpc.Client` and returns a `content.Store`. Methods implement `Info`, `Walk`, `Delete`, `ReaderAt`, `Status`, `Update`, `ListStatuses`, `Writer`, and `Abort`. Conversion helpers bridge gRPC client streams to ttrpc-shaped interfaces and convert `content.Info` to/from protobuf.

Control flow and state: read operations call remote unary/streaming APIs and translate errors to native errdefs. `ReaderAt` first calls `Info` to discover size. `Writer` applies writer opts, negotiates a write stream by sending a `STAT` request with ref/size/expected, and returns a `remoteWriter` with initial offset.

Dependencies and integration: core content interfaces, content service protobufs, grpc, ttrpc, protobuf timestamp helpers, OCI descriptors, and `errgrpc`.

Risks: constructor panics on unsupported clients. `infoFromGRPC` trusts digest strings without validation. `Walk` stops immediately on callback errors without remote cancellation beyond stream context. The comment on `Abort` has a stray phrase but implementation is direct.

Test signals: no direct tests in this file; expected to be exercised by service/proxy integration and content testsuite runs.
