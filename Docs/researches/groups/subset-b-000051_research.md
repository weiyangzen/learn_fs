# Research Group subset-b-000051

This grouped report covers containerd task, transfer, ttrpc event, version, and shared API type definitions. Each file section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/tasks/v1/tasks.pb.go -->
# sources/cloud-native/containerd/api/services/tasks/v1/tasks.pb.go

## Purpose
Generated Go protobuf bindings for `services/tasks/v1/tasks.proto`. This file is the typed message layer for the containerd task management API: task creation, process execution, lifecycle transitions, checkpointing, resource updates, metrics, and wait/delete status reporting.

## Important APIs and Types
The exported request/response structs include `CreateTaskRequest`, `StartRequest`, `DeleteTaskRequest`, `DeleteProcessRequest`, `GetRequest`, `ListTasksRequest`, `KillRequest`, `ExecProcessRequest`, `ResizePtyRequest`, `CloseIORequest`, `PauseTaskRequest`, `ResumeTaskRequest`, `ListPidsRequest`, `CheckpointTaskRequest`, `UpdateTaskRequest`, `MetricsRequest`, and `WaitRequest`, plus matching responses where needed. Fields connect tasks to container IDs, exec IDs, rootfs mounts, IO paths, terminal sizing, checkpoint descriptors, runtime options in `Any`, process info, metrics, and timestamps.

## Control Flow
There is no business control flow; each generated type provides `Reset`, `String`, `ProtoMessage`, `ProtoReflect`, deprecated `Descriptor`, and nil-safe `Get*` accessors. File initialization builds a `protoreflect.FileDescriptor` with 28 message infos, dependency indexes, and message exporters when unsafe protobuf operations are disabled.

## State and Persistence
Messages carry serialized task API state but do not persist anything themselves. The most persistence-sensitive fields are `rootfs`, `checkpoint`, `options`, `resources`, `annotations`, `metrics`, `exited_at`, and `task_api_address`/`task_api_version`, because downstream containerd services use them to create shim processes, restore state, update runtime resources, or report terminal process status.

## Dependencies and Integration Points
Depends on `api/types` for `Mount`, `Descriptor`, and `Metric`, `api/types/task` for `Process` and `ProcessInfo`, and protobuf `Any`, `Empty`, and `Timestamp`. It is consumed by the generated gRPC and ttrpc stubs and by containerd task manager implementations.

## Risks
Generated fields are wire contracts; field number changes are compatibility breaking. `Any` fields need strict type-url handling by callers. Map fields such as annotations are not stable for byte-for-byte deterministic comparisons unless deterministic marshaling is selected. `TaskApiAddress` delegates operations to an existing endpoint and needs validation in service code, not here.

## Test Signals
Useful signals are compile tests after regenerating protos, round-trip protobuf marshal/unmarshal for all message fields, compatibility tests against old clients, and task integration tests for create/start/exec/kill/wait/checkpoint/metrics paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/tasks/v1/tasks.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/tasks/v1/tasks.proto -->
# sources/cloud-native/containerd/api/services/tasks/v1/tasks.proto

## Purpose
Defines the canonical protobuf contract for the containerd `Tasks` service. It describes how clients create and operate container tasks and exec processes through either gRPC or ttrpc generated bindings.

## Important APIs and Types
The `Tasks` service exposes unary RPCs: `Create`, `Start`, `Delete`, `DeleteProcess`, `Get`, `List`, `Kill`, `Exec`, `ResizePty`, `CloseIO`, `Pause`, `Resume`, `ListPids`, `Checkpoint`, `Update`, `Metrics`, and `Wait`. Key messages include `CreateTaskRequest` with rootfs mounts, stdio paths, checkpoint descriptor, runtime options, runtime path, and optional task API endpoint/version; `ExecProcessRequest` with process spec and exec ID; `DeleteResponse` and `WaitResponse` with exit status and `exited_at`; `CheckpointTaskResponse` with descriptors; and `MetricsResponse` with `types.Metric`.

## Control Flow
The proto expresses lifecycle ordering expected by callers: create a task, start it, optionally exec additional processes, manipulate IO/pty and pause/resume, query pids/metrics, wait for exit, then delete task/process state. The service itself is not implemented here.

## State and Persistence
Persistent or externally meaningful state is represented by container IDs, exec IDs, rootfs mounts, checkpoint descriptors, resource `Any` payloads, annotations, exit timestamps, and runtime endpoint configuration. The proto uses field numbers as the stable wire schema and leaves validation/persistence semantics to containerd services.

## Dependencies and Integration Points
Imports protobuf well-known types and containerd `types/descriptor.proto`, `types/metrics.proto`, `types/mount.proto`, and `types/task/task.proto`. Generated outputs integrate with gRPC and ttrpc transport files in the same package.

## Risks
Adding fields is generally safe, but reusing/removing field numbers or changing message meaning can break wire compatibility. `Any` payloads allow runtime-specific extensibility but create risk if type URLs or versions are not checked. `task_api_address` is powerful because it redirects task operations to another endpoint.

## Test Signals
Contract tests should assert generated bindings expose every RPC, validate wire compatibility for existing field numbers, and exercise task lifecycle integration through both transports.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/tasks/v1/tasks.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/tasks/v1/tasks_grpc.pb.go -->
# sources/cloud-native/containerd/api/services/tasks/v1/tasks_grpc.pb.go

## Purpose
Generated gRPC bindings for the `Tasks` service. It provides client and server interfaces, method handlers, registration helpers, and the `grpc.ServiceDesc` used by containerd's gRPC server.

## Important APIs and Types
`TasksClient` exposes all 17 task RPCs as unary calls. `NewTasksClient` wraps a `grpc.ClientConnInterface`. `TasksServer` defines the server-side method set and requires `mustEmbedUnimplementedTasksServer` for forward compatibility. `UnimplementedTasksServer` returns `codes.Unimplemented` for every method. `RegisterTasksServer` registers `Tasks_ServiceDesc`.

## Control Flow
Client methods allocate response structs and call `cc.Invoke` with fully qualified method names such as `/containerd.services.tasks.v1.Tasks/Create`. Server handler functions decode requests, optionally route through a unary interceptor, and dispatch to the concrete `TasksServer` implementation. There are no streaming RPCs.

## State and Persistence
The file stores no runtime state beyond the client connection reference. Task state is entirely passed in protobuf request/response messages and owned by the server implementation.

## Dependencies and Integration Points
Depends on `google.golang.org/grpc`, `codes`, `status`, `context`, and `emptypb`. Integrates with containerd daemon gRPC registration and middleware/interceptors for auth, namespaces, tracing, or metrics.

## Risks
Generated service names and method paths must match clients and proto descriptors exactly. Implementations that embed `UnsafeTasksServer` opt out of forward-compatible compilation. Interceptor behavior can alter error propagation or context handling, so service tests should include middleware paths.

## Test Signals
Compile-time generated-code checks, server registration tests, fake server/client round trips for each RPC, and tests that unimplemented methods return gRPC `Unimplemented` are useful signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/tasks/v1/tasks_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/tasks/v1/tasks_ttrpc.pb.go -->
# sources/cloud-native/containerd/api/services/tasks/v1/tasks_ttrpc.pb.go

## Purpose
Generated ttrpc bindings for the `Tasks` service. This transport is used heavily between containerd and shims because it is smaller than gRPC and fits local runtime control paths.

## Important APIs and Types
`TTRPCTasksService` mirrors the 17 task RPCs. `RegisterTTRPCTasksService` registers service name `containerd.services.tasks.v1.Tasks` and a method map. `NewTTRPCTasksClient` wraps a `*ttrpc.Client` and returns a service-compatible client. Each client method calls `client.Call` with the service name, method name, request, and response pointer.

## Control Flow
Server registration maps each method string to a closure that unmarshals into the corresponding request type and invokes the supplied service implementation. Client methods allocate response values and synchronously perform unary ttrpc calls. There is no interceptor layer in this generated file.

## State and Persistence
Only the client pointer is retained. Actual task lifecycle state is external, handled by the registered service implementation and shims.

## Dependencies and Integration Points
Depends on `github.com/containerd/ttrpc`, `context`, and `emptypb`. It integrates with shim task APIs and local containerd runtime bridges that prefer ttrpc for process lifecycle operations.

## Risks
Method names are plain strings and must remain aligned with the proto. Server closures trust the ttrpc unmarshal function to reject malformed requests. Because ttrpc has different middleware semantics than gRPC, parity tests are important for task behavior across transports.

## Test Signals
Signals include generated binding compilation, registration/call tests with an in-memory ttrpc server, and transport parity tests covering task create/start/delete/wait and error status mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/tasks/v1/tasks_ttrpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/transfer/v1/doc.go -->
# sources/cloud-native/containerd/api/services/transfer/v1/doc.go

## Purpose
Package declaration file for `api/services/transfer/v1`. It establishes the Go package `transfer` for generated transfer service bindings.

## Important APIs and Types
No functions or types are defined here. The public API is supplied by `transfer.pb.go`, `transfer_grpc.pb.go`, and `transfer_ttrpc.pb.go` in the same package.

## Control Flow
There is no executable control flow.

## State and Persistence
No state is stored. It only participates in package documentation/build structure.

## Dependencies and Integration Points
No imports. Integrates indirectly with generated service files by sharing their package namespace.

## Risks
Low runtime risk. The main risk is package naming consistency; changing `package transfer` would break generated file package cohesion.

## Test Signals
Go package compilation is sufficient for this file. Broader transfer service tests live against generated bindings and implementations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/transfer/v1/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/transfer/v1/transfer.pb.go -->
# sources/cloud-native/containerd/api/services/transfer/v1/transfer.pb.go

## Purpose
Generated Go protobuf message bindings for the containerd transfer service. It models a generic transfer request that moves content from an arbitrary source to an arbitrary destination with optional progress reporting.

## Important APIs and Types
`TransferRequest` contains `Source` and `Destination` as protobuf `Any`, plus `Options`. `TransferOptions` currently exposes `ProgressStream`, a string identifier for progress reporting. Both types include standard generated reflection, descriptor, reset, string, and nil-safe getter methods.

## Control Flow
No business logic is present. Initialization constructs the file descriptor for two messages and one service, records dependency indexes for `Any`, `Empty`, and `TransferOptions`, and clears raw descriptor/go type slices after build.

## State and Persistence
The file does not persist state. It serializes transfer intent and progress stream selection. Actual content movement, source/destination unpacking, and progress persistence are implemented by transfer services and typed payloads under `api/types/transfer`.

## Dependencies and Integration Points
Depends on `anypb`, `emptypb`, protobuf reflection/runtime, `reflect`, and `sync`. Used by gRPC/ttrpc transfer transport stubs and callers that marshal typed transfer source/destination messages into `Any`.

## Risks
`Any` payload extensibility means unsupported or malicious type URLs must be rejected by the service implementation. `ProgressStream` is only a string here, so lifecycle, authorization, and cleanup of progress streams must be handled elsewhere.

## Test Signals
Round-trip tests for `TransferRequest` with expected source/destination `Any` payloads, generated descriptor tests, and integration tests that verify progress stream IDs are honored by the transfer implementation are relevant.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/transfer/v1/transfer.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/transfer/v1/transfer.proto -->
# sources/cloud-native/containerd/api/services/transfer/v1/transfer.proto

## Purpose
Canonical protobuf contract for containerd's transfer service. It defines a single high-level `Transfer` RPC for moving artifacts between typed sources and destinations.

## Important APIs and Types
`service Transfer` has unary RPC `Transfer(TransferRequest) returns (google.protobuf.Empty)`. `TransferRequest` carries `source`, `destination`, and `options`. `TransferOptions` currently contains `progress_stream`; a comment hints at future progress interval configuration.

## Control Flow
The proto defines request shape only. Runtime flow is expected to unpack source and destination `Any` payloads, perform transfer work, optionally publish progress, and return empty success or an error status.

## State and Persistence
No persistence is implemented here. The wire contract carries references to transfer endpoints and a progress stream name; content store mutations and progress state belong to service implementations.

## Dependencies and Integration Points
Imports protobuf `Any` and `Empty`. The `Any` fields are designed to integrate with containerd transfer type protos such as image store, registry, import/export, streaming, and progress definitions.

## Risks
Because the source and destination are opaque at the service boundary, type compatibility and authorization checks are critical. Expanding `TransferOptions` should preserve field numbers and clarify progress semantics.

## Test Signals
Tests should verify generated gRPC/ttrpc bindings, `Any` type-url compatibility for known transfer endpoints, invalid source/destination rejection, and progress publication behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/transfer/v1/transfer.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/transfer/v1/transfer_grpc.pb.go -->
# sources/cloud-native/containerd/api/services/transfer/v1/transfer_grpc.pb.go

## Purpose
Generated gRPC transport binding for the transfer service.

## Important APIs and Types
`TransferClient` exposes `Transfer(ctx, *TransferRequest, ...grpc.CallOption)`. `NewTransferClient` wraps a `grpc.ClientConnInterface`. `TransferServer` declares the server method and forward-compatibility embed requirement. `UnimplementedTransferServer` returns `codes.Unimplemented`. `RegisterTransferServer` registers `Transfer_ServiceDesc`.

## Control Flow
The client invokes `/containerd.services.transfer.v1.Transfer/Transfer`. The server handler decodes a `TransferRequest`, routes through a unary interceptor if present, and dispatches to the registered server implementation. The service descriptor contains one unary method and no streams.

## State and Persistence
No persistent state is kept. The client stores only the connection interface; transfer state is owned by server-side implementation.

## Dependencies and Integration Points
Depends on gRPC packages, `context`, and `emptypb`. Integrates with containerd's public gRPC server and middleware stack.

## Risks
The single broad RPC makes service implementation validation especially important. Incorrect method path or service registration breaks all gRPC transfer clients. Forward compatibility requires embedding `UnimplementedTransferServer`.

## Test Signals
Fake gRPC server/client round trips, interceptor coverage, unimplemented method status assertions, and compile checks after proto regeneration are useful.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/transfer/v1/transfer_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/transfer/v1/transfer_ttrpc.pb.go -->
# sources/cloud-native/containerd/api/services/transfer/v1/transfer_ttrpc.pb.go

## Purpose
Generated ttrpc binding for the transfer service.

## Important APIs and Types
`TTRPCTransferService` declares `Transfer`. `RegisterTTRPCTransferService` registers service `containerd.services.transfer.v1.Transfer` with one method closure. `NewTTRPCTransferClient` returns a client that implements the same interface. The client method calls ttrpc service `Transfer`, method `Transfer`, with a `TransferRequest` and `emptypb.Empty` response.

## Control Flow
Server-side control is decode then dispatch. Client-side control is allocate empty response, call, return response or error. There are no streaming or persistence operations.

## State and Persistence
Only the ttrpc client pointer is retained. Transfer progress and content state are external.

## Dependencies and Integration Points
Depends on `github.com/containerd/ttrpc`, `context`, and `emptypb`. Useful for local transport where transfer service exposure via ttrpc is desired.

## Risks
String service/method names must remain in sync with the proto. ttrpc error and context behavior should be tested against gRPC expectations if both transports are supported.

## Test Signals
Register/call tests with an in-memory ttrpc server, malformed request unmarshal tests, and parity checks with gRPC transfer behavior are relevant.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/transfer/v1/transfer_ttrpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/ttrpc/events/v1/doc.go -->
# sources/cloud-native/containerd/api/services/ttrpc/events/v1/doc.go

## Purpose
Package documentation and compatibility aliases for the ttrpc events API.

## Important APIs and Types
Declares package `events` and imports `github.com/containerd/containerd/api/types`. It defines deprecated type alias `Envelope = types.Envelope`, preserving older package users while directing them to `types.Envelope`.

## Control Flow
No executable flow beyond compile-time aliasing.

## State and Persistence
No state is stored. Event state is represented by `types.Envelope` in generated protobuf messages.

## Dependencies and Integration Points
Integrates with older event-forwarding code that referenced `events.Envelope`, while the canonical type lives in `api/types/event.proto`.

## Risks
Removing the alias could break downstream consumers. Keeping it may hide migrations, but the deprecation notice makes the canonical path clear.

## Test Signals
Package compile tests and downstream compatibility checks that `events.Envelope` remains assignable to `types.Envelope` are enough.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/ttrpc/events/v1/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/ttrpc/events/v1/events.pb.go -->
# sources/cloud-native/containerd/api/services/ttrpc/events/v1/events.pb.go

## Purpose
Generated protobuf message binding for the ttrpc event forwarding service. It defines the request envelope used to forward already-packaged events.

## Important APIs and Types
`ForwardRequest` has one field, `Envelope *types.Envelope`, with generated reset, reflection, descriptor, and getter methods. The file descriptor records one message and one `Events` service with `Forward` returning `google.protobuf.Empty`.

## Control Flow
No business logic exists. Initialization ensures the dependent `types/event.proto` descriptor is available through imports and builds protobuf reflection metadata for the service and request.

## State and Persistence
No persistence is handled. The carried `Envelope` includes timestamp, namespace, topic, and event payload; event brokers or publishers decide how to store or distribute it.

## Dependencies and Integration Points
Depends on `api/types.Envelope`, protobuf runtime/reflection, and `emptypb`. It is consumed by `events_ttrpc.pb.go` and by shim event publishers that forward event envelopes back to containerd.

## Risks
A nil envelope can be represented on the wire and must be rejected or handled by service implementation. The request trusts the caller-supplied timestamp and namespace, which is intentional for forwarding but security-sensitive.

## Test Signals
Round-trip marshaling of `ForwardRequest`, descriptor validation, nil-envelope service behavior, and end-to-end shim event forwarding tests provide coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/ttrpc/events/v1/events.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/ttrpc/events/v1/events.proto -->
# sources/cloud-native/containerd/api/services/ttrpc/events/v1/events.proto

## Purpose
Canonical proto contract for the ttrpc event forwarding service. It lets a component forward an event that is already wrapped in a timestamped, namespaced envelope.

## Important APIs and Types
`service Events` exposes unary RPC `Forward(ForwardRequest) returns (google.protobuf.Empty)`. `ForwardRequest` contains `containerd.types.Envelope envelope`.

## Control Flow
The expected runtime flow is caller constructs or receives an `Envelope`, sends it through `Forward`, and the service publishes or relays it. The proto intentionally preserves upstream timestamp, namespace, topic, and event payload.

## State and Persistence
No persistence is implemented here. Event delivery, buffering, replay, or persistence are outside this schema.

## Dependencies and Integration Points
Imports `google/protobuf/empty.proto` and `types/event.proto`. Integrates with shim event publishers and containerd event services over ttrpc.

## Risks
Forwarding on behalf of another component can spoof namespace/topic/time if service authorization is weak. Schema changes to `Envelope` affect all event transport users.

## Test Signals
Transport tests should cover forwarded timestamp/namespace preservation, nil or malformed envelope rejection, and event bus delivery after ttrpc forwarding.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/ttrpc/events/v1/events.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/ttrpc/events/v1/events_ttrpc.pb.go -->
# sources/cloud-native/containerd/api/services/ttrpc/events/v1/events_ttrpc.pb.go

## Purpose
Generated ttrpc transport binding for the event forwarding service.

## Important APIs and Types
`TTRPCEventsService` declares `Forward`. `RegisterTTRPCEventsService` registers `containerd.services.events.ttrpc.v1.Events` with a single method closure. `NewTTRPCEventsClient` wraps `*ttrpc.Client`; its `Forward` method calls service `Events`, method `Forward`, and returns `emptypb.Empty`.

## Control Flow
Server flow is unmarshal into `ForwardRequest` and dispatch to the provided service. Client flow is allocate empty response, perform unary ttrpc call, return response or error.

## State and Persistence
No persistent state is kept except the client pointer. Event publication state is controlled by the service implementation.

## Dependencies and Integration Points
Depends on `context`, `github.com/containerd/ttrpc`, and `emptypb`. It integrates with shim-side remote event publishing.

## Risks
Service and method strings must stay stable for shim compatibility. Errors returned by event forwarding may affect shim behavior, so callers need clear retry/drop policy outside this generated file.

## Test Signals
In-memory ttrpc forwarding tests, service name compatibility checks, and integration tests with shim event publisher code are useful.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/ttrpc/events/v1/events_ttrpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/version/v1/doc.go -->
# sources/cloud-native/containerd/api/services/version/v1/doc.go

## Purpose
Package documentation for the version service bindings. It declares package `version`.

## Important APIs and Types
No APIs are defined in this file. `version.pb.go`, `version_grpc.pb.go`, and `version_ttrpc.pb.go` provide the generated message and transport APIs.

## Control Flow
No executable flow.

## State and Persistence
No state.

## Dependencies and Integration Points
No imports. Shares the package namespace for generated version service files.

## Risks
Only package-name consistency risk. Runtime risks are in the generated service bindings and implementation.

## Test Signals
Go package compilation is sufficient for this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/version/v1/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/version/v1/version.pb.go -->
# sources/cloud-native/containerd/api/services/version/v1/version.pb.go

## Purpose
Generated protobuf message binding for containerd's version service.

## Important APIs and Types
`VersionResponse` contains `Version` and `Revision` strings and standard generated methods. The descriptor includes one message and a `Version` service taking `google.protobuf.Empty`.

## Control Flow
No business logic. Initialization builds the protobuf file descriptor and dependency index linking the service input to `emptypb.Empty` and output to `VersionResponse`.

## State and Persistence
No persistence. The message reports build/runtime identity supplied by the service implementation.

## Dependencies and Integration Points
Depends on protobuf reflection/runtime and `emptypb`. Used by gRPC and ttrpc generated version clients and servers.

## Risks
Version and revision are unstructured strings; callers should not assume semantic version parsing unless implementation guarantees it. The proto comment questions whether the version service itself should be versioned, so compatibility expectations should be explicit in consumers.

## Test Signals
Marshal/unmarshal tests, descriptor validation, and service integration tests that check expected version/revision values from a running daemon are relevant.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/version/v1/version.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/version/v1/version.proto -->
# sources/cloud-native/containerd/api/services/version/v1/version.proto

## Purpose
Canonical proto contract for the containerd version service.

## Important APIs and Types
`service Version` exposes `Version(google.protobuf.Empty) returns (VersionResponse)`. `VersionResponse` has `version` and `revision` strings.

## Control Flow
Runtime flow is a simple unary query: client sends empty request, server returns its version metadata.

## State and Persistence
The proto carries no persistent state. Values are expected to be derived from daemon build metadata or runtime configuration.

## Dependencies and Integration Points
Imports `google/protobuf/empty.proto`. Generated bindings expose the service over gRPC and ttrpc.

## Risks
The TODO asks whether the version service should be versioned; if future service versions diverge, clients may need compatibility negotiation outside this minimal response.

## Test Signals
Tests should verify daemon version endpoint availability, non-empty expected revision/version in release builds, and generated client compatibility across transports.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/version/v1/version.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/version/v1/version_grpc.pb.go -->
# sources/cloud-native/containerd/api/services/version/v1/version_grpc.pb.go

## Purpose
Generated gRPC transport binding for the version service.

## Important APIs and Types
`VersionClient` exposes `Version(ctx, *emptypb.Empty, ...grpc.CallOption)`. `NewVersionClient` wraps a `grpc.ClientConnInterface`. `VersionServer` defines the server method and embed requirement. `UnimplementedVersionServer` returns gRPC `Unimplemented`. `RegisterVersionServer` registers `Version_ServiceDesc`.

## Control Flow
The client invokes `/containerd.services.version.v1.Version/Version`. The handler decodes `emptypb.Empty`, optionally uses a unary interceptor, and calls the server implementation.

## State and Persistence
No state beyond the client connection. Version information is supplied externally.

## Dependencies and Integration Points
Depends on gRPC, `context`, status/codes, and `emptypb`. Integrates with the containerd daemon's gRPC service registration.

## Risks
Very small generated surface, but service path stability matters because version calls are often used by clients as a connectivity/capability probe.

## Test Signals
Fake server/client tests, unimplemented status tests, interceptor path coverage, and live daemon version query tests are useful.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/version/v1/version_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/version/v1/version_ttrpc.pb.go -->
# sources/cloud-native/containerd/api/services/version/v1/version_ttrpc.pb.go

## Purpose
Generated ttrpc transport binding for the version service.

## Important APIs and Types
`TTRPCVersionService` declares `Version(context.Context, *emptypb.Empty)`. `RegisterTTRPCVersionService` registers service `containerd.services.version.v1.Version`. `NewTTRPCVersionClient` creates a client wrapper; `Version` calls ttrpc service/method `Version`.

## Control Flow
Server closure unmarshals an empty request and dispatches. Client allocates `VersionResponse`, calls ttrpc, and returns response or error.

## State and Persistence
Only the ttrpc client pointer is held. Version metadata is external.

## Dependencies and Integration Points
Depends on `context`, `github.com/containerd/ttrpc`, and `emptypb`. It can be used by local components that query version over ttrpc.

## Risks
String method registration must match generated clients. If version checks are used as health probes, transport error mapping should be tested.

## Test Signals
In-memory ttrpc client/server test and parity checks with the gRPC version endpoint.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/version/v1/version_ttrpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/descriptor.pb.go -->
# sources/cloud-native/containerd/api/types/descriptor.pb.go

## Purpose
Generated Go binding for the containerd `Descriptor` type, a simplified OCI-style content descriptor used to reference blobs in a content store.

## Important APIs and Types
`Descriptor` fields are `MediaType`, `Digest`, `Size`, and `Annotations map[string]string`. Generated methods provide protobuf reflection and nil-safe getters.

## Control Flow
No business logic. Initialization builds a descriptor with two message infos: `Descriptor` and its generated map entry.

## State and Persistence
The struct serializes content identity and metadata. It does not persist blobs itself; persistence is in content stores that interpret digest/size/media type.

## Dependencies and Integration Points
Depends on protobuf runtime/reflection. Used by task checkpoint responses, image/content APIs, and code that bridges containerd and OCI descriptor concepts.

## Risks
Digest and size are plain fields here; validation must happen elsewhere. Annotation map iteration order is nondeterministic unless deterministic marshaling is requested. Field number 4 is unused, so future schema work should avoid accidental incompatible reuse unless intentionally reserved by project policy.

## Test Signals
Round-trip descriptor serialization, OCI conversion tests, content-store validation tests for digest/size mismatch, and deterministic marshaling tests for annotations when needed.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/descriptor.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/descriptor.proto -->
# sources/cloud-native/containerd/api/types/descriptor.proto

## Purpose
Canonical proto definition of `containerd.types.Descriptor`, used to identify content-store blobs and OCI descriptor-like references.

## Important APIs and Types
`Descriptor` includes `media_type`, `digest`, `size`, and annotation map field number 5.

## Control Flow
No control flow. This is a schema-only file.

## State and Persistence
The message carries persistent content identity metadata. Actual blob storage, verification, and garbage collection live in content store implementations.

## Dependencies and Integration Points
No proto imports. The Go package is `github.com/containerd/containerd/api/types;types`. It integrates with OCI image spec descriptor concepts and containerd checkpoint/content APIs.

## Risks
Changing field numbers or semantics would break wire compatibility and stored metadata. Digest strings require validation outside the schema.

## Test Signals
Schema compatibility checks, generated-code checks, and conversion tests to/from OCI descriptors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/descriptor.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/doc.go -->
# sources/cloud-native/containerd/api/types/doc.go

## Purpose
Package declaration for shared containerd API types.

## Important APIs and Types
No types are declared directly. The package is populated by generated protobuf files and helper files such as `platform_helpers.go`.

## Control Flow
No executable flow.

## State and Persistence
No state.

## Dependencies and Integration Points
No imports. It establishes the `types` package namespace used by many service protos.

## Risks
Package naming consistency is the only direct risk.

## Test Signals
Package compilation is sufficient.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/event.pb.go -->
# sources/cloud-native/containerd/api/types/event.pb.go

## Purpose
Generated Go binding for the event `Envelope` type, the common wrapper for containerd events.

## Important APIs and Types
`Envelope` carries `Timestamp`, `Namespace`, `Topic`, and `Event *anypb.Any`. It includes generated protobuf methods and getters. Its descriptor depends on `fieldpath.proto`, because the proto marks the message with the `containerd.types.fieldpath` option.

## Control Flow
No business control flow. Initialization calls `file_types_fieldpath_proto_init()` before building the event descriptor so the custom message option is registered.

## State and Persistence
The envelope serializes event delivery metadata. It does not store or route events itself. Downstream event services may persist, filter, or publish envelopes by namespace and topic.

## Dependencies and Integration Points
Depends on protobuf `Timestamp` and `Any`, plus the generated fieldpath extension descriptor. Used by ttrpc event forwarding and containerd event bus code.

## Risks
`Any` event payloads need type-url validation and version-aware decoding by consumers. Caller-supplied timestamps and namespaces can be security-sensitive when forwarding events. Nil timestamp or event fields are representable.

## Test Signals
Event marshal/unmarshal tests, type-url decoding tests for known event payloads, fieldpath option presence checks, and event forwarding integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/event.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/event.proto -->
# sources/cloud-native/containerd/api/types/event.proto

## Purpose
Canonical proto definition of `Envelope`, the common event wrapper for containerd APIs.

## Important APIs and Types
`Envelope` has custom option `(containerd.types.fieldpath) = true`, plus `timestamp`, `namespace`, `topic`, and opaque `event` payload fields.

## Control Flow
Schema only. Event creation, forwarding, filtering, and subscription are implemented elsewhere.

## State and Persistence
Carries event state for transmission or storage. It preserves event time, namespace scope, topic routing key, and typed payload.

## Dependencies and Integration Points
Imports protobuf `Any`, `Timestamp`, and containerd `types/fieldpath.proto`. Used by event services and publisher/subscriber integrations.

## Risks
Opaque payloads and forwarded namespace/timestamp data require authorization and decoding care. The custom option must stay registered for code that relies on fieldpath metadata.

## Test Signals
Generated descriptor tests should confirm the fieldpath option, and integration tests should verify topic/namespace preservation through event forwarding.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/event.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/fieldpath.pb.go -->
# sources/cloud-native/containerd/api/types/fieldpath.pb.go

## Purpose
Generated Go binding for custom protobuf options originally from GoGo fieldpath support and used by containerd descriptors.

## Important APIs and Types
Defines extension infos `E_FieldpathAll` for `descriptorpb.FileOptions` at field number 63300 and `E_Fieldpath` for `descriptorpb.MessageOptions` at field number 64400. There are no messages.

## Control Flow
Initialization builds a protobuf file descriptor with two extensions and no messages/services.

## State and Persistence
No runtime state or persistence. The extension values live in protobuf descriptors and can be queried by tooling or generated code.

## Dependencies and Integration Points
Depends on `descriptorpb`, protobuf runtime/reflection, and `reflect`. `event.proto` uses `fieldpath` on `Envelope`.

## Risks
Extension field numbers must remain stable and not conflict with other custom options. Consumers must use the modern protobuf extension APIs correctly.

## Test Signals
Descriptor tests should verify both extensions are registered, have expected field numbers, and can be read from protos using these options.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/fieldpath.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/fieldpath.proto -->
# sources/cloud-native/containerd/api/types/fieldpath.proto

## Purpose
Proto declaration for containerd custom fieldpath options. It is inherited from GoGo protobuf conventions and retained so schemas can mark files or messages for field-path behavior.

## Important APIs and Types
Extends `google.protobuf.FileOptions` with optional bool `fieldpath_all = 63300` and `google.protobuf.MessageOptions` with optional bool `fieldpath = 64400`.

## Control Flow
Schema-only file.

## State and Persistence
No application state. Option values are embedded in generated protobuf descriptors.

## Dependencies and Integration Points
Imports `google/protobuf/descriptor.proto`. Integrated by `event.proto` and any tooling that reads fieldpath metadata.

## Risks
Custom option compatibility depends on stable field numbers and package-qualified names. Removing it breaks descriptor parsing for protos that reference the option.

## Test Signals
Regeneration tests and descriptor reflection tests for option lookup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/fieldpath.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/introspection.pb.go -->
# sources/cloud-native/containerd/api/types/introspection.pb.go

## Purpose
Generated Go bindings for runtime introspection messages used to query runtime/shim identity, configuration, features, and annotations.

## Important APIs and Types
`RuntimeRequest` has `RuntimePath` and runtime-specific `Options *anypb.Any`. `RuntimeVersion` has `Version` and `Revision`. `RuntimeInfo` has `Name`, `Version`, `Options`, `Features`, and `Annotations map[string]string`.

## Control Flow
No business logic. Initialization builds descriptors for three messages and the generated annotation map entry. Accessors are nil-safe.

## State and Persistence
The messages carry runtime discovery state but do not persist it. `Options` corresponds to task create options; `Features` is expected to carry OCI-compatible runtime feature data; annotations describe shim metadata.

## Dependencies and Integration Points
Depends on protobuf `Any` and runtime/reflection. Used by containerd runtime managers and CRI paths that query shim/runtime capabilities.

## Risks
`Any` fields require known type URLs and version-compatible decoding. Feature payloads need clear schema expectations, especially for OCI runtime feature documents. Annotation maps have nondeterministic marshal order without deterministic settings.

## Test Signals
Runtime info query tests, `Any` decoding tests for runc/runtime options and features, map serialization tests where deterministic output matters, and backward-compatibility tests for older shims.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/introspection.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/introspection.proto -->
# sources/cloud-native/containerd/api/types/introspection.proto

## Purpose
Canonical proto definitions for runtime introspection request and response payloads.

## Important APIs and Types
`RuntimeRequest` selects a runtime path and passes runtime options. `RuntimeVersion` reports version/revision. `RuntimeInfo` reports runtime name, version, options, OCI-compatible features, and shim annotations.

## Control Flow
Schema only. Runtime managers interpret requests and return info.

## State and Persistence
Carries runtime configuration and capability metadata at query time. It does not define storage.

## Dependencies and Integration Points
Imports protobuf `Any`. Comments tie `options` to `CreateTaskRequest.options` and point OCI-compatible runtimes to the OCI runtime-spec features document shape.

## Risks
The flexible `Any` fields can drift between runtimes if type contracts are not documented. Feature and annotation semantics need consumer-side validation.

## Test Signals
Runtime introspection integration tests, type-url compatibility tests, and feature decoding tests for OCI-compatible runtimes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/introspection.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/metrics.pb.go -->
# sources/cloud-native/containerd/api/types/metrics.pb.go

## Purpose
Generated Go binding for a generic containerd metric envelope.

## Important APIs and Types
`Metric` includes `Timestamp`, `ID`, and opaque `Data *anypb.Any`. Generated methods provide reflection, descriptor access, and nil-safe getters.

## Control Flow
No business logic. Initialization builds a descriptor for one message with dependencies on `Timestamp` and `Any`.

## State and Persistence
The message carries sampled metric data but does not store it. `ID` typically identifies the task/container or metric subject; `Data` carries platform-specific metric payloads.

## Dependencies and Integration Points
Depends on protobuf well-known types. Used by the tasks `Metrics` RPC and CRI/container stats code that decodes cgroup v1/v2 or Windows metrics.

## Risks
Opaque metric payloads need type-url checks. Timestamps may be nil or caller supplied. Consumers should not assume a single metric payload type across platforms.

## Test Signals
Tests should cover metrics RPC responses, type-url decoding for cgroup v1/v2 and Windows stats, nil data handling, and timestamp propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/metrics.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/metrics.proto -->
# sources/cloud-native/containerd/api/types/metrics.proto

## Purpose
Canonical proto definition for generic metric samples.

## Important APIs and Types
`Metric` contains `timestamp`, string `id`, and `data` as protobuf `Any`.

## Control Flow
Schema only.

## State and Persistence
Represents a point-in-time metric sample or stats payload. Storage, aggregation, and display are external.

## Dependencies and Integration Points
Imports protobuf `Any` and `Timestamp`. Integrated with task metrics APIs and platform-specific stats payloads.

## Risks
The schema does not validate metric type, unit, or subject. Consumers need platform-aware decoding and fallback behavior for unknown payloads.

## Test Signals
Metrics service integration tests, unknown `Any` handling, and platform-specific decoding coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/metrics.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/mount.pb.go -->
# sources/cloud-native/containerd/api/types/mount.pb.go

## Purpose
Generated Go bindings for containerd mount-related shared types.

## Important APIs and Types
`Mount` contains `Type`, `Source`, `Target`, and `Options`. `ActiveMount` wraps a `Mount` with `MountedAt`, `MountPoint`, and `Data map[string]string`. `ActivationInfo` groups a name, active mounts, system mounts, and labels. Generated map entry messages support `Data` and `Labels`.

## Control Flow
No business logic. Initialization builds descriptors for three messages plus two generated map entries.

## State and Persistence
These messages serialize mount configuration and activation state. They do not perform mounts or persist mount tables. `ActiveMount` records activation metadata that may be stored or communicated by snapshotter/runtime services.

## Dependencies and Integration Points
Depends on protobuf `Timestamp`. `Mount` is imported by task creation and runtime shim APIs; activation messages integrate with mount/snapshotter control paths.

## Risks
Mount fields are unvalidated strings here; invalid or dangerous source/target/options must be checked by services. Map ordering is nondeterministic. Cross-platform mount option semantics differ.

## Test Signals
Task create tests with rootfs mounts, snapshotter activation tests, serialization round trips, invalid mount validation in service layers, and platform-specific mount option tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/mount.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/mount.proto -->
# sources/cloud-native/containerd/api/types/mount.proto

## Purpose
Canonical proto definitions for containerd mount data, described as a common language used by services when creating containers.

## Important APIs and Types
`Mount` follows mount syscall shape: `type`, `source`, `target`, and repeated `options`. `ActiveMount` adds activation time, mount point, and data. `ActivationInfo` groups active and system mounts with labels.

## Control Flow
Schema only. Mount execution and cleanup are implemented in snapshotter/runtime layers.

## State and Persistence
Carries mount configuration and activation metadata. Persistent meaning depends on callers storing activation info or using it to reconstruct active mounts.

## Dependencies and Integration Points
Imports protobuf `Timestamp`. Used by task create rootfs, runtime shim APIs, snapshotters, and activation-related services.

## Risks
Mount options are platform- and filesystem-specific and can be security-sensitive. The schema cannot prevent host path exposure, invalid targets, or unsupported options.

## Test Signals
Mount validation tests in service code, cross-platform task creation tests, and activation info serialization tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/mount.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/platform.pb.go -->
# sources/cloud-native/containerd/api/types/platform.pb.go

## Purpose
Generated Go binding for containerd's protobuf representation of an OCI platform.

## Important APIs and Types
`Platform` contains `OS`, `Architecture`, `Variant`, `OSVersion`, and repeated `OSFeatures`, with generated protobuf methods and getters.

## Control Flow
No business logic. Initialization builds a single-message descriptor.

## State and Persistence
The message carries platform selection metadata, often persisted in image metadata or transfer/import/export options.

## Dependencies and Integration Points
Depends only on protobuf runtime/reflection. `platform_helpers.go` converts to/from `opencontainers/image-spec/specs-go/v1.Platform`.

## Risks
The generated field name for `os_version` is `OSVersion` while the getter is `GetOsVersion`, which is normal generator behavior but easy to mistype. Platform normalization is not performed here; callers should use platform matching helpers elsewhere.

## Test Signals
Round-trip protobuf tests, OCI conversion tests, and image/platform matching tests for variant and OS feature preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/platform.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/platform.proto -->
# sources/cloud-native/containerd/api/types/platform.proto

## Purpose
Canonical proto definition of containerd's platform message, aligned with the OCI platform specification.

## Important APIs and Types
`Platform` fields are `os`, `architecture`, `variant`, `os_version`, and repeated `os_features`.

## Control Flow
Schema only.

## State and Persistence
Represents platform metadata used for image selection, transfer, import/export, and compatibility decisions.

## Dependencies and Integration Points
No proto imports. Integrated with OCI platform structs through helper functions.

## Risks
The schema does not normalize architecture aliases, OS casing, or variant semantics. Compatibility decisions must use higher-level platform matchers.

## Test Signals
OCI conversion tests and multi-platform image selection tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/platform.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/platform_helpers.go -->
# sources/cloud-native/containerd/api/types/platform_helpers.go

## Purpose
Provides hand-written conversion helpers between containerd protobuf `Platform` values and OCI image-spec `Platform` values.

## Important APIs and Types
`OCIPlatformToProto([]oci.Platform) []*Platform` allocates a protobuf slice and copies OS, OSVersion, Architecture, Variant, and OSFeatures. `OCIPlatformFromProto([]*Platform) []oci.Platform` performs the reverse copy.

## Control Flow
Both functions allocate output slices with the same length as input and iterate by index. They perform direct field copies only; no normalization or nil filtering is done.

## State and Persistence
No persistent state. The helpers transform in-memory platform metadata.

## Dependencies and Integration Points
Imports `github.com/opencontainers/image-spec/specs-go/v1` as `oci`. Integrates generated API types with OCI image-spec consumers and transfer/import/export code.

## Risks
`OCIPlatformFromProto` will panic if the input slice contains nil `*Platform` entries, because it dereferences fields directly. Neither function deep-copies the `OSFeatures` slice, so callers should avoid mutating source slices after conversion if aliasing matters.

## Test Signals
Unit tests should cover round-trip conversion, empty slices, OS features preservation, and nil input slice behavior. A nil-element test would document the current panic or motivate defensive handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/platform_helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runc/options/doc.go -->
# sources/cloud-native/containerd/api/types/runc/options/doc.go

## Purpose
Package declaration for runc runtime option API types.

## Important APIs and Types
No APIs are defined here. Generated runc option messages live in the same package, especially `oci.pb.go` from `oci.proto`.

## Control Flow
No executable flow.

## State and Persistence
No state.

## Dependencies and Integration Points
No imports. Establishes package `options` for runc option protobuf bindings used in task runtime options.

## Risks
Only package naming/build cohesion risk. Runtime option compatibility is in the generated option schema.

## Test Signals
Package compilation and tests around generated runc option messages are sufficient.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runc/options/doc.go -->
