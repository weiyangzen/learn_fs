# Research: sources/control-plane/csi-lib-utils/protosanitizer/test/csitest/csitest.pb.go

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000374`: lines 1-6213, `Docs/researches/chunks/subset-b-000374_research.md`
- `subset-b-000375`: lines 6214-6494, `Docs/researches/chunks/subset-b-000375_research.md`

## Chunk Research

### subset-b-000374: lines 1-6213

# sources/control-plane/csi-lib-utils/protosanitizer/test/csitest/csitest.pb.go lines 1-6213

## Scope

This chunk covers the generated Go protobuf bindings for the `csitest.v1` test schema from the package header through the first part of `file_csitest_proto_init()`. It includes all top-level enum definitions, all CSI-like request/response message structs, nested oneof wrapper structs, getter methods, raw descriptor data, Go type/dependency tables, and the exporter setup through `file_csitest_proto_msgTypes[43]`.

The requested range ends at line 6213 while the init function is still assigning exporters. Later lines in the same generated file finish exporters for remaining message types, register oneof wrappers, build the final `protoreflect.FileDescriptor`, and nil out descriptor construction tables; that tail is outside this chunk.

## Purpose

`csitest.pb.go` is a generated protobuf fixture used by `protosanitizer` tests. The schema mirrors a subset of the Container Storage Interface (CSI) protobuf API and deliberately adds secret-marking edge cases. Its main purpose is to provide realistic protobuf descriptors and message graphs for sanitizer code that walks messages reflectively and removes fields marked with the CSI secret option.

The file is not hand-written business logic. It supplies:

- Strongly typed Go structs for CSI-style identity, controller, and node request/response messages.
- Enum wrappers and descriptor metadata for protobuf reflection.
- Map-entry, repeated-message, nested-message, oneof, wrapper, and timestamp shapes that sanitizer code must handle.
- Secret-like fields whose names alone are insufficient, so tests can verify behavior is based on protobuf field options rather than simple string matching.

## Important APIs, Types, And Functions

Generated enum types:

- `PluginCapability_Service_Type` with `UNKNOWN`, `CONTROLLER_SERVICE`, and `VOLUME_ACCESSIBILITY_CONSTRAINTS`.
- `VolumeCapability_AccessMode_Mode` with CSI access modes such as `SINGLE_NODE_WRITER`, `MULTI_NODE_READER_ONLY`, and `MULTI_NODE_MULTI_WRITER`.
- `ControllerServiceCapability_RPC_Type` with controller feature flags including volume create/delete, publish/unpublish, list, capacity, snapshot, clone, and readonly publish support.
- `VolumeUsage_Unit` with `UNKNOWN`, `BYTES`, and `INODES`.
- `NodeServiceCapability_RPC_Type` with `STAGE_UNSTAGE_VOLUME` and `GET_VOLUME_STATS`.

For each enum, the file defines numeric constants, name/value maps, and generated methods `Enum()`, `String()`, `Descriptor()`, `Type()`, `Number()`, and deprecated `EnumDescriptor()`.

Generated message methods follow the standard `protoc-gen-go` pattern:

- `Reset()` clears the struct and stores message info in `protoimpl.MessageState` when unsafe mode is enabled.
- `String()` delegates to `protoimpl.X.MessageStringOf`.
- `ProtoMessage()` marks the type as a protobuf message.
- `ProtoReflect()` returns a `protoreflect.Message` using `file_csitest_proto_msgTypes`.
- Deprecated `Descriptor()` returns the compressed raw descriptor and the path indexes for the message.
- `Get...()` accessors return zero values on nil receivers and expose struct fields without validation.

Identity-service messages:

- `GetPluginInfoRequest`, `GetPluginInfoResponse`, `GetPluginCapabilitiesRequest`, `GetPluginCapabilitiesResponse`, `PluginCapability`, `PluginCapability_Service`, `ProbeRequest`, and `ProbeResponse`.
- `GetPluginInfoResponse` contains `Name`, `VendorVersion`, and `Manifest map[string]string`.
- `PluginCapability` uses the `Type` oneof with wrapper `PluginCapability_Service_`.
- `ProbeResponse.Ready` uses `*wrapperspb.BoolValue`, which is relevant to reflection traversal because it is a well-known message type.

Controller create-volume and volume model messages:

- `CreateVolumeRequest` includes ordinary CSI fields such as `Name`, `CapacityRange`, `VolumeCapabilities`, `Parameters`, `VolumeContentSource`, and `AccessibilityRequirements`.
- It also includes sanitizer-specific fields: `Seecreets map[string]string`, `NewSecretInt int64`, and `MaybeSecretMap map[int64]*VolumeCapability`.
- `VolumeContentSource` is a oneof container with `Snapshot` and `Volume` alternatives plus `NestedSecretField`.
- `VolumeContentSource_VolumeSource` contains `OneofSecretField`, a secret test case reachable through a oneof branch.
- `VolumeCapability` is another oneof container for block vs mount access and includes `ArraySecret`, a secret test case inside repeated `VolumeCapabilities`.
- `CapacityRange`, `Volume`, `TopologyRequirement`, and `Topology` model capacity, identifiers, volume context, source content, and topology maps.

Controller RPC messages:

- Volume lifecycle: `DeleteVolumeRequest`, `DeleteVolumeResponse`, `ControllerPublishVolumeRequest`, `ControllerPublishVolumeResponse`, `ControllerUnpublishVolumeRequest`, and `ControllerUnpublishVolumeResponse`.
- Validation and listing: `ValidateVolumeCapabilitiesRequest`, `ValidateVolumeCapabilitiesResponse`, nested `ValidateVolumeCapabilitiesResponse_Confirmed`, `ListVolumesRequest`, nested `ListVolumesResponse_Entry`, and `ListVolumesResponse`.
- Capacity and capabilities: `GetCapacityRequest`, `GetCapacityResponse`, `ControllerGetCapabilitiesRequest`, `ControllerGetCapabilitiesResponse`, `ControllerServiceCapability`, and nested `ControllerServiceCapability_RPC`.
- Snapshot lifecycle: `CreateSnapshotRequest`, `CreateSnapshotResponse`, `Snapshot`, `DeleteSnapshotRequest`, `DeleteSnapshotResponse`, `ListSnapshotsRequest`, nested `ListSnapshotsResponse_Entry`, and `ListSnapshotsResponse`.

Node RPC messages:

- Stage/publish flow: `NodeStageVolumeRequest`, `NodeStageVolumeResponse`, `NodeUnstageVolumeRequest`, `NodeUnstageVolumeResponse`, `NodePublishVolumeRequest`, `NodePublishVolumeResponse`, `NodeUnpublishVolumeRequest`, and `NodeUnpublishVolumeResponse`.
- Stats/capabilities/info: `NodeGetVolumeStatsRequest`, `NodeGetVolumeStatsResponse`, `VolumeUsage`, `NodeGetCapabilitiesRequest`, `NodeGetCapabilitiesResponse`, `NodeServiceCapability`, nested `NodeServiceCapability_RPC`, `NodeGetInfoRequest`, and `NodeGetInfoResponse`.

Descriptor and initialization globals in this chunk:

- `File_csitest_proto protoreflect.FileDescriptor` is the public descriptor variable.
- `file_csitest_proto_rawDesc` embeds the serialized `csitest.proto` descriptor, including custom field option bytes such as `0x98, 0x42, 0x01` on secret-marked fields.
- `file_csitest_proto_rawDescOnce` and `file_csitest_proto_rawDescData` implement lazy GZIP compression.
- `file_csitest_proto_rawDescGZIP()` compresses raw descriptor bytes once with `sync.Once`.
- `file_csitest_proto_enumTypes`, `file_csitest_proto_msgTypes`, `file_csitest_proto_goTypes`, and `file_csitest_proto_depIdxs` are the tables consumed by `protoimpl.TypeBuilder`.
- `init()` calls `file_csitest_proto_init()`.
- `file_csitest_proto_init()` is idempotent and starts assigning exporter functions when `protoimpl.UnsafeEnabled` is false.

## Control Flow

There is no application control flow in the usual sense; this is generated model code. Runtime behavior is centered on protobuf reflection and init-time descriptor construction.

Message usage flow:

1. Callers construct or receive one of the generated structs, such as `CreateVolumeRequest`.
2. Generated getters provide nil-safe field access but do not enforce CSI required-field rules or sanitize values.
3. Protobuf APIs call `ProtoReflect()` to obtain a `protoreflect.Message`.
4. Reflection uses `file_csitest_proto_msgTypes` and, after initialization, `File_csitest_proto` to resolve field descriptors, enum descriptors, oneofs, map entries, and custom field options.
5. Sanitizer code can then traverse the message graph by descriptor, not by concrete Go field names.

Enum flow is similarly generated. Enum `String()`, `Descriptor()`, `Type()`, and deprecated `EnumDescriptor()` all route through generated enum tables and the raw descriptor. These are relevant when tests inspect descriptors or marshal values but do not perform any sanitizer-specific logic themselves.

Oneof flow is important for sanitizer coverage:

- `PluginCapability.GetService()` type-asserts `Type` to `*PluginCapability_Service_`.
- `VolumeContentSource.GetSnapshot()` and `GetVolume()` type-assert `Type` to the corresponding wrapper.
- `VolumeCapability.GetBlock()` and `GetMount()` type-assert `AccessType`.
- `ControllerServiceCapability.GetRpc()` and `NodeServiceCapability.GetRpc()` type-assert capability oneofs.

Reflection-based traversal must handle both the outer oneof field and the message value held by the selected wrapper. `VolumeContentSource_VolumeSource.OneofSecretField` is the key secret-bearing case inside a selected oneof branch.

Descriptor initialization flow in this chunk:

1. Package `init()` calls `file_csitest_proto_init()`.
2. The init function returns immediately if `File_csitest_proto` is already non-nil.
3. In safe runtime mode, exporter functions are assigned for message structs so the protobuf runtime can access `state`, `sizeCache`, and `unknownFields`.
4. This chunk ends while exporters are being assigned, specifically after the exporter for `NodeUnpublishVolumeRequest` begins. The final type build happens later in the file.

## State And Persistence Behavior

Each message struct carries generated protobuf runtime state:

- `protoimpl.MessageState` stores message info and runtime bookkeeping.
- `protoimpl.SizeCache` caches encoded sizes.
- `protoimpl.UnknownFields` preserves fields not recognized by this generated code during unmarshalling.

Business fields are ordinary Go values:

- Scalar strings, booleans, integers, and enums are stored directly.
- Repeated fields use slices, for example `[]*VolumeCapability`, `[]*Topology`, and `[]*VolumeUsage`.
- Maps use Go maps, for example `map[string]string` and `map[int64]*VolumeCapability`.
- Nested and well-known messages are pointers.
- Oneofs are interface fields whose dynamic concrete value is a generated wrapper struct.

The getters do not deep-copy maps or slices. Callers receive the same map or slice stored in the message, so tests and sanitizer implementations must be aware that mutations through returned values mutate the original message. A sanitizer that edits messages in place will persist those edits in the same Go object.

Descriptor state is process-global:

- `File_csitest_proto` is initialized once per process.
- `file_csitest_proto_rawDescData` is compressed lazily and cached with `sync.Once`.
- `file_csitest_proto_msgTypes` and related tables persist until the tail of `file_csitest_proto_init()` builds the descriptor and clears construction-only globals.

There is no file-system persistence, database state, networking, goroutine management, or explicit synchronization beyond `sync.Once` for descriptor compression.

## Dependencies And Integration Points

Direct imports:

- Blank import `github.com/container-storage-interface/spec/lib/go/csi` keeps the CSI Go package linked because the proto imports `csi.proto` and uses CSI custom options.
- `google.golang.org/protobuf/reflect/protoreflect` supplies reflection interfaces.
- `google.golang.org/protobuf/runtime/protoimpl` supplies generated-code internals.
- Blank import `google.golang.org/protobuf/types/descriptorpb` supports descriptor option linkage.
- `google.golang.org/protobuf/types/known/timestamppb` backs `Snapshot.CreationTime`.
- `google.golang.org/protobuf/types/known/wrapperspb` backs `ProbeResponse.Ready`.
- `reflect` and `sync` are used by generated descriptor/type construction.

Integration with `protosanitizer` is descriptor-driven. The fields most likely used as sanitizer test signals include:

- Conventional CSI secret maps: `DeleteVolumeRequest.Secrets`, `ControllerPublishVolumeRequest.Secrets`, `ControllerUnpublishVolumeRequest.Secrets`, `ValidateVolumeCapabilitiesRequest.Secrets`, `CreateSnapshotRequest.Secrets`, `DeleteSnapshotRequest.Secrets`, `NodeStageVolumeRequest.Secrets`, and `NodePublishVolumeRequest.Secrets`.
- Renamed secret field: `CreateVolumeRequest.Seecreets`, intended to prove that the sanitizer follows the `csi_secret` option rather than the literal field name `secrets`.
- Non-map secret field: `CreateVolumeRequest.NewSecretInt`, proving secret handling is not limited to `map<string,string>`.
- Nested secret field: `VolumeContentSource.NestedSecretField`.
- Oneof-contained secret field: `VolumeContentSource_VolumeSource.OneofSecretField`.
- Repeated-message secret field: `VolumeCapability.ArraySecret`, reachable through arrays such as `CreateVolumeRequest.VolumeCapabilities`.
- Map-value recursion case: `CreateVolumeRequest.MaybeSecretMap map[int64]*VolumeCapability`, where sanitizer traversal must enter map values and then remove `VolumeCapability.ArraySecret`.

The generated raw descriptor includes service definitions for `Identity`, `Controller`, and `Node`. Although this file does not generate gRPC client/server stubs, the descriptor dependency indexes map RPC inputs and outputs, allowing reflection users to associate methods with message types.

## Risks And Edge Cases

The biggest risk for consumers is treating generated field names as the source of truth. This fixture intentionally defeats name-only logic with `Seecreets`, `NewSecretInt`, `NestedSecretField`, `OneofSecretField`, `ArraySecret`, and `MaybeSecretMap`. Sanitizer code must inspect protobuf field options from descriptors and recurse through message shapes.

Oneof traversal is easy to miss. A sanitizer that only iterates ordinary message fields may strip `VolumeContentSource.NestedSecretField` but miss `VolumeContentSource_VolumeSource.OneofSecretField` because it is behind a selected oneof wrapper.

Map traversal has two separate cases. Secret maps whose field is marked secret should be cleared as whole fields. Maps whose values are messages, such as `MaybeSecretMap`, require recursion into each value even when the map field itself is not the sensitive value. A sanitizer that treats maps as scalar containers will miss `VolumeCapability.ArraySecret`.

Repeated-message traversal is also required. `VolumeCapabilities []*VolumeCapability` can carry `ArraySecret` inside each element, and the same `VolumeCapability` type appears under create, validate, capacity, stage, publish, and confirmed-response paths.

Nil handling matters. Generated getters are nil-safe, but reflection-based mutation usually works on `protoreflect.Message` values and must handle nil message pointers, unset oneofs, nil map values, and nil repeated elements without panics.

Unknown fields are preserved by generated messages. A sanitizer that only clears known fields will not remove unknown encoded fields that happen to contain sensitive data from future schemas. That may be acceptable for this fixture, but it is a security-relevant boundary to document for production sanitization.

Generated-code boundaries are fragile for manual edits. This file was generated by `protoc-gen-go v1.34.2` and `protoc v4.25.2`; changes should generally be made in `csitest.proto` and regenerated. Hand-editing `csitest.pb.go` risks desynchronizing raw descriptors, Go struct tags, type indexes, and oneof wrapper tables.

The requested chunk boundary cuts through `file_csitest_proto_init()`. Research for this chunk should not assume the visible exporter assignments are the complete initializer; later lines finish exporters, oneof wrapper registration, and descriptor building.

## Test Signals

Sanitizer tests using this fixture should verify that secret detection is option-based:

- `CreateVolumeRequest.Seecreets` is stripped even though it is misspelled.
- `CreateVolumeRequest.NewSecretInt` is stripped even though it is not a map.
- Ordinary non-secret maps such as `Parameters`, `VolumeContext`, `PublishContext`, `Manifest`, and `Topology.Segments` remain intact.

Traversal-depth tests should cover:

- `CreateVolumeRequest.VolumeContentSource.NestedSecretField`.
- `CreateVolumeRequest.VolumeContentSource.Volume.OneofSecretField`.
- `CreateVolumeRequest.VolumeCapabilities[*].ArraySecret`.
- `CreateVolumeRequest.MaybeSecretMap[*].ArraySecret`.
- `ValidateVolumeCapabilitiesResponse.Confirmed.VolumeCapabilities[*].ArraySecret`.

CSI request coverage should include every conventional `Secrets` map in controller and node request messages:

- Volume delete, controller publish, controller unpublish, validate volume capabilities.
- Snapshot create and delete.
- Node stage and node publish.

Reflection tests should assert that `File_csitest_proto` exposes the expected package `csitest.v1`, message descriptors, enum descriptors, and service method input/output mappings after init. They should also verify that raw descriptor compression is stable through repeated `Descriptor()` and `ProtoReflect()` calls.

Mutation tests should distinguish in-place and copy behavior. Because generated getters expose underlying maps and slices, tests should confirm whether sanitizer APIs mutate the original message, clone before sanitizing, or preserve caller-owned structures by contract.

Compatibility tests should build under both unsafe and safe protobuf runtime modes where feasible. In safe mode, exporter functions assigned by `file_csitest_proto_init()` are used to expose message internals to `protoimpl`; in unsafe mode, direct message-state access is used instead.

### subset-b-000375: lines 6214-6494

# sources/control-plane/csi-lib-utils/protosanitizer/test/csitest/csitest.pb.go lines 6214-6494

## Purpose

This chunk is the final section of the generated `csitest.pb.go` protobuf descriptor initialization for the `csitest.v1` package. It belongs to `file_csitest_proto_init`, the package-level initializer that wires generated Go message types, enum types, oneof wrapper metadata, dependency indexes, and raw descriptor data into `google.golang.org/protobuf/runtime/protoimpl.TypeBuilder`.

The immediate purpose of lines 6214-6494 is to finish registering message exporters for the latter CSI message types when `protoimpl.UnsafeEnabled` is false, declare the generated oneof wrapper implementations for selected messages, build the runtime `protoreflect.FileDescriptor`, assign it to `File_csitest_proto`, and release temporary descriptor construction state.

## Important APIs, Types, and Functions

- `file_csitest_proto_init()` is the central generated initializer. Earlier in the function it exits early when `File_csitest_proto` is already populated, then conditionally installs exporter callbacks when unsafe protobuf reflection is unavailable.
- `file_csitest_proto_msgTypes` is a `[]protoimpl.MessageInfo` with 90 entries. In this chunk, entries for node-side CSI messages and selected nested messages are completed.
- Exporter callbacks expose internal generated-message fields by index:
  - index `0` returns `&v.state`
  - index `1` returns `&v.sizeCache`
  - index `2` returns `&v.unknownFields`
  - any other index returns `nil`
- Node-side message registrations covered directly here include:
  - `NodeUnpublishVolumeResponse`
  - `NodeGetVolumeStatsRequest`
  - `NodeGetVolumeStatsResponse`
  - `VolumeUsage`
  - `NodeGetCapabilitiesRequest`
  - `NodeGetCapabilitiesResponse`
  - `NodeServiceCapability`
  - `NodeGetInfoRequest`
  - `NodeGetInfoResponse`
  - nested `NodeServiceCapability_RPC`
- The chunk also registers exporters for nested or supporting messages used by earlier schema areas, including `PluginCapability_Service`, `VolumeContentSource_*`, `VolumeCapability_*`, `ValidateVolumeCapabilitiesResponse_Confirmed`, list response entries, and `ControllerServiceCapability_RPC`.
- `OneofWrappers` metadata is set for:
  - `PluginCapability`: `PluginCapability_Service_`
  - `VolumeContentSource`: snapshot or volume source wrappers
  - `VolumeCapability`: block or mount wrappers
  - `ControllerServiceCapability`: RPC wrapper
  - `NodeServiceCapability`: RPC wrapper
- `protoimpl.TypeBuilder` is invoked with:
  - `GoPackagePath` from `reflect.TypeOf(x{}).PkgPath()`
  - `RawDescriptor` from `file_csitest_proto_rawDesc`
  - `NumEnums: 5`
  - `NumMessages: 90`
  - `NumServices: 3`
  - `GoTypes`, `DependencyIndexes`, `EnumInfos`, and `MessageInfos`

## Control Flow

This chunk executes only inside `file_csitest_proto_init` and only after the early guard has established that `File_csitest_proto` has not already been built. The exporter assignments in this chunk are inside the `if !protoimpl.UnsafeEnabled` block, so they are used by safe protobuf reflection paths that cannot directly access generated message internals.

After exporter registration, the function configures oneof wrapper slices unconditionally. This is required so the protobuf runtime can correctly encode, decode, reflect, and type-switch generated oneof fields such as `NodeServiceCapability.Type`.

The final control-flow step constructs a local zero-sized `x` type for package path discovery, calls `protoimpl.TypeBuilder.Build()`, stores the resulting file descriptor in `File_csitest_proto`, and clears `file_csitest_proto_rawDesc`, `file_csitest_proto_goTypes`, and `file_csitest_proto_depIdxs`.

## State and Persistence Behavior

The only persistent state established by this chunk is generated protobuf runtime metadata:

- `File_csitest_proto` becomes the canonical in-process `protoreflect.FileDescriptor` for `csitest.proto`.
- `file_csitest_proto_msgTypes` retains message info, exporter callbacks where needed, and oneof wrapper metadata.
- Temporary construction slices and raw descriptor data are nulled after `Build()` to reduce retained memory.

There is no external persistence, filesystem I/O, networking, or business-state mutation. Message instance state remains in the standard generated fields `protoimpl.MessageState`, `protoimpl.SizeCache`, and `protoimpl.UnknownFields`; this chunk only teaches the protobuf runtime how to reach those fields in safe mode.

## Dependencies and Integration Points

This generated file depends on the Go protobuf runtime packages `protoreflect` and `protoimpl`, plus standard `reflect` and `sync` support used elsewhere in descriptor construction. Earlier type definitions also reference CSI-compatible schema concepts and protobuf well-known types such as `wrapperspb.BoolValue` and `timestamppb.Timestamp`.

Integration points in this chunk are reflection-oriented:

- `NodeGetCapabilitiesResponse` depends on `NodeServiceCapability`, whose oneof currently supports `NodeServiceCapability_Rpc`.
- `NodeServiceCapability_RPC` uses `NodeServiceCapability_RPC_Type`, including `STAGE_UNSTAGE_VOLUME` and `GET_VOLUME_STATS`.
- `NodeGetInfoResponse` links to `Topology` through `accessible_topology`, and the dependency index table maps that relationship into the descriptor.
- Service dependency indexes earlier in the file map the Node service RPCs `NodeGetCapabilities` and `NodeGetInfo` to these message types; this chunk finalizes the descriptor that gRPC/protobuf reflection consumers use.

Because this file lives under `protosanitizer/test/csitest`, its practical integration role is test support for protobuf sanitizer behavior against CSI-like generated messages, including nested messages, maps, oneofs, unknown fields, and node service capability structures.

## Risks and Edge Cases

- This is generated code; hand edits are high risk because message indexes, dependency indexes, exporter indexes, and oneof wrapper lists must stay synchronized with the raw descriptor and the generated structs.
- Incorrect exporter wiring would mostly affect safe-mode protobuf reflection, serialization, size calculation, and unknown-field handling. Unsafe mode could hide such errors during local testing if it is enabled.
- Missing or incorrect `OneofWrappers` entries would break correct handling of oneof fields such as `NodeServiceCapability.Type`, potentially causing marshal/unmarshal or reflective access failures.
- The chunk clears descriptor construction globals after build. Code that incorrectly expected `file_csitest_proto_rawDesc`, `file_csitest_proto_goTypes`, or `file_csitest_proto_depIdxs` to remain populated after initialization would fail, but generated protobuf consumers should use `File_csitest_proto` and message descriptors instead.
- Schema-level validation is not enforced here. For example, comments state that `NodeGetInfoResponse.NodeId` is required and `MaxVolumesPerNode` must not be negative, but generated proto3 structs and this initializer do not enforce those constraints.

## Test Signals

Useful validation signals for this chunk are generated-code and protobuf-runtime oriented:

- Package tests that marshal, unmarshal, reflect, and sanitize `NodeGetCapabilitiesResponse`, `NodeServiceCapability`, `NodeGetInfoResponse`, and `NodeGetVolumeStatsResponse` exercise the metadata finalized here.
- Oneof coverage should include `NodeServiceCapability{Type: &NodeServiceCapability_Rpc{...}}` to prove the wrapper registration is correct.
- Reflection tests can verify that `File_csitest_proto` exposes 5 enums, 90 messages, and 3 services after package initialization.
- Safe-mode protobuf runtime coverage is especially relevant because exporter callbacks are skipped when `protoimpl.UnsafeEnabled` is true.
- Regeneration from `csitest.proto` with the pinned generator versions is the strongest guard against drift, because this chunk is mechanically tied to descriptor indexes and generated struct layout.
