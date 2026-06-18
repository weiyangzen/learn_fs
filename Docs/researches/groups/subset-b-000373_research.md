# subset-b-000373 Research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/protosanitizer/test/csi.proto -->
## sources/control-plane/csi-lib-utils/protosanitizer/test/csi.proto

### Purpose
`csi.proto` is a generated copy of the Container Storage Interface v1 protobuf API used by the `protosanitizer` test fixtures. In this repository it is not an implementation file; it is schema input that defines the CSI services, messages, enums, and custom protobuf options that generated Go bindings expose through descriptors. The most important custom option for this package is `csi_secret`, a `google.protobuf.FieldOptions` extension that marks request fields whose values must be redacted from logs.

The file models the full CSI control, node, identity, group-snapshot, and snapshot-metadata RPC surface. That breadth matters for the sanitizer because secret annotations appear across many request families and because redaction must recurse through normal messages, repeated messages, map values, oneof-selected messages, enum values, wrapper messages, and unknown/future fields without mutating the source message.

### Important APIs, Types, And Functions
The top-level package is `csi.v1`, with Go output configured for `github.com/container-storage-interface/spec/lib/go/csi`. The schema imports `google/protobuf/descriptor.proto` for custom options, `timestamp.proto` for snapshot timestamps, and `wrappers.proto` for optional scalar wrappers such as `BoolValue` and `Int64Value`.

The custom extension API is central:

- `csi_secret` extends `FieldOptions` and marks sensitive fields.
- `alpha_field`, `alpha_message`, `alpha_method`, `alpha_service`, `alpha_enum`, and `alpha_enum_value` mark experimental CSI surface.

The service definitions are:

- `Identity`: `GetPluginInfo`, `GetPluginCapabilities`, and `Probe`.
- `Controller`: volume create/delete, controller publish/unpublish, validation, listing, capacity, controller capability discovery, snapshot create/delete/list, expansion, and alpha get/modify volume RPCs.
- `GroupController`: alpha group snapshot capability, create, delete, and get RPCs.
- `SnapshotMetadata`: alpha server-streaming metadata RPCs for allocated ranges and delta ranges.
- `Node`: staging, unstaging, publishing, unpublishing, stats, expansion, capability discovery, and node info.

Core messages include `GetPluginInfo*`, `PluginCapability`, `Probe*`, `CreateVolume*`, `VolumeContentSource`, `VolumeCapability`, `CapacityRange`, `Volume`, `TopologyRequirement`, `Topology`, controller publish/unpublish messages, validation messages, list messages, capacity messages, controller and node capability messages, snapshot messages, node-stage/publish/stat/expand messages, volume condition messages, group snapshot messages, and block metadata messages.

The important secret-bearing request fields are the `secrets` maps in create/delete/publish/unpublish/validate/modify/snapshot/expand/group/snapshot-metadata request messages. `NodeExpandVolumeRequest.secrets` is both secret and alpha. These annotations are the descriptor signal consumed by `protosanitizer.isCSI1Secret` via the generated `csi.E_CsiSecret` extension.

### Control Flow
The file has declarative protobuf flow rather than runtime control flow. The generated bindings use it to construct descriptors, Go message structs, oneof wrappers, enum descriptors, and service descriptors. Runtime flow enters indirectly when tests or application code pass generated CSI messages into `protosanitizer.StripSecrets`.

The effective flow for this schema in the sanitizer is:

1. A CSI request type generated from this file is populated by a test or by CSI middleware.
2. `StripSecrets` detects that the value implements `proto.Message` and walks its `ProtoReflect()` descriptor fields.
3. For each populated field, the sanitizer checks whether that field descriptor has the `csi_secret` extension.
4. If a field is marked, the serialized logging value becomes `"***stripped***"`.
5. If a field is not marked, the sanitizer recursively descends into messages, repeated values, map values, and selected oneof messages; enum values are rendered as names when known.

Within the CSI API itself, request and response messages encode expected orchestration flow: identity discovery gates controller and node use; plugin/controller/node capabilities advertise optional RPC families; `CreateVolume` can depend on topology, capacity, content source, and mutable parameters; controller publish data feeds node stage/publish calls; snapshot creation feeds volume content sources; expansion may require both controller and node expansion; list RPCs paginate through `max_entries` and `starting_token`; snapshot metadata RPCs stream ordered block ranges.

### State, Persistence, And Dependencies
The proto file persists no runtime state. It defines the persistent wire contract and generated descriptor metadata used by Go code. CSI runtime state is represented as IDs and attributes in messages: volume IDs, snapshot IDs, group snapshot IDs, node IDs, topology segments, volume context, publish context, capacity values, readiness booleans, condition messages, and pagination tokens.

Dependencies are standard protobuf descriptors, timestamps, wrappers, the CSI generated Go package, and Go protobuf reflection. The sanitizer depends on the generated extension symbol `csi.E_CsiSecret` and on field descriptors retaining the extension data. If the generated code or imported descriptor set drops custom options, secret redaction cannot reliably distinguish sensitive fields from ordinary maps or scalars.

### Integration Points
This file is a fixture for `sources/control-plane/csi-lib-utils/protosanitizer`. The production sanitizer imports the upstream generated CSI Go package and uses its `E_CsiSecret` extension. The tests use standard CSI messages such as `csi.CreateVolumeRequest` to verify redaction of real current-spec fields like `CreateVolumeRequest.secrets`.

The local `test/Makefile` does not generate Go from this file directly; it generates `csitest/csitest.pb.go` from `csitest.proto`. However, `csitest.proto` imports this file so that the test-only package can refer to `csi.v1.csi_secret` on deliberately modified fields. This makes `csi.proto` the extension authority for the test schema even when the message types live in `csitest.v1`.

### Risks
The main risk is extension identity drift. `protosanitizer.isCSI1Secret` retrieves exactly the CSI extension symbol from the generated Go package. Test or generated descriptors must use the same extension number and identity, otherwise secret fields will serialize as clear text.

The schema contains many non-secret fields whose comments warn that they may contain opaque or sensitive data, such as mount flags, parameters, volume context, publish context, topology, and condition messages. The sanitizer only strips fields marked with `csi_secret`; it does not infer sensitivity from comments or names. That is correct for descriptor-driven behavior, but callers must not assume every potentially sensitive opaque field is removed.

Because the schema includes alpha fields and services, compatibility is uneven across generated versions. New alpha fields can appear in future messages, and old sidecars can receive unknown fields. The surrounding tests explicitly cover a future-message scenario to ensure unknown fields are not dumped by the current sanitizer path.

The proto is generated and should not be hand-edited casually. A local edit that changes field numbers, package names, extension numbers, or option names can invalidate generated bindings and test assumptions.

### Test Signals
Useful test signals include redaction of `CreateVolumeRequest.secrets`, preservation of non-secret fields, recursive handling of topology and volume capability submessages, enum rendering for known enum values, numeric rendering for unknown enum values, JSON output stability, and non-mutation of the original message.

For this fixture specifically, tests should continue to verify that fields marked with `csi_secret` are stripped regardless of field name and that unmarked fields remain visible. Regeneration signals include `protoc` success with custom options retained, `go test ./sources/control-plane/csi-lib-utils/protosanitizer` passing, and expected output strings in `protosanitizer_test.go` remaining aligned with the descriptor names generated from this schema.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/protosanitizer/test/csi.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/protosanitizer/test/csitest.proto -->
## sources/control-plane/csi-lib-utils/protosanitizer/test/csitest.proto

### Purpose
`csitest.proto` is a modified CSI-like schema built specifically to test secret stripping in `protosanitizer`. The accompanying README says it is a modified version of the CSI 1.0.0 spec whose only purpose is to test stripping of secret fields. It keeps the familiar CSI `Identity`, `Controller`, and `Node` service shapes while adding deliberately awkward `csi.v1.csi_secret` placements that exercise descriptor-based redaction beyond the normal upstream `secrets` maps.

The schema lives in package `csitest.v1` and generates Go code under `github.com/kubernetes-csi/csi-lib-utils/protosanitizer/test/csitest`. It imports `csi.proto` specifically to use the `csi.v1.csi_secret` field option, so it validates that redaction is based on descriptor options rather than a hard-coded package, message name, or field name.

### Important APIs, Types, And Functions
The service set is a compact CSI 1.0 style surface:

- `Identity`: plugin info, capabilities, and probe.
- `Controller`: create/delete volume, publish/unpublish, validate capabilities, list volumes, get capacity, controller capability discovery, create/delete/list snapshots.
- `Node`: stage/unstage, publish/unpublish, get volume stats, get capabilities, and get info.

Most message types mirror CSI 1.0 structures: plugin info/capability messages, `CreateVolumeRequest`, `VolumeContentSource`, `CreateVolumeResponse`, `VolumeCapability`, `CapacityRange`, `Volume`, topology messages, controller publish/unpublish messages, validation messages, list messages, capacity messages, controller capability messages, snapshot messages, node stage/publish/stat messages, usage messages, node capability messages, and node info messages.

The test-specific secret API is concentrated in these fields:

- `CreateVolumeRequest.seecreets`: a renamed `map<string,string>` secret field, proving redaction is option-driven rather than name-driven.
- `CreateVolumeRequest.new_secret_int`: a scalar `int64` marked secret, proving secrets are not limited to string maps.
- `CreateVolumeRequest.maybe_secret_map`: an unmarked map whose values are `VolumeCapability`; this forces recursion into map values.
- `VolumeContentSource.VolumeSource.oneof_secret_field`: a secret nested inside a message selected through a oneof.
- `VolumeContentSource.nested_secret_field`: a secret in a nested message reachable from `CreateVolumeRequest.volume_content_source`.
- `VolumeCapability.array_secret`: a secret field inside messages that commonly appear in repeated arrays and map values.
- Standard `secrets` maps on delete, publish, unpublish, validate, snapshot, and node stage/publish requests.

### Control Flow
Like `csi.proto`, this file is declarative, but it is designed around a concrete sanitizer execution path. The generated `csitest.CreateVolumeRequest` in `protosanitizer_test.go` populates `Seecreets`, `NewSecretInt`, repeated `VolumeCapabilities` with `ArraySecret`, `MaybeSecretMap` values with `ArraySecret`, and `VolumeContentSource.Volume.OneofSecretField` plus `NestedSecretField`.

When passed to `StripSecrets`, the sanitizer should:

1. Visit only populated fields through protobuf reflection.
2. Replace `seecreets` and `new_secret_int` immediately because those fields carry `csi.v1.csi_secret`.
3. Recurse through the unmarked `maybe_secret_map`, stringify int64 map keys, and redact each nested `VolumeCapability.array_secret`.
4. Recurse through repeated `volume_capabilities` and redact each element's `array_secret` while preserving non-secret mount data.
5. Recurse through `volume_content_source`, follow the selected `volume` oneof, redact `oneof_secret_field`, preserve `volume_id`, and redact `nested_secret_field`.

The schema also supports a compatibility test where a `csitest.CreateVolumeRequest` is marshaled and unmarshaled into the current upstream `csi.CreateVolumeRequest`. That path verifies that fields unknown to the older type are not exposed in sanitizer output.

### State, Persistence, And Dependencies
The proto itself has no mutable state. Its durable output is the generated `test/csitest/csitest.pb.go`, including descriptor data, Go structs, oneof wrappers, map entry types, and service descriptors. The `test/Makefile` pins `protoc` default version `25.2`, installs `protoc-gen-go`, and runs `protoc --go_out=csitest --go_opt=paths=source_relative csitest.proto`.

The file depends on protobuf descriptor, timestamp, and wrapper imports plus local `csi.proto` for the `csi.v1.csi_secret` extension. The generated code is imported by `protosanitizer_test.go`, where populated messages become test inputs for the runtime sanitizer.

### Integration Points
`csitest.proto` is tightly integrated with `protosanitizer_test.go`. The expected JSON string in `TestStripSecrets` names the generated text names: `seecreets`, `new_secret_int`, `maybe_secret_map`, `array_secret`, `nested_secret_field`, and `oneof_secret_field`. Any schema change that alters those field names, field numbers, oneof structure, or secret options must update both generated Go and expected test output.

The file also integrates with the upstream-like `csi.proto` fixture. Because it imports `csi.proto` only for the extension, it is a focused guard against implementations that redact based on exact CSI request type or on a field literally named `secrets`. It proves that any field in any generated protobuf package carrying the CSI secret option is treated as sensitive.

### Risks
The most important risk is generated-code drift. `csitest.pb.go` must be regenerated after edits to this proto, or tests may run against stale descriptors. Because the sanitizer is descriptor-driven, stale generated descriptors can make source review misleading.

Another risk is accidental weakening of the fixture. Renaming `seecreets` back to `secrets`, removing scalar or nested secret fields, or marking `maybe_secret_map` itself as secret would reduce coverage of option-based, recursive redaction. Similarly, removing the oneof nesting would stop testing oneof traversal.

The import relationship with `csi.proto` is required. If the local extension definition diverges from the generated CSI package used by `protosanitizer.isCSI1Secret`, the test may fail or, worse, stop exercising the same extension identity as production.

As with the upstream-like schema, unmarked opaque fields remain visible. This is intentional for the fixture, but any future test additions should be explicit about whether a field is secret by option or merely sensitive by comment.

### Test Signals
Strong test signals are the exact expected JSON in `TestStripSecrets`: `seecreets`, `new_secret_int`, every `array_secret`, `nested_secret_field`, and `oneof_secret_field` must become `"***stripped***"`; `volume_id`, `name`, `capacity_range`, and mount `fs_type` must remain visible; integer map keys must become string JSON keys; and the original message must remain unchanged after formatting.

Build signals include successful `make build` in the `protosanitizer/test` directory, regenerated `csitest/csitest.pb.go` containing the test fields and oneof wrappers, and `go test` for the protosanitizer package. Regression tests should fail if redaction depends on the literal field name `secrets`, if scalar secret values leak, if recursion into maps/repeated messages/oneofs is removed, or if unknown future fields are logged after unmarshaling into an older CSI type.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/protosanitizer/test/csitest.proto -->
