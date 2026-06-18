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
