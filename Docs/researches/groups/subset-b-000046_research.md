# subset-b-000046 Research

Grouped research for the containerd API event, release, bootstrap, sandbox, and task API files in subset B. Each section is source-tree-aligned and bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/image.pb.go -->
# sources/cloud-native/containerd/api/events/image.pb.go

Purpose: generated Go protobuf bindings for `events/image.proto`, exporting image lifecycle event payloads in package `events`. It represents `ImageCreate`, `ImageUpdate`, and `ImageDelete` as protobuf messages used by containerd event publishers/subscribers.

Important APIs/types/functions: `ImageCreate` and `ImageUpdate` carry `Name` plus `Labels map[string]string`; `ImageDelete` carries only `Name`. Each type implements generated protobuf methods (`Reset`, `String`, `ProtoMessage`, `ProtoReflect`, deprecated `Descriptor`) and nil-safe getters (`GetName`, `GetLabels`). The file-level descriptor `File_events_image_proto`, raw descriptor compression helper, message info table, dependency indexes, and `file_events_image_proto_init` wire the types into `google.golang.org/protobuf`.

Control flow: runtime behavior is limited to protobuf reflection and getters. `ProtoReflect` stores message info when unsafe protobuf support is enabled; `rawDescGZIP` lazily compresses descriptor bytes with `sync.Once`; `init` builds the descriptor once and nils raw metadata after registration.

State/persistence: no durable storage or business state is managed here. State is serialized only when callers marshal event messages; label map entries are encoded as generated map-entry messages.

Dependencies/integration: imports protobuf reflection/runtime packages and blank-imports `github.com/containerd/containerd/api/types` so the fieldpath extension referenced by the proto is linked. Integrates with containerd's event exchange and any code that unmarshals image event topics.

Risks/test signals: this file is generated and should be regenerated from `image.proto` rather than edited. Compatibility risk is field-number drift, especially `labels = 2`; consumer risk is assuming `GetLabels` returns a non-nil map. No direct tests in this subset; confidence comes from protobuf generation and downstream event serialization tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/image.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/image.proto -->
# sources/cloud-native/containerd/api/events/image.proto

Purpose: source protobuf schema for containerd image events. It defines public event payloads for image creation, update, and deletion.

Important APIs/types/functions: package is `containerd.services.images.v1` while the Go package is `github.com/containerd/containerd/api/events;events`. `ImageCreate` and `ImageUpdate` contain `name` and `labels`; `ImageDelete` contains `name`. The file imports `types/fieldpath.proto` and sets `(containerd.types.fieldpath_all) = true` so fieldpath accessors are generated.

Control flow: declarative schema only; flow is event producer populates these messages, the event system serializes them, and consumers decode them by message type/topic.

State/persistence: no local state. The schema defines wire compatibility, so field numbers are persistent API state.

Dependencies/integration: integrates with the images service event stream and generated Go/fieldpath code. The package name differs from the other event protos, tying image events to the images service namespace.

Risks/test signals: wire compatibility depends on not renumbering or changing field types. Label fieldpath lookup joins path segments after `labels`, so dotted label keys are supported by convention. Testing should cover create/update/delete event publication and fieldpath filtering by `name` and labels.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/image.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/image_fieldpath.pb.go -->
# sources/cloud-native/containerd/api/events/image_fieldpath.pb.go

Purpose: generated fieldpath helpers for image event messages. These helpers let event filters query selected protobuf fields as strings.

Important APIs/types/functions: `(*ImageCreate).Field`, `(*ImageUpdate).Field`, and `(*ImageDelete).Field` accept a `[]string` path and return `(value, true)` when the field is present. They support `name`; create/update additionally support `labels.<key>` by joining remaining path components with `"."`.

Control flow: each method rejects empty fieldpaths, switches on the first component, performs simple non-empty checks for string fields, and returns map lookup results for labels. Unknown paths return `("", false)`.

State/persistence: no state is stored. Results are computed from the message instance.

Dependencies/integration: imports `strings` only for label key reconstruction. Integrates with containerd event filtering generated from the `fieldpath_all` option in `image.proto`.

Risks/test signals: label lookup is explicitly special-cased and could break if label semantics change. Empty string values are treated as absent for `name`; map entries with empty values still return `true` if the key exists. Tests should exercise dotted label keys and empty message cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/image_fieldpath.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/namespace.pb.go -->
# sources/cloud-native/containerd/api/events/namespace.pb.go

Purpose: generated Go protobuf bindings for namespace lifecycle events. It exposes create, update, and delete payloads in the shared `events` package.

Important APIs/types/functions: `NamespaceCreate` and `NamespaceUpdate` include `Name` and `Labels`; `NamespaceDelete` includes `Name`. Generated methods include protobuf reflection (`ProtoReflect`), descriptor access, nil-safe getters, raw descriptor compression, and descriptor initialization through `file_events_namespace_proto_init`.

Control flow: like other generated protobuf files, runtime flow is reflective registration and getter access. `init` builds message metadata and exporter functions for non-unsafe builds.

State/persistence: no persistence beyond protobuf wire encoding. Field numbers and map-entry representation form the compatibility contract.

Dependencies/integration: blank-imports containerd API types for the fieldpath extension, and depends on protobuf reflection/runtime packages. Integrated with namespace service event publication and event filters.

Risks/test signals: generated file should track `namespace.proto`; manual edits are fragile. Consumers must distinguish nil labels from empty maps. Tests should validate namespace event marshaling and filtering through fieldpath helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/namespace.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/namespace.proto -->
# sources/cloud-native/containerd/api/events/namespace.proto

Purpose: protobuf schema for namespace lifecycle events in containerd.

Important APIs/types/functions: package `containerd.events`, Go package `api/events;events`. Defines `NamespaceCreate`, `NamespaceUpdate`, and `NamespaceDelete`; create/update include `name` and `labels`, delete includes `name`. Enables fieldpath generation with `(containerd.types.fieldpath_all) = true`.

Control flow: declarative schema used by code generation and event serialization. No executable control flow.

State/persistence: persistent API state is the message names and field numbers. Labels are represented as a string map.

Dependencies/integration: depends on `types/fieldpath.proto`; integrates with namespace metadata mutation paths and event subscription/filtering.

Risks/test signals: renaming or renumbering fields would break wire compatibility and event filters. Tests should confirm create/update include label changes and delete events remain minimal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/namespace.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/namespace_fieldpath.pb.go -->
# sources/cloud-native/containerd/api/events/namespace_fieldpath.pb.go

Purpose: generated fieldpath accessors for namespace events.

Important APIs/types/functions: `Field` methods exist for `NamespaceCreate`, `NamespaceUpdate`, and `NamespaceDelete`. They expose `name` for all messages and `labels.<key>` for create/update by joining remaining path segments.

Control flow: methods guard against empty paths, switch on the first path segment, check non-empty string fields, and perform map lookups.

State/persistence: stateless derived access over message fields.

Dependencies/integration: imports `strings`; produced from `namespace.proto` fieldpath options. Event filter code can use these helpers to match namespaces by name or labels.

Risks/test signals: dotted label keys depend on `strings.Join(fieldpath[1:], ".")`. Empty string names are considered undefined. Tests should cover absent labels, empty label maps, and label keys containing dots.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/namespace_fieldpath.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/sandbox.pb.go -->
# sources/cloud-native/containerd/api/events/sandbox.pb.go

Purpose: generated Go protobuf bindings for sandbox lifecycle event payloads.

Important APIs/types/functions: defines `SandboxCreate`, `SandboxStart`, and `SandboxExit`. Create/start carry `SandboxID`; exit carries `SandboxID`, `ExitStatus`, and `ExitedAt *timestamppb.Timestamp`. Generated getters return zero values for nil receivers.

Control flow: only protobuf reflection/descriptor initialization and field getters. `file_events_sandbox_proto_init` registers three message types and timestamp dependency metadata.

State/persistence: no internal persistence. Wire fields capture sandbox lifecycle facts emitted elsewhere.

Dependencies/integration: depends on protobuf runtime/reflection and `google.protobuf.Timestamp`. Integrates with sandbox runtimes and event consumers tracking sandbox start/exit.

Risks/test signals: fieldpath generation for sandbox events handles only `sandbox_id`, so filters cannot directly match exit status or timestamp. Tests should validate timestamp marshaling and event consumers' handling of zero exit status versus unset fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/sandbox.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/sandbox.proto -->
# sources/cloud-native/containerd/api/events/sandbox.proto

Purpose: source schema for sandbox lifecycle events.

Important APIs/types/functions: package `containerd.events`, Go package `api/events;events`. `SandboxCreate` and `SandboxStart` contain `sandbox_id`; `SandboxExit` adds `exit_status` and `google.protobuf.Timestamp exited_at`.

Control flow: declarative event payload definition. Runtime behavior is outside this file in sandbox/runtime components that publish events.

State/persistence: field numbers define persistent API compatibility. No storage.

Dependencies/integration: imports `google/protobuf/timestamp.proto`. Unlike several peer event protos, it does not import `types/fieldpath.proto` or set `fieldpath_all`, though a generated fieldpath file exists for string fields.

Risks/test signals: timestamp presence and zero exit code need clear consumer interpretation. Tests should cover create/start/exit event publication and backward compatibility for the three fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/sandbox.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/sandbox_fieldpath.pb.go -->
# sources/cloud-native/containerd/api/events/sandbox_fieldpath.pb.go

Purpose: generated fieldpath accessors for sandbox events.

Important APIs/types/functions: `Field` methods for `SandboxCreate`, `SandboxStart`, and `SandboxExit` expose only `sandbox_id`. The `SandboxExit` method comments `exit_status` and `exited_at` as unhandled.

Control flow: empty paths return false; a switch on the first segment returns the sandbox ID if non-empty; unknown or unsupported fields return false.

State/persistence: no state; fieldpath output is computed from the event message.

Dependencies/integration: no external imports. Used by event filtering systems that operate on string field values.

Risks/test signals: callers cannot filter sandbox exits by exit status or timestamp through this helper. This is a deliberate limitation of the generator's supported scalar/string handling and should be documented in filter behavior tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/sandbox_fieldpath.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/snapshot.pb.go -->
# sources/cloud-native/containerd/api/events/snapshot.pb.go

Purpose: generated Go protobuf bindings for snapshot events.

Important APIs/types/functions: `SnapshotPrepare` has `Key`, `Parent`, and `Snapshotter`; `SnapshotCommit` has `Key`, `Name`, and `Snapshotter`; `SnapshotRemove` has `Key` and `Snapshotter`. Each has standard protobuf methods and nil-safe getters.

Control flow: generated descriptor setup and getter access only. `rawDescGZIP` lazily compresses the schema descriptor; `file_events_snapshot_proto_init` registers three messages.

State/persistence: no state beyond serialized event payloads. The gap in field numbers (`snapshotter = 5`) preserves compatibility with earlier schema evolution.

Dependencies/integration: blank-imports containerd API types for fieldpath extension registration; uses protobuf runtime/reflection. Integrates with snapshotter operations and event filters.

Risks/test signals: field number 5 for `snapshotter` should not be compacted. Consumers should handle empty parent on prepare and absent snapshotter in older events. Tests should cover prepare/commit/remove event payloads and fieldpath lookups.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/snapshot.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/snapshot.proto -->
# sources/cloud-native/containerd/api/events/snapshot.proto

Purpose: protobuf schema for snapshot lifecycle events.

Important APIs/types/functions: defines `SnapshotPrepare`, `SnapshotCommit`, and `SnapshotRemove`. Common fields are `key` and `snapshotter`; prepare also carries `parent`, commit carries final `name`. Fieldpath generation is enabled.

Control flow: declarative only. Snapshot service code emits these messages around snapshot prepare, commit, and removal operations.

State/persistence: message field numbers are persistent API state. `snapshotter = 5` indicates reserved/legacy numbering space and must remain stable.

Dependencies/integration: imports `types/fieldpath.proto`; generated Go uses package `events`. Used by event publication, filtering, and snapshotter-specific consumers.

Risks/test signals: key/name semantics differ between active snapshot keys and committed snapshot names; tests should ensure consumers do not confuse them. Compatibility testing should preserve field numbers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/snapshot.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/snapshot_fieldpath.pb.go -->
# sources/cloud-native/containerd/api/events/snapshot_fieldpath.pb.go

Purpose: generated string fieldpath accessors for snapshot events.

Important APIs/types/functions: `SnapshotPrepare.Field` exposes `key`, `parent`, and `snapshotter`; `SnapshotCommit.Field` exposes `key`, `name`, and `snapshotter`; `SnapshotRemove.Field` exposes `key` and `snapshotter`.

Control flow: simple path length guard and first-segment switch; returns a field value only when the string is non-empty.

State/persistence: stateless derived access over an event message.

Dependencies/integration: no external imports. Integrates with event matching/filtering for snapshot-related event topics.

Risks/test signals: empty strings are considered undefined, so a valid empty parent cannot be matched as present. Tests should verify filter behavior for root snapshots where parent may be empty.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/snapshot_fieldpath.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/task.pb.go -->
# sources/cloud-native/containerd/api/events/task.pb.go

Purpose: generated Go protobuf bindings for container task lifecycle and exec events.

Important APIs/types/functions: exports `TaskCreate`, `TaskStart`, `TaskDelete`, `TaskIO`, `TaskExit`, `TaskOOM`, `TaskExecAdded`, `TaskExecStarted`, `TaskPaused`, `TaskResumed`, and `TaskCheckpointed`. Important fields include container IDs, bundle path, rootfs mounts, IO paths, checkpoint reference, PIDs, exit statuses, exec IDs, and `ExitedAt` timestamps. Getters are nil-safe and return zero values.

Control flow: generated code handles protobuf reflection, descriptor compression, and metadata registration. `TaskCreate` depends on `containerd.types.Mount` and nested `TaskIO`; delete/exit depend on protobuf timestamps. No task management behavior is implemented here.

State/persistence: no local state. Serialized messages are durable event payload contracts; field numbers and message names are API state.

Dependencies/integration: imports `github.com/containerd/containerd/api/types`, protobuf runtime/reflection, and timestamp types. Integrates with runtime task services, event streams, and consumers watching task state transitions.

Risks/test signals: task events have many fields where zero values can mean either unset or a real value, notably PID and exit status. `TaskDelete.ID` defaults to empty string to mean init exec, which consumers must interpret correctly. Tests should cover init exec versus named exec, rootfs mount serialization, timestamps, and checkpoint events.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/task.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/task.proto -->
# sources/cloud-native/containerd/api/events/task.proto

Purpose: source protobuf schema for container task events.

Important APIs/types/functions: package `containerd.events`, Go package `api/events;events`. Defines lifecycle messages for task create/start/delete/exit/OOM/pause/resume/checkpoint plus exec add/start and `TaskIO`. It imports timestamps, fieldpath options, and mount types.

Control flow: declarative API contract; runtime task service code publishes messages as task state changes occur. `TaskDelete` comment defines an important convention: empty `id` matches the init exec for the task.

State/persistence: wire field numbers and message names are the persistent event schema. `rootfs` embeds `containerd.types.Mount`; timestamps encode exit time.

Dependencies/integration: integrates with task runtime implementations, containerd event service, mount type schema, and fieldpath filtering.

Risks/test signals: changing `id` semantics would break exec lifecycle consumers. Tests should cover all event variants, fieldpath generation, timestamp fields, and compatibility with historical task event payloads.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/task.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/events/task_fieldpath.pb.go -->
# sources/cloud-native/containerd/api/events/task_fieldpath.pb.go

Purpose: generated fieldpath accessors for task event messages.

Important APIs/types/functions: `Field` methods expose string fields across task messages: container IDs, bundle, checkpoint, IO stream paths, exec IDs, and task exit/delete IDs. Numeric, boolean, timestamp, and repeated mount fields are marked unhandled in comments.

Control flow: each method guards empty paths, switches on first path segment, and returns non-empty string field values. Nested `TaskCreate.io.*` delegates to `TaskIO.Field` when `IO` is non-nil.

State/persistence: stateless runtime field lookup.

Dependencies/integration: no external imports. Used by event filters that match string-valued task event fields.

Risks/test signals: filters cannot match PID, exit status, terminal, timestamps, or rootfs mounts through these generated helpers. `TaskCreate.io` is absent if the nested message is nil. Tests should cover nested IO lookup, unsupported fields returning false, and empty string IDs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/events/task_fieldpath.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/releases/v1.10.0.toml -->
# sources/cloud-native/containerd/api/releases/v1.10.0.toml

Purpose: release configuration for the containerd API module version `api/v1.10.0`.

Important APIs/types/functions: TOML keys set `commit = "HEAD"`, project/repository identity, `sub_path = "api"`, ignored self dependency `github.com/containerd/containerd`, previous release `api/v1.9.0`, `pre_release = false`, and a preface saying this is the 11th containerd 1.x API release aligned with containerd 2.2.

Control flow: consumed by release tooling rather than executed. The tool reads this configuration to select the tagged commit, generate release notes, and compare against the previous API release.

State/persistence: persistent release metadata; `previous` is especially important for changelog diffing.

Dependencies/integration: integrates with the containerd release process and GitHub repository `containerd/containerd`.

Risks/test signals: wrong `previous` would produce incorrect release notes; wrong `sub_path` would tag the wrong module. Release validation should confirm the intended API tag, changelog span, and no unintended dependency inclusion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/releases/v1.10.0.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/releases/v1.11.0.toml -->
# sources/cloud-native/containerd/api/releases/v1.11.0.toml

Purpose: release configuration for `api/v1.11.0`.

Important APIs/types/functions: sets `commit = "HEAD"`, `project_name = "containerd"`, `github_repo = "containerd/containerd"`, `sub_path = "api"`, ignores the root containerd dependency, points `previous` to `api/v1.10.0`, disables pre-release mode, and describes the 12th 1.x API release aligned with containerd 2.3.

Control flow: declarative input for release tooling.

State/persistence: records the release lineage from `api/v1.10.0` to `api/v1.11.0`.

Dependencies/integration: used by API module release automation and GitHub release note generation.

Risks/test signals: because `commit` is `HEAD`, release runs must ensure checkout state is exactly the intended tag source. Tests/checks should validate the generated changelog references the 2.3-aligned API release.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/releases/v1.11.0.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/releases/v1.8.0.toml -->
# sources/cloud-native/containerd/api/releases/v1.8.0.toml

Purpose: release configuration for the first dedicated containerd API release.

Important APIs/types/functions: identifies the project and GitHub repo, sets `sub_path = "api"`, ignores `github.com/containerd/containerd`, uses `previous = "v1.7.0"`, marks `pre_release = false`, and includes a preface explaining this starts dedicated API releases while continuing 1.x compatibility as the ninth minor API release.

Control flow: consumed by release tooling for diffing and release-note generation.

State/persistence: captures the boundary between the previous root/containerd tag and the new API module tag line.

Dependencies/integration: integrates the API submodule into containerd's release workflow.

Risks/test signals: this file is riskier than later release configs because `previous` uses `v1.7.0` rather than an `api/` tag. Release tooling should be tested against that cross-tag lineage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/releases/v1.8.0.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/releases/v1.9.0.toml -->
# sources/cloud-native/containerd/api/releases/v1.9.0.toml

Purpose: release configuration for `api/v1.9.0`.

Important APIs/types/functions: standard release keys select `HEAD`, `containerd/containerd`, API subpath, ignored self dependency, `previous = "api/v1.8.0"`, non-prerelease mode, and a preface that the 10th 1.x API release aligns with containerd 2.1.

Control flow: declarative input to release automation.

State/persistence: tracks release lineage and human-facing release note preface.

Dependencies/integration: used by the containerd API release process and changelog generation.

Risks/test signals: incorrect previous tag or release preface would mislead consumers about API compatibility. Release dry-runs should validate diff base and generated notes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/releases/v1.9.0.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/bootstrap/v1/bootstrap.pb.go -->
# sources/cloud-native/containerd/api/runtime/bootstrap/v1/bootstrap.pb.go

Purpose: generated Go protobuf bindings for the shim bootstrap protocol.

Important APIs/types/functions: exports open numeric enum `LogLevel` with negative verbose values and positive severe values, `Capability`, `BootstrapParams`, `Extension`, and `BootstrapResult`. `BootstrapParams` includes instance ID, namespace, log level, containerd version, TTRPC/gRPC addresses, binary path, typed extensions, and optional `SocketDir *string`. `BootstrapResult` includes version, address, protocol, capabilities, and metadata.

Control flow: protobuf-generated methods provide enum descriptors, message reflection, getters, descriptor compression, and type registration. `GetSocketDir` returns empty string when the optional pointer is nil.

State/persistence: no local storage; this file defines the JSON/protobuf-compatible startup contract between containerd and shims. Optional field presence matters for `socket_dir`.

Dependencies/integration: depends on protobuf runtime/reflection and `google.protobuf.Any`. Integrates with bootstrap helpers, shim process startup, and typed extension negotiation.

Risks/test signals: generated code shows duplicated `ms.StoreMessageInfo(mi)` in `BootstrapParams.ProtoReflect`, harmless but a regeneration artifact worth watching. Unknown log levels are allowed by schema; consumers must not reject them. Tests should cover optional socket_dir presence, Any extensions, metadata maps, and enum numeric compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/bootstrap/v1/bootstrap.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/bootstrap/v1/bootstrap.proto -->
# sources/cloud-native/containerd/api/runtime/bootstrap/v1/bootstrap.proto

Purpose: authoritative bootstrap protocol schema between containerd and shim processes at startup.

Important APIs/types/functions: documents the flow: containerd spawns shim, writes `BootstrapParams` as JSON to stdin, shim writes `BootstrapResult` as JSON to stdout, then containerd connects to the returned address. `BootstrapParams` centralizes identity, namespace, log level, daemon version, daemon API addresses, binary path, typed extensions, and optional socket directory. `BootstrapResult` returns shim protocol/address/capabilities/metadata. Enums define log level and future capabilities.

Control flow: declarative schema plus protocol documentation. The actual control flow occurs in bootstrap callers and shims following the documented stdin/stdout exchange.

State/persistence: field numbers and JSON names are the persistent inter-process contract. `google.protobuf.Any` extensions are the extension mechanism without changing core fields.

Dependencies/integration: imports `google/protobuf/any.proto`; Go package is `api/runtime/bootstrap/v1;bootstrap`. Integrates shim startup, log configuration, daemon connection addresses, and optional capability negotiation.

Risks/test signals: stdin/stdout JSON exchange is sensitive to logging accidentally polluting stdout. `socket_dir` must stay short due to Unix socket path limits. Tests should exercise JSON round trips, unknown log-level values, extension preservation, and protocol/address validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/bootstrap/v1/bootstrap.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/bootstrap/v1/doc.go -->
# sources/cloud-native/containerd/api/runtime/bootstrap/v1/doc.go

Purpose: package declaration file for `runtime/bootstrap/v1`.

Important APIs/types/functions: declares package `bootstrap`; contains only license header and package statement.

Control flow: none.

State/persistence: none.

Dependencies/integration: establishes Go package documentation/compilation unit for bootstrap protocol files in this folder.

Risks/test signals: low risk. Its presence matters for package-level documentation and build consistency; tests are indirect through package compilation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/bootstrap/v1/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/bootstrap/v1/helpers.go -->
# sources/cloud-native/containerd/api/runtime/bootstrap/v1/helpers.go

Purpose: hand-written convenience helpers around the generated bootstrap protocol.

Important APIs/types/functions: `LogLevelFromString` converts logrus-style strings and numeric strings into `LogLevel`, defaulting unknown values to info. `(*BootstrapParams).AddExtension` appends a protobuf message as an `Extension`, avoiding double wrapping when the input is already `*anypb.Any`. `(*BootstrapParams).FindExtension` searches extensions for a message type matching `dst` and unmarshals into it.

Control flow: `LogLevelFromString` uses a switch for known strings, then `strconv.ParseInt` for numeric input. `AddExtension` type-checks for `*anypb.Any` or calls `anypb.New`. `FindExtension` nil-checks the receiver, derives the destination full name for errors, iterates extensions, uses `MessageIs`, and returns on the first successful unmarshal.

State/persistence: mutates `BootstrapParams.Extensions` in memory. Does not persist outside the eventual serialized bootstrap params.

Dependencies/integration: imports `fmt`, `strconv`, protobuf `proto`, and `anypb`. Integrates generated `BootstrapParams` with callers that need typed extension configuration.

Risks/test signals: `FindExtension` assumes `dst` is non-nil; passing nil would panic via `ProtoReflect`. Unknown textual log levels silently become info, which may hide typoed configuration. Tests in `helpers_test.go` cover add/find, missing extensions, and pre-wrapped Any values.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/bootstrap/v1/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/bootstrap/v1/helpers_test.go -->
# sources/cloud-native/containerd/api/runtime/bootstrap/v1/helpers_test.go

Purpose: unit tests for bootstrap extension helpers.

Important APIs/types/functions: `TestExtensions` verifies adding a typed runc options message and finding/unmarshaling it. `TestExtensionNotFound` verifies a missing extension returns `found=false` without error. `TestAddExtensionWithAny` verifies pre-wrapped `anypb.Any` is accepted without double wrapping and that its type URL still contains `Options`.

Control flow: each test creates a fresh `BootstrapParams`, calls helper methods, and uses `t.Fatalf` on unexpected errors or field values.

State/persistence: test-only in-memory state; no files or external services.

Dependencies/integration: imports `github.com/containerd/containerd/api/types/runc/options` as a concrete extension message, `anypb`, `strings`, and `testing`. These tests validate integration with generated protobuf Any behavior.

Risks/test signals: coverage does not include `LogLevelFromString`, nil receiver behavior beyond `FindExtension`, nil destination panic behavior, or malformed Any unmarshal errors. Existing tests are strong signals for typed extension round trips.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/bootstrap/v1/helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/sandbox/v1/doc.go -->
# sources/cloud-native/containerd/api/runtime/sandbox/v1/doc.go

Purpose: package declaration file for the runtime sandbox v1 API package.

Important APIs/types/functions: declares package `sandbox`; otherwise only license header.

Control flow: none.

State/persistence: none.

Dependencies/integration: participates in Go package compilation for generated sandbox protobuf, gRPC, and TTRPC bindings.

Risks/test signals: low risk; build/package tests are the relevant signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/sandbox/v1/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/sandbox/v1/sandbox.pb.go -->
# sources/cloud-native/containerd/api/runtime/sandbox/v1/sandbox.pb.go

Purpose: generated Go protobuf bindings for the optional shim sandbox runtime API.

Important APIs/types/functions: exports request/response types for sandbox create, start, platform, stop, update, wait, status, ping, shutdown, and metrics. Important fields include sandbox ID, bundle path, rootfs mounts, options/resources `Any`, netns path, annotations, start PID/spec/created time, platform, stop timeout, wait exit data, status info/extra, and metrics.

Control flow: generated message methods provide nil-safe getters, reflection, descriptor compression, and descriptor registration. The descriptor includes one service with nine RPCs; `UpdateSandboxRequest/Response` exist as messages but there is no corresponding service method in this proto.

State/persistence: no local persistence. The messages define wire contracts between containerd and sandbox-capable shims.

Dependencies/integration: imports containerd `types` for mounts, metrics, and platform plus protobuf `Any` and `Timestamp`. Integrates with gRPC/TTRPC transport files and shim implementations.

Risks/test signals: mismatch between message definitions and service methods can confuse implementers, especially the unused update messages. Map fields are nil on absent messages. Tests should validate cross-transport encoding, status timestamps, metrics type, and optional Any payload unpacking.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/sandbox/v1/sandbox.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/sandbox/v1/sandbox.proto -->
# sources/cloud-native/containerd/api/runtime/sandbox/v1/sandbox.proto

Purpose: source protobuf service definition for optional sandbox-capable shim APIs.

Important APIs/types/functions: defines service `Sandbox` with unary RPCs `CreateSandbox`, `StartSandbox`, `Platform`, `StopSandbox`, `WaitSandbox`, `SandboxStatus`, `PingSandbox`, `ShutdownSandbox`, and `SandboxMetrics`. Message types describe sandbox identity, bundle/rootfs/options, network namespace, annotations, start response PID/spec, platform response, stop timeout, wait exit data, status info, ping/shutdown, and metrics.

Control flow: intended call sequence is create after shim launch, start, platform query for OCI spec generation, status/metrics/ping while running, stop/wait/shutdown for teardown. The schema itself is declarative.

State/persistence: no storage; message fields define transport API state. `Any` fields support runtime-specific options/resources/spec/extra.

Dependencies/integration: imports protobuf Any/Timestamp and containerd metrics, mount, and platform types. Generated bindings provide both gRPC and TTRPC transports.

Risks/test signals: `UpdateSandboxRequest/Response` are defined but absent from the service, which may be intentional future work or API drift. Implementers must define exact state strings and status info conventions. Tests should cover RPC method registration and compatibility across gRPC/TTRPC.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/sandbox/v1/sandbox.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/sandbox/v1/sandbox_grpc.pb.go -->
# sources/cloud-native/containerd/api/runtime/sandbox/v1/sandbox_grpc.pb.go

Purpose: generated gRPC bindings for the sandbox runtime service, excluded when build tag `no_grpc` is set.

Important APIs/types/functions: `SandboxClient` interface and `NewSandboxClient` wrap `grpc.ClientConnInterface` and invoke nine fully-qualified RPCs. `SandboxServer` declares the same methods and requires embedding `UnimplementedSandboxServer` for forward compatibility. `RegisterSandboxServer`, per-method `_Sandbox_*_Handler` functions, and `Sandbox_ServiceDesc` register server-side unary RPCs.

Control flow: client methods allocate response objects and call `cc.Invoke`. Server handlers decode requests, optionally pass through unary interceptors, and dispatch to the concrete `SandboxServer`. Unimplemented methods return `codes.Unimplemented`.

State/persistence: no durable state; clients hold a connection handle and server registration holds service metadata.

Dependencies/integration: imports `context`, `google.golang.org/grpc`, and gRPC status/codes. Integrates sandbox service implementations with gRPC transport.

Risks/test signals: generated `_Sandbox_StartSandbox_Handler` contains a duplicated unreachable `return nil, err` in the decode-error branch. It is harmless but indicates generated-code quality should be checked on regeneration. Tests should cover service registration, interceptor path, unimplemented defaults, and build behavior with `no_grpc`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/sandbox/v1/sandbox_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/sandbox/v1/sandbox_ttrpc.pb.go -->
# sources/cloud-native/containerd/api/runtime/sandbox/v1/sandbox_ttrpc.pb.go

Purpose: generated TTRPC bindings for the sandbox runtime service.

Important APIs/types/functions: `TTRPCSandboxService` declares the nine sandbox RPC methods. `RegisterTTRPCSandboxService` registers a service name `containerd.runtime.sandbox.v1.Sandbox` with a method map that unmarshals requests and calls the service. `NewTTRPCSandboxClient` returns a client implementing the same interface, with each method calling `ttrpc.Client.Call`.

Control flow: server registration stores closures per method; each closure unmarshals into a request struct and invokes the service. Client methods create response structs, perform a TTRPC call with service/method names, and return the response or error.

State/persistence: no persistent state. Client struct holds the TTRPC client pointer.

Dependencies/integration: imports `context` and `github.com/containerd/ttrpc`. This is the lightweight transport path commonly used by shims.

Risks/test signals: method names must stay exactly aligned with the proto service and gRPC bindings. Tests should cover registration, bad unmarshal errors, per-method client call names, and parity with gRPC behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/sandbox/v1/sandbox_ttrpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v2/doc.go -->
# sources/cloud-native/containerd/api/runtime/task/v2/doc.go

Purpose: package declaration file for the runtime task v2 API package.

Important APIs/types/functions: declares package `task`; only license header and package statement are present in this file.

Control flow: none.

State/persistence: none.

Dependencies/integration: supports package-level compilation/documentation for task v2 API files elsewhere in the folder.

Risks/test signals: low risk. Build tests covering the package are sufficient.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v2/doc.go -->
