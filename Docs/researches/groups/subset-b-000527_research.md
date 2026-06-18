# Research: subset-b-000527

Grouped research for the BeeGFS protobuf Flex Go outputs generated from `flex.proto`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/go/flex/flex.pb.go -->
# sources/distributed-fs/beegfs-protobuf/go/flex/flex.pb.go

## Purpose

This generated Go file is the protobuf data-model contract for package `flex`, produced by `protoc-gen-go v1.36.2` from `flex.proto` with `//go:build !protoopaque`. It defines the typed messages, enums, reflection metadata, field accessors, oneof wrappers, and builder helpers used by BeeGFS Flex services. The schema models worker-node control traffic, work assignment/status, remote storage target configuration, job request construction, and worker capability advertisement.

The file is generated code and contains no business algorithm beyond protobuf marshaling/reflection support, but the comments and field layout describe the distributed workflow contract between BeeRemote-style controllers and worker nodes such as BeeSync.

## Important APIs, Types, And Functions

The exported enums are protocol-state values:

- `UpdateWorkRequest_NewState`: `UNSPECIFIED` and `CANCELLED`; cancellation is the only single-work state transition exposed by this request type.
- `BulkUpdateWorkRequest_NewState`: `UNSPECIFIED` and `UNCHANGED`; intended for draining or initial node connection workflows where existing work is left unchanged.
- `SyncJob_Operation`: `UNSPECIFIED`, `UPLOAD`, and `DOWNLOAD`.
- `Work_State`: lifecycle states `UNKNOWN`, `CREATED`, `SCHEDULED`, `RUNNING`, `RESCHEDULED`, `ERROR`, `FAILED`, `CANCELLED`, and `COMPLETED`, with comments distinguishing retryable errors from terminal failures/cancellations/completions.
- `UpdateConfigResponse_Result`: `SUCCESS`, `PARTIAL`, and `FAILURE`.

RPC payload messages define the worker-node service contract:

- `HeartbeatRequest` and `HeartbeatResponse` carry readiness and optional `NodeStats`.
- `SubmitWorkRequest` wraps a `WorkRequest`; `SubmitWorkResponse` returns a `Work`.
- `UpdateWorkRequest` identifies work by `job_id` and `request_id` and requests a new state; `UpdateWorkResponse` returns the resulting `Work`.
- `BulkUpdateWorkRequest` and `BulkUpdateWorkResponse` apply a node-wide work-state action and return aggregate success/message details.
- `UpdateConfigRequest` sends a `BeeRemoteNode` plus the full desired list of `RemoteStorageTarget` entries; the comment states omitted RSTs should be deleted.
- `UpdateConfigResponse` returns a result enum and troubleshooting message.
- `GetCapabilitiesRequest` is empty; `GetCapabilitiesResponse` returns `BuildInfo`, recursive `Feature` maps, and `start_timestamp`.

Job and work schema types are the core data model:

- `JobLockedInfo` records precomputed local/remote file state: lock flag, existence, size, mode, local and remote mtimes, stub URL target/path, external ID, and archival status.
- `JobRequestCfg` describes high-level job construction inputs: remote storage target ID, local/remote paths, download/stub/overwrite/flatten/force flags, optional `LockedInfo`, optional scalar fields for `update`, `tagging`, `priority`, `storage_class`, `allow_restore`, `filter_expr`, and a metadata map.
- `WorkRequest` is an assigned work unit with `job_id`, `request_id`, external coordination ID, path, optional `Segment`, RST ID, `stub_local`, optional priority, and a `Type` oneof containing `MockJob`, `SyncJob`, or `BuilderJob`.
- `BuilderJob` creates further job requests and tracks submitted/error counts.
- `MockJob` supports test/simulation work with segment count, file size, external ID, failure injection, locked info, and request config.
- `SyncJob` describes upload/download intent and request options without specifying the execution plan. It includes overwrite, remote path, flatten, locked info, optional update/tagging/storage class/allow restore, and metadata.
- `Work` is the status/result form returned for assigned work. It carries path, IDs, `Work_Status`, repeated `Work_Part`, and a `job_builder` marker.
- `WorkRequest_Segment` identifies inclusive byte offset and part ranges assigned to a worker node.
- `Work_Status` carries `Work_State` plus a status message.
- `Work_Part` represents a parallelizable unit inside a segment, including part number, inclusive offsets, ETag, SHA-256 checksum, and completion flag.

Remote configuration schema types include:

- `BeeRemoteNode` with IDs, addresses, BeeGFS management TLS settings, proxy flag, auth secret, and auth disable flag.
- `RemoteStorageTarget` with ID, name, optional policies, and a `type` oneof for `S3`, `POSIX`, `Azure`, or `Mock`.
- `RemoteStorageTarget_Policies` with `fast_start_max_size`, which controls whether BeeRemote coordinates multipart work itself or lets a single worker handle fast-start work.
- `RemoteStorageTarget_S3` with endpoint URL, partition ID, region, bucket, access key, secret key, and storage class definitions.
- `RemoteStorageTarget_Azure`, currently shaped around an embedded S3-compatible config plus account.
- `RemoteStorageTarget_POSIX` with a local path.
- `RemoteStorageTarget_S3_StorageClass` and nested `Archival` options for retrieval tier, retention days, polling times, and auto-restore.

Every message has generated `Reset`, `String`, `ProtoMessage`, `ProtoReflect`, `Get*`, `Set*`, `Has*`, `Clear*`, and `_builder.Build()` helpers where applicable. Presence-sensitive optional scalar fields are represented as pointers, while protobuf oneofs use generated wrapper structs and `WhichType` helpers for `WorkRequest` and `RemoteStorageTarget`.

Reflection globals and initialization include `File_flex_proto`, `file_flex_proto_rawDesc`, enum/message info arrays, Go type tables, dependency indexes, and `file_flex_proto_init()`. Initialization registers oneof wrappers, builds the descriptor using `protoimpl.TypeBuilder`, then releases raw descriptor/type/dependency slices.

## Control Flow

Runtime control flow in this file is generated protobuf mechanics:

1. Package initialization calls `file_flex_proto_init()`.
2. The initializer exits early if `File_flex_proto` is already populated.
3. It registers the oneof wrapper types for `WorkRequest`, `RemoteStorageTarget`, and optional/presence-bearing generated fields.
4. It builds a `protoreflect.FileDescriptor` with five enums, thirty-seven messages, and one service definition.
5. Individual message methods lazily attach `protoimpl.MessageInfo` to message state in `Reset` and `ProtoReflect`.
6. Getters return zero values when the receiver or optional pointer is nil; setters assign fields directly; `Has*`/`Clear*` helpers manage message and optional-field presence.

The business-level protocol flow implied by the schema is:

1. A controller sends `UpdateConfig` with BeeRemote connection details and complete RST configuration.
2. It checks node liveness/readiness using `Heartbeat`, optionally requesting stats.
3. It assigns work with `SubmitWork`, using a `WorkRequest` that selects a concrete job type and optional segment/priority.
4. Workers report resulting `Work` objects with lifecycle state and per-part transfer state.
5. The controller can request cancellation with `UpdateWork` or node-wide drain/initialization behavior with `BulkUpdateWork`.
6. The controller can query `GetCapabilities` to learn build metadata and feature support.

## State And Persistence Behavior

This file itself does not persist data. All state is in-memory protobuf message fields and serialized wire representations. The schema, however, encodes persistent or externally meaningful state:

- Work identity is represented by `job_id`, `request_id`, path, external IDs, and RST IDs.
- Work lifecycle state is externally visible through `Work_Status` and `Work_State`.
- Parallel transfer progress is represented by `Work_Part.Completed`, ETags, checksums, and inclusive offset ranges.
- Configuration state is declarative in `UpdateConfigRequest`: all desired RSTs must be included, and omitted RSTs are treated as deletions by service implementations.
- Sensitive configuration can flow through `BeeRemoteNode.AuthSecret`, TLS cert bytes, and S3 access/secret keys.
- Optional scalar fields preserve presence separately from zero values via pointers; callers must use `Has*` when default values are semantically different from unset values.
- Unknown protobuf fields are retained through `protoimpl.UnknownFields`, supporting forward/backward compatibility.

## Dependencies

Direct imports are:

- `google.golang.org/protobuf/reflect/protoreflect` for enum, message, and file descriptor reflection.
- `google.golang.org/protobuf/runtime/protoimpl` for generated message runtime support.
- `google.golang.org/protobuf/types/known/timestamppb` for timestamp fields.
- `reflect` for deriving the Go package path during descriptor construction.

Generated compatibility constants enforce a sufficiently recent protobuf runtime. The raw descriptor declares the Go package path as `github.com/thinkparq/protobuf/go/flex`.

## Integration Points

The file is paired with `flex_grpc.pb.go`, whose client/server interfaces reference these request/response messages for the `WorkerNode` service. It is also an integration boundary for code that:

- Configures worker nodes from BeeRemote using `UpdateConfigRequest`, `BeeRemoteNode`, and `RemoteStorageTarget`.
- Submits and tracks distributed upload/download work using `WorkRequest`, `SyncJob`, `Work`, `Work_Status`, and `Work_Part`.
- Builds jobs from filesystem events or CLI/user input using `JobRequestCfg`, `BuilderJob`, and `JobLockedInfo`.
- Supports multiple RST backends. A source comment explicitly notes that new RST oneof variants must also be added to `rst.SupportedRSTTypes` and compatible config unmarshalling hooks.
- Exposes capability discovery through `GetCapabilitiesResponse.Features` and `BuildInfo`.

## Risks

- This is generated code; manual edits would be overwritten and can desynchronize from `flex.proto`.
- Optional scalar getters return zero values when unset, so logic that does not check `HasUpdate`, `HasPriority`, `HasStorageClass`, `HasAllowRestore`, `HasFilterExpr`, or similar helpers can confuse an explicit default with absence.
- `WorkRequest_builder.Build()` and `RemoteStorageTarget_builder.Build()` assign oneof fields sequentially; if multiple oneof builder fields are set, the last non-nil field wins.
- `UpdateConfigRequest` has replace-all semantics for RSTs, so partial configuration updates can accidentally delete omitted targets.
- Secret material is represented in normal protobuf fields (`AuthSecret`, `AccessKey`, `SecretKey`, TLS cert bytes). Logging/stringifying messages or storing serialized configs needs redaction controls outside this generated file.
- Several comments describe responsibility outside protobuf enforcement: RST/job compatibility, valid time-duration strings for archival polling, endpoint formats, and unsupported combinations such as some upload/download option asymmetries.
- `Work_State_UNSPECIFIED` and other `UNSPECIFIED` enum values are default zero values but are documented as programming errors; validation must happen in service/business code.
- `SetMgmtdTlsCert` and `SetAuthSecret` normalize nil byte slices to empty slices, so callers that care about nil versus empty must not rely on those setters preserving nil.

## Test Signals

Useful tests around this file should target generated-contract behavior rather than re-testing protobuf internals:

- Compile tests for code consuming generated types after regenerating from `flex.proto`.
- Serialization round trips for representative `WorkRequest` oneof variants and `RemoteStorageTarget` oneof variants.
- Presence tests for optional scalars to confirm unset, explicit false, explicit zero, and explicit empty string are handled correctly through `Has*` methods.
- Config update tests that assert omitted RSTs are intentionally deleted by the service implementation.
- Redaction tests in higher-level logging paths that include `BeeRemoteNode` and `RemoteStorageTarget_S3`.
- Work lifecycle tests for valid transitions and handling of `ERROR`, `FAILED`, `CANCELLED`, and `COMPLETED`.
- Compatibility tests between this generated file and `flex_grpc.pb.go`, especially method request/response types and package/service names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/go/flex/flex.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/go/flex/flex_grpc.pb.go -->
# sources/distributed-fs/beegfs-protobuf/go/flex/flex_grpc.pb.go

## Purpose

This generated Go file is the gRPC binding for the `flex.WorkerNode` service declared in `flex.proto`, produced by `protoc-gen-go-grpc v1.5.1`. It exposes typed client and server interfaces over the protobuf messages defined in `flex.pb.go`. The service models a worker node that accepts configuration, reports readiness, receives work, updates work state, supports bulk work-state operations, and advertises capabilities.

The file contains transport glue only: it does not implement worker behavior, persistence, validation, scheduling, or transfer logic. Those responsibilities belong to code that implements `WorkerNodeServer` or calls `WorkerNodeClient`.

## Important APIs, Types, And Functions

The package-level compatibility constant `grpc.SupportPackageIsVersion9` requires gRPC-Go v1.64.0 or later.

Full method-name constants define the canonical unary RPC paths:

- `WorkerNode_UpdateConfig_FullMethodName`: `/flex.WorkerNode/UpdateConfig`
- `WorkerNode_Heartbeat_FullMethodName`: `/flex.WorkerNode/Heartbeat`
- `WorkerNode_SubmitWork_FullMethodName`: `/flex.WorkerNode/SubmitWork`
- `WorkerNode_UpdateWork_FullMethodName`: `/flex.WorkerNode/UpdateWork`
- `WorkerNode_BulkUpdateWork_FullMethodName`: `/flex.WorkerNode/BulkUpdateWork`
- `WorkerNode_GetCapabilities_FullMethodName`: `/flex.WorkerNode/GetCapabilities`

`WorkerNodeClient` is the typed client interface:

- `UpdateConfig(context.Context, *UpdateConfigRequest, ...grpc.CallOption) (*UpdateConfigResponse, error)`
- `Heartbeat(context.Context, *HeartbeatRequest, ...grpc.CallOption) (*HeartbeatResponse, error)`
- `SubmitWork(context.Context, *SubmitWorkRequest, ...grpc.CallOption) (*SubmitWorkResponse, error)`
- `UpdateWork(context.Context, *UpdateWorkRequest, ...grpc.CallOption) (*UpdateWorkResponse, error)`
- `BulkUpdateWork(context.Context, *BulkUpdateWorkRequest, ...grpc.CallOption) (*BulkUpdateWorkResponse, error)`
- `GetCapabilities(context.Context, *GetCapabilitiesRequest, ...grpc.CallOption) (*GetCapabilitiesResponse, error)`

`NewWorkerNodeClient` wraps a `grpc.ClientConnInterface` in the unexported `workerNodeClient`. Each client method prepends `grpc.StaticMethod()` to call options, allocates the typed response, invokes the full method name through `cc.Invoke`, returns the response on success, and returns nil plus the transport error on failure.

`WorkerNodeServer` is the implementation interface. It mirrors the six unary methods and includes `mustEmbedUnimplementedWorkerNodeServer()` to enforce forward-compatible embedding.

`UnimplementedWorkerNodeServer` provides default methods that return `codes.Unimplemented` errors through `status.Errorf`. Generated comments recommend embedding it by value to avoid nil-pointer panics when future unimplemented methods are invoked.

`UnsafeWorkerNodeServer` allows an implementation to opt out of forward compatibility by satisfying only `mustEmbedUnimplementedWorkerNodeServer()`, but the generated comment warns that newly added methods will become compile-time breaks.

`RegisterWorkerNodeServer` validates by-value embedding when available, then registers `WorkerNode_ServiceDesc` with a `grpc.ServiceRegistrar`.

Private unary handler functions (`_WorkerNode_UpdateConfig_Handler`, `_WorkerNode_Heartbeat_Handler`, `_WorkerNode_SubmitWork_Handler`, `_WorkerNode_UpdateWork_Handler`, `_WorkerNode_BulkUpdateWork_Handler`, and `_WorkerNode_GetCapabilities_Handler`) decode incoming requests, call the server implementation directly when no interceptor is present, or wrap the call in `grpc.UnaryServerInfo` and an interceptor handler.

`WorkerNode_ServiceDesc` declares service name `flex.WorkerNode`, the server handler type, all six unary method descriptors, no streams, and metadata `flex.proto`.

## Control Flow

Client-side control flow for every method is identical:

1. Start with `grpc.StaticMethod()` and append user-supplied call options.
2. Allocate the expected response message.
3. Call `ClientConnInterface.Invoke(ctx, fullMethodName, request, response, options...)`.
4. Return the populated response or the encountered error.

Server-side handler flow for every unary RPC is:

1. Allocate the expected request message.
2. Decode the inbound message with the provided decoder.
3. If decode fails, return the decode error.
4. If no unary interceptor is configured, type-assert `srv` to `WorkerNodeServer` and call the matching method.
5. If an interceptor exists, create `grpc.UnaryServerInfo` with the full method name and a closure that type-asserts the request, then pass control to the interceptor.

Registration flow calls `testEmbeddedByValue()` if the server implementation exposes it through the embedded unimplemented server. This intentionally panics early if `UnimplementedWorkerNodeServer` was embedded as a nil pointer, preventing a later runtime panic during an unimplemented method call.

## State And Persistence Behavior

This file has no persistent state. It defines stateless client stubs, server registration metadata, and per-call request/response allocation. Request cancellation, deadlines, authentication metadata, retries, and transport behavior flow through `context.Context`, `grpc.CallOption`, interceptors, and gRPC configuration supplied by callers.

The RPCs move domain state represented by `flex.pb.go` messages:

- `UpdateConfig` carries desired worker configuration.
- `Heartbeat` observes readiness and optional node statistics.
- `SubmitWork` assigns a unit of work and receives the worker's accepted status.
- `UpdateWork` requests a specific work-state change, such as cancellation.
- `BulkUpdateWork` handles node-wide outstanding work behavior during connection or drain/removal flows.
- `GetCapabilities` discovers worker build and feature metadata.

## Dependencies

Direct imports are:

- `context` from the standard library.
- `google.golang.org/grpc` for client connections, service registration, method descriptors, interceptors, and call options.
- `google.golang.org/grpc/codes` and `google.golang.org/grpc/status` for default unimplemented server errors.

All request and response message types come from the same `flex` package and are generated in `flex.pb.go`.

## Integration Points

This file integrates generated protobuf messages with the gRPC runtime:

- Clients use `NewWorkerNodeClient` with any `grpc.ClientConnInterface`.
- Servers implement `WorkerNodeServer`, usually embed `UnimplementedWorkerNodeServer` by value, and call `RegisterWorkerNodeServer`.
- Interceptors can observe and control all RPCs through full method names and typed request objects.
- `WorkerNode_ServiceDesc` supports direct registration by gRPC and service reflection/introspection tools.
- The service method list matches dependency indexes embedded in `flex.pb.go`, which record one service with six unary methods.

## Risks

- Manual edits are generated-code drift and will be overwritten by `protoc-gen-go-grpc`.
- Server implementations must embed `UnimplementedWorkerNodeServer` by value for forward compatibility; embedding it as a nil pointer can cause an intentional registration-time panic.
- Client methods return nil response plus error on transport failure; callers must not dereference response values before checking errors.
- Handler functions use type assertions to `WorkerNodeServer` and concrete request types. Misregistration or incorrect manual use of handlers will panic.
- There are no streaming RPCs, so long-running work status updates must be modeled through unary calls and returned `Work` messages rather than a persistent stream.
- The generated stubs do not enforce semantic validation such as allowed work-state transitions, configuration completeness, credential secrecy, or RST/job compatibility.
- The `grpc.StaticMethod()` call option marks methods as static for gRPC internals; custom call-option logic should account for it being prepended before caller-supplied options.

## Test Signals

Useful validation should focus on integration behavior:

- Compile tests that generated `flex.pb.go` and `flex_grpc.pb.go` are in sync with `flex.proto`.
- A fake `WorkerNodeServer` registered on a bufconn or test gRPC server, with client calls for all six methods.
- Interceptor tests verifying full method names and typed request dispatch.
- Forward-compatibility tests or static checks ensuring server implementations embed `UnimplementedWorkerNodeServer` by value.
- Error-path tests for unimplemented default methods returning `codes.Unimplemented`.
- Caller tests that check errors before response dereference for all client methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/go/flex/flex_grpc.pb.go -->
