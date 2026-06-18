# subset-b-000076 research

This grouped report covers the requested containerd service plugins and snapshotter files. Each source file has its own reconciliation section wrapped with the required markers.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/namespaces/local.go -->
# sources/cloud-native/containerd/plugins/services/namespaces/local.go

## Purpose
`local.go` implements the local namespaces service plugin. It exposes the namespaces API client directly against the metadata database, with event publication for create, update, and delete operations.

## Important APIs, Types, And Functions
The registered service plugin has ID `services.NamespacesService` and requires the metadata and event plugins. The `local` type stores a `*metadata.DB` and an `events.Publisher` and implements `api.NamespacesClient`. Main methods are `Get`, `List`, `Create`, `Update`, `Delete`, plus transaction helpers `withStore`, `withStoreView`, and `withStoreUpdate`.

## Control Flow
Reads run inside `metadata.DB.View` and writes inside `metadata.DB.Update`, each wrapping a `metadata.NewNamespaceStore(tx)`. `Create` stores the namespace and labels, then publishes `/namespaces/create` with the namespace placed in context. `Update` either applies field-mask paths under `labels.` or replaces all labels, then publishes `/namespaces/update`. `Delete` removes the namespace and publishes `/namespaces/delete`.

## State And Persistence
Namespace names and labels persist in the shared Bolt-backed metadata database. Events are transient but important for subscribers. Label deletion is represented by setting an empty string through the namespace store contract.

## Dependencies And Integration Points
This file integrates the plugin registry, metadata namespace store, containerd events, protobuf namespace service types, and `errgrpc` conversion. It is consumed by the gRPC wrapper in `service.go`.

## Risks
The code assumes `req.Namespace` is non-nil in `Create` and `Update`; malformed direct client calls can panic before validation. `Update` only accepts label field paths and rejects all other field-mask paths. Event publication happens after the DB transaction, so a publish failure returns an error even though the metadata change already committed.

## Test Signals
No direct tests are in this subset. Coverage is expected through namespace service integration tests elsewhere and event subscriber behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/namespaces/local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/namespaces/service.go -->
# sources/cloud-native/containerd/plugins/services/namespaces/service.go

## Purpose
`service.go` exposes the local namespaces service through the containerd gRPC plugin system.

## Important APIs, Types, And Functions
The gRPC plugin registers ID `namespaces`, requires service plugins, and retrieves `services.NamespacesService`. The `service` type embeds `api.UnimplementedNamespacesServer`, stores an `api.NamespacesClient`, and implements `Register`, `Get`, `List`, `Create`, `Update`, and `Delete`.

## Control Flow
Initialization resolves the already-registered local namespaces client, wraps it, and returns a gRPC registrar. Each RPC method forwards the request directly to the local client without additional business logic.

## State And Persistence
This file owns no durable state. Persistence is delegated to `local.go` and the metadata namespace store.

## Dependencies And Integration Points
It connects `github.com/containerd/containerd/api/services/namespaces/v1` to the plugin registry and `grpc.Server`. It relies on the service plugin ID declared in `plugins/services/services.go`.

## Risks
The cast to `api.NamespacesClient` assumes the service plugin has the expected concrete API. Validation, event semantics, and error conversion remain entirely in the local service.

## Test Signals
No direct tests are present. A failure would normally surface when gRPC plugin initialization or namespace RPC smoke tests run.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/namespaces/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/opt/path_unix.go -->
# sources/cloud-native/containerd/plugins/services/opt/path_unix.go

## Purpose
`path_unix.go` defines the default opt directory for non-Windows builds.

## Important APIs, Types, And Functions
The only exported behavior is the package-level `defaultPath` constant set to `/opt/containerd`.

## Control Flow
There is no executable control flow. The value is selected by the `!windows` build tag.

## State And Persistence
The path is used by the opt service as the base directory for `bin` and `lib` subdirectories. It affects process environment setup but does not persist anything itself.

## Dependencies And Integration Points
It feeds `service.go` in the same package and is mutually exclusive with `path_windows.go`.

## Risks
The hard-coded Unix default may require elevated permissions to create, depending on how containerd is launched. Operators can override it through opt plugin config.

## Test Signals
No direct tests are included. Build-tag selection is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/opt/path_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/opt/path_windows.go -->
# sources/cloud-native/containerd/plugins/services/opt/path_windows.go

## Purpose
`path_windows.go` defines the Windows-specific default opt directory.

## Important APIs, Types, And Functions
The package-level `defaultPath` variable is `filepath.Join(defaults.DefaultRootDir, "opt")`.

## Control Flow
There is no runtime control flow beyond variable initialization. The file is selected on Windows by the absence of a restrictive build tag and the competing Unix file's `!windows` tag.

## State And Persistence
The value controls where the opt service creates `bin` and `lib` directories on Windows. It does not directly create files.

## Dependencies And Integration Points
It depends on `path/filepath` and `containerd/v2/defaults`, and is consumed by `opt/service.go`.

## Risks
The path follows the configured/default containerd root, so unexpected root changes affect PATH and library search path injection.

## Test Signals
No direct tests are present. Cross-platform builds validate that the package has exactly one `defaultPath`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/opt/path_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/opt/service.go -->
# sources/cloud-native/containerd/plugins/services/opt/service.go

## Purpose
`service.go` registers an internal opt manager plugin that prepares an opt directory and prepends its `bin` and `lib` paths to process environment variables.

## Important APIs, Types, And Functions
`Config` has a TOML `path` field. The internal plugin ID is `opt`. Initialization writes `ic.Meta.Exports["path"]`, creates `<path>/bin` and `<path>/lib`, and updates `PATH` and `LD_LIBRARY_PATH`. The returned `manager` type is empty.

## Control Flow
At plugin initialization, the configured path defaults from the platform file. The service creates directories with mode `0711`, then calls `os.Setenv` to prepend the new executable and library paths.

## State And Persistence
The plugin persists directories on disk and mutates the daemon process environment. The environment mutation is global to the process and can affect later plugin execution and child processes.

## Dependencies And Integration Points
It uses the containerd plugin registry, `plugins.InternalPlugin`, filesystem APIs, and platform path defaults.

## Risks
`LD_LIBRARY_PATH` is Unix-centric but used unconditionally, including Windows builds. Prepending paths can change binary/library resolution order for later subprocesses. Directory creation failures stop plugin initialization.

## Test Signals
No direct tests are in this subset. Startup behavior and plugin metadata exports are the expected validation points.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/opt/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/sandbox/controller_service.go -->
# sources/cloud-native/containerd/plugins/services/sandbox/controller_service.go

## Purpose
This file implements the gRPC service for sandbox controllers. It multiplexes requests to named sandbox controller plugins and publishes lifecycle events.

## Important APIs, Types, And Functions
The plugin registers gRPC ID `sandbox-controllers` and gathers controllers from both `plugins.PodSandboxPlugin` and `plugins.SandboxControllerPlugin`. `controllerService` implements `api.ControllerServer`. Key RPCs are `Create`, `Start`, `Stop`, `Wait`, `Status`, `Shutdown`, `Metrics`, and `Update`; `getController` validates controller names.

## Control Flow
Initialization builds a map of controller name to `sandbox.Controller`, tolerating missing controller plugin groups but failing if none exist. RPCs validate `Sandboxer`, call the selected controller, translate protobuf values to core `sandbox` and `mount` structures, and convert errors through `errgrpc`. `Create`, `Start`, and `Wait` publish `/sandboxes/create`, `/sandboxes/start`, and `/sandboxes/exit`.

## State And Persistence
The service itself is stateless except for the controller map and event publisher. Durable sandbox state belongs to individual controllers and the sandbox store service.

## Dependencies And Integration Points
It integrates plugin discovery, sandbox core interfaces, protobuf conversion, mount conversion, events exchange, logging, and gRPC registration.

## Risks
Event publication after successful controller operations can return errors after side effects have already happened. `Update` returns a plain error for nil sandbox instead of `errgrpc` conversion. The service trusts controller implementations for persistence, cleanup, metrics shape, and concurrency safety.

## Test Signals
`controller_service_test.go` covers controller lookup errors, request-to-controller option mapping, returned start/status/wait fields, metrics/update delegation, and nil `Extra` normalization.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/sandbox/controller_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/sandbox/controller_service_test.go -->
# sources/cloud-native/containerd/plugins/services/sandbox/controller_service_test.go

## Purpose
This test file validates the sandbox controller gRPC adapter without requiring real sandbox runtimes.

## Important APIs, Types, And Functions
`stubController` implements `sandbox.Controller` and records the last arguments for create, stop, wait, status, shutdown, metrics, and update. `newTestService` builds a `controllerService` with a test controller and event exchange. Test functions cover `getController`, `Create`, `Start`, `Stop`, `Wait`, `Status`, `Shutdown`, `Metrics`, and `Update`.

## Control Flow
Each test constructs a service, invokes an RPC method using a namespaced context, and asserts either gRPC status codes or captured stub state. The status tests verify that nil controller `Extra` becomes a non-nil protobuf `Any` and that non-nil extra fields are copied.

## State And Persistence
Only in-memory stub state is used. No metadata store or real runtime state is persisted.

## Dependencies And Integration Points
Tests use `exchange.NewExchange` for event publishing, `status.FromError` for gRPC code assertions, protobuf sandbox types, and `testify`.

## Risks
The tests do not assert event delivery, stop timeout option propagation, controller error status mapping for every RPC, or initialization behavior with plugin discovery. `Update` nil sandbox behavior is only checked as an error, not a specific gRPC code.

## Test Signals
These tests provide good adapter-level confidence that protobuf inputs are converted and delegated correctly, especially for create options, status fields, and update field lists.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/sandbox/controller_service_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/sandbox/store_local.go -->
# sources/cloud-native/containerd/plugins/services/sandbox/store_local.go

## Purpose
`store_local.go` registers the local sandbox metadata store plugin.

## Important APIs, Types, And Functions
The plugin type is `plugins.SandboxStorePlugin`, ID `local`, and it requires the metadata plugin. Initialization returns `metadata.NewSandboxStore(m.(*metadata.DB))`.

## Control Flow
Plugin initialization resolves the single metadata DB and constructs a store wrapper around it.

## State And Persistence
Sandbox records persist in the shared metadata database through `metadata.NewSandboxStore`.

## Dependencies And Integration Points
The file connects the plugin registry, metadata DB, and sandbox store plugin type. It is consumed by `store_service.go`.

## Risks
The implementation assumes the metadata plugin instance is `*metadata.DB`. All validation and concurrency behavior is delegated to the metadata store.

## Test Signals
No direct tests are present. Sandbox store service and metadata store tests elsewhere are the likely coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/sandbox/store_local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/sandbox/store_service.go -->
# sources/cloud-native/containerd/plugins/services/sandbox/store_service.go

## Purpose
This file exposes the sandbox store over gRPC, adapting protobuf requests to the core `sandbox.Store` interface.

## Important APIs, Types, And Functions
The gRPC plugin ID is `sandboxes` and requires `plugins.SandboxStorePlugin`. `sandboxService` embeds `api.UnimplementedStoreServer` and implements `Create`, `Update`, `List`, `Get`, and `Delete`.

## Control Flow
Initialization resolves the local sandbox store. Each RPC logs the request, converts protobuf sandbox values via `sandbox.FromProto` and `sandbox.ToProto`, forwards filters or field paths, and converts errors with `errgrpc`.

## State And Persistence
Durable state lives in the sandbox store backed by metadata. The service does not cache store results.

## Dependencies And Integration Points
It integrates gRPC, protobuf sandbox service types, core sandbox store interfaces, metadata-backed local store, logging, and `errgrpc`.

## Risks
Malformed requests with nil sandbox payloads rely on `sandbox.FromProto` behavior. The service logs whole requests at debug level, which can include user-provided labels or annotations.

## Test Signals
No direct tests are in this subset. Store behavior is likely covered through metadata store tests and higher-level sandbox API tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/sandbox/store_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/services.go -->
# sources/cloud-native/containerd/plugins/services/services.go

## Purpose
`services.go` centralizes string IDs for containerd service plugins.

## Important APIs, Types, And Functions
Constants include `ContentService`, `SnapshotsService`, `SandboxControllersService`, `ImagesService`, `ContainersService`, `TasksService`, `NamespacesService`, `DiffService`, `IntrospectionService`, and `StreamingService`.

## Control Flow
There is no runtime control flow. The file is a shared identifier contract.

## State And Persistence
No state is stored. These constants affect plugin lookup names and therefore daemon wiring.

## Dependencies And Integration Points
Many service and gRPC plugin packages call `ic.GetByID(plugins.ServicePlugin, services.<Name>)` with these constants.

## Risks
Changing a constant silently breaks plugin lookup compatibility. The `SandboxControllersService` comment says snapshots service, which is misleading documentation.

## Test Signals
Build and plugin initialization tests are the primary signal; there are no direct unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/services.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/snapshots/service.go -->
# sources/cloud-native/containerd/plugins/services/snapshots/service.go

## Purpose
This file implements the gRPC snapshots service, multiplexing requests to named snapshotter instances.

## Important APIs, Types, And Functions
The gRPC plugin ID is `snapshots`. `service` stores `map[string]snapshots.Snapshotter` and implements `Prepare`, `View`, `Mounts`, `Commit`, `Remove`, `Stat`, `Update`, streaming `List`, `Usage`, and `Cleanup`. `getSnapshotter` validates snapshotter names.

## Control Flow
Initialization obtains the map from the `services.SnapshotsService` plugin. Each RPC looks up the requested snapshotter, converts labels and mount/info/usage protobufs through `mount` and `proxy` helpers, calls the core snapshotter, and converts errors with `errgrpc`. `List` batches walk results into responses of up to 100 infos.

## State And Persistence
The service owns no snapshot state. State persists inside each snapshotter and in metadata stores. `Cleanup` is exposed only when the snapshotter implements `snapshots.Cleaner`.

## Dependencies And Integration Points
It integrates snapshotter core interfaces, snapshotter proxy conversions, gRPC streaming, metadata-provided snapshotter map, and plugin registration.

## Risks
Missing or unloaded snapshotters are returned as invalid argument, not not found. `Commit` can set parent through options when provided, so callers must preserve correct parent semantics. `List` errors are returned directly for some paths, while most unary errors are converted with `errgrpc`.

## Test Signals
No direct tests here. Snapshotter suites for individual backends indirectly exercise service-compatible behavior, but not this gRPC adapter.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/snapshots/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/snapshots/snapshotters.go -->
# sources/cloud-native/containerd/plugins/services/snapshots/snapshotters.go

## Purpose
`snapshotters.go` registers the service plugin that exposes all metadata-managed snapshotters to the gRPC snapshots service.

## Important APIs, Types, And Functions
The service plugin uses ID `services.SnapshotsService`, requires metadata, and returns `m.(*metadata.DB).Snapshotters()`.

## Control Flow
Initialization resolves the metadata DB and returns its snapshotter map.

## State And Persistence
No state is created here. The returned snapshotter map is owned by metadata DB wiring.

## Dependencies And Integration Points
It connects metadata DB plugin initialization to `plugins/services/snapshots/service.go`.

## Risks
The type assertion assumes the metadata plugin is the expected DB implementation. Availability of named snapshotters depends on prior snapshot plugin registration and metadata setup.

## Test Signals
No direct tests are in this subset. Daemon plugin initialization validates it.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/snapshots/snapshotters.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/streaming/service.go -->
# sources/cloud-native/containerd/plugins/services/streaming/service.go

## Purpose
This file implements the bidirectional streaming gRPC service used by containerd transfer and other stream-based APIs.

## Important APIs, Types, And Functions
The plugin ID is `streaming` and requires the streaming manager plugin. `service.Stream` registers a `serviceStream` with the `streaming.StreamManager`. `serviceStream` implements `Send`, `Recv`, and `Close` over `api.Streaming_StreamServer`. `emptyResponse` caches a marshalled empty protobuf response.

## Control Flow
The stream RPC expects the first received message to unmarshal as `api.StreamInit`. It registers the stream ID, sends an empty acknowledgement, then waits for either context cancellation or `serviceStream.Close`. `Send` and `Recv` normalize gRPC errors with `errgrpc.ToNative`.

## State And Persistence
All state is in-memory. A channel signals stream closure. No payload data is persisted by this service.

## Dependencies And Integration Points
It depends on `typeurl` marshalling, core streaming manager interfaces, gRPC stream APIs, and protobuf empty responses. Transfer progress uses this service to deliver progress events.

## Risks
There is no timeout waiting for the initial stream init message. Registering duplicate IDs depends on manager behavior. The double `errgrpc.ToNative` branch for non-EOF errors is harmless but redundant.

## Test Signals
No direct tests are included. Integration with transfer progress streams is the likely coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/streaming/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/tasks/local.go -->
# sources/cloud-native/containerd/plugins/services/tasks/local.go

## Purpose
`local.go` implements the task service plugin that bridges API task requests to runtime v2 tasks, process operations, checkpoints, metrics, block I/O/RDT configuration, and deprecation warnings.

## Important APIs, Types, And Functions
The service plugin ID is `services.TasksService`. `Config` carries BlockIO and RDT config paths. `local` stores container metadata, content store, event publisher, task monitor, platform runtime, and warning service. Major methods implement the `api.TasksClient`: `Create`, `Start`, `Delete`, `DeleteProcess`, `Get`, `List`, `Pause`, `Resume`, `Kill`, `ListPids`, `Exec`, `ResizePty`, `CloseIO`, `Checkpoint`, `Update`, `Metrics`, and `Wait`. Helpers include `getProcessState`, `addTasks`, `getTasksMetrics`, `writeContent`, `getContainer`, `getTask`, `getTaskFromContainer`, `getCheckpointPath`, and `formatOptions`.

## Control Flow
Initialization resolves runtime v2, metadata, events, task monitor, and warning plugins, then monitors existing runtime tasks. `Create` loads the container, formats runtime options, handles checkpoint path/image restoration, builds `runtime.CreateOpts`, checks for existing tasks, creates the runtime task, starts monitoring it, and returns the PID. Process operations select either the init process or an exec process. Checkpointing writes checkpoint tar data and config into the content store when no direct image path is supplied. Metrics lists runtime tasks, filters them, and collects stats.

## State And Persistence
Container metadata is read from the metadata DB. Runtime task state is owned by the runtime plugin. Checkpoint artifacts may be extracted to temp runtime dirs and committed to the content store. Monitor registrations are in-memory but tied to task lifecycle. BlockIO/RDT global package config is set at startup.

## Dependencies And Integration Points
This service integrates metadata container store, content store, runtime v2, monitor, archive/content helpers, OCI descriptors, typeurl options, timeout configuration, deprecation warnings, filters, blockio, RDT, and protobuf conversion.

## Risks
Several operations commit side effects before later errors, such as runtime create before PID retrieval or checkpoint archive writes before descriptor response. Temp checkpoint directories created during `Create` from checkpoint image are not removed in this file. Typeurl option mismatches return errors tied to the runtime name. `getProcessState` uses a 2 second timeout and silently maps unknown statuses to `UNKNOWN` after logging.

## Test Signals
No task service tests are in this subset. Runtime integration tests, checkpoint tests, and deprecation-warning checks elsewhere are needed for coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/tasks/local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/tasks/service.go -->
# sources/cloud-native/containerd/plugins/services/tasks/service.go

## Purpose
`service.go` exposes the local task service over gRPC.

## Important APIs, Types, And Functions
The gRPC plugin ID is `tasks`. `service` stores an `api.TasksClient`, embeds `api.UnimplementedTasksServer`, registers with `api.RegisterTasksServer`, and forwards all task RPCs to `local`.

## Control Flow
Initialization resolves `services.TasksService`. Every RPC is a direct pass-through, preserving the local service's error handling and response shape.

## State And Persistence
This wrapper stores only a local client reference. Runtime, metadata, content, and checkpoint state are handled by `local.go`.

## Dependencies And Integration Points
It connects the service plugin to the gRPC task API and plugin registry.

## Risks
No additional validation is performed at the gRPC layer. The type assertion depends on the service plugin implementing `api.TasksClient`.

## Test Signals
No direct tests are present. RPC registration and task integration tests are the likely signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/tasks/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/transfer/service.go -->
# sources/cloud-native/containerd/plugins/services/transfer/service.go

## Purpose
This file implements the gRPC transfer service. It resolves typed source and destination payloads, attaches optional progress streaming, and delegates to registered transfer plugins.

## Important APIs, Types, And Functions
The plugin ID is `transfer` and requires transfer and streaming plugins. `service` stores a slice of `transfer.Transferrer` and a `streaming.StreamManager`. Main functions are `newService`, `Register`, `Transfer`, and `convertAny`. `streamUnmarshaler` lets payload types resolve embedded streams through the stream manager.

## Control Flow
Initialization gathers all transfer plugins and the streaming manager. `Transfer` builds options, including a progress callback that marshals `transferTypes.Progress` and sends it on the named stream. Source and destination are resolved using `tplugins.ResolveType` or plain `typeurl.UnmarshalAny`. The service tries each transferrer until one succeeds, skips `ErrNotImplemented`, and returns unimplemented if none accept the pair.

## State And Persistence
No durable state is owned here. Data movement and persistence are handled by transferrer implementations and stream payloads.

## Dependencies And Integration Points
It integrates transfer plugins, streaming manager, typeurl, OCI descriptor protobuf conversion, log warnings, and gRPC status conversion.

## Risks
Transfer plugin ordering is unspecified. Progress send failures are logged but do not fail the transfer. A progress stream is closed by defer after `Transfer`, so transferrers must not retain the callback asynchronously beyond the call.

## Test Signals
No direct tests are included. End-to-end image/content transfer tests are needed to validate plugin selection and progress behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/transfer/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/version/service.go -->
# sources/cloud-native/containerd/plugins/services/version/service.go

## Purpose
`version/service.go` registers the gRPC version service.

## Important APIs, Types, And Functions
The plugin ID is `version`. `service` implements `api.VersionServer`; `Version` returns `ctrdversion.Version` and `ctrdversion.Revision`.

## Control Flow
Plugin initialization returns an empty service. `Register` installs the server on a gRPC server. The `Version` RPC ignores the empty request and reads package-level version variables.

## State And Persistence
No mutable state or persistence exists. Values are build-time/version package state.

## Dependencies And Integration Points
It integrates the version API, plugin registry, gRPC, and `containerd/v2/version`.

## Risks
If version variables are not populated at build time, the service returns those defaults. No validation is performed.

## Test Signals
No direct tests are in this subset. Basic daemon API tests normally cover this endpoint.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/version/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/warning/service.go -->
# sources/cloud-native/containerd/plugins/services/warning/service.go

## Purpose
This file implements the warning service used to collect last-seen deprecation warnings.

## Important APIs, Types, And Functions
`Service` exposes `Emit` and `Warnings`. The plugin type is `plugins.WarningPlugin`, ID `plugins.DeprecationsPlugin`. `Warning` includes ID, last occurrence time, and message. The private `service` stores a map from `deprecation.Warning` to `time.Time` guarded by an RW mutex.

## Control Flow
`Emit` validates warning IDs, logs invalid IDs, and records `time.Now()` for valid warnings. `Warnings` snapshots the map into a slice and resolves messages through the deprecation package, skipping unknown messages.

## State And Persistence
Warnings are in-memory only and reset on daemon restart. Only the most recent occurrence per warning ID is stored.

## Dependencies And Integration Points
The task service emits deprecated runc option warnings through this service. It depends on `pkg/deprecation`, logging, plugin registration, and synchronization primitives.

## Risks
There is no persistence, count, or ordering guarantee in the returned slice. Time uses wall clock, so clock jumps affect last occurrence values.

## Test Signals
No direct tests are in this subset. Task creation paths that consume deprecated options provide indirect coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/services/warning/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/blockfile/blockfile.go -->
# sources/cloud-native/containerd/plugins/snapshots/blockfile/blockfile.go

## Purpose
`blockfile.go` implements a snapshotter that represents each snapshot as a mountable filesystem image file, usually loop-mounted ext4.

## Important APIs, Types, And Functions
`SnapshotterConfig` controls scratch generation, filesystem type, mount options, scratch recreation, and a test-only view hook. Options include `WithScratchFile`, `WithFSType`, `WithMountOptions`, and `WithRecreateScratch`. The `snapshotter` implements snapshotter methods `Stat`, `Update`, `Usage`, `Prepare`, `View`, `Mounts`, `Commit`, `Remove`, `Walk`, `Close`, plus helpers `createSnapshot`, `getBlockFile`, `mounts`, and `copyFileWithSync`.

## Control Flow
`NewSnapshotter` creates the root, ensures a scratch image exists or is generated, sets defaults, creates a metadata store and snapshots directory, and returns the snapshotter. Active snapshots copy either the parent block file or scratch file into a new snapshot file. View snapshots with parents mount the parent block file read-only. Commit records file size usage. Remove deletes metadata transactionally and renames the block file to `rm-<id>` before final removal.

## State And Persistence
Snapshot metadata persists in `metadata.db`. Block files persist under `<root>/snapshots/<id>`, with a root-level `scratch` template. Usage is approximated by file sizes and parent subtraction.

## Dependencies And Integration Points
It depends on containerd snapshot storage metadata, mount specs, continuity file copy helpers, platform runtime checks, and plugin errors for skip behavior.

## Risks
Usage underreports or overreports when sparse files or shared extents are involved. `mounts` appends to `o.options` without copying, which can accidentally accumulate `ro` or `rw` across calls if the backing slice is reused. Scratch generation is mandatory for first startup unless an existing scratch is present. Remove rollback logs but cannot fully recover from failed renames.

## Test Signals
`blockfile_test.go` runs the generic snapshotter suite. Platform setup tests create ext4 loopback scratch images where supported and skip elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/blockfile/blockfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/blockfile/blockfile_loopsetup_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/blockfile/blockfile_loopsetup_test.go

## Purpose
This Linux/non-Darwin test helper creates a usable ext4 scratch image and mount options for blockfile snapshotter tests.

## Important APIs, Types, And Functions
`setupSnapshotter` locates `mkfs.ext4`, creates a scratch file, formats it, verifies it can mount, and returns blockfile options. `testMount` mounts the scratch file and removes `lost+found`. `testViewHook` mounts a backing file read-write to force filesystem recovery before read-only view use.

## Control Flow
The setup helper creates an 8 MB or 16 MB image depending on page size, syncs it, runs `mkfs.ext4`, verifies loop mount behavior, and returns options including direct I/O, sync, no scratch recreation, and view hook.

## State And Persistence
All files are under test temporary directories. Loopback mounts are transient and unmounted within helpers.

## Dependencies And Integration Points
It depends on `mkfs.ext4`, root/mount capability through the tests, containerd mount helpers, and blockfile options.

## Risks
Tests are environment-sensitive: missing `mkfs.ext4`, insufficient privileges, page size, and mount behavior can skip or fail. The view hook intentionally mutates/replays filesystem state to avoid ext4 read-only recovery issues.

## Test Signals
This file enables `TestBlockfile` to run the generic snapshotter suite on supported Linux environments.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/blockfile/blockfile_loopsetup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/blockfile/blockfile_other_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/blockfile/blockfile_other_test.go

## Purpose
This platform-specific test helper skips blockfile snapshotter tests on Windows and Darwin.

## Important APIs, Types, And Functions
`setupSnapshotter` calls `t.Skip("No support for loopback mounts")` and returns nil values.

## Control Flow
The function is selected by `windows || darwin` build tags and prevents tests from attempting unsupported loopback mounts.

## State And Persistence
No state is created.

## Dependencies And Integration Points
It pairs with the Linux loop setup helper and feeds `blockfile_test.go`.

## Risks
Platform coverage for blockfile behavior is intentionally absent on these systems.

## Test Signals
The test signal is a clean skip rather than failure on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/blockfile/blockfile_other_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/blockfile/blockfile_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/blockfile/blockfile_test.go

## Purpose
This file runs containerd's generic snapshotter conformance suite against the blockfile snapshotter.

## Important APIs, Types, And Functions
`newSnapshotter` obtains platform-specific setup options and returns a factory compatible with `testsuite.SnapshotterSuite`. `TestBlockfile` requires root and invokes the suite with name `Blockfile`.

## Control Flow
Test setup builds a snapshotter with `NewSnapshotter(root, opts...)` and returns a closer that calls `Close`.

## State And Persistence
Test state is created below temporary roots and cleaned by the suite/closer where possible.

## Dependencies And Integration Points
It depends on the generic snapshotter testsuite, testutil root gating, and platform-specific `setupSnapshotter`.

## Risks
The generic suite does not specifically assert blockfile sparse-file usage accounting, scratch recreation, or mount option slice mutation.

## Test Signals
Passing the suite validates core snapshotter lifecycle behavior: prepare, view, commit, remove, stat, walk, mounts, and usage expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/blockfile/blockfile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/blockfile/plugin/plugin.go -->
# sources/cloud-native/containerd/plugins/snapshots/blockfile/plugin/plugin.go

## Purpose
This file registers the blockfile snapshotter plugin.

## Important APIs, Types, And Functions
`Config` exposes `root_path`, `scratch_file`, `fs_type`, `mount_options`, and `recreate_scratch`. The snapshot plugin type is `plugins.SnapshotPlugin`, ID `blockfile`. Initialization sets default platform metadata, builds blockfile options, exports `plugins.SnapshotterRootDir`, and calls `blockfile.NewSnapshotter`.

## Control Flow
The plugin chooses the configured root path or plugin root property, translates non-empty config fields to options, always appends `WithRecreateScratch`, and returns the snapshotter.

## State And Persistence
The configured root contains blockfile metadata and snapshot images. The plugin itself only exports root metadata.

## Dependencies And Integration Points
It integrates blockfile snapshotter construction with containerd plugin registration and platform metadata.

## Risks
Without a scratch file or preexisting scratch image, the underlying snapshotter skips plugin initialization. Configuration type mismatches fail startup. No platform guard is present here, so support depends on runtime mount behavior.

## Test Signals
No direct plugin test is included. Blockfile snapshotter suite validates the implementation, while daemon plugin tests would validate config wiring.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/blockfile/plugin/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/btrfs/btrfs.go -->
# sources/cloud-native/containerd/plugins/snapshots/btrfs/btrfs.go

## Purpose
`btrfs.go` implements a Linux/cgo btrfs snapshotter using btrfs subvolumes and readonly snapshots.

## Important APIs, Types, And Functions
`NewSnapshotter` validates that root is on btrfs, creates `active`, `view`, and `snapshots` directories, and opens a `storage.MetaStore`. `snapshotter` implements `Stat`, `Update`, `Usage`, `Walk`, `Prepare`, `View`, `Commit`, `Mounts`, `Remove`, and `Close`. Helpers include `usage`, `makeSnapshot`, and `mounts`.

## Control Flow
Prepare/View create metadata and then create a btrfs subvolume or subvolume snapshot. Mounts use the root device plus a `subvolid=<id>` option from `btrfs.SubvolID`. Commit computes usage, commits metadata, creates a readonly snapshot under `snapshots`, and deletes the active subvolume. Remove creates a temporary `rm-<id>` snapshot, deletes the source, and restores from it if metadata transaction commit fails.

## State And Persistence
Metadata persists in `metadata.db`. Filesystem state persists as btrfs subvolumes under `active`, `view`, and `snapshots`. Usage for active snapshots is computed from filesystem disk usage or diff usage against the parent.

## Dependencies And Integration Points
It depends on `github.com/containerd/btrfs/v2`, containerd mount lookup, snapshot storage metadata, continuity filesystem usage helpers, and plugin skip errors.

## Risks
The root must be a mounted btrfs filesystem. Removal and commit use multiple filesystem operations around metadata transactions, so rollback paths are important but not perfect. Usage can be expensive for active snapshots. Build tags limit availability to Linux with cgo and without `no_btrfs`.

## Test Signals
`btrfs_test.go` runs the generic snapshotter suite on a loopback btrfs filesystem and includes a mount-specific content inheritance test.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/btrfs/btrfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/btrfs/btrfs_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/btrfs/btrfs_test.go

## Purpose
This file provides root-gated integration tests for the btrfs snapshotter.

## Important APIs, Types, And Functions
`boltSnapshotter` creates a loopback device, formats it with `mkfs.btrfs`, mounts it, and returns a snapshotter factory. `TestBtrfs` runs `testsuite.SnapshotterSuite`. `TestBtrfsMounts` verifies generated btrfs mounts and basic parent/child content behavior.

## Control Flow
Tests skip when `mkfs.btrfs` or the btrfs kernel module is unavailable. The factory retries snapshotter initialization after remounting if btrfs mount detection races. Cleanup closes the snapshotter, unmounts, and closes the loopback device.

## State And Persistence
All state lives on temporary loopback files and temporary mount roots. Subvolumes are created and removed during test lifecycle.

## Dependencies And Integration Points
The tests depend on root privileges, btrfs kernel support, mkfs tooling, loopback helpers, containerd mount helpers, and snapshotter testsuite.

## Risks
Environment sensitivity is high. The tests do not exercise all rollback paths or quota/usage edge cases, but they do catch core mount and content inheritance behavior.

## Test Signals
Passing tests indicate the snapshotter conforms to generic lifecycle expectations and returns usable `subvolid` mount specs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/btrfs/btrfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/btrfs/plugin/plugin.go -->
# sources/cloud-native/containerd/plugins/snapshots/btrfs/plugin/plugin.go

## Purpose
This file registers the btrfs snapshotter plugin for Linux/cgo builds.

## Important APIs, Types, And Functions
`Config` exposes `root_path`. The plugin type is `plugins.SnapshotPlugin`, ID `btrfs`, and initialization sets `ic.Meta.Platforms`, chooses the root path, exports `plugins.SnapshotterRootDir`, and calls `btrfs.NewSnapshotter`.

## Control Flow
The plugin uses the configured root when present, otherwise the plugin root property. Invalid config type returns an error.

## State And Persistence
Persistent state is created by `btrfs.NewSnapshotter` under the selected root.

## Dependencies And Integration Points
It integrates plugin registry, platform metadata, and the btrfs snapshotter implementation.

## Risks
Initialization skips or fails if the root is not on btrfs or system support is missing. Build tags exclude non-Linux, no-cgo, or `no_btrfs` builds.

## Test Signals
No direct plugin tests are included. Snapshotter integration tests validate the implementation behind the plugin.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/btrfs/plugin/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/blkdiscard/blkdiscard.go -->
# sources/cloud-native/containerd/plugins/snapshots/devmapper/blkdiscard/blkdiscard.go

## Purpose
This file wraps the Linux `blkdiscard` command for devmapper snapshot cleanup.

## Important APIs, Types, And Functions
`Version` runs `blkdiscard --version`, `CheckBinary` verifies the binary is on PATH, `BlkDiscard` discards all blocks for a device path, and private `blkdiscard` executes the command.

## Control Flow
All command wrappers use `exec.Command(...).CombinedOutput()` and return command output or error.

## State And Persistence
The wrapper can irreversibly discard blocks on the specified block device. It does not track state itself.

## Dependencies And Integration Points
`pool_device.go` uses this indirectly through `dmsetup.DiscardBlocks` when discard behavior is enabled.

## Risks
Callers must verify the device is correct and not in use. Errors are command errors without structured stderr wrapping in this package.

## Test Signals
No direct tests for this wrapper are included. `dmsetup_test.go` indirectly exercises discard behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/blkdiscard/blkdiscard.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/config.go -->
# sources/cloud-native/containerd/plugins/snapshots/devmapper/config.go

## Purpose
`config.go` defines and validates devmapper snapshotter configuration.

## Important APIs, Types, And Functions
`Config` includes root path, pool name, base image size string and parsed bytes, async remove, discard blocks, filesystem type, and filesystem options. `LoadConfig` reads TOML, `parse` converts base image size and defaults filesystem type, and `Validate` checks required fields and supported filesystems.

## Control Flow
`LoadConfig` opens the path, decodes TOML, parses sizes/defaults, validates, and returns the config. Validation accumulates multiple errors through `errors.Join`.

## State And Persistence
No state is persisted by this file. Parsed config drives root paths, thin pool names, filesystem creation, and cleanup policy.

## Dependencies And Integration Points
It depends on `go-toml/v2`, Docker units parsing, and filesystem type constants from `snapshotter.go`.

## Risks
`parse` requires `BaseImageSize` to parse before `Validate`, so missing base size can surface as a parse error in some call paths. Unsupported filesystem strings fail validation.

## Test Signals
`config_test.go` covers TOML loading, invalid paths, invalid size parsing, required field errors, and a valid minimal config.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/config_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/devmapper/config_test.go

## Purpose
This test file validates devmapper configuration loading, parsing, and field validation.

## Important APIs, Types, And Functions
Tests include `TestLoadConfig`, `TestLoadConfigInvalidPath`, `TestParseInvalidData`, `TestFieldValidation`, and `TestExistingPoolFieldValidation`.

## Control Flow
The loading test writes TOML to a temp file, loads it, and checks parsed values including byte conversion. Validation tests assert missing fields produce four joined errors and that a complete ext4 config succeeds.

## State And Persistence
Only temporary config files are created.

## Dependencies And Integration Points
The tests use `go-toml/v2` encoding and `testify/assert`.

## Risks
The tests do not cover xfs/ext2 validation, async/remove flags, discard flag, or custom filesystem options.

## Test Signals
They give focused confidence in config parsing and required-field error aggregation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/device_info.go -->
# sources/cloud-native/containerd/plugins/snapshots/devmapper/device_info.go

## Purpose
This file defines devmapper thin-device state and metadata records.

## Important APIs, Types, And Functions
`maxDeviceID` defines the 24-bit device ID limit. `DeviceState` enumerates lifecycle states from `Unknown` through create/activate/suspend/resume/deactivate/remove states plus `Faulty`. `DeviceState.String` renders names. `DeviceInfo` stores device ID, size, name, parent name, state, and error text.

## Control Flow
Only `String` has control flow, mapping known states to labels and unknown values to `unknown <n>`.

## State And Persistence
`DeviceInfo` is JSON-marshaled into the devmapper pool metadata Bolt database. State transitions mirror dmsetup operations and recovery status.

## Dependencies And Integration Points
It is used by `metadata.go`, `pool_device.go`, and devmapper tests.

## Risks
State names are part of diagnostics and persisted JSON values. Adding states requires recovery logic in `ensureDeviceStates`.

## Test Signals
Metadata and pool-device tests exercise several states, especially `Faulty`, `Activated`, `Removed`, and ID reuse.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/device_info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/dmsetup/dmsetup.go -->
# sources/cloud-native/containerd/plugins/snapshots/devmapper/dmsetup/dmsetup.go

## Purpose
`dmsetup.go` wraps Linux `dmsetup` and related device-mapper command behavior for the devmapper snapshotter.

## Important APIs, Types, And Functions
Constants include `/dev/mapper/` and 512-byte sector size. Major APIs are `CreatePool`, `ReloadPool`, `CreateDevice`, `ActivateDevice`, `SuspendDevice`, `ResumeDevice`, `Table`, `CreateSnapshot`, `DeleteDevice`, `RemoveDevice`, `Info`, `Version`, `Status`, `GetFullDevicePath`, `BlockDeviceSize`, and `DiscardBlocks`. It defines `DeviceInfo`, `DeviceStatus`, remove options, and `ErrInUse`.

## Control Flow
Pool and thin-device functions build dmsetup table strings or messages, then execute `dmsetup`. `Info` parses column output and attribute flags. `Status` parses target status fields. Command errors are normalized by extracting Linux errno text from dmsetup output when possible. `DiscardBlocks` checks open count before invoking blkdiscard.

## State And Persistence
Commands mutate kernel device-mapper state and thin-pool metadata. This file stores no durable state itself.

## Dependencies And Integration Points
It depends on `os/exec`, `unix.Errno`, blkdiscard wrapper, and filesystem/block-device APIs. `pool_device.go` uses it for all actual device operations.

## Risks
Parsing command output is fragile across dmsetup versions/locales. `BlockDeviceSize` uses seek and assumes the path supports it. Errno extraction is best-effort string matching. Calling wrappers with wrong names can remove or mutate real devices.

## Test Signals
`dmsetup_test.go` performs root-gated integration coverage for pool creation, reload, thin devices, snapshots, status parsing, suspend/resume, discard, removal, and version.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/dmsetup/dmsetup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/dmsetup/dmsetup_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/devmapper/dmsetup/dmsetup_test.go

## Purpose
This file integration-tests the dmsetup wrapper against real loopback-backed device-mapper devices.

## Important APIs, Types, And Functions
`TestDMSetup` creates data and metadata loop devices, then runs subtests for pool creation, pool reload, thin device creation, snapshot creation/deletion, activation, status, suspend/resume, discard, remove, and version. Helper `createLoopbackDevice` allocates loop devices.

## Control Flow
The test creates a thin pool, executes operations in order, asserts expected errno values for duplicate or invalid operations, and removes pool/devices at the end. Loop devices are detached in defers.

## State And Persistence
Temporary files are attached as loop devices, then used as devmapper data/metadata devices. Kernel device-mapper state is created and removed during the test.

## Dependencies And Integration Points
It requires root, `dmsetup`, blkdiscard behavior, loop devices, containerd mount helpers, docker units, and `testify`.

## Risks
Tests are highly environment-dependent and can leave devices behind if cleanup fails. They do not test all dmsetup output variants.

## Test Signals
Passing tests strongly validate command construction and parsing against the local kernel/tools combination.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/dmsetup/dmsetup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/metadata.go -->
# sources/cloud-native/containerd/plugins/snapshots/devmapper/metadata.go

## Purpose
`metadata.go` manages the devmapper pool metadata database, including thin device records and device ID allocation.

## Important APIs, Types, And Functions
`PoolMetadata` wraps a Bolt DB. Public methods include `NewPoolMetadata`, `AddDevice`, `ChangeDeviceState`, `MarkFaulty`, `UpdateDevice`, `GetDevice`, `RemoveDevice`, `WalkDevices`, `GetDeviceNames`, and `Close`. Helpers include `getNextDeviceID`, `markDeviceID`, `putObject`, and `getObject`.

## Control Flow
Initialization creates `devices` and `device_ids` buckets. `AddDevice` rejects non-faulty duplicate names, allocates the next free or new device ID, and stores JSON `DeviceInfo`. `UpdateDevice` loads a record, runs a callback, ensures name and device ID did not change, then stores it. `RemoveDevice` deletes the record and marks the ID free. `MarkFaulty` marks both the device record and ID as faulty.

## State And Persistence
State persists in Bolt buckets: `devices` maps device names to JSON `DeviceInfo`, while `device_ids` maps numeric ID keys to free/taken/faulty state bytes. Faulty IDs are intentionally not reused automatically.

## Dependencies And Integration Points
It integrates Bolt transactions, `errdefs` not-found/already-exists errors, and `DeviceInfo` state transitions used by `PoolDevice`.

## Risks
Device ID keys are string-sorted, which is acceptable for scanning free entries but not numeric ordering after multi-digit IDs. Faulty records allow same-name recreation only by overwriting a faulty device, preserving faulty ID tracking. Context parameters are currently unused by Bolt operations.

## Test Signals
`metadata_test.go` covers add, rollback, duplicate rejection, ID reuse, removal, update, faulty marking, walking, and name listing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/metadata_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/devmapper/metadata_test.go

## Purpose
This file unit-tests the devmapper pool metadata store.

## Important APIs, Types, And Functions
Tests cover `AddDevice`, rollback on invalid metadata, duplicates, device ID reuse, removal, update callbacks, `MarkFaulty`, `WalkDevices`, and `GetDeviceNames`. Helpers create and close a temp Bolt store.

## Control Flow
Each test creates an isolated metadata DB, performs metadata operations, and checks persisted `DeviceInfo` values or expected errors.

## State And Persistence
Temporary Bolt databases are created under test temp dirs and closed after use.

## Dependencies And Integration Points
Tests use Bolt directly for checking faulty ID state and `testify/assert`.

## Risks
Walk order follows Bolt key order and tests assert specific order for simple names. The tests do not simulate max device ID exhaustion or JSON corruption.

## Test Signals
They provide solid coverage for local persistence invariants and state/ID bookkeeping.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/metadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/plugin/plugin.go -->
# sources/cloud-native/containerd/plugins/snapshots/devmapper/plugin/plugin.go

## Purpose
This file registers the devmapper snapshotter plugin.

## Important APIs, Types, And Functions
The snapshot plugin ID is `devmapper` and config type is `*devmapper.Config`. Initialization sets default platform metadata, validates config type, skips when `PoolName` is empty, defaults `RootPath`, exports `plugins.SnapshotterRootDir`, and calls `devmapper.NewSnapshotter`.

## Control Flow
The plugin does minimal config normalization before delegating validation and pool setup to the snapshotter.

## State And Persistence
Persistent state is created under `RootPath` and in the configured thin pool by the snapshotter.

## Dependencies And Integration Points
It integrates containerd plugin registration, platform metadata, and the devmapper snapshotter package.

## Risks
An empty pool name causes a skip, so devmapper must be explicitly configured. Config type mismatch fails initialization. Root path defaults to plugin property if absent.

## Test Signals
No direct plugin tests are included. Devmapper snapshotter tests validate the underlying implementation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/plugin/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/pool_device.go -->
# sources/cloud-native/containerd/plugins/snapshots/devmapper/pool_device.go

## Purpose
`pool_device.go` coordinates devmapper thin-pool operations with persistent pool metadata and recovery state transitions.

## Important APIs, Types, And Functions
`PoolDevice` stores pool name, `PoolMetadata`, and discard policy. Major APIs are `NewPoolDevice`, `CreateThinDevice`, `CreateSnapshotDevice`, `SuspendDevice`, `ResumeDevice`, `DeactivateDevice`, `IsActivated`, `IsLoaded`, `GetUsage`, `RemoveDevice`, `RemovePool`, `MarkDeviceState`, `WalkDevices`, and `Close`. Internal helpers include `ensureDeviceStates`, `transition`, `rollbackActivate`, `createDevice`, `activateDevice`, `createSnapshot`, `deleteDevice`, and retry helpers.

## Control Flow
Initialization checks dmsetup, optional blkdiscard, opens metadata, verifies pool presence, and reconciles persisted device states. Creation saves metadata, sends dmsetup create/snapshot messages, activates devices, and rolls back or marks faulty on failures. Snapshot creation suspends active parent devices before taking internal snapshots and resumes afterward. Deactivation can discard blocks and remove devices with retry/deferred/force options.

## State And Persistence
Device lifecycle state persists in the pool metadata DB. Kernel device-mapper state is mutated through dmsetup. Faulty states preserve device IDs for manual repair. Removed devices may remain until cleanup when deferred or async behavior is used.

## Dependencies And Integration Points
It depends on `dmsetup`, `blkdiscard`, Bolt-backed pool metadata, logging, `unix` errno, and snapshotter cleanup policy.

## Risks
Recovery is complex: incomplete states after crashes are marked faulty except selected safe states. Suspend/resume retries use string matching on error text. Device removal with discard must avoid busy devices. Rollback failures can leave faulty devices requiring manual intervention.

## Test Signals
`pool_device_test.go` covers real thin device creation, filesystem formatting, snapshot isolation, deactivation/removal, rollback activation, and faulty-state marking.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/pool_device.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/pool_device_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/devmapper/pool_device_test.go

## Purpose
This file integration-tests devmapper pool device orchestration on loopback-backed thin pools.

## Important APIs, Types, And Functions
`TestPoolDevice` creates a thin pool, constructs `PoolDevice`, creates thin devices, formats ext4, writes data, creates a snapshot, verifies snapshot isolation, deactivates/removes devices, and tests rollback activation. `TestPoolDeviceMarkFaulty` checks state reconciliation. Helpers create loop devices, mkfs ext4, and mount devices.

## Control Flow
The main test executes an ordered scenario because later operations depend on earlier devices. It uses `mount.WithTempMount` to write/read data. Cleanup removes the pool and detaches loop devices.

## State And Persistence
Tests create real kernel device-mapper devices and temporary metadata databases under temp dirs.

## Dependencies And Integration Points
They require root, dmsetup, mkfs.ext4, loop devices, mount helpers, docker units, and logging configuration.

## Risks
Environment failures can leave kernel devices if cleanup fails. Coverage is realistic but expensive and not suitable for unprivileged CI.

## Test Signals
Passing tests validate pool creation, device ID metadata, snapshot correctness, usage reporting after mkfs, deactivation, removal, and recovery marking.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/pool_device_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/snapshotter.go -->
# sources/cloud-native/containerd/plugins/snapshots/devmapper/snapshotter.go

## Purpose
`snapshotter.go` implements the containerd snapshotter interface using Linux device-mapper thin devices.

## Important APIs, Types, And Functions
`Snapshotter` stores a `storage.MetaStore`, `PoolDevice`, config, cleanup functions, and `sync.Once`. It implements `NewSnapshotter`, `Stat`, `Update`, `Usage`, `Mounts`, `Prepare`, `View`, `Commit`, `Remove`, `Walk`, `ResetPool`, `Close`, `Cleanup`, and helpers `createSnapshot`, `removeDevice`, `mkfs`, `getDeviceName`, `getDevicePath`, and `buildMounts`.

## Control Flow
Creation parses and validates config, creates root and metadata store, and opens the pool device. Prepare/View create snapshot metadata, determine filesystem type from config or parent label, create a thin device or snapshot device, format base devices, remove `lost+found`, and return mount specs. Commit calculates device usage, commits metadata, suspends/resumes to flush IO, and deactivates the committed device. Remove deletes snapshot metadata and either removes the device immediately or marks it removed for async cleanup. Cleanup removes devices marked `Removed` when async remove is enabled.

## State And Persistence
Containerd snapshot metadata persists in `metadata.db`. Pool device metadata persists in `<pool>.db`. Thin devices persist in kernel thin-pool state until removed. Filesystem type is stored in snapshot labels under `containerd.io/snapshot/devmapper/fstype`.

## Dependencies And Integration Points
It integrates snapshot storage metadata, `PoolDevice`, dmsetup paths, filesystem mkfs tools, containerd mount helpers, errdefs, logging, and snapshot GC cleanup via `snapshots.Cleaner`.

## Risks
Metadata and kernel state must stay synchronized across failures. `mkfs` failures trigger rollback but depend on `RemoveDevice`. Async remove can leave devices until `Cleanup`. XFS requires `nouuid` mounts. Parent snapshots without fs type labels default to ext4 for compatibility.

## Test Signals
`snapshotter_test.go` runs the generic snapshotter suite, usage tests, mkfs command error tests, and an XFS multiple-mount scenario.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/snapshotter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/snapshotter_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/devmapper/snapshotter_test.go

## Purpose
This file integration-tests the devmapper snapshotter and selected filesystem formatting behavior.

## Important APIs, Types, And Functions
`TestSnapshotterSuite` runs the generic snapshotter suite and a devmapper usage test. `testUsage` checks active base usage and committed child usage after writing a 1 MB file. `TestMkfsExt4`, `TestMkfsExt4NonDefault`, `TestMkfsXfs`, and `TestMkfsXfsNonDefault` validate mkfs error wrapping. `TestMultipleXfsMounts` checks XFS layer creation/mount behavior. `createSnapshotter` creates loopback pool devices and cleanup functions.

## Control Flow
Tests require root, create loopback data and metadata devices, create a thin pool, instantiate the snapshotter, prepend pool cleanup to snapshotter cleanup functions, and run lifecycle operations.

## State And Persistence
Real loopback files, thin pools, thin devices, and metadata DBs are created under temporary roots.

## Dependencies And Integration Points
They rely on root, dmsetup, mkfs.ext4/mkfs.xfs, loop devices, mount helpers, snapshotter testsuite, namespaces, and continuity filesystem test appliers.

## Risks
High environment sensitivity and potential cleanup leakage if kernel/device operations fail. The mkfs tests assert error text for empty paths rather than successful formatting.

## Test Signals
Passing tests validate snapshotter conformance, usage accounting directionally, fs type labels/options, and XFS `nouuid` mount behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/devmapper/snapshotter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/erofs.go -->
# sources/cloud-native/containerd/plugins/snapshots/erofs/erofs.go

## Purpose
`erofs.go` implements an EROFS plus overlayfs snapshotter, with optional fs-verity, immutable layer files, block-mode writable layers, idmapped mount support, merged fsmeta handling, and dm-verity mount policy.

## Important APIs, Types, And Functions
`SnapshotterConfig` controls overlay options, fsverity, immutable flag, default writable size, ID remapping, and dm-verity mode. Options include `WithOvlOptions`, `WithFsverity`, `WithImmutable`, `WithDmverityMode`, `WithDefaultSize`, and `WithRemapIDs`. The `snapshotter` implements `Prepare`, `View`, `Commit`, `Mounts`, `Remove`, `Stat`, `Update`, `Walk`, `Usage`, and `Close`. Important helpers include path builders, `writableSize`, `prepareDirectory`, `mountFsMeta`, `applyDmverityPolicy`, `createErofsMount`, `mounts`, `createSnapshot`, `commitBlock`, `getCleanupDirectories`, and `verifyFsverity`.

## Control Flow
Initialization validates dm-verity mode, checks compatibility when not in block mode, optionally checks fsverity support, opens metadata, and creates a snapshots directory. Prepare/View create a temp snapshot directory, create `fs` and optional `work`, write `.erofslayer` for active snapshots, create metadata, apply ownership remapping, rename into place, and build mounts. Mount construction returns direct EROFS mounts for committed layers, bind mounts for single no-parent directories, or formatted overlay mount chains across parent EROFS layers. Commit converts an upperdir or block writable layer to `layer.erofs` when needed, enables fsverity/immutable flags if configured, and commits metadata with disk usage. Remove clears immutable flags for committed layers, removes metadata, unmounts upper paths, and deletes orphan snapshot directories.

## State And Persistence
Snapshot metadata persists in `metadata.db`. Per-snapshot files live under `<root>/snapshots/<id>/`, including `fs`, `work`, `rwlayer.img`, `layer.erofs`, and optional `fsmeta.erofs` or `.dmverity` metadata. Active usage scans upper directories; committed usage is stored metadata.

## Dependencies And Integration Points
It integrates storage metadata, mount formatter conventions, EROFS conversion utilities, dm-verity metadata helpers, fsverity helpers, user namespace ID maps, continuity disk usage, and snapshot label contracts.

## Risks
Mount option templates such as `{{ mount 0 }}` depend on containerd mount handler support. dm-verity `on` mode rejects old layers without metadata. Block mode changes active writable semantics. Cleanup after metadata removal is best effort. `setImmutable` failures are warnings on commit but errors when clearing during remove except not implemented.

## Test Signals
No EROFS tests are in this requested subset, though related `erofs_linux_test.go` exists outside it. Required coverage should include dm-verity modes, fsverity, block mode, ID mapping, fsmeta merging, and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/erofs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/erofs_linux.go -->
# sources/cloud-native/containerd/plugins/snapshots/erofs/erofs_linux.go

## Purpose
`erofs_linux.go` provides Linux-specific helpers for the EROFS snapshotter.

## Important APIs, Types, And Functions
`defaultWritableSize` is `0` on Linux. `FindErofs` checks `/proc/filesystems`. `checkCompatibility` verifies d_type support and EROFS kernel support. `setImmutable` toggles `FS_IMMUTABLE_FL` with ioctls. `cleanupUpper` unmounts EROFS mounts under an upper path. `convertDirToErofs` calls `erofsutils.ConvertErofs` then removes upperdir children. `getParentOwnership` returns UID/GID from `syscall.Stat_t`.

## Control Flow
Compatibility checking runs during snapshotter creation when not in block mode. Immutable toggling opens the file, reads inode flags, updates the bit if needed, and writes flags back. Conversion cleans up the overlay upperdir after producing an EROFS layer.

## State And Persistence
The file mutates Linux inode flags, removes converted upperdir contents, and unmounts mount points. It does not own metadata.

## Dependencies And Integration Points
It depends on `/proc/filesystems`, continuity d_type checks, Linux ioctls, containerd mount helpers, EROFS conversion utilities, and syscall stat data. `erofs.go` calls these helpers for initialization, commit, remove, and ownership propagation.

## Risks
Kernel/filesystem support is mandatory. Immutable flag manipulation can fail due to permissions or unsupported filesystems. `convertDirToErofs` removes all children under the upperdir after conversion, so conversion correctness is critical before cleanup.

## Test Signals
No tests in this subset directly target these helpers. Linux EROFS snapshotter tests outside the requested list should cover compatibility and conversion behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/erofs_linux.go -->
