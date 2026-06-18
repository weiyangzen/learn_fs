# Research: sources/cloud-native/buildkit/frontend/gateway/pb/gateway_vtproto.pb.go

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000019`: lines 1-11890, `Docs/researches/chunks/subset-b-000019_research.md`
- `subset-b-000020`: lines 11891-16682, `Docs/researches/chunks/subset-b-000020_research.md`

## Chunk Research

### subset-b-000019: lines 1-11890

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

### subset-b-000020: lines 11891-16682

# sources/cloud-native/buildkit/frontend/gateway/pb/gateway_vtproto.pb.go lines 11891-16682

## Scope

This chunk is generated by `protoc-gen-go-vtproto` for `frontend/gateway/pb/gateway.proto`. It covers the tail of `ResolveSourceHTTPResponse.UnmarshalVT` and then a long sequence of `UnmarshalVT` methods for gateway protocol messages used by BuildKit frontends, filesystem gateway calls, warning reporting, container lifecycle, exec streaming, and blob descriptors.

The implementation is wire-format decoding only. It does not execute BuildKit operations itself; it reconstructs typed Go protobuf messages from bytes, validates protobuf wire shape and bounds, and preserves unknown fields for forward compatibility.

## Purpose

The purpose of these functions is fast vtprotobuf unmarshalling for gateway RPC payloads:

- Convert length-delimited strings, byte slices, nested messages, maps, oneofs, enums, booleans, and integers from protobuf wire bytes into generated Go structs.
- Avoid generic reflection-heavy unmarshalling for most known BuildKit protobuf types by calling nested `UnmarshalVT` methods.
- Retain unrecognized fields in each message's `unknownFields` buffer using `protohelpers.Skip`, so newer senders can interoperate with older receivers.
- Return structured errors on malformed input: wrong wire types, illegal tags, end-group wire types, varint overflow, invalid lengths, and truncated payloads.

## Important APIs, Types, and Functions

Primary functions in this chunk:

- `(*ResolveSourceHTTPRequest).UnmarshalVT`, `(*ChecksumRequest).UnmarshalVT`, `(*ChecksumResponse).UnmarshalVT`, plus the tail of `(*ResolveSourceHTTPResponse).UnmarshalVT`: HTTP source metadata and optional checksum negotiation.
- `(*SolveRequest).UnmarshalVT`, `(*CacheOptionsEntry).UnmarshalVT`, `(*SolveResponse).UnmarshalVT`: gateway solve request/response decoding, including frontend options, cache imports, frontend inputs, evaluation mode, source policies, and result return.
- `(*ReadFileRequest).UnmarshalVT`, `(*FileRange).UnmarshalVT`, `(*ReadFileResponse).UnmarshalVT`, `(*ReadDirRequest).UnmarshalVT`, `(*ReadDirResponse).UnmarshalVT`, `(*StatFileRequest).UnmarshalVT`, `(*StatFileResponse).UnmarshalVT`, `(*EvaluateRequest).UnmarshalVT`, `(*EvaluateResponse).UnmarshalVT`: filesystem and reference evaluation message decoding.
- `(*PingRequest).UnmarshalVT`, `(*PongResponse).UnmarshalVT`: gateway capability/worker ping response decoding.
- `(*WarnRequest).UnmarshalVT`, `(*WarnResponse).UnmarshalVT`: frontend warning payloads with digest, level, short/detail bytes, URL, source info, and source ranges.
- `(*NewContainerRequest).UnmarshalVT`, `(*NewContainerResponse).UnmarshalVT`, `(*ReleaseContainerRequest).UnmarshalVT`, `(*ReleaseContainerResponse).UnmarshalVT`: container allocation/release control messages.
- `(*ExecMessage).UnmarshalVT`, `(*InitMessage).UnmarshalVT`, `(*ExitMessage).UnmarshalVT`, `(*StartedMessage).UnmarshalVT`, `(*DoneMessage).UnmarshalVT`, `(*FdMessage).UnmarshalVT`, `(*ResizeMessage).UnmarshalVT`, `(*SignalMessage).UnmarshalVT`: interactive process protocol messages. `ExecMessage` decodes a protobuf oneof into one of init, file, resize, started, exit, done, or signal wrappers.
- `(*Blob).UnmarshalVT`, `(*Descriptor).UnmarshalVT`: inline content blob and OCI-like descriptor decoding.

Key referenced message families:

- BuildKit solver protobufs imported as `pb`: `Definition`, `Mount`, `Platform`, `WorkerConstraints`, `HostIP`, `Meta`, `SecretEnv`, `SourceInfo`, and `Range`.
- Source policy protobufs imported as `pb1`: `Policy`.
- API capability protobufs imported as `pb2`: `APICap`.
- API type protobufs imported as `types1`: `WorkerRecord`.
- fsutil protobufs imported as `types`: `Stat`.
- `timestamppb.Timestamp`, decoded through vtprotobuf's timestamp wrapper.
- `google.rpc.status.Status`, decoded through `UnmarshalVT` when available and falling back to `proto.Unmarshal`.

## Control Flow

Each `UnmarshalVT` follows the same generated state machine:

1. Store `l := len(dAtA)` and scan with `iNdEx`.
2. For each field, read the key varint into `wire`; derive `fieldNum := int32(wire >> 3)` and `wireType := int(wire & 0x7)`.
3. Reject end-group wire type `4` and non-positive field numbers.
4. Switch on `fieldNum`.
5. For known fields, assert the expected wire type and decode the payload.
6. For unknown fields, reset to `preIndex`, skip the whole encoded field with `protohelpers.Skip`, append the skipped bytes to `m.unknownFields`, and continue.
7. After the loop, reject index overrun with `io.ErrUnexpectedEOF`.

Length-delimited fields always read a varint length, check negative and overflow cases, compute `postIndex`, and ensure it does not exceed the message boundary. Nested messages allocate the destination if nil and then call `UnmarshalVT` on the slice for that submessage.

Map fields are decoded by parsing each length-delimited map entry into local `mapkey` and `mapvalue` variables, skipping unknown entry fields, and assigning after the entry loop. This appears in `SolveRequest.FrontendOpt`, `SolveRequest.FrontendInputs`, `CacheOptionsEntry.Attrs`, and `Descriptor.Annotations`.

Repeated message fields append a new concrete element and unmarshal into the newly appended slot. Repeated byte fields differ by shape: singular byte fields such as `ReadFileResponse.Data`, `FdMessage.Data`, and `Blob.Data` reuse the destination slice with `append(dst[:0], ...)`, while repeated byte slices such as `WarnRequest.Detail` allocate and copy a new slice per entry.

`InitMessage.Fds` supports both unpacked varint form and packed length-delimited form. For packed form it first counts element terminators to preallocate when possible, then appends each decoded `uint32`.

`ExecMessage` implements oneof decoding by checking whether the current oneof already has the same concrete wrapper. If it does, the nested message is unmarshalled into the existing wrapper value. Otherwise, a new nested message is allocated, decoded, and wrapped in the corresponding oneof struct. In ordinary protobuf "last one wins" streams, later oneof fields of a different type replace earlier oneof values.

## State and Persistence Behavior

These functions mutate only the receiver object and do not write external state. Persistence-relevant behavior is about in-memory decoded message state:

- Unknown fields are appended to `m.unknownFields` rather than discarded.
- Repeated fields append to existing slices, so callers reusing a receiver without clearing it may accumulate repeated values across unmarshalling calls.
- Some singular byte fields overwrite by reusing existing capacity with `append(slice[:0], ...)`; if a field appears multiple times, the last decoded instance replaces prior bytes for that field.
- Singular nested messages reuse an existing pointed-to object when non-nil, which can preserve previously present subfields if the nested unmarshal merges rather than clears them. This is standard protobuf unmarshal merge behavior and matters when receivers are reused.
- Map fields initialize nil maps but do not clear existing maps; decoded entries overwrite matching keys and leave unrelated previous keys intact on reused receivers.
- Empty marker messages (`EvaluateResponse`, `PingRequest`, `WarnResponse`, `NewContainerResponse`, `ReleaseContainerResponse`, `StartedMessage`, `DoneMessage`) still preserve unknown fields.

No filesystem, database, cache, network, container, or process state is changed by this chunk. The decoded messages are consumed elsewhere by gateway RPC handlers and clients that perform those actions.

## Dependencies and Integration Points

The chunk depends on:

- `protohelpers` for skip and canonical generated errors such as `ErrIntOverflow` and `ErrInvalidLength`.
- `io.ErrUnexpectedEOF` and `fmt.Errorf` for malformed payload reporting.
- vtprotobuf-generated `UnmarshalVT` methods on nested BuildKit protobuf packages.
- `google.golang.org/protobuf/proto` as a fallback for `status.Status` when a vtprotobuf method is not available.

Integration points:

- Gateway solve APIs receive `SolveRequest` and return `SolveResponse`, tying frontend selection, LLB definitions, cache imports, source policies, and results to BuildKit's solver layer.
- Source HTTP resolution integrates checksum requests/responses and timestamps.
- Filesystem gateway APIs decode refs, mount indexes, paths, ranges, directory stats, and file payloads.
- Capability negotiation flows through `PingRequest` and `PongResponse`, including frontend API caps, LLB caps, and worker records.
- Warning APIs feed frontend diagnostics into BuildKit progress/status surfaces.
- Container and exec messages are the serialized control plane for creating gateway containers, starting processes, passing fd data, resizing TTYs, signaling processes, and observing started/exit/done events.
- Blob/descriptor messages represent content transfer metadata and inline data.

## Risks and Edge Cases

- This file is generated. Manual edits are high risk because they can diverge from `gateway.proto` and from vtprotobuf generator invariants.
- Reusing a message instance without resetting it can retain map entries, unknown fields, repeated field entries, and nested-message substate. Callers expecting replacement semantics need to clear receivers before unmarshal.
- Map entry decoding uses default zero values if an entry omits key or value. Malformed or partial-but-valid map entries can write an empty-string key or nil value for message-valued maps.
- The generated code validates byte boundaries aggressively, but very large valid payloads can still allocate large slices, maps, and nested message arrays.
- `ExecMessage` oneof semantics mean later oneof fields can replace earlier different oneof variants; streams with multiple oneof variants in the same message depend on protobuf merge ordering.
- `ExitMessage.Error` has a generic fallback path through `proto.Unmarshal`, so behavior can differ from pure vtprotobuf paths if the status type does not expose `UnmarshalVT`.
- Enum values such as checksum algorithm, network mode, and security mode are decoded numerically without local semantic validation; invalid enum numbers may survive to downstream validation.
- Packed and unpacked repeated varint support for `InitMessage.Fds` is necessary for compatibility, but malformed packed sequences fail only through overflow/truncation checks, not semantic fd validation.

## Test Signals

Useful verification should include:

- Round-trip protobuf tests for every message in this range using both standard `proto.Unmarshal` and `UnmarshalVT`, comparing resulting message equality.
- Fuzz tests against each `UnmarshalVT` for truncated varints, oversized lengths, wrong wire types, end-group wire types, illegal field number zero, and nested-message truncation.
- Compatibility tests for unknown-field preservation: unmarshal bytes containing unknown fields, then marshal and confirm the unknown payload survives as expected.
- Receiver reuse tests for maps, repeated fields, byte slices, nested messages, and `ExecMessage` oneofs to document merge-versus-replace behavior.
- Specific coverage for `SolveRequest` maps and nested `pb.Definition` values, `InitMessage.Fds` packed and unpacked encodings, `WarnRequest.Detail` repeated byte slices, `PongResponse` repeated capability/worker messages, and `Descriptor.Annotations`.
- Negative tests confirming wrong wire types return errors that identify the field and that truncated length-delimited fields return `io.ErrUnexpectedEOF`.
- Integration tests at the gateway RPC layer that exercise solve, read/stat/dir, warning, container, exec, and blob flows using messages decoded by this generated path.
