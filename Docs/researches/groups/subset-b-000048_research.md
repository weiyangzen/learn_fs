# Research: subset-b-000048

Grouped research for containerd service API files under `sources/cloud-native/containerd/api/services`. Each section preserves the source path and is intended to be split into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/containers/v1/containers.pb.go -->
# sources/cloud-native/containerd/api/services/containers/v1/containers.pb.go

Generated Go protobuf bindings for the Containers service messages. The file materializes the `containers.proto` contract as concrete Go structs, getters, descriptor metadata, and one-time protobuf reflection initialization for package `containers`.

Important API surface: `Container`, nested `Container_Runtime`, request/response types for `Get`, `List`, `ListStream`, `Create`, `Update`, and `Delete`, plus `File_services_containers_v1_containers_proto`. `Container` carries identity, labels, image reference, runtime `Any` options, runtime-specific spec, snapshotter/snapshot key, timestamps, extension `Any` map, and sandbox id. `UpdateContainerRequest` includes a `fieldmaskpb.FieldMask`.

Control flow is generated message plumbing: `Reset`, `String`, `ProtoReflect`, deprecated `Descriptor`, and nil-safe `Get*` accessors. Package `init` calls `file_services_containers_v1_containers_proto_init`, which builds a `protoimpl.TypeBuilder`, assigns exporters when unsafe protobuf mode is disabled, compresses raw descriptors through `sync.Once`, and then nils raw descriptor/type slices after building.

State is per-message in struct fields plus package-global descriptor caches. Persistence is not implemented here; the metadata persistence semantics belong to the service implementation behind this API. Dependencies include protobuf reflection/runtime, `anypb`, `emptypb`, `fieldmaskpb`, `timestamppb`, `reflect`, and `sync`.

Integration points are the generated gRPC/ttrpc stubs, container metadata services, snapshot and task creation flows, and clients that pack runtime specs/extensions into `Any`. Risks are descriptor drift from hand edits, assuming getters enforce validation, map-size constraints not enforced in generated code, and field-mask semantics that must be honored by implementations. Test signals should include protobuf round-trip compatibility, nil getter behavior, field-mask update behavior in the real service, and regeneration checks from `containers.proto`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/containers/v1/containers.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/containers/v1/containers.proto -->
# sources/cloud-native/containerd/api/services/containers/v1/containers.proto

Protocol definition for containerd's container metadata service. It defines a state-independent container object used for management, resource pinning, and as base parameters for task/process creation.

The `Containers` service exposes `Get`, `List`, server-streaming `ListStream`, `Create`, `Update`, and `Delete`. `Container` is the central type: immutable `id`, mutable label map, image reference, `Runtime` name/options, runtime-specific `spec`, snapshotter, GC-pinning `snapshot_key`, creation/update timestamps, extension map, and sandbox id. Requests wrap ids, filters, full container payloads, and `FieldMask` updates.

Control flow is declarative RPC schema. Implementations must enforce the documented behavior: list filters are ORed using containerd filter syntax, empty filters return all containers, `id` cannot be updated, label updates replace the whole map unless a map-key field path is used, and empty update masks apply all fields.

The proto itself has no persistence, but it defines durable metadata shape. Snapshot references affect garbage collection because `snapshot_key` pins snapshots. Dependencies are well-known protobuf `Any`, `Empty`, `FieldMask`, and `Timestamp`. Integration points include container metadata stores, runtime task creation, snapshot services, image metadata, sandbox orchestration, generated Go protobuf bindings, and gRPC/ttrpc transports.

Risks center on overloading the container object with runtime state, incorrect field-mask application, stale snapshot/image/spec combinations after updates, unbounded/oversized labels or extensions if implementations skip validation, and cross-version `Any` type compatibility. Test signals should cover CRUD semantics, filter OR behavior, list streaming equivalence to list, immutable id rejection, map-key field mask updates, snapshot GC pinning, and generated-code regeneration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/containers/v1/containers.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/containers/v1/containers_grpc.pb.go -->
# sources/cloud-native/containerd/api/services/containers/v1/containers_grpc.pb.go

Generated gRPC bindings for the Containers service, built only when the `no_grpc` build tag is not set. The file adapts the protobuf contract into gRPC client interfaces, server interfaces, stream wrappers, method handlers, and `grpc.ServiceDesc`.

Important APIs are `ContainersClient`, `NewContainersClient`, unary client methods `Get`, `List`, `Create`, `Update`, `Delete`, streaming client `ListStream`, `ContainersServer`, `UnimplementedContainersServer`, `UnsafeContainersServer`, `RegisterContainersServer`, and `Containers_ServiceDesc`. `ListStream` uses `grpc.NewStream`, sends one `ListContainersRequest`, closes the send side, and returns a `Recv` wrapper over `ListContainerMessage`.

Server control flow is the standard generated pattern: unary handlers allocate request structs, decode with `dec`, call the service directly or through a `grpc.UnaryServerInterceptor`, and populate `UnaryServerInfo.FullMethod`. The stream handler receives the initial request and delegates to `srv.ListStream` with a send-only wrapper.

The file has no durable state. Runtime state is held in connections, contexts, and streams. Dependencies are `context`, `google.golang.org/grpc`, `codes/status`, and `emptypb`. Integration points are containerd daemon gRPC registration, clients using `grpc.ClientConnInterface`, interceptors for auth/namespace/metrics, and the protobuf message file.

Risks include client leaks if streaming responses are not drained/canceled, interceptor behavior changing error paths, forward-compatibility compile failures if implementations do not embed `UnimplementedContainersServer`, and divergence if edited rather than regenerated. Test signals include compile with gRPC-Go v1.32+, service registration smoke tests, interceptor coverage, unary error propagation, and `ListStream` cancellation/backpressure tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/containers/v1/containers_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/containers/v1/containers_ttrpc.pb.go -->
# sources/cloud-native/containerd/api/services/containers/v1/containers_ttrpc.pb.go

Generated ttrpc bindings for the Containers service. This is the lightweight containerd transport counterpart to the gRPC file and exposes the same logical service methods through `github.com/containerd/ttrpc`.

Important APIs are `TTRPCContainersService`, `TTRPCContainers_ListStreamServer`, `RegisterTTRPCContainersService`, `TTRPCContainersClient`, `NewTTRPCContainersClient`, and the stream client/server wrappers. Unary methods are registered in a `map[string]ttrpc.Method`; `ListStream` is registered in a `map[string]ttrpc.Stream` with `StreamingServer: true`.

Control flow is straightforward generated dispatch. Registration unmarshals each unary request into a stack-local request value and calls the service implementation. The streaming handler receives the initial list request from the stream, then delegates to `svc.ListStream`. Client methods call `client.Call` for unary RPCs and `client.NewStream` for streaming.

There is no persistence in this file. State lives in ttrpc clients, contexts, and active streams. Dependencies are `context`, `github.com/containerd/ttrpc`, and `emptypb`, plus message types from `containers.pb.go`. Integration points include containerd internal services where ttrpc is preferred over gRPC, shim/client paths, and generated protobuf types.

Risks include method-name drift from proto changes, stream lifetime leaks when callers stop reading without canceling context, lack of the gRPC file's explicit unimplemented-server forward compatibility wrapper, and regeneration mismatches. Test signals should exercise ttrpc registration, unary call round trips, stream receive behavior, context cancellation, and parity with the gRPC service surface.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/containers/v1/containers_ttrpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/containers/v1/doc.go -->
# sources/cloud-native/containerd/api/services/containers/v1/doc.go

Package declaration and license carrier for `containers`. It establishes the Go package for generated and hand-written files under the Containers v1 API directory.

There are no exported functions, types, constants, or runtime control paths in this file. Its practical role is package-level integration: keeping the directory a normal Go package even aside from generated files and providing the Apache license header.

State and persistence are absent. Dependencies are absent. Integration is with `containers.pb.go`, `containers_grpc.pb.go`, `containers_ttrpc.pb.go`, and any downstream code importing `github.com/containerd/containerd/api/services/containers/v1`.

Risk is low, but package-name changes would break imports and generated file consistency. Test signals are compile/package discovery and license/header checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/containers/v1/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/content/v1/content.pb.go -->
# sources/cloud-native/containerd/api/services/content/v1/content.pb.go

Generated Go protobuf bindings for the Content service. It turns `content.proto` into Go structs, enum helpers, getters, reflection descriptors, and initialization metadata for content-addressable storage RPCs.

Important API surface includes enum `WriteAction` with `STAT`, `WRITE`, and `COMMIT`; metadata type `Info`; ingestion `Status`; request/response types for `Info`, `Update`, `List`, `Delete`, `Read`, `Status`, `ListStatuses`, `Write`, and `Abort`; and `File_services_content_v1_content_proto`. `WriteContentRequest` carries action, ref, total, expected digest, offset, data, and labels. `WriteContentResponse` returns action, timestamps, offset, total, and digest.

Control flow is generated protobuf mechanics: enum string/descriptor helpers, message `Reset`, `ProtoReflect`, deprecated descriptors, nil-safe getters, raw descriptor GZIP via `sync.Once`, exporter setup when unsafe protobuf mode is disabled, and `protoimpl.TypeBuilder` construction in `init`.

State is message-local plus package-global descriptor caches. The file does not persist content or ingestion status; it defines the wire shape consumed by content-store implementations. Dependencies include protobuf runtime/reflection, `emptypb`, `fieldmaskpb`, `timestamppb`, `reflect`, and `sync`.

Integration points are content store services, gRPC/ttrpc bindings, ingest writers/readers, label metadata update code, and clients using digest/ref protocols. Risks include assuming generated code validates digest/offset/label limits, incorrect enum default handling (`STAT` is numeric zero while comments say write is default behavior), field-mask misuse around immutable fields, and compatibility drift if generated artifacts are stale. Test signals should cover marshal round trips, enum values, nil getters, write stream semantics in the service, immutable metadata rejection, and proto regeneration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/content/v1/content.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/content/v1/content.proto -->
# sources/cloud-native/containerd/api/services/content/v1/content.proto

Protocol definition for containerd's content-addressable storage service. It describes metadata lookup/update, listing, deletion, ranged reads, ingest status, streaming writes, and abort behavior.

The `Content` service exposes unary `Info`, `Update`, `Delete`, `Status`, `ListStatuses`, `Abort`; server-streaming `List` and `Read`; and bidirectional-streaming `Write`. Data types include `Info` for committed blob metadata, `Status` for active ingests, `WriteAction` for stream behavior, and request/response wrappers. `WriteContentRequest` is the main state-transition message for ingests: it can stat, write at offset, or commit while validating total size and digest.

Control flow is defined by RPC semantics. `List` streams chunks of `Info`. `Read` streams one or more byte chunks from digest/offset/size. `Write` starts or resumes a ref, permits only one active stream per ref, expects non-overlapping offsets, can stat while holding the lock, and terminates on commit. `Abort` cancels a ref and frees resources.

Persistence is implemented elsewhere, but the proto defines durable content metadata and active ingest status. Dependencies are `Empty`, `FieldMask`, and `Timestamp`. Integration points include content store backends, image pull/unpack flows, diff uploads, garbage collection, label indexing, and generated transports.

Risks include ambiguous handling of zero-valued `WriteAction`, offset overlap/concurrency races, digest/size validation holes, large streaming datasets, regex/filter cost in status listing, and incorrect updates to immutable fields. Test signals should cover streaming read/write, commit validation, duplicate digest failures, abort cleanup, update masks, label limits, list filtering, and cancellation/backpressure behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/content/v1/content.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/content/v1/content_grpc.pb.go -->
# sources/cloud-native/containerd/api/services/content/v1/content_grpc.pb.go

Generated gRPC bindings for the Content service behind the `!no_grpc` build tag. It exposes typed clients, servers, stream wrappers, unary handlers, stream handlers, and `Content_ServiceDesc`.

Important APIs are `ContentClient`, `NewContentClient`, unary methods `Info`, `Update`, `Delete`, `Status`, `ListStatuses`, `Abort`, server-streaming `List` and `Read`, bidirectional `Write`, `ContentServer`, `UnimplementedContentServer`, `UnsafeContentServer`, `RegisterContentServer`, and stream interfaces for list/read/write.

Control flow follows gRPC generated conventions. Unary client methods call `cc.Invoke`; `List` and `Read` create streams, send one request, close send, then expose `Recv`. `Write` creates a bidirectional stream and leaves send/receive sequencing to the caller. Server handlers decode unary requests or receive stream initial requests, wrap streams with typed `Send`/`Recv` helpers, and call interceptors for unary methods.

The file has no persistence. Runtime state is in contexts, `grpc.ClientStream`/`ServerStream`, and service implementations. Dependencies include `context`, gRPC, `codes/status`, and `emptypb`. Integration points include the containerd API server, content-store implementation, interceptors for namespace/auth/observability, and generated protobuf messages.

Risks include deadlocks or leaks if bidirectional `Write` callers do not coordinate send/receive/close, unbounded memory if list/read consumers do not drain, interceptor coverage gaps for streaming methods, and compile breakage when servers omit `UnimplementedContentServer`. Test signals should include unary dispatch, stream cancellation, write half-close behavior, registration metadata, and parity with ttrpc and proto definitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/content/v1/content_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/content/v1/content_ttrpc.pb.go -->
# sources/cloud-native/containerd/api/services/content/v1/content_ttrpc.pb.go

Generated ttrpc bindings for the Content service. It maps the same content-store API onto containerd's lightweight ttrpc transport, including unary, server-streaming, and bidirectional streaming methods.

Important APIs are `TTRPCContentService`, stream server interfaces for `List`, `Read`, and `Write`, `RegisterTTRPCContentService`, `TTRPCContentClient`, `NewTTRPCContentClient`, and corresponding stream clients. Registration creates unary method handlers for `Info`, `Update`, `Delete`, `Status`, `ListStatuses`, and `Abort`, plus stream handlers for `List`, `Read`, and `Write`.

Control flow is generated dispatch. Unary handlers unmarshal into request structs and call the service. `List`/`Read` stream handlers receive one initial request before delegating. `Write` delegates immediately with a typed stream that supports both `Send` and `Recv`. Client methods use `client.Call` or `client.NewStream`; write streams are opened with no initial request.

The file does not persist content; active stream state lives in ttrpc runtime and service code. Dependencies are `context`, `github.com/containerd/ttrpc`, `emptypb`, and generated message types. Integration points include internal containerd clients, shims or lower-overhead IPC paths, and content services that also expose gRPC.

Risks include bidirectional-stream ordering bugs, context cancellation not freeing active ingests, method-name drift after proto edits, no generated unimplemented server type, and parity gaps with gRPC behavior. Test signals should include ttrpc unary round trips, server-stream read/list behavior, bidirectional write commit/abort paths, cancellation, and transport parity with gRPC.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/content/v1/content_ttrpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/content/v1/doc.go -->
# sources/cloud-native/containerd/api/services/content/v1/doc.go

Package declaration and license carrier for the `content` API package. It anchors the generated protobuf, gRPC, and ttrpc files in a single Go package.

No functions, types, control flow, state, persistence, or imports are defined here. Its integration role is package naming and license consistency for downstream imports of the content service API.

Dependencies are absent. Integration points are the generated content service files and external code importing the package path. Risks are limited to accidental package renaming or deletion, which would break builds. Test signals are package compilation and repository license checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/content/v1/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/diff/v1/diff.pb.go -->
# sources/cloud-native/containerd/api/services/diff/v1/diff.pb.go

Generated Go protobuf bindings for the Diff service. It defines request/response message structs, nil-safe getters, descriptor metadata, and reflection initialization for filesystem diff apply/create operations.

Important APIs are `ApplyRequest`, `ApplyResponse`, `DiffRequest`, `DiffResponse`, and `File_services_diff_v1_diff_proto`. `ApplyRequest` carries a content `Descriptor`, target `Mount` list, arbitrary `Any` payloads, and `sync_fs`. `DiffRequest` carries left/right mount sets, media type, pre-commit content ref, labels, and `source_date_epoch`. Responses return descriptors for applied or generated diff content.

Control flow is generated message plumbing: `Reset`, `String`, `ProtoReflect`, deprecated descriptors, getters, raw descriptor compression through `sync.Once`, unsafe-disabled exporters, and `protoimpl.TypeBuilder` setup. There is no service execution logic in this file.

State is limited to message fields and package-level descriptor caches. Persistence is external: generated diff content is stored through the content store using refs/descriptors. Dependencies include containerd API `types.Descriptor` and `types.Mount`, protobuf runtime/reflection, `anypb`, `timestamppb`, `reflect`, and `sync`.

Integration points include diff service implementations, content storage, snapshot/mount handling, archive decompression/apply code, reproducible build timestamp handling, and generated transports. Risks include treating request descriptors/mounts as validated, mishandling `sync_fs` cost/semantics, timestamp reproducibility edge cases, and generated descriptor drift. Test signals should cover proto round trips, map payload preservation, descriptor field numbers, apply/diff service validation, and regeneration from `diff.proto`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/diff/v1/diff.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/diff/v1/diff.proto -->
# sources/cloud-native/containerd/api/services/diff/v1/diff.proto

Protocol definition for the Diff service, which applies archive diffs onto mounts and creates new diff content from mount comparisons.

The service exposes two unary RPCs: `Apply(ApplyRequest) returns (ApplyResponse)` and `Diff(DiffRequest) returns (DiffResponse)`. `ApplyRequest` references the diff blob by `containerd.types.Descriptor`, target mounts, optional `Any` payloads, and a `sync_fs` flag. `DiffRequest` provides left and right mount sets, output media type, content-store ref, labels, and `source_date_epoch` for reproducibility. Responses return descriptors for the applied uncompressed content or generated diff.

Control flow is schema-level. Implementations are expected to fetch content by descriptor, decompress/extract when applying, compare mount trees when diffing, and commit generated content to the content store under the provided ref.

State and persistence are external but implied: content descriptors identify blobs, refs coordinate pre-commit uploads, and labels persist with generated content. Dependencies include protobuf `Any`/`Timestamp` plus containerd `Descriptor` and `Mount` types. Integration points include content service, snapshot mounts, archive apply/diff code, reproducible build tooling, and generated gRPC/ttrpc bindings.

Risks include unsafe mount handling, descriptor/content mismatch, expensive or partial `sync_fs`, reproducibility mismatches around source date epoch and whiteout timestamps, and labels/ref validation gaps. Test signals should include apply of compressed/uncompressed diffs, diff output media type and digest validation, source-date reproducibility, sync behavior, and invalid mount/descriptor errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/diff/v1/diff.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/diff/v1/diff_grpc.pb.go -->
# sources/cloud-native/containerd/api/services/diff/v1/diff_grpc.pb.go

Generated gRPC bindings for the Diff service, built under `!no_grpc`. It exposes unary client/server adapters for `Apply` and `Diff` plus service registration metadata.

Important APIs are `DiffClient`, `NewDiffClient`, `DiffServer`, `UnimplementedDiffServer`, `UnsafeDiffServer`, `RegisterDiffServer`, internal unary handlers, and `Diff_ServiceDesc`. Client methods call `cc.Invoke` with full method names `/containerd.services.diff.v1.Diff/Apply` and `/Diff`.

Control flow is generated unary dispatch. Server handlers allocate request structs, decode them, call the implementation directly or through a `grpc.UnaryServerInterceptor`, and pass `UnaryServerInfo` with method names. No streaming paths exist, and `Diff_ServiceDesc.Streams` is empty.

No durable state is kept. Runtime state is limited to gRPC contexts and connections. Dependencies are `context`, gRPC, and `codes/status`. Integration points include containerd's API server, diff implementation registration, interceptors, and protobuf messages in `diff.pb.go`.

Risks include missing `UnimplementedDiffServer` embedding causing forward-compatibility compile issues, interceptor behavior hiding service errors, and stale generated code after proto edits. Test signals include compile with gRPC-Go v1.32+, service registration, unary request/response round trips, interceptor coverage, and parity with ttrpc bindings.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/diff/v1/diff_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/diff/v1/diff_ttrpc.pb.go -->
# sources/cloud-native/containerd/api/services/diff/v1/diff_ttrpc.pb.go

Generated ttrpc bindings for the Diff service. It provides the lightweight transport adapter for the unary `Apply` and `Diff` RPCs.

Important APIs are `TTRPCDiffService`, `RegisterTTRPCDiffService`, private client `ttrpcdiffClient`, and `NewTTRPCDiffClient`, which returns the service interface implemented by the client. Registration installs two ttrpc method handlers keyed by `Apply` and `Diff`.

Control flow is generated unary dispatch: handlers unmarshal into `ApplyRequest` or `DiffRequest`, call the service implementation, and return its response. Client methods allocate response structs and use `client.Call` with service name `containerd.services.diff.v1.Diff`.

The file has no persistence and no long-lived state beyond the ttrpc client pointer. Dependencies are `context`, `github.com/containerd/ttrpc`, and generated message types. Integration points include containerd internal IPC, diff service implementations, and transport parity with gRPC.

Risks include method-name drift, no generated unimplemented-server guard, and client construction returning `TTRPCDiffService`, which is convenient but can blur client/server roles in tests. Test signals should include ttrpc registration, unary round trips, error propagation, context cancellation, and parity with gRPC method names and proto messages.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/diff/v1/diff_ttrpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/diff/v1/doc.go -->
# sources/cloud-native/containerd/api/services/diff/v1/doc.go

Package declaration and license carrier for the `diff` service API package.

No runtime APIs, control flow, state, persistence, or imports are defined. The file integrates with generated protobuf/gRPC/ttrpc files by fixing the package name and preserving licensing in the directory.

Risks are limited to accidental package-name mismatch or removal, both of which would break generated-file package cohesion. Test signals are Go package compilation and license checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/diff/v1/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/events/v1/doc.go -->
# sources/cloud-native/containerd/api/services/events/v1/doc.go

Package-level file for the `events` API package. It documents that the package defines event publishing and subscription services, imports containerd API `types`, and provides a deprecated alias `Envelope = types.Envelope`.

The only API is the type alias `Envelope`, retained for compatibility while directing users to `types.Envelope`. There is no function control flow, persistence, or mutable state.

Dependencies are `github.com/containerd/containerd/api/types`. Integration points include older callers that imported `events.Envelope`, generated event protobuf files that use `types.Envelope`, and migration paths to the canonical type.

Risks are compatibility-related: removing the alias would break downstream consumers, while continued use can hide the preferred package boundary. Test signals include compilation of legacy imports and static/deprecation checks encouraging `types.Envelope`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/events/v1/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/events/v1/events.pb.go -->
# sources/cloud-native/containerd/api/services/events/v1/events.pb.go

Generated Go protobuf bindings for the Events service messages and descriptors. It defines publish, forward, and subscribe request types and ties the service to `types.Envelope`.

Important APIs are `PublishRequest` with topic and `Any` event, `ForwardRequest` with a prebuilt `types.Envelope`, `SubscribeRequest` with filters, and `File_services_events_v1_events_proto`. Accessors are nil-safe and return zero values for missing receivers.

Control flow is generated protobuf plumbing: `Reset`, `String`, `ProtoReflect`, deprecated `Descriptor`, getters, raw descriptor compression via `sync.Once`, exporter assignment for safe mode, and `protoimpl.TypeBuilder` initialization.

State is limited to message fields and descriptor caches. The file does not store events or manage subscriptions. Dependencies include containerd `api/types`, protobuf runtime/reflection, `anypb`, `emptypb`, `reflect`, and `sync`. Integration points are event broker implementations, generated gRPC/ttrpc transports, topic publishers, namespace-aware envelopes, and subscribers using filter syntax.

Risks include assuming generated code validates topic/filter syntax or `Any` payload types, stale descriptors after proto edits, and namespace semantics being enforced only by service implementation. Test signals should include protobuf round trips, `Any` payload packing/unpacking, envelope forwarding compatibility, filter handling in the event service, and regeneration from `events.proto`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/events/v1/events.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/events/v1/events.proto -->
# sources/cloud-native/containerd/api/services/events/v1/events.proto

Protocol definition for containerd's event publishing, forwarding, and subscription service.

The `Events` service exposes unary `Publish` and `Forward` plus server-streaming `Subscribe`. `PublishRequest` carries a topic and an `Any` event payload; the service is expected to wrap it in a timestamped envelope with namespace from context. `ForwardRequest` carries an already packaged `containerd.types.Envelope`. `SubscribeRequest` carries filter strings and can receive all namespaces unless the caller filters by namespace.

Control flow is declarative. Implementations publish new events, forward existing envelopes without retimestamping/re-namespacing, and stream matching envelopes to subscribers until completion or cancellation.

Persistence is not specified; event retention/buffering is implementation-dependent. Dependencies are protobuf `Any`/`Empty` and containerd `types/event.proto`. Integration points include namespace context handling, event broker, consumers watching task/image/content changes, generated Go bindings, and gRPC/ttrpc stream transports.

Risks include namespace leakage when subscribers omit namespace filters, malformed filter expressions, large or unknown `Any` payloads, subscriber backpressure, and timestamp correctness for forwarded events. Test signals should include publish wrapping, forward preservation, namespace filtering, multi-filter behavior, stream cancellation/backpressure, and payload type compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/events/v1/events.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/events/v1/events_grpc.pb.go -->
# sources/cloud-native/containerd/api/services/events/v1/events_grpc.pb.go

Generated gRPC bindings for the Events service under `!no_grpc`. It exposes unary publish/forward calls and a server-streaming subscribe call.

Important APIs are `EventsClient`, `NewEventsClient`, `Events_SubscribeClient`, `EventsServer`, `Events_SubscribeServer`, `UnimplementedEventsServer`, `UnsafeEventsServer`, `RegisterEventsServer`, handlers for `Publish`, `Forward`, and `Subscribe`, and `Events_ServiceDesc`. Subscribe returns `types.Envelope` messages through a typed `Recv` client.

Control flow follows generated gRPC patterns. Unary calls use `cc.Invoke` and server handlers support unary interceptors. `Subscribe` creates a stream, sends one `SubscribeRequest`, closes the send side, then receives envelopes. The server stream handler receives the initial request and delegates to `srv.Subscribe` with a send wrapper.

No persistence is implemented. Runtime state is in gRPC streams, contexts, and the event service. Dependencies are `context`, containerd `api/types`, gRPC, `codes/status`, and `emptypb`. Integration points include containerd event service registration, subscribers, interceptors, namespace/auth handling, and protobuf messages.

Risks include subscriber stream leaks, backpressure blocking event dispatch, missing namespace filters exposing cross-namespace events, forward compatibility compile issues without embedding `UnimplementedEventsServer`, and streaming methods bypassing unary interceptors. Test signals should include publish/forward unary behavior, subscribe stream cancellation, namespace filtering, interceptor coverage, and service descriptor registration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/events/v1/events_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/events/v1/events_ttrpc.pb.go -->
# sources/cloud-native/containerd/api/services/events/v1/events_ttrpc.pb.go

Generated ttrpc bindings for the Events service. It provides lightweight unary publish/forward and server-streaming subscribe adapters.

Important APIs are `TTRPCEventsService`, `TTRPCEvents_SubscribeServer`, `RegisterTTRPCEventsService`, `TTRPCEventsClient`, `NewTTRPCEventsClient`, and `TTRPCEvents_SubscribeClient`. Registration installs unary methods `Publish` and `Forward`, plus a `Subscribe` stream with server streaming enabled.

Control flow is generated dispatch. Unary handlers unmarshal request structs and call the service. The subscribe stream handler receives the initial `SubscribeRequest`, then calls `svc.Subscribe` with a typed stream wrapper. Client methods use `client.Call` or `client.NewStream` and expose `Recv` for `types.Envelope`.

There is no persistence or event buffering in this file. State is limited to ttrpc clients, contexts, and active streams. Dependencies are `context`, containerd `api/types`, `github.com/containerd/ttrpc`, `emptypb`, and generated messages. Integration points include internal containerd IPC and event broker implementations.

Risks include stream cancellation/backpressure problems, method-name drift, lack of generated unimplemented-server wrapper, and parity gaps with gRPC behavior. Test signals should cover ttrpc registration, publish/forward calls, subscribe receive/cancel paths, error propagation, and parity with proto and gRPC service names.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/events/v1/events_ttrpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/images/v1/docs.go -->
# sources/cloud-native/containerd/api/services/images/v1/docs.go

Package declaration and license carrier for the `images` API package. Despite the filename `docs.go`, it contains only the package declaration after the standard containerd license header.

There are no functions, types, control flow, state, persistence, imports, or direct dependencies. Its purpose is to keep package documentation/license context and package cohesion for other files in `api/services/images/v1`.

Integration points are generated or hand-written image service API files in the same package and downstream imports of the images API package. Risks are limited to package-name mismatch or accidental deletion causing build/package discovery failures. Test signals are Go package compilation and license/header checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/images/v1/docs.go -->
