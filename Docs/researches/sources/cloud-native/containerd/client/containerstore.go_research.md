<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/containerstore.go -->
# sources/cloud-native/containerd/client/containerstore.go

Purpose: gRPC-backed implementation of the core `containers.Store` interface.

Important APIs/types/functions: `remoteContainers`, `NewRemoteContainerStore`, `Get`, `List`, `list`, `stream`, `Create`, `Update`, `Delete`, `containerToProto`, `containerFromProto`, and `containersFromProto`.

Control flow: `List` prefers `ListStream` and falls back to unary `List` only on unimplemented streaming. `stream` receives until EOF, checks context cancellation, and converts each proto. Create/update/delete wrap gRPC requests and convert errors to native errdefs.

State/persistence: operations persist and retrieve container metadata through the containerd containers service. Conversion preserves IDs, labels, image, runtime/options, spec, snapshotter/key, timestamps, extensions, and sandbox ID.

Dependencies/integration: containers gRPC API, errgrpc, typeurl, protobuf timestamp helpers, field masks.

Risks: `containerFromProto` assumes non-nil container proto. Streaming list can return partial results on context cancellation. Conversion of extensions maps `*Any` directly into `typeurl.Any`, so callers must not mutate unexpectedly. Update with no field paths replaces according to server semantics.

Test signals: unary fallback on unimplemented, context cancellation, proto conversion round trips including extensions/sandbox/timestamps, update masks, and native error conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/containerstore.go -->
