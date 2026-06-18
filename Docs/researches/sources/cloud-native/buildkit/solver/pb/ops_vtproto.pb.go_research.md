# Research: sources/cloud-native/buildkit/solver/pb/ops_vtproto.pb.go

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000026`: lines 1-12302, `Docs/researches/chunks/subset-b-000026_research.md`
- `subset-b-000027`: lines 12303-15648, `Docs/researches/chunks/subset-b-000027_research.md`

## Chunk Research

### subset-b-000026: lines 1-12302

# sources/cloud-native/buildkit/solver/pb/ops_vtproto.pb.go research chunk subset-b-000026

Source range: `sources/cloud-native/buildkit/solver/pb/ops_vtproto.pb.go` lines 1-12302.

## Purpose

This chunk is generated Go support code for BuildKit solver protobuf messages defined by `github.com/moby/buildkit/solver/pb/ops.proto`. It is emitted by `protoc-gen-go-vtproto` and adds vtprotobuf fast paths to the message types declared elsewhere in the same `pb` package. The range covers deep cloning, `proto.Message` clone adapters, semantic equality, vtprotobuf marshaling, size calculation, and unmarshaling through the start of `ExportCache.UnmarshalVT`.

The code is performance infrastructure for BuildKit LLB operation graphs. The represented messages model solver operations such as `Op`, `ExecOp`, `SourceOp`, `BuildOp`, `FileOp`, `MergeOp`, `DiffOp`, and related metadata. The methods here let those structures be copied, compared, serialized, and parsed without relying only on reflective protobuf paths.

## Important APIs, Types, And Functions

- `CloneVT` methods deep-copy every covered protobuf message type. They allocate new messages, copy scalar fields, clone nested message pointers, duplicate slices, duplicate maps, copy byte slices, and preserve `unknownFields`.
- `CloneMessageVT` methods adapt typed `CloneVT` output to `google.golang.org/protobuf/proto.Message` for messages that need generic proto integration.
- oneof wrapper clone methods cover `Op_Exec`, `Op_Source`, `Op_File`, `Op_Build`, `Op_Merge`, `Op_Diff`, `Op_Passthrough`, `FileAction_Copy`, `FileAction_Mkfile`, `FileAction_Mkdir`, `FileAction_Rm`, `FileAction_Symlink`, `UserOpt_ByName`, and `UserOpt_ByID`.
- `EqualVT` methods implement field-by-field equality, including unknown field bytes. They compare slices in order, compare maps by key/value membership, dispatch oneof equality through wrapper-specific interfaces, and treat nil nested messages carefully.
- `EqualMessageVT` methods bridge typed equality to generic `proto.Message` equality by type-asserting the peer message before calling `EqualVT`.
- `MarshalVT`, `MarshalToVT`, and `MarshalToSizedBufferVT` methods encode messages into protobuf wire format using vtprotobuf reverse-buffer encoding. The public `MarshalVT` allocates `SizeVT()` bytes; `MarshalToVT` writes into a caller buffer; `MarshalToSizedBufferVT` performs the actual reverse write.
- `SizeVT` methods calculate exact encoded size for each covered message and must match the wire fields emitted by `MarshalToSizedBufferVT`.
- `UnmarshalVT` methods parse protobuf wire data into existing message receivers. This chunk includes unmarshaling for `Op`, `Platform`, `Input`, `ExecOp`, `Meta`, `HostIP`, `Ulimit`, `SecretEnv`, `CDIDevice`, `Mount`, `TmpfsOpt`, `CacheOpt`, `SecretOpt`, `SSHOpt`, `SourceOp`, `BuildOp`, `BuildInput`, `OpMetadata`, `Source`, `Locations`, `SourceInfo`, `Location`, `Range`, `Position`, and the beginning of `ExportCache`.

The covered data model includes platform targeting (`Platform`), graph edges (`Input`, `BuildInput`, diff/merge inputs), execution metadata (`Meta`, `Mount`, `SecretEnv`, `CDIDevice`, `Ulimit`, `ProxyEnv`, `LinuxResources`, `WorkerConstraints`), source locations (`Source`, `Locations`, `SourceInfo`, `Location`, `Range`, `Position`), file actions (`FileOp`, `FileAction*`, `ChownOpt`, `UserOpt`, `NamedUserOpt`), and operation metadata (`OpMetadata`, `ExportCache`, `ProgressGroup`).

## Control Flow

Clone flow is uniform: nil receivers return nil typed pointers; non-nil receivers allocate a fresh message; scalar fields are copied directly; pointer fields call their own `CloneVT`; slices and maps allocate new containers; oneofs dispatch through an interface that exposes `CloneVT`; `unknownFields` are copied byte-for-byte.

Equality flow first handles pointer identity and nil mismatch. For nested pointers it commonly normalizes nil nested messages to empty value structs before calling nested `EqualVT`, matching generated proto equality semantics in this file. Oneof equality rejects mismatched wrapper types. Map equality checks length first, then validates each key and recursively compares nested values where needed. Unknown fields participate in equality by comparing their byte content.

Marshal flow is size-first and reverse-write:

- `MarshalVT` calls `SizeVT`, allocates an exact buffer, delegates to `MarshalToSizedBufferVT`, and returns the written prefix.
- `MarshalToSizedBufferVT` starts at `len(dAtA)` and writes fields in reverse tag order so the final byte slice is in normal protobuf order.
- nested messages are marshaled recursively into the remaining prefix, then prefixed with length and field tag.
- repeated message/string fields are iterated backward during reverse writes.
- packed scalar repeated fields such as `Meta.ValidExitCodes` and `PassthroughOp.Outputs` compute packed payload size, write packed varints, then emit the length-delimited field wrapper.
- map fields are emitted as synthetic length-delimited map-entry messages containing key and value fields.
- `unknownFields` are copied into the tail first so they remain part of the serialized output.

Size flow mirrors marshal flow. Each `SizeVT` method adds tag sizes, varint length sizes via `protohelpers.SizeOfVarint`, nested message sizes, packed payload sizes, and `len(m.unknownFields)`. Any schema change in `ops.proto` requires regenerated `SizeVT` and marshal methods to remain byte-exact.

Unmarshal flow is a hand-written generated parser pattern. Each method loops until `iNdEx >= len(dAtA)`, decodes the wire tag as a varint, validates illegal end-group and non-positive field numbers, switches on field number, checks expected wire type, decodes scalar/string/bytes/message/map/packed fields, and appends unknown wire segments to `m.unknownFields` using `protohelpers.Skip`. Length-delimited reads validate negative lengths, integer overflow, and EOF before slicing. Nested messages are allocated on demand and then parsed recursively.

## State And Persistence Behavior

There is no external persistence, filesystem access, networking, process state, or global mutable state in this chunk. The only state mutation is receiver-local:

- clone methods create independent in-memory copies;
- marshal methods read receiver state and produce byte slices;
- size methods read receiver state only;
- equality methods read both operands;
- unmarshal methods mutate the receiver by assigning scalars, appending repeated fields, allocating nested messages/maps, and preserving unknown wire fields.

Unmarshal is append-oriented for repeated fields and unknown fields, and it reuses some byte-slice storage for fields such as `SourceInfo.Data` with `append(m.Data[:0], ...)`. Callers that unmarshal into reused message instances should account for repeated fields accumulating unless they reset the message first.

## Dependencies

The chunk imports:

- `fmt` for generated parse errors with message and field context.
- `io` for `io.ErrUnexpectedEOF` on truncated wire input.
- `github.com/planetscale/vtprotobuf/protohelpers` for varint sizing/encoding, unknown-field skipping, and shared protobuf parse errors such as invalid length and integer overflow.
- `google.golang.org/protobuf/proto` for generic `proto.Message` adapter methods.
- `google.golang.org/protobuf/runtime/protoimpl` for generated version compatibility checks.

The code depends heavily on message structs, oneof interfaces, enum types, and `unknownFields` fields generated in companion protobuf files for the same package. Examples include `isOp_Op`, `isFileAction_Action`, `isUserOpt_User`, `NetMode`, `SecurityMode`, `MountType`, `CacheSharingOpt`, and `MountContentCache`.

## Integration Points

BuildKit solver code can use these methods through vtprotobuf interfaces for faster cloning, equality, marshaling, and unmarshaling of LLB operation definitions. Important integration paths include:

- cache key and graph comparison logic that benefits from `EqualVT`;
- solver graph duplication or metadata transformation paths using `CloneVT`;
- LLB definition storage, transport, or digest computation using `MarshalVT` and `SizeVT`;
- receiving or decoding protobuf operation data using `UnmarshalVT`;
- generic protobuf utilities that accept `proto.Message` and can call `CloneMessageVT` or `EqualMessageVT` where vtprotobuf integration is wired.

The file is generated and should be regenerated from `ops.proto` rather than manually edited. Any change to `ops.proto`, vtprotobuf generator version, oneof shape, enum tags, or unknown-field representation must be reflected consistently across this file and the base generated protobuf file.

## Risks And Edge Cases

- Manual edits are high risk because marshal, size, unmarshal, clone, and equality methods are schema-coupled generated code. A single mismatched field tag, size calculation, or wire type can corrupt serialized definitions.
- Equality includes `unknownFields`; semantically equivalent messages with different unknown-field byte ordering or preservation can compare unequal.
- Unmarshal appends repeated fields and unknown fields to the receiver, so reuse without reset can retain prior state.
- Maps are marshaled by ranging over Go maps, so byte output for map-containing messages may be nondeterministic unless callers use a deterministic marshal path elsewhere. This matters for digests or cache keys if this vt path is used directly for hashing.
- Oneof clone/marshal/equality dispatch relies on generated wrapper types satisfying expected private interfaces. Introducing a new oneof case in `ops.proto` requires regenerating this file; otherwise that case will not be handled by these fast paths.
- Unknown field handling preserves forward compatibility but also increases equality and marshal output sensitivity.
- The unmarshaler accepts enum numeric values directly into enum-typed fields without semantic validation. Unknown enum numbers can be preserved as field values, as protobuf generally permits.
- Integer and length checks guard against malformed inputs, but this is still generated parsing code over attacker-provided byte slices if exposed at a boundary; fuzz and corpus tests are valuable.
- This chunk ends during `ExportCache.UnmarshalVT`; unmarshal methods for later message types are outside the requested range and must be covered by the next chunk before whole-file conclusions are made.

## Test Signals

Useful validation signals for this generated chunk include:

- round-trip tests comparing `proto.Marshal`/`proto.Unmarshal` behavior with `MarshalVT`/`UnmarshalVT` for populated `Op`, `Definition`, `ExecOp`, `FileOp`, `BuildOp`, `Source`, and metadata messages;
- clone tests verifying nested slices, maps, byte slices, oneof wrappers, and unknown fields are deep-copied rather than aliased;
- equality tests for nil versus empty nested messages, oneof mismatches, map equality, repeated field ordering, unknown-field preservation, and byte slice fields;
- size tests asserting `SizeVT()` equals `len(MarshalVT())` across representative messages;
- fuzz tests feeding malformed varints, invalid wire types, truncated length-delimited fields, oversized lengths, unknown fields, packed/unpacked repeated integers, and map entries into `UnmarshalVT`;
- deterministic-output tests if any BuildKit digest/cache path directly uses these vt marshal methods on messages containing maps.

Because this file is generated, the strongest regression signal is a generator-based test or CI check that regenerates protobuf outputs from `ops.proto` and fails on diffs, combined with protobuf conformance-style round trips for BuildKit operation definitions.

### subset-b-000027: lines 12303-15648

# sources/cloud-native/buildkit/solver/pb/ops_vtproto.pb.go lines 12303-15648

## Scope

This chunk is generated `protoc-gen-go-vtproto` code for high-speed protobuf unmarshalling of the latter half of BuildKit's LLB operation schema. It starts inside `ExportCache.UnmarshalVT`, then covers complete `UnmarshalVT` implementations for `ProgressGroup`, `LinuxResources`, `ProxyEnv`, `WorkerConstraints`, `Definition`, `FileOp`, `FileAction`, file action payloads, ownership/user options, merge/diff inputs, `DiffOp`, and `PassthroughOp`.

The source schema for these messages is `sources/cloud-native/buildkit/solver/pb/ops.proto`; the Go type declarations are in `ops.pb.go`. This file is generated and should normally be changed by editing the proto/generation pipeline rather than hand editing the generated decoder.

## Purpose

The code decodes serialized LLB graph and operation messages into Go structs without going through reflective protobuf decoding. These messages sit on the BuildKit solver API boundary: `Definition` carries marshaled `Op` vertices plus metadata, `FileOp` describes filesystem mutation vertices, `MergeOp` and `DiffOp` model snapshot graph operations, `PassthroughOp` exposes external/custom outputs, and metadata helper messages carry cache, progress, resource, proxy, and worker-selection information.

## Important APIs And Types

- `ExportCache.UnmarshalVT` decodes the boolean `Value` field and preserves unknown fields. This is used through `OpMetadata.export_cache`.
- `ProgressGroup.UnmarshalVT` decodes progress grouping fields `id`, `name`, and `weak`, used by `OpMetadata.progress_group`.
- `LinuxResources.UnmarshalVT` decodes cgroup-style limits: memory, memory+swap, CPU shares/period/quota, and CPU/memory node affinity strings. The schema comments state these are per-step metadata constraints that do not affect cache keys.
- `ProxyEnv.UnmarshalVT` decodes the proxy environment tuple `http_proxy`, `https_proxy`, `ftp_proxy`, `no_proxy`, and `all_proxy`. `Meta` references this message outside the chunk.
- `WorkerConstraints.UnmarshalVT` appends repeated containerd-style filter strings. `Op` references this as top-level worker constraints.
- `Definition.UnmarshalVT` decodes repeated raw `def` byte blobs, a `map[string]*OpMetadata`, and optional `Source`. `def` entries are copied into newly allocated byte slices, so they do not alias the input buffer.
- `FileOp.UnmarshalVT` appends repeated `*FileAction` entries.
- `FileAction.UnmarshalVT` decodes numeric input/output indices and the oneof action variants: copy, mkfile, mkdir, rm, and symlink.
- `FileActionCopy.UnmarshalVT` handles copy options including source/destination paths, optional owner, mode/mode string, symlink handling, directory behavior, Docker archive unpack compatibility, destination creation, wildcard behavior, timestamp, include/exclude patterns, replacement behavior, and required paths.
- `FileActionMkFile`, `FileActionSymlink`, `FileActionMkDir`, and `FileActionRm` decode their operation-specific payloads plus optional owner/timestamp fields where applicable.
- `ChownOpt`, `UserOpt`, and `NamedUserOpt` decode ownership overrides. `UserOpt` is a oneof between a named user with an input index and a numeric ID.
- `MergeInput`/`MergeOp`, `LowerDiffInput`/`UpperDiffInput`/`DiffOp`, and `PassthroughOp` decode graph-composition operations. `PassthroughOp.outputs` accepts both packed and unpacked repeated varints.

## Control Flow

Every method follows the same vtprotobuf pattern:

1. Iterate through `dAtA` with `iNdEx < l`.
2. Decode a varint tag into `wire`, split it into `fieldNum` and `wireType`.
3. Reject end-group wire type and non-positive field numbers.
4. Switch on `fieldNum`, validate the expected wire type, decode the field, and advance `iNdEx`.
5. For unknown fields, reset to `preIndex`, call `protohelpers.Skip`, bounds-check the skipped range, append the bytes to `m.unknownFields`, and continue.
6. Return `io.ErrUnexpectedEOF`, `protohelpers.ErrIntOverflow`, or `protohelpers.ErrInvalidLength` on malformed input.

Nested messages are length-delimited, allocated lazily, and decoded by calling their own `UnmarshalVT`. Repeated message fields append new pointers before recursive decode. Repeated string fields append decoded strings. Oneof fields reuse the existing concrete oneof value if it already matches the incoming field, otherwise allocate a fresh payload and replace the oneof.

## State And Persistence Behavior

The decoder mutates the receiver in place. Scalar fields are generally reset to zero before varint accumulation, but repeated fields append to any existing slice. Nested pointer fields are allocated only when the serialized field is present; if a pointer already exists, decoding merges into it. Unknown fields are preserved by appending raw wire bytes to the receiver's protobuf unknown field storage.

`Definition.Def` is deep-copied from the input buffer. `FileActionMkFile.Data` is copied with `append(m.Data[:0], ...)`, which can reuse the receiver's existing capacity but does not retain an alias into `dAtA`. Strings are created from byte slices, so they allocate immutable Go strings. `PassthroughOp.Outputs` preallocates capacity for packed values by counting terminating varint bytes when the output slice is currently empty.

There is no external persistence, I/O, locking, or caching in this chunk. The persistent state is the in-memory protobuf message graph produced from serialized input.

## Dependencies

The chunk depends on:

- `github.com/planetscale/vtprotobuf/protohelpers` for skipping unknown fields and common protobuf decode errors.
- `io` for `io.ErrUnexpectedEOF`.
- `fmt` for malformed-wire error messages.
- Other generated message methods in the same file, such as `OpMetadata.UnmarshalVT` and `Source.UnmarshalVT`, when decoding nested messages.
- Schema/type definitions from `ops.proto` and `ops.pb.go`.

Integration with hand-written code is visible in `json.go`, which customizes JSON encoding for `Op`, `FileAction`, and `UserOpt`, and in `caps.go`, which declares capability IDs for `meta.exportcache`, `exec.meta.linux.resources`, `mergeop`, `diffop`, and `passthroughop`.

## Integration Points

`Definition` is the serialized LLB graph container and appears in `BuildOp` and `SourceInfo`. Any solver path that receives or stores LLB definitions depends on this decoder preserving raw op bytes, metadata map entries, and source mappings correctly.

`FileOp` and `FileAction` are integrated with BuildKit filesystem operations. `FileAction` comments explicitly say changes must be represented in `json.go`, making JSON/protobuf parity an integration contract. The vtprotobuf path supports the symlink oneof, while the current custom JSON helper lists copy, mkfile, mkdir, and rm but not symlink.

`WorkerConstraints`, `ProxyEnv`, `ProgressGroup`, `ExportCache`, and `LinuxResources` are metadata/control-plane types. They influence worker selection, environment propagation, UI/progress grouping, cache export behavior, and runtime resource limits rather than directly describing filesystem snapshots.

`MergeOp`, `DiffOp`, and `PassthroughOp` are graph operation variants selected by the top-level `Op` oneof decoded earlier in the file. They must remain wire-compatible with capability checks in `caps.go` and with clients that may send either packed or unpacked repeated `outputs`.

## Risks

- Because this file is generated, direct edits are fragile and will be overwritten. Schema-level changes must update `ops.proto`, regenerate `ops.pb.go` and `ops_vtproto.pb.go`, and keep `json.go` in sync where comments require it.
- In-place decode semantics mean reusing a non-empty receiver can append repeated fields and unknown fields instead of replacing them. Callers expecting a clean decode should reset or allocate a fresh message first.
- Oneof merge behavior can be subtle: duplicate same-variant oneof fields merge into the existing payload, while a different oneof field replaces the active variant.
- The decoder performs wire-level validation and length checks, but it does not enforce semantic validity such as valid paths, safe wildcard patterns, meaningful resource limits, valid cpuset syntax, or non-empty metadata digest keys.
- Signed integer fields are decoded as plain proto3 varints. Negative values are legal at the wire/type level but expensive on the wire and require downstream semantic handling.
- `Definition.Metadata` assigns `m.Metadata[mapkey] = mapvalue` even if a malformed map entry omits key or value but remains wire-valid. Downstream code should not assume non-empty keys or non-nil values solely because the map exists.
- The hand-written JSON adapter appears to omit `FileAction_Symlink`, so JSON round-trip coverage may lag protobuf/vtprotobuf support for that oneof.

## Test Signals

Direct tests for generated `UnmarshalVT` methods are not present in this chunk. Useful signals are:

- `sources/cloud-native/buildkit/solver/pb/json_test.go` covers JSON round trips for top-level `Op` variants including file, build, merge, and diff; file action variants copy, mkfile, mkdir, and rm; and `UserOpt` by-name/by-ID behavior.
- `json_test.go` does not cover `FileAction_Symlink`, `PassthroughOp`, `LinuxResources`, `ProxyEnv`, `ProgressGroup`, `ExportCache`, `Definition.Metadata`, packed/unpacked `PassthroughOp.Outputs`, malformed wire data, or receiver reuse semantics.
- Regeneration consistency is a key test signal: generated vtprotobuf methods should match `ops.proto` field numbers and `ops.pb.go` types exactly.
- Fuzzing or table tests around malformed varints, truncated length-delimited fields, unknown fields, duplicate oneof fields, map entries missing key/value, and packed/unpacked repeated outputs would exercise the main error and compatibility paths in this chunk.
