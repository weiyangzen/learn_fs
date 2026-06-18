# sources/control-plane/csi-lib-utils/protosanitizer/test/csi.proto Research

## Purpose
`csi.proto` is a generated copy of the Container Storage Interface v1 protobuf API used by the `protosanitizer` test fixtures. In this repository it is not an implementation file; it is schema input that defines the CSI services, messages, enums, and custom protobuf options that generated Go bindings expose through descriptors. The most important custom option for this package is `csi_secret`, a `google.protobuf.FieldOptions` extension that marks request fields whose values must be redacted from logs.

The file models the full CSI control, node, identity, group-snapshot, and snapshot-metadata RPC surface. That breadth matters for the sanitizer because secret annotations appear across many request families and because redaction must recurse through normal messages, repeated messages, map values, oneof-selected messages, enum values, wrapper messages, and unknown/future fields without mutating the source message.

## Important APIs, Types, And Functions
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

## Control Flow
The file has declarative protobuf flow rather than runtime control flow. The generated bindings use it to construct descriptors, Go message structs, oneof wrappers, enum descriptors, and service descriptors. Runtime flow enters indirectly when tests or application code pass generated CSI messages into `protosanitizer.StripSecrets`.

The effective flow for this schema in the sanitizer is:

1. A CSI request type generated from this file is populated by a test or by CSI middleware.
2. `StripSecrets` detects that the value implements `proto.Message` and walks its `ProtoReflect()` descriptor fields.
3. For each populated field, the sanitizer checks whether that field descriptor has the `csi_secret` extension.
4. If a field is marked, the serialized logging value becomes `"***stripped***"`.
5. If a field is not marked, the sanitizer recursively descends into messages, repeated values, map values, and selected oneof messages; enum values are rendered as names when known.

Within the CSI API itself, request and response messages encode expected orchestration flow: identity discovery gates controller and node use; plugin/controller/node capabilities advertise optional RPC families; `CreateVolume` can depend on topology, capacity, content source, and mutable parameters; controller publish data feeds node stage/publish calls; snapshot creation feeds volume content sources; expansion may require both controller and node expansion; list RPCs paginate through `max_entries` and `starting_token`; snapshot metadata RPCs stream ordered block ranges.

## State, Persistence, And Dependencies
The proto file persists no runtime state. It defines the persistent wire contract and generated descriptor metadata used by Go code. CSI runtime state is represented as IDs and attributes in messages: volume IDs, snapshot IDs, group snapshot IDs, node IDs, topology segments, volume context, publish context, capacity values, readiness booleans, condition messages, and pagination tokens.

Dependencies are standard protobuf descriptors, timestamps, wrappers, the CSI generated Go package, and Go protobuf reflection. The sanitizer depends on the generated extension symbol `csi.E_CsiSecret` and on field descriptors retaining the extension data. If the generated code or imported descriptor set drops custom options, secret redaction cannot reliably distinguish sensitive fields from ordinary maps or scalars.

## Integration Points
This file is a fixture for `sources/control-plane/csi-lib-utils/protosanitizer`. The production sanitizer imports the upstream generated CSI Go package and uses its `E_CsiSecret` extension. The tests use standard CSI messages such as `csi.CreateVolumeRequest` to verify redaction of real current-spec fields like `CreateVolumeRequest.secrets`.

The local `test/Makefile` does not generate Go from this file directly; it generates `csitest/csitest.pb.go` from `csitest.proto`. However, `csitest.proto` imports this file so that the test-only package can refer to `csi.v1.csi_secret` on deliberately modified fields. This makes `csi.proto` the extension authority for the test schema even when the message types live in `csitest.v1`.

## Risks
The main risk is extension identity drift. `protosanitizer.isCSI1Secret` retrieves exactly the CSI extension symbol from the generated Go package. Test or generated descriptors must use the same extension number and identity, otherwise secret fields will serialize as clear text.

The schema contains many non-secret fields whose comments warn that they may contain opaque or sensitive data, such as mount flags, parameters, volume context, publish context, topology, and condition messages. The sanitizer only strips fields marked with `csi_secret`; it does not infer sensitivity from comments or names. That is correct for descriptor-driven behavior, but callers must not assume every potentially sensitive opaque field is removed.

Because the schema includes alpha fields and services, compatibility is uneven across generated versions. New alpha fields can appear in future messages, and old sidecars can receive unknown fields. The surrounding tests explicitly cover a future-message scenario to ensure unknown fields are not dumped by the current sanitizer path.

The proto is generated and should not be hand-edited casually. A local edit that changes field numbers, package names, extension numbers, or option names can invalidate generated bindings and test assumptions.

## Test Signals
Useful test signals include redaction of `CreateVolumeRequest.secrets`, preservation of non-secret fields, recursive handling of topology and volume capability submessages, enum rendering for known enum values, numeric rendering for unknown enum values, JSON output stability, and non-mutation of the original message.

For this fixture specifically, tests should continue to verify that fields marked with `csi_secret` are stripped regardless of field name and that unmarked fields remain visible. Regeneration signals include `protoc` success with custom options retained, `go test ./sources/control-plane/csi-lib-utils/protosanitizer` passing, and expected output strings in `protosanitizer_test.go` remaining aligned with the descriptor names generated from this schema.
