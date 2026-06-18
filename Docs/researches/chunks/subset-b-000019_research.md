# sources/cloud-native/buildkit/frontend/gateway/pb/gateway_vtproto.pb.go lines 1-11890

## Scope

This chunk covers the first 11,890 lines of `gateway_vtproto.pb.go`, a generated `protoc-gen-go-vtproto` companion for `github.com/moby/buildkit/frontend/gateway/pb/gateway.proto`. The covered span contains the vtprotobuf helpers for all gateway protobuf message types through cloning, proto-message cloning adapters, equality, marshaling, size calculation, and the beginning of unmarshaling. The chunk ends inside `ResolveSourceHTTPResponse.UnmarshalVT`, after it starts decoding the `Filename` field; later fields and the rest of the file are outside this chunk.

## Purpose

The file supplies high-performance protobuf operations for BuildKit gateway frontend messages without replacing the canonical generated types in `gateway.pb.go`. It adds methods that generated/runtime code can call directly:

- `CloneVT` and `CloneMessageVT` for deep copies.
- `EqualVT` and `EqualMessageVT` for semantic equality that includes unknown fields.
- `MarshalVT`, `MarshalToVT`, and `MarshalToSizedBufferVT` for size-precomputed wire encoding.
- `SizeVT` for exact protobuf wire size calculation.
- `UnmarshalVT` for hand-written wire decoding and unknown-field retention.

These methods are attached to the message types generated in `gateway.pb.go`, so this file is operational glue for the gateway gRPC protocol rather than a separate domain model.

## Important APIs And Types

The covered methods apply to the gateway protocol's result, solve, source metadata, filesystem, warning, container, exec, attestation, and descriptor messages:

- Result/reference messages: `Result`, `Result_RefDeprecated`, `Result_RefsDeprecated`, `Result_Ref`, `Result_Refs`, `RefMapDeprecated`, `Ref`, `RefMap`.
- Attestation messages: `Attestations`, `Attestation`, `InTotoSubject`, `AttestationChain`, `Blob`, `Descriptor`.
- Gateway lifecycle messages: `ReturnRequest`, `ReturnResponse`, `InputsRequest`, `InputsResponse`, `SolveRequest`, `SolveResponse`, `PingRequest`, `PongResponse`, `WarnRequest`, `WarnResponse`.
- Source resolution messages: `ResolveImageConfigRequest`, `ResolveImageConfigResponse`, `ResolveSourceMetaRequest`, `ResolveSourceMetaResponse`, `ResolveSourceImageRequest`, `ResolveSourceImageResponse`, `ResolveSourceGitRequest`, `ResolveSourceGitResponse`, and the first part of `ResolveSourceHTTPResponse`.
- Filesystem and evaluation messages: `ReadFileRequest`, `FileRange`, `ReadFileResponse`, `ReadDirRequest`, `ReadDirResponse`, `StatFileRequest`, `StatFileResponse`, `EvaluateRequest`, `EvaluateResponse`.
- Container execution messages: `NewContainerRequest`, `NewContainerResponse`, `ReleaseContainerRequest`, `ReleaseContainerResponse`, `ExecMessage` and all oneof wrappers, `InitMessage`, `ExitMessage`, `StartedMessage`, `DoneMessage`, `FdMessage`, `ResizeMessage`, `SignalMessage`.

The imports show the integration surface: BuildKit solver protobufs (`solver/pb`), source policy protobufs, API capability protobufs, worker records, fsutil stat types, gRPC status, standard protobuf runtime, vtprotobuf helpers, vtprotobuf timestamp helpers, and `io`/`fmt` for parse errors.

## Clone Behavior

`CloneVT` methods allocate a new message, copy scalar fields, deep-copy byte slices and string slices, duplicate maps, recursively clone nested protobuf messages, and copy `unknownFields`. For external messages, such as `status.Status` and `types.Stat`, the code checks for a `CloneVT` method and falls back to `proto.Clone` when needed.

Oneof wrappers implement typed `CloneVT` methods returning the relevant oneof interface, such as `isResult_Result` or `isExecMessage_Input`. The parent `Result` and `ExecMessage` clones use type assertions to call the wrapper clone. This assumes generated oneof values are one of the vtproto-generated wrapper types; manually installed custom implementations of the same oneof interface would panic if they do not implement the expected vtproto method.

Nil receiver handling is consistent for top-level messages: `nil.CloneVT()` returns a typed nil pointer, and `CloneMessageVT` simply wraps `CloneVT` for the `proto.Message` interface.

## Equality Behavior

`EqualVT` methods compare pointer identity first, then nilness, then field content. The equality code compares:

- Scalars directly.
- Byte slices through string conversion.
- Maps by length, key presence, and value comparison.
- Slices by length and index-preserving element comparison.
- Nested vtproto-capable messages by their `EqualVT` methods.
- External protobufs by `EqualVT` when implemented, otherwise by `proto.Equal`.
- Unknown fields by exact byte sequence equality.

For many nested pointer fields, nil is normalized to an empty message for comparison. For example, when a repeated element or map value pointer differs, nil is replaced with an empty message before calling `EqualVT`. This matches common protobuf semantics but means equality can treat nil nested messages and explicit empty nested messages as equivalent in several places.

Oneof equality is stricter about wrapper type: a `Result_Ref` is not equal to a `Result_RefDeprecated`, and an `ExecMessage_File` is not equal to another oneof arm even if nested wire payloads were otherwise empty.

## Marshal Control Flow

`MarshalVT` allocates exactly `SizeVT()` bytes and delegates to `MarshalToSizedBufferVT`. `MarshalToVT` assumes the supplied buffer has enough room for `SizeVT()` bytes and slices it to that size. `MarshalToSizedBufferVT` writes protobuf wire data from the end of the buffer backward and returns `len(dAtA) - i`.

Important encoding patterns:

- Unknown fields are copied first into the end of the reverse buffer so they appear at the end of the final wire output.
- Repeated fields are iterated backward to preserve wire order after reverse-buffer encoding.
- Map fields are emitted by ranging over Go maps, so map-entry wire order is intentionally nondeterministic.
- Oneof wrapper marshalers emit the correct field tags for each arm and encode a zero-length nested message when the wrapper's nested pointer is nil.
- Packed repeated numeric fields appear in `InitMessage.Fds`, where the code computes the packed byte size, writes varints into the packed segment, then prefixes length and tag.
- External protobuf fields use `MarshalToSizedBufferVT` when available and fall back to `proto.Marshal`.

The methods skip default-valued scalar and empty length-delimited fields, except where a nil oneof wrapper nested pointer is represented as a zero-length message. Boolean fields such as `Tty`, `NoConfig`, `AttestationChain`, and `ReturnObject` are emitted only when true.

## Size Calculation

`SizeVT` mirrors the marshal logic and is required for correctness of `MarshalVT` and `MarshalToVT`. It sums field tags, length prefixes, varint sizes, nested message sizes, map-entry envelope sizes, repeated element sizes, and `len(m.unknownFields)`. For external protobufs it uses `SizeVT` when implemented and otherwise `proto.Size`.

Size calculation has the same nondeterministic map traversal as marshaling, but because map order does not affect total size, only output byte order is nondeterministic. The calculations for oneof wrapper nil nested pointers add three bytes for an empty length-delimited oneof field.

## Unmarshal Control Flow

The covered `UnmarshalVT` implementations all follow the same parser loop:

1. Read a protobuf wire varint into `wire`.
2. Derive `fieldNum` and `wireType`.
3. Reject end-group wire types and illegal nonpositive tags.
4. Decode the known field according to expected wire type.
5. For unknown fields, reset to `preIndex`, call `protohelpers.Skip`, append raw bytes to `unknownFields`, and advance.
6. Return `protohelpers.ErrIntOverflow`, `protohelpers.ErrInvalidLength`, or `io.ErrUnexpectedEOF` for malformed lengths and truncated input.

The chunk covers full unmarshallers for `Result` through `ResolveSourceGitResponse`, and the start of `ResolveSourceHTTPResponse.UnmarshalVT`. These unmarshallers allocate nested messages lazily, append repeated fields, initialize maps before assignment, and preserve unknown fields exactly. Byte fields generally reuse destination capacity with `append(m.Field[:0], incoming...)` and then force an empty non-nil slice when the decoded bytes are zero-length.

Map decoding is inlined per map field. Each map entry has temporary `mapkey` and `mapvalue` variables, decodes field 1 and field 2 inside the entry boundary, skips unknown entry fields, and assigns `m.Map[mapkey] = mapvalue` after the entry loop. Message-valued maps allocate the value and call its `UnmarshalVT`.

Oneof decoding for `Result` reuses the existing wrapper when the same oneof arm is already present; otherwise it allocates a new nested message and installs the corresponding wrapper. The `ExecMessage` unmarshaller itself starts later in the file and is outside this chunk, but the clone/equality/marshal/size support for all of its arms is covered here.

## State And Persistence

There is no application state, disk state, network IO, or persistence in this file. The only mutable state is in-memory protobuf message content. The file preserves forward-compatibility state through each message's `unknownFields`, and clone/equality/marshal/size/unmarshal all account for those unknown bytes.

Because this is generated code, its durable source of truth is `gateway.proto` plus the vtprotobuf generator and version noted in the header. Manual edits would be overwritten by regeneration and are not a stable customization point.

## Dependencies And Integration Points

This code is tightly coupled to:

- The concrete message struct layout and oneof interfaces generated in `gateway.pb.go`.
- vtprotobuf's `protohelpers` for reverse varint encoding, size math, skipping unknown fields, and canonical parse errors.
- vtprotobuf timestamp helpers for `ResolveSourceHTTPResponse.LastModified`, accessed through conversions between `google.golang.org/protobuf/types/known/timestamppb.Timestamp` and the vtprotobuf timestamp type.
- BuildKit solver/source-policy/API-capability generated messages that provide their own `CloneVT`, `EqualVT`, `MarshalToSizedBufferVT`, `SizeVT`, and `UnmarshalVT` methods.
- Generic protobuf runtime fallback APIs for external types that may not implement vtproto helpers.

The gateway frontend gRPC implementation can use these methods through protobuf interfaces for faster clone/marshal/equality/unmarshal paths. Any changes to field numbers, oneof arms, field types, or unknown-field representation in `gateway.pb.go` require this file to be regenerated in lockstep.

## Risks And Edge Cases

- Generated code must not be hand edited; drift from `gateway.proto` or `gateway.pb.go` would corrupt wire compatibility.
- Map marshaling is nondeterministic because Go map iteration order is nondeterministic. Tests should avoid comparing exact wire bytes for messages with maps unless deterministic marshaling is explicitly handled elsewhere.
- Several parent methods assert that oneof wrapper values implement vtproto helper interfaces. Custom oneof implementations could panic; normal generated wrappers are safe.
- Equality includes exact unknown-field byte order, so two messages that are semantically equivalent at the known-field level can compare unequal if unknown fields differ in ordering or encoding.
- Nil and empty nested messages are often treated as equal, while nil and empty byte slices can both marshal to no field but may be normalized differently after unmarshal.
- `MarshalToVT` slices the caller's buffer to `SizeVT()` without checking capacity itself; callers must provide a buffer large enough.
- Unmarshal methods append repeated fields instead of clearing them first, so unmarshalling into a reused nonzero message merges/appends protobuf data rather than replacing the whole object.
- The assigned chunk ends mid-function at line 11890; final per-file analysis must merge this with later chunk coverage before drawing conclusions about the complete unmarshal set.

## Test Signals

Useful validation signals for this generated file include:

- Regeneration check: running the repository's protobuf/vtprotobuf generation should produce no diff.
- Round trip tests: for each gateway message, `MarshalVT` followed by `UnmarshalVT` should preserve `EqualVT`, including nested messages, oneofs, maps, repeated fields, and unknown fields.
- Compatibility tests: `proto.Marshal`/`proto.Unmarshal` and `MarshalVT`/`UnmarshalVT` should interoperate for the same message types.
- Clone tests: mutating maps, byte slices, repeated nested messages, and unknown fields on an original after `CloneVT` should not affect the clone.
- Error-path fuzzing: malformed varints, negative/overflowing lengths, wrong wire types, truncated messages, and unknown fields should return the expected `protohelpers` or `io` errors without panics.
- Map-order-aware tests: assertions should compare decoded messages or use `EqualVT`, not raw bytes, for messages containing maps.
