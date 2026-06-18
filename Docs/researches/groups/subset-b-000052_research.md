# Research: subset-b-000052

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runc/options/oci.pb.go -->
# sources/cloud-native/containerd/api/types/runc/options/oci.pb.go

Purpose: generated Go protobuf bindings for `types/runc/options/oci.proto`, used as the typed `Any` payload for runc shim runtime options, checkpoint options, and process details. It is data-contract code rather than hand-written behavior.

Important APIs/types/functions: exports `Options`, `CheckpointOptions`, and `ProcessDetails`, each with standard `Reset`, `String`, `ProtoMessage`, `ProtoReflect`, deprecated `Descriptor`, and nil-safe getters. `Options` carries runc task configuration such as `NoPivotRoot`, `NoNewKeyring`, shim cgroup, I/O pipe uid/gid, runc binary/root, systemd cgroup, CRIU image/work paths, and deprecated task API address/version fields. `CheckpointOptions` carries CRIU checkpoint flags including exit, TCP, external unix sockets, terminal, file locks, empty namespaces, cgroups mode, image path, and work path. `ProcessDetails` carries an `ExecID` for shim-managed exec processes.

Control flow: generated initialization builds `File_types_runc_options_oci_proto`, raw descriptors, exporter functions for unsafe-disabled builds, message infos, and Go type mappings. Runtime methods are protobuf reflection accessors and do not perform validation or side effects.

State/persistence: instances serialize to protobuf bytes and are persisted wherever containerd stores runtime `Any` options, task checkpoint request options, or checkpoint image metadata. Field number 8 remains reserved by the source proto, so old `criu_path` data must not be reused.

Dependencies/integration: depends on `protoreflect`, `protoimpl`, and `reflect/sync`. Hand-written client checkpoint code marshals `options.CheckpointOptions` into task checkpoint requests and checkpoint image records. Runtime option payloads integrate with runc shim implementations through typeurl/protobuf `Any`.

Risks: generated file must stay in lockstep with `oci.proto`; editing it directly will be overwritten. Deprecated `TaskApiAddress` and `TaskApiVersion` still deserialize for compatibility but should not guide new behavior. Proto3 zero values make unset and explicit false/zero indistinguishable, so callers must rely on higher-level defaults.

Test signals: regeneration via the repository proto target should be clean. API compatibility tests should cover marshal/unmarshal of all fields, reserved tag 8 non-reuse, checkpoint option round trips, and compatibility with client checkpoint code.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runc/options/oci.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runc/options/oci.proto -->
# sources/cloud-native/containerd/api/types/runc/options/oci.proto

Purpose: defines the protobuf wire schema for runc runtime, checkpoint, and process-detail options under package `containerd.runc.v1`.

Important APIs/types/functions: `Options` describes shim/runc creation behavior: pivot-root/keyring toggles, shim cgroup, I/O ownership, binary/root path, systemd cgroups, CRIU image/work paths, and deprecated task API fields. `CheckpointOptions` describes CRIU checkpoint behavior: exit-after-checkpoint, open TCP, external Unix sockets, pty, file locks, empty namespaces, cgroups mode, image path, and work path. `ProcessDetails` identifies a shim-managed exec process by `exec_id`.

Control flow: no executable flow; protoc turns this schema into Go bindings and descriptors. Field numbering is the control surface because serialized checkpoint/runtime data depends on stable tags.

State/persistence: these messages are persisted in runtime option `Any` payloads and checkpoint content. `reserved 8` protects the removed `criu_path` field from incompatible reuse.

Dependencies/integration: `go_package` maps to `github.com/containerd/containerd/api/types/runc/options;options`. The client checkpoint implementation uses `CheckpointOptions`; runtime shims consume `Options` through typeurl/protobuf.

Risks: changing field numbers or semantics breaks persisted checkpoints and external clients. Deprecated task API fields remain part of the schema for old payloads. Path-like fields have no schema validation and must be checked by consumers.

Test signals: generated `oci.pb.go` should match this file. Compatibility tests should check older payloads, reserved-field preservation, and checkpoint option behavior against runc shim/task service integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runc/options/oci.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runtimeoptions/v1/api.pb.go -->
# sources/cloud-native/containerd/api/types/runtimeoptions/v1/api.pb.go

Purpose: generated protobuf binding for generic runtime configuration indirection. It lets containerd pass either a config file path or in-memory config body plus a type URL to runtime implementations.

Important APIs/types/functions: `Options` has `TypeUrl`, `ConfigPath`, and `ConfigBody` fields with standard generated reflection and getters. `File_types_runtimeoptions_v1_api_proto` exposes the file descriptor for dynamic protobuf users.

Control flow: only generated reflection, getter, reset, raw descriptor gzip, and init/build code. There is no validation deciding precedence between `ConfigPath` and `ConfigBody`; that is documented in the proto and handled by consumers.

State/persistence: serialized `Options` may be stored in runtime config or sent through gRPC/typeurl `Any`. `ConfigBody` can carry TOML bytes in memory, while `ConfigPath` points to filesystem state external to the protobuf.

Dependencies/integration: uses `protoreflect` and `protoimpl`; generated from `api.proto` in package `runtimeoptions.v1`. Integrated by runtime plugin configuration code that accepts a generic runtime-options message.

Risks: direct edits will be overwritten by `make protos`. Large `ConfigBody` payloads increase gRPC/config memory pressure. Consumers must treat `TypeUrl` as a type-dispatch hint and validate body/path contents themselves.

Test signals: proto regeneration should be deterministic. Round-trip tests should cover path-only, body-only, empty body, and type URL preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runtimeoptions/v1/api.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runtimeoptions/v1/api.proto -->
# sources/cloud-native/containerd/api/types/runtimeoptions/v1/api.proto

Purpose: source schema for runtime option indirection, especially runtime-specific config supplied by path or embedded TOML bytes.

Important APIs/types/functions: `Options` includes `type_url` to identify the config type, `config_path` for a filesystem config file, and `config_body` for an in-memory TOML blob used when `config_path` is absent.

Control flow: no executable flow; schema comments define precedence semantics: `config_body` is used if `config_path` is not specified.

State/persistence: `config_path` references mutable external filesystem state; `config_body` embeds a snapshot of config bytes in the serialized message.

Dependencies/integration: `go_package` is `github.com/containerd/containerd/api/types/runtimeoptions/v1;runtimeoptions`. Runtime plugin loaders and shims can consume this message via protobuf `Any`.

Risks: unclear or invalid `type_url` can lead to runtime-specific decode failures. Path-based configs depend on file availability and permissions at runtime. Body payloads are unvalidated by schema.

Test signals: validate generated Go bindings, precedence between path and body in consuming code, and error behavior for unknown type URLs or unreadable paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runtimeoptions/v1/api.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runtimeoptions/v1/doc.go -->
# sources/cloud-native/containerd/api/types/runtimeoptions/v1/doc.go

Purpose: package documentation stub for the generated `runtimeoptions` Go package.

Important APIs/types/functions: declares package `runtimeoptions`; it has no functions or exported types beyond those generated in `api.pb.go`.

Control flow: none.

State/persistence: none directly; it anchors package documentation for the runtime options schema package.

Dependencies/integration: integrates with Go documentation and package compilation. License header matches containerd source conventions.

Risks: low. Package comment is minimal, so discoverability relies on proto comments.

Test signals: package should compile with generated files; documentation checks may expect the package declaration to remain.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runtimeoptions/v1/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/sandbox.pb.go -->
# sources/cloud-native/containerd/api/types/sandbox.pb.go

Purpose: generated protobuf Go binding for sandbox metadata objects managed by sandbox controllers.

Important APIs/types/functions: `Sandbox` includes `SandboxID`, nested `Sandbox_Runtime`, `Spec`, labels, `CreatedAt`, `UpdatedAt`, extensions, and `Sandboxer`. `Sandbox_Runtime` includes runtime `Name` and `Options` as `Any`. Generated getters expose nil-safe access to maps, timestamps, and `Any` fields.

Control flow: generated descriptor initialization builds message info for `Sandbox`, map-entry types, and nested runtime. Runtime behavior is limited to protobuf reflection and getters.

State/persistence: sandbox records persist identity, runtime selection/options, spec blob, labels, timestamps, extension blobs, and owning sandboxer. Maps serialize as protobuf map entries; timestamps use protobuf timestamp semantics.

Dependencies/integration: imports `google.protobuf.Any` and `Timestamp`; Go package is `github.com/containerd/containerd/api/types`. The client exposes sandbox store/controller proxies from `client.go`, and container metadata can reference a sandbox ID through `WithSandbox`.

Risks: `Any` fields require type registration/consumer knowledge. Map fields are mutable in Go and can be nil. Schema comments contain typos but not semantic issues. Field number gap to `sandboxer = 10` should be preserved for compatibility.

Test signals: sandbox store/controller tests should round-trip runtime options, spec, labels, extensions, and timestamp conversions; generated code should match `sandbox.proto`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/sandbox.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/sandbox.proto -->
# sources/cloud-native/containerd/api/types/sandbox.proto

Purpose: defines the sandbox metadata wire contract for containerd sandbox controllers.

Important APIs/types/functions: `Sandbox` stores `sandbox_id`, nested `Runtime` with name/options, OCI-like `spec` as `Any`, labels, created/updated timestamps, extension blobs, and `sandboxer` controller name.

Control flow: schema-only file; field layout controls persistence and gRPC compatibility.

State/persistence: acts as persisted sandbox metadata for controllers. Labels and extensions provide open-ended state; timestamps track creation/mutation.

Dependencies/integration: imports protobuf `Any` and `Timestamp`; `go_package` maps to API types. Used by sandbox service APIs and client sandbox proxy accessors.

Risks: untyped `Any` payloads and arbitrary extensions can create decode/version skew. Controller name must match an available sandbox controller. Schema does not validate spec type or label keys.

Test signals: sandbox service tests should cover create/update/list serialization, extension preservation, runtime option compatibility, and timestamp behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/sandbox.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/task/doc.go -->
# sources/cloud-native/containerd/api/types/task/doc.go

Purpose: package documentation for the task API type package.

Important APIs/types/functions: declares package `task` and documents it as defining the task service. Actual exported API types are generated from `task.proto`.

Control flow: none.

State/persistence: none directly.

Dependencies/integration: provides Go package identity for `github.com/containerd/containerd/api/types/task`.

Risks: minimal; package docs are sparse.

Test signals: package compilation with `task.pb.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/task/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/task/task.pb.go -->
# sources/cloud-native/containerd/api/types/task/task.pb.go

Purpose: generated Go binding for task process status and process-info messages.

Important APIs/types/functions: enum `Status` has `UNKNOWN`, `CREATED`, `RUNNING`, `STOPPED`, `PAUSED`, and `PAUSING` plus generated enum helpers. `Process` carries container/process IDs, pid, status, stdio FIFO paths, terminal flag, exit status, and `ExitedAt`. `ProcessInfo` carries pid plus platform-specific `Any` info.

Control flow: generated enum/message descriptor setup and nil-safe getters. It does not manage process lifecycle; lifecycle is implemented in task service/shims and surfaced through these messages.

State/persistence: serialized process state appears in task service responses and event payloads. FIFO path fields are used by client I/O attach code to reconstruct `cio.FIFOSet`.

Dependencies/integration: imports protobuf `Any` and `Timestamp`. `client/container.go` checks `Process.Status` before attaching existing IO and copies pid/status fields from task service responses.

Risks: `UNKNOWN` status intentionally suppresses IO attach in the client because FIFO paths may be absent. `ProcessInfo.Info` is platform-specific and requires consumer-specific decoding. PID and exit status are uint32, matching API conventions but not all host abstractions.

Test signals: task service/client tests should cover status transitions, attach behavior for `UNKNOWN`, timestamp conversion, and platform-specific `ProcessInfo` decode.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/task/task.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/task/task.proto -->
# sources/cloud-native/containerd/api/types/task/task.proto

Purpose: source schema for process/task status data exposed by containerd task APIs.

Important APIs/types/functions: `Status` enum enumerates process lifecycle states. `Process` records container ID, process ID, pid, status, stdio paths, terminal flag, exit status, and exit timestamp. `ProcessInfo` carries pid plus platform-dependent extra info as `Any`.

Control flow: schema-only; status values define the external state machine vocabulary used by task service clients.

State/persistence: captures live or historical task/process state in task RPC responses/events. Stdio path fields are persisted long enough for clients to attach to FIFOs.

Dependencies/integration: imports protobuf `Any` and `Timestamp`; generated Go package is `api/types/task`. The client uses this schema in `container.Task` and `loadTask`.

Risks: clients must handle `UNKNOWN` and future enum values defensively. FIFO path values are host paths and may be absent, stale, or sensitive. Platform-specific `Any` needs clear type registration.

Test signals: generated bindings, task state transition events, attach/load behavior, and process-info platform payload round trips.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/task/task.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/container.pb.go -->
# sources/cloud-native/containerd/api/types/transfer/container.pb.go

Purpose: generated Go binding for transfer endpoints that refer to paths inside active containers.

Important APIs/types/functions: `ContainerPath` has `ContainerID`, `Path`, `NoWalk`, and `PreserveOwnership` with standard generated methods/getters.

Control flow: no operational flow beyond protobuf descriptor init and getters.

State/persistence: serialized as transfer source/destination metadata for archive-like operations. `NoWalk` changes directory traversal semantics; `PreserveOwnership` affects extraction ownership semantics.

Dependencies/integration: package `transfer`, generated from `container.proto`; consumed by transfer service/proxy layers that copy data to/from container filesystems.

Risks: path interpretation is delegated to transfer implementation and must avoid traversal/symlink surprises. Ownership preservation has privilege and user namespace implications. `ContainerID` must resolve in the active namespace.

Test signals: transfer tests should cover stat-like `NoWalk`, recursive walk, ownership preservation, missing container/path, and namespace isolation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/container.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/container.proto -->
# sources/cloud-native/containerd/api/types/transfer/container.proto

Purpose: schema for identifying a filesystem path inside an active container as a transfer source or destination.

Important APIs/types/functions: `ContainerPath` defines `container_id`, `path`, `no_walk`, and `preserve_ownership`.

Control flow: schema-only; comments define traversal and extraction ownership behavior.

State/persistence: transfer request metadata only; actual filesystem state lives in the container/snapshot.

Dependencies/integration: `go_package` maps to transfer API types. Transfer service implementations use it to archive/extract container paths.

Risks: schema does not constrain absolute/relative paths, symlink behavior, or uid/gid validity. Consumers must enforce namespace and permission rules.

Test signals: generated binding consistency and transfer integration around directory traversal and ownership.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/container.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/doc.go -->
# sources/cloud-native/containerd/api/types/transfer/doc.go

Purpose: package stub for transfer API type bindings.

Important APIs/types/functions: declares package `transfer`; generated files provide the exported messages/enums.

Control flow: none.

State/persistence: none directly.

Dependencies/integration: anchors the Go package for transfer protobuf types.

Risks: low; documentation is minimal.

Test signals: package compilation with all transfer generated files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/imagestore.pb.go -->
# sources/cloud-native/containerd/api/types/transfer/imagestore.pb.go

Purpose: generated bindings for image-store transfer configuration, covering image naming, platform filtering, metadata walking, and unpack instructions.

Important APIs/types/functions: `ImageStore` has name, labels, platforms, all-metadata flag, manifest limit, extra references, and unpack configurations. `UnpackConfiguration` carries platform and snapshotter. `ImageReference` describes import/lookup naming behavior with prefix, overwrite, add-digest, and skip-named-digest flags.

Control flow: generated descriptor/map setup and getters only.

State/persistence: request/response metadata for transfer operations. Labels can be applied to stored images; platform and manifest options control content graph traversal; unpack config triggers snapshotter state changes in consumers.

Dependencies/integration: imports `types/platform.proto` and generated platform types. Transfer service and proxy code use these messages when importing/exporting/pulling/pushing image content.

Risks: naming flags interact subtly and can overwrite or suppress references. `ManifestLimit` can trade completeness for bounded traversal. Multiple unpack configs can cause partial success/failure complexity.

Test signals: transfer tests should cover prefix matching, digest reference creation, overwrite policy, all metadata versus platform-limited transfer, manifest limits, and multi-platform unpack.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/imagestore.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/imagestore.proto -->
# sources/cloud-native/containerd/api/types/transfer/imagestore.proto

Purpose: source schema for image-store endpoints in transfer workflows.

Important APIs/types/functions: `ImageStore` identifies an image name and labels, platform filters, all-metadata/manifest-limit traversal settings, extra import references, and repeated `UnpackConfiguration`. `UnpackConfiguration` selects platform and snapshotter. `ImageReference` encodes prefix/digest/overwrite matching and storing rules.

Control flow: schema comments define resolver/store behavior; actual traversal/unpack logic is in transfer implementations.

State/persistence: influences image metadata records, content graph retention, and snapshotter unpack state created by transfer operations.

Dependencies/integration: imports `types/platform.proto`; consumed by transfer API and client `TransferService`.

Risks: spelling/comment typo in snapshotter comment aside, the main risk is ambiguous reference policy. Incomplete platform selections or low manifest limits can omit content users expect.

Test signals: generated code, transfer image import/export cases, naming conflict handling, and unpack per platform/snapshotter.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/imagestore.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/importexport.pb.go -->
# sources/cloud-native/containerd/api/types/transfer/importexport.pb.go

Purpose: generated bindings for tar-stream import/export endpoints in transfer operations.

Important APIs/types/functions: `ImageImportStream` carries stream ID, media type, and force-compress flag. `ImageExportStream` carries stream ID, media type, platform list, all-platforms flag, skip Docker compatibility manifest flag, and skip non-distributable flag.

Control flow: generated protobuf methods only.

State/persistence: messages identify binary streams managed by the transfer streaming protocol; exported/imported content persists in content/image stores outside this message.

Dependencies/integration: imports platform proto types; paired with `streaming.proto` stream control messages and transfer service.

Risks: stream IDs must match active binary streams. Platform/all-platforms flags can conflict semantically and must be resolved by implementation. `ForceCompress` and non-distributable filtering affect reproducibility and distribution legality.

Test signals: import/export tests should cover stream lifecycle, media type handling, compression, platform filters, compatibility manifest generation, and non-distributable exclusion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/importexport.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/importexport.proto -->
# sources/cloud-native/containerd/api/types/transfer/importexport.proto

Purpose: source schema for transfer import/export tar streams.

Important APIs/types/functions: `ImageImportStream` declares a client-to-server raw tar stream with media type and force-compress. `ImageExportStream` declares server-to-client raw tar stream and export filters/options.

Control flow: schema-only; stream direction is documented and implemented by transfer streaming.

State/persistence: stream messages are transient, while content/image records are created or read by the transfer operation.

Dependencies/integration: imports platform types and pairs with `streaming.proto`.

Risks: missing stream validation can deadlock transfers. Media type and platform option combinations must be checked by implementation.

Test signals: bidirectional stream tests, cancellation/error propagation, and archive content validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/importexport.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/progress.pb.go -->
# sources/cloud-native/containerd/api/types/transfer/progress.pb.go

Purpose: generated binding for transfer progress events.

Important APIs/types/functions: `Progress` includes event, name, parent names, current progress, total, and optional content descriptor.

Control flow: generated methods only; event ordering and aggregation happen in transfer implementations.

State/persistence: progress messages are transient telemetry, not authoritative content state. Descriptor field can identify content blobs associated with progress.

Dependencies/integration: imports `types/descriptor.proto`; used by transfer service streams or callbacks.

Risks: progress/total can be unknown or non-monotonic depending on source. Parent relationships are string-based and require consumer interpretation.

Test signals: progress stream tests should cover event ordering, descriptor mapping, unknown totals, cancellation, and parent aggregation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/progress.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/progress.proto -->
# sources/cloud-native/containerd/api/types/transfer/progress.proto

Purpose: source schema for transfer progress telemetry.

Important APIs/types/functions: `Progress` fields are `event`, `name`, repeated `parents`, numeric `progress`/`total`, and a containerd descriptor.

Control flow: schema-only; semantics of event names and parent graph are external.

State/persistence: transient reporting state for long-running transfers.

Dependencies/integration: imports descriptor proto and is consumed by transfer clients.

Risks: weakly typed event/name strings can drift between producers and consumers. Numeric fields need clear handling for unknown totals.

Test signals: generated binding consistency and UI/client handling for event graphs and descriptors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/progress.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/registry.pb.go -->
# sources/cloud-native/containerd/api/types/transfer/registry.pb.go

Purpose: generated bindings for OCI registry transfer endpoints, resolver configuration, authentication callbacks, and HTTP debug options.

Important APIs/types/functions: enum `HTTPDebug` has `DISABLED`, `DEBUG`, `TRACE`, `BOTH`; enum `AuthType` has `NONE`, `CREDENTIALS`, `REFRESH`, `HEADER`. `OCIRegistry` carries reference and resolver. `RegistryResolver` carries auth stream, headers, host directory, default scheme, HTTP debug mode, and logs stream. `AuthRequest` carries host, repository reference, and `WWW-Authenticate` values. `AuthResponse` carries auth type, secret, username, and expiry.

Control flow: generated enum/message helpers and descriptor init only. Authentication callback sequencing is implemented by transfer registry/resolver code.

State/persistence: resolver settings are request-scoped; auth responses may contain credentials and expiry times. Header maps and secrets must be treated as sensitive.

Dependencies/integration: imports protobuf `Timestamp`. Used by transfer service registry source/destination configuration and stream-based auth/log callback plumbing.

Risks: secrets in `AuthResponse` and headers can leak through logs or debugging. `HEADER` auth allows raw authorization header injection. Host directory/default scheme influence trust and endpoint selection. Debug/trace modes may expose credentials if not redacted.

Test signals: registry transfer tests should cover auth challenge/response types, expiry, custom headers, host directory config, HTTP debug/log streams, and secret redaction.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/registry.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/registry.proto -->
# sources/cloud-native/containerd/api/types/transfer/registry.proto

Purpose: source schema for registry-backed transfer endpoints and auth/debug callback contracts.

Important APIs/types/functions: `OCIRegistry` identifies a registry reference plus resolver settings. `RegistryResolver` configures auth stream, headers, host dir, default scheme, HTTP debug, and logs stream. `AuthRequest` and `AuthResponse` define credential callback messages. Enums define HTTP debug and auth response modes.

Control flow: schema-only; comments define callback and debug stream use.

State/persistence: mostly transient transfer configuration, but carries sensitive auth material and optional expiry timestamp.

Dependencies/integration: imports protobuf timestamp and integrates with transfer streaming for auth/log callbacks.

Risks: auth fields are security-sensitive. Debug/trace output and logs stream must avoid credential disclosure. Header/default scheme/host-dir values can weaken registry TLS/auth behavior if mishandled.

Test signals: auth flow tests for credentials/refresh/header, no-auth behavior, challenge parsing, TLS host-dir behavior, and log redaction.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/registry.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/streaming.pb.go -->
# sources/cloud-native/containerd/api/types/transfer/streaming.pb.go

Purpose: generated bindings for the binary stream control protocol used by transfer import/export and callback streams.

Important APIs/types/functions: `Data` carries raw bytes. `WindowUpdate` carries flow-control credit. `ReadStream` identifies client-to-server data streams. `WriteStream` identifies server-to-client data streams. Each has standard generated methods/getters.

Control flow: generated code only; stream flow control and data movement are implemented by transfer stream creator/proxy code.

State/persistence: stream data is transient; no durable state in the message itself. Window updates represent in-flight flow-control state.

Dependencies/integration: package `transfer`; used with import/export and registry auth/log streaming.

Risks: flow-control bugs can deadlock or over-buffer transfers. Raw byte streams need cancellation/error propagation. Stream IDs must be unique and scoped to an operation.

Test signals: streaming tests should cover backpressure, large payloads, EOF/cancel/error behavior, concurrent streams, and media type propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/streaming.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/streaming.proto -->
# sources/cloud-native/containerd/api/types/transfer/streaming.proto

Purpose: source schema for transfer binary stream messages and stream descriptors.

Important APIs/types/functions: `Data`, `WindowUpdate`, `ReadStream`, and `WriteStream` model bytes, flow-control credits, and named stream endpoints with media type.

Control flow: schema comments define stream direction; actual protocol control is in transfer implementation.

State/persistence: transient stream protocol state only.

Dependencies/integration: used by image import/export stream messages and transfer proxy stream creation.

Risks: signed `int32` window updates need validation against negative or overflow behavior. Media type is not constrained by schema.

Test signals: generated binding consistency plus stream protocol tests for flow-control correctness and cancellation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/streaming.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/client.go -->
# sources/cloud-native/containerd/client/client.go

Purpose: central high-level containerd client implementation. It constructs gRPC-backed or injected-service clients, exposes service adapters, manages defaults, and implements image/container convenience operations.

Important APIs/types/functions: `New`, `NewWithConn`, `Client`, `Reconnect`, `Runtime`, `IsServing`, `Containers`, `NewContainer`, `LoadContainer`, `Fetch`, `Push`, `GetImage`, `ListImages`, `Restore`, `GetLabel`, `Subscribe`, `Close`, service accessors, `Version`, `Server`, snapshotter/runtime introspection helpers, and `RuntimeInfo`. `RemoteContext` holds resolver, platform, unpack, label, handler, concurrency, metadata, and referrer options.

Control flow: `New` applies `Opt`s, configures defaults, builds gRPC dial options with insecure local transport, connect backoff, context dialer, default message sizes, optional namespace interceptors, and a reconnect connector. Default runtime/sandboxer/snapshotter resolve lazily from namespace labels under a mutex and then cache. Container creation wraps operations in a lease, applies `NewContainerOpts`, creates metadata, and traces attributes. Fetch prepares a remote context, rejects unpack-on-fetch, resolves platform matcher, creates a lease, calls lower-level fetch helpers, and creates an image record. Push resolves platform matcher, appends digest to refs lacking `@`, obtains a pusher, wraps handlers, applies optional upload limiter, and calls `remotes.PushContent`. Service methods return injected services when present, otherwise create proxies from the current gRPC connection.

State/persistence: holds connection state behind `connMu`, default namespace/platform, cached default runtime/sandboxer, and optional service injection fields. It persists container metadata through the container service, images through image service, content through content store, leases around content/snapshot mutations, and checkpoint indexes via content/image records. Namespace labels influence default runtime, sandboxer, and snapshotter.

Dependencies/integration: integrates with containerd gRPC API services, core content/images/containers/snapshots/events/leases/sandbox/transfer/mount/introspection packages, typeurl, OCI specs, Docker resolver, tracing, defaults, and plugin introspection. `init` registers common runtime-spec type URLs and works around Windows gRPC resolver behavior.

Risks: default gRPC transport is insecure and assumes local/containerd socket trust. Lazy default caching can hide later namespace-label changes. Many service accessors create proxies with `c.conn` even if nil unless callers used injected services consistently. `SnapshotService` falls back to default snapshotter on label resolution error, which can mask namespace issues. `Push` mutates refs without digest into digest-qualified refs. Runtime option typeurl marshal/unmarshal failures surface late.

Test signals: unit/integration tests should cover dial option precedence, namespace interceptors, reconnect, injected-service mode, default label resolution/caching, lease cleanup on errors, fetch/push platform selection, service accessors with nil conn, version/server unavailable errors, snapshotter plugin lookup, and runtime info typeurl decode.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/client_opts.go -->
# sources/cloud-native/containerd/client/client_opts.go

Purpose: option types for configuring the high-level client and remote image transfer contexts.

Important APIs/types/functions: `clientOpts`, `Opt`, and functions for default namespace/runtime/sandboxer/platform, dial/call options, service injection, and timeout. `RemoteOpt` configures `RemoteContext`: platform strings/matcher, pull unpack, unpack opts, snapshotter, labels, child label mapping, resolver, image handlers/wrappers, download/upload limiters, concurrent layer buffer, all metadata, and referrers provider.

Control flow: each option mutates a config struct. `WithDialOpts` replaces base dial options, while `WithExtraDialOpts` appends to defaults. `WithPlatform` deduplicates platform strings. `WithPlatformMatcher` supersedes platform strings in later client logic. Label options initialize maps and copy values.

State/persistence: options affect client defaults and remote operation behavior but do not persist by themselves. Pull labels persist on image records; snapshotter/unpack options affect snapshot state when used.

Dependencies/integration: uses Go `maps/slices`, containerd content/images/remotes/snapshots, platform matchers, OCI descriptors, semaphores, and gRPC options.

Risks: `WithDialOpts` can accidentally remove required defaults such as credentials, dialer, or message size unless caller supplies replacements. Platform matcher precedence can surprise callers combining platform options. Label maps passed through may be later mutated by caller depending on option.

Test signals: option composition tests should cover append vs replace dial opts, repeated platform dedupe, label copy behavior, matcher precedence, limiter fields, and service injection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/client_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/container.go -->
# sources/cloud-native/containerd/client/container.go

Purpose: high-level container metadata object and lifecycle helpers for task creation, metadata update, checkpoint, restore, and IO attachment.

Important APIs/types/functions: `Container` interface, concrete `container`, `containerFromRecord`, `Info`, `Extensions`, `Labels`, `SetLabels`, `Spec`, `Delete`, `Task`, `Image`, `NewTask`, `Update`, `handleMounts`, `Restore`, `Checkpoint`, `loadTask`, `attachExistingIO`, and `loadFifos`.

Control flow: `Info` refreshes metadata by default. `Delete` refuses to delete if a running task loads, then applies delete options such as snapshot cleanup. `NewTask` creates IO, builds `CreateTaskRequest`, adds snapshot mounts with SELinux mount labels, loads runtime/options, applies task opts, marshals task options, and calls task service create; IO is canceled/closed on failure. `Checkpoint` builds an OCI index, defaults CRIU options, loads image/container metadata, leases content, annotates image/runtime/snapshotter, applies checkpoint opts, writes index content, and creates an image record. `Restore` creates IO and sends a task create request with a checkpoint descriptor annotation.

State/persistence: caches local metadata in the `container` struct. Metadata changes persist through container service. Task creation creates shim/task state and FIFO paths. Checkpoint creates content blobs and an image record. FIFO closer removes FIFO files and best-effort parent directories.

Dependencies/integration: uses task gRPC API, API mount descriptors, runc checkpoint options, task status types, errdefs, fifo, typeurl, OCI specs, image/content services, cio, oci, tracing, and container service.

Risks: `SetLabels` updates only provided label paths and cannot remove unspecified labels. `Spec` assumes `r.Spec` is non-nil and JSON-encoded. `Delete` treats any successful task load as running; races remain between check and delete. IO attach must avoid multiple readers. `loadFifos` removes FIFO paths, so misuse can affect another consumer. Checkpoint requires an image-backed container.

Test signals: cover metadata refresh/no-refresh, label update masks, spec decode errors, delete with running task, NewTask cleanup on create failure, mount label propagation, checkpoint image/index contents, restore request annotations, attach behavior for unknown status, and FIFO cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/container_checkpoint_opts.go -->
# sources/cloud-native/containerd/client/container_checkpoint_opts.go

Purpose: checkpoint option functions that add image, task, runtime options, and writable-layer data to a checkpoint OCI index.

Important APIs/types/functions: `ErrMediaTypeNotFound`, `CheckpointOpts`, `WithCheckpointImage`, `WithCheckpointTask`, `WithCheckpointRuntime`, `WithCheckpointRW`, `WithCheckpointTaskExit`, and `GetIndexByMediaType`.

Control flow: `WithCheckpointImage` appends the base image target descriptor. `WithCheckpointTask` marshals CRIU options, calls task service `Checkpoint`, appends returned descriptors, writes serialized checkpoint options as content, and appends its descriptor. `WithCheckpointRuntime` serializes runtime options if present and appends a runtime-options content descriptor. `WithCheckpointRW` computes a diff for the container snapshot and appends it. `WithCheckpointTaskExit` toggles `copts.Exit` before task checkpoint runs. `GetIndexByMediaType` scans manifests.

State/persistence: writes checkpoint option blobs, runtime option blobs, task checkpoint descriptors, and rootfs diffs into the content store/index. Platform is set to current GOOS/GOARCH for local checkpoint-specific descriptors.

Dependencies/integration: task API, runc checkpoint options, diff/rootfs/content helpers, typeurl/proto, image media types, platform defaults.

Risks: option order matters, especially `WithCheckpointTaskExit` before `WithCheckpointTask`. `WithCheckpointRW` depends on snapshot key/snapshotter and can be expensive. `GetIndexByMediaType` returns a copy of the descriptor, not a pointer into the slice, which is fine for reads but not mutation. AlreadyExists handling is performed by caller.

Test signals: checkpoint option ordering, content media types, CRIU option serialization, task service descriptor conversion, runtime option preservation, RW diff creation, and media type lookup errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/container_checkpoint_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/container_opts.go -->
# sources/cloud-native/containerd/client/container_opts.go

Purpose: option functions for creating, updating, and deleting container metadata.

Important APIs/types/functions: `DeleteOpts`, `NewContainerOpts`, `UpdateContainerOpts`, `InfoOpts`, `InfoConfig`, `WithRuntime`, `WithSandbox`, `WithImage`, `WithImageName`, label options, `WithImageStopSignal`, `WithSnapshotter`, `WithSnapshot`, `WithSnapshotCleanup`, `WithNewSnapshot`, `WithNewSnapshotView`, `WithContainerExtension`, `WithNewSpec`, `WithSpec`, and `WithoutRefreshedMetadata`.

Control flow: creation options mutate a `containers.Container` before `Create`. Snapshot options resolve snapshotter, validate or create view/prepare snapshots from image rootfs chain ID, and set `SnapshotKey`/`Image`. Spec options generate/apply OCI specs and marshal them into typeurl `Any`. Extension option validates non-empty name and type registration.

State/persistence: persists runtime info/options, sandbox ID, image name, labels, stop signal label, snapshotter/key, extensions, and spec in container metadata. Snapshot creation/delete mutates snapshotter state.

Dependencies/integration: content/image config reading, snapshots, namespaces, OCI spec generation, typeurl, errdefs, identity chain IDs, and rootfs snapshot option resolution.

Risks: option order matters; `WithSnapshotter` must precede snapshot options. Label options can clear or merge labels depending on function. `WithImageConfigLabels` trusts image config labels wholesale. Snapshot creation can leak snapshots if later options fail unless caller cleans up. `WithContainerExtension` requires typeurl registration.

Test signals: option ordering, snapshot cleanup after create failure, label overwrite/merge behavior, image config labels and stop signal, extension registration errors, generated spec namespace defaulting, and update masks through callers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/container_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/container_opts_unix.go -->
# sources/cloud-native/containerd/client/container_opts_unix.go

Purpose: Unix-only container options for creating user-namespace-remapped snapshots and read-only views.

Important APIs/types/functions: `WithRemappedSnapshot`, `WithUserNSRemappedSnapshot`, `WithRemappedSnapshotView`, `WithUserNSRemappedSnapshotView`, internal `withRemappedSnapshotBase`, `remapRootFS`, and `chown`.

Control flow: computes image rootfs chain ID, derives a stable remapped snapshot ID from UID/GID mappings, reuses existing remapped snapshots if available, otherwise prepares a temporary remap snapshot, temp-mounts it, walks the filesystem and `Lchown`s every path through the userns map, commits the remapped snapshot, then prepares or views the requested container snapshot.

State/persistence: creates reusable remapped snapshot layers and per-container snapshots/views. Mutates file ownership in the remap snapshot while preserving special permission bits on non-symlinks.

Dependencies/integration: Unix build tag, snapshotters, mount temp mounts, internal userns mapping, OCI runtime-spec ID mappings, identity chain IDs, syscall stat, filesystem walking.

Risks: type asserts `i.(*image)`, so custom `Image` implementations can panic. Full filesystem walk can be slow and permission-sensitive. Error cleanup removes `usernsID` rather than the `usernsID+"-remap"` active snapshot in one path, which deserves scrutiny. Ownership remap must avoid symlink dereference, which `Lchown` handles.

Test signals: remap ID determinism, custom image interface behavior, reuse existing remap snapshot, cleanup on remap failure, symlink ownership, setuid/setgid/sticky preservation, read-only view creation, and large filesystem performance.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/container_opts_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/container_restore_opts.go -->
# sources/cloud-native/containerd/client/container_restore_opts.go

Purpose: restore option functions that reconstruct a container from checkpoint image index metadata and content.

Important APIs/types/functions: errors for missing image/runtime/snapshotter annotations, `RestoreOpts`, `WithRestoreImage`, `WithRestoreRuntime`, `WithRestoreSpec`, and `WithRestoreRW`.

Control flow: `WithRestoreImage` reads image and snapshotter annotations, loads the referenced image, computes rootfs parent chain, prepares a new snapshot, and sets container image/snapshot fields. `WithRestoreRuntime` reads runtime annotation, optionally finds runtime-options media type, reads and unmarshals options, and sets runtime info. `WithRestoreSpec` reads checkpoint config media type and sets container spec. `WithRestoreRW` finds gzip layer, mounts the snapshot, and applies the diff.

State/persistence: creates a restored container metadata record and snapshot state; reads checkpoint image content and applies RW layer content to snapshot.

Dependencies/integration: checkpoint media type constants from images package, content store, proto `Any`, diff service, image rootfs, OCI index annotations.

Risks: `WithRestoreImage` checks `name == ""` when validating snapshotter annotation, likely intending `snapshotter == ""`; empty snapshotter may slip through. Type assertion to `*image` rejects custom image implementations. It assumes gzip layer media type for RW diff. Partial restore can leave prepared snapshots if later options fail.

Test signals: missing annotation errors, runtime option round-trip, spec restore, RW layer application, snapshot cleanup on failure, custom image behavior, and the snapshotter-empty validation edge case.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/container_restore_opts.go -->

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

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/diff.go -->
# sources/cloud-native/containerd/client/diff.go

Purpose: small adapter exposing the diff service as a combined comparer/applier interface.

Important APIs/types/functions: `DiffService` embeds `diff.Comparer` and `diff.Applier`; `NewDiffServiceFromClient` returns a proxy diff applier cast to `DiffService`.

Control flow: no complex flow; constructor delegates to core diff proxy.

State/persistence: diff operations performed through the returned service can create content and apply filesystem changes, but this file holds no state.

Dependencies/integration: diff gRPC API, core diff interfaces, diff proxy. Used by image unpack, checkpoint RW diff, and restore RW apply.

Risks: constructor uses a type assertion on proxy result; interface changes could panic. Behavior depends entirely on proxy implementation.

Test signals: compile-time/interface assertion through tests, compare/apply RPC error conversion, integration with unpack/checkpoint/restore.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/diff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/events.go -->
# sources/cloud-native/containerd/client/events.go

Purpose: gRPC-backed event publish/forward/subscribe adapter.

Important APIs/types/functions: `EventService` combines publisher, forwarder, subscriber. `NewEventServiceFromClient` returns `eventRemote`. Methods `Publish`, `Forward`, and `Subscribe` marshal typeurl events and protobuf envelopes.

Control flow: publish/forward are single RPCs with native error conversion. Subscribe opens a stream, returns event and error channels, and starts a goroutine receiving envelopes until stream error or context cancellation. It suppresses `context.Canceled` as an error but reports other context errors.

State/persistence: events are transient; envelopes carry timestamp, namespace, topic, and `Any` payload. Goroutine/channel lifecycle is the main local state.

Dependencies/integration: events gRPC API, API `Envelope`, typeurl, protobuf timestamp conversion, core events interfaces.

Risks: returned event channel is not closed in the goroutine, only error channel is closed; consumers must follow documented error-channel termination. Initial subscribe RPC errors are sent without errgrpc conversion. Backpressure on `evq` can block receiver goroutine.

Test signals: publish/forward marshal failures, native error conversion, subscribe initial error, stream EOF/error, context cancel/deadline, channel behavior, and slow consumer backpressure.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/export.go -->
# sources/cloud-native/containerd/client/export.go

Purpose: high-level wrapper for exporting images/content as an OCI tar archive, optionally Docker manifest compatible.

Important APIs/types/functions: `Client.Export(ctx, w, opts...)` delegates to `archive.Export` with the client content store.

Control flow: single delegation; archive options drive selection and formatting.

State/persistence: reads from the content store and writes to the provided `io.Writer`; no client metadata mutation.

Dependencies/integration: core images archive exporter and content store accessor.

Risks: writer errors and content-store missing blobs propagate from archive exporter. Large exports depend on caller-provided writer backpressure.

Test signals: archive format tests, writer error propagation, platform option behavior in archive exporter, and missing content errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/grpc.go -->
# sources/cloud-native/containerd/client/grpc.go

Purpose: namespace-injecting gRPC client interceptors used when a client has a default namespace.

Important APIs/types/functions: `namespaceInterceptor`, its `unary` and `stream` methods, and `newNSInterceptors`.

Control flow: each interceptor checks whether the context already has a namespace; if absent, it adds the configured default namespace before invoking the unary or stream RPC.

State/persistence: no durable state; the namespace value travels in context metadata through downstream namespace machinery.

Dependencies/integration: containerd namespaces package and gRPC interceptor APIs. `New` installs these interceptors when `WithDefaultNamespace` is set.

Risks: callers using `WithDialOpts` can replace default dial options and skip these interceptors unless they add equivalents. Existing namespace in context always wins over default.

Test signals: unary and stream namespace injection, preservation of explicit namespace, interaction with custom dial options, and service calls under default namespace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/grpc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/image.go -->
# sources/cloud-native/containerd/client/image.go

Purpose: high-level image object implementation with metadata access, rootfs/config resolution, size/usage calculation, unpacking, and platform-aware behavior.

Important APIs/types/functions: `Image` interface, usage options, `NewImage`, `NewImageWithPlatform`, concrete `image`, `RootFS`, `Size`, `Usage`, `Config`, `IsUnpacked`, `Spec`, `UnpackConfig`, unpack options, `Unpack`, `getManifest`, `getLayers`, `checkSnapshotterSupport`, `ContentStore`, and `Platform`.

Control flow: `RootFS` caches diff IDs under a mutex. `Usage` maps client options into usage package options. `Spec` reads and unmarshals image config JSON. `Unpack` leases content, applies unpack options, resolves manifest/layers, resolves snapshotter, optionally checks snapshotter platform support, applies each layer through rootfs/diff services, writes uncompressed digest labels for newly unpacked layers, then labels the config blob with a snapshot GC reference.

State/persistence: caches `diffIDs` in memory. Unpack creates snapshotter state, updates content labels for uncompressed digests and snapshot GC references, and uses leases for mutation lifetime.

Dependencies/integration: content, diff, images/usage, snapshots, keyed mutex type, labels, rootfs, errdefs, platforms, OCI descriptors/specs, digest/identity, semaphores.

Risks: `UnpackConfig` has duplication suppressor and limiter fields but this `Unpack` implementation does not use them directly, so callers expecting local throttling may need higher-level paths. `getLayers` fails if image layer count differs from diff IDs after filtering non-layer artifact descriptors. Platform support check only runs for OSFeatures or explicit option. Cached diffIDs may become stale if image metadata changes behind the object.

Test signals: RootFS caching, usage option mapping, config/spec errors, unpack layer application and label updates, mismatched layer/diffID errors, IsUnpacked not-found behavior, platform support checks, and lease cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/image_store.go -->
# sources/cloud-native/containerd/client/image_store.go

Purpose: gRPC-backed implementation of the core `images.Store` interface.

Important APIs/types/functions: `remoteImages`, `NewImageStoreFromClient`, `Get`, `List`, `Create`, `Update`, `Delete`, `imageToProto`, `imageFromProto`, and `imagesFromProto`.

Control flow: each store method builds the corresponding image service request, optionally includes update masks/delete options, converts source-date epoch from context for create/update, invokes gRPC, converts errors through `errgrpc`, and maps protobuf descriptors/timestamps.

State/persistence: persists image name, labels, target descriptor, timestamps, and delete semantics through the image service. Delete can be synchronous and can target a specific descriptor.

Dependencies/integration: images gRPC API, errgrpc, protobuf timestamps/field masks, epoch context, OCI descriptor conversion, core images store.

Risks: conversion assumes non-nil target/image protos from server. Create/update source date epoch behavior depends on context. Delete target filtering semantics are delegated to server.

Test signals: proto conversion round trips, source-date epoch propagation, update masks, delete sync/target options, list filters, and native error conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/image_store.go -->
